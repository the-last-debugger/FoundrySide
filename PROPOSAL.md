# FoundrySide — Formal Research-Phase Proposal

**Status:** revision 2, for sponsor review. Authorises research only. No application,
product schema, deployment or public service is proposed here, and none is authorised.

**Basis:** `PRE_PROPOSAL.md` (vision), `CRITIQUE.md` (what it got wrong), the sponsor's
settled directions of 2026-11-03 (D-04…D-13), the measured results in
`research/RESULTS_T0_T1_T3.md`, the paired power analysis in `research/POWER.md`, and the
preregistration in `docs/EVALUATION_PROTOCOL.md`.

**Changes from revision 1**, in response to review: the competition mix is corrected
(E1 is the second tier, not a top division); the sample floor is replaced by a
target-effect sizing, computed on the paired design rather than a one-sample
approximation; the first market is resolved to over/under 2.5; proper scoring rules
replace accuracy as the primary metric; descriptive and inferential claims are separated;
contextual intelligence is recorded as parked.

---

## 1. What this phase is for

Phase one does not test whether FoundrySide can beat a betting market. It tests whether
the **instrument** needed to answer that question can be built and trusted:

1. can lawful, affordable data be obtained, and at what coverage;
2. can a baseline be measured with an interval, on real closing prices;
3. can a prediction be frozen before the event and scored after it, without leakage;
4. can a claim survive correction across the number of tests actually run.

If any of those fail, no version of the ambition is testable, and the phase stops without
the ambition being revised. That distinction is the point of the three-tier scope in
`PROPOSAL_SETTLEMENT.md` §0.

## 2. Scope

**In scope**

- A reproducible research harness: data acquisition, manifest, as-of joins, frozen
  prediction records, scoring, calibration and correction.
- Football. The first confirmatory market is **over/under 2.5**, on de-vigged Pinnacle
  closing prices; 1X2 and BTTS follow only after the first experiment is frozen and run.
  The reasoning is in `docs/EVALUATION_PROTOCOL.md` §1.
- Two evaluation tracks: **A** price-beating against a market benchmark, **B** decision
  support (calibration, abstention, explanation) — measured separately, never merged.
- Desk research: information-latency hypotheses, coverage/margin gradients across
  divisions, accumulator dependence, jackpot feasibility, prior art.
- A bounded exploration stream (≤20% of research effort), reported as exploratory and
  never counted as confirmatory.

**Out of scope**

- Production application, permanent product schema, deployment, public interface.
- Accounts, third-party contact, spending, real-money execution, public claims.
- Multi-sport measurement (desk research only), accumulators as a product, jackpots as a
  product.
- Contextual intelligence — lineups, news, environment, press conferences — is **parked**
  (`docs/PARKED.md`): not built now, not scored, allowed only as occasional desk notes
  tied to an active test.
- League-level or season-level claims from a single slice; any claim below the sample
  the pilot prescribes.

## 3. Data and legal position (T1, measured)

| Property | Measured |
| --- | --- |
| Source | football-data.co.uk division files, `mmz4281/<season>/<league>.csv` |
| Files | 40 (8 divisions × 5 seasons, 2020-09-12 → 2025-05-25) |
| Fixtures | 14,802 |
| With complete closing 1X2 | 14,802 (**100%**) |
| With complete closing over/under 2.5 | 14,737 Pinnacle, 14,800 Bet365 |
| Price source used for 1X2 | Pinnacle closing for 14,799; Bet365 closing for 3 |
| Provenance | `research/data_manifest.csv` — SHA-256 per file, URL, retrieval time |

**Competition mix, stated accurately.** The corpus is eight divisions: E0 (English
Premier League), SP1, D1, I1, F1, N1, P1 — seven top divisions — plus **E1, the English
Championship, which is the second tier**. Revision 1 called these "eight top-division
European leagues", which was wrong and materially so: E1 is both the largest single
contributor (2,760 fixtures, 18.6%) and the league with the lowest favourite accuracy
(47.5%), so misdescribing the mix would misdescribe the homogeneity claim as well.

**Coverage-versus-generalisation trade-off.** The mix gives high closing-price coverage
and a mostly homogeneous modelling problem, but the pooled baseline hides real
dispersion — favourite accuracy runs from 47.5% (E1) to 56.4% (N1), an 8.9-point spread.
Pooling is legitimate for measuring the *instrument* and illegitimate for claiming a
*model works*. The proposal keeps pooled measurement and forbids pooled claims.

**Legal position, stated precisely:** the files are published for reuse with attribution;
that was read, not negotiated, and it is **not** a legal opinion. No account was created,
no terms accepted on the sponsor's behalf, nothing redistributed. Publication of derived
data is P-03 and it is the sponsor's decision.

## 4. Evaluation rules

**Baselines, measured on the same fixtures (T0).**

| Policy | n | Accuracy |
| --- | --- | --- |
| Favourite by closing price | 14,802 | **53.3%** (95% CI 52.5–54.1) |
| Home always | 14,802 | 43.0% |
| Draw always | 14,802 | 25.2% |
| Uniform random | 14,802 | 33.3% |

Mean 1X2 overround 2.8%. The OLPRS figure of 51.5% stays withdrawn: it came from a virtual
league and is *lower* than the real baseline, so importing it would have set a bar that is
too easy. These accuracy figures are **descriptive**, not a success threshold.

**The benchmark for the first experiment is a probability, not a pick:** the de-vigged
Pinnacle closing probability for over/under 2.5, whose own log loss is **0.6706 nats**
(Brier 0.2390) on 14,735 fixtures, with a mean implied probability of 51.5% against an
observed 51.7%.

**The bar is a rule, pre-registered before any engine is scored** (D-05):

```
bar_A = benchmark + delta,   delta fixed before scoring, from the pilot's power analysis
```

on the primary metric (log loss for the first experiment), with calibration reported
alongside and survival under Benjamini-Hochberg across the declared family of engine ids.
`delta` is justified, not chosen; the full specification is
`docs/EVALUATION_PROTOCOL.md` §5–§7.

**Power and sample size — revised for the paired design.** Revision 1 used a one-sample
proportion approximation. That was the wrong model: the model and the market are scored
on the same fixtures, so their errors are paired, and power depends on how often they
disagree. Recalculated on the paired (McNemar) design by simulation
(`research/POWER.md`):

| Target edge | n for 80% power (analytic) | Simulated check |
| --- | --- | --- |
| 1pp | ~27,000 | 40,000 gives 92% |
| 2pp | ~6,900 | 10,000 gives 92% |
| 3pp | ~3,000 | 5,000 gives 94% |
| 5pp | ~1,100 | 2,000 gives 97% |

Two findings worth stating plainly. **Clustering barely affects this test** at 40
league-season clusters, even at ICC 0.10 — the contrast is within-fixture, so
between-cluster shifts largely cancel. The concern was reasonable; the measurement does
not support a correction at this cluster count. And **the requirement is a function of
the target edge and the disagreement rate**, so a single universal floor is the wrong
instrument: 5,000 is right for ~3pp and wrong either side of it.

The sizing that governs the first experiment is the paired log-loss power in
`docs/EVALUATION_PROTOCOL.md` §6: a pilot slice estimates the distribution of Δ, the
sample is sized from it, and only then does the confirmatory slice run.

**Multiple testing.** Family size is declared at freeze time. BH at FDR 0.05 across that
family. A sub-family reported afterwards is exploratory.

## 5. What has already been learned (T3, measured)

§6 of the pre-proposal asserted that same-match legs are correlated. Measured on the same
14,802 fixtures:

| Measure | Value |
| --- | --- |
| P(BTTS) | 53.1% |
| P(over 2.5) | 51.8% |
| Product of marginals | 27.5% |
| Realised joint | **40.9%** (95% CI 40.1–41.7) |
| Ratio, realised ÷ product | **1.49×** (bootstrap 95% CI 1.47–1.51) |
| P(over 2.5 given BTTS) | 77.0% |

Multiplying those marginals understates the joint by 13.4 percentage points — a 49%
relative error — and it does so in every one of the eight divisions (ratios 1.32×–1.63×).

**Correction:** revision 1 quoted 1.46–1.52 as the ratio's confidence interval by dividing
the Wilson limits of the joint rate by a *fixed* product of marginals. That treats both
marginals as known constants; it is not a confidence interval. The bootstrap interval is
1.47–1.51. The point estimate and the conclusion are unchanged, which is luck rather than
justification — the method was wrong.

## 6. Deliverables

| # | Deliverable | State |
| --- | --- | --- |
| D1 | Data manifest + retrieval, reproducible offline | **done** |
| D2 | Baseline and dependence analysis with intervals | **done**, interval corrected |
| D3 | Evaluation protocol: market, benchmark, scoring, power, correction family | **drafted** — `docs/EVALUATION_PROTOCOL.md`, awaiting agreement |
| D4 | Paired power analysis with clustering | **done** — `research/POWER.md` |
| D5 | First preregistration record (§8 of the protocol) and the pilot | next |
| D6 | Jackpot feasibility note | bounded, ≤1 day, not started |
| D7 | Research log: every test, its cost, its negative results | continuous |

## 7. Gates, and what stops

| Gate | Question | Pass | Stop |
| --- | --- | --- | --- |
| **G1** *(met)* | Can lawful data and a real baseline be obtained? | 14,802 fixtures, 100% closing prices, benchmark scored | Already passed |
| **G2** | Can a pre-registered engine beat the benchmark on the primary metric on unseen data? | Δ above the frozen threshold, calibration guardrail intact, survives BH | Track A stops for that market; result recorded as a null with its interval; a retry needs a new hypothesis, not a retune |
| **G3** | Is the instrument portable and affordable? | Second market measured at ≤ KSh 0 marginal cost | Cost per resolved prediction above ceiling |
| **G4** | Does the ladder's next rung earn its cost? | Evidence per the §0 ladder | Defer; rung stays queued, not abandoned |

**Immediate decisions for the sponsor (two, both in the protocol):**

1. Accept `docs/EVALUATION_PROTOCOL.md` as the basis for the first experiment — market
   (over/under 2.5), benchmark (de-vigged Pinnacle closing), primary metric (log loss),
   effect size (0.01 nats, 1.5% relative to the market's 0.6706).
2. Accept that the sample is sized from a pilot slice rather than fixed at 5,000, and
   that the pilot may not contribute to the confirmatory claim.

Neither is reversible after the freeze, which is why they are asked now rather than later.

## 8. Cost ceiling

KSh 0 recurring. No paid API, no hosting, no cloud, no account. Compute is local and
already available. Inference is metered per task and reported, with no spend without prior
approval. The full five-season, eight-division corpus is ~6.7 MB, so storage is not a
constraint at any scale this phase will reach.

## 9. Honest limits of this proposal

- It measures an instrument on data that is already public and already priced. Nothing
  here demonstrates an edge, and the first experiment may not find one.
- Seven top divisions plus one second tier is the *easiest* coverage case. A finding there
  may not transfer to the thin markets where an edge is more plausible.
- Track B has no measurement design yet. It is named so it is not forgotten, not because
  it is ready.
- The dependence result bounds multiplication; it says nothing about whether bookmakers
  price combinations fairly, which is a separate question and not yet asked.
- The 0.01-nat target is a judgement. It is argued in the protocol, and the pilot may show
  it is unachievable at any affordable sample — which would itself be a finding.
