<!-- generated-by: user_simulation.py sha256=6196600b924b -->

# What a user with KSh 100–300 would have done

Pre-registered at `docs/PREREG-USER-SIM.md`. **Retrospective**, over 930 historical match-days
in the held corpus. The corpus runs from January 2021 to December 2023, so this says nothing about
today; there is no data for today and none was invented.

Mean closing margin across the corpus: **0.0484**.

## Two prices, two answers

The arithmetic is unambiguous: at a quoted price, expected net is `-s * m/(1+m)`, which on KSh 100 is
**KSh -4.62**. But a backtest has to choose *which* price the user gets, and the
corpus records both an average and a maximum across books. That choice changes the sign:

| Price used | Mean net per KSh 100 | What it means |
| --- | --- | --- |
| Average closing price (A8) | **-0.20** | Roughly break-even |
| Best recorded closing price (A1) | **+4.11** | Looks profitable, and is not attainable |

The gap between those two is the selection effect measured in E20: the maximum of several noisy quotes
sits above the average by construction, and a backtest that always assumes the maximum is measuring an
artefact. **The honest expectation is the average-price row**, and even that is only about break-even
because favourites in this corpus won slightly more often than their de-vigged probability implied —
the same small departure E25 found at short prices. It is a calibration fact, not an edge, and it is
too small to survive a worse price or a limit.

## Every way to spend the budget

| | Archetype | Budget | Mean net | Median | 5th … 95th | Days ending down | Days losing the lot |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A1 | Single favourite | KSh 100 | +4.1 | +24.5 | -100.0 … +156.0 | 45% | 45% |
| A2 | Single favourite, full budget | KSh 300 | +12.3 | +73.5 | -300.0 … +468.0 | 45% | 45% |
| A3 | Split three ways | KSh 300 | +4.6 | -5.5 | -300.0 … +309.0 | 51% | 10% |
| A4 | Target 3x, single | KSh 100 | +6.3 | -100.0 | -100.0 … +190.0 | 62% | 62% |
| A5 | Target 6x, double | KSh 100 | +13.9 | -100.0 | -100.0 … +500.8 | 81% | 81% |
| A6 | Accumulator, three legs | KSh 100 | +4.4 | -100.0 | -100.0 … +661.1 | 85% | 85% |
| A7 | Abstain | KSh 0 | +0.0 | +0.0 | +0.0 … +0.0 | 0% | 100% |
| A8 | Single favourite, average price | KSh 100 | -0.2 | +20.5 | -100.0 … +145.0 | 45% | 45% |

Days where the archetype could not be constructed: A4 474, A5 9 (the corpus
does not offer that price that day, so the search correctly found nothing).

## What this says

**The mean is small and the variance is not.** A single favourite bet on one day ends down about
45% of the time, losing the whole
KSh 100, and wins a few tens the rest. The average is close to zero; a single day is mostly noise.

**Higher multipliers convert a small mean into a large occasional swing.** The 6× double ends down on
81% of days, and the three-leg
accumulator on 85%. Their means
are flattered by rare large wins; the shape of the distribution is what a user feels.

**Abstaining is the only archetype with no downside**, which is why the product is allowed to say it.

## What this does not say

- Nothing about today. The last fixture in the corpus is from 2023.
- Nothing about obtainable prices: even the average-price row assumes a book at the market average.
- Nothing about a strategy: these are single-day draws, and the corpus cannot tell you whether the next
  draw is favourable.

## The answer, in one line

On a KSh 100–300 budget for one day, the expected loss at a price you could plausibly get is
**about KSh 0–5**, but the day ends down roughly **45% of the time on a single favourite and 80%+ on
anything ambitious** — and the ambitious structures are where the money actually goes.
