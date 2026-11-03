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
harnesses and measurements only. This is the constraint the whole repository is shaped by.

## D-02

**Decision:** Real-money betting execution is out of scope. It is not deferred v1
work; it would require a separate legal and licensing assessment before it is even
a candidate.

**Status:** accepted
**Authority:** `PRE_PROPOSAL.md` §12 ("initially concentrate on research, data collection and
simulated evaluation") and §17 ("Real-money execution is outside the initial research scope").

## D-03

**Decision:** Practical availability from Kenya is a first-class constraint on every
candidate data source and provider, not a later filter.

**Status:** accepted
**Authority:** `PRE_PROPOSAL.md` §10 (source evaluation includes "Availability from Kenya"),
§12 and §14 (the KSh 0–200 recurring-cost ceiling).
