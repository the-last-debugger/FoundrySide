# Product contingency — price discovery and decision assistance

**Status: recorded as a fallback, not a pivot.** The research programme continues unchanged.
Nothing here authorises a build, an integration, an account, a paid API, hosting, deployment or
any real-money functionality. This exists so that a genuine dead end does not leave the project
without a direction, and so that the direction is defined before it is needed.

## The distinction the product lives or dies on

**Best available price** is not **positive expected value**. A better price improves a user's
position; it does not make a selection profitable. Everything below is written to keep those two
apart, because a price-comparison product that blurs them would be misrepresenting arithmetic to
its users.

The corpus already shows how large the gap is. Across 8,938 pilot fixtures with two books'
closing over/under 2.5 prices (`research/BEST_PRICE.md`):

| | |
| --- | --- |
| Fixtures where the two books differ | 93.1% |
| Overround at one book | 3.08% |
| Overround at the better of the two | 2.91% |
| Margin saved by always taking the best price | **0.17 pp** [0.14, 0.20] |
| Fixtures still negative expected value at the best price | **99.1%** |

So price discovery is worth about 0.17 percentage points of margin — real, small, and nowhere near
turning a losing bet into a winning one.

## What the existing research already says about each capability

| Capability | Existing evidence | What it implies |
| --- | --- | --- |
| **1. Best-price discovery** | `BEST_PRICE.md`: 0.17 pp saved, 99.1% still negative | The value is real but bounded; the product must present it as margin reduction, never as edge |
| **2. Slip assistance** | `RESULTS_T0_T1_T3.md`: same-match legs are dependent, realised joint 40.9% vs 27.5% product, ratio 1.49 | Any combinatorial slip tool that multiplies probabilities is wrong by a factor of ~1.5 on the same match; dependence must be modelled or disclosed |
| **3. Profit/loss projection** | `CALIBRATION_STUDY.md`: probabilities can be made calibrated out of fold | Projections can be built on calibrated numbers rather than raw model output; they must show gross vs net and never present a payout as expected |
| **4. Jackpot assistance** | dependence evidence above; `GAP_DIAGNOSIS.md` on where models lose resolution | Multi-event jackpots compound the dependence problem; the honest contribution is probability disclosure, not selection |
| **5. Multi-platform data** | `DATA_LANDSCAPE.md`: two books are freely available; every other source examined is gated or licence-restricted | Aggregation beyond these two books requires paid or permissioned access — an approval boundary |
| **6. UI/UX** | none | Not a research question; cannot be validated with this corpus |

## What additional evidence each capability needs before it could be called useful

None of these can be established with the current data, and feature availability is not evidence of
benefit. Each needs an experiment of its own:

1. **Best-price discovery** — **blocked on access, investigated in docs/SOURCE_TIMING.md**: no
   route found that is free, lawful, timestamped and reachable here. The cheapest unblock is
   retrying the Wayback index from a network where it resolves; then a free-tier API, which needs
   a sponsor decision because registration is an approval boundary.
2. **Slip assistance** — a dependence-aware pricing model validated out of sample, and evidence
   that users make better slip decisions with it. The current corpus can supply the first, not the
   second.
3. **Projection tools** — usability evidence that disclosed assumptions change decisions for the
   better, and that no wording induces loss-chasing. This is a behaviour study, not an analysis.
4. **Jackpot assistance** — **blocked**, recorded in docs/JACKPOT_FEASIBILITY.md: press coverage
   exists, a structured history of rounds does not in any form located, and operator terms were
   not examined under this authorisation. The honest interim product is arithmetic disclosure.
5. **Multi-platform aggregation** — licence review and costed access for each provider, with
   latency and coverage measured. Currently blocked by the zero-cost boundary, not by technique.

## Why this is not authorised now

- The evidence above is thin precisely where a product needs it: availability in time, and user
  behaviour.
- Building would require paid or permissioned data access, and any public-facing or real-money
  functionality requires legal and regulatory work that is not in scope.
- The research programme has not reached a dead end: it has reached the edge of what this corpus
  can tell us, which is a different and narrower statement.

## What would trigger the pivot

Any **two** of the following, on evidence:

1. a sponsor decision that new information sources are unavailable or unaffordable, closing
   Track A;
2. a measured user benefit from price comparison or decision support in a controlled study;
3. lawful, affordable access to a timestamped multi-book feed.

Until then this stays on the ladder as a recorded option, and the research continues as it is.
