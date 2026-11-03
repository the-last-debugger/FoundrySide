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

Validation, run and observed: `python research/fixture_time.py --audit` parses every
fixture clock, maps its division, and fails on any timestamp that falls in a spring gap or
an autumn fold. Result on the corpus: **14,802 clocks parsed, 8 divisions mapped, zero
ambiguous or unmapped**. A timestamp in a gap or a fold is an error, not a rounding
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
2. **Decompose the variance**: within-cluster `σ²_w`, between-cluster `σ²_b` of the
   cluster means, and `m̄` the mean fixtures per cluster.
3. **ICC** = `σ²_b / (σ²_b + σ²_w)`; **design effect** `D = 1 + (m̄ − 1) · ICC`.
4. **The variance the sizing uses** is `Var(mean Δ) ≈ σ²_b / K + σ²_w / n`, with `K`
   clusters and `n` fixtures — not `sd²/n`. This is the quantity that decides power.
5. **Uncertainty in `D`**: cluster-bootstrap the pilot (resample clusters with
   replacement, 2,000 replicates), recompute ICC and `D` each time, and size against the
   **95th percentile** of `D`. Sizing on a point estimate of `D` would repeat the error
   of sizing on a point estimate of the spread.
6. **The confirmatory test is the same statistic**: a cluster bootstrap over `K`
   clusters of the confirmatory mean Δ, rejecting when the 95% percentile interval
   excludes zero. If the pilot's bootstrap is too coarse because `K` is small, that is
   reported as a limitation of the design, not smoothed over.

`K` is 40 here (8 divisions × 5 seasons). That is not many, and it is the reason step 5
exists: the uncertainty in `D` is large enough to matter.

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
difference Δ, not on the baseline's standard error. `research/LOGLOSS_POWER.md` computes
it on real fixtures and reports the governing quantity:

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
