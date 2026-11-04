<!-- generated-by: best_price.py sha256=48d904a1ed50 -->

# Best-price discovery — what a better available price is worth

Pilot seasons, 8,938 fixtures with both books' closing over/under 2.5 prices. This measures the
contingency product's central claim: that comparing prices improves a user's position.

## The two books differ, modestly and often

| Quantity | Value |
| --- | --- |
| Fixtures where the two books' over prices differ | 8,319 of 8,938 (93.1%) |
| Median absolute difference in decimal odds | 0.040 |
| Mean overround at one book | 0.0308 |
| Mean overround at the better of the two | 0.0291 |
| Mean margin saved, cluster 95% | **0.0017** [0.0014, 0.0020] |

## By division

| Division | Fixtures | One book | Best of two | Saved |
| --- | --- | --- | --- | --- |
| D1 | 897 | 0.0303 | 0.0275 | 0.0028 |
| E0 | 1,138 | 0.0288 | 0.0272 | 0.0017 |
| E1 | 1,654 | 0.0320 | 0.0307 | 0.0013 |
| F1 | 1,138 | 0.0289 | 0.0265 | 0.0024 |
| I1 | 1,139 | 0.0292 | 0.0270 | 0.0021 |
| N1 | 916 | 0.0351 | 0.0339 | 0.0012 |
| P1 | 917 | 0.0339 | 0.0333 | 0.0006 |
| SP1 | 1,139 | 0.0293 | 0.0275 | 0.0018 |

The saving is largest where the single-book margin is largest, which is what a comparison tool
should be expected to deliver: it recovers some of the margin rather than all of it.

## What that does and does not buy

Taking the better price on both sides reduces the overround by about
0.17 percentage points, from 3.08% to
2.91%. For a user this is a real improvement in position: they pay
less for the same exposure.

It does not make the bet profitable. Backing at the better price with the de-vigged fair
probability still returns a negative expected value on **8,856 of 8,938 fixtures**
(99.1%). The mean improvement in expected return is
+0.14 percentage points per unit staked, which is worth having
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
