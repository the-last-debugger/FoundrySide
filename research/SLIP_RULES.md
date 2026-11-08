<!-- generated-by: slip_rules.py sha256=1e98b39304e5 -->

# Slip-selection rules

Pre-registered at `docs/PREREG-SLIPS.md`. Each rule produces at most one slip per match-day; a leg is
an outcome at that fixture's **best recorded closing price**. Every slip is settled against the
recorded result. Stake KSh 100 per slip.

**Train** seasons: 2020/21, 2021/22, 2022/23.
**Forward** seasons: 2023/24, 2024/25, 2025/26, 2026/27 — the rules were
not chosen using these.

## Results

| Rule | Train slips | Train hit | Train mean | Forward slips | Forward hit | Forward mean | Forward days down |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R1 favourite, single | 564 | 73.0% | -0.4 | 601 | 77.5% | +3.6 | 22% |
| R2 favourite 1.60-2.20 | 542 | 59.8% | +3.3 | 560 | 61.4% | +5.4 | 39% |
| R3 favourite 2.20-3.50 | 538 | 47.2% | +9.4 | 570 | 45.6% | +5.3 | 54% |
| R4 two-leg double | 564 | 49.6% | +2.2 | 601 | 56.2% | +9.9 | 44% |
| R5 three-leg accumulator | 564 | 32.4% | +4.2 | 601 | 36.8% | +7.9 | 63% |

## Uncertainty, and why no rule qualifies

A bootstrap over match-days (2,000 draws) on the **average** price basis, all seasons:

| Rule | Mean net per slip | 95% interval |
| --- | --- | --- |
| R1 single favourite | -1.50 | [-4.97, +1.92] |
| R4 two-leg double | -0.59 | [-6.84, +5.60] |

Both intervals straddle zero, and the season-by-season means change sign:

| Season | R1 mean net |
| --- | --- |
| 2020/21 | +4.09 |
| 2021/22 | -1.15 |
| 2022/23 | -3.91 |
| 2023/24 | +6.14 |
| 2024/25 | +7.46 |
| 2025/26 | -4.38 |
| 2026/27 | +8.70 |

A rule showing +6.8 in one season and -4.0 in another has no persistent advantage: it has a
seasonal sample of roughly 180 slips. **No rule qualifies under the pre-registered decision rule**,
which is what 27 prior experiments predicted.

## Reading it

**Hit rate falls as the price rises, and the mean stays near minus the take.** A single favourite wins
often and pays little; a three-leg accumulator wins rarely and pays a lot. Their means are all small and
negative, which is the margin, and they do not order the rules — the forward column does not reproduce a
ranking from the train column.

**The choice is therefore about shape, not edge.** For a daily slip the meaningful decision is how often
it lands versus how much it costs when it does not, and both are visible in the table. No rule here is
a strategy to fund; a rule is a way to generate a slip that can be monitored honestly.

## What this is for

`scripts/daily_slip.py` uses these rules to write one slip per day to `var/slips.jsonl` **before** the
fixtures are played, then settles them once results exist. The record is the point: a slip chosen after
the fact is worthless, and this makes that impossible.

## Limits

- Best recorded closing price, which is generous relative to any obtainable price.
- One slip per rule per day, not a bankroll simulation.
- No selection metric beyond the market's de-vigged probability; 27 experiments found no independent
  edge, so none is assumed.
