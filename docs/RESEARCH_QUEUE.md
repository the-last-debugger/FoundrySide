# Research status register

Nothing is active and nothing is queued behind it. Everything finished is listed with its report;
everything else is deferred with the evidence that would justify activating it. Historical records
are not erased.

## Active

**No active task.**

## Next

**No next task currently authorised.**

## Decision pending with the sponsor

One decision, and only one: whether to authorise the **thin-division market-efficiency
measurement** described in docs/OPPORTUNITY_ASSESSMENT.md.

It is not a model extension. It asks whether the de-vigged closing price is less well calibrated in
the thirteen authorised divisions than in the eight already held. It needs no model to beat anything, no
protocol change, no new market family, and no data cost. The evidence pack — availability, licence
status, fixture counts and the exact estimand — is in the assessment, which this register treats as
complete.

Until that decision is taken, nothing runs: no measurement, no download, no merge, no experiment.

## Completed this session, in order

| Item | Result | Report |
| --- | --- | --- |
| Disagreement-aware shrinkage (queue 1) | no policy beats market-only; fitted thresholds hit the grid floor | `SHRINKAGE_POLICY.md` (E19) |
| Price inventory (queue 2, first half) | opening and closing snapshots exist; per-selection best price is tradeable, the Max overround is synthetic | `PRICE_INVENTORY.md` (E20) |
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
