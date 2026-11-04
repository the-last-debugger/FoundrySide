"""E11 — the pre-registered favourite-longshot test.

The specification in `docs/PREREG-FL.md` was committed before this script existed. It fixes the
threshold-selection rule on two seasons, a single test season, the two quantities, the interval
method and the decision rule. This file implements that specification and nothing else: it does
not search thresholds on the test season, does not re-specify after seeing the result, and does
not add exclusions.

    python research/fl_test.py

Writes research/FL_TEST.md.
"""

from __future__ import annotations

import math
import statistics
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research"))

import analyse        # noqa: E402
import report_stamp   # noqa: E402

OUT = ROOT / "research" / "FL_TEST.md"
SELECTION = ("2021", "2122")
TEST = "2223"
THRESHOLDS = (0.65, 0.70, 0.75)
MIN_N = 200
BOOTSTRAPS = 2000
SEED = 20261103


def load() -> list[dict]:
    rows = []
    for r in analyse.load():
        try:
            over, under = float(r["PC>2.5"]), float(r["PC<2.5"])
            hg, ag = int(r["FTHG"]), int(r["FTAG"])
        except (KeyError, TypeError, ValueError):
            continue
        if not (math.isfinite(over) and math.isfinite(under)) or over <= 1.0 or under <= 1.0:
            continue
        p_over = 1 / over / (1 / over + 1 / under)
        favourite_over = p_over >= 0.5
        rows.append({"season": r["_season"], "cluster": f"{r['_league']}_{r['_season']}",
                     "p_side": max(p_over, 1 - p_over),
                     "price": over if favourite_over else under,
                     "correct": int((1 if hg + ag >= 3 else 0) == int(favourite_over))})
    return rows


def gap(rows: list[dict]) -> float:
    return statistics.mean(r["correct"] for r in rows) - statistics.mean(r["p_side"] for r in rows)


def ret(rows: list[dict]) -> float:
    return statistics.mean(r["correct"] * r["price"] - 1.0 for r in rows)


def cluster_interval(rows: list[dict], fn, draws: int = BOOTSTRAPS) -> tuple[float, float]:
    by_cluster: dict[str, list[dict]] = {}
    for r in rows:
        by_cluster.setdefault(r["cluster"], []).append(r)
    keys = sorted(by_cluster)
    rng = np.random.default_rng(SEED)
    out = []
    for _ in range(draws):
        picked = [by_cluster[keys[rng.integers(0, len(keys))]] for _ in keys]
        flat = [r for group in picked for r in group]
        if flat:
            out.append(fn(flat))
    out.sort()
    return out[int(0.025 * len(out))], out[int(0.975 * len(out)) - 1]


def main() -> int:
    rows = load()
    selection = [r for r in rows if r["season"] in SELECTION]
    held = [r for r in rows if r["season"] == TEST]

    selection_table = []
    chosen = None
    for tau in THRESHOLDS:
        subset = [r for r in selection if r["p_side"] >= tau]
        g = gap(subset) if subset else float("nan")
        selection_table.append((tau, len(subset), g))
        if chosen is None and len(subset) >= MIN_N and g > 0:
            chosen = tau

    if chosen is None:
        verdict = "not supported — no threshold met the selection rule, so the test stopped"
        doc = f"""{report_stamp.stamp(Path(__file__))}

# E11 — pre-registered favourite-longshot test

{verdict}

| Threshold | Selection fixtures | Gap |
| --- | --- | --- |
""" + "\n".join(f"| {t:.2f} | {n:,} | {g:+.4f} |" for t, n, g in selection_table) + f"""

The selection rule required at least {MIN_N} fixtures and a positive gap. None qualified, so the
held-out season was not examined and no claim is made about it.
"""
        OUT.write_text(doc, encoding="utf-8", newline="\n")
        print(verdict)
        return 0

    test_subset = [r for r in held if r["p_side"] >= chosen]
    g = gap(test_subset)
    r_ = ret(test_subset)
    g_lo, g_hi = cluster_interval(test_subset, gap)
    r_lo, r_hi = cluster_interval(test_subset, ret)
    supported = g_lo > 0 and r_lo > 0
    verdict = "supported" if supported else "not supported"

    doc = f"""{report_stamp.stamp(Path(__file__))}

# E11 — pre-registered favourite-longshot test

Specification committed at `docs/PREREG-FL.md` before this script existed. Selection seasons
{' and '.join(SELECTION)}; test season {TEST}; threshold chosen by the pre-registered rule and
applied unmodified.

## Threshold selection (selection seasons only)

| Threshold | Fixtures | Gap |
| --- | --- | --- |
""" + "\n".join(f"| {t:.2f} | {n:,} | {gp:+.4f} |" for t, n, gp in selection_table) + f"""

Chosen threshold: **{chosen:.2f}** (lowest meeting both the {MIN_N}-fixture floor and a positive
gap).

## Test ({TEST}, held out)

| Quantity | Value | Cluster 95% |
| --- | --- | --- |
| Fixtures | {len(test_subset):,} | — |
| Accuracy | {statistics.mean(r['correct'] for r in test_subset):.4f} | — |
| Mean implied | {statistics.mean(r['p_side'] for r in test_subset):.4f} | — |
| Gap (accuracy − implied) | {g:+.4f} | [{g_lo:+.4f}, {g_hi:+.4f}] |
| Return per unit | {r_:+.4f} | [{r_lo:+.4f}, {r_hi:+.4f}] |

## Verdict

**{verdict}.** The pre-registered decision rule required both intervals to exclude zero. Here the
gap interval is [{g_lo:+.4f}, {g_hi:+.4f}] and the return interval is [{r_lo:+.4f}, {r_hi:+.4f}]
on {len(test_subset):,} held-out fixtures.

This is the answer the test was designed to give, and it is reported as it came out: no
re-specification, no threshold search on the test season, no additional exclusions.

## Limits

- One held-out season, roughly {len(test_subset):,} fixtures at this threshold: low power, so a
  null cannot distinguish "no signal" from "signal too small to detect here".
- The threshold rule was applied to seasons that had already been read descriptively, so the
  selection seasons are not fully clean even though the test season is.
- One book, closing prices, no quote timestamps; the T−90 caveat stands.
"""
    OUT.write_text(doc, encoding="utf-8", newline="\n")

    print(f"chosen={chosen:.2f} n={len(test_subset)} gap={g:+.4f} [{g_lo:+.4f},{g_hi:+.4f}] "
          f"ret={r_:+.4f} [{r_lo:+.4f},{r_hi:+.4f}] supported={supported}")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
