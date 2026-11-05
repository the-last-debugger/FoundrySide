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

## 3. Synthetic check — the logit-space projection is not comparable

The review asked for a synthetic test of the common-scale statistic, and it fails. `research/dispersion_check.py`
simulates complete three-way book vectors under the stated model, forms the maximum exactly as the
source does (highest decimal odds per outcome), de-vigs that synthetic vector, and compares.

| Quantity | Value |
| --- | --- |
| mean `logit(p_max) − logit(p_avg)` | **−0.00614** |
| mean `logit(p_avg) − logit(p_max)` | +0.00614 |
| projection `d · E[max_K]` | 0.16771 |
| ratio observed / projection | **0.037** |

Two conclusions, both of which change the protocol.

**The sign was wrong**, as the review suspected: the better *price* is the lower de-vigged
*probability*, so `logit(p_max) − logit(p_avg)` is negative by construction while the projection is
positive. The comparable quantity is `logit(p_avg) − logit(p_max)`.

**More seriously, the magnitudes are not comparable.** De-vigging the synthetic maximum odds vector
renormalises across the three outcomes, and that renormalisation removes almost all of the movement:
the de-vigged gap is 3.7% of the book-level logit range, and 27 times smaller than the projection.
So the synthetic de-vigged maximum is *not* the per-outcome extreme logit, exactly as the review
argued, and a logit-space projection cannot be subtracted from it.

## 4. Narrowed estimand — the projection moves to price space

The question the study exists to answer is about the **price gap**, which is measurable directly:
`mean log(MaxC / AvgC)` — the quantity behind the 6.51%. Both the observed statistic and the
projection are therefore computed in price space, where the comparison is like-for-like.

Procedure:

1. Estimate the pairwise de-vigged dispersion `d` per outcome from the two individually recorded
   books — the one quantity these fields identify.
2. Simulate K books under the equicorrelation model, **calibrating σ so that the simulated `d`
   matches the observed `d`**. The margin is set to the corpus-observed overround.
3. From the same simulation, compute the price gap `mean log(max odds / mean odds)` — the model's
   prediction for the statistic the corpus reports.
4. Compare the **simulated price gap** with the **observed price gap**, with a cluster bootstrap on
   the observed side.
5. **Excess = observed price gap − simulated price gap.**

This is a model-based projection, not a decomposition, and it is stated as such. Its virtue is that
both sides are the same statistic in the same units.

## 3b. What the calibration buys

Fitting σ to the observed dispersion means the simulation matches one moment of the data by
construction. The comparison then asks whether that calibrated model also reproduces the *price* gap.
If it does, the 6.5% is consistent with arithmetic plus ordinary dispersion. If the observed price
gap substantially exceeds the simulated one, something else is present — and that something is what
the product claim would rest on.

## 5. Per-outcome estimation and compositional dependence

`d` is estimated **separately for Home, Draw and Away**, because de-vigging redistributes margin
differently across outcomes and the three have very different variances. Pooling happens at the
fixture level, after per-outcome estimation.

The three outcomes of one fixture are compositionally dependent — they sum to one — so they are not
independent observations. **The fixture is the sampling unit throughout**: the bootstrap resamples
division-season clusters, and no test treats the three outcomes as independent.

## 6. Procedure

1. Per fixture, per book (Pinnacle, Bet365): de-vig the three-way closing prices proportionally, take
   logits, and compute the pairwise difference for each outcome.
2. `d_outcome = SD(fixture-level pairwise difference)/√2`, per division and pooled.
3. Per fixture: `E[max_K]` from observed `Bb1X2`; projected gap `d · E[max_K]` averaged across outcomes.
4. Observed `gap_z` as in §3.
5. **Excess = observed − projected**, with a cluster bootstrap interval over division-seasons.

## 7. Sensitivity and the one internal check

- `d` scaled by 0.5 and 2.0, reporting how the excess moves.
- **Regression of observed `gap_z` on `E[max_K]`.** What it tests: whether the gap grows with the
  number of books at the rate the projection implies. What it **cannot** test: normality, the
  equicorrelation assumption, or that `Max`/`Avg` are computed over the same books. A slope near `d`
  is consistent with the model; it is not a validation of it.
- Separate reporting for fixtures where `K` is small enough that the order-statistic approximation is
  weakest.

## 8. Decision rules, fixed now

| Observed vs simulated price gap | Reading | Consequence |
| --- | --- | --- |
| Interval overlaps the simulated gap | consistent with arithmetic under calibrated dispersion | price-shopping claim **weakened**: present as arithmetic, not advantage |
| Observed entirely above simulated | observed price gap exceeds what dispersion explains | claim **strengthened**, subject to availability |
| Observed entirely below simulated | observed gap smaller than the model predicts | **integrity check first** — verify `Max` and `Avg` book sets before interpreting |

## 9. Stop condition

One analysis, one report. No follow-up variant without new authorisation.

## 10. What this cannot support

No expected-value, profitability or user-advantage claim. Nothing about obtainable prices. No
statement that dispersion reflects "true" probability disagreement: it reflects differences in
de-vigged probabilities under proportional de-vig, with margin allocation not fully separated.

And no claim of decomposition. The study compares an observed price gap against a calibrated
simulation of it; it does not partition the 6.5% into "mechanical" and "genuine" shares, because these
fields do not identify that partition.
