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


---

## Programme structure — three lanes, not one

The ranked list below was restricted to data already held, which is right for choosing the cheapest
experiment and wrong as the boundary of the programme. The ambition explicitly includes football
markets, pools/jackpots and other sports, and some of that can only be *mapped* now, not tested.

| Lane | What it is | What it produces | Rule |
| --- | --- | --- | --- |
| **A. Empirical** | Bounded experiments on data already held | Validated or refuted statements about the markets we hold | One active at a time; pre-registered |
| **B. Desk discovery** | Low-cost mapping of rules, data availability, payout mechanics and testability for markets we do not hold — pools, jackpots, other sports | A feasibility record and a named data requirement, never a result | No pretence of testing what we cannot test |
| **C. Data-dependent** | Studies waiting on a lawful, affordable source | A specification ready to run when the source exists | Stays parked with its activation evidence |

Jackpots sit in B today: the rules and a per-round history were not located, so the honest product is
arithmetic disclosure and the honest next step is mapping, not measuring. That stream stays visible
rather than dropped. Nothing in lane B is a substitute for lane A, and nothing in lane C may be
described as planned work until the source exists.

Translation rule, unchanged and now explicit: a finding becomes a feature only when it is shown to
change a user's understanding or action. Descriptive and negative findings are legitimate outputs on
their own.


## 4. Questions worth pursuing, ranked

Ranked by expected learning per unit of cost, restricted to data already held.

| # | Question | Why it is worth it | Cost | Status of evidence |
| --- | --- | --- | --- | --- |
| 1 | **(A)** **How do books allocate their margin across outcomes?** Favourite–longshot structure by division, book and season, using the 1X2, O/U and Asian handicap prices already held | Explains *where* a price is worst, which is the only actionable thing a comparison product can say; also tests whether the known bias survives in this corpus | Low — closing prices only, no new data | Plausible, untested here |
| 2 | **(A)** **Dependence taxonomy**: same-match, same-day and same-competition correlation of outcomes | Every pool, slip and jackpot product depends on it; we have one number (1.49) and no structure | Low — results only | Established for same-match; unknown elsewhere |
| 3 | **(A)** **Decomposing the 6.5% price improvement**: how much is genuine dispersion versus the mechanical selection effect of taking a maximum | Decides whether price shopping is a product claim or an artefact | Low — Max/Avg columns | Speculative; the artefact is plausible and unquantified |
| 4 | **(B)** **Payout-structure arithmetic** for pools and jackpots: value as a function of entrants, rollover and dead heats | Pools are a different economic object from fixed-odds; nobody has calculated this here | Medium — needs published rules, which are not established | Speculation until rules are obtainable |
| 5 | **(A/C)** **Decision-rule analysis**: what a rational participant does given prices, uncertainty and limits | Turns measurements into a normative baseline a product can be compared against | Medium — no users needed, but needs careful framing | Open |

Question 3 is the one I would do first: it is cheap, it corrects a number I already published, and
it decides whether the only positive product fact we have is real.


---

## Specification of the proposed first experiment — the 6.5% decomposition

Authorised only to the point of method and pre-registration; not executed.

### What the 6.5% is

Across 44,406 selection-snapshots (14,802 fixtures × three 1X2 outcomes), for each *single*
selection: `g = log(best price / average price)`, where **best** is `MaxC*` (the highest closing price
the provider tracked for that outcome) and **average** is `AvgC*` (their mean). The reported 6.51% is
`exp(mean g) − 1` — the average relative improvement from taking the best of the books rather than the
market average, for one selection. Not a portfolio, not a slip, not an expected value.

### The identification problem in my first version

I proposed estimating cross-book dispersion from the two books whose prices are recorded
individually, and treating that as disagreement about the fair probability. **That was wrong.** A
bookmaker's raw price is fair probability *plus that book's margin allocation*, so the spread between
two raw prices mixes two things: genuine disagreement about the probability, and differences in how
the two books structure their margin. The two-book spread therefore does not, on its own, isolate the
quantity the study needs.

### What the available fields can identify

| Quantity | Identified? | How, or why not |
| --- | --- | --- |
| Each book's **de-vigged** probability, per selection | **Yes, assumptionally** | Proportional de-vig on one book's three-way prices. Assumes the book spreads its margin proportionally across outcomes |
| Dispersion between two books' **de-vigged** probabilities | **Yes, assumptionally** | Logit difference of the two de-vigged probabilities. Removes *margin level*; leaves any difference in margin *allocation* that proportional de-vig does not absorb, plus de-vig method error |
| Dispersion across **all K** books | **No** — projected | Only two books are recorded individually; the rest contribute only to `Max` and `Avg` |
| Separation of opinion from margin-allocation differences | **No** | Would need each book's own allocation, which the corpus does not record |
| Whether the best price is **obtainable** | **No** | No timestamps, no account or limit data |

So the honest claim structure changes: the study identifies **cross-book dispersion in de-vigged
probabilities, under a proportional-de-vig assumption**, and *projects* that to K books under an
exchangeability assumption. It does **not** measure "disagreement about the true probability", and it
must not be described as doing so.

### The comparison, restated with that limit

1. **De-vig each book separately** — Pinnacle's and Bet365's closing 1X2 prices — to probabilities per
   selection. This is the correction the review required: raw odds never enter the dispersion estimate.
2. **Pairwise dispersion** `σ₂`: the standard deviation of the logit difference between the two books'
   de-vigged probabilities, divided by √2 under an equal-variance assumption. Per division and pooled.
3. **Projected gap for K books**: `σ₂ · E[max of K standard normals]`, with `K` taken from the
   provider's own `Bb1X2` field — observed per fixture, not assumed.
4. **Observed gap**: the mean log ratio of `MaxC` to `AvgC` for the same selections.
5. **Excess = observed − projected.** That is the quantity, and it is a comparison between a measured
   quantity and a projection, not a decomposition into true components.

### Sensitivity, because the projection is an assumption

- `σ₂` varied by a factor of two in each direction, reporting how the excess moves.
- The exchangeability assumption tested where `K` varies: regress the observed gap on
  `E[max_K]`; a slope consistent with `σ₂` supports the projection, a slope far from it does not.
- Books copy each other, so independent draws overstate the projected gap; that biases the excess
  **downward**, making the test conservative in the direction of the price-shopping claim surviving.

### Decision rules, fixed in advance

| Result | Interpretation | Consequence |
| --- | --- | --- |
| Excess ≈ 0 within interval | The 6.5% is consistent with arithmetic | **Claim weakened** — present as price arithmetic, not advantage |
| Excess materially > 0 | Dispersion exceeds what the projection explains | **Claim strengthened**, still subject to availability |
| Excess < 0 | Observed gap smaller than projected | **Data-integrity signal** — check that `Max` and `Avg` cover the same book set before concluding anything |

Cluster bootstrap over division-seasons for the interval; the criterion is the interval, not the
0.01-nat scale, which is the wrong unit here.

### Why this before margin allocation

Margin allocation is descriptive: it says where a price is worst and changes no action. This decides
whether the only positive product fact is real, and therefore what the product may say. Testing the
claim before building on it is the ordering that matters.

### Limits, before the result

- Identified only under proportional de-vig, and only for two books' de-vigged probabilities.
- The K-book projection assumes exchangeability; the `K`-slope test is the check, not a proof.
- Closing prices without timestamps: a property of quotes, not of obtainable prices.
- A fact about price quality, never about profit.

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
