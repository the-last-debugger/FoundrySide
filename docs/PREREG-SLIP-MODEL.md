# Pre-registration — can a model predict slip success?

Written before fitting.

## Question

Given a slip built from a match-day's fixtures, can a fitted model predict whether it wins better than
multiplying the legs' de-vigged probabilities?

The baseline is not arbitrary: multiplying is what a user does, and 28 prior experiments found no
predictive edge over the market. If a model cannot beat the product, the honest product shows the
product.

## Design

- **Slips**: built greedily from a day's fixtures, most probable first, until the combined price reaches
  one of {1.5, 2, 3, 5, 10, 20}×. One slip per target per day.
- **Features**: `logit(∏ implied)` and `(n_legs − 1)`, plus an intercept. Three parameters.
- **Fit**: logistic regression by Newton steps on seasons up to 2022/23.
- **Score**: seasons 2023/24 onwards, untouched during fitting.
- **Metrics**: log loss and Brier against the baseline; calibration slope of the fitted logits.

## Decision rule, fixed in advance

The model replaces the baseline only if **both** hold out of time:

1. log loss improves by more than **0.001 nats**, and
2. the calibration slope lies in **[0.7, 1.3]**.

A loss improvement with a broken slope is not a usable probability, and this project treats a
mis-shaped model as a failure rather than a partial success.

## What this cannot establish

- That any slip is a good bet. Both artefacts are probabilities of *winning*, not of *profiting*.
- That the greedy construction is the best slip at a multiplier; it is one construction.
- That the recorded prices were obtainable.

## Stop condition

One fit, one report, one commit. No feature additions without a new pre-registration.
