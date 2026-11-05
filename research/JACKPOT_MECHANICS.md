<!-- generated-by: jackpot_mechanics.py sha256=f8c2ebc722dd -->

# Jackpot pool mechanics

Pre-registered at `docs/PREREG-JACKPOT.md`. **This is arithmetic, not evidence.** No jackpot rules or
payout history were locatable for any operator examined, so every number below is a function of
assumed parameters. It says when a pool ticket *could* have positive expected value, and what that
depends on. It says nothing about any real product.

## The model

Pool `P = N · s · (1 − t)`. Your coverage `q`, the field's average coverage `r`. Expected winning
tickets `1 + (N − 1)·r`, counting yours. Expected net of one line:

`EV = q · P / (1 + (N − 1)·r) − s`

with `s = KSh 100`, `r = 1/1000`, and `q` set by the ratio in each column.

## Expected net per line, by takeout and field size

| Takeout | Entrants | q/r = 0.5 | q/r = 1 | q/r = 2 | q/r = 4 | Break-even q/r |
| --- | --- | --- | --- | --- | --- | --- |
| 10% | 100 | -95.9 | -91.8 | -83.6 | -67.2 | 12.2× |
| 10% | 1,000 | -77.5 | -55.0 | -10.0 | +80.1 | 2.2× |
| 10% | 10,000 | -59.1 | -18.2 | +63.7 | +227.3 | 1.2× |
| 20% | 100 | -96.4 | -92.7 | -85.4 | -70.9 | 13.7× |
| 20% | 1,000 | -80.0 | -60.0 | -20.0 | +60.1 | 2.5× |
| 20% | 10,000 | -63.6 | -27.3 | +45.5 | +190.9 | 1.4× |
| 30% | 100 | -96.8 | -93.6 | -87.3 | -74.5 | 15.7× |
| 30% | 1,000 | -82.5 | -65.0 | -30.0 | +40.1 | 2.9× |
| 30% | 10,000 | -68.2 | -36.4 | +27.3 | +154.6 | 1.6× |
| 40% | 100 | -97.3 | -94.5 | -89.1 | -78.2 | 18.3× |
| 40% | 1,000 | -85.0 | -70.0 | -40.0 | +20.1 | 3.3× |
| 40% | 10,000 | -72.7 | -45.4 | +9.1 | +118.2 | 1.8× |

## What the table says

**At the field's average coverage you lose, and a small field loses far more.** With `q = r` the
expected net tends to `-s*t` only as the field grows; at 100 entrants and a 30% takeout it
is about -94 on a stake of 100, because a single guaranteed winner dominates a small
pool. Both are the benchmark the rest of the table is read against.

**Break-even coverage falls as the field grows, towards `1/(1 − t)`.** With few entrants your line is a
large share of a small pool, so a rival line moves your expected value a lot; with many entrants the
pool and the winner count grow together and the ratio settles at the level the takeout sets:

| Takeout | Break-even `q/r` for a large field | Break-even at 100 entrants |
| --- | --- | --- |
| 10% | ≈ 1.11× | 12.2× |
| 20% | ≈ 1.25× | 13.7× |
| 30% | ≈ 1.43× | 15.7× |
| 40% | ≈ 1.67× | 18.3× |

So the honest statement is: **in a large pool you need to be modestly better than the field, and the
takeout sets how much better** — 11% better at a 10% takeout, 67% better at 40%. In a small pool you
would need to be many times better, because one rival line is a large fraction of the winners.

**The break-even column is the summary that transfers.** It converts "is this +EV?" into "how much
better than the field must I be?", which a player can reason about; a payout table without it cannot be
interpreted at all.

## Why this is not a jackpot strategy

- The parameters are a grid, not measurements. No operator's rules, pool sizes or entrant counts were
  obtainable.
- Predicting the field's coverage `r` is the hard part, and this study does not model it. A cell that
  is positive in the grid assumes you already know `r`.
- Dead heats, rollovers, consolation tiers and pool caps are not modelled; each would change the
  arithmetic.
- Nothing here is a profitability claim about any product.

## What would make this measurable

The rules document and a per-round history: entrants, pool, takeout, winners and the winning line.
With those, `r` becomes observable and the model becomes testable rather than illustrative. That is
recorded in `LEAD_TRIAGE.md` as the reopening condition.
