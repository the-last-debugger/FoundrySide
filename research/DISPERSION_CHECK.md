<!-- generated-by: dispersion_check.py sha256=54473e4e703b -->

# Dispersion protocol — synthetic validation of the common-scale statistic

Synthetic only: 20,000 replicates, 8 books, three outcomes, σ = 0.15, ρ = 0.6, proportional
margin 3%. No fixture data is read.

## 1. Which sign is correct?

| Statistic | Value |
| --- | --- |
| mean `logit(p_max) − logit(p_avg)` | **-0.00614** |
| mean `logit(p_avg) − logit(p_max)` | +0.00614 |

Higher odds mean lower probability, so the best **price** is the lowest de-vigged **probability**.
The protocol's `logit(p_max) − logit(p_avg)` is therefore negative by construction, while the
projection `d·E[max_K]` is positive. **The sign in the protocol was wrong**; the comparable quantity
is `logit(p_avg) − logit(p_max)`.

## 2. Does the projection match the synthetic statistic?

| Quantity | Value |
| --- | --- |
| pairwise de-vigged dispersion `d` | 0.11748 |
| `E[max_K]` for K = 8 | 1.42760 |
| **projection** `d · E[max_K]` | **0.16771** |
| **synthetic statistic** (correct sign) | **0.00614** |
| ratio statistic / projection | 0.037 |

## 3. Is the de-vigged maximum a per-outcome order statistic?

| Quantity | Value |
| --- | --- |
| mean per-outcome logit range among books, `max − mean` | 0.16765 |
| mean of `logit(p_max) − logit(p_avg)` (signed) | -0.00614 |
| ratio | 0.037 |

If the synthetic de-vigged vector equalled the outcome-wise extreme of book-level logits, this ratio
would be near 1. It is 0.037, so **de-vigging the synthetic
maximum odds vector is not the same as taking the per-outcome extreme logit**, exactly as the review
suspected.

## Reading

The projection and the statistic do **not** agree in magnitude: the ratio is
{gap_flipped.mean() / projected:.3f}. The fields therefore do not identify a projected gap that is
comparable to the observed statistic, and the study must be narrowed to descriptive quantities rather
than subtracting a model quantity from a measured one.

## Limits

- One parameterisation (σ, ρ, margin, K) and one true market. A different σ or correlation structure
  could change the ratio.
- The simulation assumes books quote with a proportional margin and equicorrelated logit noise —
  the same assumptions the projection needs, so it validates internal consistency, not the model.
- Not a substitute for held-data validation; it is the arithmetic check the review asked for.
