# How to settle the proposal this week

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

## 1. The three questions

Only three things actually block a proposal. Everything else in the pre-proposal is
either downstream of them or cheap to reverse later.

**Q1 — What is the product?**
A board that restates the market's view, with abstention discipline, is supportable
today from evidence in this sponsor's own repositories. An independent model that
beats that board at matched coverage is not supported by anything yet. Which one is
being proposed changes the first ninety days completely.

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

### D-04 — Product thesis

**Options:** (a) market-restatement board with abstention discipline; (b) independent
model that must beat a market baseline to ship; (c) research instrument with no user
product.

**Default: (a) as the product, (b) as the research programme.** The evidence supports
(a) now — the market pick reaches 61.1% accuracy at 12.2% coverage on 12,595 priced
fixtures (`OLPRS_v2/docs/USER_ADVANTAGE_2026-10-31.md`). Nothing in either repository
supports (b) yet, including on 10,329 signals where the answer was 45.6% against the
market's 45.9%.

**Why this default:** it lets the project ship something honest on day one while the
research programme attempts the harder claim. It also makes the programme's failure
non-fatal: a null result on (b) leaves a working board, not an empty repository.

**Reverse cost:** low. A positioning statement, no code.

### D-05 — The bar *(must be answered explicitly)*

**Options:** any numeric threshold for a claim of edge.

**Default recommendation:** a model may be described as predictive only if, on
fixtures it chose, at matched coverage, it beats the favourite baseline — 1X2 accuracy
of **≥ 51.5%** — on **n ≥ 2,000** resolved predictions, with calibration within ±3
percentage points, and significance surviving Benjamini-Hochberg correction across all
engine ids tested.

**Why this number:** 0.515 is the measured favourite baseline on 16,831 fixtures at
matched coverage (`USER_ADVANTAGE`). It is the honest bar because it is the thing a
user can do without the system. The correction requirement comes from the same body
of work: 27 signal ids produced raw edges up to +12.7 points, and none survived
correction (`SIGNAL_MARKET_VERDICT`). The sample size is what makes the interval
narrow enough to be worth quoting.

**Reverse cost:** high. Once a bar is published, lowering it is the failure mode the
whole repository exists to prevent. This is why it is the one item that cannot be
defaulted.

### D-06 — First slice

**Default:** football only; 1X2, over/under 2.5 and both-teams-to-score; competitions
where closing prices are reliably obtainable, listed explicitly in the data
catalogue. Kenyan-accessible competitions included only if D-08 clears.

**Why:** four sports before one edge is breadth bought with attention (§5 of the
pre-proposal). The three markets chosen are the ones with the most available data and
the clearest baselines.

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

**Week 1–2: three tests, each ≤ 1 day, each with a pass/fail.**

| Test | Question | Pass looks like | If it fails |
| --- | --- | --- | --- |
| **T1 Access** | Can we obtain a season of results and closing prices, legally and free, for the D-06 slice? | A coverage table with closing prices for ≥ 80% of fixtures, and a recorded ToS verdict per source | Scope dies or D-08's budget rises — a sponsor decision, not a builder workaround |
| **T2 Baseline** | On a market *not* used in OLPRS (over/under 2.5), does anything we can build beat the favourite at matched coverage? | Accuracy and calibration against favourite-always, market-implied and base rate, with intervals | The board-only product (D-04a) stands alone; the research programme is re-aimed before it grows |
| **T3 Dependence** | For same-match accumulator legs, how far is realised joint frequency from the product of the marginals? | A ratio with an interval on one season of fixtures | §6 and §7 close, and the pre-proposal loses its most expensive open track |

**Day 30 — gate G1.** T1 passed and ≥ 200 predictions frozen and scored forward.
*Kill:* no compliant source of closing prices. The project does not continue to
collection engineering on data it may not use.

**Day 60 — gate G2.** T2 either produced a market-relative edge that survives
correction, or the programme formally becomes board-only and the proposal is rewritten
to say so. *Kill:* two independent attempts with no edge above the baseline.

**Day 90 — gate G3.** Proposal v2, with measured cost per resolved prediction and per
decisive experiment. Decide: build, narrow, or stop.

---

## 5. Why this is faster and not merely shorter

The pre-proposal treats research as a prerequisite for decision. That ordering has a
hidden cost: research produced *before* a commitment is not aimed at anything, so it
answers the questions that were easy to ask rather than the ones that decide. The
three tests above are cheap precisely because a decision has already been made about
what would count as failure.

It also respects the one scarce resource these three repositories share. ODE records
its cost at KSh 3–5 per investigation and concludes that "the scarce resource is your
attention, not tokens" (`ODE/README.md`). Thirteen reports is a lot of attention
spent before anything can be rejected. Ten defaults and three tests is attention spent
on the three things that can change the answer.

---

## 6. What this document does not do

It does not answer the research, and it does not replace the proposal. It makes the
proposal decidable, which is the step the project is actually stuck on. If a default
is wrong, one line in the reply fixes it — that is the point of expressing them as
defaults rather than as findings.

The one thing it cannot default is the bar. A project that has not decided what
counts as success will report success.
