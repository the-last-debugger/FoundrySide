# Review Queue

One row per reviewable change. The builder sets `draft` or `ready_for_review`;
only oversight writes `changes_requested` or `accepted`, and only with a `review`
entry in `THREAD.md` naming the row and the same revision.

| ID | Change | Ref | Revision | State | Evidence | Reviewer |
| --- | --- | --- | --- | --- | --- | --- |
| RQ-001 | Collaboration bridge ported from ODE/OLPRS_v2: thread, queue, decisions, proposals, note and check scripts, tests | docs/COLLAB/, scripts/collab_note.py, scripts/collab_check.py, tests/test_collab.py | - | draft | `collab_check.py` -> errors=0; `unittest discover` -> 19 tests OK | oversight |
| RQ-002 | Critique of PRE_PROPOSAL.md: eleven findings, keep/cut verdicts, prior-art mapping to OLPRS_v2 and ODE | CRITIQUE.md | - | draft | findings F1-F11 each cite the section they contradict | oversight |
| RQ-003 | Fast-settlement path: ten-decision register D-04..D-13 with recommended defaults and a same-day drafting rule | PROPOSAL_SETTLEMENT.md | - | draft | three blocking questions, one reply shape | oversight |
