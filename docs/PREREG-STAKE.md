# Pre-registration — stake and multiplier structures

Written before the analysis. The question came from the sponsor's example: is KSh 100 at 3× the same
proposition as KSh 200 at 2×?

## What is actually being compared

A structure is a pair **(stake `s`, decimal odds `o`)**. Two structures are *matched on outcome* when
they return the same **net profit** `G = s(o − 1)`. The sponsor's example is exactly this:

| Structure | Stake | Odds | Gross | Net if it wins | Lost if it fails |
| --- | --- | --- | --- | --- | --- |
| A | 100 | 3.0 | 300 | +200 | −100 |
| B | 200 | 2.0 | 400 | +200 | −200 |

Same upside, different downside. So the comparison is **not** which pays more — it is what the same
upside costs in stake, probability and variance.

## Quantities, and how each is obtained

For a selection at decimal odds `o` with market-implied probability `p` (proportional de-vig of the
recorded average closing quote), and stake `s`:

| Quantity | Definition | Kind |
| --- | --- | --- |
| Hit probability | `p` from the recorded quotes | estimated (market-implied, not our forecast) |
| Realised hit rate | share of such selections that won, in the held corpus | observed |
| Net if it wins | `s(o − 1)` | hypothetical arithmetic |
| Loss if it fails | `s` | hypothetical arithmetic |
| Expected net | `p·s(o − 1) − (1 − p)s` | arithmetic on the market's own probability |
| Variance of net | `p(1 − p)(s·o)²` | arithmetic |
| Downside | `s`, the full stake | arithmetic |

**A note on expected value.** At a book's quoted price with margin `m`, `p·o = 1/(1 + m)`, so
`EV = −s·m/(1 + m)`: the expected loss is **proportional to the stake**, not to the odds. That is an
algebraic identity under proportional margin, not a discovery, and the study states it rather than
pretending to measure it.

## The comparison

Matched on net upside `G`:

1. For a grid of odds bands (≈1.5, 2.0, 3.0, 4.0, 6.0) and a fixed `G`, solve the stake each band needs.
2. For each band, report the **market-implied hit probability**, the **realised hit rate** with a
   cluster-bootstrap interval, the **stake required**, the **variance**, and the **worst case**.
3. Compare bands **at equal `G`**, not by picking a favourite.

Selections are drawn from the held corpus by de-vigged probability band, across the eight divisions and
three pilot seasons. The confirmatory slice is not read.

## What is deliberately not done

- **No assumption that equal odds imply equal risk.** Two selections at the same price differ in
  probability if the market is efficient; the study reports the market's own probability per band.
- **No cross-market pooling.** 1X2 outcomes only; over/under is not mixed in.
- **No claim that a higher multiplier is better value.** The finding, if any, is about the trade-off
  between stake at risk and probability, not about which structure is "better".
- **No profitability claim.** Every expected-net figure is negative under a quoted price with a margin;
  that is arithmetic.

## Decision rule, fixed in advance

The study reports, for each matched `G`: (a) which band has the lower stake at risk, (b) by how much
the hit probability differs, (c) whether the realised hit rates are consistent with the market-implied
probabilities, and (d) the variance ordering.

If realised hit rates in each band are consistent with market-implied probabilities, then the
structures are **equivalent in expectation after margin** and differ only in the distribution of
outcomes — which is the honest answer to the sponsor's question. If a band's realised rate departs
from its implied probability beyond the interval, that is a calibration finding and is reported as
such, with the same caution this project applies everywhere: it is evidence about the market, not an
edge.

## Stop condition

One analysis, one report, one commit. No follow-up variant without new authorisation.
