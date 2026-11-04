# Conclusion — Track A

**Track A is closed.** This records what was established, what was not, and the conditions under
which it may be reopened.

## What the programme tested

Over twenty-four experiments the programme asked one question in many forms: can a forecast built
from publicly available results and closing prices beat the closing price itself?

It cannot, in this corpus. The evidence is consistent across methods:

- **The model is worse, and worse in every sense.** Log loss 0.6988 against 0.6742; AUC 0.562
  against 0.607; hard-pick accuracy 54.30% against 57.66% with a cluster interval excluding zero.
- **Calibration was the one recoverable defect, and recovering it was not enough.** Forward-only
  Platt transfer recovers +0.0102 nats — deployable, and about half the deficit.
- **The residual is a resolution deficit, and it is not uniform.** The model loses 0.0574 nats where
  it departs from the price by ≥0.6 logit, and 0.0039 where it nearly agrees. That ordering
  reproduces in both forward seasons and all eight divisions.
- **No weighting recovers it.** Six pre-registered shrinkage policies; the best ties the market by
  collapsing to market-only, with fitted thresholds at the bottom of the grid.
- **Thin markets are not the answer.** Thirteen additional divisions, 13,569 scored fixtures, +0.0017
  nats against the existing eight — well inside the 0.01 scale.

## What this does not establish

- That all markets are efficient. Thirteen divisions were tested within one provider's coverage.
- That every narrower opportunity is ruled out. Match-level microstructure, live prices and
  information arriving before kickoff were not testable here.
- That a user gains nothing. Price shopping improves the price paid by ~6.5% per selection. What is
  not established is that it improves expected value or decisions.
- That the model approach is wrong in general. The finding is about this information set, not about
  modelling.

## What survives

Two facts worth carrying forward:

1. **Recalibration transfers forward** (+0.0102 nats on matched rows). Any future forecaster should
   expect to recalibrate and should test it out of time.
2. **Price comparison improves the price paid** (~6.5% per selection across 44,406 snapshots) —
   tradeable, bounded, and not the same as value.

## Reopening conditions

Closure is not permanent. Track A may be proposed for revival if genuinely new information appears:

- a lawful, affordable **timestamped** odds source — the one gap every experiment ran into;
- materially new market or fixture data, including competitions outside this provider;
- a new method or external finding that changes the evidence;
- a newly identified, testable inefficiency.

A revival proposal must state what is new, why it changes the prior conclusion, and the smallest
bounded test — and needs sponsor approval for that scope before work starts. Repeating the same
analysis, or reopening because the queue is empty, is not a reason.

## State at closure

P-02 confirmatory slice: untouched, unscored, unexamined. No paid resources, no provider contact,
no redistribution, no public claims. The research record is committed: 24 experiments, 33 stamped
reports, pre-registrations for every experiment that made a claim, and guards that verify the
artefacts reproduce.
