"""Why does the market still win after calibration?

Forward calibration took the model from 0.0246 nats behind to roughly 0.014. This asks where the
remainder sits, because the answer decides whether anything can be done about it.

Splits, each with its sample size and a cluster interval, corrected within dimension:

1. **Market-probability band** — is the gap in the market's confident region or its uncertain one?
2. **Division and season** — is it structural or distributed?
3. **Disagreement** — when the model and the market disagree, who is right? This is the most
   product-relevant split: if the model loses precisely where it departs from the price, its
   "views" are the liability.
4. **Disagreement magnitude** — does a larger departure lose more?

Calibration is fitted forward only (seasons strictly before the target), so the calibrated
predictions carry no hindsight.

    python research/residual_gap.py

Writes research/RESIDUAL_GAP.md.
"""

from __future__ import annotations

import csv
import math
import statistics
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research"))

import calibration_study as cs   # noqa: E402
import report_stamp              # noqa: E402

OUT = ROOT / "research" / "RESIDUAL_GAP.md"
DELTAS = ROOT / "research" / "pilot_deltas.csv"
BOOTSTRAPS = 1000
SEED = 20261103


def load() -> list[dict]:
    rows = []
    with DELTAS.open(encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            if r["phase"] != "pilot":
                continue
            rows.append({"season": r["season"], "cluster": r["cluster"],
                         "league": r["league"], "p": float(r["p_model"]),
                         "p_market": float(r["p_market"]), "y": int(r["y"])})
    return rows


def calibrate_forward(rows: list[dict]) -> None:
    """p_cal = Platt fitted only on seasons strictly before each row's own season."""
    seasons = sorted({r["season"] for r in rows})
    for r in rows:
        r["p_cal"] = r["p"]
        # The earliest pilot season has no prior seasons to fit a map on, so it stays raw. That is
        # a property of the design, not of the season, and it must not be read as a season effect.
        r["calibrated"] = "no (no prior season)"
    for held in seasons:
        train = [{"p": r["p"], "y": r["y"]} for r in rows if r["season"] < held]
        if len(train) < 100:
            continue
        a, b = cs.fit_platt(train)
        for r in rows:
            if r["season"] == held:
                r["p_cal"] = cs.sigmoid(a * cs.logit(r["p"]) + b)
                r["calibrated"] = "yes"


def gap(r: dict) -> float:
    """Positive means the **model is worse** than the market on this fixture.

    Calibrated model loss minus market loss. Defining it this way means a positive number reads as
    "the market is ahead by this much", which is the direction every sentence in the report uses.
    """
    return cs.logloss(r["p_cal"], r["y"]) - cs.logloss(r["p_market"], r["y"])


def bh(pvalues: list[float]) -> list[float]:
    n = len(pvalues)
    order = sorted(range(n), key=lambda i: pvalues[i])
    out = [0.0] * n
    running = 1.0
    for rank in range(n - 1, -1, -1):
        i = order[rank]
        running = min(running, pvalues[i] * n / (rank + 1))
        out[i] = running
    return out


def split(rows: list[dict], key, label: str, rng, clusters: dict) -> list[dict]:
    groups: dict[str, list[int]] = {}
    for i, r in enumerate(rows):
        groups.setdefault(key(r), []).append(i)
    keys = sorted(clusters)
    out = []
    for name, idx in sorted(groups.items()):
        observed = statistics.mean(gap(rows[i]) for i in idx)
        sub = {c: [i for i in idx if rows[i]["cluster"] == c] for c in keys}
        draws = []
        for _ in range(BOOTSTRAPS):
            flat = [i for c in (keys[rng.integers(0, len(keys))] for _ in keys) for i in sub[c]]
            if flat:
                draws.append(statistics.mean(gap(rows[i]) for i in flat))
        draws.sort()
        sd = statistics.stdev(draws) if len(draws) > 2 else float("nan")
        all_mean = statistics.mean(gap(r) for r in rows)
        z = (observed - all_mean) / sd if sd and sd > 0 else 0.0
        p = 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))
        out.append({"label": name, "n": len(idx), "gap": observed,
                    "lo": draws[int(0.025 * len(draws))],
                    "hi": draws[int(0.975 * len(draws)) - 1], "p": p})
    adjusted = bh([o["p"] for o in out])
    for o, q in zip(out, adjusted):
        o["q"] = q
    return out


def table(stats: list[dict]) -> str:
    lines = ["| Split | n | Model worse by (nats) | Cluster 95% | q |",
             "| --- | --- | --- | --- | --- |"]
    for s in stats:
        lines.append(f"| {s['label']} | {s['n']:,} | {s['gap']:+.4f} | "
                     f"[{s['lo']:+.4f}, {s['hi']:+.4f}] | {s['q']:.3f} |")
    return "\n".join(lines)


def main() -> int:
    rows = load()
    calibrate_forward(rows)
    overall = statistics.mean(gap(r) for r in rows)

    rng = np.random.default_rng(SEED)
    clusters: dict[str, list[int]] = {}
    for i, r in enumerate(rows):
        clusters.setdefault(r["cluster"], []).append(i)

    def band(r):
        p = r["p_market"]
        return f"{int(p * 10) * 10}-{int(p * 10) * 10 + 10}%"

    def disagree(r):
        if r["p"] > r["p_market"]:
            return "model above market"
        if r["p"] < r["p_market"]:
            return "model below market"
        return "exact"

    def magnitude(r):
        d = abs(cs.logit(r["p"]) - cs.logit(r["p_market"]))
        if d < 0.1:
            return "<0.10"
        if d < 0.3:
            return "0.10-0.30"
        if d < 0.6:
            return "0.30-0.60"
        return ">=0.60"

    dims = [("Market-probability band", band), ("Division", lambda r: r["league"]),
            ("Season", lambda r: r["season"]),
            ("Was a forward map available", lambda r: r["calibrated"]),
            ("Disagreement direction", disagree),
            ("Disagreement magnitude (logit)", magnitude)]
    stats = {label: split(rows, key, label, rng, clusters) for label, key in dims}

    doc = f"""{report_stamp.stamp(Path(__file__))}

# Where the remaining gap sits, after forward calibration

Pilot seasons, {len(rows):,} fixtures. Calibration is fitted forward only, so no row is scored with
a map trained on its own season or later. **Positive means the model is worse** than the market on that split; the overall gap is **{overall:+.4f} nats**.

## {dims[0][0]}

{table(stats[dims[0][0]])}

## {dims[1][0]}

{table(stats[dims[1][0]])}

## {dims[2][0]}

{table(stats[dims[2][0]])}

## {dims[3][0]}

{table(stats[dims[3][0]])}

## {dims[4][0]}

{table(stats[dims[4][0]])}

## {dims[5][0]}

{table(stats[dims[5][0]])}

## Reading

The first row of the calibration split explains the season split: the earliest pilot season has no
prior seasons, so no forward map could be fitted for it and it stays raw. Its larger gap is a
property of the design, not evidence that the season was harder.

The disagreement splits are the product-relevant ones. If the gap is concentrated where the model
departs from the price, then the model's independent view is the liability and nothing is gained by
trusting it further; if the gap is uniform, the model is simply a slightly worse estimate of the
same thing everywhere.

A dimension whose q column does not clear the family is indistinguishable from noise in this search,
and the interval beside each row is the honest summary of its precision.

## Limits

- Every split is a search over the same pilot, so these are descriptions of where the loss sits,
  not confirmed subgroups.
- Cluster intervals resample division-seasons; a split defined by a fixture-level quantity inherits
  the cluster structure but does not model it.
- Closing prices without timestamps; the T−90 caveat applies to any claim about what was available.
"""
    OUT.write_text(doc, encoding="utf-8")

    for label, _ in dims:
        worst = max(stats[label], key=lambda s: s["gap"])
        print(f"{label}: worst {worst['label']} {worst['gap']:+.4f} "
              f"[{worst['lo']:+.4f},{worst['hi']:+.4f}] q={worst['q']:.3f} n={worst['n']}")
    print(f"overall gap={overall:+.4f}")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
