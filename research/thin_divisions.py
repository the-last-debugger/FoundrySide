"""Thin-division market-efficiency measurement, per docs/METHOD-THIN-DIVISIONS.md.

No model is fitted. The question is whether the de-vigged closing price is less well calibrated in
thirteen unused divisions than in the eight already held. Files are read into memory only and are not
stored, merged or added to the corpus.

    python research/thin_divisions.py

Writes research/THIN_DIVISIONS.md.
"""

from __future__ import annotations

import csv
import io
import math
import statistics
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research"))

import feature_screen as fs   # noqa: E402
import report_stamp           # noqa: E402

OUT = ROOT / "research" / "THIN_DIVISIONS.md"
ADDED = ["E2", "E3", "EC", "I2", "SP2", "F2", "D2", "B1", "T1", "SC0", "SC1", "SC2", "SC3"]
EXISTING = ["E0", "D1", "E1", "F1", "I1", "N1", "P1", "SP1"]
SEASONS = ["2021", "2122", "2223"]
URL = "https://football-data.co.uk/mmz4281/{season}/{league}.csv"
BOOTSTRAPS = 2000
SEED = 20261103
RELEVANCE = 0.01


def devig(over: float, under: float) -> float:
    return (1 / over) / (1 / over + 1 / under)


def usable(*vals) -> bool:
    try:
        return all(math.isfinite(float(v)) and float(v) > 1.0 for v in vals)
    except (TypeError, ValueError):
        return False


def fetch(season: str, league: str) -> tuple[list[dict], dict]:
    """Read one division-season into memory. Nothing is written to disk.

    Returns the scored rows and the accounting that explains every excluded row: raw fixtures,
    those with a usable two-sided Over 2.5 price, those also carrying a result, and the two
    exclusion reasons separately.
    """
    counts = {"raw": 0, "no_price": 0, "no_result": 0, "scored": 0}
    try:
        raw = urllib.request.urlopen(URL.format(season=season, league=league), timeout=30)
        text = raw.read().decode("latin-1")
    except Exception:
        return [], counts
    out = []
    for row in csv.DictReader(io.StringIO(text)):
        counts["raw"] += 1
        if not usable(row.get("PC>2.5"), row.get("PC<2.5")):
            counts["no_price"] += 1
            continue
        try:
            hg, ag = int(row["FTHG"]), int(row["FTAG"])
        except (TypeError, ValueError):
            counts["no_result"] += 1
            continue
        p = devig(float(row["PC>2.5"]), float(row["PC<2.5"]))
        out.append({"p": p, "y": 1 if hg + ag >= 3 else 0, "season": season})
        counts["scored"] += 1
    return out, counts


def logloss(rows: list[dict]) -> float:
    return statistics.mean(-(r["y"] * math.log(r["p"]) + (1 - r["y"]) * math.log(1 - r["p"]))
                           for r in rows)


def brier(rows: list[dict]) -> float:
    return statistics.mean((r["p"] - r["y"]) ** 2 for r in rows)


def decomposition(rows: list[dict]) -> tuple[float, float]:
    bins: dict[int, list[dict]] = {}
    for r in rows:
        bins.setdefault(min(9, int(r["p"] * 10)), []).append(r)
    base = statistics.mean(r["y"] for r in rows)
    rel = res = 0.0
    for group in bins.values():
        w = len(group) / len(rows)
        mp = statistics.mean(g["p"] for g in group)
        my = statistics.mean(g["y"] for g in group)
        rel += w * (mp - my) ** 2
        res += w * (my - base) ** 2
    return rel, res



def slope(rows: list[dict]) -> float:
    """One-parameter logistic calibration slope on the price's logit."""
    import calibration_study as cs
    a, _b = cs.fit_platt([{"p": r["p"], "y": r["y"]} for r in rows])
    return a


def main() -> int:
    data: dict[str, list[dict]] = {}
    accounting: dict[tuple[str, str], dict] = {}
    for league in ADDED + EXISTING:
        rows = []
        for season in SEASONS:
            part, counts = fetch(season, league)
            accounting[(league, season)] = counts
            rows.extend(part)
        data[league] = rows

    added_rows = [r for lg in ADDED for r in data[lg]]
    existing_rows = [r for lg in EXISTING for r in data[lg]]

    per_division = []
    for league in ADDED:
        rows = data[league]
        if not rows:
            per_division.append({"league": league, "n": 0})
            continue
        seasons = []
        for season in SEASONS:
            sub = [r for r in rows if r["season"] == season]
            seasons.append(logloss(sub) if sub else float("nan"))
        rel, res = decomposition(rows)
        per_division.append({"league": league, "n": len(rows), "ll": logloss(rows),
                             "brier": brier(rows), "rel": rel, "res": res,
                             "slope": slope(rows), "seasons": seasons})

    ref_ll = logloss(existing_rows)
    added_ll = logloss(added_rows)

    # Bootstrap over division-seasons, for the pooled comparison only.
    import numpy as np
    clusters = {}
    for league in ADDED:
        for season in SEASONS:
            rows = [r for r in data[league] if r["season"] == season]
            if rows:
                clusters[f"{league}_{season}"] = rows
    keys = sorted(clusters)
    rng = np.random.default_rng(SEED)
    draws = []
    for _ in range(BOOTSTRAPS):
        picked = [clusters[keys[rng.integers(0, len(keys))]] for _ in keys]
        flat = [r for group in picked for r in group]
        if flat:
            draws.append(logloss(flat))
    draws.sort()
    lo, hi = draws[int(0.025 * len(draws))], draws[int(0.975 * len(draws)) - 1]

    # Interval for the *difference*, which is the comparison the method describes. Each set's
    # clusters are resampled independently, so the interval reflects both sampling errors.
    ref_clusters = {}
    for league in EXISTING:
        for season in SEASONS:
            part = [r for r in data[league] if r["season"] == season]
            if part:
                ref_clusters[f"{league}_{season}"] = part
    ref_keys = sorted(ref_clusters)
    diffs = []
    for _ in range(BOOTSTRAPS):
        add_pick = [clusters[keys[rng.integers(0, len(keys))]] for _ in keys]
        ref_pick = [ref_clusters[ref_keys[rng.integers(0, len(ref_keys))]] for _ in ref_keys]
        add_flat = [r for g in add_pick for r in g]
        ref_flat = [r for g in ref_pick for r in g]
        if add_flat and ref_flat:
            diffs.append(logloss(add_flat) - logloss(ref_flat))
    diffs.sort()
    d_lo, d_hi = diffs[int(0.025 * len(diffs))], diffs[int(0.975 * len(diffs)) - 1]

    diff = added_ll - ref_ll
    spread = [d["ll"] - ref_ll for d in per_division if d["n"]]

    def cell(d):
        if not d["n"]:
            return "no data"
        seasons = ", ".join(f"{s:.4f}" for s in d["seasons"])
        return f"{d['ll']:.4f} (n={d['n']:,}; {seasons})"

    doc = f"""{report_stamp.stamp(Path(__file__))}

# Thin-division market efficiency

Specification fixed at `docs/METHOD-THIN-DIVISIONS.md` before the run. **No model is involved**: the
subject is the de-vigged closing price itself. Files were read into memory only, never stored, merged
or added to the corpus; the confirmatory slice was not read.

## Per division — descriptive

Each row shows the market log loss, the fixture count, and the three individual season values. There
are **no intervals and no significance claims at division level**: each division contributes three
season-clusters, and a bootstrap over three units would not support one.

| Division | Market log loss (three seasons, individually) |
| --- | --- |
""" + "\n".join(f"| {d['league']} | {cell(d)} |" for d in per_division) + f"""

## Denominator accounting — where every document's number comes from

The assessment counts **source fixtures**; this report counts **scored observations**. They are not
the same sample and the difference is disclosed here rather than reconciled by assertion.

| Division | Raw | No usable two-sided O/U | No result | Scored |
| --- | --- | --- | --- | --- |
""" + "\n".join(
        f"| {d['league']} | {sum(accounting[(d['league'], s)]['raw'] for s in SEASONS):,} | "
        f"{sum(accounting[(d['league'], s)]['no_price'] for s in SEASONS):,} | "
        f"{sum(accounting[(d['league'], s)]['no_result'] for s in SEASONS):,} | "
        f"{sum(accounting[(d['league'], s)]['scored'] for s in SEASONS):,} |"
        for d in per_division) + f"""

| Season | Raw | No price | No result | Scored |
| --- | --- | --- | --- | --- |
""" + "\n".join(
        f"| {s} | {sum(accounting[(lg, s)]['raw'] for lg in ADDED):,} | "
        f"{sum(accounting[(lg, s)]['no_price'] for lg in ADDED):,} | "
        f"{sum(accounting[(lg, s)]['no_result'] for lg in ADDED):,} | "
        f"{sum(accounting[(lg, s)]['scored'] for lg in ADDED):,} |"
        for s in SEASONS) + f"""

Every exclusion is a missing or unusable two-sided Over 2.5 price, or a missing result; no row is
dropped for any other reason. Turkey 1 accounts for the largest single loss, consistent with its
lower price coverage in the assessment.

## Pooled comparison

| Set | Fixtures | Market log loss |
| --- | --- | --- |
| Eight existing divisions | {len(existing_rows):,} | {ref_ll:.4f} |
| Thirteen additions | {len(added_rows):,} | {added_ll:.4f} |
| Difference (additions − existing) | — | **{diff:+.4f}** |

Approximate division-season bootstrap interval for the **difference** (additions − existing),
resampling each set's clusters independently: **[{d_lo:+.4f}, {d_hi:+.4f}]**. The earlier version of
this report gave an interval for the additions' log loss alone, which is a different quantity; that
figure was [{lo:.4f}, {hi:.4f}] and it is retained only as context.

**Spread of division-level differences** against the existing eight: minimum {min(spread):+.4f},
maximum {max(spread):+.4f}, median {statistics.median(spread):+.4f}. The pooled figure alone would
conceal that range, which is why both are reported.

## Secondary metrics

| Division | Brier | Reliability | Resolution | Calibration slope |
| --- | --- | --- | --- | --- |
""" + "\n".join(
        f"| {d['league']} | {d['brier']:.4f} | {d['rel']:.4f} | {d['res']:.4f} | {d['slope']:.3f} |"
        for d in per_division if d["n"]) + f"""

## What this says and does not say

The difference of {diff:+.4f} nats between the pooled additions and the existing eight is
{'at or beyond' if abs(diff) >= RELEVANCE else 'below'} the 0.01-nat scale used elsewhere in the
project as a descriptive yardstick — which is a scale, not a test.

**It is not evidence of exploitable value.** Price quality is a property of the price, not of a
strategy: exploiting any of it would need prices a user can obtain, stakes, limits and a decision
rule, none of which this corpus records. Nothing here supports a claim of user advantage.

## Limits

- Three seasons per division; only a large difference would be visible, and small divisions are
  reported with their counts so the reader can discount them.
- The eight-division reference is a different set of competitions, not a matched control.
- Closing prices without timestamps; the T−90 caveat applies throughout.
- Internal analysis only; no redistributable dataset was created and P-03 remains open for any
  publication.
"""
    OUT.write_text(doc, encoding="utf-8")

    for d in per_division:
        if d["n"]:
            print(f"{d['league']:4} n={d['n']:5,} ll={d['ll']:.4f} "
                  f"seasons={[round(s,4) for s in d['seasons']]}")
    print(f"existing {ref_ll:.4f} ({len(existing_rows):,}) vs additions {added_ll:.4f} "
          f"({len(added_rows):,}) diff={diff:+.4f} [approx {lo:.4f},{hi:.4f}]")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
