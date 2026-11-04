# Confirmatory readiness — the P-02 decision, prepared

**Nothing here scores the confirmatory slice.** No confirmatory fixture has been touched, no model
has been tuned against it, and no freeze has been declared. This document exists so the P-02
decision can be taken on current evidence rather than on the state of knowledge when P-02 was
written.

## The four P-02 items, with what is now known

| # | Item as written | Status now | Recommendation |
| --- | --- | --- | --- |
| 1 | Over/under 2.5 as the first market, on 99.6% coverage | Unchanged and still correct — 14,737 closing prices | **Accept** |
| 2 | De-vigged closing price as benchmark, log loss primary, accuracy descriptive | Unchanged; the corpus has since confirmed the benchmark at 0.6742 log loss on the pilot slice | **Accept** |
| 3 | The 0.01-nat target (1.5% relative to the market) | Unchanged; the margin is 2.9–3.5%, so the target remains the same order of magnitude as the cost of trading | **Accept** |
| 4 | Pilot-based, dependence-aware sizing | Superseded by measurement: power is **70.5%** at the calibrated cutoff with the current model's spread, and the 80% crossing sits at **0.0116–0.0130 nats** | **Accept the method, but see the problem below** |

## The problem the evidence now creates

P-02 assumed the open question was *how large a sample is needed to detect the effect*. The
experiments since then answered a different question: **is there an effect to detect?**

The pilot model trails the market by 0.0246 nats. Out-of-fold recalibration recovers about half,
leaving roughly 0.012 — around the 80% crossing, but with the model still behind after calibration.
Nothing in fourteen experiments found information the price lacks. So a confirmatory test of this
model would not discover whether it beats the market; it would **document that it does not**, at a
cost of the confirmatory slice.

That is a legitimate thing to do — a formal, pre-registered negative result has value — but it is a
different purchase from the one P-02 contemplated, and it should be bought deliberately.

## Three options, costed honestly

| Option | What it produces | What it costs | What it forecloses |
| --- | --- | --- | --- |
| **A. Freeze and run as designed** | A definitive pre-registered measurement of the current model's deficit, with cluster-robust inference | The confirmatory slice, once | Cannot reuse the slice for a better model later |
| **B. Freeze and hold** | The design, verified and ready; the slice untouched | Nothing now | Nothing; delay only |
| **C. Redefine the target** | A test of a candidate that has a mechanism (needs new data) | A data decision | The current model never gets a formal verdict |

**My recommendation is B, with A available the moment the sponsor wants a published negative.** The
confirmatory slice is a non-renewable resource: 5,794 fixtures, and the only unbiased test this
project has. Spending it on a model that the pilot already shows is worse than the benchmark buys a
formal statement we can already make from pilot evidence, with a caveat, and gives up the chance to
test something better.

If the sponsor wants the formal negative for its own sake — a defensible position, since "we tested
it properly and it lost" is a stronger claim than "we think it would lose" — then A is one freeze
commit away and the sizing already supports it.

## What a freeze would require

Protocol §8 lists the freeze record. What remains incomplete:

1. **Commit the frozen protocol text** with a hash, and record the hash here.
2. **Freeze the model specification**: the exact parameters, shrinkage, update order and cutoff
   rule, as code and as a written description that cannot drift.
3. **Freeze the prediction file** before any confirmatory outcome is read — generate predictions,
   hash them, commit the hash.
4. **Declare the decision rule** in advance: the 0.01-nat target, the cluster-robust test, the
   one-sided direction and the multiplicity family (one market, one metric, one test).

Items 1 and 4 are writing; items 2 and 3 are mechanical and could be produced in a single block.

## What has not changed

- The market comparator: de-vigged closing price, unchanged.
- The primary metric: log loss, unchanged.
- The target: 0.01 nats, unchanged.
- The confirmatory slice: untouched, unscored, unexamined.

## What this document is not

It is not a freeze, not a scoring run and not a recommendation to spend the slice. It is the
decision, prepared so it can be taken in one sitting rather than rediscovered.
