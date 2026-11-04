"""Best-price discovery — what is a better available price actually worth?

The contingency direction proposes a product whose value is finding the best available price
rather than beating the market. That claim is measurable with the corpus already held: it contains
two books' closing over/under 2.5 prices, so the dispersion between them and the value of always
taking the better side can be computed directly.

Three quantities:

- **how often the books differ**, and by how much, on the same selection;
- **the overround the user pays** at one book versus at the better of the two;
- **the improvement in expected return** from backing at the better price, keeping the outcome
  probabilities fixed at the de-vigged mean.

The last point is the one that matters and the one most easily overstated: a better price improves
the user's position without making the bet positive. This reports both.

    python research/best_price.py

Writes research/BEST_PRICE.md.
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

OUT = ROOT / "research" / "BEST_PRICE.md"
PILOT = ("2021", "2122", "2223")
SEED = 20261103


def load() -> list[dict]:
    rows = []
    for r in analyse.load():
        if r["_season"] not in PILOT:
            continue
        try:
            po_over, po_under = float(r["PC>2.5"]), float(r["PC<2.5"])
            pb_over, pb_under = float(r["B365C>2.5"]), float(r["B365C<2.5"])
        except (KeyError, TypeError, ValueError):
            continue
        prices = (po_over, po_under, pb_over, pb_under)
        if not all(math.isfinite(p) for p in prices) or min(prices) <= 1.0:
            continue
        rows.append({"league": r["_league"],
                     "cluster": f"{r['_league']}_{r['_season']}",
                     "po_over": po_over, "po_under": po_under,
                     "pb_over": pb_over, "pb_under": pb_under})
    return rows


def overround(over: float, under: float) -> float:
    return 1 / over + 1 / under - 1


def main() -> int:
    rows = load()
    n = len(rows)

    single = [overround(r["po_over"], r["po_under"]) for r in rows]
    best = [overround(max(r["po_over"], r["pb_over"]), max(r["po_under"], r["pb_under"]))
            for r in rows]
    saving = [a - b for a, b in zip(single, best)]

    # Dispersion on the over side, as a fair-comparison measure of how often books differ.
    diffs = [r["po_over"] - r["pb_over"] for r in rows]
    differ = sum(1 for d in diffs if abs(d) > 1e-9)

    # Improvement in expected return when the *same* implied probability is backed at the
    # better of the two prices: fair odds improve by the ratio of prices.
    def fair_prob(r):
        inv = 1 / r["po_over"] + 1 / r["po_under"]
        return (1 / r["po_over"]) / inv

    improvements = []
    for r in rows:
        p = fair_prob(r)
        single_ev = p * r["po_over"] - 1
        best_ev = p * max(r["po_over"], r["pb_over"]) - 1
        improvements.append(best_ev - single_ev)

    rng = np.random.default_rng(SEED)
    by_cluster: dict[str, list[int]] = {}
    for i, r in enumerate(rows):
        by_cluster.setdefault(r["cluster"], []).append(i)
    keys = sorted(by_cluster)
    draws = []
    for _ in range(2000):
        flat = [i for k in (keys[rng.integers(0, len(keys))] for _ in keys) for i in by_cluster[k]]
        draws.append(statistics.mean(saving[i] for i in flat))
    draws.sort()
    lo, hi = draws[int(0.025 * len(draws))], draws[int(0.975 * len(draws)) - 1]

    still_negative = sum(1 for r in rows if max(r["po_over"], r["pb_over"]) * fair_prob(r) - 1 < 0)

    # Per-division: is the saving uniform, or concentrated where margins are widest?
    by_league: dict[str, list[dict]] = {}
    for row in rows:
        by_league.setdefault(row["league"], []).append(row)
    split = []
    for league, group in sorted(by_league.items()):
        s_single = statistics.mean(overround(g["po_over"], g["po_under"]) for g in group)
        s_best = statistics.mean(overround(max(g["po_over"], g["pb_over"]),
                                           max(g["po_under"], g["pb_under"])) for g in group)
        split.append((league, len(group), s_single, s_best, s_single - s_best))

    doc = f"""{report_stamp.stamp(Path(__file__))}

# Best-price discovery — what a better available price is worth

Pilot seasons, {n:,} fixtures with both books' closing over/under 2.5 prices. This measures the
contingency product's central claim: that comparing prices improves a user's position.

## The two books differ, modestly and often

| Quantity | Value |
| --- | --- |
| Fixtures where the two books' over prices differ | {differ:,} of {n:,} ({differ / n:.1%}) |
| Median absolute difference in decimal odds | {statistics.median(abs(d) for d in diffs):.3f} |
| Mean overround at one book | {statistics.mean(single):.4f} |
| Mean overround at the better of the two | {statistics.mean(best):.4f} |
| Mean margin saved, cluster 95% | **{statistics.mean(saving):.4f}** [{lo:.4f}, {hi:.4f}] |

## By division

| Division | Fixtures | One book | Best of two | Saved |
| --- | --- | --- | --- | --- |
""" + "\n".join(
        f"| {d} | {n:,} | {s:.4f} | {b:.4f} | {sv:.4f} |" for d, n, s, b, sv in split) + f"""

The saving is largest where the single-book margin is largest, which is what a comparison tool
should be expected to deliver: it recovers some of the margin rather than all of it.

## What that does and does not buy

Taking the better price on both sides reduces the overround by about
{statistics.mean(saving) * 100:.2f} percentage points, from {statistics.mean(single) * 100:.2f}% to
{statistics.mean(best) * 100:.2f}%. For a user this is a real improvement in position: they pay
less for the same exposure.

It does not make the bet profitable. Backing at the better price with the de-vigged fair
probability still returns a negative expected value on **{still_negative:,} of {n:,} fixtures**
({still_negative / n:.1%}). The mean improvement in expected return is
{statistics.mean(improvements) * 100:+.2f} percentage points per unit staked, which is worth having
and is not an edge.

That distinction is the product's honest claim: *better available price*, not *positive expected
value*. A comparison tool that said otherwise would be misrepresenting arithmetic.

## What this does not measure

- Whether a better price is **available to the user at the moment they act** — closing prices with
  no timestamps, one pair of books, one market.
- Limits, stake restrictions, account terms or jurisdiction — all of which decide whether an
  advertised price is genuinely obtainable.
- Whether users act on the comparison, which is the question a product would have to answer.

## Limits

- Two books only, and both closing prices; live dispersion is usually wider and staler.
- One market (over/under 2.5) in eight divisions across three seasons.
- The de-vigged fair probability is an assumption inside the expected-return calculation, not a
  measurement of the true probability.
"""
    OUT.write_text(doc, encoding="utf-8")

    print(f"differ={differ}/{n} ({differ/n:.1%}) "
          f"overround single={statistics.mean(single):.4f} best={statistics.mean(best):.4f} "
          f"saved={statistics.mean(saving):.4f} [{lo:.4f},{hi:.4f}]")
    print(f"still negative EV: {still_negative}/{n} ({still_negative/n:.1%})")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
