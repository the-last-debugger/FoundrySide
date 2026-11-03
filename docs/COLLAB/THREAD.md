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

### 2026-11-03T11:57:06Z · builder · evidence
Bridge, critique and settlement register pushed at 883ecfa. Evidence: collab_check.py -> entries=4 rows=3 accepted=0 warnings=0 errors=0; python -m unittest discover -s tests -> Ran 19 tests in 0.179s, OK. The queue rows moved to ready_for_review against this revision.
- revision: 883ecfa
- ref: docs/COLLAB/REVIEW_QUEUE.md

### 2026-11-03T12:02:47Z · builder · research
Correction accepted, superseding F7 as first written. The sponsor challenged the provenance of the OLPRS null: OdiLeague is a virtual league, not real sport. Verified in OLPRS_v2/docs/SYSTEM_MAP_2026-10-31.md line 12 ('fixtures are simulated, not played') and ODILEAGUE_STRUCTURE.md (38 rounds per season, two minutes apart, season about 76 minutes) - roughly 600 fixtures an hour, which is why 16,831 priced fixtures exist there and will not exist here. Three consequences, now in the documents: (1) F7 retitled and rewritten - what transfers is the method and the feature-class lesson, not the domain conclusion; the null is about one operator's price on an outcome that operator may itself generate, with no sharp money, and SYSTEM_MAP records that whether the simulation is seeded is unknown and not testable from outside. (2) 0.515 is withdrawn as the bar; that number was mine, imported without a domain caveat, and it is replaced by T0, a one-day measurement of the real-league favourite baseline from closing prices. (3) The evidence rate differs by about three orders of magnitude, so one division yields about 90 fixtures in 90 days against a bar needing n >= 2000: D-06 must be a wide slice (about twenty divisions) or the horizon must be a full season. The claim 'real markets are softer because the prior came from a virtual league' is explicitly rejected in the same section - real closing lines aggregate informed money, and the honest difference is latency, coverage and correlation, not realism.
- revision: 01035b0
- ref: CRITIQUE.md
