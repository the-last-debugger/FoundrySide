# Proposals

Open questions and suggested defaults awaiting a sponsor decision. Nothing here is
decided; decided items move to `DECISIONS.md`. The rationale, the alternatives and
the evidence for each of the ten items below are in `PROPOSAL_SETTLEMENT.md`, which
is the document to read before answering.

**Status: under review.** The sponsor's response of 2026-11-03 declines to accept
D-04–D-13 wholesale and declines to fix D-05 before T0. D-04 and D-06 were revised in
answer and remain proposals; `PROPOSAL_SETTLEMENT.md` §0 now separates the project's
ambition from the phase-one constraints, and the expansion ladder records what would
earn each wider scope rather than assuming it away.

## Proposal P-01 — the settlement register (D-04 … D-13)

Three questions block the proposal: what the product is, what the numeric bar is,
and what is out of scope for the first ninety days. Everything else in
`PRE_PROPOSAL.md` is either downstream of those three or cheap to reverse later.
The register expresses the three as ten answerable items, each with a recommended
default, so "accept all defaults" is a complete reply.

| Decision | Question | Recommended default | Cost to reverse |
| --- | --- | --- | --- |
| D-04 | Phase-one deliverable, not the product: instrument plus a provisional board; product vision left open to G3 | Instrument and a provisional market-view board; ambition unchanged | Low — a positioning statement, no code |
| D-05 | The bar: rule now, number after T0 | Pre-registered rule — measured baseline + delta at 80% power, n >= 2,000, calibrated within ±3pp, BH-corrected | High once published — this is the one decision that is expensive to change later |
| D-06 | First slice: sport, markets, competitions | Football; 1X2, O/U 2.5, BTTS; leagues with reliable closing prices only | Medium — collection and schema choices |
| D-07 | Accumulators and jackpots in v1 | Out of scope until a single-selection edge exists (gate G2) | Low now, high after build |
| D-08 | Data: sources, budget, terms | Free-tier and published sources only; KSh 0 for phase 1; every source ToS-checked before collection | Low |
| D-09 | Infrastructure | Local-first, SQLite, one machine; no cloud until an unattended job is proven necessary | Low |
| D-10 | Autonomy boundary | Unattended collection and scoring allowed; no accounts, no spending, no third-party contact without a decision | Medium — it is a policy others will rely on |
| D-11 | Interface | CLI plus a local dashboard; no mobile, no public web | Low |
| D-12 | Legal and responsible-gambling posture | Research-only framing, no return targets in user-facing copy, BCLB position documented before any public launch | Low |
| D-13 | Timeline and gates | 30/60/90-day gates with pre-registered kill conditions; stop on G1 failure | Medium |

**Why this is fast:** the proposal does not need the thirteen reports in
`PRE_PROPOSAL.md` §21. It needs three numbers — the bar, the coverage cost of
getting there, and the cost per experiment — and three scope decisions. The reports
become de-risking after the proposal is drafted, not a gate in front of it.
