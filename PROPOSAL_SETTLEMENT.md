# How to settle the proposal this week

**Status: recommendations under review, not decisions.** The sponsor's response of
2026-11-03 asks whether D-04 and D-06 are phase-one constraints or a change to the
project's ambition, declines to accept D-04–D-13 wholesale, and declines to set D-05
before T0 has produced a real-market measurement. All three points are accepted below;
`DECISIONS.md` still holds only what the sponsor has settled, and nothing here is
approved.

The pre-proposal asks for thirteen research reports before a formal proposal (§21,
§22). That is a six-to-twelve-month gate in front of a document that can be written
in a day, and it has a failure mode the sponsor has already seen twice: research
expands to fill the attention available, and the decision moves further away the
more is learned.

This document proposes the opposite order. **Write the proposal first, as a set of
commitments with defaults. Let research de-risk the commitments instead of gating
them.** The proposal is then a hypothesis the research can kill, which is a stronger
artifact than a summary of research that can no longer be argued with.

The mechanism has three parts: three questions, ten decisions, and one reply shape.

---

## 0. Scope: ambition, programme, phase

The sponsor's question — are D-04 and D-06 phase-one constraints or a narrowing of the
vision — has a short answer: **phase-one constraints, and the revision of D-04 below
withdraws the one place where I had blurred it.** Three tiers keep them apart.

| Tier | What it is | Changes when |
| --- | --- | --- |
| **Ambition** | `PRE_PROPOSAL.md` §2: an autonomous, multi-sport research laboratory with competing engines, accumulators and jackpots | Not in this phase. Nothing here removes an ambition item from the vision |
| **Programme** | A rolling research line inside the ambition: football 1X2 now; a second market set, a second sport, accumulators later | On evidence, at a named rung of the ladder |
| **Phase 1** | A fixed window: build the instrument, run one programme | At G3 |

**What phase one actually tests is the instrument, not the thesis.** Three properties:
can we obtain lawful, affordable data; can it be stored with point-in-time integrity;
can a baseline be measured with an interval. If any of those fail, no version of the
ambition is testable — so phase one stops, and the ambition is untouched, because what
failed was the apparatus rather than the idea.

**What preserving the ambition costs today: one schema decision.** Records keyed by
`(sport, competition, market, engine)` with a declared input contract per engine, rather
than football-shaped tables. That costs approximately nothing now and is a rewrite
later. It is the only place where the ambition is paid for during phase one, and it is
the difference between a narrow start and a narrow project.

**The expansion ladder.** Nothing is dropped from the vision; it is queued behind a
measurable entry condition.

| Rung | Unlocked by | Not unlocked by |
| --- | --- | --- |
| **E0** Instrument + football programme | This register being answered | Enthusiasm |
| **E1** Second market set (O/U, BTTS) | T0 and T2 producing baselines with intervals | The first market being interesting |
| **E2** Second sport | E1 showing the instrument transfers, or materially better data access there, measured as cost per resolved prediction | An argument that the sport is unexplored |
| **E3** Accumulators and jackpots | T3 showing dependence is large enough to matter, and jackpot structures being obtainable | §6 and §7 being well written |
| **E4** Autonomy claims | A measured share of unattended operations above target, with freeze and rollback proven | A scheduler existing |

**The stop rule.** Phase one stops if T1 finds no compliant source of closing prices,
if two pre-registered engine attempts fail to beat the baseline at matched coverage, or
if cost per decisive experiment exceeds the ceiling. Stopping kills the programme; it
does not revise the ambition, and the record states which condition fired.

**Two tracks, because the market is a control and not a ceiling.** The market is what
makes a claim falsifiable; it is not a definition of what FoundrySide may investigate.

- **Track A — price-beating.** "We estimate the outcome better than the closing price."
  The market does cap this one, and the bar applies.
- **Track B — decision support.** "A user makes a better decision with this than with a
  raw price": calibrated uncertainty, abstention value, explanation of what would change
  the estimate. The market does not cap this, because a system can be more useful than a
  price without beating it — which is what §16 and §17 of the pre-proposal are about.

Phase one instruments Track A because it is the one with a clean measurement. Track B
needs its own measurement design and must not be judged by Track A's bar, or it will be
declared worthless for failing a test it was never given.

---

## 1. The three questions

Only three things actually block a proposal. Everything else in the pre-proposal is
either downstream of them or cheap to reverse later.

**Q1 — What is the product?**
A board that restates the market's view, with abstention discipline, is supportable
today from evidence in this sponsor's own repositories. An independent model that
beats that board at matched coverage is not supported by anything yet. The sponsor has
left this open, which is right while the instrument is unmeasured: phase one needs a
deliverable, not a product decision.

**Q2 — What is the bar?**
A single number a model must clear before any claim is made about it. Without it,
"improvement" is undecidable, and §11's thirteen metrics become a menu rather than a
test.

**Q3 — What is out of scope for ninety days?**
Accumulators, jackpots, multi-sport coverage, a public interface, real-money
execution. Each is defensible later. All of them together are how the first ninety
days disappear.

---

## 2. The ten decisions

Each has a recommended default, so the register can be answered in one message. The
default is what happens if the sponsor says nothing — with one exception, D-05, which
is the only decision that is expensive to reverse and therefore must be answered
explicitly.

### D-04 — Phase-one deliverable *(revised after the sponsor response)*

**What this is not:** a decision about the product. The first draft framed the board as
"the product", which turned a defensible interim display into the ceiling of the vision.
That was the error in the sponsor's question, and this revision withdraws it.

**Options for the phase-one deliverable:** (a) the measurement instrument alone;
(b) instrument plus a board that shows the market's view with abstention discipline;
(c) instrument plus a model-backed board.

**Default: (b).** The board is what it is honest to display while the instrument is
unproven — the market's own view, restated, with an implied probability and a refusal
to show anything weak. It is a floor, not a destination.

**What stays open:** whether FoundrySide's product is a board, a model, an engine
marketplace, or all three. That is decided at G3 on T0/T2 numbers, not now. The
ambition in `PRE_PROPOSAL.md` §2 — multi-sport, competing engines, accumulators,
jackpots — is unchanged and is carried by the ladder in §0, not by this decision.

**Reverse cost:** low. A positioning statement, no code.

### D-05 — The bar: the rule now, the number after T0 *(revised after the sponsor response)*

**The sponsor's condition is accepted:** no numeric bar is set before T0. Falsifiability
does not require knowing the constant in advance — it requires that the rule producing it
cannot be adjusted afterwards. So the decision is the rule; the number falls out of T0.

**Rule, pre-registered before any engine is scored:**

```
bar_A = baseline_T0  (95% interval, matched coverage)  +  delta
```

where `delta` is the smallest effect the planned sample resolves at 80% power, for a
correction family declared in advance. The bar is therefore a number with a published
lower bound, and it must be cleared on `n >= 2,000` resolved predictions of fixtures the
engine chose, at matched coverage, with:

- accuracy above the measured baseline by at least `delta`, on non-overlapping intervals
  at the stated confidence;
- calibration within ±3 percentage points across probability bins;
- significance surviving Benjamini-Hochberg correction across every engine id tested.

**Why the rule and not the constant:** this register previously imported 0.515 from
OLPRS and used it as the bar. That was wrong twice — wrong domain, and a constant fixed
before the real baseline was known. Both errors have one fix: measure first, pre-register
the rule, then compute the number so it cannot move afterwards without a recorded
sponsor decision.

**What the rule forbids:** lowering `delta` after seeing results; changing the correction
family after seeing results; reporting a subset of engines; presenting Track B evidence
(§0) as Track A evidence.

**Reverse cost:** high, deliberately. The rule is published before the first score, and
changing it is a sponsor decision recorded in `DECISIONS.md` with its reason — which is
the only honest way to change a bar.

### D-06 — Phase-one sampling frame *(revised after the sponsor response)*

**What this is not:** a scope decision. Football is the first domain in which the
instrument is calibrated, not the boundary of the project. Tennis, basketball, cricket,
accumulators and jackpots remain in the ambition and on the ladder in §0; this decision
governs only what is measured before E1.

**Default:** football only; 1X2, over/under 2.5 and both-teams-to-score; competitions
where closing prices are reliably obtainable, listed explicitly in the data
catalogue. Kenyan-accessible competitions included only if D-08 clears.

**Why:** four sports before one edge is breadth bought with attention (§5 of the
pre-proposal). The three markets chosen are the ones with the most available data and
the clearest baselines.

**A constraint that follows from D-05:** the slice cannot be one division. A single
league produces roughly one fixture a day, so ~90 resolved predictions in 90 days —
short of the bar's sample requirement by more than an order of magnitude. Reaching
n ≥ 2,000 forward means roughly twenty divisions, which changes the modelling claim
from "this works in this league" to "this generalises across leagues". Both are
defensible; picking one without noticing the other is not. Either widen the slice or
extend the horizon to a full season and say so.

**Reverse cost:** medium — collection code and schema follow the slice.

### D-07 — Accumulators and jackpots

**Default: out of scope until gate G2 passes.** Replaced by a single one-day
measurement (test T3 below), which is the part of §6 and §7 that can produce a number
now.

**Why:** §6's dependence insight is correct and important, but it is one test, not a
laboratory. Jackpot feasibility (§7) depends on whether accessible operators publish
structures and results at all — also a one-day check, not a research track.

**Reverse cost:** low now, high after any build.

### D-08 — Data sources and budget

**Default:** free-tier and published sources only in phase 1; KSh 0 for data; every
source's terms of service checked and recorded before the first automated request;
raw responses stored with a fetch timestamp and a content hash.

**Why:** §10 is right that data quality is the whole game, and §14 is right that the
budget is real. Phase 1 needs to know whether compliant closing-price access exists
at all — that is test T1 and it can kill the scope cheaply.

**Reverse cost:** low.

### D-09 — Infrastructure

**Default:** local-first. One machine, SQLite, no cloud, no services. Introduce a
hosted component only when an unattended job is proven necessary and cannot run
locally.

**Why:** ODE runs entirely on a laptop with SQLite and standard-library Python
(`ODE/README.md`), and has done since its first commit. The zero-cost cloud question
in §14 is deferred rather than answered, which is correct: it is not on the critical
path.

**Reverse cost:** low.

### D-10 — Autonomy boundary

**Default:** unattended collection and scoring allowed. No account creation, no
spending, no third-party contact, no published claim without a recorded decision. This
is the same boundary `docs/COLLAB/README.md` states for the bridge itself.

**Why:** §9's autonomy is a direction, not a permission. The boundary has to be stated
before the first scheduled job, not after.

**Reverse cost:** medium — it is a policy others will rely on.

### D-11 — Interface

**Default:** CLI plus a local dashboard on the ODE pattern (`python -m ode serve`,
port 8777). No mobile, no public web, no authentication surface.

**Reverse cost:** low.

### D-12 — Legal and responsible-gambling posture

**Default:** research-only framing in all user-facing copy; no return targets, no
"double your stake", no stake-size personas; BCLB licensing and Kenya advertising
rules documented before any public launch; the §8 profiles rewritten as decision
contexts (see CRITIQUE.md F9).

**Why:** §8 as written encodes the return targets §17 disclaims. That contradiction is
a legal exposure, not just a tone problem.

**Reverse cost:** low before launch, high after.

### D-13 — Timeline and gates

**Default:** 30/60/90-day gates, each with a pre-registered kill condition (below).
Proposal v1 drafted the day the register is answered; revised at gate G1.

**Reverse cost:** medium.

---

## 3. The one reply shape

A complete answer looks like this:

```
D-04: default
D-05: 51.5% at matched coverage, n>=2000, BH-corrected - accepted
D-06: default
D-07: default
D-08: default
D-09: default
D-10: default
D-11: default
D-12: default
D-13: default
```

or, with changes:

```
All defaults except:
D-06: include the Kenyan top flight if T1 clears it
D-09: use the existing OLPRS VM, not a laptop
```

That is the whole input. The builder drafts `PROPOSAL.md` the same day, at most six
pages: problem, bar, first slice, out of scope, kill conditions, cost model, gates.

**Silence is consent for everything except D-05.** The bar must be stated by the
sponsor, because it is the one decision that cannot be quietly revised later.

---

## 4. What happens next, in order

**Day 0 (90 minutes of sponsor time).** Answer the register.

**Day 0.** Builder drafts `PROPOSAL.md` v1 and files it as a queue row.

**Week 1–2: four tests, each ≤ 1 day, each with a pass/fail.**

| Test | Question | Pass looks like | If it fails |
| --- | --- | --- | --- |
| **T0 Baseline** | What is the real-league favourite baseline at matched coverage, from actual closing prices? | A number with an interval, computed the same way as the OLPRS measurement, on real fixtures — this replaces the imported 0.515 and sets D-05 | The bar cannot be set, so nothing can be scored, so nothing ships. This test is not optional |
| **T1 Access** | Can we obtain a season of results and closing prices, legally and free, for the D-06 slice? | A coverage table with closing prices for ≥ 80% of fixtures, and a recorded ToS verdict per source | Scope dies or D-08's budget rises — a sponsor decision, not a builder workaround |
| **T2 Baseline** | On a market *not* used in OLPRS (over/under 2.5), does anything we can build beat the measured favourite at matched coverage? | Accuracy and calibration against favourite-always, market-implied and base rate, with intervals | The board-only product (D-04a) stands alone; the research programme is re-aimed before it grows |
| **T3 Dependence** | For same-match accumulator legs, how far is realised joint frequency from the product of the marginals? | A ratio with an interval on one season of fixtures | §6 and §7 close, and the pre-proposal loses its most expensive open track |

**Day 30 — gate G1.** T1 passed and ≥ 200 predictions frozen and scored forward.
*Kill:* no compliant source of closing prices. The project does not continue to
collection engineering on data it may not use.

**Day 60 — gate G2.** T2 either produced a market-relative edge that survives
correction, or the programme formally becomes board-only and the proposal is rewritten
to say so. *Kill:* two independent attempts with no edge above the baseline. Note what
the domain change costs here: a twenty-division slice yields roughly 2,700 forward
fixtures in 90 days, enough for the bar's sample but not enough for league-level
claims, so no statement about a particular league is made from one season of forward
data.

**Day 90 — gate G3.** Proposal v2, with measured cost per resolved prediction and per
decisive experiment. Decide: build, narrow, or stop.

---

## 5. Why this is faster and not merely shorter

The pre-proposal treats research as a prerequisite for decision. That ordering has a
hidden cost: research produced *before* a commitment is not aimed at anything, so it
answers the questions that were easy to ask rather than the ones that decide. The
four tests above are cheap precisely because a decision has already been made about
what would count as failure.

It also respects the one scarce resource these three repositories share. ODE records
its cost at KSh 3–5 per investigation and concludes that "the scarce resource is your
attention, not tokens" (`ODE/README.md`). Thirteen reports is a lot of attention
spent before anything can be rejected. Ten defaults and four tests is attention spent
on the three things that can change the answer.

---

## 6. What this document does not do

It does not answer the research, and it does not replace the proposal. It makes the
proposal decidable, which is the step the project is actually stuck on. If a default
is wrong, one line in the reply fixes it — that is the point of expressing them as
defaults rather than as findings.

The one thing it cannot leave undecided is the *rule* for the bar. The number can wait
for T0 — the sponsor is right about that — but the procedure that produces it cannot
wait, because a project that has not fixed how success will be computed will report
success against whatever number it happens to reach.

## Contingency

A separate product direction is recorded in docs/PRODUCT_CONTINGENCY.md: price discovery,
slip assistance and decision support, which do not require beating the market. It is a fallback,
not a pivot, and it authorises no build.
