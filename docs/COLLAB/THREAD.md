# Thread

Append-only chronological log for the builder, sponsor and oversight. New entries
are appended by `scripts/collab_note.py`; existing entries are never edited.

---

### 2026-11-03T11:51:00Z · builder · note
Repository cloned; the only content was `PRE_PROPOSAL.md` (39,448 bytes, one commit
`3747f9e` "Add FoundrySide comprehensive pre-proposal"). Working copy now matches
`origin/main` at `C:\dev\FoundrySide`.
- ref: PRE_PROPOSAL.md

### 2026-11-03T11:52:00Z · builder · note
Collaboration bridge created, ported from ODE and OLPRS_v2 with the format
unchanged. Files: `docs/COLLAB/` (README, THREAD, REVIEW_QUEUE, DECISIONS,
PROPOSALS), `scripts/collab_note.py`, `scripts/collab_check.py`, `tests/test_collab.py`.
The append-only rule is enforced from this first commit rather than grandfathered:
this repository has no pre-checker history to excuse.
- ref: docs/COLLAB/README.md

### 2026-11-03T11:54:00Z · builder · research
CRITIQUE recorded against the pre-proposal: eleven findings, of which four are
structural (no falsifier; a thirteen-report waterfall standing in for a proposal;
prior results in OLPRS_v2 not cited; no cost unit), and one is decisive — the
central research question in §4 has already been answered on 10,329 signals by the
sponsor's own system, at zero edge and negative user advantage. The document is
good on intent and silent on the two questions that decide feasibility: what result
would stop the project, and why the edge would still be there for us.
- ref: CRITIQUE.md

### 2026-11-03T11:56:00Z · builder · blocker
The proposal is blocked on three sponsor answers, not on thirteen reports.
`PROPOSAL_SETTLEMENT.md` turns them into a register of ten decisions (`D-04`–`D-13`),
each with a recommended default, so "accept all defaults" is a complete and
sufficient reply and the proposal can be drafted the same day. Questions:
(1) is the product a market-restatement board with abstention discipline, or an
independent model that must beat a market baseline at matched coverage;
(2) what is the numeric bar, in the same units OLPRS already measured;
(3) what is explicitly out of scope for the first 90 days — accumulator and jackpot
research, real-money execution, autonomy claims.
Nothing in PRE_PROPOSAL.md authorises implementation, so no build work starts until
a proposal exists. This entry is the blocker: it needs a sponsor decision, not a
plan from the builder.
- ref: PROPOSAL_SETTLEMENT.md
