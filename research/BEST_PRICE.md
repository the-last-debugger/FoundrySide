<!-- generated-by: best_price.py sha256=4ca91b35d91a -->

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
