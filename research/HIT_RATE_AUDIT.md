<!-- generated-by: hit_rate_audit.py sha256=8e9db92704f8 -->

# Hit-rate and metric audit

Pre-registered at `docs/PREREG-HITRATE.md` before these numbers were computed. Target: **Over 2.5
goals**, 8,941 pilot fixtures. The market column is the de-vigged Pinnacle closing price for the
same market; the model is the prequential forecast. Identical rows throughout.

## Hard picks at 0.5

| Picker | Correct | Accuracy | Balanced accuracy | Precision (Over / Under) | Recall (Over / Under) |
| --- | --- | --- | --- | --- | --- |
| market | 5,155 / 8,941 | 0.5766 | 0.5765 | 0.5829 / 0.5701 | 0.5780 / 0.5751 |
| model (raw) | 4,855 / 8,941 | 0.5430 | 0.5432 | 0.5515 / 0.5351 | 0.5259 / 0.5605 |
| model (forward-calibrated) | 4,862 / 8,941 | 0.5438 | 0.5438 | 0.5505 / 0.5371 | 0.5440 / 0.5435 |

### Confusion matrices

| Picker | TP | FP | TN | FN |
| --- | --- | --- | --- | --- |
| market | 2,619 | 1,874 | 2,536 | 1,912 |
| model (raw) | 2,383 | 1,938 | 2,472 | 2,148 |
| model (forward-calibrated) | 2,465 | 2,013 | 2,397 | 2,066 |

### The paired comparison

| | Count |
| --- | --- |
| Model right, market wrong | 1,176 |
| Market right, model wrong | 1,476 |
| Discordant pairs | 2,652 |

Accuracy difference (model − market): **-0.0336**,
cluster bootstrap 95% **[-0.0459, -0.0214]**. McNemar-style binomial p = **6.17e-09**,
which treats fixtures as independent and is reported only for comparability; the bootstrap is the
one that respects the cluster structure.

## Probability metrics on the same rows

| Measure | Market | Model (raw) | Model (calibrated) |
| --- | --- | --- | --- |
| Log loss | 0.6742 | 0.6988 | 0.6920 |
| Brier | 0.2407 | 0.2520 | 0.2491 |
| ROC AUC | 0.6073 | 0.5623 | 0.5603 |
| Reliability | 0.0001 | 0.0048 | 0.0016 |
| Resolution | 0.0083 | 0.0030 | 0.0025 |

Calibration slope from a fit on all rows: **0.407**, intercept +0.030. A slope near
0.4 means the model's logits are roughly two and a half times too spread.

## The 1X2 baseline is a different task

The **53.3% favourite accuracy** in `RESULTS_T0_T1_T3.md` is home/draw/away on 14,802 fixtures. The
model audited here predicts Over 2.5 on 8,941 pilot fixtures. **No 1X2 model predictions exist in
this repository**, so we have not compared our model's 1X2 pick accuracy against 1X2 favourites,
and this report does not manufacture that comparison from the totals model. The 53.3% figure stands
as a market-only benchmark for a task the model has not been asked to do.

## Does a higher hit rate imply better decisions?

Acceptance by market-probability band, market against realised:

| Band | Fixtures | Implied | Realised | Realised − implied |
| --- | --- | --- | --- | --- |
| 20-30% | 19 | 0.281 | 0.263 | -0.018 |
| 30-40% | 919 | 0.371 | 0.386 | +0.016 |
| 40-50% | 3,510 | 0.451 | 0.442 | -0.009 |
| 50-60% | 2,902 | 0.545 | 0.543 | -0.002 |
| 60-70% | 1,289 | 0.638 | 0.626 | -0.012 |
| 70-80% | 279 | 0.728 | 0.767 | +0.039 |
| 80-90% | 23 | 0.819 | 0.913 | +0.094 |

Accuracy and value are not the same quantity. A picker can be right more often and still lose,
because the price already charges for the probability: the second column is what the outcome cost,
the third is what happened. **Expected value depends on the price paid, not on the hit rate**, and
this corpus records closing prices with no timestamp, so no executable value is claimed.

## What this audit supports

**Both senses of worse are supported, and neither is marginal.**

The model's hard-pick accuracy is 0.5430 against the market's
0.5766: a difference of
-0.0336 with a cluster interval of
[-0.0459, -0.0214], which excludes zero. The paired counts say the same thing without averaging:
on 1,176 fixtures the model was right where the market was wrong, and on
1,476 the reverse. The model does not merely score badly; it picks the wrong
side more often, by enough that a user would notice.

So the ordering is: worse at ranking (AUC), worse at probabilities (log loss, resolution), and
worse at the hard pick (accuracy). The one thing that is *not* worse is calibration after the fact,
which is recoverable and recovered.

The distinction that still matters is task: this is Over 2.5 on 8,941 fixtures, not the 1X2
favourite question, and the 53.3% benchmark belongs to the other task.

## Limits

- Pilot only; the confirmatory slice is untouched and unscored.
- Closing prices without timestamps; no claim about executable value.
- Threshold 0.5 was pre-declared; a different threshold would trade accuracy for coverage.
