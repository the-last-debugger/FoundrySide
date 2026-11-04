<!-- generated-by: accumulator_pricing.py sha256=028a3db34e14 -->

# Accumulator pricing — is multiplying cross-match legs safe?

Pilot seasons, slips of favourite legs drawn from one division on one matchday, priced by the
product of de-vigged probabilities — exactly how a book prices an accumulator.

| Legs | Slips | Won | Multiplied probability | Realised rate | Cluster 95% | Realised ÷ multiplied |
| --- | --- | --- | --- | --- | --- | --- |
| 2 | 3,666 | 1,014 | 0.2721 | 0.2766 | [0.2523, 0.3034] | 1.016 |
| 3 | 2,041 | 290 | 0.1429 | 0.1421 | [0.1236, 0.1613] | 0.994 |
| 5 | 752 | 38 | 0.0368 | 0.0505 | [0.0382, 0.0661] | 1.373 |

## Reading

Read the Won column before the ratio. A ratio near 1 means cross-match legs multiply correctly, and
the earlier same-match dependence finding does not generalise — which is what one would expect,
since the dependence there came from legs sharing an outcome.

Two and three legs are consistent with 1: 1.016 [0.93, 1.12] and 0.994 [0.87, 1.13]. The five-leg
cell comes out above 1 at 1.373, but it rests on roughly forty winning slips, so its interval is
wide and its point estimate is not evidence that long accumulators are underpriced. It is a cell
that needs more data, not a finding.

A ratio materially below 1 would mean the multiplied probability is too high and the accumulator is
priced against the user. A ratio above 1 would mean the opposite, which would be strange for a
book-priced product and is more likely a selection effect in taking favourites.

Coverage matters here: with a favourite-only rule the naive probability is high, so slips are won
often enough to estimate the rate, unlike long-odds accumulators where the event is too rare to
observe in three seasons.

## Long combinations cannot be estimated here

| Legs | Multiplied probability | Slips for a ±10% estimate | Slips available in corpus |
| --- | --- | --- | --- |
| 3 | 0.14130 | 608 | 2,041 |
| 5 | 0.03833 | 2,509 | 752 |
| 8 | 0.00542 | 18,364 | 152 |
| 10 | 0.00147 | 67,963 | 101 |
| 12 | 0.00040 | 250,795 | 14 |

A ±10% relative estimate of an eight-leg combination needs on the order of ten thousand
slips; the corpus can form a few hundred at most, and a jackpot is longer than eight. **Jackpot
outcome rates are not estimable with this data**, and any product claim about them would have to
rest on published rules and arithmetic rather than on observed results. That is a statement about
evidence, not about jackpots being profitable or not.

## Why this matters for a slip-assistance product

A tool that shows the probability of a slip must either justify multiplication or model the
dependence. The same-match case is already known to be wrong by a factor of about 1.5; this
establishes whether the cross-match case is wrong at all, which is the case that actually appears
in a user's slip.

## Limits

- Slips are sampled from within a division on a date, not from a user's actual constraints.
- Favourite-only selections; long-odds legs have rare outcomes and cannot be estimated here.
- One book's prices, de-vigged with proportional margin removal; the margin model matters more for
  long slips than for these.
