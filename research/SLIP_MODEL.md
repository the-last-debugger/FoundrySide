<!-- generated-by: slip_model.py sha256=8fe29b4d3805 -->

# Can a model predict slip success better than the market's product?

Pre-registered at `docs/PREREG-SLIP-MODEL.md`. Slips are built greedily from a match-day's fixtures
until the combined price reaches each multiplier target, then settled against recorded results.

Fitted on seasons up to 2022/23 (3,384 slips), scored on
later seasons (3,606 slips).

## The model

`p = sigmoid(a + b·logit(∏ implied) + c·(legs − 1))`

Three parameters. The baseline is `∏ implied`, which is what multiplying the market's probabilities
gives you.

## Out of time

| | Baseline (market product) | Fitted model |
| --- | --- | --- |
| Log loss | 0.5072 → **0.4870** | 0.5001 → **0.4857** |
| Brier | 0.1657 → 0.1614 | 0.1645 → 0.1604 |
| Calibration slope (test) | — | 0.192 |

The first number in each cell is training, the second is the held-out seasons.

## Realised versus implied, by multiplier

| Target | Slips (test) | Mean implied | Realised |
| --- | --- | --- | --- |
| 1.5× | 601 | 51.8% | 57.9% |
| 2.0× | 601 | 36.7% | 44.4% |
| 3.0× | 601 | 23.7% | 30.6% |
| 5.0× | 601 | 13.7% | 17.0% |
| 10.0× | 601 | 7.4% | 8.7% |
| 20.0× | 601 | 4.7% | 5.2% |

## Verdict

The fitted model does **not** justify replacing the market product out of time. It moves log loss by +0.0013 nats, which is within noise, and its calibration slope is 0.19 rather than near 1, so its probabilities are the wrong shape even where the loss improves. The planner therefore shows the product of the implied probabilities and does not dress it as a model.

A calibration slope near 1 means the fitted probabilities are the right shape; far from 1 means they
are over- or under-confident even where the loss improves.

## Limits

- Three features. A richer model could do better, but 28 experiments give no reason to expect so.
- The greedy construction is one of many; different slips at the same multiplier differ in shape.
- Best recorded prices, so the implied probabilities are optimistic for a real user.
- One draw per match-day per target; season-level correlation is not modelled.
