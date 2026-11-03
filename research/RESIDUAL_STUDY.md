<!-- generated-by: residual_study.py sha256=b5cf22db32e7 -->

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

The middle row of the first table is the one that matters: if recalibration collapses
reliability while resolution stays where it was, the remaining deficit is information and no
further calibration work can help.

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
Concentration on disagreeing-with-the-market fixtures would suggest the model is asserting a
view; concentration in a band would suggest overconfidence; neither would suggest a fix on its
own.

## Limits

- The tail is defined by the model's own loss, so it is selected on the outcome; the profile is
  descriptive, and a "pattern" in it is not evidence that the pattern is exploitable.
- Bins are equal-width; reliability and resolution depend on that choice.
- One model, one market, pilot only, with the closing-price timing caveat.
