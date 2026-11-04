# Pre-registration — disagreement-aware shrinkage

**Written and committed before the experiment runs.** Item 1 of the sponsor's research queue.

## Why

E18 found that the model's deficit is not uniform: where it nearly agrees with the market it loses
0.0039 nats, and where it departs by 0.6 or more on the logit scale it loses 0.0574. If that is a
real property rather than a description of the pilot, a policy that **trusts the model less as it
departs further** should beat both the model and the raw market on log loss. If it does not, the
disagreement pattern is descriptive only and the market-only fallback is justified.

## Hypotheses

- **H1**: a shrinkage policy fitted on prior seasons improves log loss over the forward-calibrated
  model on the next season.
- **H2**: it does not beat the market-only policy. If H1 fails and H2 holds, the honest product is
  the market price, which is the strongest negative this line can produce.

## Policies, all fixed before the run

| Policy | Definition |
| --- | --- |
| `market` | the de-vigged closing price alone |
| `model` | forward-calibrated model alone (the current best) |
| `fixed 0.5` | midpoint of the two on the logit scale, no fitting |
| `shrink-linear` | weight on the model = `max(0, 1 − d/d0)`, with `d` the absolute logit departure and `d0` fitted on prior seasons |
| `shrink-threshold` | if `d > t` use the market, else the model; `t` fitted on prior seasons |
| `market-fallback` | `shrink-threshold` with `t` fixed at 0.6, the band boundary in E18 |

Fitting is by grid search over pre-declared grids (`d0` and `t` in 0.05 steps over [0, 1.5]),
minimising log loss **on the prior seasons only**. No parameter is fitted on the evaluation season.

## Evaluation

Forward folds only: seasons strictly before the target supply the fit, and each later pilot season
is scored once. The first pilot season cannot be evaluated forward and is excluded from all policies
equally.

Metrics per policy: log loss, reliability and resolution from the binned decomposition, coverage
(share of fixtures where the policy differs from the market by more than 0.01), and sample counts.
Uncertainty by cluster bootstrap over division-seasons, 2,000 draws.

## Decision rule, fixed now

A policy is **worth carrying forward** only if, on the shared evaluation seasons:

1. its log loss is lower than both `market` and `model`; and
2. the cluster interval on its improvement over `market` excludes zero.

Otherwise the result is recorded as a null and `market` is the recommended fallback. A policy that
only beats `model` but not `market` is reported as such: it would mean the best available correction
still does not reach the benchmark.

## Stop criterion

If no policy satisfies both conditions, this line stops. The subsequent work would then be robustness
of the finding (queue item 3) rather than further policy variants, because a family of six policies
with four fitted parameters failing together is evidence about the information, not about the
parameterisation.

## Leakage controls

- Parameters fitted on prior seasons only, never on the evaluation season.
- The market comparator is the same de-vigged closing price used everywhere else in the programme.
- No confirmatory fixture is read; the frozen slice is untouched.
- The policy definitions and grids are fixed in this file, so a later idea cannot be presented as
  part of the same test.

## Limits acknowledged in advance

- Two forward folds from one corpus: a rule that works on both is promising here, not validated.
- Closing prices with no timestamps: any policy improvement is about accuracy against a closing
  benchmark, not about what was executable.
- Thresholds fitted on two seasons may be unstable; the fitted values are reported so a reader can
  see whether they are interior optima or boundary hits.
