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


### 2026-11-03T12:XX:00Z · sponsor · response

Thank you for the independent critique and, especially, for correcting the OLPRS comparison.

I agree that the OdiLeague result must not be treated as a conclusion about real-world sporting markets. The distinction is material: the transferable evidence is the evaluation methodology and the lessons about feature testing and correction, not the virtual league's measured outcome or its favourite baseline. Withdrawing the imported 0.515 threshold and replacing it with a measured real-market baseline is the right correction. Please preserve that distinction consistently in all subsequent research and proposal material.

I also agree with the broader discipline behind the settlement register: define falsifiable tests, measure the real-market baseline, establish lawful and affordable data access, and avoid building ahead of evidence. The proposed tests are useful ways to turn uncertainty into concrete work.

However, I want to clarify one important point before treating the proposed first slice as a settled description of FoundrySide.

The long-term ambition remains an autonomous, multi-sport sports-intelligence research laboratory. Football may be the most practical first experimental domain, and a small set of well-supported markets may be the right place to begin measurement. That does not mean the overall project should become football-only, that other sports and markets are no longer part of the research ambition, or that the market-restatement board is now the final product vision.

Please clarify whether D-04 and D-06 are intended strictly as pragmatic phase-one constraints — a narrow, testable starting point from which the wider FoundrySide vision can be pursued if evidence and resources justify it — or whether you are recommending a substantive change to the ultimate ambition and product direction.

My preference is to retain the wider ambition while being uncompromising about sequencing. We should earn expansion through evidence, not discard it simply because the first experiment must be narrow. Likewise, the market should be a serious reference baseline, not automatically the ceiling of what FoundrySide is allowed to investigate.

For now, treat the settlement defaults as recommendations under review, not sponsor-approved decisions. In particular, I am not yet accepting D-04 through D-13 wholesale, and I am not setting the D-05 numeric success bar before T0 has produced a defensible real-market measurement and interval.

Please respond to the distinction above and explain how you would preserve the full FoundrySide ambition while keeping the first phase focused, falsifiable, affordable and capable of being stopped if the evidence does not support continuation.

No implementation is authorised. The existing research-and-proposal gate remains in force.

### 2026-11-03T12:19:30Z · builder · answer
Answering the three questions in the sponsor response.

1. D-04 and D-06 are phase-one constraints, not a change of ambition. The one place I blurred that was D-04, which called the market-view board the product - that treated a defensible interim display as the ceiling of the vision, and it is withdrawn. D-04 now names a phase-one deliverable (instrument plus a provisional board) and leaves the product question open to G3. D-06 now says explicitly that football is the first domain in which the instrument is calibrated, not the boundary of the project.

2. How the ambition is preserved: three tiers, stated in PROPOSAL_SETTLEMENT.md section 0. Ambition (unchanged), programme (a rolling research line), phase (a fixed window). Nothing in phase one removes an ambition item; wider scope is queued, not discarded, on an expansion ladder with an evidence condition at each rung - E1 second market set, E2 second sport, E3 accumulators and jackpots, E4 autonomy claims. E3 in particular is unlocked by the dependence measurement (T3), not by the quality of the writing in section 6.

3. The cost of preserving it is one schema decision, paid now: records keyed by (sport, competition, market, engine) with a declared input contract per engine, rather than football-shaped tables. Approximately free today, a rewrite later. That is the difference between a narrow start and a narrow project.

4. On the market as a reference baseline and not a ceiling: accepted, and it changes the evaluation design rather than the rhetoric. Track A is price-beating, and the market does cap that. Track B is decision support - calibrated uncertainty, abstention value, explanation of what would change the estimate - and the market does not cap it, because a system can be more useful than a price without beating it. Phase one instruments Track A because it has a clean measurement; Track B needs its own design and must not be judged by Track A bar.

5. D-05: accepted that no number is set before T0. What is proposed instead is that the rule is fixed before any engine is scored, so the number cannot be moved afterwards: bar = measured baseline at 95 percent interval + delta at 80 percent power for a pre-declared correction family, with n of at least 2000, calibration within 3pp and BH correction. The number falls out of T0; the procedure does not wait for it.

6. Process note, reported rather than fixed quietly. The sponsor entry at 12:XX:00Z has a placeholder timestamp and the kind response, neither of which the header grammar accepts. The parser treated the unparsed header as body text of the preceding builder entry, so the entry vanished from the structured record while the checker still reported clean - a fail-open parse, the same defect class ODE fixed for git inspection. It is now fail-closed: an entry-looking line that does not parse is an error, the affected header is acknowledged in ACKNOWLEDGED_MALFORMED and printed as a warning on every run, and response is an accepted kind. The malformed line stays in place because THREAD.md is append-only; this entry is its structured restatement. Evidence: 23 tests OK, collab_check.py -> entries=6 rows=5 warnings=1 errors=0.

No implementation has started and none will without a proposal and an authorisation. RQ-002, RQ-003, RQ-004 and RQ-005 are at ready_for_review against this revision.
- revision: 0e05653
- ref: PROPOSAL_SETTLEMENT.md


### 2026-11-03T12:23:48Z · sponsor · response

The clarification is accepted. D-04 and D-06 are phase-one constraints, not a reduction of FoundrySide's ambition. The three-tier distinction — ambition, rolling research programme, and bounded phase — is the right way to preserve the wider multi-sport vision while keeping the first work testable. The expansion ladder is also useful, provided that "queued" means retained as a live research direction rather than silently abandoned.

I want us to settle the proposal promptly and begin useful research now. We should not turn the proposal process into another long prerequisite waterfall. Please prepare a concise formal research-phase proposal from the direction below, while running the authorised tests and investigations in parallel. The proposal should state the scope, boundaries, cost ceiling, evaluation rules, deliverables and stop/continue gates. It can be refined with measured results; it does not need to wait for every experiment to finish.

**Direction and decisions for the first phase**

1. **D-04 — phase-one deliverable:** accept the instrument plus a provisional market-view board as the practical starting deliverable, not the final product definition. Keep both research tracks alive: (A) whether any independent method can beat an appropriate market baseline at matched coverage, and (B) whether calibrated uncertainty, abstention, explanation and decision support add value even without beating the market. The market is a benchmark, not the boundary of our ambition.

2. **D-05 — evaluation rule:** accept pre-registration before scoring and measurement of the real-market baseline through T0. Do not import OLPRS's virtual-league 0.515 figure. I am not approving the proposed n ≥ 2,000 or ±3 percentage-point calibration rule as universal constants yet. Show the power/sample-size reasoning, outcome and market dependence, confidence intervals, calibration method, multiple-testing family and practical effect size. Recommend a defensible protocol before the first scored experiment; once agreed, freeze it and do not move the goalposts.

3. **D-06 — first slice:** accept football as the first calibration domain and 1X2, O/U 2.5 and BTTS as candidate initial markets. Do not commit blindly to twenty divisions or claim league-level generalisation. Use T0/T1 to identify a feasible, lawful competition set and report the coverage-versus-generalisation trade-off. Other sports remain on the expansion ladder and may be investigated at desk-research level where useful.

4. **D-07 — accumulators and jackpots:** defer product/engineering scope, but do not prohibit research. Run the proposed dependence measurement (T3) and a bounded feasibility check of whether relevant jackpot rules/results are publicly available. These are inexpensive investigations that can inform later decisions.

5. **D-08 — data and cost:** prioritise free, published and legally usable sources. Target KSh 0 recurring cost; do not incur paid API, hosting or inference charges without asking me first. If a genuinely useful option requires spending, present the exact cost and benefit for approval. Check source terms, Kenya accessibility, coverage, historical depth and closing-price availability before automation.

6. **D-09 — infrastructure:** local-first and resource-efficient by default. Research existing available compute and low-cost options only where they materially help. No cloud deployment or paid service is authorised by this response.

7. **D-10 — autonomy:** DeepSeek is authorised to independently run the agreed research, desk investigations, data-access checks, reproducible offline/limited-scope experiments and supporting research scripts. It may choose sensible next tests, challenge assumptions, compare methods and report findings without seeking approval at every step. It must preserve raw evidence, timestamps, source/terms provenance, frozen predictions, experiment definitions, costs and negative results. No account creation, third-party contact, spending, public claims or real-money execution without separate approval.

8. **D-11 — interface:** defer the interface decision. CLI/local dashboard may be evaluated as options, but do not let an early interface choice drive the research or become application development.

9. **D-12 — legal and responsible posture:** accept research-only framing. No promises or return targets, no encouragement to chase losses, and no real-money betting execution. Record the Kenya legal/licensing questions before any public-facing launch is proposed.

10. **D-13 — gates:** use staged decision gates, but treat 30/60/90 days as planning checkpoints rather than artificial deadlines that override evidence availability. Each test must have a stated question, method, data requirements, cost, pass/fail or inconclusive outcome, and what decision follows.

**Immediate authorisation**

Please start T0 and T1 as priorities: establish the real-world baseline methodology and determine whether suitable closing-price/result data can be obtained lawfully, affordably and with adequate coverage. Run T3's bounded dependence/jackpot feasibility work in parallel. Design T2 properly once the baseline and data access are understood; do not manufacture an edge claim from a tiny or unsuitable sample.

You may also investigate other prediction approaches, information-latency hypotheses, coverage/margin differences, market-specific effects and useful prior art where they can produce a concrete, testable next step. Keep a modest exploration stream for ideas outside the current thesis, but distinguish exploratory findings from confirmatory evidence.

This is authorisation for research and experiments, not for building the FoundrySide application. Reproducible research code, temporary test harnesses and analysis artefacts are allowed where needed to answer the questions; no production application, permanent product schema, deployment or public service is authorised.

Please update the proposal/decision register to reflect these settled directions, draft the concise formal proposal promptly, and proceed with the authorised work without waiting for another round of permission. Bring me decisions that genuinely require my input — especially any cost, legal boundary or irreversible scope choice — rather than routine research choices.

The aim is momentum with discipline: settle the research programme now, learn from evidence as it arrives, and preserve the full FoundrySide ambition without pretending that the first experiment has already proved it.

### 2026-11-03T12:29:46Z · builder · evidence
T0, T1 and T3 are run, and the proposal is drafted. Results first, because two of them change decisions.

T1 (access): football-data.co.uk division files, 40 files, 8 divisions, 5 seasons, 2020-09-12 to 2025-05-25, 14,802 fixtures. Every fixture has a complete closing 1X2 price; 14,799 of them are Pinnacle closing, 3 are Bet365 closing. sha256 per file recorded in research/data_manifest.csv. Cost KSh 0, no account, nothing redistributed. Legal position recorded as a reading of published reuse terms, not an opinion - any publication of derived data is a separate decision (P-03).

T0 (baseline): favourite by closing price is 53.3 percent, 95 percent interval 52.5-54.1, on 14,802 fixtures. Home always 43.0, draw always 25.2, random 33.3. Mean 1X2 overround 2.8 percent. The OLPRS figure of 51.5 is withdrawn and would have been too lenient: the real baseline is 1.8 points higher. Per-league accuracy runs from 47.5 (E1) to 56.4 (N1), an 8.9 point spread, which is why pooling is allowed for measuring the instrument and forbidden for claiming a model works.

T3 (dependence): P(BTTS) 53.1, P(over 2.5) 51.8, product 27.5, realised joint 40.9 (95 percent interval 40.1-41.7), ratio 1.49 (1.46-1.52), P(over 2.5 given BTTS) 77.0. Multiplying the marginals understates the joint by 13.4 points, a 49 percent relative error, and the ratio is above 1.3 in all eight divisions. Section 6 of the pre-proposal was right and its magnitude is now known.

One consequence needs your decision, and I have not treated it as settled. The power arithmetic at the measured baseline shows the proposed floor of n >= 2000 can only detect a 3.1 point edge; n = 5000 detects 2.0; the whole corpus detects 1.1. A 3.1 point requirement is implausibly large for the signals this project would build, so a null at 2000 would look decisive while being uninformative. PROPOSAL.md section 4 therefore recommends n >= 5000 for any claim of edge, with n around 2000 accepted only as inconclusive. That is P-02 and it is the single thing blocking T2.

Also updated: D-04 to D-13 are recorded in DECISIONS.md as settled, with the two changes made in settlement - D-04 is now a phase-one deliverable rather than a product definition, and D-05 is settled as a rule with its constants left open, which is exactly what P-02 is. PROPOSALS.md now holds only three items: the closed register, the sample floor, and the derived-data publication question.

Proposal: PROPOSAL.md, six sections of substance - what the phase is for, scope in and out, data and legal position, evaluation rules including the power table, what was learned, deliverables and gates. Gate G1 has passed; G2 is the first pre-registered engine, which waits on P-02.

Not claimed: any edge. Nothing here beats the market, and the proposal says so in section 9. T2 is designed next, after P-02, and the jackpot feasibility check is a bounded one-day desk question.
- revision: eb0844d
- ref: PROPOSAL.md

### 2026-11-03T12:40:00Z · sponsor · response

I have reviewed the new formal proposal, the T0/T1/T3 results, the analysis script and the manifest. Thank you for moving the work forward in parallel. The proposal is close to a useful working agreement, and the data work has produced genuinely useful evidence. I am approving the research direction and the bounded work below, but I am not signing off the statistical protocol or treating this draft as final yet.

**What is approved**

1. **Phase-one direction and boundaries:** approved as set out in the sponsor response at 12:23:48Z. The wider multi-sport ambition remains intact. Football is a practical first calibration domain, not the definition of FoundrySide.
2. **G1 / T1 access result:** provisionally accepted as a successful research finding. The 40 files, five seasons, eight divisions and 14,802 fixtures provide a useful historical 1X2 dataset, with the manifest and file hashes preserving provenance. The reported 14,799 Pinnacle closing prices and three Bet365 closing prices are a strong initial access result. This is approval for internal research use only, not a legal opinion or permission to redistribute the source data or derived datasets.
3. **T0:** accepted as a descriptive first measurement. The 53.3% favourite-pick accuracy and its reported interval are useful reference facts for this particular sample. The withdrawn OLPRS 0.515 figure must stay withdrawn. Do not treat 53.3% as the final success threshold or as a complete measure of market quality.
4. **T3:** the point estimate is accepted as a useful descriptive finding: BTTS and over 2.5 outcomes are positively associated in this sample, so multiplying their marginal outcome frequencies is not a valid independence assumption. This supports further dependence research, not a conclusion about bookmaker combination pricing or a ready-made accumulator model.
5. **Autonomy and cost:** continue the already authorised independent research, reproducible analysis and bounded experiments. The cost ceiling remains KSh 0 recurring; no paid data, hosting, inference, accounts, third-party contact, publication or real-money execution is authorised.

**What is not yet approved**

**P-02 — do not accept n ≥ 5,000 as the final sample floor yet.** I agree with the concern that n = 2,000 may be too underpowered to rule out small improvements. However, the calculation in the current proposal uses a one-sample proportion approximation. Our actual question is a comparison of two methods on the same fixtures, so their errors are paired; the detectable difference depends on how often the methods disagree and which one is correct on those disagreements. League, season and time clustering may also affect uncertainty. Please calculate power for the actual paired evaluation design, preferably with a simulation or a justified paired test and cluster-aware resampling. Show several plausible effect sizes and the sample sizes needed to detect them. Keep n = 5,000 as a provisional planning scenario only, not an approved universal threshold.

The final protocol should also:
- Compare probability forecasts with the de-vigged market probabilities using proper scoring rules such as log loss and Brier score, alongside calibration and coverage. Favourite-pick accuracy can remain a descriptive metric, but it is not enough to establish that one probability model is better than another.
- Use paired, time-aware evaluation and uncertainty estimates that respect league/season clustering where appropriate. The current Wilson intervals are useful descriptive summaries, but should not be assumed to settle the uncertainty for future model comparisons.
- Recalculate the T3 ratio interval. The current interval divides the Wilson limits for the joint rate by a fixed product of marginal rates; it does not propagate uncertainty in both marginals. A bootstrap or other justified interval for the ratio is needed before quoting 1.46–1.52 as its confidence interval.
- Explain the practical effect size being targeted, the correction family and the role of the proposed ±3pp calibration tolerance. Calibration tolerance should be a guardrail reported with reliability plots and bin counts, not a substitute for proper probabilistic scoring.

**Two proposal corrections before review can pass**

- The proposal describes the sample as eight top-division European leagues, but E1 is the English second tier. Please correct that description and state the actual competition mix. The difference matters when discussing homogeneity and generalisation.
- The scope says 1X2 first, while the earlier T2 recommendation proposed over/under 2.5 because it was not used in OLPRS. Please resolve this explicitly. Recommend which single market and benchmark should be the first confirmatory experiment, and explain why. Do not score an engine until the target market, forecast timestamp, benchmark, coverage rule, scoring metrics, sample/power method and multiple-testing family are preregistered.

**Contextual Intelligence & Anomaly Discovery — approved as a parked research direction, not a current priority.**

I do want FoundrySide eventually to be capable of connecting the smaller details around a match: official and predicted lineups, player availability, manager and tactical changes, stadium and environmental changes, press conferences, credible news, historical patterns and unusual fan-recognised observations. But this is not a priority feature now. We need to cover meaningful ground on the core instrument and first experiments before opening a substantial contextual-data programme.

Please record this as a future research direction only. Do not build a news archive, contextual database, ingestion pipeline or feature system now. Do not divert T0/T1 follow-through or the design and execution of T2. At most, retain occasional low-cost desk notes when directly relevant to an active test; keep them exploratory and separate from confirmatory work. Revisit the programme only at a later gate, when the core work has matured and we can justify the data coverage, provenance, licensing and incremental-value tests. If and when it is investigated, preserve point-in-time integrity: distinguish event time from when information became available, official facts from rumours or fan speculation, predicted lineups from confirmed lineups, and pre-match information from in-play and post-match information. No arbitrary superstition weights: fan-recognised patterns are hypotheses to test, not signals to assume.

**Review disposition for this revision**

- RQ-006 (PROPOSAL.md, revision `eb0844d`): **changes requested**. The draft is useful and close, but the power method, scoring design, competition description and first-market choice need correction before formal acceptance.
- RQ-007 (T0/T1/T3 results and analysis, revision `eb0844d`): **changes requested for the inferential presentation**, not rejection of the dataset or descriptive point estimates. Preserve the raw data, manifest and current results; correct the uncertainty treatment and label descriptive versus inferential claims clearly.
- The other queue rows have not been reviewed in this pass and should not be marked accepted by implication.

Please continue with the corrections and the next useful core research steps without waiting for another permission round. The contextual-intelligence idea is safely parked; the immediate priority remains a sound, affordable, preregistered first experiment. Bring back only decisions that genuinely require my approval.
- revision reviewed: eb0844d
- refs: PROPOSAL.md, research/RESULTS_T0_T1_T3.md, research/analyse.py, research/data_manifest.csv

### 2026-11-03T12:59:55Z · builder · evidence
Corrections made against the review of eb0844d. Six substantive items, and two of the review's points changed numbers rather than wording.

Power (P-02). The one-sample approximation is withdrawn; the design is paired, so power was recomputed for McNemar on the discordant pairs, by simulation, 2000 replications per cell, with a discordance assumption of 0.35. Results: a 1pp edge needs about 27,000 fixtures (40,000 gives 92 percent), 2pp about 6,900 (10,000 gives 92), 3pp about 3,000 (5,000 gives 94), 5pp about 1,100. The 5,000 floor is withdrawn as a universal threshold and replaced by sizing to the target effect. One finding is contrary to the expectation behind the request: clustering at 40 league-season clusters barely moves the test, even at ICC 0.10, because the contrast is within-fixture and between-cluster shifts largely cancel. I did not apply a design-effect correction the simulation does not support; the reasoning and the numbers are in research/POWER.md so it can be argued with.

Scoring. Log loss is now primary, Brier secondary, calibration a guardrail reported with reliability plots and bin counts rather than a test, and favourite-pick accuracy is explicitly descriptive. The benchmark is scored on its own terms: de-vigged Pinnacle over/under 2.5 gives log loss 0.6706 nats, Brier 0.2390, mean implied 51.5 against observed 51.7 on 14,735 fixtures. The target is 0.01 nats, which is 1.5 percent relative and the same order as the market 3.1 percent margin; that is argued in the protocol, not asserted.

T3 interval. The earlier 1.46-1.52 was wrong as a method: it divided Wilson limits of the joint rate by a fixed product of marginals, treating both as known constants. Replaced with a percentile bootstrap over the four outcome cells, 10,000 resamples: 1.49 with 95 percent interval 1.47-1.51. The point estimate is unchanged, and the old interval happened to be close, which is luck rather than validity; the corrected method is now the only one quoted.

Descriptive versus inferential. New section 4 of the results states which numbers are which. Proportions with Wilson intervals and the bootstrap ratio are inferential. Per-league accuracy splits are descriptive and no test of difference has been run on them, which the earlier document implied by presenting them as intervals.

Competition mix. Corrected: seven top divisions plus E1, the English Championship, which is the second tier. That was a real error, not a wording slip: E1 is 2,760 fixtures, 18.6 percent of the corpus, and the lowest-accuracy league at 47.5 percent, so the old description overstated homogeneity.

First market. Resolved to over/under 2.5, on measured coverage of 14,737 Pinnacle closing prices (99.6 percent) and 14,800 Bet365. Reasons in the protocol: two-way so de-vigging is unambiguous, not the market OLPRS consumed, and the outcome has a specifiable structure so a failure is interpretable. 1X2 is deferred, not rejected. Nothing is scored until the freeze record in protocol section 8 is filled and committed.

Contextual intelligence. Recorded as parked in docs/PARKED.md, with what is not authorised, what is allowed, the conditions for reopening, and the point-in-time requirements to carry forward if it is ever opened.

Two process changes, both because the review itself would otherwise have been invisible to the tooling. The review used the field names revision reviewed and refs, which the parser did not accept, so both verdicts failed to authorise anything and the checker correctly failed closed; those two aliases are now accepted. And the verdict was authored by sponsor with kind response, which the checker did not treat as a verdict at all; it now does when the entry names a queue row, while a sponsor response that names no row stays directions rather than a verdict, and the builder still cannot authorise its own work. Three tests cover that boundary.

State: RQ-006 to RQ-010 at ready_for_review against this revision; 28 tests pass; checker errors 0, one acknowledged warning. Two decisions are asked in PROPOSAL.md section 7: accept the protocol as the basis for the first experiment, and accept pilot-based sizing rather than a fixed floor. Neither is reversible after the freeze.
- revision: 00d2923
- ref: PROPOSAL.md

### 2026-11-03T13:03:53Z · sponsor · response

I have reviewed revision `00d2923`, including the revised phase proposal, evaluation protocol, paired power analysis, corrected T0/T1/T3 results and parked-direction note. The response to the previous review is substantial and mostly sound. I am settling the phase proposal and the corrected descriptive results, while keeping the first experiment's statistical protocol open until the remaining issues below are resolved.

**Accepted**

- **RQ-006 — formal research-phase proposal, revision `00d2923`: accepted as the phase-one research plan.** The scope, cost ceiling, deliverables, gates, competition description and choice of over/under 2.5 as the proposed first market are a coherent basis for proceeding. This accepts the research plan, not an application build, not a frozen preregistration, and not permission to score a confirmatory engine yet.
- **RQ-007 — T0/T1/T3 results, revision `00d2923`: accepted.** The corrected bootstrap interval for the dependence ratio (1.49×, 95% interval 1.47–1.51) replaces the invalid earlier interval. The clearer distinction between descriptive sample summaries and inferential intervals is also accepted. Keep the important limitation: this measures outcome dependence, not bookmaker accumulator pricing.
- **RQ-010 — parked contextual-intelligence direction, revision `00d2923`: accepted.** It accurately records the decision: future direction, not a priority, no build or data pipeline now, and only occasional low-cost notes tied to active research.

**Changes still required before the first experiment can be frozen**

1. **RQ-008 — evaluation protocol: changes requested.** The protocol's overall structure is approved as the working basis, but its power section is not yet complete for its primary metric. The first confirmatory metric is log loss, while `research/POWER.md` currently calculates McNemar power for *accuracy differences*. That analysis is useful as a supplementary pick-level sensitivity study; it does not establish power for the proposed 0.01-nat paired log-loss improvement. Implement the pilot-based log-loss power simulation promised in §6, show the distribution of per-fixture score differences and the resulting sample-size/power curve, and state what happens if the available confirmatory slice cannot reach the target power. Do not present the McNemar table as power evidence for log loss.
2. **Forecast timing must be auditable.** The benchmark is a closing price, but the protocol says the model forecast must precede the closing-price timestamp. The current source files establish closing prices but do not appear to provide an auditable timestamp for when each closing quote was observed. Define a fixed, reproducible model information cutoff (for example, a specified interval before kickoff) and demonstrate that every input was available by that cutoff. The closing price can remain the later benchmark; do not imply that an unavailable quote timestamp has been verified. If an actual timestamped price source is later obtained, document its provenance separately.
3. **RQ-009 — paired power analysis: changes requested for its inferential claims and reproducibility.** The script calls `random.gammavariate` through the module-level generator, while the binomial draws use a locally seeded `Random` instance. Consequently the stated seed does not control all random draws and the reported simulation is not fully reproducible. Route every random draw through the same seeded generator and add a repeatability check. Also, the cluster simulation varies the *rate of discordance* by cluster but holds the model's conditional chance of winning a discordant pair constant. It therefore does not test whether the model's relative advantage varies across league-season clusters. Do not conclude that clustering is negligible from this design. Add sensitivity for cluster-level variation in the paired advantage (or use a justified cluster bootstrap), and label the current McNemar results as an accuracy-only analysis.

**Record consistency**

`docs/COLLAB/PROPOSALS.md` still contains the superseded P-02 recommendation for a universal 5,000 floor and the old one-sample accuracy arithmetic. `DECISIONS.md` still quotes the superseded T3 interval of 1.46–1.52. Please reconcile both records with revision `00d2923`: P-02 should reflect the actual outstanding protocol/pilot-sizing decision, and D-07's evidence should use the corrected bootstrap interval. Do not silently delete the history of the earlier correction; state that the old figure was superseded.

**The two sponsor decisions in PROPOSAL.md §7 remain open for now.** I am not yet accepting the protocol as frozen, nor approving the proposed pilot/confirmatory split as sufficient until the log-loss power simulation and forecast-time rule are made operational. You may continue exploratory pilot work and research-script development under the existing authorisation, but no confirmatory engine scoring until the freeze record is complete, the protocol is corrected, and the final preregistration is committed.

Continue without waiting for another permission round on routine research. The phase plan is accepted; the remaining work is to make the first experiment genuinely auditable and statistically aligned with the question it claims to answer.
- revision reviewed: 00d2923
- refs: RQ-006, RQ-007, RQ-008, RQ-009, RQ-010

### 2026-11-03T13:14:27Z · builder · evidence
RQ-008 and RQ-009 corrections, plus the record reconciliation.

Log-loss power, now implemented. research/logloss_power.py builds per-fixture score differences on the real fixtures and prices: the model deviates from the de-vigged market probability by w, toward the truth with probability 0.6 and away otherwise, with the deviation magnitude varying per fixture. That gives a two-sided distribution, which matters: my first attempt blended the market with an oracle, so every fixture improved, the SD collapsed to 0.004 and the script reported 100 percent power at every sample size. It was degenerate and I replaced it rather than report it.

The governing result is not the device. It is the sensitivity of sample size to the unknown SD of delta, which the pilot must measure: at a 0.01-nat effect, SD 0.10 needs 785 fixtures, 0.15 needs 1,766, 0.20 needs 3,140, 0.27 needs 5,722. The confirmatory slice holds 5,794, so it supports 80 percent power at this effect only while SD is at or below 0.271; at SD 0.35 power is 58.5 percent and at 0.50 it is 33.1 percent. A null from an underpowered slice is uninformative, so the protocol now names the three responses available if the pilot finds a larger SD: extend the slice, add markets to the family, or raise the target effect - each declared in the freeze, none applied after seeing results.

Forecast timing, made auditable. The source files carry a closing price and a kickoff date and time, and no observation timestamp for the quote. The protocol no longer implies one. It defines a fixed cutoff of kickoff minus 90 minutes, computed from the fixture's own Date and Time, requires that inputs come only from matches final before that cutoff - kickoff plus three hours, which excludes a 12:30 match for a 15:00 fixture - and requires every prediction record to store its maximum input timestamp so the audit can fail the run. The benchmark remains the closing price, which is later than the cutoff, and that is now stated as a deliberate comparison rather than a claim about when the quote existed.

RQ-009, three defects. First, reproducibility: random.gammavariate drew from the module-level generator while the binomial draws used a seeded instance, so the stated seed controlled only part of the simulation. Every draw now goes through one seeded generator and main() asserts that two runs with the same seed are identical; it passes. Second, the test: a two-sided McNemar ignores between-cluster variance and rejects too often under heterogeneity, so the clustered scenarios now use a cluster-robust t on per-cluster differences. Third, the model: I varied the discordance rate but held the model's advantage constant, which cannot detect a model that is better in particular leagues.

That third defect produced a finding that reverses my previous claim. With advantage varying (ICC 0.05), power at a 3pp edge falls from about 93 percent to about 44 percent at 5,000 fixtures, and adding fixtures then stops helping: 10,000 gives 50 percent, not 93. With 40 league-season clusters the binding constraint is the number of clusters, not the number of matches. The earlier statement that clustering is negligible at 40 clusters is withdrawn, and POWER.md is relabelled as an accuracy-only supplementary study so it cannot be cited as power evidence for log loss.

Record reconciliation, done as asked and with the history visible rather than deleted. P-02 no longer recommends a universal 5,000 floor; it states that the recommendation was withdrawn and why, then lists the four protocol items actually awaiting decision. D-07 now carries the corrected bootstrap interval 1.47 to 1.51, records the superseded 1.46 to 1.52 with the reason it was invalid, and states the scope limit that this measures outcome dependence and not bookmaker pricing.

State: RQ-008 and RQ-009 back to ready_for_review, RQ-011 added for the log-loss power work; 28 tests pass, checker errors 0. The two sponsor decisions in PROPOSAL.md section 7 remain open, and nothing has been scored against the benchmark.
- revision: 16ec671
- ref: docs/EVALUATION_PROTOCOL.md


### 2026-11-03 · sponsor · review

I reviewed revision `16ec671`, including the new log-loss power device, the revised accuracy clustering simulation, the evaluation protocol, and the record reconciliation.

**Accepted**

- **RQ-009 — paired accuracy sensitivity analysis: accepted for its stated, limited purpose.** The script now routes random draws through one seeded generator and asserts repeatability; it distinguishes variation in discordance from variation in paired advantage; and it withdraws the unsupported claim that clustering is negligible. The resulting analysis is explicitly accuracy-only and supplementary. Its assumed ICC scenarios are sensitivity assumptions, not estimates of the real project’s cluster structure. Do not use these results as log-loss power evidence.

**Changes still required**

- **RQ-008 — evaluation protocol: changes requested.** The T−90 cutoff is a useful improvement, and the source timestamp limitation is now stated honestly. However, the protocol is internally inconsistent in two places: §5 still says clustering was measured to have a negligible effect on the accuracy contrast, which the new analysis explicitly withdraws; and §8 still lists the forecast timestamp as the “last recorded pre-kickoff price”, although the proposed model cutoff is kickoff minus 90 minutes and the benchmark is the later closing price. Correct both. Also define the timezone and daylight-saving interpretation of each competition’s Date/Time fields before calling the cutoff fully auditable; a reproducible arithmetic rule is not enough if the underlying clock is ambiguous. State how the cutoff is validated against the actual parsed fixture timestamp.

- **RQ-011 — log-loss power: changes requested.** The new script is candid that it uses a synthetic deviation device, not a real engine or pilot predictions; that is useful for sensitivity exploration, but it does not yet establish the actual experiment’s power. More importantly, `power()` computes only the upper-tail probability `Phi(mean*sqrt(n)/sd - z` while the protocol specifies a two-sided alpha of 0.05. The bootstrap check uses an absolute two-sided statistic, so the analytic curve and bootstrap check are not testing the same rejection rule. Correct the analytic power calculation to the stated two-sided test and regenerate the report. Then keep the synthetic device clearly labelled as illustrative and make the freeze contingent on the pilot’s actual out-of-fold paired log-loss differences, including a cluster-aware uncertainty/power assessment. The pilot must estimate both the within-fixture spread and between-division-season variation; the 0.271 SD threshold alone is not sufficient if dependence reduces effective information.

The T−90 design also needs the time-zone clarification above before I can accept the claim that it is auditable. The benchmark may remain the closing price, provided the protocol consistently describes this as a T−90 forecast compared with the closing line, not as a forecast proven to precede an observed closing-price timestamp.

**State:** RQ-009 accepted with its accuracy-only scope. RQ-008 and RQ-011 remain changes requested. Exploratory research and pilot preparation may continue under the existing authorisation. No confirmatory engine scoring is authorised; the protocol is not frozen.

- revision reviewed: `16ec671`
- refs: RQ-008, RQ-009, RQ-011

### 2026-11-03T13:25:10Z · builder · evidence
RQ-008 and RQ-011 corrections against the review of 16ec671. Four points, all fixed, and one of them needed a new module rather than a paragraph.

Two-sided power. The review is right: power() computed Phi(x - z) only, while the protocol states alpha 0.05 two-sided and the bootstrap check used |t|. The curve and the check beside it were testing different rules, which makes neither evidence. power() now computes both tails, and the bootstrap uses the same |t| rule. At these effect sizes the two differ by rounding, so the numbers barely moved - which is the point, not a defence: the mismatch was real and would have mattered at larger effects.

Synthetic device, labelled. The deviation model is now described as illustrative in the document heading, not only in the body: it is a sensitivity exploration, not pilot power. The freeze is explicitly contingent on the pilot's own out-of-fold paired log-loss differences.

Dependence, quantified rather than caveated. The threshold 0.271 was stated for independent fixtures, and the review is right that dependence reduces effective information. The document now carries a design-effect table: permitted SD falls from 0.272 at D=1 to 0.248 at 1.2, 0.222 at 1.5 and 0.192 at 2.0. The pilot therefore estimates two things, the within-fixture spread of delta and the between-division-season variance that produces D. Sizing on the spread alone would repeat the accuracy mistake.

The clock, made auditable. This needed code. research/fixture_time.py maps each division to an IANA zone, converts the fixture's local civil time to UTC, and computes the cutoff in UTC; it detects spring gaps and autumn folds rather than resolving them silently. Run over the corpus: 14,802 clocks parsed, 8 divisions mapped, zero ambiguous or unmapped. 13 tests cover a BST kickoff, a post-transition kickoff, the one-hour continental offset, a gap, a fold, the same-day 12:30 versus 15:00 case, and the DST boundary. The protocol states the mapping as an assumption about the source rather than a fact read from it, which is what the audit is for, and the prediction record stores the parsed instant so the check is against the fixture's real timestamp rather than against clock text.

Two protocol inconsistencies from the review, both corrected. Section 5 no longer says clustering was measured negligible; it now says the opposite, citing the accuracy analysis and applying the caution to log loss rather than assuming it away. Section 8 no longer lists the forecast timestamp as the last recorded price; it is kickoff minus 90 minutes in UTC, with a timezone field beside it.

Process note. The review's revision line wrote the SHA in backticks, so the field parsed as a literal backticked string and neither verdict matched its row; the checker failed closed with two errors, which is what it is for. Emphasis is now stripped from the field value, since it is formatting rather than data. The same review also used a date-only entry stamp, which the chronology check was reporting as out of order; a date-only stamp means the time is unknown, so it is now skipped rather than assigned a midnight it never claimed.

State: RQ-008 and RQ-011 back to ready_for_review, RQ-012 added for the clock module; RQ-009 accepted with its accuracy-only scope; 41 tests pass; checker errors 0, one acknowledged warning. Protocol remains unfrozen and nothing has been scored.
- revision: 55780e2
- ref: docs/EVALUATION_PROTOCOL.md
