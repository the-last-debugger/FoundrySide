<!-- generated-by: stake_structures.py sha256=3b16c4d59c08 -->

# Stake and multiplier structures

Pre-registered at `docs/PREREG-STAKE.md` before the run. The sponsor's question: is KSh 100 at 3x the
same proposition as KSh 200 at 2x?

Both return the same **net profit** if they win. They differ in what is at risk, how often they win,
and how widely outcomes vary. This report measures that trade-off on the held corpus, using the
recorded market-average closing prices, de-vigged proportionally.

Average closing margin across the corpus: **0.0484**. Selections available: **44,406**
outcome-quotes from 14,802 fixtures.

## The identity that fixes the expected value

At a quoted price with proportional margin `m`, the market-implied probability satisfies
`p · odds = 1/(1+m)`, so the expected net is

`EV = p·s(odds − 1) − (1 − p)s = −s · m/(1 + m)`

That is **proportional to the stake, not to the odds**. Two structures with the same stake have the
same expected loss regardless of price; two structures matched on net upside have expected losses in
proportion to their stakes. This is algebra under the margin assumption, not a measurement.

## Matched on a net upside of KSh 200

| Odds band | Selections | Median price | Stake needed | Lost if it fails | Mean implied | Implied at median | Realised hit (95% cluster) | Realised EV at median |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1.4–1.7 | 2,893 | 1.56 | KSh 357 | KSh 357 | 61.5% | 61.1% | 63.3% [61.5, 65.5] | -1.27% |
| 1.8–2.2 | 4,205 | 2.01 | KSh 198 | KSh 198 | 47.8% | 47.5% | 48.4% [46.7, 49.8] | -2.73% |
| 2.7–3.3 | 7,958 | 3.09 | KSh 96 | KSh 96 | 31.2% | 30.9% | 30.6% [29.6, 31.6] | -5.53% |
| 3.6–4.4 | 7,007 | 3.89 | KSh 69 | KSh 69 | 24.4% | 24.5% | 23.5% [22.7, 24.5] | -8.40% |
| 5.4–6.6 | 2,181 | 5.90 | KSh 41 | KSh 41 | 16.1% | 16.2% | 15.5% [13.8, 16.9] | -8.29% |

Reading the table: to make the same KSh 200 net, a 1.5 shot needs a **large** stake and a
6 shot needs a **small** one. The probability of winning falls as the stake falls, roughly in step.
The expected loss, being stake-proportional, falls with the stake.

## Variance

| Odds band | Variance of net result |
| --- | --- |
| 1.4–1.7 | 73,748 |
| 1.8–2.2 | 39,502 |
| 2.7–3.3 | 18,658 |
| 3.6–4.4 | 13,413 |
| 5.4–6.6 | 7,860 |

Variance grows with the gross return, so the low-odds structure has the smaller variance for the same
net upside — at the cost of a much larger stake at risk.

## Do the realised rates match the market's probabilities?

- **1.4–1.7**: mean implied 61.5%, realised 63.3%, interval [61.5, 65.5] — **outside** the interval: a calibration departure, not an edge.
- **1.8–2.2**: mean implied 47.8%, realised 48.4%, interval [46.7, 49.8] — consistent with the mean implied probability.
- **2.7–3.3**: mean implied 31.2%, realised 30.6%, interval [29.6, 31.6] — consistent with the mean implied probability.
- **3.6–4.4**: mean implied 24.4%, realised 23.5%, interval [22.7, 24.5] — consistent with the mean implied probability.
- **5.4–6.6**: mean implied 16.1%, realised 15.5%, interval [13.8, 16.9] — consistent with the mean implied probability.

### What the realised-EV column says

`realised hit x median price - 1` is what a flat-stake backer would have earned in each band, before
stake limits and with no price shopping. Every band is **negative**, including the short one where the
realised rate runs above the mean implied probability. Each figure is computed from that band's own
median price and its own realised rate, and printed with the price it used, so the two cannot drift
apart:

- **1.4–1.7**: median price 1.56, realised 63.29%, EV -1.27%
- **1.8–2.2**: median price 2.01, realised 48.39%, EV -2.73%
- **2.7–3.3**: median price 3.09, realised 30.57%, EV -5.53%
- **3.6–4.4**: median price 3.89, realised 23.55%, EV -8.40%
- **5.4–6.6**: median price 5.90, realised 15.54%, EV -8.29%

A calibration pattern that does not survive its own margin is not an opportunity, and here the margin
is larger than the departure.

## The answer to the question

**They are not the same proposition, and neither is better.** For the same net upside:

- the **higher-odds** structure risks **less money**, wins **less often**, and has a **smaller absolute
  expected loss**;
- the **lower-odds** structure risks **more money**, wins **more often**, and has **smaller variance**
  in the outcome for the same upside — but a larger downside in absolute terms.

There is one asymmetry in the data worth naming: short prices won slightly **more** often than
their de-vigged probability implied, the direction of the classic favourite-longshot bias, while the
high-price bands ran slightly below. The departure is small, sits at the edge of the interval, and does
not survive the margin - so it is a fact about market calibration, not a reason to prefer one structure.

That is a preference over distributions, not a valuation. Anyone claiming one is "better value" is
either assuming a risk preference or ignoring the margin.

## Limits

- Market-implied probabilities under proportional de-vig; not our forecasts.
- Stake arithmetic ignores limits, rounding, account terms and whether the price is obtainable — the
  corpus has no timestamps.
- Selections are grouped by price band, so a band mixes fixtures of very different kinds; the
  intervals account for division-season clustering, not for that heterogeneity.
- No profitability claim: every expected net here is negative by the margin.
