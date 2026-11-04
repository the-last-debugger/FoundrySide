<!-- generated-by: track_b.py sha256=6ccb7593510a -->

# E10 — what an abstention rule over market prices is worth

Pilot seasons only, 8,941 fixtures with a complete totals price. The rule shows the favourite side
of the totals market only when its de-vigged probability clears the threshold.

| Threshold | n | Coverage | Accuracy | Gap vs implied (95%) | Return per unit (95%) | Log-growth at 1% stake (95%) |
| --- | --- | --- | --- | --- | --- | --- |
| 0.50 | 8,941 | 100.0% | 57.7% | +0.1% [-0.6%, +0.9%] | -2.9% [-4.1%, -1.5%] | -0.0003 [-0.0004, -0.0002] |
| 0.55 | 5,472 | 61.2% | 60.8% | +0.1% [-1.0%, +1.1%] | -3.1% [-4.8%, -1.3%] | -0.0003 [-0.0005, -0.0002] |
| 0.60 | 2,545 | 28.5% | 64.0% | -0.6% [-2.2%, +0.9%] | -4.4% [-6.8%, -2.1%] | -0.0005 [-0.0007, -0.0002] |
| 0.65 | 893 | 10.0% | 71.1% | +1.7% [-1.5%, +4.7%] | -1.5% [-6.0%, +2.6%] | -0.0002 [-0.0006, +0.0002] |
| 0.70 | 322 | 3.6% | 77.6% | +4.2% [-0.8%, +7.6%] | +1.5% [-5.2%, +6.0%] | +0.0001 [-0.0005, +0.0006] |
| 0.75 | 77 | 0.9% | 83.1% | +4.6% [-2.4%, +10.5%] | +1.3% [-7.2%, +8.7%] | +0.0001 [-0.0007, +0.0009] |
| 0.80 | 23 | 0.3% | 91.3% | +9.4% [+0.2%, +18.4%] | +6.5% [-4.2%, +17.0%] | +0.0006 [-0.0004, +0.0017] |

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

This is what Track B can honestly offer: fewer decisions, each more likely right, with the
uncertainty stated. It is not an edge, and no threshold makes it one.

## What would make Track B stronger

- A decision-theoretic utility model with the user's actual stakes and risk preferences, rather
  than the flat one-unit return computed here.
- A measured comparison against real users, which this corpus cannot provide.
- Information beyond the price, which is Track A and has failed on this data.

## Limits

- One market, one book, pilot seasons. The confirmatory slice is untouched.
- The pricing is the recorded closing price; no quote timestamp exists, so the T−90 caveat stands.
- Expected return assumes the user always stakes when the rule fires; a real user may not.
