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

## 3. Forecast timing and point-in-time rule

**There is no observation timestamp in the source files.** They record a closing price
and a kickoff date and time; they do not record when the closing quote was observed.
Nothing in this protocol may claim otherwise, and no result may describe the model's
cutoff as "before the closing price was observed", because that instant is unknown.

Instead the design uses a **fixed, reproducible information cutoff**:

```
cutoff = kickoff time − 90 minutes
```

applied to the fixture's own `Date` and `Time` columns. The rules that follow from it:

- **Model inputs.** Only matches whose result was final before the cutoff. Operationally:
  a prior match qualifies when its kickoff plus three hours is at or before the cutoff,
  which covers full time plus stoppage and a margin for publication.
- **No same-day leakage.** A match earlier the same day does not qualify unless it
  finished inside that window, which excludes the common case of a 15:00 fixture
  following a 12:30 one.
- **No aggregate that includes the fixture.** No season-ending tables, no form window
  that reaches forward, no standings computed from a snapshot taken after the cutoff.
- **Auditability.** Every prediction record stores the maximum input timestamp used.
  The audit recomputes the cutoff from `Date` and `Time` and fails the run if any record
  exceeds it. This is the write-time provenance lesson from
  `OLPRS_v2/docs/PIT_INTEGRITY_2026-10-31.md`, where the join was correct and the
  provenance was still lost.
- **The benchmark stays the closing price**, which is later than the cutoff. That is
  deliberate — the comparison is "our T−90 forecast against the closing line" — and it is
  not a claim about when the closing price was set.
- If a timestamped price source is obtained later, its provenance is documented
  separately and it becomes a second benchmark, not a reinterpretation of this one.

### The clock is an assumption, and it is checked

The files carry a date and a kickoff time with no timezone field. Subtracting ninety
minutes from a wall clock is reproducible arithmetic on an ambiguous clock, which is not
auditable. The rule is therefore: each division's date and time are **local civil time in
that country**, converted to UTC with the IANA zone below, and all arithmetic happens in
UTC.

| Division | Zone |
| --- | --- |
| E0, E1 | Europe/London |
| SP1 | Europe/Madrid |
| D1 | Europe/Berlin |
| I1 | Europe/Rome |
| F1 | Europe/Paris |
| N1 | Europe/Oslo |
| P1 | Europe/Lisbon |

This is an assumption about the source, not a fact read from it, which is why it is
tested. It matters twice a year: across a daylight-saving boundary two apparently
adjacent fixtures differ by an hour, and that hour decides whether an earlier match counts
as available.

Validation, run and observed:

```
python research/fixture_time.py --audit --expect 14802
fixture rows:            14802
parsed to a UTC instant: 14802
missing clock fields:    0
failed conversion:       0
all 14802 fixture rows accounted for, no ambiguous or unmapped clocks
```

The audit fails on any missing or unparseable clock rather than skipping it, and
`--expect` fails the run when the corpus is incomplete, so a truncated download cannot
pass as clean. A timestamp in a spring gap or an autumn fold is an error, not a rounding
decision.

The parsed instant is what the cutoff is computed from and what the prediction record
stores, so "the cutoff was respected" is checked against the fixture's actual parsed
timestamp rather than against string comparison of clock text.

A run in which the cutoff cannot be verified is reported as invalid, not as a result.

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

**Sign convention, defined once.** Δ is **market minus model**: the reduction in log loss
the model achieves. Positive Δ is an improvement, and the target is Δ ≥ 0.01 nats. An
earlier draft of this protocol wrote the difference as model minus market, which would
have made every improvement negative; the code and the generated tables have always used
market minus model, and the definition lives here so the two cannot drift again.

The comparison is **paired**: per-fixture Δ, summarised as a mean with a bootstrap
interval resampled over fixtures, and a cluster bootstrap over (division, season). The
accuracy study in `research/POWER.md` found that clustering can remove most of the power
when a model's advantage varies by league — an earlier claim in this protocol that
clustering was negligible is withdrawn, and the same caution is applied to log loss
rather than assumed away.

### The cluster-aware procedure, operationally

A table of assumed design effects is sensitivity analysis, not a method. The method is
this, and it is what the pilot runs:

1. **From the pilot's out-of-fold predictions**, compute Δ for each fixture, labelled by
   cluster `k` (division × season), with `m_k` fixtures per cluster.
2. **State the estimand.** The headline metric is the **fixture-weighted** mean Δ: every
   eligible fixture counts equally, so a large division-season contributes more than a
   small one. This is not the same estimand as an equal-weighting of the 16 clusters, and
   the two give different variances.
3. **Decompose the variance**: within-cluster `σ²_w`, between-cluster `σ²_b` of the
   cluster means. `ICC = σ²_b/(σ²_b + σ²_w)` and `D = 1 + (m̄ − 1)·ICC` are reported for
   continuity, but they are not what the sizing uses.
4. **The variance the sizing uses**, for the fixture-weighted estimand with the actual
   cluster sizes:

   ```
   Var(mean Δ) = σ²_w / n  +  σ²_b · Σ_k (m_k / n)²
   ```

   With equal sizes `Σ(m_k/n)² = 1/K` and this collapses to the familiar expression. The
   confirmatory clusters are **not** equal — 293 to 552 fixtures — and for this corpus
   `Σ(m_k/n)² = 0.0656` against `1/16 = 0.0625`, so the between-cluster term is **1.049×**
   the equal-size value. Small, but it is not one, and `m̄` does not make it go away.

   | Phase | Seasons | Fixtures | Clusters `K` |
   | --- | --- | --- | --- |
   | Pilot | 2021–2223 | 8,941 | **24** (8 × 3) |
   | Confirmatory | 2324–2425 | 5,794 | **16** (8 × 2) |
   | Whole corpus | 2021–2425 | 14,735 | 40 (8 × 5) |

   Sizing uses the **confirmatory** count, 16. Fixtures inside those 16 do not create
   clusters; only seasons do.
5. **The confirmatory test is a cluster-robust t**, not the percentile bootstrap: a
   linearised cluster-robust variance of the fixture-weighted mean, with `t` on `K−1 = 15`
   degrees of freedom. The reason is measured, not stylistic. At 16 clusters the
   percentile bootstrap rejects **8.1%** of the time under the null where 5% is nominal,
   because the resampled distribution is too narrow; the cluster-robust t rejects **4.9%**.
   A power figure computed for the bootstrap is therefore inflated by false positives.
   The valid test costs power — 72.8% against 79.2% at the same cell — and that is the
   price of a calibrated test.
6. **Sizing resamples the pilot; it does not model it.** The pilot Δ are centred on their
   fixture-weighted mean, then the target effect is imposed. Each simulation draws 16
   clusters with replacement from the 24 pilot clusters, resamples fixtures within each to
   the confirmatory cluster sizes, and runs the confirmatory test. Power is the rejection
   rate. No `σ_w`, no `σ_b`, no formula.

   **Centring is not a detail.** The pilot mean is about −0.025 — the model is behind the
   market — so imposing +0.01 on uncentred data tests "still behind, slightly less", and a
   two-sided test rejects on the existing disadvantage. An earlier version did that and
   reported 93.5%, which was not power at all. Offset invariance is now a regression test:
   adding a constant to every pilot Δ must leave the power unchanged.

   **Measured result, pilot Δ of the first model:** power **66.6%** (MC SE ±1.7pp) at a
   0.01-nat effect; null rejection 5.2% against a nominal 5; independent runs 64.2% and
   66.1%. **The design is not adequate at 0.01 nats for this spread.** It reaches 80% at an
   effect of about **0.0116** nats, so the stated target is just beyond it.

**What this implies.** The adequacy question that was open for many rounds now has an
answer for one model's spread: 16 clusters and 5,794 fixtures give roughly two-thirds power
at 0.01 nats. Three responses are available and all are sponsor decisions, taken before the
freeze:

1. **Raise the target effect** to something this design detects — about 0.012 nats — and say
   so in the freeze rather than after a null.
2. **Add clusters**, which means adding seasons, which raises the exchangeability question
   the earlier analysis already flagged.
3. **Add markets to the family**, increasing n at the cost of a larger correction family.

What is not available is running the test as designed, missing significance, and reporting
it as evidence of no edge.

The ±3pp calibration tolerance is a **guardrail, not a test**: it flags a model whose
probabilities are systematically off, and it is reported with the reliability plot and
bin counts so a thin-bin artefact is visible.

## 6. Effect size, and why 0.01 nats

**Target: 0.01 nats per fixture**, i.e. 0.6706 → 0.6606, a 1.5% relative improvement.

That is not a modest ask. The market's margin is 3.1%, so a 1.5% relative gain in log
loss is the same order as the book's own edge — which is exactly why it is the right
scale for a first serious test rather than a comfortable one. An improvement of 0.001
nats would be indistinguishable from noise at any sample this project can afford.

**Sample size, for this metric.** Power depends on the spread of the per-fixture score
difference Δ, not on the baseline's standard error. `research/LOGLOSS_POWER.md` is a
**synthetic sensitivity calculation on the real-fixture corpus**: real prices and outcomes
are the inputs, but the per-fixture Δ is produced by a device, not by a model's
out-of-fold predictions. It therefore fixes the *shape* of the relationship between the
spread and the sample needed; it does **not** measure this experiment's power, and the
pilot has not yet produced an empirical figure.

The table below is that synthetic sensitivity, not measured power:

| SD of Δ | n for 80% power | Power at the confirmatory slice (5,794) |
| --- | --- | --- |
| 0.10 | 785 | 100% |
| 0.15 | 1,766 | 99.9% |
| 0.20 | 3,140 | 96.8% |
| **0.27** | **5,722** | **80.5%** |
| 0.35 | 9,615 | 58.5% |
| 0.50 | 19,622 | 33.1% |

**The confirmatory slice supports 80% power at 0.01 nats only while SD(Δ) ≲ 0.271** under
independence, before any design effect. That number, not the margin, is what the pilot
has to establish.

**Dependence changes the threshold, so the SD alone is not sufficient.** With a design
effect `D` — effective n = n/D — the permitted SD shrinks by `sqrt(D)`:

| Design effect | Effective confirmatory n | SD(Δ) still detectable |
| --- | --- | --- |
| 1.0 | 5,794 | 0.272 |
| 1.2 | 4,828 | 0.248 |
| 1.5 | 3,863 | 0.222 |
| 2.0 | 2,897 | 0.192 |

The pilot estimates both quantities through steps 2–5 of §5. The table above is what
happens to the threshold as `D` grows; it is not a substitute for measuring `D`, and
sizing on the spread alone would repeat the mistake the accuracy analysis made.

Procedure:

1. **Pilot** on seasons 2021–2223, disjoint from the confirmatory slice: fit the engine,
   and measure SD(Δ) and the between-cluster variance of Δ on out-of-fold predictions.
2. **Compute n** from the measured spread, not from a guess, and record it.
3. **Freeze**, then run on 2324–2425.

The pilot may not contribute to the confirmatory claim; that is the reason it is a
separate slice.

If the measured SD exceeds the threshold, the response is chosen **before** scoring, from:
extending the slice to more seasons (older, possibly not exchangeable); adding markets to
the family (raises n, enlarges the correction family); or raising the target effect and
saying so in the freeze. What is not available is running the test, missing significance,
and reporting it as evidence of no edge.

The accuracy tables in `research/POWER.md` are now explicitly a **supplementary
pick-level sensitivity study** and must not be cited as power evidence for log loss.

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
| Forecast timestamp | kickoff − 90 min, computed in UTC per §3 |
| Competition timezones | per-division IANA zones, `research/fixture_time.py` |
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
