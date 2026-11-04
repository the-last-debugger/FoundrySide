<!-- generated-by: track_b.py sha256=2e2f861ad358 -->

# E10 — what an abstention rule over market prices is worth

Pilot seasons only, 8,941 fixtures with a complete totals price. The rule shows the favourite side
of the totals market only when its de-vigged probability clears the threshold.

| Threshold | n | Coverage | Accuracy | Shown calibration gap | Policy growth | Raw board | Policy − raw | Regret | Growth at 0.5%/2% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0.50 | 8,941 | 100.0% | 57.7% | 0.016 | -0.00032 | -0.00032 | +0.00000 | 0.00730 | -0.00015 / -0.00071 |
| 0.55 | 5,472 | 61.2% | 60.8% | 0.018 | -0.00021 | -0.00032 | +0.00012 | 0.00719 | -0.00010 / -0.00045 |
| 0.60 | 2,545 | 28.5% | 64.0% | 0.031 | -0.00013 | -0.00032 | +0.00019 | 0.00712 | -0.00007 / -0.00028 |
| 0.65 | 893 | 10.0% | 71.1% | 0.052 | -0.00002 | -0.00032 | +0.00030 | 0.00700 | -0.00001 / -0.00004 |
| 0.70 | 322 | 3.6% | 77.6% | 0.094 | +0.00000 | -0.00032 | +0.00033 | 0.00698 | +0.00000 / +0.00001 |
| 0.75 | 77 | 0.9% | 83.1% | nan | +0.00000 | -0.00032 | +0.00032 | 0.00698 | +0.00000 / +0.00000 |
| 0.80 | 23 | 0.3% | 91.3% | nan | +0.00000 | -0.00032 | +0.00032 | 0.00698 | +0.00000 / +0.00000 |

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
