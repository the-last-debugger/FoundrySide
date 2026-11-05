# Pre-registration — is the observed price-space dispersion statistic consistent with a calibrated model?

**Status: stopped before scoring** — a required input is absent from the held data. See
docs/DISPERSION_BLOCKER.md. No result exists and none was fabricated.

Written before scoring. This revision replaces the earlier draft entirely: the previous document
contained two competing estimands, and the audit was right that a pre-registration with residual
logit-space sections is not a pre-registration. The withdrawal of the original projection is kept in
§2 because it is part of the record.

## 1. Question

Taking the best closing price for a selection beats taking the market average by 6.51% in the held
snapshots. A maximum exceeds a mean **arithmetically, by construction** — that part is not in doubt
and needs no study.

The question is narrower: **is a specified, one-moment-calibrated model of ordinary book-to-book
dispersion consistent with that observed statistic, or does the observed statistic sit outside what
the model and its sensitivity grid can produce?**

That is a consistency question about a model, not a decomposition of the 6.51%, and not a decision
about what a product may claim. If the observed statistic is unsurprising under the model, that means
**this one summary statistic is not inconsistent with this calibrated model and grid** — not that the
model is generally adequate, and not that it would reproduce other statistics. If it is surprising,
the model as specified is contradicted by this statistic. Neither establishes a "genuine" component,
because a residual under an assumed dispersion model is not identified as anything in particular.

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
| Market strength | **Complete observed three-way de-vigged probability vectors are resampled** from the held corpus (one per simulated fixture), so both the favourite level and the draw/away split come from data rather than reconstruction | resampled from data |
| Book deviation | See §4a — indices and sharing specified exactly | assumption |
| Dispersion scale | Chosen so simulated pairwise de-vigged dispersion `d` equals the observed `d` from Pinnacle and Bet365 | **calibrated** |
| Correlation ρ | Not identified from two books; sensitivity parameter at 0, 0.3, 0.6, 0.9 | assumption |
| Margin | Proportional markup set to the corpus-observed closing overround | measured |
| Books per fixture K | **Unknown; evaluated over a pre-specified grid** (Amendment A1) | **assumption, not measured** |
| Missingness | Quotes absent at the observed per-outcome availability rate; `Max`/`Avg` computed over survivors | measured, approximate |
| Max/Avg formation | `max` and `mean` of simulated **decimal odds** per outcome, exactly as the source does | mechanical |

### 4a. Covariance construction, exactly

Indices: fixture `f`, book `b`, outcome `o`.

1. **Market.** For fixture `f`, resample a **complete three-way de-vigged probability vector**
   `(p_{f,H}, p_{f,D}, p_{f,A})` from the held corpus. Resampling whole vectors preserves the
   favourite level, the draw/away split and their joint distribution; a scalar favourite-probability
   distribution would not define the other two outcomes. Set `z_{f,o} = logit(p_{f,o})`.
2. **Common draw.** For each fixture and outcome, draw `U_{f,o} ~ N(0,1)` — **shared across all books
   for that outcome**, not across outcomes.
3. **Independent draw.** For each fixture, book and outcome, draw `ε_{f,b,o} ~ N(0,1)`, independent
   everywhere.
4. **Deviation.** `δ_{f,b,o} = σ · (√ρ · U_{f,o} + √(1−ρ) · ε_{f,b,o})`. So books are correlated
   **within an outcome** (positive ρ) and conditionally independent across outcomes given the market.
5. **Probability and margin.** Let `q_{f,b,o} = softmax_o(z_{f,o} + δ_{f,b,o})`, so `Σ_o q = 1`.
   Apply the book's margin `m_b ≥ 0` as a proportional markup:

   `π_{f,b,o} = q_{f,b,o} · (1 + m_b)`, so that `Σ_o π = 1 + m_b`.

   **No renormalisation follows.** The quoted implied probabilities sum to `1 + m_b` by construction;
   renormalising them back to 1 would silently delete the margin the model is meant to apply.
6. **Odds.** `odds_{f,b,o} = 1 / π_{f,b,o}`. The book's three-way overround is then
   `Σ_o (1/odds) = 1 + m_b`, exactly as intended.

   `m_b` is **measured** as the mean closing overround of the same book in the held corpus for the
   same seasons, where the two individually recorded books are available. For books whose overround is
   not individually observed, `m_b` is drawn from the observed distribution of overrounds. Applying a
   *proportional* markup is a **simulation assumption**, not a measured reproduction of the
   provider's construction; the sensitivity grid varies it by allowing the margin to be allocated
   more heavily to longshots, which is the alternative documented in the corpus.
7. **Missingness.** Drop book-outcome quotes at the observed availability rate, **before** forming
   the maximum and average, because the provider's `Max`/`Avg` are computed over the books it
   retained.
8. **Max and Avg.** `Max_{f,o} = max_b odds_{f,b,o}` and `Avg_{f,o} = mean_b odds_{f,b,o}` over
   surviving books — a maximum and a **mean of odds**, not of probabilities, matching the source.

**Cross-outcome dependence after de-vigging** arises in two places and the protocol states both: the
softmax normalisation couples the three outcomes compositionally, and any correlation in `U` across
outcomes would add to it — this version uses independent `U` across outcomes, so the only cross-outcome
dependence is compositional. That is a stated modelling choice, and step 4 of the sensitivity grid
varies it by allowing `U` to be shared across outcomes with correlation 0.5.

**Identified from the two-book data:** `d` only, plus the shape of the pairwise difference
distribution. **Assumed:** ρ, equicorrelation, proportional margin, logit-normal deviations.
**Sensitivity parameters:** ρ, dispersion scale (±50%), K distribution, missingness rate.

This is a one-moment-calibrated model. It is not validation of the model.

### 4b. Amendment A1 — `K` is unknown, and treated as such

**Why.** `Bb1X2`, the provider field that would give the number of books behind `Max` and `Avg`, is
absent from all 40 held files. The original protocol assumed it was available; it is not
(`docs/DISPERSION_BLOCKER.md`).

**What the held fields can and cannot constrain.**

- **Can**: that at least two books were aggregated, because `Max` and `Avg` exist and two individual
  books are also recorded. That is the only hard constraint, and it is nearly vacuous.
- **Can**: the empirical distribution of `Max/Avg − 1` for each fixture — but using it to *infer* `K`
  is rejected, because that ratio is the quantity the study is testing.
- **Cannot**: the actual number of books, or how it varied by fixture, division or season.

**The grid.** `K ∈ {4, 6, 8, 10, 12}`, each evaluated separately, with `S_sim(K)` reported for every
value so the band is visible rather than collapsed to a point.

*Justification for the range.* The provider aggregates commercial bookmaker prices for European
league football; aggregator coverage in that setting is typically several books, not two and not
twenty. `K = 4` is a conservative lower end — more than the two individually recorded books, fewer
than a broad aggregator plausibly carries. `K = 12` is a generous upper end. Values outside this range
would imply either a two-book aggregate, which the separate presence of `Max` and `Avg` argues
against, or a very wide aggregator, which the coverage of lower divisions makes unlikely. **This is a
judgement about plausible provider coverage, not a measurement, and it is labelled as such.**

**A limiting case is reported as context.** `max − mean` grows like `σ√(2 ln K)`, so the band
flattens: the difference between `K = 12` and `K = 30` is small relative to the difference between
`K = 4` and `K = 12`. `S_sim` at `K = 20` is reported alongside the grid to show how much the answer
could move if the assumption is wrong in the direction that matters.

**What this costs the study, stated plainly.** A wider band makes "inside the range" easier to
satisfy, so the test of model adequacy becomes **weaker**: it has less power to reject. The
informative outcome is not `S_obs` sitting inside a broad band — it is `S_obs` lying **above the band
at the largest plausible `K`**, since `S_sim` increases with `K` and that is the hardest case for the
model to fail. The report must say this where the band is presented, and the decision rules below are
read with that asymmetry in mind.

**Everything else is unchanged**: the observed statistic, inclusion rules, calibration approach,
sensitivity grid over ρ and dispersion, uncertainty reporting and descriptive-only interpretation.

## 5. Procedure

1. Estimate `d` per outcome from Pinnacle and Bet365 de-vigged logits, divided by √2, separately for
   home, draw and away.
2. Estimate the margin from the same selections' closing overround.
3. Simulate fixtures **for each `K` in the grid of Amendment A1**: for each book draw equicorrelated
   logit deviations; form probabilities; apply the margin; form decimal odds; drop quotes at the
   observed availability rate; compute `Max` and `Avg` per outcome; compute `r = max/mean − 1`.
4. Calibrate the dispersion scale so simulated `d` matches observed `d`, per outcome — separately
   for each `K`, so the band reflects `K` alone and not a change in calibration.
5. **S_sim(K) = arithmetic mean of `r` over simulated selection-snapshots**, for each `K`.
6. **Excess(K) = S_obs − S_sim(K)**, reported for every `K` in the grid, with the band
   `[min_K S_sim, max_K S_sim]` alongside.

## 6. Uncertainty — intervals on both sides

- **Observed side — exact scheme.** A **pairs (cluster) bootstrap**: the sampling unit is the
  division-season. There are 24 (8 divisions × 3 seasons). Each replicate draws 24 clusters **with
  replacement** from those 24, concatenates their selections, recomputes `S_obs` on the concatenation,
  and the 2.5th and 97.5th percentiles of 2,000 replicates form the interval. Clusters are resampled
  whole, so within-cluster dependence (shared competition, shared season, and all three outcomes of a
  fixture) is carried through.
- **The 24-cluster limitation is real and stated.** A percentile cluster bootstrap with 24 clusters
  can understate variance, and the tails are poorly estimated. Two checks are run on the same data:
  a **leave-one-division-out jackknife** (eight refits, reporting the range of `S_obs` without each
  division) and **per-division intervals** reported separately. If those suggest material
  between-division heterogeneity, the pooled interval is described as approximate rather than
  definitive — and if it cannot be resolved with held data, the protocol says so rather than
  presenting the interval as exact.
- **Simulation side**: repeated simulation gives a 2.5th–97.5th percentile interval reflecting K,
  dispersion draws and fixture randomness, **not** parameter uncertainty, because the dispersion
  scale is calibrated.
- **Parameter uncertainty** is handled by the sensitivity grid (ρ; ±50% dispersion), reported as a
  range of `S_sim` rather than folded into one interval.

**The comparison is interval-to-interval.** No sampling distribution is claimed for the difference,
because `S_sim` is a model prediction, not a sample.

## 7. Decision rules, fixed now

All three outcomes are **descriptive statements about model adequacy**. None is permission to make a
product claim, and none establishes user benefit.

| Comparison | What it means | What it does **not** mean |
| --- | --- | --- |
| `S_obs` inside the band over the `K` grid and ρ sensitivity | the observed statistic is unsurprising under this calibrated model, for some plausible `K` | not that the difference *is* arithmetic, and not that no dispersion exists; a wide band makes this weak evidence |
| `S_obs` above the band at **every** `K` in the grid | the model, as specified, does not reproduce the observed statistic even at the largest plausible `K` | not proof of "genuine dispersion", because a finite grid over assumed structures cannot exhaust alternatives; it means this model is inadequate |
| `S_obs` below every `S_sim` | the same, in the other direction — a model-adequacy failure | an **integrity check first**: verify `Max`/`Avg` book sets and `Bb1X2` semantics before interpreting |

The 0.01-nat scale is **not** used: the quantity is a relative price difference, not a log loss.

Compatibility is not explanation. The grid is assumption-dependent and the model is calibrated on one
moment, so "inside the range" means only that this model is not contradicted.

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
