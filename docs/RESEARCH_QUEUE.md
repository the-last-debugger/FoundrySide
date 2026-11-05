# Research status register

No corpus scoring is authorised. The dispersion protocol remains gated; the market-companion
assessment is queued for the next cycle and must not start concurrently. Everything finished is listed
with its report; everything else is deferred with the evidence that would justify activating it.
Historical records are not erased.

Two experiments were completed under the day-pass and are recorded: **E25** (stake and multiplier
structures) and **E26** (jackpot pool mechanics, arithmetic only).

## Active

**No corpus scoring is authorised.** **Track A is closed** (docs/CONCLUSION.md).

The dispersion study was **approved** and then **stopped before scoring**: its pre-registered model
requires Bb1X2, the number of books behind the maximum and average, and **no held file contains that
column** (0 of 40 checked). docs/DISPERSION_BLOCKER.md records the defect and three options; the
study has not started and no result exists.

## Next

**No next task authorised.** Two items wait on the sponsor rather than on the builder:

1. **The dispersion study** needs the Amendment A1 protocol approved before any scoring. Its blocker is
   documented and its options are priced.
2. **The market-companion assessment** is queued and must not start concurrently.

Everything else in the deferred backlog waits on data that does not exist yet, and each entry records
the evidence that would justify activating it.

## Queued by the sponsor — not started

**Market-companion assessment and architecture.** Queued 2026-11-05 for the next cycle, explicitly
not to run concurrently with the dispersion study.

Scope when it opens: how market modelling, standalone/slip/jackpot workflows, target-multiplier
construction and long-run selection monitoring fit together; which capabilities are supportable with
held data versus needing method validation, timestamped data or nothing at all; metrics that keep hit
rate, calibration, price improvement, expected value and profitability separate; how favourites are
used without being called safe; and how jackpot discovery sits beside the wider ambition. The smallest
coherent next steps and their dependencies are part of the ask.

**Status: queued for the next cycle; it must not start concurrently with the dispersion study.**
Nothing has been drafted.

## Decision pending with the sponsor

Whether to accept the strategic assessment and authorise its proposed first bounded scope. No
experiment starts before that review.

## Completed this session, in order

| Item | Result | Report |
| --- | --- | --- |
| Disagreement-aware shrinkage (queue 1) | no policy beats market-only; fitted thresholds hit the grid floor | `SHRINKAGE_POLICY.md` (E19) |
| Price inventory (queue 2, first half) | opening and closing snapshots exist; the per-selection best quote exceeds the average quote; the Max overround is synthetic | `PRICE_INVENTORY.md` (E20) |
| Hit-rate and metric audit | 54.30% vs 57.66%, diff −0.0336 [−0.0459, −0.0214]: worse at picking and at scoring | `HIT_RATE_AUDIT.md` (E21) |
| Price movement (queue 2, second half) | signed −0.00022 [−0.00041, −0.00004], size −0.00001: the close already contains the move | `MOVEMENT_STUDY.md` (E22) |

## Deferred backlog

Each entry records why it is deferred and what would activate it. None is active.

| Idea | Why deferred | Activation evidence |
| --- | --- | --- |
| New feature families | eight variables, three mechanism classes and two market structures found nothing; more of the same has low expected value | a mechanism that predicts *disagreement quality*, not just its size |
| New model families | overdispersion was real but worth 0.0004 nats; shrinkage collapses to market-only | evidence any model can beat market-only on held-out log loss |
| Timestamped price feed | blocked on access, not technique | a lawful, zero-cost, timestamped source; `SOURCE_TIMING.md` has the retry |
| Multi-book live comparison | only closing snapshots exist | a live feed with timestamps and account terms |
| Jackpot assistance | no structured per-round history found | published rules plus a results archive; `JACKPOT_FEASIBILITY.md` |
| 1X2 model comparison | no 1X2 model exists; 53.3% is a market benchmark only | building one, which is a new workstream and not yet justified |
| Other sports (multi-sport ambition) | no data held, and the current corpus has open questions | sponsor authorisation plus a zero-cost source |
| Track B product build | no build authorised; evidence negative | a measured user benefit from a study this corpus cannot run |

## Blockers

| Blocker | What it stops | Who resolves |
| --- | --- | --- |
| No timestamped prices | any executable-value claim | a source decision (`SOURCE_TIMING.md`) |
| No user study | any behavioural claim about decision support | outside this corpus |
| P-02 freeze not taken | confirmatory scoring | sponsor; recommendation is to hold (`CONFIRMATORY_READINESS.md`) |

## Rules

- One active task at a time; breadth lives here, not in execution.
- Every experiment gets a pre-registration committed before it runs.
- A completed item is reported with its result and recommendation, then the next authorised item
  starts without waiting.
- Cheap, independent exploratory work is allowed only if it does not compete with the active task.
