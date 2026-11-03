<!-- generated-by: residual_study.py sha256=294febcda075 -->

# Workstream 3 — what is left after recalibration, and what the worst errors are

Pilot seasons only. Platt calibration is fitted leave-one-season-out, so every `p_cal` is
out of fold.

## Log loss

| Forecast | Log loss |
| --- | --- |
| Raw model | 0.6988 |
| Platt (out-of-fold) | 0.6874 |
| Market | 0.6742 |

## Decomposition after calibration

| Forecast | Reliability | Resolution | Brier (raw) |
| --- | --- | --- | --- |
| Raw model | 0.0048 | 0.0030 | 0.2520 |
| Platt (out-of-fold) | 0.0000 | 0.0022 | 0.2472 |
| Market | 0.0001 | 0.0083 | 0.2407 |

The middle row is the informative one, but it is a **bin-dependent** decomposition: a monotone
map changes bin membership, so resolution can move even though the ranking does not. The AUC row
below is the rank-only check.

## Rank separation

| Forecast | AUC |
| --- | --- |
| Raw model | 0.5623 |
| Platt (out-of-fold) | 0.5618 |
| Market | 0.6073 |

AUC is invariant to recalibration, so the raw and Platt rows should be nearly identical — and
they are, by construction. The gap to the market's row is the separation deficit in a form that
does not depend on binning.

## The worst 2% of fixtures

| Property | Worst 2% | All fixtures |
| --- | --- | --- |
| n | 178 | 8941 |
| Disagrees with the market's side | 7.3% | 29.7% |
| Model in 20–40% band | 41.0% | 20.8% |
| Over-predicted (model above the outcome) | 48.9% | 49.3% |

| Band | Share of the worst tail |
| --- | --- |
| 20–30% | 41.0% |
| 70–80% | 36.0% |
| 80–90% | 12.9% |
| 10–20% | 10.1% |

## Reading

The tail profile answers one question only: whether the large losses are a *class* of fixture
the model could be taught to handle, or the upper tail of a distribution that is simply wide.
**The tail is selected on the outcomes it describes**, so this is a descriptive profile, not
evidence that no pattern exists. What it can say is narrow: within this pilot, the highest-loss
fixtures are not dominated by contrarian views, so a strategy of filtering on market disagreement
would not have addressed them. It does not establish that the tail is patternless.

## Limits

- The tail is defined by the model's own loss, so it is selected on the outcome; the profile is
  descriptive, and a "pattern" in it is not evidence that the pattern is exploitable.
- Bins are equal-width; reliability and resolution depend on that choice.
- One model, one market, pilot only, with the closing-price timing caveat.
