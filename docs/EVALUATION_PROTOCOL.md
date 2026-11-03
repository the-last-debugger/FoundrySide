# Evaluation Protocol — preregistration for the first confirmatory experiment

**Status: proposal for sponsor agreement. Not frozen, nothing scored.** No engine is
scored against the benchmark until every field in §8 is filled and committed, because a
metric chosen after seeing results is not a metric.

---

## 1. Which market, and why

**Recommendation: over/under 2.5 goals**, measured on de-vigged Pinnacle closing prices.

| Reason | Evidence |
| --- | --- |
| Closing prices exist, from two independent books | Pinnacle closing on 14,737 of 14,802 fixtures (99.6%); Bet365 closing on 14,800 (100%) |
| It is a two-way market | De-vigging needs no model of the draw outcome, so one source of arbitrary choice disappears |
| It is not the market OLPRS consumed | The prior work built form/position/odds-tier features for 1X2 and BTTS; starting elsewhere reduces the chance of re-running the same idea |
| The outcome has a specifiable structure | Goals per side admit a count model, so a failure is interpretable as "the model of goals is wrong", not "the features were unhelpful" |

**Why not 1X2 first.** Three-way de-vig introduces a choice that has to be argued
about; and 1X2 is where the project's only existing number (53.3% favourite accuracy)
lives, which makes it inviting to frame the question as "beat the pick" rather than
"beat the probability". The pick is descriptive; the probability is the thing that can
be scored properly.

## 2. The benchmark

De-vigged Pinnacle closing probability, proportional (multiplicative) normalisation:

```
p_over = (1 / o_over) / (1 / o_over + 1 / o_under)
```

Measured on 14,735 fixtures:

| Property | Value |
| --- | --- |
| Mean de-vigged P(over 2.5) | 51.5% |
| Observed over-2.5 rate | 51.7% |
| Mean two-way overround | 3.1% |
| **Benchmark log loss** | **0.6706 nats** |
| Benchmark Brier | 0.2390 |

Proportional de-vig is one of several defensible methods. It is declared here rather
than buried, and the sensitivity check is to repeat the headline comparison against the
Bet365 pair — if the conclusion changes with the book, the conclusion was about the book.

## 3. Forecast timestamp and point-in-time rule

- The benchmark is the closing price **as recorded**, i.e. the last pre-kickoff
  observation in the file.
- The model must produce its probability from information available **strictly before**
  that timestamp.
- Any feature whose value could have changed after that timestamp is excluded unless its
  as-of value is stored with the prediction. This is the lesson from
  `OLPRS_v2/docs/PIT_INTEGRITY_2026-10-31.md`, where the join was correct and the
  provenance was still lost.
- Training data for a fixture is drawn only from matches strictly before its date. No
  season-ending aggregates, no league tables that include the fixture itself.
- A run in which the rule cannot be verified is reported as invalid, not as a result.

## 4. Coverage and exclusions

Include a fixture when both closing prices and a result exist. Exclusions are counted
and reported. **No exclusions may be added after outcomes are seen**; anything that looks
like an outlier is kept, because dropping it is how a backtest becomes a story.

## 5. Scoring

| Metric | Role |
| --- | --- |
| Log loss (nats) | **Primary.** Proper scoring rule for probability forecasts |
| Brier score | Secondary, robustness |
| Calibration: reliability curve with bin counts, slope and intercept of observed on predicted | Required alongside the score, never instead of it |
| Accuracy of the favourite-pick | Descriptive only — it compares picks, not probabilities |

The comparison is **paired**: per-fixture Δ log loss (model − market), summarised as a
mean with a bootstrap interval resampled over fixtures, and a cluster bootstrap over
(division, season) as a robustness check. Clustering was measured to have a negligible
effect on the accuracy contrast (`research/POWER.md`); for log loss it is checked rather
than assumed.

The ±3pp calibration tolerance is a **guardrail, not a test**: it flags a model whose
probabilities are systematically off, and it is reported with the reliability plot and
bin counts so a thin-bin artefact is visible.

## 6. Effect size, and why 0.01 nats

**Target: 0.01 nats per fixture**, i.e. 0.6706 → 0.6606, a 1.5% relative improvement.

That is not a modest ask. The market's margin is 3.1%, so a 1.5% relative gain in log
loss is the same order as the book's own edge — which is exactly why it is the right
scale for a first serious test rather than a comfortable one. An improvement of 0.001
nats would be indistinguishable from noise at any sample this project can afford.

**Sample size.** The power that matters is for the paired log-loss difference, which
depends on the spread of Δ, not on the baseline's standard error. That spread is unknown
until measured, so it is measured first:

1. **Pilot** on seasons 2021–2223 (disjoint from the confirmatory slice): fit the engine,
   produce the per-fixture Δ distribution, and estimate the observed discordance.
2. **Power by simulation** on that distribution, for the target 0.01 nats, at 80% power
   and two-sided alpha 0.05.
3. **Freeze n**, then run on 2324–2425.

The pilot slice may not contribute to the confirmatory claim — that is the whole reason
it is a separate slice.

The accuracy-based power table in `research/POWER.md` remains the guide for how much data
a given *pick-level* edge needs (roughly 10k–30k fixtures for a 1–2pp edge). It is no
longer the primary sizing argument, because accuracy is no longer the primary metric.

## 7. Multiple testing

The family is the set of engine ids declared at freeze time. Benjamini-Hochberg at FDR
0.05 across that family. Any split reported afterwards — by league, by season, by
threshold — is exploratory and labelled so. A subgroup result that is not in the frozen
family is not evidence of an edge.

## 8. The freeze record

Committed as `research/PREREG-<id>.md` before any scoring, containing:

| Field | Value |
| --- | --- |
| Market and outcome definition | over/under 2.5 goals, `FTHG + FTAG >= 3` |
| Benchmark and de-vig method | Pinnacle closing, proportional normalisation |
| Forecast timestamp | last recorded pre-kickoff price |
| Engine id and version | _to be filled_ |
| Feature list, with as-of rule per feature | _to be filled_ |
| Training window and refit cadence | _to be filled_ |
| Coverage rule | §4 |
| Pilot slice / confirmatory slice | 2021–2223 / 2324–2425 |
| Power calculation and frozen n | _from step 2 above_ |
| Primary metric and scoring rules | §5 |
| Correction family | §7 |
| Kill condition | §9 |
| Commit SHA and freeze timestamp | _to be filled_ |

## 9. Kill condition

If the frozen engine does not beat the benchmark on the frozen sample at the pre-agreed
significance, Track A stops for this market. The result is recorded as a null with its
interval, the run is preserved, and a second attempt on the same market requires a
*different hypothesis* — not a retuned version of the same features. That is the only
rule in this document that prevents the project from becoming a search over its own
history.

## 10. What this protocol does not do

- It does not claim the market is beatable, and it does not estimate the chance that it
  is.
- It does not settle Track B (decision support); that needs its own design.
- It does not license publishing derived data — that is P-03, and it is the sponsor's.
- It is not frozen until §8 is filled and the sponsor accepts the freezes.
