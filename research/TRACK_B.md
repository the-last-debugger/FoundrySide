<!-- generated-by: track_b.py sha256=e2447bc61cd7 -->

# E10 — what an abstention rule over market prices is worth

Pilot seasons only, 8,941 fixtures with a complete totals price. The rule shows the favourite side
of the totals market only when its de-vigged probability clears the threshold.

| Threshold | n | Coverage | Accuracy | Cluster 95% | Implied | Accuracy − implied | Expected return per unit |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0.50 | 8,941 | 100.0% | 57.7% | [56.8%, 58.6%] | 57.6% | +0.1% | -1.9% |
| 0.55 | 5,472 | 61.2% | 60.8% | [59.8%, 62.1%] | 60.8% | +0.1% | -2.5% |
| 0.60 | 2,545 | 28.5% | 64.0% | [62.3%, 65.8%] | 64.7% | -0.6% | -3.9% |
| 0.65 | 893 | 10.0% | 71.1% | [67.6%, 74.4%] | 69.4% | +1.7% | -1.1% |
| 0.70 | 322 | 3.6% | 77.6% | [71.7%, 81.6%] | 73.4% | +4.2% | +1.7% |
| 0.75 | 77 | 0.9% | 83.1% | [75.0%, 89.1%] | 78.6% | +4.6% | +1.5% |
| 0.80 | 23 | 0.3% | 91.3% | [82.4%, 100.0%] | 81.9% | +9.4% | +6.7% |

## Reading

Accuracy rises with the threshold, and most of that rise is **selection**: the
accuracy-minus-implied column stays near zero at every threshold, because the rule is restating
the price's own confidence rather than adding information. That is the honest description of what
an abstention product does — it shows fewer, more confident calls, and the confidence is the
market's.

The expected-return column is the correction to any temptation to describe this as profitable. At
every threshold the mean price carries the book's margin, so a user staking one unit loses on
average. A rule that improves *decisions* is not a rule that makes money, and the difference is
the margin.

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
