"""Robustness of the disagreement finding, per docs/PREREG-ROBUSTNESS.md.

Does "the model loses most where it departs furthest" survive across forward seasons and
divisions? The bands and the reproduction rule are fixed in the pre-registration.

    python research/robustness.py

Writes research/ROBUSTNESS.md.
"""

from __future__ import annotations

import csv
import statistics
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research"))

import calibration_study as cs   # noqa: E402
import report_stamp              # noqa: E402

OUT = ROOT / "research" / "ROBUSTNESS.md"
DELTAS = ROOT / "research" / "pilot_deltas.csv"
NEAR, FAR = 0.10, 0.60
BOOTSTRAPS = 2000
SEED = 20261103
SMALL = 100


def load() -> list[dict]:
    rows = []
    with DELTAS.open(encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            if r["phase"] != "pilot":
                continue
            rows.append({"season": r["season"], "cluster": r["cluster"],
                         "league": r["league"], "p": float(r["p_model"]),
                         "p_market": float(r["p_market"]), "y": int(r["y"])})
    seasons = sorted({r["season"] for r in rows})
    for r in rows:
        r["p_cal"] = r["p"]
    for held in seasons:
        train = [{"p": r["p"], "y": r["y"]} for r in rows if r["season"] < held]
        if len(train) < 100:
            continue
        a, b = cs.fit_platt(train)
        for r in rows:
            if r["season"] == held:
                r["p_cal"] = cs.sigmoid(a * cs.logit(r["p"]) + b)
    for r in rows:
        r["departure"] = abs(cs.logit(r["p_cal"]) - cs.logit(r["p_market"]))
    return rows


def gap(r: dict) -> float:
    """Positive means the model is worse than the market."""
    return cs.logloss(r["p_cal"], r["y"]) - cs.logloss(r["p_market"], r["y"])


def band_mean(rows: list[dict], lo: float, hi: float, rng, clusters: dict) -> dict:
    subset = [r for r in rows if lo <= r["departure"] < hi]
    if not subset:
        return {"n": 0, "gap": float("nan"), "lo": float("nan"), "hi": float("nan")}
    observed = statistics.mean(gap(r) for r in subset)
    keys = sorted(clusters)
    by = {k: [r for r in subset if r["cluster"] == k] for k in keys}
    draws = []
    for _ in range(BOOTSTRAPS):
        flat = [r for k in (keys[rng.integers(0, len(keys))] for _ in keys) for r in by[k]]
        if flat:
            draws.append(statistics.mean(gap(r) for r in flat))
    draws.sort()
    return {"n": len(subset), "gap": observed,
            "lo": draws[int(0.025 * len(draws))], "hi": draws[int(0.975 * len(draws)) - 1]}


def main() -> int:
    rows = load()
    seasons = ["2122", "2223"]
    divisions = sorted({r["league"] for r in rows})
    rng = np.random.default_rng(SEED)

    season_rows = {}
    for season in seasons:
        subset = [r for r in rows if r["season"] == season]
        clusters: dict[str, list[int]] = {}
        for r in subset:
            clusters.setdefault(r["cluster"], []).append(r)
        season_rows[season] = {
            "near": band_mean(subset, 0.0, NEAR, rng, {k: None for k in clusters}),
            "far": band_mean(subset, FAR, 999.0, rng, {k: None for k in clusters}),
        }

    division_rows = []
    for division in divisions:
        subset = [r for r in rows if r["league"] == division and r["season"] in seasons]
        clusters = {}
        for r in subset:
            clusters.setdefault(r["cluster"], []).append(r)
        division_rows.append({
            "division": division,
            "near": band_mean(subset, 0.0, NEAR, rng, clusters),
            "far": band_mean(subset, FAR, 999.0, rng, clusters),
        })

    def reproduces(s: dict) -> bool:
        n, f = s["near"], s["far"]
        return (f["n"] > 0 and f["gap"] > n["gap"] and f["lo"] > 0)

    outcomes = {s: reproduces(season_rows[s]) for s in seasons}
    overall = all(outcomes.values())
    verdict = ("reproduced in both forward seasons" if overall
               else "NOT reproduced across forward seasons")

    def cell(d: dict) -> str:
        if d["n"] == 0:
            return "—"
        marker = " (small sample)" if d["n"] < SMALL else ""
        return f"{d['gap']:+.4f} [{d['lo']:+.4f}, {d['hi']:+.4f}]{marker} (n={d['n']:,})"

    doc = f"""{report_stamp.stamp(Path(__file__))}

# Robustness of the disagreement finding

Pre-registered at `docs/PREREG-ROBUSTNESS.md`. Bands fixed from E18: near = departure under 0.10 on
the logit scale, far = 0.60 or more. Positive means the model is worse than the market.

## By forward season

| Season | Near band | Far band | Pattern |
| --- | --- | --- | --- |
""" + "\n".join(
        f"| {s} | {cell(season_rows[s]['near'])} | {cell(season_rows[s]['far'])} | "
        f"{'holds' if outcomes[s] else 'fails'} |" for s in seasons) + f"""

**Verdict: {verdict}.** The pre-registered rule required the far-band deficit to exceed the
near-band deficit and its interval to exclude zero, in both seasons.

## By division (descriptive)

| Division | Near band | Far band |
| --- | --- | --- |
""" + "\n".join(
        f"| {d['division']} | {cell(d['near'])} | {cell(d['far'])} |" for d in division_rows) + f"""

Division cells are descriptive and several are small; a cell under {SMALL} fixtures is marked and
is not used in any conclusion. With eight divisions split into two bands these intervals are wide by
construction, and no division is tested against another.

## What this supports

{'The ordering reproduces in both forward seasons, so E18 can be cited as a seasonal-robust pattern within this pilot rather than a pooled artefact.' if overall else 'The ordering does not reproduce in both forward seasons. E18 must therefore be cited as a pooled pilot description, not as a pattern that holds out of time, and every reference to it in the repository should say so.'}

Either way, E19 stands: no shrinkage policy beat market-only, so a disagreement pattern — reproduced
or not — does not create a deployable edge on this corpus.

## Limits

- Two forward seasons from one corpus; reproduction here is not external validity.
- The bands were fixed from E18 by design, which is honest but means E18 and this test are not
  independent evidence about the band boundaries themselves.
- Closing prices without timestamps throughout.
"""
    OUT.write_text(doc, encoding="utf-8", newline="\n")

    for s in seasons:
        n, f = season_rows[s]["near"], season_rows[s]["far"]
        print(f"{s}: near {n['gap']:+.4f} (n={n['n']}) far {f['gap']:+.4f} "
              f"[{f['lo']:+.4f},{f['hi']:+.4f}] (n={f['n']}) holds={outcomes[s]}")
    print("verdict:", verdict)
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
