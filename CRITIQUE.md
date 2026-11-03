# Critique: FoundrySide pre-proposal

A review of `PRE_PROPOSAL.md` (23 sections, 39 KB) written before any code exists.
This is not a summary. It assumes you have read the document and it argues with it.

Scope note: nothing here authorises implementation. `DECISIONS.md` D-01 says the
project is not authorised to build, and this critique does not change that.

---

## 1. What is genuinely strong

Four things here are better than most documents of this kind, and the
recommendations below are designed to protect them.

**The research-lab framing (§3).** Competing engines, promotion on demonstrated
performance, history preserved, no retroactive editing of predictions. Most
prediction products are a single model with a marketing layer; this is an
epistemology. The refusal to declare a winning methodology in advance is correct.

**The independence requirement (§3.1).** "The central ensemble should not
automatically trust the newest or most sophisticated model" is the sentence that
separates this from a demo. It is also the sentence that makes the rest of the
project expensive, which the document does not yet acknowledge.

**The accumulator insight (§6).** Both teams to score and over 2.5 goals in the same
match are correlated, and multiplying marginals is wrong. Most accumulator products
ship that error. Naming it before writing code is a real contribution.

**Calibration as a first-class metric (§11).** "A model that predicts 80% should
experience that outcome 80% of the time" is the right test, and it is the one most
prediction projects avoid because it is the one that fails.

**The responsible-language discipline (§17).** No guaranteed returns, no concealed
losses, no simulated results presented as real. This is rare enough to be worth
saying plainly.

Everything below is about the gap between those instincts and a document that
produces a decidable proposal.

---

## 2. Structural findings

### F1 — There is no falsifier anywhere in the document

Twenty-three sections describe what the system will investigate. None states what
result would end the project. §3 says methods that fail should be retired, but the
programme itself has no kill condition, and §20's principles are all directions
("investigate", "preserve", "minimise") rather than tests.

ODE's correction to its own proposal is the relevant precedent: every experiment
there carries a **pre-registered kill condition**, written before the evidence is
gathered, "so it cannot be quietly renegotiated afterwards" (`ODE/README.md`). A
research programme without one does not fail; it continues, publishing confidence.

**Fix:** three kill conditions, written into the proposal, each with a date and a
number. The obvious candidates: no market-relative edge after N resolved
predictions; the same at matched coverage against the favourite baseline; data access
cost exceeding the ceiling. If none can be stated, the project is not a research
programme yet, it is an intention.

### F2 — §21's thirteen reports are a waterfall standing in for a proposal

The sequence in §22 is: thirteen research deliverables, then a proposal, then
authorisation. Read as a plan, that is a 6–12 month gate in front of a document that
could be written this week.

Three of those deliverables (existing systems, market analysis, infrastructure
feasibility) are already substantially answered — by this sponsor's own prior work,
which §13 declines to cite. The rest are cheap: ODE's measured cost of one
investigation of this shape is **KSh 3–5** at current model prices
(`ODE/README.md`, `STRATEGY.md` §6). The scarce resource in all three of these
repositories is attention, not tokens, and this document spends attention on breadth.

**Fix:** invert the order. Write the proposal first, as a set of commitments with
defaults; let research *de-risk* the commitments instead of gating them. A proposal
that cannot be written before the research is usually a proposal that is avoiding a
decision.

### F3 — The unit of record is a "predictive engine", which is a conclusion-shaped object

§3.1 says each engine should have "a clearly defined methodology, input
requirements, output format and performance history". That describes the *output* of
reasoning, not the reasoning. ODE identified exactly this defect in its own
foundational proposal and inverted the schema: the unit of record became a
**falsifiable claim** with the opportunity as a hub, because "once the record is a
conclusion, the evidence standards have nowhere to live ... and the database fills
with confident prose" (`ODE/STRATEGY.md` §2.1).

FoundrySide repeats the mistake at a higher level. "Engine performance history" is a
number; it cannot answer *which claims did this engine contradict*, *what did we
believe in August that we no longer believe*, or *how many independent origins back
this edge*. Those are the questions that make §3's laboratory worth running.

**Fix:** claims, predictions and experiments as first-class rows; engines as
registries that point at them. This is a schema decision, and it is cheap now and
expensive after the first hundred predictions.

### F4 — There is no cost unit, so "KSh 0" cannot fail

§14 sets a target of KSh 0 recurring and a fallback of KSh 100–200/month. There is no
per-unit accounting: no cost per fixture collected, per prediction generated, per
experiment run, per thousand tokens. Without that, the zero-cost claim is not a
constraint, it is an adjective, and the first month that costs KSh 4,000 has no
baseline to be compared against.

ODE meters every task and reports cost-per-investigation and cost-per-decisive-test
(`ODE/STRATEGY.md` §2.5). That is what turns a budget into a policy.

**Fix:** a cost ledger from the first collection run, and one headline number —
KSh per resolved prediction and KSh per decisive experiment — reported on the
dashboard whether or not it is flattering.

---

## 3. Evidence findings

### F5 — There is no null model

§11 lists thirteen metrics and no comparison. Accuracy, Brier score and log loss are
all *relative*: a 55% hit rate means nothing until it is placed against the base
rate, the market, and the favourite.

The document's own §4 gets close — "market odds contain information ... they are an
important reference point" — but never makes the comparison mechanical. ODE's finding
applies directly: "An anomaly is not a property of a number. It is a property of a
number relative to a comparison distribution" (`ODE/STRATEGY.md` §2.2). A system
without a null model generates plausible noise with excellent sourcing.

**Fix:** three mandatory baselines on every evaluation, computed on the same fixtures:
market-implied probability, favourite-always, and the unconditional base rate. Any
claim that does not name which of the three it beats, and by how much, is not
reportable.

### F6 — The persistence question is never asked

§4 hedges correctly ("should not assume that the market is always correct") and then
moves on. It never asks the question that decides whether any of this is worth
building: **if a public-data edge exists, what has stopped everyone else from taking
it?**

ODE makes this a mandatory, length-checked field on every record, because "an
enthusiastic researcher who has spent three hours assembling evidence will not ask
this question spontaneously, because the answer threatens the work"
(`ODE/STRATEGY.md` §2.4). The candidate answers are specific and testable: search
cost, licensing, capital floor, regulatory lag, transaction cost, or a measurement
artefact.

For FoundrySide the leading candidate is uncomfortable and should be stated in the
proposal: **bookmaker margin plus the closing-line efficiency of a heavily traded
market.** If that is the answer, the honest product is not edge.

**Fix:** every proposed engine carries a persistence explanation, or it is recorded
as a lead rather than a research programme.

### F7 — The central research question has been answered once, in a market that is not this one

§13 says the project "should not assume that its proposed capabilities are entirely
new" — and then proposes to investigate from scratch a question OLPRS_v2 has already
tested on 10,329 resolved signals. The results are in the sponsor's own repository and
are not cited anywhere in the pre-proposal.

**The domain narrows the transfer, and the first draft of this critique over-read it.**
OdiLeague is a *virtual* league: `OLPRS_v2/docs/SYSTEM_MAP_2026-10-31.md` describes it
as "a virtual football league: fixtures are simulated, not played", with 38 rounds a
season at two-minute intervals and each season lasting about 76 minutes
(`ODILEAGUE_STRUCTURE.md`). That cadence is why OLPRS could amass 16,831 priced
fixtures. It is also why the market in those fixtures is not a real one.

`OLPRS_v2/docs/SIGNAL_MARKET_VERDICT_2026-10-31.md`, on 10,329 resolved signals
matched to a priced fixture:

| measure | value |
| --- | --- |
| all signals, accuracy | 45.6% |
| all signals, price-implied | 45.9% |
| edge | −0.2pp (95% interval 44.7–46.6%) |
| signal ids surviving Benjamini-Hochberg at n ≥ 60 | **0 of 27** |

`OLPRS_v2/docs/USER_ADVANTAGE_2026-10-31.md`, on 16,831 fixtures at matched coverage:

| policy | accuracy |
| --- | --- |
| favourite (highest implied probability) | **0.515** |
| home always | 0.505 |
| the system's own signal | 0.470 |
| uniform | 0.431 |

Following the signal was 4.5 points **worse** than picking the favourite, on
non-overlapping intervals. And the most useful positive result in that body of work
is not a model at all: it is that the market pick, shown only when the implied
probability clears a threshold, reaches 61.1% at 12.2% coverage
(`USER_ADVANTAGE`, second half) — a defensible *board* claim built from nothing but
price and abstention.

**What transfers, and what does not.**

| | Transfers? | Why |
| --- | --- | --- |
| The method: market-implied benchmark, matched coverage, BH correction, calibration, point-in-time provenance | **Yes, fully** | These are properties of a comparison, not of a league |
| The constant 0.515 as "the bar" | **No** | It is a virtual-league quantity and must be re-measured on real closing prices before it can be a bar — corrected in `PROPOSAL_SETTLEMENT.md` D-05 |
| "Real football markets are efficient, so FoundrySide is pointless" | **No — and this critique does not claim it** | OLPRS traded against one operator's price on an outcome that operator may itself generate, with no sharp money and no aggregated information flow |
| "Real markets are softer than virtual ones" | **No** | The opposite is likelier: real closing lines aggregate informed money and are the most heavily modelled prices in sport |
| The feature-class lesson: form, position and odds-tier features restate the price | **Yes** | It is a property of the features, and those are the features §3 and §4 propose to rebuild |

`SYSTEM_MAP` also records that whether OdiLeague's simulation is deterministic or
seeded is "unknown, and not testable from outside". That line is the strongest reason
not to over-read the null: if the operator prices from the same process that generates
the result, the market is unbeatable *by construction*, and the experiment measured the
operator's information advantage rather than market efficiency. The honest summary is
narrower than "already answered": one feature class, against one kind of market,
produced nothing.

**What is left for "what is different this time".** Three differences are nameable and
each has a measurement. None of them is "the real world", which is a setting, not a
hypothesis.

1. **Information latency.** Real prices move as lineups, injuries, travel and weather
   become public. Whether a *specific* class of announcement is absorbed slowly is
   measurable, has a clock attached, and has no analogue in a league where nothing is
   announced.
2. **Coverage gradient.** Sharp money concentrates in the top five leagues and the main
   markets; lower divisions and secondary markets carry wider margins and thinner
   attention. That is a place an edge could survive because nobody is looking — which
   is exactly the persistence explanation F6 demands, and it is testable by comparing
   margin and closing-line behaviour across divisions.
3. **Correlation structure.** §6's dependence question is arithmetic about how
   combinations are priced, not a fact about football, and it survives the domain change
   intact.

**A planning consequence the domain change forces.** Real football accrues evidence
about three orders of magnitude slower than OdiLeague: roughly 600 fixtures an hour
there, roughly one fixture per league per day here. One division yields ~90 fixtures in
90 days; twenty divisions yield ~2,700. So D-05's sample requirement and D-06's slice
are not independent decisions — a narrow slice cannot satisfy the bar inside the gates,
and a wide slice changes what the model must generalise across. That tension is carried
into `PROPOSAL_SETTLEMENT.md` rather than hidden.

**Fix:** cite these results as prior art with their domain attached, and make "what is
different from OLPRS" a required section that answers the three items above. A
programme that cannot answer them will reproduce a null for a different reason and will
not know which.

### F8 — §6 names the right problem and proposes no test for it

The accumulator section is the document's best technical observation and its least
actionable section. It lists ten things to distinguish and no measurement. The
decisive test is cheap and should be named: take one season of fixtures where
same-match selections were offered, compute the realised frequency of the joint
outcome against the product of the marginals, and report the ratio with an interval.
If dependence is small, the whole correlation programme is unnecessary; if it is
large, it is the most interesting number in the project. Either way it costs a day,
not a research track.

The same applies to the jackpot section: its evaluation is well specified and its
feasibility question — do accessible operators publish the structures and results
needed to score a simulated entry at all — is unanswered and is a one-day check.

---

## 4. Design findings

### F9 — §8 writes a product specification for payout-chasing, which §17 forbids

The user profiles are defined by stake size and desired return: KSh 30–100 hoping for
large returns, KSh 100–300 "hope to achieve returns in the region of KSh 1,000–3,000",
KSh 500+ hoping to "double or triple the amount". §8.3 then correctly notes the
system should sometimes say *do not bet*.

Those two positions cannot both hold. A profile defined by a return target creates
pressure to hit the target; §17's "no guaranteed outcomes" becomes a disclaimer
attached to a product that is shaped around the thing it disclaims. The Kenya
gambling advertising rules and BCLB licensing position make this a legal exposure as
well as an ethical one.

**Fix:** replace stake-size personas with **decision contexts** defined by the
question the user is asking — "which of these is mispriced", "which should I avoid",
"how confident is this" — and let stake size be a display filter, not an identity.
This is also better product design: the abstention result above is worth more than
any accumulator feature, and it only exists if the user's question is "should I bet
at all".

### F10 — "Continuous autonomous operation at KSh 0" is internally contradictory

§9 wants continuous autonomous operation; §14 wants KSh 0; §9.2 correctly says LLM
inference should be used selectively. Those three cannot all be maximised. LLM calls
cost money, continuous scheduling on free tiers hits quota and cold-start limits, and
the document itself warns that promotional credits are not a zero-cost solution.

The honest version is not a slogan but a number: a fixed monthly inference budget,
spent where reasoning adds value, with the routine numerical work in conventional
models. ODE's KSh 3–5 per investigation is the only measured figure available in
these repositories and it should be the starting point, not an embarrassment.

**Fix:** replace "KSh 0" with "KSh ≤ 200/month, metered, and the meter is published",
and replace "continuous" with a schedule: what runs hourly, what runs daily, what
runs on demand.

### F11 — "Autonomy" is unfalsifiable and has no failure modes

§9 lists sixteen capabilities and no mechanism. There is no idempotency requirement,
no freeze-at-write, no replay, no schema-drift detection, no statement of what
happens when a source silently changes shape, and no definition of "autonomous" that
could be measured and found wanting.

The sponsor's own systems already contain both lessons. `OLPRS_v2/docs/PIT_INTEGRITY_2026-10-31.md`
found the as-of join was correct but the provenance was **not persisted**: 0 of 4,622
live rows recorded which standings snapshot informed them, so what was knowable at
prediction time could not be reconstructed later. The fix was one column written at
write time. FoundrySide §10 demands exactly this ("the source of each important
observation") and does not specify when it is written — which is how the same gap
reappears.

**Fix:** define autonomy operationally — the share of weekly operations needing
human action — and make the *first* schema decision the immutable prediction record
with its input snapshot hash, written once, never updated.

---

## 5. Verdict

| Section | Verdict | Reason |
| --- | --- | --- |
| §1–2 vision | Keep | Clear, honest, correctly distinguishes advantage from profit |
| §3 research laboratory | Keep, fix F1 F3 | Right epistemology, no falsifier, wrong unit of record |
| §4 market as reference | Keep, fix F5 F7 | Right instinct; the prior is narrower than it first looks; no null model |
| §5 sports coverage | Cut to one sport | Four sports before one edge is breadth bought with attention |
| §6 accumulators | Keep as a one-day test | Best insight in the document; needs a measurement, not a laboratory |
| §7 jackpots | Defer | Feasibility question unanswered and cheap to answer |
| §8 user profiles | Rewrite (F9) | Encodes the return targets §17 disclaims |
| §9 autonomy | Fix F10 F11 | Unfalsifiable as written |
| §10 data integrity | Keep, make mechanical | Correct requirement, missing the write-time rule |
| §11 evaluation | Keep, add baselines (F5) | Best section after §3; needs a comparison set |
| §12 providers | Keep, narrow | A source catalogue is a week's work, not a track |
| §13 existing work | Keep, and cite OLPRS | Currently the largest omission in the document |
| §14 zero cost | Rewrite as a budget (F10) | A target with no meter cannot fail |
| §15 architecture | Defer | Correctly refuses to decide early; honour that |
| §16–17 reporting, safety | Keep | Genuinely good; constrain §8 |
| §18–22 process | Cut to three questions | The waterfall is F2 |
| §23 intent | Keep | It is the standard the rest should be held to |

---

## 6. Prior art: what to take from OLPRS and ODE

Both repositories belong to this sponsor, so this is not a literature review; it is
an inventory of parts already built and paid for.

**From ODE, take the epistemic machinery — it is the transferable asset:**

- claim/evidence as the unit of record, with evidence counted per **independent
  origin** rather than per source;
- a mandatory **persistence explanation** on every proposed edge (F6);
- a mandatory **null model** dimension (F5);
- **pre-registered kill conditions** on every experiment (F1);
- a **cost ledger** with cost-per-decisive-test (F4);
- **explore-share** budgeting: 80% by expected value, 20% reserved for what the
  current thesis does not justify — the executable version of §3's promise not to
  pre-declare where value lives;
- **supersede, never delete**: a wrong belief is the most useful record in the file.

**From OLPRS, take the measurements and the scars — they are the project's only
empirical base:**

- the market is the benchmark, and it wins there: 45.6% vs 45.9%, 0/27 after
  correction — a result about a virtual league, so see F7 before importing it;
- the favourite is the baseline to beat, not "the market" in the abstract: 0.515 at
  matched coverage on virtual fixtures, a figure that must be re-measured on real
  closing prices before it is a bar;
- abstention is the strongest product finding available: 61.1% at 12.2% coverage;
- point-in-time integrity is a *write-time* obligation, not an analysis-time one;
- collector drift is normal, not exceptional: sources change shape silently, so
  schema-drift detection belongs in the collection path, not the debugging session;
- and the meta-lesson from both repositories: **a reviewer that does not re-test
  inherits the error.** ODE's bridge records a case where a claim about a revoked TLS
  certificate was propagated into four files without being re-tested, by reviewers
  who trusted the dossier. FoundrySide's most important numbers are comparisons, and
  comparisons survive review while being wrong. Re-fetch, re-run, re-quote.

---

## 7. The three questions that actually block the proposal

Everything above reduces to three questions the sponsor has to answer, and no amount
of research answers them on the sponsor's behalf:

1. **What is the product?** A board that restates the market's view with abstention
   discipline — which the evidence supports today — or an independent model that
   must beat that board at matched coverage — which nothing yet supports.
2. **What is the bar?** A number, in the units OLPRS already measured, that a model
   must clear before any claim is made about it.
3. **What is out of scope for ninety days?** Accumulators, jackpots, multi-sport
   coverage, public interface, real-money execution — each of which is defensible
   later and expensive now.

`PROPOSAL_SETTLEMENT.md` turns those three into ten decisions with recommended
defaults, so the answer can be one message long.
