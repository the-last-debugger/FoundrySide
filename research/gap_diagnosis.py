"""Why does the model trail the market? Decompose the gap instead of guessing.

The pilot model is about 0.025 nats worse than the closing price. That number says nothing
about *why*, and two very different failures look identical in it:

- **miscalibration** — the probabilities are systematically too high or too low;
- **lack of resolution** — the probabilities are calibrated but do not separate outcomes
  well, so they are close to the base rate.

Murphy's Brier decomposition separates them, and the same table shows the market's own
profile for comparison. This is the first diagnostic any modelling work should have run,
and it was not in the plan until now.

    python research/gap_diagnosis.py

Writes research/GAP_DIAGNOSIS.md.
"""

from __future__ import annotations

import csv
import random
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research"))

import report_stamp   # noqa: E402

OUT = ROOT / "research" / "GAP_DIAGNOSIS.md"
DELTAS = ROOT / "research" / "pilot_deltas.csv"
BINS = 10


def load() -> list[dict]:
    rows = []
    with DELTAS.open(encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            if r["phase"] != "pilot":
                continue
            rows.append({
                "division": r["league"], "cluster": r["cluster"],
                "p_model": float(r["p_model"]), "p_market": float(r["p_market"]),
                "y": int(r["y"]), "delta": float(r["delta"]),
            })
    return rows


def brier(rows: list[dict], key: str) -> float:
    return statistics.mean((r[key] - r["y"]) ** 2 for r in rows)


def decompose(rows: list[dict], key: str) -> dict[str, float]:
    """Murphy decomposition **of the binned forecast**.

    Reliability and resolution are computed from each bin's mean forecast, so the identity
    inned = reliability − resolution + uncertainty reconstructs the Brier score of the
    *coarsened* forecast, not of the raw per-fixture probabilities. The gap between the two
    is the within-bin variation of the forecast, and it is reported separately rather than
    folded silently into the total.
    """
    n = len(rows)
    base = statistics.mean(r["y"] for r in rows)
    bins: dict[int, list[dict]] = {}
    for r in rows:
        b = min(BINS - 1, int(r[key] * BINS))
        bins.setdefault(b, []).append(r)
    reliability = resolution = 0.0
    for b, group in bins.items():
        weight = len(group) / n
        predicted = statistics.mean(g["p"] if "p" in g else g[key] for g in group)
        observed = statistics.mean(g["y"] for g in group)
        reliability += weight * (predicted - observed) ** 2
        resolution += weight * (observed - base) ** 2
    binned = reliability - resolution + base * (1 - base)
    raw = statistics.mean((r[key] - r["y"]) ** 2 for r in rows)
    return {
        "reliability": reliability,
        "resolution": resolution,
        "uncertainty": base * (1 - base),
        "brier": binned,
        "brier_raw": raw,
        "within_bin": raw - binned,
    }


def calibration_table(rows: list[dict], key: str) -> str:
    n = len(rows)
    bins: dict[int, list[dict]] = {}
    for r in rows:
        bins.setdefault(min(BINS - 1, int(r[key] * BINS)), []).append(r)
    lines = ["| Bin | n | Mean prediction | Observed rate | Gap |",
             "| --- | --- | --- | --- | --- |"]
    for b in sorted(bins):
        group = bins[b]
        predicted = statistics.mean(g[key] for g in group)
        observed = statistics.mean(g["y"] for g in group)
        lines.append(f"| {b * 10}–{b * 10 + 9}% | {len(group)} | {predicted:.3f} | "
                     f"{observed:.3f} | {observed - predicted:+.3f} |")
    return "\n".join(lines)


def division_deltas(rows: list[dict]) -> str:
    by_div: dict[str, list[float]] = {}
    for r in rows:
        by_div.setdefault(r["division"], []).append(r["delta"])
    lines = ["| Division | n | Mean Δ (market − model) |", "| --- | --- | --- |"]
    for div in sorted(by_div):
        vals = by_div[div]
        lines.append(f"| {div} | {len(vals):,} | {statistics.mean(vals):+.4f} |")
    return "\n".join(lines)


def cluster_bootstrap(rows: list[dict], reps: int = 2000, seed: int = 20261103) -> tuple[float, float]:
    """Interval for the mean Δ, resampling clusters — fixture-level CIs would be too tight."""
    rng = random.Random(seed)
    by_cluster: dict[str, list[float]] = {}
    for r in rows:
        by_cluster.setdefault(r["cluster"], []).append(r["delta"])
    keys = sorted(by_cluster)
    draws = []
    for _ in range(reps):
        pick = [by_cluster[keys[rng.randrange(len(keys))]] for _ in keys]
        flat = [v for group in pick for v in group]
        draws.append(statistics.mean(flat))
    draws.sort()
    return (draws[int(0.025 * len(draws))], draws[int(0.975 * len(draws)) - 1])


def main() -> int:
    rows = load()
    model = decompose(rows, "p_model")
    market = decompose(rows, "p_market")
    lo, hi = cluster_bootstrap(rows)

    doc = f"""{report_stamp.stamp(Path(__file__))}

# Why the model trails the market

Generated by `python research/gap_diagnosis.py` from `research/pilot_deltas.csv`.

## The gap, with an interval

Mean Δ (market log loss − model log loss) on the pilot slice:
**{statistics.mean(r['delta'] for r in rows):+.4f}** nats, cluster-bootstrap 95% interval
**[{lo:+.4f}, {hi:+.4f}]**. Negative means the model is worse. The interval resamples the 24
division-season clusters, because fixtures within a league-season are not independent.

## Brier decomposition

| Component | Model | Market | Reading |
| --- | --- | --- | --- |
| Reliability (lower better) | {model['reliability']:.4f} | {market['reliability']:.4f} | how far predictions sit from the observed rate in their bin |
| Resolution (higher better) | {model['resolution']:.4f} | {market['resolution']:.4f} | how much the predictions separate outcomes |
| Uncertainty | {model['uncertainty']:.4f} | {market['uncertainty']:.4f} | a property of the outcome, identical for both |
| Brier of the **binned** forecast | {model['brier']:.4f} | {market['brier']:.4f} | reliability − resolution + uncertainty |
| Brier of the **raw** forecast | {model['brier_raw']:.4f} | {market['brier_raw']:.4f} | computed directly, per fixture |
| Within-bin forecast variation | {model['within_bin']:.4f} | {market['within_bin']:.4f} | raw minus binned; omitted by the binned identity |

## Calibration, model

{calibration_table(rows, 'p_model')}

## Calibration, market

{calibration_table(rows, 'p_market')}

## Mean Δ by division

{division_deltas(rows)}

## What this says

The model's Brier is worse and the decomposition attributes it. Read the two components
rather than the total: a model that is *less resolved* than the market is not adding
information, whatever its calibration; a model that is *miscalibrated* but equally resolved
is recoverable by a monotone correction. The table above distinguishes those cases, which
the single Δ number cannot.

The division split is descriptive. It shows where the gap is largest, not why, and no test
of difference between divisions has been run.

## Limits

- Bins are equal-width and the bin count is a choice. Reliability and resolution depend on
  it, and they describe the *binned* forecast: the identity is exact for the coarsened
  forecast, and the raw Brier differs from it by the within-bin variation reported above.
- One model, one market, one corpus, pilot seasons only.
- The benchmark is a closing price with no recorded observation time, so this compares a
  T−90 model with a later benchmark.
"""
    OUT.write_text(doc, encoding="utf-8")

    print(f"n={len(rows)} mean_delta={statistics.mean(r['delta'] for r in rows):+.4f} "
          f"ci=[{lo:+.4f},{hi:+.4f}]")
    print(f"model rel={model['reliability']:.4f} res={model['resolution']:.4f} "
          f"brier={model['brier']:.4f}")
    print(f"market rel={market['reliability']:.4f} res={market['resolution']:.4f} "
          f"brier={market['brier']:.4f}")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
