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
| 1 | **Calibration vs information** | The gap is partly a mapping failure, not only missing information | Whether to keep this model family and recalibrate, or replace it | **first result: mixed** — Platt recovers 46% |
| 2 | **Where and when the gap changes** | The model is less wrong in identifiable segments | Whether to segment rather than pool | **done: the gap is uniform** |
| 3 | **Residual and failure analysis** | The largest errors are systematic, not isolated | Which feature class to attack next | **done: the tail is not a class** |
| 4 | **Alternative information and model families** | Pre-cutoff data hold information the market has not fully priced | Whether an incremental feature exists at all | **next — the only workstream that can now move the number** |
| 5 | **Market structure and segmentation** | The market is differently calibrated by band or division | Where the price is weakest, if anywhere | **first result: margins uniform** |
| 6 | **Data and timing audit** | Undetected leakage or misalignment is inflating or deflating every number | Whether current evidence can be trusted | partially done (provenance, availability proxy) |

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

## What the three studies together say

Calibration is finished. After an out-of-fold Platt map the reliability term is 0.0000 — there
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

## Next actions, in order

1. **Workstream 2** — segment the residual by season, probability band, division and kickoff
   hour, with clustered intervals and a multiplicity note. Cheap, uses held data.
2. **Workstream 1, second half** — re-run the decomposition on the Platt-calibrated forecast:
   how much of the reliability term survives, and what resolution it has.
3. **Workstream 3** — the 200 highest-loss pilot fixtures: are they a pattern or a tail?
4. **Workstream 4** — one genuinely new pre-cutoff feature, chosen after 2 and 3 say where the
   errors are. Not before.

## Stop conditions

A workstream stops, and says so, when: its hypothesis is refuted on held-out seasons; the effect
disappears under cluster-aware uncertainty; the gain is calibration-only and the primary metric
does not move; or the cost of the next test exceeds its expected information. Negative results
are preserved in the report that produced them.
