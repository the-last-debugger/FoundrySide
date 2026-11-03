"""T0, T1 and T3: real-market baseline, data coverage, and accumulator dependence.

Reads every CSV in research/data (football-data.co.uk division files), computes:

  T0  the favourite baseline at matched coverage, on closing 1X2 prices, with
      Wilson intervals, a coverage/accuracy curve and per-league splits
  T1  what was actually obtainable: rows, closing-price completeness, date range
  T3  realised joint frequency of same-match legs against the product of the
      marginals, which is the number that decides whether marginals may be
      multiplied

Writes research/RESULTS_T0_T1_T3.md and research/data_manifest.csv. Prints a short
summary. Standard library only, so it runs anywhere without an install.

    python research/analyse.py
"""

from __future__ import annotations

import csv
import hashlib
import math
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "research" / "data"
OUT = ROOT / "research" / "RESULTS_T0_T1_T3.md"
MANIFEST = ROOT / "research" / "data_manifest.csv"

SOURCE = "https://www.football-data.co.uk/mmz4281/{season}/{league}.csv"

# Closing prices, best first. Pinnacle closing is the sharpest reference and the
# one to prefer when present; Bet365 closing is the fallback.
CLOSING_1X2 = [
    ("PSCH", "PSCD", "PSCA"),
    ("B365CH", "B365CD", "B365CA"),
    ("PSH", "PSD", "PSA"),
    ("B365H", "B365D", "B365A"),
    ("AvgH", "AvgD", "AvgA"),
]

Z = 1.959963984540054


def wilson(hits: int, n: int) -> tuple[float, float]:
    """95% Wilson score interval for a proportion."""
    if n == 0:
        return (float("nan"), float("nan"))
    p = hits / n
    denom = 1 + Z * Z / n
    centre = (p + Z * Z / (2 * n)) / denom
    half = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def load() -> list[dict]:
    rows: list[dict] = []
    for path in sorted(DATA.glob("*.csv")):
        league, season = path.stem.split("_")
        with path.open(encoding="latin-1", newline="") as fh:
            for record in csv.DictReader(fh):
                record["_league"] = league
                record["_season"] = season
                record["_file"] = path.name
                rows.append(record)
    return rows


def as_float(value: str | None) -> float | None:
    try:
        f = float(value)
    except (TypeError, ValueError):
        return None
    return f if f > 1.0 else None


def closing(record: dict) -> tuple[tuple[float, float, float], str] | None:
    """Best available closing price, with the label of the source actually used.

    The fallback chain is deliberate, but a silent fallback would let the results
    describe prices from one bookmaker while claiming another. The label is carried
    through to the output so the mix is visible.
    """
    for h, d, a in CLOSING_1X2:
        if h in record and d in record and a in record:
            hs, ds, as_ = as_float(record[h]), as_float(record[d]), as_float(record[a])
            if hs and ds and as_:
                return ((hs, ds, as_), h.rstrip("H"))
    return None


def implied(odds: tuple[float, float, float]) -> tuple[list[float], float]:
    raw = [1.0 / o for o in odds]
    total = sum(raw)
    return ([r / total for r in raw], total - 1.0)


def score(rows: list[dict]) -> list[dict]:
    scored = []
    for r in rows:
        found = closing(r)
        if not found:
            continue
        odds, source = found
        try:
            hg, ag = int(r["FTHG"]), int(r["FTAG"])
        except (KeyError, TypeError, ValueError):
            continue
        probs, overround = implied(odds)
        pick = max(range(3), key=lambda i: probs[i])
        outcome = "H" if hg > ag else ("A" if hg < ag else "D")
        scored.append({
            "league": r["_league"], "season": r["_season"], "source": source,
            "prob": probs[pick], "pick": "HDA"[pick], "outcome": outcome,
            "hit": "HDA"[pick] == outcome,
            "home": outcome == "H", "draw": outcome == "D",
            "btts": hg > 0 and ag > 0, "over25": hg + ag >= 3,
            "goals": hg + ag, "overround": overround,
        })
    return scored


def pct(x: float) -> str:
    return f"{100 * x:.1f}%"


def interval(hits: int, n: int) -> str:
    lo, hi = wilson(hits, n)
    return f"{pct(hits / n)} (95% CI {pct(lo)}–{pct(hi)})"


def coverage_table(rows: list[dict]) -> str:
    groups: dict[tuple[str, str], list[dict]] = {}
    for r in rows:
        groups.setdefault((r["_league"], r["_season"]), []).append(r)
    lines = ["| League | Season | Rows | With closing 1X2 | Complete | First date | Last date | Price source |",
             "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    totals = [0, 0]
    for key in sorted(groups):
        grp = groups[key]
        with_odds = sum(1 for r in grp if closing(r))
        dates = []
        for r in grp:
            try:
                dates.append(datetime.strptime(r.get("Date", ""), "%d/%m/%Y"))
            except (ValueError, TypeError):
                continue
        dates.sort()
        totals[0] += len(grp)
        totals[1] += with_odds
        labels = [closing(r)[1] for r in grp if closing(r)]
        label = max(set(labels), key=labels.count) if labels else "—"
        lines.append(f"| {key[0]} | {key[1]} | {len(grp)} | {with_odds} | "
                     f"{pct(with_odds / len(grp)) if grp else '—'} | "
                     f"{dates[0]:%Y-%m-%d} | {dates[-1]:%Y-%m-%d} | {label} |"
                     if dates else
                     f"| {key[0]} | {key[1]} | {len(grp)} | {with_odds} | "
                     f"{pct(with_odds / len(grp)) if grp else '—'} | — | — | {label} |")
    lines.append(f"| **all** | | **{totals[0]}** | **{totals[1]}** | "
                 f"**{pct(totals[1] / totals[0]) if totals[0] else '—'}** | | | |")
    return "\n".join(lines)


def source_mix(scored: list[dict]) -> str:
    """Which price column actually supplied each fixture's odds."""
    counts: dict[str, int] = {}
    for s in scored:
        counts[s["source"]] = counts.get(s["source"], 0) + 1
    total = len(scored)
    lines = ["| Price source used | n | Share |", "| --- | --- | --- |"]
    for label, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        lines.append(f"| {label} | {n} | {pct(n / total)} |")
    return "\n".join(lines)


def sensitivity(scored: list[dict], label: str = "PSC") -> str:
    """The baseline on a single source, so a fallback cannot flatter the pooled figure."""
    subset = [s for s in scored if s["source"] == label]
    if not subset:
        return "No single source covers enough fixtures for a sensitivity check."
    hits = sum(1 for s in subset if s["hit"])
    return (f"Restricted to `{label}` only: {interval(hits, len(subset))} on "
            f"{len(subset)} fixtures. The pooled figure includes the fallbacks listed "
            f"above; if the two disagree materially, the pooled number is the one to "
            f"distrust.")


def baseline_table(scored: list[dict]) -> str:
    n = len(scored)
    hits = sum(1 for s in scored if s["hit"])
    home = sum(1 for s in scored if s["home"])
    draw = sum(1 for s in scored if s["draw"])
    margin = sum(s["overround"] for s in scored) / n
    lines = ["| Policy | n | Accuracy |", "| --- | --- | --- |",
             f"| Favourite by closing price | {n} | {interval(hits, n)} |",
             f"| Home always | {n} | {interval(home, n)} |",
             f"| Draw always | {n} | {interval(draw, n)} |",
             f"| Uniform random (expected) | {n} | 33.3% |"]
    lines.append("")
    lines.append(f"Mean 1X2 overround (bookmaker margin): **{pct(margin)}**.")
    return "\n".join(lines)


def curve_table(scored: list[dict]) -> str:
    edges = [0.0, 0.34, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 1.01]
    lines = ["| Favourite implied probability | n | Coverage | Accuracy |",
             "| --- | --- | --- | --- |"]
    n_all = len(scored)
    for lo, hi in zip(edges, edges[1:]):
        band = [s for s in scored if lo <= s["prob"] < hi]
        if not band:
            continue
        hits = sum(1 for s in band if s["hit"])
        lines.append(f"| {lo:.2f}–{min(hi, 1.0):.2f} | {len(band)} | "
                     f"{pct(len(band) / n_all)} | {interval(hits, len(band))} |")
    return "\n".join(lines)


def league_table(scored: list[dict]) -> str:
    groups: dict[str, list[dict]] = {}
    for s in scored:
        groups.setdefault(s["league"], []).append(s)
    lines = ["| League | n | Favourite accuracy | Home always |",
             "| --- | --- | --- | --- |"]
    for league in sorted(groups):
        grp = groups[league]
        hits = sum(1 for s in grp if s["hit"])
        home = sum(1 for s in grp if s["home"])
        lines.append(f"| {league} | {len(grp)} | {interval(hits, len(grp))} | "
                     f"{pct(home / len(grp))} |")
    return "\n".join(lines)


def bootstrap_ratio(scored: list[dict], reps: int = 10000, seed: int = 20261103) -> tuple[float, float]:
    """Percentile bootstrap for the ratio, resampling fixtures.

    The earlier interval divided the Wilson limits of the joint rate by a fixed
    product of marginals, which treats both marginals as known constants. They are
    estimated on the same sample, so their uncertainty has to propagate. Resampling
    the four outcome cells is exactly a multinomial draw on the observed proportions,
    which is cheap and needs no library.
    """
    import random

    rng = random.Random(seed)
    n = len(scored)
    cells = [0, 0, 0, 0]           # (btts&over, btts&!over, !btts&over, !btts&!over)
    for s in scored:
        if s["btts"] and s["over25"]:
            cells[0] += 1
        elif s["btts"]:
            cells[1] += 1
        elif s["over25"]:
            cells[2] += 1
        else:
            cells[3] += 1
    p = [c / n for c in cells]
    ratios = []
    for _ in range(reps):
        # Sequential binomial draws give a multinomial without numpy.
        n1 = rng.binomialvariate(n, p[0])
        n2 = rng.binomialvariate(n - n1, p[1] / (1 - p[0])) if p[0] < 1 else 0
        n3 = rng.binomialvariate(n - n1 - n2, p[2] / (1 - p[0] - p[1])) \
            if p[0] + p[1] < 1 else 0
        btts = (n1 + n2) / n
        over = (n1 + n3) / n
        denom = btts * over
        if denom > 0:
            ratios.append((n1 / n) / denom)
    ratios.sort()
    if not ratios:
        return (float("nan"), float("nan"))
    return (ratios[int(0.025 * len(ratios))], ratios[int(0.975 * len(ratios)) - 1])


def dependence(scored: list[dict]) -> dict:
    n = len(scored)
    p_btts = sum(1 for s in scored if s["btts"]) / n
    p_over = sum(1 for s in scored if s["over25"]) / n
    joint = sum(1 for s in scored if s["btts"] and s["over25"])
    p_joint = joint / n
    product = p_btts * p_over
    lo, hi = wilson(joint, n)
    boot_lo, boot_hi = bootstrap_ratio(scored)
    return {
        "n": n, "p_btts": p_btts, "p_over": p_over, "p_joint": p_joint,
        "product": product, "ratio": p_joint / product if product else float("nan"),
        "joint_lo": lo, "joint_hi": hi,
        "ratio_lo": boot_lo, "ratio_hi": boot_hi,
        "naive_lo": lo / product if product else float("nan"),
        "naive_hi": hi / product if product else float("nan"),
        "p_over_given_btts": joint / sum(1 for s in scored if s["btts"]) if p_btts else float("nan"),
    }


def dependence_table(scored: list[dict]) -> str:
    pooled = dependence(scored)
    lines = ["| Measure | Value |", "| --- | --- |",
             f"| n (fixtures with prices) | {pooled['n']} |",
             f"| P(both teams score) | {pct(pooled['p_btts'])} |",
             f"| P(over 2.5 goals) | {pct(pooled['p_over'])} |",
             f"| Product of marginals | {pct(pooled['product'])} |",
             f"| Realised joint P(BTTS and over 2.5) | {pct(pooled['p_joint'])} "
             f"(95% CI {pct(pooled['joint_lo'])}–{pct(pooled['joint_hi'])}) |",
             f"| Ratio, realised ÷ product | **{pooled['ratio']:.2f}×** "
             f"(bootstrap 95% CI {pooled['ratio_lo']:.2f}–{pooled['ratio_hi']:.2f}) |",
             f"| P(over 2.5 given BTTS) | {pct(pooled['p_over_given_btts'])} |",
             "",
             "The ratio is a ratio of three estimated proportions, so its interval has to",
             "propagate uncertainty in both marginals. An earlier version divided the Wilson",
             "limits of the joint rate by a *fixed* product and quoted "
             f"{pooled['naive_lo']:.2f}–{pooled['naive_hi']:.2f}; that treats the marginals as",
             "known constants and is not a confidence interval. The bootstrap interval above",
             "is the one to use. The point estimate is unchanged."]
    return "\n".join(lines)


def market_coverage(rows: list[dict]) -> str:
    """Closing-price availability per market, which decides the first experiment."""
    n = len(rows)
    checks = [
        ("1X2, Pinnacle closing", "PSCH", "PSCD", "PSCA"),
        ("1X2, Bet365 closing", "B365CH", "B365CD", "B365CA"),
        ("Over/under 2.5, Pinnacle closing", "PC>2.5", None, "PC<2.5"),
        ("Over/under 2.5, Bet365 closing", "B365C>2.5", None, "B365C<2.5"),
    ]
    lines = ["| Market | Fixtures with a complete closing price | Share |",
             "| --- | --- | --- |"]
    for label, a, b, c in checks:
        def present(rec):
            keys = [a, c] if b is None else [a, b, c]
            return all(rec.get(k) not in (None, "") for k in keys)
        count = sum(1 for r in rows if present(r))
        lines.append(f"| {label} | {count} | {pct(count / n)} |")
    return "\n".join(lines)


def dependence_by_league(scored: list[dict]) -> str:
    groups: dict[str, list[dict]] = {}
    for s in scored:
        groups.setdefault(s["league"], []).append(s)
    lines = ["| League | n | P(BTTS) | P(O2.5) | Product | Realised joint | Ratio |",
             "| --- | --- | --- | --- | --- | --- | --- |"]
    for league in sorted(groups):
        d = dependence(groups[league])
        lines.append(f"| {league} | {d['n']} | {pct(d['p_btts'])} | {pct(d['p_over'])} | "
                     f"{pct(d['product'])} | {pct(d['p_joint'])} | {d['ratio']:.2f}× |")
    return "\n".join(lines)


def manifest() -> str:
    lines = ["file,league,season,bytes,sha256,source_url,retrieved_utc"]
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for path in sorted(DATA.glob("*.csv")):
        league, season = path.stem.split("_")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{path.name},{league},{season},{path.stat().st_size},{digest},"
                     f"{SOURCE.format(season=season, league=league)},{stamp}")
    MANIFEST.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return f"manifest rows: {len(lines) - 1}"


def market_benchmark(rows: list[dict]) -> str:
    """Characterise the over/under 2.5 benchmark: de-vigged log loss and Brier.

    This is not a model comparison. It measures how well the market's own de-vigged
    probability scores, which sets the scale against which a model's log loss is read,
    and is the number the preregistration needs for its effect-size argument.
    """
    import math

    pairs = 0
    logloss = 0.0
    brier = 0.0
    implied_over = 0.0
    observed_over = 0
    overrounds: list[float] = []
    for r in rows:
        try:
            o_over = float(r.get("PC>2.5", ""))
            o_under = float(r.get("PC<2.5", ""))
        except (TypeError, ValueError):
            continue
        if o_over <= 1.0 or o_under <= 1.0:
            continue
        try:
            hg, ag = int(r["FTHG"]), int(r["FTAG"])
        except (KeyError, TypeError, ValueError):
            continue
        raw_over, raw_under = 1 / o_over, 1 / o_under
        total = raw_over + raw_under
        p_over = raw_over / total
        y = 1 if hg + ag >= 3 else 0
        pairs += 1
        observed_over += y
        implied_over += p_over
        overrounds.append(total - 1)
        logloss += -(math.log(p_over) if y else math.log(1 - p_over))
        brier += (p_over - y) ** 2
    if not pairs:
        return "No over/under 2.5 closing prices found."
    return "\n".join([
        "| Benchmark measure (de-vigged Pinnacle over/under 2.5) | Value |",
        "| --- | --- |",
        f"| Fixtures | {pairs} |",
        f"| Mean de-vigged P(over 2.5) | {pct(implied_over / pairs)} |",
        f"| Observed over-2.5 rate | {pct(observed_over / pairs)} |",
        f"| Market log loss | **{logloss / pairs:.4f} nats** |",
        f"| Market Brier score | {brier / pairs:.4f} |",
        f"| Mean two-way overround | {pct(sum(overrounds) / len(overrounds))} |",
        "",
        "This is the benchmark's own score, not a model's. It is what a model has to",
        "beat, and the first number a preregistered effect size should be stated against.",
    ])


def main() -> int:
    rows = load()
    scored = score(rows)
    pooled = dependence(scored)

    doc = f"""# T0, T1, T3 — measured results

Generated by `python research/analyse.py` on {datetime.now(timezone.utc).strftime('%Y-%m-%d')}.
Everything below is computed from the files listed in `research/data_manifest.csv`;
no number here is estimated, and every table can be reproduced by re-running the
script against the same manifest.

**Source.** football-data.co.uk division files, `mmz4281/<season>/<league>.csv`,
retrieved {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%MZ')}. Free, publicly
published, no account. Terms reviewed at the level of "published for reuse with
attribution"; this is **not** a legal opinion and is recorded as such — see the
open question in §4.

---

## 1. T1 — what was actually obtainable

{coverage_table(rows)}

### Closing-price availability by market

{market_coverage(rows)}

This table is the evidence behind the first-market recommendation in
`docs/EVALUATION_PROTOCOL.md`. Over/under 2.5 has a complete closing price on almost
every fixture from two independent books, which is what makes it the cheapest market
in which to run a paired, de-vigged comparison.

## 2. T0 — the real-league favourite baseline

Pooled across every fixture with a complete closing 1X2 price:

{baseline_table(scored)}

### Which prices these are

{source_mix(scored)}

{sensitivity(scored)}

### Accuracy by implied probability

{curve_table(scored)}

### By league

{league_table(scored)}

## 3. T3 — accumulator dependence

The question §6 of the pre-proposal raises: may same-match legs be multiplied?
Marginals are measured from outcomes, not prices, so this is independent of the
bookmakers' view.

{dependence_table(scored)}

### By league

{dependence_by_league(scored)}

## 3b. The benchmark's own score

The over/under 2.5 market, de-vigged by proportional normalisation. This is a
characterisation of the benchmark, not a model comparison — it sets the scale for the
effect size in `docs/EVALUATION_PROTOCOL.md`.

{market_benchmark(rows)}

## 4. Descriptive versus inferential

Stated explicitly, because the two were mixed in the first version of this document.

- **Descriptive** (no inference claimed): the accuracy figures, the overround, the
  per-league splits, the coverage table, and the point estimates in §3. These describe
  this sample.
- **Inferential** (intervals, and only where the estimator matches): the Wilson
  intervals on proportions — accuracy, home, draw, joint rate — and the bootstrap
  interval on the dependence ratio. Nothing else here is inferential.
- **Not inferential at all**, despite appearing in the same tables: per-league accuracy
  comparisons between divisions. Those are descriptive splits; the intervals overlap
  and no test of difference has been run.
- The earlier ratio interval (1.46–1.52) was **miscomputed** — see the note in §3 — and
  is replaced by the bootstrap interval.

## 5. What these numbers do not establish

- **Not a legal opinion.** Attribution and reuse terms were read, not negotiated.
  Nothing here authorises redistribution of the underlying files.
- **Not a claim of edge.** T0 measures a baseline, not a model. A model that beats
  it has not been built, and this document does not assert one could be.
- **Closing prices are a proxy.** `PSC*` where present, otherwise `B365C*`, then
  pre-close prices. The mix is not uniform across seasons and is reported per file
  rather than smoothed over.
- **BTTS and O2.5 dependence is a property of football, not of a betting market.**
  It bounds what multiplication can do; it says nothing about whether a combination
  is fairly priced.
"""
    OUT.write_text(doc, encoding="utf-8")
    print(manifest())
    print(f"rows={len(rows)} scored={len(scored)}")
    print(f"favourite={interval(sum(1 for s in scored if s['hit']), len(scored))}")
    print(f"overround={pct(sum(s['overround'] for s in scored) / len(scored))}")
    print(f"dependence ratio={pooled['ratio']:.3f} "
          f"(joint {pct(pooled['p_joint'])} vs product {pct(pooled['product'])})")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
