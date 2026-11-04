# Product direction — independent assessment

Requested before further research. This is my judgement; where I disagree with the framing I say so.

---

## 1. Do these three experiences make sense as the core structure?

**Partly.** They are not three products. They are **one engine with three views**, and treating them as
peers will cause duplication and inconsistent claims.

The thing they share is the hard part and it is already most of the work: estimate a probability,
compare it against an obtainable price, quantify uncertainty, and decide whether to speak. A
standalone assessment is that engine on one selection. A slip is the same engine over a joint
distribution. A jackpot is the same engine with a pool-based payoff instead of a fixed price.

What differs is only the **payoff structure** and the **dependence structure**. Two axes, not three
products:

| | Independent legs | Dependent legs |
| --- | --- | --- |
| **Fixed price** | standalone selection | same-match slips |
| **Pool payoff** | not meaningful | jackpots, pools |

So I would keep the three *experiences* — users recognise them — but build **one engine** and derive
the views. The failure mode to avoid is three code paths that compute the same probability three
ways and disagree on screen.

## 2. What I would retain, change, combine, postpone

**Retain**: the abstention principle, stated explicitly in the sponsor's list and the most important
line in it. A system that says "no recommendation" is more honest than one that always answers, and
it is the only defence against manufacturing confidence.

**Change the word "recommendation".** It implies an edge. What the evidence supports is an
**assessment** with an explicit action: act, abstain, or "the price is better than average here".
Calling a price improvement a recommendation will lead users to read edge into arithmetic. I would
label every output by the *kind of claim* it makes, and never merge the kinds into one score:

| Claim kind | What it says | What it needs | Status |
| --- | --- | --- | --- |
| **Price** | "the same selection is available at a better price elsewhere" | multiple books, timestamps | partially supported |
| **Probability** | "our estimate differs from the price" | a forecast that beats the market | **not supported** |
| **Risk** | "this combination is more correlated than multiplication implies" | dependence model | supported in part |
| **Payout** | "here is what this structure pays, and to whom" | rules, pool mechanics | blocked |

**Combine** standalone and slip: a slip is a selection with a joint distribution. One evaluation
path, two presentations.

**Postpone** jackpots as a *product* while keeping them as a discovery stream. Without published
rules and a per-round history, any jackpot feature would be arithmetic on invented parameters.

**Add** a fourth view that is cheap and defensible and missing from the sponsor's list: **"what the
price implies"** — the de-vigged probability, its uncertainty, and the margin being paid. It needs no
edge, no timestamp, and no data we do not have, and it is the honest core of a market-intelligence
product.

## 3. Evidence and capabilities needed per experience

| Experience | Needed capability | Needed evidence | Have it? |
| --- | --- | --- | --- |
| Standalone — price | multi-book snapshot, matching selections | dispersion and its decomposition | **partly** — closing only, the 6.5% is unexplained |
| Standalone — probability | forecast better than the price | 0.01-nat edge on held-out seasons | **no** — 23 experiments say so |
| Slip — dependence | joint model over legs | same-match dependence measured; cross-match approximated | **mostly** — 1.49 same-match, ~1.0 cross-match |
| Slip — risk | joint probability + variance of payout | same, plus stake rules | **mostly** |
| Jackpot — payout | pool rules, rollover, dead heats | published rules + per-round history | **no** |
| All — uncertainty | calibration and intervals | forward calibration works (+0.0102) | **yes** |

The column that matters: **probability-based selection has no supporting evidence, and it is the only
one of the four whose absence cannot be fixed by better engineering.** It is fixed by information we
do not have.

## 4. What can be useful now, what needs data, what must stay unavailable

**Useful now, with existing evidence:**
- Price comparison, presented as *price*, with the selection-effect caveat.
- Dependence disclosure: "these legs are more correlated than multiplication assumes" — we have the
  number (1.49) and the method.
- Abstention and uncertainty display, on the back of forward-calibrated probabilities.
- "What the price implies" — margin, de-vigged probability, uncertainty.

**Needs new lawful data:**
- Any statement about *obtainable* prices (timestamps).
- Pools and jackpots (rules, histories).
- Any multi-sport claim.

**Must remain explicitly unavailable until validated:**
- **Any probability-based pick presented as an edge.** We have measured that our forecasts are worse
  than the price on every axis tested; to present one as a recommendation would be to contradict our
  own evidence.
- Jackpot coverage optimisation.
- Any expected-value or profitability claim.

## 5. How to distinguish the four claim kinds

By **what is being asserted**, not by how confident it looks:

- *Price* claims are about **availability of a better quote**, and are true or false about the
  market, not about the outcome. They never use the word "value".
- *Probability* claims are about **the event**, and require a forecast with demonstrated skill.
- *Risk* claims are about **the joint distribution**, and require a dependence model with a stated
  error.
- *Payout* claims are about **the structure**, and require rules.

A screen that shows a price improvement beside a probability estimate beside a payout projection,
without labelling which is which, will be read as one combined recommendation. That is the single
biggest product risk in this direction.

## 6. What the product should do when evidence is weak

It should **abstain, and say why**, in one sentence, with the specific gap named:

- "No price available for this selection at the time you acted." (stale data)
- "This combination's dependence is measured; the price is not."
- "Our estimate is not better than the price — we are showing you the price." (no edge)
- "The best available price is still worse than fair; this is a poor value bet." (honest negative)

The last one matters: the product must be willing to say **"do not bet this"**, and to say it when
the best price is still bad. That is the behaviour that distinguishes an intelligence tool from a
tipping service.

## 7. Does this change my ranking, and what is the smallest first activity?

**It sharpens it rather than changing it.**

The product direction makes the **price claim** load-bearing: experience 1 rests on it, and the whole
"better price, not edge" framing rests on it. That is exactly what the **6.5% decomposition** tests.
So it stays first — and the product framing raises its stakes, because if the 6.5% is mechanical, the
product's headline claim changes from "we find you a better price" to "we show you the price and the
margin".

The direction also **promotes** the dependence work: it is the only capability where our evidence is
positive (same-match 1.49, cross-match ≈ 1.0) and where most competing tools are simply wrong. I
would move it from rank 2 to the clear second activity, and scope it as a **joint-probability
calculator** rather than a model of matchups.

**Smallest coherent first activity: the 6.5% decomposition, unchanged.** One bounded study, data in
hand, corrects a published number, and decides what the product may say. The dependence calculator
follows as the second, and it is already half-built from the accumulator study.

## What I would refuse to build, for the record

A probability-based recommendation surface. Not because it is hard, but because we have measured
that it would be worse than the market, and shipping it would make the product's central claim
false. If that changes, it changes because new information arrives — not because a product plan
asserts it.
