<!-- generated-by: calibration_study.py sha256=87609f019338 -->

# Calibration study — does recalibrating recover the gap?

Out-of-fold by construction: the calibrator is fitted on two pilot seasons and
evaluated on the third, rotated over all three. No calibrated prediction in this
report was produced by a map that had seen its own outcome.

| Forecast | Log loss | Brier |
| --- | --- | --- |
| Raw model | 0.6988 | 0.2520 |
| Platt (a·logit+b) | 0.6874 | 0.2472 |
| Isotonic | 0.7637 | 0.2831 |

## Per held-out season

| Held out | n | Platt a | Platt b | Raw | Platt | Isotonic |
| --- | --- | --- | --- | --- | --- | --- |
| 2021 | 2,980 | 0.416 | +0.043 | 0.7007 | 0.6872 | 0.7721 |
| 2122 | 2,986 | 0.385 | +0.025 | 0.6950 | 0.6866 | 0.7606 |
| 2223 | 2,975 | 0.422 | +0.021 | 0.7007 | 0.6886 | 0.7584 |

## Reading

Best calibrated variant: **platt**, +0.0114 nats against the raw model.
Platt moves log loss by +0.0114 and isotonic by -0.0649.

Interpretation depends on the size of that gain relative to the gap to the market
(about 0.025 nats). A calibration gain of a few thousandths leaves the gap essentially
where it was, which is the resolution failure the decomposition described. A gain
close to the whole gap would mean the model had the ordering and lost it in the
mapping — a very different diagnosis.

## Limits

- Three seasons means three folds; the fold-to-fold spread is the honest uncertainty,
  and there is no confidence interval on the aggregate beyond that.
- The calibrator is fitted on two seasons that were themselves collected online under
  the same T−90 proxy, so any timing error is shared by fit and evaluation.
- Isotonic is flexible enough to fit noise at this sample size; its per-fold numbers
  should be read against Platt's rather than on their own.
- The market comparator is unchanged and is a closing price with no observation
  timestamp.
