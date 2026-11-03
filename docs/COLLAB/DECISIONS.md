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
