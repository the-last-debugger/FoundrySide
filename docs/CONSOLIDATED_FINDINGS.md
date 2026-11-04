# Consolidated findings

One document for a reader who wants the state of the project without reading eighteen research
reports. Everything below is traceable to a stamped artefact in `research/` and a script whose
hash that artefact records.

**Scope.** Research phase only. No confirmatory scoring has occurred; the confirmatory seasons
are untouched. The 0.01-nat target and the market comparator have not changed.

---

## 1. What was measured, independently of any model

| Finding | Value | Source |
| --- | --- | --- |
| Corpus | 40 files, 8 divisions, 5 seasons, 14,802 fixtures | `RESULTS_T0_T1_T3.md` |
| Closing-price coverage | 100% for 1X2 (14,799 Pinnacle, 3 Bet365); 99.6% for O/U 2.5 | same |
| Favourite accuracy, 1X2 | **53.3%** (95% CI 52.5–54.1) | same |
| Home / draw / random | 43.0% / 25.2% / 33.3% | same |
| Mean 1X2 overround | 2.8% | same |
| Same-match leg dependence | realised joint 40.9% vs product of marginals 27.5%; **ratio 1.49** (bootstrap CI 1.47–1.51) | same |
| Margins by division | 1X2 2.6–3.2%; O/U 2.9–3.5% — uniform | `MARKET_STRUCTURE.md` |
| Data integrity | 0 duplicate fixtures, 0 double headers, 0 missing scores | `DATA_AUDIT.md` |

The 51.5% figure imported from the virtual-league project is **withdrawn**: it is lower than the
real baseline, so using it would have set a bar that was too easy.

## 2. The first model and what is wrong with it

A multiplicative goals model with shrinkage, updated match by match, predicting at a T−90 proxy
cutoff. 8,941 pilot predictions.

| Measure | Model | Market |
| --- | --- | --- |
| Log loss | 0.6988 | **0.6742** |
| Brier | 0.2520 | 0.2407 |
| AUC | 0.5623 | **0.6073** |
| Reliability (lower better) | 0.0048 | 0.0001 |
| Resolution (higher better) | 0.0030 | **0.0083** |

Mean Δ = **−0.0246 nats**, cluster CI [−0.0285, −0.0207]. The model is worse than the closing
price, and the decomposition says why: it carries roughly **a quarter of the market's
separation**. Reliability is a smaller and fixable defect; resolution is the structural one.

## 3. Calibration: recovered, and it is not enough

Out-of-fold Platt scaling (fitted on two seasons, evaluated on the third, rotated) improves log
loss in every held-out season:

| | Log loss |
| --- | --- |
| Raw model | 0.6988 |
| Platt (out-of-fold) | **0.6874** |
| Isotonic | 0.7637 (overfits) |

Gain **0.0114 nats** — about 46% of the deficit — with a fitted slope of **0.40**, meaning the raw
model's logits are two and a half times too spread. After calibration, reliability falls to
0.0000 and AUC is unchanged by construction (0.5623): **a monotone map cannot create
separation**, and about half the deficit is exactly that.

## 4. Where the gap is, and is not

| Split | Result |
| --- | --- |
| Season | no differences survive correction (q 0.48–0.71) |
| Division | no differences survive correction |
| Probability band | **the only dimension that moves**: 20–30% worst (−0.078, q 0.006), 40–50% best (−0.014, q 0.001) |
| Kickoff slot | only 21+, 3 clusters — disregarded |

The band pattern is what overconfidence predicts, and it is what the Platt map already fixes.
There is no division or season in which the model is fine.

The worst 2% of fixtures (n=178) show only **7.3% disagreement with the market's side**, against
29.7% overall: the tail is confident calls that lost, not contrarian views that failed.

## 5. Information sources tested, and their verdicts

All tests use the same protocol: market-conditioned logistic, leave-one-season-out, cluster
bootstrap, and — in the screen — a within-season permutation null and Benjamini-Hochberg across
families.

**How to count these.** They are not nine independent experiments. E4, E5 and E7 are three
families that E8 also contains; E8 tests six families built from eight variables; E9 is one
alternative distributional specification over the same inputs. The honest count is **eight
variables, in six families, screened once** — with three of those families also examined
individually earlier, which is repetition rather than replication.

| # | Candidate | Gain (nats) | Interval | Verdict |
| --- | --- | --- | --- | --- |
| E4 | Cross-book disagreement | −0.0001 | [−0.0002, +0.0001] | no gain detected |
| E5 | Schedule congestion | −0.0012 | [−0.0024, −0.0002] | negative, significantly |
| E7 | Cross-market (1X2 → totals) | −0.0002 | [−0.0004, +0.0000] | no gain detected |
| E8 | Recent scoring trend | −0.0001 | [−0.0003, +0.0001] | no gain detected |
| E8 | League scoring environment | −0.0000 | [−0.0002, +0.0002] | no gain detected |
| E8 | All eight features combined | −0.0016 | [−0.0029, −0.0005] | negative, significantly |
| E9 | Negative-binomial totals | +0.0004 | prequential dispersion | not a material gain |
| E11 | Favourite-longshot (pre-registered, held-out season) | gap +0.026, return −0.004 | interval spans zero | not supported |

Three further **mechanism classes** were tested after the feature screen, each under the same
protocol: calendar folklore (full moon, Friday 13th, the 13th, weekend), head-to-head history
(bogey-team goals and results, with pair-level resampling), and style mismatch (attack/defence
interaction, venue asymmetry, scoring volatility). Calendar folklore resolves to four distinct outcomes rather than one: the 13th of the month is
significantly negative, weekend kickoff is undetermined at this precision, the full moon is null,
and Friday the 13th is untested at eleven fixtures. Head-to-head and style are null, after
stress testing.

In the screen, all six families have permutation p between 0.388 and 0.900 and BH q = 0.900. No
family is positive in any held-out season. A high permutation p means **a positive gain of that
size was not detected**; it is not evidence that no information exists.

## 6. What this establishes

1. **The market baseline is measured, not assumed** — 53.3% favourite accuracy on 14,802 real
   fixtures, with intervals, and a benchmark whose own log loss is 0.6742.
2. **The evaluation instrument works** — point-in-time rules, frozen predictions, cluster-aware
   uncertainty, permutation nulls, multiplicity correction, and artefact provenance.
3. **The first model's deficit is quantified and decomposed** — 0.0246 nats, of which about half
   is calibration (recoverable) and half is missing separation (not recoverable by any map).
4. **No tested candidate demonstrated a material improvement** over the closing price under the
   current pilot design. Eight variables, six families, one screen with a permutation null.
5. **The corpus is internally consistent** — the nulls are not a data-corruption artefact.
6. **The one positive signal failed its own pre-registered test** — the favourite-longshot gap at
   0.65 was +0.026 on a held-out season with an interval spanning zero, and a negative return.

## 6a. Track B — what a filtered view is worth

An abstention rule over the market price raises hit rate from 57.7% at full coverage to 91.3% at
0.3% coverage, but the accuracy-minus-implied gap stays near zero: the confidence is the market's,
not the filter's. In decision-theoretic terms, over every fixture with abstentions scoring zero,
following the raw board at a 1% stake costs 0.0003 nats of log-wealth per fixture, and filtering at
0.65 recovers most of that cost: policy growth −0.00002 with a cluster interval of
[−0.00006, +0.00003]. The filter is worth roughly what the margin costs, which is to say it
breaks even rather than pays.

That interval is a full-denominator measure and was corrected once: an earlier version
recomputed the bootstrap mean over the selected fixtures only, which produced an interval ten
times too wide for a different estimand.

`docs/TRACK_B_DESIGN.md` fixes the success criteria before scoring. Criterion 2 — non-negative
log-growth with an interval excluding a 0.001-nat loss — fails on current evidence, so the design
predicts that **this product, measured this way, on this market, is not worth building**. That is a
result under the tested measures and scope, not a general verdict on decision-support products: the
broader objective includes a user deciding better, which a corpus of already-placed closing prices
cannot evaluate.

## 7. What this does not establish

- That no edge exists in football. This corpus has eight large European divisions, four-plus
  seasons, closing prices only, and no news, lineups, or in-play data.
- That the market is efficient. It says these prices absorbed the information available here.
- That a better model cannot do better. It says a better model needs information this corpus
  does not contain — not a better functional form, a different segmentation, or more
  recalibration.
- Anything about the confirmatory seasons. They were never scored.

## 8. What would change the answer

Three routes, each a sponsor decision because each costs money, time, or legal exposure:

| Route | What it needs | Why it might work |
| --- | --- | --- |
| **Faster information** | Lineup and team-news feeds, timestamped before kickoff | The model's deficit is information, and pre-lineup prices are the classic place a slower price is exploitable |
| **Thinner markets** | Lower divisions, secondary markets, non-European leagues | Less sharp money; margins here were uniform, but the corpus contains only large competitions |
| **Different comparison** | A market where the price is not the benchmark of skill — e.g. decision support rather than price-beating | The protocol already separates Track A (beat the price) from Track B (help a user decide) |

None of these can be tested with the current data, and no spending is authorised.

## 7a. Source map

Every claim above traces to one of these reports; each carries a hash of the generator that
produced it.

| Report | Experiment | Establishes |
| --- | --- | --- |
| RESULTS_T0_T1_T3.md | T0, T1, T3 | baseline, coverage, accumulator dependence |
| MARKET_STRUCTURE.md | E-survey | margins by division, uniform |
| PILOT_FRAME.md | frame | the pilot/confirmatory split and its inclusion rules |
| PILOT_PREDICTIONS.md | model | the prequential forecast, match by match |
| PILOT_POWER.md | sizing | power at the calibrated cutoff and the option costings |
| LOGLOSS_POWER.md, CLUSTER_POWER.md, POWER.md | sizing | earlier power analyses, superseded but retained |
| GAP_DIAGNOSIS.md | E3 | the decomposition: reliability versus resolution |
| CALIBRATION_STUDY.md | E1 | Platt recovers 46%; isotonic overfits |
| SEGMENT_STUDY.md | E2 | the band is the only dimension that moves |
| RESIDUAL_STUDY.md | E3 | AUC and the shape of the worst errors |
| BOOK_DISAGREEMENT.md | E4 | cross-book disagreement adds nothing |
| CONGESTION_STUDY.md | E5 | rest and load add nothing |
| CROSS_MARKET.md | E7 | the 1X2 draw adds nothing |
| FEATURE_SCREEN.md | E8 | eight variables, six families, all null |
| MODEL_FAMILY.md | E9 | the specification is not the constraint |
| TRACK_B.md | E10 | abstention buys selection, not skill |
| FL_TEST.md | E11 | the favourite-longshot signal failed out of sample |
| SUPERSTITION_STUDY.md | E12 | calendar folklore is null |
| BOGEY_TEAM.md | E13 | head-to-head fails pair-level resampling |
| STYLE_MISMATCH.md | E14 | style interaction is null, and negative |
| DATA_AUDIT.md | E6 | the corpus is internally consistent |

## 8a. Reproducibility

scripts/repro_sweep.py regenerates every report in dependency order and reports drift: any
committed artefact that changes when its generator is rerun. Two defects it was written to catch
were both live.

The manifest stamped every row with the current clock, so a rerun against byte-identical data
rewrote all eighty rows and every report quoting the snapshot hash churned with it. It now keeps
a file's first-seen time unless its bytes changed, and the reports derive their provenance from
the manifest rather than from 
ow().

The report-stamp test carried a hand-maintained list that silently stopped growing because the
anchor string it inserted against had moved; it now discovers every stamped report.

## 9. Open items

- The protocol is not frozen; the sizing says a 0.01-nat effect needs about 0.0116–0.0130 nats at
  the confirmatory design's power, and a third season would raise power from 70.5% to 86.6%.
- The availability rule is a three-hour proxy, sensitivity-tested at six hours, not a measured
  timestamp.
- The closing price has no observation time, so no claim here is about information available at
  T−90 in the market.
- Every protocol correction is recorded in `docs/COLLAB/THREAD.md`, append-only, with the revision
  it answers; the review queue holds the rows still outstanding, and its count changes with every
  review round, so it is not restated here.

---

**The one-sentence version.** The project built a trustworthy instrument, measured the market it
must beat, fitted a first model, diagnosed exactly why it falls short, and found no information
source in this corpus that improves on the closing price — so the next step is new data or a
different question, and both are decisions rather than experiments.
