# Pre-registration — is the 6.5% price improvement arithmetic or dispersion?

Committed before scoring. Revised after review; the revisions are in §2 and §3 and the earlier
derivation errors are recorded rather than hidden.

## 1. Question

Taking the best closing price for a selection is 6.51% better than taking the market average. For any
set of quotes the maximum exceeds the mean by construction. How much of that gap is consistent with
that arithmetic, and how much requires dispersion in de-vigged probabilities beyond it?

## 2. Derivation — corrected

**My first version was wrong twice.** It treated the pairwise estimator as the marginal dispersion σ,
and it claimed that positive correlation between books biased the excess *downward*. Both are
incorrect.

Let each book's de-vigged logit for one outcome be `σ Z_i`, where the `Z_i` are equicorrelated with
correlation ρ. Write `Z_i = √ρ U + √(1−ρ) ε_i` with `U, ε_i` independent standard normals. Then:

- `Var(Z_i − Z_j) = 2(1 − ρ)`, so `SD(Z_i − Z_j)/√2 = σ√(1−ρ)`.
- `max_i Z_i − mean_i Z_i = σ√(1−ρ) · (max_i ε_i − mean_i ε_i)`, whose expectation is
  `σ√(1−ρ) · E[max_K]`.

Both quantities carry the **same** factor `σ√(1−ρ)`. So the pairwise estimator `d ≡ SD(Δ)/√2` is
exactly the right scale for the K-book gap under equicorrelation — it is neither σ, nor a quantity
needing a correction. Verified numerically: with σ = 1, ρ = 0.6, K = 8, the simulated pairwise
estimator is 0.6316 against `σ√(1−ρ) = 0.6325`, and the simulated mean `max − mean` is 0.900 against
`σ√(1−ρ)E[max_8] = 0.9004`.

**Consequence:** there is no directional bias to claim. The projection is unbiased *if* the
equicorrelation model holds; if correlation structure is not equicorrelated, the direction is
unknown, and the protocol says so instead of asserting conservatism.

## 3. A common scale

The earlier version subtracted a ratio of **decimal prices** from a projection in **logit
probability** units. Those are different scales and the subtraction was invalid.

Both sides are now in logit-probability units:

- **Observed**: de-vig `MaxC` and `AvgC` separately (both are complete three-way sets), take logits,
  and compute `gap_z = logit(p_max) − logit(p_avg)` per outcome; average across the three outcomes
  within a fixture; then average over fixtures.
- **Projected**: `d · E[max_K]`, with `d` from §2 and `K` from the provider's `Bb1X2` field.

Approximations this introduces, stated because they are not removable with these fields:

1. `AvgC` is an average of **prices**, so `logit(de-vig(AvgC))` is not the mean of the books' logits.
   The gap is between the de-vigged best and the de-vigged average quote, not between the best and the
   mean logit.
2. `MaxC` may take different books for different outcomes, so `de-vig(MaxC)` is a synthetic
   three-way quote, not one book's price.
3. The two individually recorded books are assumed to be drawn from the same pool as the K books.

## 4. Per-outcome estimation and compositional dependence

`d` is estimated **separately for Home, Draw and Away**, because de-vigging redistributes margin
differently across outcomes and the three have very different variances. Pooling happens at the
fixture level, after per-outcome estimation.

The three outcomes of one fixture are compositionally dependent — they sum to one — so they are not
independent observations. **The fixture is the sampling unit throughout**: the bootstrap resamples
division-season clusters, and no test treats the three outcomes as independent.

## 5. Procedure

1. Per fixture, per book (Pinnacle, Bet365): de-vig the three-way closing prices proportionally, take
   logits, and compute the pairwise difference for each outcome.
2. `d_outcome = SD(fixture-level pairwise difference)/√2`, per division and pooled.
3. Per fixture: `E[max_K]` from observed `Bb1X2`; projected gap `d · E[max_K]` averaged across outcomes.
4. Observed `gap_z` as in §3.
5. **Excess = observed − projected**, with a cluster bootstrap interval over division-seasons.

## 6. Sensitivity and the one internal check

- `d` scaled by 0.5 and 2.0, reporting how the excess moves.
- **Regression of observed `gap_z` on `E[max_K]`.** What it tests: whether the gap grows with the
  number of books at the rate the projection implies. What it **cannot** test: normality, the
  equicorrelation assumption, or that `Max`/`Avg` are computed over the same books. A slope near `d`
  is consistent with the model; it is not a validation of it.
- Separate reporting for fixtures where `K` is small enough that the order-statistic approximation is
  weakest.

## 7. Decision rules, fixed now

| Excess (cluster interval) | Reading | Consequence |
| --- | --- | --- |
| Contains zero | consistent with arithmetic | price-shopping claim **weakened**: present as arithmetic, not advantage |
| Entirely above zero | dispersion exceeds the projection | claim **strengthened**, subject to availability |
| Entirely below zero | observed below projection | **integrity check first** — verify `Max` and `Avg` book sets before interpreting |

## 8. Stop condition

One analysis, one report. No follow-up variant without new authorisation.

## 9. What this cannot support

No expected-value, profitability or user-advantage claim. Nothing about obtainable prices. And no
statement that dispersion reflects "true" probability disagreement: it reflects differences in
de-vigged probabilities under proportional de-vig, with margin allocation not fully separated.
