# Pre-registration — hit-rate and metric audit

**Written and committed before the calculations.** The question: does the model make more or fewer
correct hard predictions than the market, on the same target and the same fixtures?

## What is being compared, stated before any number

- **Target**: Over 2.5 goals. `y = 1` when the match had three or more goals.
- **Model**: `p_model` from `pilot_model.py`, prequential, T−90 proxy.
- **Market**: the de-vigged Pinnacle closing over 2.5 price, `p_market`, computed as
  `(1/over) / (1/over + 1/under)`.
- **Rows**: pilot seasons only, 8,941 fixtures, identical for every metric. No row is included in
  one comparison and excluded from another.
- **The 53.3% 1X2 favourite baseline is a different task** — home/draw/away on 14,802 fixtures — and
  is reported separately as a market benchmark, never as a head-to-head.

## Hard picks

Threshold **0.5, declared now**: pick Over when the probability is at least 0.5, Under otherwise.
Three pickers: raw model, forward-calibrated model, market. Calibration is fitted on seasons
strictly before the target season, so the calibrated column contains no hindsight.

Reported for each: accuracy, number correct and incorrect, the 2×2 confusion matrix, precision and
recall for Over and for Under, and balanced accuracy (the mean of the two recalls, which does not
reward always answering the majority class).

## The comparison that answers the question

**Paired discordance**, not two independent accuracies: the count of fixtures where the model is
right and the market wrong, against the count where the market is right and the model wrong. A
difference in accuracy is entirely determined by those two counts, and reporting them makes the
direction and size of the disagreement visible.

Uncertainty is cluster-aware: a bootstrap resampling **division-seasons**, 2,000 draws, giving an
interval on the accuracy difference. A McNemar-style binomial test on the discordant pairs is
reported alongside, with the caveat that it treats fixtures as independent and the bootstrap is the
one to trust.

## Probability metrics on the identical rows

Log loss, Brier, ROC AUC, reliability and resolution from a ten-bin decomposition, and the
calibration slope and intercept from a logistic fit. Reported for the market, the raw model and the
forward-calibrated model, with sample counts.

Each is labelled with the question it answers:

- **Log loss / Brier** — how good the probabilities are, penalising confident errors.
- **AUC** — ranking only; unchanged by any monotone recalibration.
- **Reliability / resolution** — whether probabilities are right on average, and whether they
  separate outcomes.
- **Accuracy** — how often the hard pick is right; blind to confidence.

## Does a higher hit rate imply better decisions?

No, and the report will show why with two measurements: realised accuracy by market-probability
band, and the relationship between the implied probability and the realised rate. A picker can be
more accurate and still lose money, because accuracy ignores price. Expected value at the closing
price is reported where it is computable, with the timestamp caveat.

## Stop criterion

The audit is descriptive: it concludes with which sense of "worse" is supported and which is not.
If the hard-pick accuracy difference is indistinguishable from zero while the log-loss difference
is not, the correct statement is that the model is worse calibrated rather than worse at picking,
and the report must say that rather than "the model is poor".

## Limits stated in advance

- No 1X2 model predictions exist in the repository; if that is still true at audit time, item 3 is
  answered as "not compared", not manufactured from the O/U model.
- Closing prices carry no observation timestamp.
- Pilot only; the confirmatory slice is untouched.
