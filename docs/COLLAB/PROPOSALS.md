# Proposals

Open questions awaiting a sponsor decision. Settled items move to `DECISIONS.md`.

## P-01 — the settlement register (D-04 … D-13) — **settled 2026-11-03**

All ten items were answered in the sponsor's response of 2026-11-03T12:23:48Z and are
recorded in `DECISIONS.md`. Two changed in settlement and the change matters:

- **D-04** was redefined from "product thesis" to "phase-one deliverable", because the
  original wording let a provisional board stand in for the product vision.
- **D-05** was accepted as a *rule* (pre-register, measure the baseline, freeze) with its
  constants explicitly left open, which is now P-02.

## P-02 — the sample floor and calibration tolerance *(open)*

This is the only number in the proposal that still needs the sponsor's agreement, and
the power arithmetic changed what it should be.

| Planned n | Detectable difference at 80% power, baseline 53.3% |
| --- | --- |
| 500 | ~6.3pp |
| 2,000 | ~3.1pp |
| 5,000 | ~2.0pp |
| 14,802 (the whole corpus) | ~1.1pp |

**Recommendation:** n ≥ 5,000 for any claim of edge; n ≈ 2,000 accepted only as
*inconclusive and underpowered*, never as evidence that an edge does not exist; the
calibration tolerance stays at ±3pp because it is a practical bound rather than a
statistical one, and it should be reported alongside the reliability curve rather than
instead of it.

**Why the change:** the register proposed n ≥ 2,000 as a floor. At that size the test
can only see a 3.1-point edge, which is implausibly large for the signals this project
would build, so a null at 2,000 would be uninformative while looking decisive. That is
the failure mode the repository exists to prevent.

**Decision needed:** accept the 5,000 floor, or set another number with a stated reason.

## P-03 — publishing derived data *(open, legal)*

If any derived dataset, model output or board is published beyond internal research, the
reuse terms of the source need a proper review rather than the reading recorded in
`PROPOSAL.md` §3. Not urgent, and flagged now so it is not discovered late.
