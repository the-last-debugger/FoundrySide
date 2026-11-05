# Decisions

Accepted decisions only. A decision is here when the sponsor has settled it; open
questions and suggested defaults live in `PROPOSALS.md`. Each entry records the
authority it rests on, so a decision cannot later be remembered as stronger than it
was.

## D-01

**Decision:** FoundrySide is not authorised to implement. The project remains in the
research and planning phase until a formal proposal is reviewed and approved.

**Status:** accepted
**Authority:** `PRE_PROPOSAL.md` header ("Implementation status: Not authorised") and §22 Stage 6.
**Consequence for the builder:** no application code, no schema, no deployment. Documents,
harnesses and measurements only. Amended by D-10, which authorises research code.

## D-02

**Decision:** Real-money betting execution is out of scope. It is not deferred v1
work; it would require a separate legal and licensing assessment before it is even
a candidate.

**Status:** accepted
**Authority:** `PRE_PROPOSAL.md` §12 and §17; reaffirmed by the sponsor 2026-11-03 (D-12).

## D-03

**Decision:** Practical availability from Kenya is a first-class constraint on every
candidate data source and provider, not a later filter.

**Status:** accepted
**Authority:** `PRE_PROPOSAL.md` §10, §12, §14; reaffirmed 2026-11-03 (D-08).

## D-04

**Decision:** The phase-one deliverable is the measurement instrument plus a provisional
market-view board. It is not the product definition. Both evaluation tracks stay alive:
A (price-beating at matched coverage) and B (calibration, abstention, explanation,
decision support).

**Status:** accepted
**Authority:** sponsor response 2026-11-03T12:23:48Z, item 1.

## D-05

**Decision:** The evaluation rule is pre-registered before any engine is scored, and the
baseline is measured, not imported. The OLPRS virtual-league figure of 0.515 is not used.
The specific sample floor and calibration tolerance are **not yet agreed** — a protocol
with power and sample-size reasoning is required first, then frozen. See `PROPOSAL.md` §4
and `PROPOSALS.md` P-02.

**Status:** accepted (rule) / open (constants)
**Authority:** sponsor response 2026-11-03T12:23:48Z, item 2.

## D-06

**Decision:** Football is the first calibration domain; 1X2, O/U 2.5 and BTTS are
candidate initial markets. No commitment to a fixed division count, and no league-level
generalisation claims. T0/T1 determine a feasible, lawful competition set, reporting the
coverage-versus-generalisation trade-off.

**Status:** accepted
**Authority:** sponsor response 2026-11-03T12:23:48Z, item 3. Measured in
`research/RESULTS_T0_T1_T3.md`.

## D-07

**Decision:** Accumulators and jackpots are deferred as product and engineering scope,
but not prohibited as research. The dependence measurement (T3) and a bounded jackpot
feasibility check proceed.

**Status:** accepted
**Authority:** sponsor response 2026-11-03T12:23:48Z, item 4.
**Evidence:** T3 complete — realised joint 40.9% (95% CI 40.1–41.7) against a product of
marginals of 27.5%, **ratio 1.49× (bootstrap 95% CI 1.47–1.51)**, consistent across all
eight divisions (1.32×–1.63×).

**Superseded figure, kept visible:** an earlier version of this entry quoted 1.46–1.52 as
the ratio interval. That interval was wrong as a method — it divided the Wilson limits of
the joint rate by a fixed product of marginals, treating both as known constants — and is
replaced by the bootstrap interval. The earlier figure is recorded here rather than
deleted, because a decision that cited an invalid interval should show that it did.

**Scope limit, as the sponsor recorded it:** this measures outcome dependence, not
bookmaker accumulator pricing. It bounds what multiplication can do; it says nothing about
whether a combination is fairly priced.

## D-08

**Decision:** Free, published and legally usable sources first. Target KSh 0 recurring;
no paid API, hosting or inference without the sponsor's explicit approval. Source terms,
Kenya accessibility, coverage, historical depth and closing-price availability are
checked before any automation.

**Status:** accepted
**Authority:** sponsor response 2026-11-03T12:23:48Z, item 5.
**Evidence:** T1 satisfied on football-data.co.uk — 40 files, 14,802 fixtures, 100%
closing 1X2, sha256 manifest. Legal position is a reading of published terms, not an
opinion.

## D-09

**Decision:** Local-first and resource-efficient by default. No cloud deployment or paid
service is authorised.

**Status:** accepted
**Authority:** sponsor response 2026-11-03T12:23:48Z, item 6.

## D-10

**Decision:** The builder is authorised to run agreed research independently: desk
investigations, data-access checks, reproducible offline or limited-scope experiments,
and research scripts. It may choose sensible next tests and must preserve raw evidence,
timestamps, source provenance, frozen predictions, experiment definitions, costs and
negative results. No account creation, third-party contact, spending, public claims or
real-money execution without separate approval.

**Status:** accepted
**Authority:** sponsor response 2026-11-03T12:23:48Z, item 7.

## D-11

**Decision:** The interface decision is deferred. CLI or local dashboard may be evaluated
as options but must not drive the research or become application development.

**Status:** accepted
**Authority:** sponsor response 2026-11-03T12:23:48Z, item 8.

## D-12

**Decision:** Research-only framing. No promises or return targets, no encouragement to
chase losses, no real-money execution. Kenya legal and licensing questions are recorded
before any public-facing launch is proposed.

**Status:** accepted
**Authority:** sponsor response 2026-11-03T12:23:48Z, item 9.

## D-13

**Decision:** Staged decision gates, with 30/60/90 days treated as planning checkpoints
rather than deadlines that override evidence. Each test states its question, method, data
requirements, cost, pass/fail/inconclusive outcome, and the decision that follows.

**Status:** accepted
**Authority:** sponsor response 2026-11-03T12:23:48Z, item 10. Operationalised in
`PROPOSAL.md` §7.


## D-14

**Decision:** The builder has standing authority to pursue useful, reversible, zero-cost research proactively and in parallel, including exploratory research into sports superstitions and unconventional hypotheses, additional lawful public data, alternative features, model families, parameter/weight estimation, calibration, residual analysis and validation improvements. The builder may choose and sequence the next experiments without waiting for routine sponsor approval. Pilot data and properly separated exploratory samples may be used; the frozen confirmatory slice, evaluation protocol and primary comparator remain protected unless separately authorised.

**Status:** **superseded by D-15** (the parallel-authority clause only; its protections remain)
**Authority:** sponsor direction 2026-11-04T04:27:00Z in docs/COLLAB/THREAD.md.
**Limits:** Research-only; KSh 0; no paid services, account creation, third-party contact, cloud commitments, public claims, application development or real-money execution. Any proposal crossing one of those boundaries, or changing the confirmatory protocol/slice, must be brought to the sponsor first. Superstition-related ideas are hypotheses to operationalise and test, not assumed effects or causal explanations.

## D-15

**Decision:** The standing authority for parallel, self-sequenced research granted in D-14 is withdrawn.
Execution is narrow and sequential: one active task at a time, chosen from an explicitly authorised
scope, with new experiments requiring sponsor approval of that scope. Everything D-14 protects — the
frozen confirmatory slice, the evaluation protocol and the primary comparator — stays protected.

**Status:** superseded for the 2026-11-05 autonomy window by D-16; otherwise retained as the standing rule
outside that time-boxed window.
**Authority:** sponsor direction on work-in-progress control and the subsequent authorised scopes,
including the 2026-11-05 instruction not to run the market-companion assessment concurrently.
**Limits (standing, outside D-16):** Research-only; KSh 0; no paid services, account creation, third-party
contact, cloud commitments, public claims, redistribution, product work or real-money functionality.


## D-16

**Decision:** Time-boxed builder autonomy for 2026-11-05. DeepSeek may independently choose, sequence,
research, design, implement and test a coherent local/demo product within the established FoundrySide
direction. Routine reversible choices do not require sponsor approval. The sponsor's role during this
window is progress review and error identification, not routine product steering.

**Public data permission:** Freely and lawfully accessible public datasets, pages, documentation,
repositories and unauthenticated APIs may be accessed and used without asking first, provided no payment,
new account, credentials, provider contact or acceptance of new contractual terms is required. Respect
source terms, licences, access controls and rate limits; do not bypass restrictions or collect
personal/sensitive data. Record provenance and do not redistribute material without permission. This
supersedes the day-pass's earlier blanket ban on new external data acquisition.

**Parallel work permission:** Independent, non-conflicting exploratory research, implementation and
testing workstreams may proceed in parallel. The former one-active-empirical-task limit is relaxed for
such work, provided reproducibility, data separation and research integrity are preserved.

**Protected boundaries:** P-02 and its 5,794-fixture confirmatory slice remain untouched. The amended
dispersion study still requires its separate fresh sponsor approval. No spending, paid services, new
accounts or credentials, provider contact, acceptance of new terms, cloud commitments, deployment,
external publication, commercial use, unauthorised redistribution, live bookmaker account access,
bet placement, deposits, withdrawals or real-money execution. Keep recurring cost at KSh 0.

**Duration:** This is a one-day authority for 2026-11-05 only. After the end-of-day review, ordinary
sponsor review and the standing rules resume unless the sponsor renews or changes them.

**Status:** accepted.
**Authority:** sponsor day-pass direction and subsequent 2026-11-05 clarification in
`docs/COLLAB/THREAD.md`.
