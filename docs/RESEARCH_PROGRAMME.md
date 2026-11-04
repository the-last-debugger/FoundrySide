# Research programme

**Objective.** Find a reliable, repeatable way to give a user an advantage over relying on the
market alone — or establish, with evidence, that the available data cannot.

**Standing rules.** Pilot seasons only for exploration; the confirmatory slice stays untouched.
The market comparator, outcome definition, primary metric (log loss) and the 0.01-nat target do
not change without the sponsor. Every result here is exploratory until independently supported.
No spending, accounts, publication or real-money execution.

**Discipline for every study.** Named hypothesis, as-of rule, sample and exclusions, comparator,
split design, tuning boundary, seeds, commands, cluster-aware uncertainty, multiple-testing
treatment and a stated failure condition. Fit and evaluation never share outcomes.

---

## Workstreams, ranked by expected information per unit cost

| # | Workstream | Hypothesis | Decision it could change | Status |
| --- | --- | --- | --- | --- |
| 1 | **Calibration vs information** | The gap is partly a mapping failure, not only missing information | Whether to keep this model family and recalibrate, or replace it | **done: Platt recovers 46%; rest is resolution** |
| 2 | **Where and when the gap changes** | The model is less wrong in identifiable segments | Whether to segment rather than pool | **done: band only; divisions and seasons flat** |
| 3 | **Residual and failure analysis** | The largest errors are systematic, not isolated | Which feature class to attack next | **done: tail is confident losses, not a class** |
| 4 | **Alternative information and model families** | Pre-cutoff data hold information the market has not fully priced | Whether an incremental feature exists at all | **done: eight variables, six families, all null** |
| 5 | **Market structure and segmentation** | The market is differently calibrated by band or division | Where the price is weakest, if anywhere | **done: margins uniform, 2.6-3.5%** |
| 6 | **Data and timing audit** | Undetected leakage or misalignment is inflating or deflating every number | Whether current evidence can be trusted | **done: audit clean; availability proxy labelled** |

## What is already established

| Finding | Evidence | Status |
| --- | --- | --- |
| The market baseline is 53.3% favourite accuracy; the virtual-league 51.5% does not transfer | `RESULTS_T0_T1_T3.md` | accepted |
| Same-match accumulator legs cannot be multiplied (1.49×, CI 1.47–1.51) | `RESULTS_T0_T1_T3.md` | accepted |
| Margins are uniform across the eight divisions (2.6–3.2% on 1X2) | `MARKET_STRUCTURE.md` | descriptive |
| The pilot model trails the market by 0.0246 nats (CI −0.0285 … −0.0207) | `GAP_DIAGNOSIS.md` | descriptive |
| The model is badly overconfident: Platt's slope is ~0.40 | `CALIBRATION_STUDY.md` | out-of-fold, consistent across folds |
| Recalibration recovers **0.0114 of 0.0246 nats** | `CALIBRATION_STUDY.md` | out-of-fold, all three folds improve |
| Isotonic overfits at this sample size (0.7637 vs 0.6874) | `CALIBRATION_STUDY.md` | as expected |

## Experiment register

| # | Experiment | Result | Status |
| --- | --- | --- | --- |
| E1 | Platt/isotonic recalibration, leave-one-season-out | Platt +0.0114 nats of a 0.0246 gap; isotonic overfits | survives out of fold; exploratory |
| E2 | Gap by season, division, band, kickoff slot | Band is the only dimension that moves; divisions and seasons do not | descriptive; band only |
| E3 | Decomposition after calibration, tail profile | Reliability collapses to 0.0000; AUC 0.562 vs market 0.607; tail is confident losses | descriptive |
| E4 | **Cross-book disagreement as incremental information** | **gain −0.0001 nats, CI [−0.0002, +0.0001], AUC unchanged** | **negative: no gain detected under this specification** |
| E5 | **Schedule congestion (rest difference, days between matches, 14-day load)** | **gain −0.0012 nats, cluster CI [−0.0024, −0.0002], AUC 0.6070 → 0.6055** | **negative — degrades; not the route** |
| E6 | Data and timing audit: duplicates, double headers, misses, extreme kickoffs | 0 duplicates, 0 double headers, 0 missing scores, 67 missing O/U prices, 0 implausible times | clean |
| E7 | **Cross-market: 1X2 draw probability as information for totals** | **gain −0.0002 nats, cluster CI [−0.0004, +0.0000], AUC 0.6070 → 0.6066** | **negative — the two prices agree** |
| E8 | **Feature screen: six families under one protocol, permutation nulls, BH across families** | **all six null; q = 0.900; permutation p 0.388–0.900; no family positive in any season** | **negative under tested specifications; feature space not exhausted** |
| E9 | **Model family: independent Poisson versus an overdispersed negative binomial** | **conditional dispersion 1.064 [1.032, 1.094]; NB gain 0.0004 nats; market still 0.024 ahead** | **negative: mildly misspecified, but correcting it is worth 0.0004** |
| E10 | **Track B: abstention rule over market prices** | **accuracy 57.7 to 91.3 percent as coverage falls 100 to 0.3 percent; accuracy minus implied near 0 except at 0.70+, where cells hold 23-322 fixtures** | **value is selection, not skill; top rows are favourite-longshot suspect** |
| E11 | **Pre-registered favourite-longshot test: threshold chosen on 2021-2122, applied unmodified to 2223** | **not supported: gap +0.026 with interval [-0.016, +0.087]; return -0.004 with interval [-0.062, +0.081] on 266 held-out fixtures** | **negative — the one positive signal did not replicate** |
| E12 | **Superstition: full moon, Friday 13th, the 13th, weekend** | **four outcomes: the 13th significantly negative, weekend undetermined, full moon null, Friday 13th untested at n=11** | **negative** |
| E13 | **Bogey team: head-to-head goals and result history** | **first positive point estimates (+0.00002, +0.00010) but both intervals straddle zero and widen under pair-level resampling** | **negative after stress test** |
| E14 | **Style mismatch: attack/defence interaction, venue asymmetry, volatility** | **all null; the intuitive interaction is negative (-0.00017)** | **negative** |
| E15 | **Best-price discovery between the two held books, by division** | **0.17 pp saved overall [0.14, 0.20]; 0.06 pp in P1 to 0.28 pp in D1; 99.1% still negative EV** | **real, bounded, and larger where margins are wider** |
| E16 | **Accumulator pricing: cross-match multiplication, plus estimability of long combinations** | **2-3 legs consistent with 1; 5 legs 1.373 on 38 wins; an 8-leg rate needs ~18,000 slips and the corpus can form 152** | **multiplication adequate; jackpots not estimable here** |
| E17 | **Forward-only calibration transfer: train on priors, score the next season** | **+0.0102 nats forward against +0.0114 under leave-one-season-out; slopes 0.39 and 0.42** | **deployable: about nine tenths of the gain survives without seeing the future** |
| E18 | **Where the post-calibration gap sits: bands, division, season, disagreement** | **model worse by 0.0178 overall; by 0.0574 where it departs >=0.6 logit (q<0.001, n=1,636) and 0.0039 where it nearly agrees** | **the independent view is the liability, not a uniform deficit** |

## What the three studies together say

Provisional, not final. Calibration is very likely solved. After an out-of-fold Platt map the reliability term is 0.0000 — there
is nothing left to correct — while resolution sits at 0.0022 against the market's 0.0083. The
model carries about a quarter of the market's separation, and no monotone map can change that.

Segmentation offers no route either. The gap is uniform across seasons and divisions once the
multiple-comparison correction is applied; the only deviations are at the extreme probability
bands and the 21+ kickoff slot, both with fewer than 70 fixtures, both in the direction the
overconfidence finding predicts rather than a new one.

The worst errors are not a teachable class. Among the 178 highest-loss fixtures, only 7.3% saw
the model take the opposite side to the market, against 29.7% overall: the tail is dominated by
confident calls that lost, not by contrarian views that failed. There is no sub-population to
route around.

The three results agree on one conclusion: the current feature set does not contain the
information the market has, and the deficit is resolution, not calibration, segmentation or a
fixable tail.

## The calibration result, and why it is not the win it looks like

Platt scaling improves log loss in every held-out season — 0.7007→0.6872, 0.6950→0.6866,
0.7007→0.6886 — with a slope near 0.40, meaning the model's logits need shrinking by a factor of
two and a half. That is real, out-of-fold, and consistent.

It does not close the gap. Half remains, and the decomposition says that half is a resolution
deficit: a monotone map cannot create separation that was never there. So the honest position is
that the current model family is *recoverable to about half its deficit* and no further by
calibration alone.

The trap this result sets is worth naming: a model that is merely shrunk toward the base rate
will look better calibrated and still carry almost no information. The next study must test
whether anything adds **resolution**, not whether something improves the score.

## Where the programme stands

**The original six workstreams are complete** — each was exercised and reported, and the table
above records its outcome. That is not the same as the programme having nothing open: follow-on
work is active, and it is deliberately outside the original six:

| Active follow-on | Status |
| --- | --- |
| E15 best-price discovery, by division | measured; blocked from going further by timestamped-price access (SOURCE_TIMING.md) |
| E16 accumulator pricing and estimability | measured; long combinations closed as not estimable here |
| Product contingency | recorded as a fallback, not a pivot (PRODUCT_CONTINGENCY.md) |
| Source and timing lane | blocked on access, not technique |
| Confirmatory preparation | decision-ready, gated at P-02 (CONFIRMATORY_READINESS.md) |

The earlier serial ordering (segment, then residuals, then one new feature) described the plan
before the work; it is superseded by the evidence, and by the sponsor's instruction that
workstreams run in parallel and that the builder picks the next question rather than following a
queue.

What this does **not** mean: that the corpus contains no exploitable information. It means no
information was detected under the specifications tested — eight variables through a
permutation-tested screen, three mechanism classes, and two cross-source and cross-market checks.
The feature space is not exhausted, and the pilot screen was not designed to exhaust it.

The honest remaining options are the three recorded in the consolidated findings: new information
with a timelier cutoff, thinner markets, or a different comparison. Each is a sponsor decision.

## Verification, not experiment

Three guards now protect the artefacts rather than the hypotheses, and all three have caught
real defects:

| Guard | Catches | Times it fired |
| --- | --- | --- |
| Report stamps | a report edited apart from its generator | twice (drift), once (PILOT_PREDICTIONS after a signature change) |
| Bridge checker | a verdict that names no revision, a row not authorised | once (per-row verdicts), once (malformed header) |
| scripts/repro_sweep.py | any report that does not reproduce, and any generator that rewrites history when nothing changed | once (manifest clock churn) |

A clean sweep is **27 generators** reproducing byte-for-byte.

## Product contingency

A fallback product direction — price discovery, slip assistance, decision support — is recorded
in docs/PRODUCT_CONTINGENCY.md, with the evidence each capability would need. It is not a pivot
and authorises no build.

## Stop conditions

A workstream stops, and says so, when: its hypothesis is refuted on held-out seasons; the effect
disappears under cluster-aware uncertainty; the gain is calibration-only and the primary metric
does not move; or the cost of the next test exceeds its expected information. Negative results
are preserved in the report that produced them.
