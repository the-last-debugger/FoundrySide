<!-- generated-by: bogey_team.py sha256=5035978f39ad -->

# Bogey-team study — does head-to-head history predict beyond the price?

Pilot seasons only, 8,941 fixtures. 4,380 have at least two prior meetings
between the same pair; the rest fall back to the shrunk base rate, so the feature is effectively
absent for them and the estimate is driven by the fixtures where the belief could apply.

| Hypothesis | Gain (nats) | Division-season 95% | Pair 95% | Perm. p | BH q |
| --- | --- | --- | --- | --- | --- |
| B1 pair goals history | +0.00002 | [-0.00015, +0.00019] | [-0.00026, +0.00030] | 0.169 | 0.169 |
| B2 pair result history | +0.00010 | [-0.00017, +0.00037] | [-0.00022, +0.00043] | 0.070 | 0.139 |

Baseline log loss of the market price alone: **0.6744**.

## Reading

The belief deserves a fair hearing because it has a mechanism: repeated matchups could encode a
stylistic mismatch that team-level ratings average away. If that mechanism exists and the price
does not carry it, the feature should show a positive gain.

A null here is informative in a way the calendar null was not, because the feature has a plausible
causal story. It would mean either the mechanism is absent, or the market already prices it —
and this design cannot distinguish those two. What it can say is whether a user with that belief
would have profited from acting on it beyond the price, and that is the question that matters.

## Method notes

- Histories are availability-gated: a meeting enters the pair record only when kickoff + 3h is at
  or before the target cutoff, enforced by a pending queue ordered by kickoff.
- Rates are shrunk toward 0.5 with a prior weight of 4, so a pair with one prior
  meeting does not dominate.
- Resampling is by division-season, not by pair: a pair-level effect that survives resampling whole
  competitions is the strong claim, and the weaker one would need pair-level clusters with very few
  observations each.

## Limits

- Three seasons give most pairs two to six meetings. That is enough to estimate a persistent effect
  only if it is large, and the power here is correspondingly low.
- One market, one corpus, closing prices without timestamps; the T−90 caveat applies.
- "Bogey" in the folklore sense often means a single famous upset, which this design cannot detect
  and would not want to.
