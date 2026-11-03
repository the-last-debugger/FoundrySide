# Review Queue

One row per reviewable change. The builder sets `draft` or `ready_for_review`;
only oversight writes `changes_requested` or `accepted`, and only with a `review`
entry in `THREAD.md` naming the row and the same revision.

| ID | Change | Ref | Revision | State | Evidence | Reviewer |
| --- | --- | --- | --- | --- | --- | --- |
| RQ-001 | Collaboration bridge ported from ODE/OLPRS_v2: thread, queue, decisions, proposals, note and check scripts, tests | docs/COLLAB/, scripts/collab_note.py, scripts/collab_check.py, tests/test_collab.py | 01035b0 | ready_for_review | `collab_check.py` -> errors=0; `unittest discover` -> 19 tests OK | oversight |
| RQ-002 | Critique of PRE_PROPOSAL.md: eleven findings, keep/cut verdicts, prior-art mapping to OLPRS_v2 and ODE | CRITIQUE.md | 01035b0 | ready_for_review | findings F1-F11 each cite the section they contradict | oversight |
| RQ-003 | Fast-settlement path: ten-decision register D-04..D-13 with recommended defaults and a same-day drafting rule | PROPOSAL_SETTLEMENT.md | 01035b0 | ready_for_review | three blocking questions, one reply shape | oversight |
| RQ-004 | Correction to F7 and D-05 after the sponsor challenge: OLPRS is a virtual league, so the prior is narrower and 0.515 is not a transferable bar; T0 added to measure the real baseline | CRITIQUE.md, PROPOSAL_SETTLEMENT.md | 01035b0 | ready_for_review | OdiLeague confirmed simulated at OLPRS_v2/docs/SYSTEM_MAP_2026-10-31.md line 12; ODILEAGUE_STRUCTURE.md for cadence | oversight |
