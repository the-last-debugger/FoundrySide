# Proposals

Open questions awaiting a sponsor decision. Settled items move to `DECISIONS.md`.

## P-01 — the settlement register (D-04 … D-13) — **settled 2026-11-03**

All ten items were answered in the sponsor's response of 2026-11-03T12:23:48Z and are
recorded in `DECISIONS.md`. Two changed in settlement and the change matters:

- **D-04** was redefined from "product thesis" to "phase-one deliverable", because the
  original wording let a provisional board stand in for the product vision.
- **D-05** was accepted as a *rule* (pre-register, measure the baseline, freeze) with its
  constants explicitly left open, which is now P-02.

## P-02 — the first experiment's protocol and pilot sizing *(open)*

**Superseded, kept visible:** the earlier wording here recommended a universal floor of
n ≥ 5,000 on the strength of a one-sample accuracy calculation. Both parts were wrong.
The design is paired, and the primary metric is log loss, not accuracy. That
recommendation is withdrawn rather than deleted, because the mistake is part of the
record.

**What is now open** is the protocol itself, in `docs/EVALUATION_PROTOCOL.md`:

1. Accept over/under 2.5 as the first market, on the measured coverage (14,737 Pinnacle
   closing prices, 99.6%).
2. Accept the de-vigged closing price as benchmark and **log loss as the primary metric**,
   with accuracy demoted to descriptive.
3. Accept the 0.01-nat target — 1.5% relative to the market's 0.6706, the same order as
   the book's 3.1% margin.
4. Accept **pilot-based, dependence-aware sizing** rather than a fixed n or a single
   threshold. The confirmatory slice (5,794 fixtures) reaches 80% power at 0.01 nats only
   while SD(Δ) ≲ 0.27 **at D = 1**, falling to 0.19 at D = 2 — so the pilot measures both
   the within-fixture spread and the between-division-season variance, per protocol §5.
   No number here stands on its own.

**Decision needed:** items 1–4, or a stated alternative. Nothing is scored until the
freeze record in protocol §8 is complete.

## P-03 — publishing derived data *(open, legal)*

If any derived dataset, model output or board is published beyond internal research, the
reuse terms of the source need a proper review rather than the reading recorded in
`PROPOSAL.md` §3. Not urgent, and flagged now so it is not discovered late.
