# Pre-registration — is the 6.5% best-price improvement arithmetic or dispersion?

Written before scoring. This revision replaces the earlier draft entirely: the previous document
contained two competing estimands, and the audit was right that a pre-registration with residual
logit-space sections is not a pre-registration. The withdrawal of the original projection is kept in
§2 because it is part of the record.

## 1. Question

Taking the best closing price for a selection beats taking the market average by 6.51% in the held
snapshots. Any maximum exceeds a mean **by construction**. The question is how much of that 6.51% a
model of ordinary book-to-book dispersion can reproduce, and how much would require dispersion beyond
it.

The answer decides what the product may say: either "the best price is arithmetic", or "there is
genuine dispersion the best price is capturing".

## 2. What was withdrawn, and why

The first draft proposed a logit-space order-statistic projection, `d · E[max_K]`, compared directly
against the observed gap. The audit identified two fatal problems, both confirmed by
`research/dispersion_check.py`:

- the sign was reversed, because a better price is a **lower** de-vigged probability;
- the magnitudes were not comparable: de-vigging the outcome-wise maximum-odds vector renormalises
  across outcomes, giving a gap 0.037× the projection.

So the logit-space decomposition is **withdrawn**, and the "mechanical versus genuine" partition is
not claimed. What remains is a comparison in **price space**, where the observed statistic lives.

The equicorrelation relationship is retained because it fixes how a pairwise estimator relates to a
multi-book spread: for equicorrelated logits with correlation ρ, `SD(Δ)/√2 = σ√(1−ρ)`, and the
multi-book spread carries the same factor.

## 3. The observed statistic, reconciled with the inventory

`PRICE_INVENTORY.md` reports 6.51%, and this protocol uses exactly that quantity rather than a
convenient approximation.

`research/price_inventory.py` computes, per eligible selection, `r = MaxC/AvgC − 1`, then takes the
**arithmetic mean** of `r`. Therefore:

**S_obs = mean over eligible selection-snapshots of (MaxC/AvgC − 1) = 0.0651**

It is an arithmetic mean of relative price differences — not a geometric mean, not a mean of logs, not
a portfolio return. Eligible: every closing 1X2 selection in the eight held divisions across the three
pilot seasons with both `MaxC` and `AvgC` usable — 44,406 selection-snapshots from 14,802 fixtures,
all three outcomes present throughout.

`MaxC` is the highest closing decimal price the provider tracked for that outcome; `AvgC` is its mean
across the books it tracks. Both are **quotes**, not verified obtainable prices.

## 4. The price-space data-generating model

The simulation must produce `S_sim` the same way the source produces `S_obs`.

| Component | Specification | Status |
| --- | --- | --- |
| Market strength | Three-way market drawn from the corpus-observed distribution of de-vigged favourite probabilities, so the simulation is not anchored to a single market | assumption, sensitivity-checked |
| Book deviation | Logit deviations, `√ρ·U + √(1−ρ)·ε`, ε independent per book and outcome | assumption |
| Dispersion scale | Chosen so simulated pairwise de-vigged dispersion `d` equals the observed `d` from Pinnacle and Bet365 | **calibrated** |
| Correlation ρ | Not identified from two books; sensitivity parameter at 0, 0.3, 0.6, 0.9 | assumption |
| Margin | Proportional markup set to the corpus-observed closing overround | measured |
| Books per fixture K | Drawn from the observed `Bb1X2` distribution | measured |
| Missingness | Quotes absent at the observed per-outcome availability rate; `Max`/`Avg` computed over survivors | measured, approximate |
| Max/Avg formation | `max` and `mean` of simulated **decimal odds** per outcome, exactly as the source does | mechanical |

**Identified from the two-book data:** `d` only, plus the shape of the pairwise difference
distribution. **Assumed:** ρ, equicorrelation, proportional margin, logit-normal deviations.
**Sensitivity parameters:** ρ, dispersion scale (±50%), K distribution, missingness rate.

This is a one-moment-calibrated model. It is not validation of the model.

## 5. Procedure

1. Estimate `d` per outcome from Pinnacle and Bet365 de-vigged logits, divided by √2, separately for
   home, draw and away.
2. Estimate the margin from the same selections' closing overround.
3. Simulate fixtures: draw K from the observed `Bb1X2` distribution; for each book draw
   equicorrelated logit deviations; form probabilities; apply the margin; form decimal odds; drop
   quotes at the observed availability rate; compute `Max` and `Avg` per outcome; compute
   `r = max/mean − 1`.
4. Calibrate the dispersion scale so simulated `d` matches observed `d`, per outcome.
5. **S_sim = arithmetic mean of `r` over simulated selection-snapshots.**
6. **Excess = S_obs − S_sim.**

## 6. Uncertainty — intervals on both sides

- **Observed side**: cluster bootstrap over division-seasons (24 clusters), resampling whole
  division-seasons and recomputing `S_obs`; 95% interval.
- **Simulation side**: repeated simulation gives a 2.5th–97.5th percentile interval reflecting K,
  dispersion draws and fixture randomness, **not** parameter uncertainty, because the dispersion
  scale is calibrated.
- **Parameter uncertainty** is handled by the sensitivity grid (ρ; ±50% dispersion), reported as a
  range of `S_sim` rather than folded into one interval.

**The comparison is interval-to-interval.** No sampling distribution is claimed for the difference,
because `S_sim` is a model prediction, not a sample.

## 7. Decision rules, fixed now

| Comparison | Reading | Consequence |
| --- | --- | --- |
| `S_obs` inside the sensitivity range of `S_sim` | consistent with arithmetic under calibrated dispersion | claim **weakened**: present as arithmetic, not advantage |
| `S_obs` above every `S_sim` in the grid | observed improvement exceeds what the model reproduces | claim **strengthened**, subject to availability |
| `S_obs` below every `S_sim` | observed smaller than the model predicts | **integrity check first**: verify `Max`/`Avg` book sets and `Bb1X2` semantics |

The 0.01-nat scale is **not** used: the quantity is a relative price difference, not a log loss.

## 8. What this cannot establish

- No expected-value, profitability or user-advantage claim; no price is verified as obtainable.
- No "mechanical versus genuine" partition. The study compares an observed statistic with a calibrated
  model; it does not decompose 6.51% into shares, because these fields do not identify them.
- No claim about books' true beliefs: de-vigged probabilities under proportional de-vig are an
  assumption, and margin allocation is not fully separated from dispersion.
- No claim that the model is correct. Reproducing one moment is calibration; agreement on a second is
  consistency, not proof.

## 9. Stop condition

One analysis, one report, one commit. No follow-up variant without new authorisation.

## 10. Cost and boundaries

Zero data cost; held data only. No provider contact, no new data, no P-02 access, no product work.
