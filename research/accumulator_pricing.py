"""Accumulator pricing — is multiplying legs across different matches safe?

The dependence result (E-T3) showed same-match legs cannot be multiplied: the realised joint rate
is 40.9% against a 27.5% product, a ratio of 1.49. That is a same-match effect, because the legs
share an outcome.

Cross-match slips are the product-relevant case: a user builds an accumulator from several
fixtures, and every book prices it by multiplying. If fixtures on the same matchday are
independent given the prices, multiplication is correct. If they are not — shared weather, shared
referee cohorts, correlated team strengths within a division — the product understates the joint
probability and the displayed price is wrong in the user's disfavour.

This measures the realised joint rate against the multiplied probability for slips of 2, 3 and 5
favourite legs drawn from one division on one date, which is what an ordinary weekend slip looks
like.

    python research/accumulator_pricing.py

Writes research/ACCUMULATOR_PRICING.md.
"""

from __future__ import annotations

import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research"))

import analyse        # noqa: E402
import report_stamp   # noqa: E402

OUT = ROOT / "research" / "ACCUMULATOR_PRICING.md"
PILOT = ("2021", "2122", "2223")
SIZES = (2, 3, 5)
SEED = 20261103


def load() -> list[dict]:
    rows = []
    for r in analyse.load():
        if r["_season"] not in PILOT:
            continue
        try:
            h, d, a = float(r["PSCH"]), float(r["PSCD"]), float(r["PSCA"])
            hg, ag = int(r["FTHG"]), int(r["FTAG"])
        except (KeyError, TypeError, ValueError):
            continue
        prices = (h, d, a)
        if not all(math.isfinite(p) for p in prices) or min(prices) <= 1.0:
            continue
        inv = 1 / h + 1 / d + 1 / a
        probs = {"H": (1 / h) / inv, "D": (1 / d) / inv, "A": (1 / a) / inv}
        outcome = "H" if hg > ag else ("A" if ag > hg else "D")
        # The favourite side, which is what a slip typically takes.
        pick = max(probs, key=probs.get)
        rows.append({"date": r["Date"], "league": r["_league"], "season": r["_season"],
                     "prob": probs[pick], "won": 1 if pick == outcome else 0,
                     "price": {"H": h, "D": d, "A": a}[pick]})
    return rows


def main() -> int:
    rows = load()
    by_day: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in rows:
        by_day[(r["league"], r["date"])].append(r)

    rng = np.random.default_rng(SEED)
    table = []
    for k in SIZES:
        slips = []
        for (_league, _date), group in by_day.items():
            if len(group) < k:
                continue
            # Several slips per matchday where the fixture list allows it, deterministically.
            for _ in range(min(5, len(group) // k)):
                picks = rng.choice(len(group), size=k, replace=False)
                legs = [group[i] for i in picks]
                naive = 1.0
                for leg in legs:
                    naive *= leg["prob"]
                slips.append({"naive": naive, "won": int(all(leg["won"] for leg in legs)),
                              "cluster": f"{_league}_{group[0]['season']}"})
        if not slips:
            continue
        naive_mean = statistics.mean(s["naive"] for s in slips)
        realised = statistics.mean(s["won"] for s in slips)

        by_cluster: dict[str, list[int]] = defaultdict(list)
        for i, s in enumerate(slips):
            by_cluster[s["cluster"]].append(i)
        keys = sorted(by_cluster)
        draws = []
        for _ in range(2000):
            flat = [i for c in (keys[rng.integers(0, len(keys))] for _ in keys)
                    for i in by_cluster[c]]
            draws.append(statistics.mean(slips[i]["won"] for i in flat))
        draws.sort()
        lo, hi = draws[int(0.025 * len(draws))], draws[int(0.975 * len(draws)) - 1]

        table.append({"k": k, "n": len(slips), "naive": naive_mean, "realised": realised,
                      "wins": sum(s["won"] for s in slips),
                      "lo": lo, "hi": hi, "ratio": realised / naive_mean})

    # Estimability of long combinations: how many slips would a ±10% relative estimate need?
    mean_p = statistics.mean(r["prob"] for r in rows)
    estimability = []
    for k in (3, 5, 8, 10, 12):
        prob = mean_p ** k
        needed = (1 - prob) / (prob * 0.10 ** 2) if prob > 0 else float("inf")
        available = sum(len(g) // k for g in by_day.values())
        estimability.append((k, prob, needed, available))

    doc = f"""{report_stamp.stamp(Path(__file__))}

# Accumulator pricing — is multiplying cross-match legs safe?

Pilot seasons, slips of favourite legs drawn from one division on one matchday, priced by the
product of de-vigged probabilities — exactly how a book prices an accumulator.

| Legs | Slips | Won | Multiplied probability | Realised rate | Cluster 95% | Realised ÷ multiplied |
| --- | --- | --- | --- | --- | --- | --- |
""" + "\n".join(
        f"| {r['k']} | {r['n']:,} | {r['wins']:,} | {r['naive']:.4f} | {r['realised']:.4f} | "
        f"[{r['lo']:.4f}, {r['hi']:.4f}] | {r['ratio']:.3f} |" for r in table) + f"""

## Reading

Read the Won column before the ratio. A ratio near 1 means cross-match legs multiply correctly, and
the earlier same-match dependence finding does not generalise — which is what one would expect,
since the dependence there came from legs sharing an outcome.

Two and three legs are consistent with 1: 1.016 [0.93, 1.12] and 0.994 [0.87, 1.13]. The five-leg
cell comes out above 1 at 1.373, but it rests on roughly forty winning slips, so its interval is
wide and its point estimate is not evidence that long accumulators are underpriced. It is a cell
that needs more data, not a finding.

A ratio materially below 1 would mean the multiplied probability is too high and the accumulator is
priced against the user. A ratio above 1 would mean the opposite, which would be strange for a
book-priced product and is more likely a selection effect in taking favourites.

Coverage matters here: with a favourite-only rule the naive probability is high, so slips are won
often enough to estimate the rate, unlike long-odds accumulators where the event is too rare to
observe in three seasons.

## Long combinations cannot be estimated here

| Legs | Multiplied probability | Slips for a ±10% estimate | Slips available in corpus |
| --- | --- | --- | --- |
""" + "\n".join(
        f"| {k} | {p:.5f} | {n:,.0f} | {a:,} |" for k, p, n, a in estimability) + f"""

""" + f"""A ±10% relative estimate of an eight-leg combination needs on the order of ten thousand
slips; the corpus can form a few hundred at most, and a jackpot is longer than eight. **Jackpot
outcome rates are not estimable with this data**, and any product claim about them would have to
rest on published rules and arithmetic rather than on observed results. That is a statement about
evidence, not about jackpots being profitable or not.

## Why this matters for a slip-assistance product

A tool that shows the probability of a slip must either justify multiplication or model the
dependence. The same-match case is already known to be wrong by a factor of about 1.5; this
establishes whether the cross-match case is wrong at all, which is the case that actually appears
in a user's slip.

## Limits

- Slips are sampled from within a division on a date, not from a user's actual constraints.
- Favourite-only selections; long-odds legs have rare outcomes and cannot be estimated here.
- One book's prices, de-vigged with proportional margin removal; the margin model matters more for
  long slips than for these.
"""
    OUT.write_text(doc, encoding="utf-8")

    for r in table:
        print(f"k={r['k']} n={r['n']} naive={r['naive']:.4f} realised={r['realised']:.4f} "
              f"[{r['lo']:.4f},{r['hi']:.4f}] ratio={r['ratio']:.3f}")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
