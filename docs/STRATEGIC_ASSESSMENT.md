# Strategic assessment

Prepared at the sponsor's request, before any new work is authorised. This is my own judgement,
not a summary of what the sponsor suggested.

---

## 1. What I saw early, and how the evidence has treated it

My first critique argued the prediction-first thesis was unlikely to be the best product direction.
The reasons were specific, and they have fared unevenly.

**Supported.** I said the market's closing prices would be a harsh benchmark and that a model built
from results alone would struggle to beat them. That has held: 23 of 24 experiments are negative or
immaterial, and the model is worse at ranking, at probabilities *and* at the hard pick. I also said
the virtual-league 51.5% figure was the wrong baseline; it was, by two points.

**Weakened.** I argued the binding constraint was *resolution* — that the model lacked separation.
The decomposition later showed roughly half the deficit was calibration, recoverable and recovered.
I had the mechanism half right and the magnitude wrong, and I stated it too confidently.

**Weakened further.** I implied a better model family might close some of the gap. Overdispersion
was real (φ = 1.064) and correcting it was worth 0.0004 nats. The family was never the issue.

**Not supported as stated.** I expected price shopping to be a weak consolation. It measures at
~6.5% per selection — larger than I assumed. I still do not believe it implies profit, but I
under-rated the magnitude.

The honest summary: my direction was right, my reasoning was partly wrong, and the strongest result
of the programme (the disagreement pattern) is one I did not anticipate.

## 2. What FoundrySide should become

Not a prediction engine. A **market-intelligence capability**: a body of validated facts about how
sports markets are priced, how their outcomes depend on one another, how their payout structures
distribute value, and where a participant's decisions are systematically worse than they need to be.

The distinction matters commercially as well as intellectually. A prediction engine is judged by
whether it beats a price — a single, brutal test that this corpus fails. A market-intelligence
capability is judged by whether it produces knowledge that changes a decision, and it can succeed
by documenting that a market is *fair*, that a product is *worse than it looks*, or that a
shortcut people believe in is *not real*. Those are publishable, defensible and useful.

The ambition should stay wider than football: the methods here — calibration, dependence, payout
structure, decision value — transfer to any market with priced uncertainty.

## 3. Where simulations and market testing fit

Simulation is the instrument, not the product. Its job is to answer "what would this structure
pay, and to whom?" without anyone staking money. Concretely:

- **Mechanics**: how a market's overround is allocated across outcomes, and how that allocation
  shifts with favourite strength, division and book.
- **Dependence**: which legs genuinely co-move — same match, same day, same competition — and by how
  much, since every combinatorial product depends on getting this right.
- **Payout structures**: pools, jackpots and place terms, where the payoff is not a simple
  probability times a price but a share of a pool, with rollovers and dead heats.
- **Uncertainty**: what a user should believe given estimation error, not just a point estimate.
- **Decision value**: what a rational participant should do, and whether a proposed feature changes
  that action.

None of this requires beating a market. All of it requires honest measurement, which is what the
last twenty-four experiments built.

## 4. Questions worth pursuing, ranked

Ranked by expected learning per unit of cost, restricted to data already held.

| # | Question | Why it is worth it | Cost | Status of evidence |
| --- | --- | --- | --- | --- |
| 1 | **How do books allocate their margin across outcomes?** Favourite–longshot structure by division, book and season, using the 1X2, O/U and Asian handicap prices already held | Explains *where* a price is worst, which is the only actionable thing a comparison product can say; also tests whether the known bias survives in this corpus | Low — closing prices only, no new data | Plausible, untested here |
| 2 | **Dependence taxonomy**: same-match, same-day and same-competition correlation of outcomes | Every pool, slip and jackpot product depends on it; we have one number (1.49) and no structure | Low — results only | Established for same-match; unknown elsewhere |
| 3 | **Decomposing the 6.5% price improvement**: how much is genuine dispersion versus the mechanical selection effect of taking a maximum | Decides whether price shopping is a product claim or an artefact | Low — Max/Avg columns | Speculative; the artefact is plausible and unquantified |
| 4 | **Payout-structure arithmetic** for pools and jackpots: value as a function of entrants, rollover and dead heats | Pools are a different economic object from fixed-odds; nobody has calculated this here | Medium — needs published rules, which are not established | Speculation until rules are obtainable |
| 5 | **Decision-rule analysis**: what a rational participant does given prices, uncertainty and limits | Turns measurements into a normative baseline a product can be compared against | Medium — no users needed, but needs careful framing | Open |

Question 3 is the one I would do first: it is cheap, it corrects a number I already published, and
it decides whether the only positive product fact we have is real.

## 5. What to stop doing

- **Feature cycles on this corpus.** Eight variables, three mechanism classes and thirteen thin
  divisions all returned nothing. A ninth is not a plan.
- **Model-family variants.** The distributional question is settled at 0.0004 nats.
- **Confirmatory scoring of a known-losing model.** It would spend a non-renewable slice to confirm
  what the pilot already shows.
- **Claiming edge from closing prices.** No timestamp, no obtainable price, no edge claim.
- **Product builds.** No build is authorised, and nothing yet justifies one.
- **Metric proliferation.** Log loss plus calibration plus a hard-pick check answers most questions;
  more metrics mostly create opportunities to pick a favourable one.

## 6. Operating model for a continuing capability

Light, because heavy process was itself a failure mode in this project.

1. **Hypothesis register** — one active item, explicitly deferred others with activation evidence.
2. **Pre-registration before running** — question, method, leakage controls, baselines, metrics,
   stop condition. Committed first; the commit order is the proof.
3. **Bounded experiments** — small, falsifiable, reusing existing data and code.
4. **Negative findings retained** — with the same care as positives; they are the majority product.
5. **Translation gate** — a finding becomes a feature only if it changes a user's *action*; price
   quality and decision value are separate claims and must be stated separately.
6. **Artefact integrity** — every report reproducible, every claim traceable.

## Recommended smallest coherent next step

**Question 3, alone**: decompose the 6.5% price improvement into dispersion and selection effect.
It is one bounded study on data already held, it tests the only positive product fact we have, and
its outcome changes what the product could honestly claim. If the effect is mostly mechanical, the
price-comparison claim weakens — and we would know before building anything on it.

I would not start anything else until that is answered and reviewed.
