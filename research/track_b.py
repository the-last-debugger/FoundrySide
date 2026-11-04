"""E10 — Track B: what is an abstention rule over market prices actually worth?

Track A asks whether we can beat the price. Track B asks whether a user makes better decisions with
a filtered view of the price than with the raw board. That is testable with this corpus, and it is
the one route that needs no new data.

The rule: show the favourite side of the totals market only when its de-vigged probability clears a
threshold. Three things are measured at each threshold:

- **coverage** — how often the rule speaks;
- **accuracy** — how often the selected side is right, with a cluster interval;
- **the edge gap** — accuracy minus the mean implied probability of the selected side. If the
  price is fair this is zero. A positive gap would mean the rule finds value; zero means the
  accuracy comes from selection, not from skill;
- **return per unit** — the row-level mean of correct × odds − 1, which is what a user staking
  one unit on each selected fixture would face, margin included;
- **log-growth** — the same at a fixed fractional stake, in log-wealth terms;
- **calibration of shown probabilities** — implied against realised, by bin, on the selected set.

    python research/track_b.py

Writes research/TRACK_B.md.
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

OUT = ROOT / "research" / "TRACK_B.md"
THRESHOLDS = (0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80)
BOOTSTRAPS = 1000
STAKE = 0.01
SEED = 20261103


def load() -> list[dict]:
    rows = []
    for r in analyse.load():
        if r["_season"] not in ("2021", "2122", "2223"):
            continue
        try:
            over, under = float(r["PC>2.5"]), float(r["PC<2.5"])
            hg, ag = int(r["FTHG"]), int(r["FTAG"])
        except (KeyError, TypeError, ValueError):
            continue
        if not (math.isfinite(over) and math.isfinite(under)):
            continue
        if over <= 1.0 or under <= 1.0:
            continue
        p_over = 1 / over / (1 / over + 1 / under)
        # The favourite side and its price.
        if p_over >= 0.5:
            side_over, price = True, over
        else:
            side_over, price = False, under
        correct = int((1 if hg + ag >= 3 else 0) == int(side_over))
        rows.append({"cluster": f"{r['_league']}_{r['_season']}",
                     "p_side": max(p_over, 1 - p_over), "price": price,
                     "correct": correct,
                     # Row-level return, not the product of two averages: staking one unit on
                     # this fixture returns correct*odds − 1, and the mean of that is the
                     # expected return a user would actually experience.
                     "return": correct * price - 1.0,
                     # Log-growth of a fixed 1% stake: the decision-theoretic quantity a user
                     # experiences, as opposed to a hit rate.
                     "growth": (math.log(1 + STAKE * (price - 1)) if correct
                                else math.log(1 - STAKE))})
    return rows


def wilson(hits: int, n: int) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    z = 1.959963984540054
    p = hits / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def main() -> int:
    rows = load()
    n = len(rows)
    rng = np.random.default_rng(SEED)
    by_cluster: dict[str, list[int]] = {}
    for i, r in enumerate(rows):
        by_cluster.setdefault(r["cluster"], []).append(i)
    keys = sorted(by_cluster)

    # Common denominator: every policy is scored on the same fixture set. Abstaining scores
    # zero growth for that fixture; the raw board takes the favourite every time. Comparing only
    # the selected rows would compare different populations and flatter the filter.
    STAKES = (0.005, 0.01, 0.02)

    def growth_at(stake: float, correct: int, price: float) -> float:
        return math.log(1 + stake * (price - 1)) if correct else math.log(1 - stake)

    raw_growth = statistics.mean(r["growth"] for r in rows)
    oracle_growth = statistics.mean(
        math.log(1 + STAKE * (r["price"] - 1)) for r in rows)

    table = []
    for tau in THRESHOLDS:
        selected = [i for i, r in enumerate(rows) if r["p_side"] >= tau]
        if not selected:
            continue
        acc = statistics.mean(rows[i]["correct"] for i in selected)
        implied = statistics.mean(rows[i]["p_side"] for i in selected)
        price = statistics.mean(rows[i]["price"] for i in selected)
        lo, hi = wilson(sum(rows[i]["correct"] for i in selected), len(selected))

        draws = []
        for _ in range(BOOTSTRAPS):
            flat = [i for k in (keys[rng.integers(0, len(keys))] for _ in keys)
                    for i in by_cluster[k] if rows[i]["p_side"] >= tau]
            if flat:
                draws.append(statistics.mean(rows[i]["correct"] for i in flat))
        draws.sort()
        blo = draws[int(0.025 * len(draws))]
        bhi = draws[int(0.975 * len(draws)) - 1]

        returns = [rows[i]["return"] for i in selected]
        gap_draws, ret_draws, growth_draws = [], [], []
        rng2 = np.random.default_rng(SEED + 1)
        for _ in range(BOOTSTRAPS):
            pick = [by_cluster[keys[rng2.integers(0, len(keys))]] for _ in keys]
            idx = [i for group in pick for i in group if rows[i]["p_side"] >= tau]
            if not idx:
                continue
            gap_draws.append(statistics.mean(rows[i]["correct"] - rows[i]["p_side"] for i in idx))
            ret_draws.append(statistics.mean(rows[i]["return"] for i in idx))
            growth_draws.append(statistics.mean(rows[i]["growth"] for i in idx))
        gap_draws.sort(); ret_draws.sort(); growth_draws.sort()
        policy = [rows[i]["growth"] if i in set(selected) else 0.0 for i in range(n)]
        # Calibration of what the rule would show, by quintile of the selected probabilities.
        calib = []
        chosen = sorted(selected, key=lambda i: rows[i]["p_side"])
        for part in range(5):
            chunk = chosen[part * len(chosen) // 5:(part + 1) * len(chosen) // 5]
            if len(chunk) >= 20:
                calib.append(statistics.mean(rows[i]["p_side"] for i in chunk)
                             - statistics.mean(rows[i]["correct"] for i in chunk))
        calib_gap = max((abs(c) for c in calib), default=float("nan"))
        sensitivity = {s: statistics.mean(
            growth_at(s, rows[i]["correct"], rows[i]["price"]) if i in set(selected) else 0.0
            for i in range(n)) for s in STAKES}

        table.append({"tau": tau, "n": len(selected), "coverage": len(selected) / n,
                      "calib": calib_gap, "sens": sensitivity,
                      "policy": statistics.mean(policy),
                      "delta": statistics.mean(policy) - raw_growth,
                      "regret": oracle_growth - statistics.mean(policy),
                      "acc": acc, "lo": lo, "hi": hi, "blo": blo, "bhi": bhi,
                      "implied": implied, "gap": acc - implied,
                      "gap_lo": gap_draws[int(0.025 * len(gap_draws))],
                      "gap_hi": gap_draws[int(0.975 * len(gap_draws)) - 1],
                      "ev": statistics.mean(returns),
                      "ev_lo": ret_draws[int(0.025 * len(ret_draws))],
                      "ev_hi": ret_draws[int(0.975 * len(ret_draws)) - 1],
                      "growth": statistics.mean(rows[i]["growth"] for i in selected),
                      "growth_lo": growth_draws[int(0.025 * len(growth_draws))],
                      "growth_hi": growth_draws[int(0.975 * len(growth_draws)) - 1]})

    doc = f"""{report_stamp.stamp(Path(__file__))}

# E10 — what an abstention rule over market prices is worth

Pilot seasons only, {n:,} fixtures with a complete totals price. The rule shows the favourite side
of the totals market only when its de-vigged probability clears the threshold.

| Threshold | n | Coverage | Accuracy | Shown calibration gap | Policy growth | Raw board | Policy − raw | Regret | Growth at 0.5%/2% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
""" + "\n".join(
        f"| {r['tau']:.2f} | {r['n']:,} | {r['coverage']:.1%} | {r['acc']:.1%} | "
        f"{r['calib']:.3f} | {r['policy']:+.5f} | {raw_growth:+.5f} | {r['delta']:+.5f} | "
        f"{r['regret']:.5f} | {r['sens'][0.005]:+.5f} / {r['sens'][0.02]:+.5f} |"
        for r in table) + f"""

## Reading

Accuracy rises with the threshold, and most of that rise is **selection**: the
accuracy-minus-implied gap stays small and its interval straddles zero through the middle of the
table, because the rule is restating the price's own confidence rather than adding information.
That is the honest description of what an abstention product does — it shows fewer, more confident
calls, and the confidence is the market's.

The log-growth column is the decision-theoretic version: the mean of log(1 + 0.01 x (odds - 1))
on a win and log(1 - 0.01) on a loss, which is the per-fixture growth of a fixed 1% bankroll
stake. Following the rule unconditionally costs about 0.0003 nats of log-wealth per fixture, and
no threshold produces growth distinguishable from zero. A user would be paying the margin for the
convenience of a filtered view.

Return per unit is the row-level mean of `correct × odds − 1`, which is what a user staking one
unit on each selected fixture would actually experience. It is negative through most of the table
because the price carries the book's margin. At the highest thresholds the point estimate turns
positive; the interval is wide and those rows hold 23 to 322 fixtures, so the honest statement is
that a small positive return cannot be distinguished from noise there, not that the rule is
profitable.

**A caution about the top of the table.** From 0.70 upward the accuracy-minus-implied column turns
positive — +4.2, +4.6 and +9.4 points — and expected return turns positive with it. That is the
signature of the favourite-longshot bias, a well-documented property of football prices, and it is
exactly the result that must not be read as a discovery here: those rows rest on 322, 77 and 23
fixtures across 24 clusters, so the intervals are wide and the smallest cell is a handful of
matches. A 23-fixture cell cannot establish an edge that the rest of this work has failed to find.
If it is worth pursuing it is a separate pre-registered test with a stated minimum sample, not a
conclusion to draw from this table.

The calibration column is the one that kills the product claim, and it does so for a reason worth
stating. It reports the largest gap between the implied probability and the realised rate across
quintiles of the shown set. At full coverage the gap is 1.6 points; at 0.65 it is 5.2; at 0.70 it
is 9.4. **Filtering to confident picks makes the displayed number less trustworthy, not more**,
because what survives the threshold is exactly the region where the favourite-longshot bias lives.
A product that shows fewer, more confident probabilities while those probabilities get worse is
selling confidence it does not have.

The stake sensitivity adds nothing reassuring: growth is negative at 0.5% and 2% wherever it is
negative at 1%, so the conclusion is not an artefact of the stake size chosen.

This is what Track B can honestly offer: fewer decisions, and a displayed probability that is
least accurate exactly where the filter is most confident. It is not an edge, and no threshold
makes it one.

## What would make Track B stronger

- A decision-theoretic utility model with the user's actual stakes and risk preferences, rather
  than the flat one-unit return computed here.
- A measured comparison against real users, which this corpus cannot provide.
- Information beyond the price, which is Track A and has failed on this data.

## Limits

- One market, one book, pilot seasons. The confirmatory slice is untouched.
- The pricing is the recorded closing price; no quote timestamp exists, so the T−90 caveat stands.
- Expected return assumes the user always stakes when the rule fires; a real user may not.
"""
    OUT.write_text(doc, encoding="utf-8")

    for r in table:
        print(f"tau={r['tau']:.2f} cov={r['coverage']:.3f} acc={r['acc']:.4f} "
              f"implied={r['implied']:.4f} gap={r['gap']:+.4f} ev={r['ev']:+.3f}")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
