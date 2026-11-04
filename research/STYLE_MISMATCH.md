<!-- generated-by: style_mismatch.py sha256=e85743d76008 -->

# Style-mismatch study — do team shapes interact beyond additive ratings?

Pilot seasons only, 8,941 fixtures. Each feature enters a market-conditioned logistic, so
a gain means information the closing price did not contain.

| Hypothesis | Feature SD | Gain (nats) | Cluster 95% | Perm. p | BH q |
| --- | --- | --- | --- | --- | --- |
| S1 attack/defence interaction | 0.128 | -0.00017 | [-0.00053, +0.00013] | 0.741 | 0.741 |
| S2 home/away asymmetry | 0.647 | -0.00007 | [-0.00024, +0.00007] | 0.552 | 0.741 |
| S3 scoring volatility | 0.384 | +0.00016 | [-0.00015, +0.00049] | 0.070 | 0.209 |

Baseline log loss of the market price alone: **0.6744**.

## Reading

S1 is the interesting one: it is the formal version of "a good attack against a bad defence
produces more than the ratings suggest", and unlike the calendar beliefs it has a mechanism.
S2 and S3 are controls for the same idea expressed as venue asymmetry and consistency.

A gain of zero with a tight interval means the market already prices the interaction or the
interaction is not there. A gain that is positive but an order of magnitude below the 0.0246
deficit is a curiosity, not a route.

## Method

- Features use only completed matches, gated by the pending-result queue at each cutoff.
- Attack and defence excess are shrunk toward the league mean with a prior weight of 5
  over a 10-match window, so a promoted side with two matches does not dominate.
- Permutation is stratified by division-season, preserving cluster geometry.

## Limits

- Ten matches is a short window for a style estimate; longer windows would dilute a change of
  manager or squad.
- One corpus, one market, closing prices without timestamps; the T−90 caveat applies.
- Style is inferred from goals alone, which cannot separate a high press from a direct long-ball
  side; this tests the *interaction* that goals can express, not the tactical taxonomy.
