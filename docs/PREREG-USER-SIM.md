# Pre-registration — what a user with KSh 100–300 would have done

Written before the run. The question came from a direct challenge: if the product had been launched
today and used with a small stake, what would it have cost? The honest answer has two halves: what is
arithmetically certain, and what the corpus can show.

## What cannot be answered

**Nothing in this corpus is from today.** The data runs from 2021-01-01 to 2023-12-31. Any statement
about 2026-11-07 would be invented, so none is made. The simulation uses the held fixtures and says so.

## What is asked

For a budget of KSh 100 to 300, and for each way a user could deploy it through the product, what is the
distribution of outcomes over historical match-days?

## Archetypes — the full set of ways to spend the budget

Every combination the product can suggest, and one it should:

| # | Archetype | Behaviour | Stake |
| --- | --- | --- | --- |
| A1 | Single favourite | Back the most likely outcome at the best recorded price | 100 |
| A2 | Single favourite, full budget | Same, at the whole 300 | 300 |
| A3 | Split three ways | Three favourites, one per fixture, on one day | 3 × 100 |
| A4 | Target multiplier, single | The single closest to 3× | 100 |
| A5 | Target multiplier, double | Two legs closest to 6× | 100 |
| A6 | Accumulator, three legs | Three favourites across matches, one slip | 100 |
| A7 | Abstain | The product says no recommendation | 0 |

A7 is included deliberately: an empty day is a real outcome the product is allowed to produce, and it
costs nothing.

## Method

- Group the corpus by match date; each date with at least three fixtures is one simulated day.
- Settle every bet against the recorded result. Use the best recorded closing price, which is generous
  to the user: no real account is guaranteed to have it.
- Report per archetype: mean net, median, 5th and 95th percentiles, worst and best day, probability of
  ending the day down, and probability of losing the whole stake.

## What is fixed in advance

- **Stake sizes**: 100 and 300, as stated by the user.
- **Archetypes**: the seven above, chosen before seeing results.
- **Baseline check**: the mean net per archetype must be close to the margin identity
  `−stake × m/(1+m)`, since that is what a quoted price implies. A large divergence would mean the
  simulation is wrong, not that the market is beatable.

## What this cannot establish

- That any specific day would have gone a specific way. It is a distribution, not a prediction.
- Anything about today, or about a price a user could actually obtain.
- That abstaining is always better; on many single days it is, but that is variance, not an edge.

## Stop condition

One analysis, one report, one commit.
