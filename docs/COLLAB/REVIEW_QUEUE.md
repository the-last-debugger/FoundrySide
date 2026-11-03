# Review Queue

One row per reviewable change. The builder sets `draft` or `ready_for_review`;
only oversight writes `changes_requested` or `accepted`, and only with a `review`
entry in `THREAD.md` naming the row and the same revision.

| ID | Change | Ref | Revision | State | Evidence | Reviewer |
| --- | --- | --- | --- | --- | --- | --- |
| RQ-001 | Collaboration bridge ported from ODE/OLPRS_v2: thread, queue, decisions, proposals, note and check scripts, tests | docs/COLLAB/, scripts/collab_note.py, scripts/collab_check.py, tests/test_collab.py | 0e05653 | ready_for_review | `collab_check.py` -> errors=0; `unittest discover` -> 19 tests OK | oversight |
| RQ-002 | Critique of PRE_PROPOSAL.md: eleven findings, keep/cut verdicts, prior-art mapping to OLPRS_v2 and ODE | CRITIQUE.md | 0e05653 | ready_for_review | findings F1-F11 each cite the section they contradict | oversight |
| RQ-003 | Fast-settlement path: ten-decision register D-04..D-13 with recommended defaults and a same-day drafting rule | PROPOSAL_SETTLEMENT.md | 0e05653 | ready_for_review | three blocking questions, one reply shape | oversight |
| RQ-004 | Correction to F7 and D-05 after the sponsor challenge: OLPRS is a virtual league, so the prior is narrower and 0.515 is not a transferable bar; T0 added to measure the real baseline | CRITIQUE.md, PROPOSAL_SETTLEMENT.md | 0e05653 | ready_for_review | OdiLeague confirmed simulated at OLPRS_v2/docs/SYSTEM_MAP_2026-10-31.md line 12; ODILEAGUE_STRUCTURE.md for cadence | oversight |
| RQ-005 | Fail-closed header parsing: an entry-looking line that does not match the grammar is now an error, not body text of the previous entry; the sponsor placeholder entry is acknowledged as a visible warning | scripts/collab_note.py, scripts/collab_check.py, tests/test_collab.py | 0e05653 | ready_for_review | 17 new tests pass (23 total, OK); collab_check.py -> entries=6 rows=4 warnings=1 errors=0, the warning naming the acknowledged header | oversight |
| RQ-006 | Formal research-phase proposal: scope, data position, evaluation rules with power arithmetic, deliverables and gates | PROPOSAL.md | eb0844d | ready_for_review | one open blocker, P-02 sample floor; everything else settled by the sponsor response of 2026-11-03 | oversight |
| RQ-007 | T0/T1/T3 measured on real data: 40 files, 5 seasons, 8 divisions, 14,802 fixtures | research/RESULTS_T0_T1_T3.md, research/analyse.py, research/data_manifest.csv | eb0844d | ready_for_review | favourite 53.3 percent (95 CI 52.5-54.1); overround 2.8 percent; dependence ratio 1.49 (1.46-1.52); 100 percent closing-price coverage; sha256 manifest | oversight |
