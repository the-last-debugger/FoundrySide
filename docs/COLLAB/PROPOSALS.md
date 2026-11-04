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

## P-03 — source use and publication *(open, legal)*

The earlier wording treated source use as one question. It is three, and they have different answers.

### (a) This project's own use so far — one-off, internal, non-commercial

Transient reads and internal analysis for a research exercise, no redistribution, no hosted service,
no commercial use. The provider offers its CSV/Excel files free for personal and academic analysis.
**This is the category every analysis in this repository falls into**, including the E24 thin-division
measurement, which read files into memory and retained nothing.

### (b) Recurring automated collection or model training

A different question. Automated collection at scale, or training models for distribution, is not
covered by a personal-use reading and would need the provider's terms examined properly.

**The provider's stated policy, as reported by the sponsor and not independently located here:**
free access is intended for private individuals' personal betting and/or academic research, via
manual download or at most light automated download (twice weekly), and is distinguished from
commercial and heavy automated data-training use. My own checks could not find that text: `terms.php`
and `terms.txt` return 404, and `disclaimer.php`, `data.php` and `notes.txt` contain liability and
column documentation but no reuse policy. The site footer does assert "© Football-Data. Liability
Disclaimer. All Rights Reserved."

So the position is: the *policy as described* supports (a); it does not obviously support (b); and it
was not verified from the source in this session.

### (c) Public distribution, hosted service or commercialisation

Not established. The footer's "All Rights Reserved" is contrary to redistribution, and no licence
grants it. Any publication of derived data stays blocked until either the provider's terms are
reviewed properly or a qualified legal opinion is obtained.

### The Kenyan research/private-use exception

Kenyan copyright law provides fair-dealing-style exceptions for research and private use, which may
support category (a) with source acknowledgement. It is **not** a blanket licence, it is not a legal
opinion, and it does not reach (b) or (c). Recorded because the sponsor asked for it to be considered
explicitly, not as a conclusion.

### What this changes in practice

Nothing about the current restrictions: no redistribution, no public claims, no hosted service, no
commercial use. What it changes is the framing — a one-off internal research read is a materially
different act from a standing automated pipeline, and the document now says so instead of treating use
as automatically blocked.

