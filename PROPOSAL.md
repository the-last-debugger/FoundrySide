# FoundrySide — Formal Research-Phase Proposal

**Status:** draft for sponsor review. Authorises research only. No application, product
schema, deployment or public service is proposed here, and none is authorised by the
sponsor's response of 2026-11-03.

**Basis:** `PRE_PROPOSAL.md` (vision), `CRITIQUE.md` (what it got wrong), the sponsor's
settled directions of 2026-11-03 (D-04…D-13), and the first measured results in
`research/RESULTS_T0_T1_T3.md`. This document is expected to be revised as T2 and later
tests report; it is not waiting for them.

---

## 1. What this phase is for

Phase one does not test whether FoundrySide can beat a betting market. It tests whether
the **instrument** needed to answer that question can be built and trusted:

1. can lawful, affordable data be obtained, and at what coverage;
2. can a baseline be measured with an interval, on real closing prices;
3. can a prediction be frozen before the event and scored after it, without leakage;
4. can a claim survive correction across the number of tests actually run.

If any of those fail, no version of the ambition is testable, and the phase stops
without the ambition being revised. That distinction is the point of the three-tier
scope in `PROPOSAL_SETTLEMENT.md` §0.

## 2. Scope

**In scope**

- A reproducible research harness: data acquisition, manifest, as-of joins, frozen
  prediction records, scoring, calibration and correction.
- Football, 1X2 first; over/under 2.5 and BTTS as secondary markets once T2 is designed.
- Two evaluation tracks: **A** price-beating against a market baseline, **B** decision
  support (calibration, abstention, explanation) — measured separately, never merged.
- Desk research: information-latency hypotheses, coverage/margin gradients across
  divisions, accumulator dependence, jackpot feasibility, prior art.
- A bounded exploration stream (≤20% of research effort) for ideas outside the current
  thesis, reported as exploratory and never counted as confirmatory.

**Out of scope**

- Production application, permanent product schema, deployment, public interface.
- Accounts, third-party contact, spending, real-money execution, public claims.
- Multi-sport measurement (desk research only), accumulators as a product, jackpots as
  a product.
- League-level claims from a single season; any claim from n below the floor in §4.

## 3. Data and legal position (T1, measured)

| Property | Measured |
| --- | --- |
| Source | football-data.co.uk division files, `mmz4281/<season>/<league>.csv` |
| Files | 40 (8 divisions × 5 seasons, 2020-09-12 → 2025-05-25) |
| Fixtures | 14,802 |
| With complete closing 1X2 | 14,802 (**100%**) |
| Price source actually used | Pinnacle closing (`PSC`) for 14,799; Bet365 closing for 3 |
| Provenance | `research/data_manifest.csv` — SHA-256 per file, URL, retrieval time |

**Legal position, stated precisely:** the files are published for reuse with
attribution; that was read, not negotiated, and it is **not** a legal opinion. No
account was created, no terms accepted on the sponsor's behalf, nothing redistributed.
Any use beyond internal research — publication of derived datasets, a public product —
needs a proper review, and that is a sponsor decision, flagged rather than assumed.

**Coverage-versus-generalisation trade-off (the sponsor asked for this explicitly).**
Eight top-division European leagues give high coverage and a homogeneous modelling
problem; they also give a pooled baseline that hides real dispersion — favourite
accuracy ranges from **47.5% (E1)** to **56.4% (N1)**, an 8.9-point spread. Pooling is
therefore legitimate for measuring the *instrument*, and illegitimate for claiming a
*model works*. The proposal keeps pooled measurement and forbids pooled claims.

## 4. Evaluation rules

**Baselines, all measured on the same fixtures (T0).**

| Policy | n | Accuracy |
| --- | --- | --- |
| Favourite by closing price | 14,802 | **53.3%** (95% CI 52.5–54.1) |
| Home always | 14,802 | 43.0% |
| Draw always | 14,802 | 25.2% |
| Uniform random | 14,802 | 33.3% |

Mean 1X2 overround: **2.8%**. The OLPRS figure of 51.5% is withdrawn: it came from a
virtual league and is *lower* than the real baseline, so importing it would have set a
bar that is too easy.

**The bar is a rule, pre-registered before any engine is scored** (D-05):

```
bar_A = baseline_T0 + delta,   delta = smallest effect the planned n resolves at 80% power
```

with calibration within ±3pp, and survival under Benjamini-Hochberg across the declared
family of engine ids. `delta` is computed from the measured baseline, not chosen.

**Power and sample size — the arithmetic the sponsor asked for.** Using
`delta = (1.96 + 0.84) · sqrt(p(1−p)/n)` at p = 0.533:

| Planned n | Detectable difference at 80% power | Reading |
| --- | --- | --- |
| 500 | ~6.3pp | useless: only the most absurd edge is visible |
| 2,000 | ~3.1pp | the minimum defensible floor, and still a large edge |
| 5,000 | ~2.0pp | the smallest sample where a plausible edge is detectable |
| 14,802 (all data) | ~1.1pp | enough for the instrument; not enough per league |

**This changes the bar.** n ≥ 2,000 was proposed as a floor; on this arithmetic it can
only detect a 3.1-point edge, which is far larger than anything a form or lineup signal
would plausibly produce. The defensible protocol is therefore **n ≥ 5,000 for any claim
of edge**, with n ≥ 2,000 accepted only as "inconclusive, underpowered" — and a null at
2,000 must never be reported as evidence that no edge exists. The exact floor is the one
number in this proposal that needs the sponsor's agreement (see §7).

**Multiple testing.** Family size is declared with the pre-registration: the number of
engine ids that will be scored, before scoring. BH at FDR 0.05 across that family. A
sub-family reported afterwards is exploratory and labelled as such.

**Calibration.** Reliability curve plus Brier score; a model is not described as
calibrated on the basis of aggregate accuracy. Bin counts are reported so that a
thin-bin artefact is visible.

## 5. What has already been learned (T3, measured)

§6 of the pre-proposal asserted that same-match legs are correlated. Measured on the
same 14,802 fixtures:

| Measure | Value |
| --- | --- |
| P(BTTS) | 53.1% |
| P(over 2.5) | 51.8% |
| Product of marginals | 27.5% |
| Realised joint | **40.9%** (95% CI 40.1–41.7) |
| Ratio, realised ÷ product | **1.49×** (1.46–1.52) |
| P(over 2.5 given BTTS) | 77.0% |

Multiplying those two marginals understates the joint by **13.4 percentage points** —
a 49% relative error — and it does so in every one of the eight divisions (ratios
1.32×–1.63×). The pre-proposal's instinct was right and the magnitude is now known.
This is the cheapest decided question in the project, and it is decided.

## 6. Deliverables

| # | Deliverable | State |
| --- | --- | --- |
| D1 | Data manifest + retrieval script, reproducible offline | **done** (`research/data_manifest.csv`) |
| D2 | Baseline and dependence analysis with intervals | **done** (`research/RESULTS_T0_T1_T3.md`) |
| D3 | Evaluation protocol: power, correction family, calibration bins | this document §4, awaiting D-05 agreement |
| D4 | T2 design: one market, one engine, pre-registered kill condition | next |
| D5 | Jackpot feasibility note: are structures and results publicly available | bounded, ≤1 day |
| D6 | Research log: every test, its cost, and its negative results | continuous |

## 7. Gates, and what stops

| Gate | Question | Pass | Stop |
| --- | --- | --- | --- |
| **G1** *(met)* | Can lawful data and a real baseline be obtained? | 14,802 fixtures, 100% closing prices, baseline with interval | Already passed — the failure mode this gate existed for did not occur |
| **G2** | Can a pre-registered engine beat `bar_A` at matched coverage on data it never saw? | Edge above `delta`, calibration within ±3pp, survives BH | Two pre-registered attempts with no edge: the price-beating track stops, the record says so, the board track stands alone |
| **G3** | Is the instrument portable and affordable? | Second market set measured at ≤ KSh 0 marginal cost | Cost per resolved prediction above ceiling |
| **G4** | Does the ladder's next rung earn its cost? | Evidence per the §0 ladder, not enthusiasm | Defer; rung stays queued, not abandoned |

**Immediate blocker for the sponsor (one decision):** the sample floor. §4 recommends
**n ≥ 5,000** for a claim of edge and treats n ≈ 2,000 as inconclusive-only. That is a
change from the 2,000 in the register, it is justified by the power arithmetic, and it
is the sponsor's to accept or reject.

## 8. Cost ceiling

KSh 0 recurring. No paid API, no hosting, no cloud, no account. Compute is local and
already available. Inference is metered per task and reported, with no spend without
prior approval. Data volume is ~6.7 MB for the full five-season, eight-division corpus,
so storage is not a constraint at any scale this phase will reach.

## 9. Honest limits of this proposal

- It measures an instrument on data that is already public, which is exactly the data a
  market has already priced. Nothing here demonstrates an edge, and T2 may not find one.
- Eight European top divisions are the *easiest* coverage case. A finding there may not
  transfer to the leagues where an edge is more plausible (thin markets, lower divisions).
- Track B has no measurement design yet. It is named so it is not forgotten, not because
  it is ready.
- The dependence result bounds multiplication; it says nothing about whether the
  bookmakers price combinations fairly, which is a separate question and not yet asked.
