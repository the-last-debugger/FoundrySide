<!-- generated-by: market_structure.py sha256=6b9c09ecd2f8 -->

# Market structure by division

Descriptive only. Margins and favourite accuracy are properties of the sampled
closing prices, not measures of how beatable a division is.

| Division | Fixtures | 1X2 margin | O/U 2.5 margin | O/U favourite accuracy |
| --- | --- | --- | --- | --- |
| D1 | 1,486 | 2.64% | 3.10% | 62.0% |
| E0 | 1,889 | 2.64% | 3.04% | 58.1% |
| E1 | 2,758 | 3.03% | 3.23% | 56.3% |
| F1 | 1,747 | 2.61% | 2.92% | 56.8% |
| I1 | 1,900 | 2.63% | 2.93% | 57.3% |
| N1 | 1,529 | 3.24% | 3.54% | 60.4% |
| P1 | 1,529 | 3.19% | 3.44% | 60.4% |
| SP1 | 1,897 | 2.61% | 2.99% | 60.0% |
| **pooled** | **14,735** | **2.82%** | **3.14%** | **58.6%** |

## What the numbers say

**Margins are close to uniform across these eight divisions** — 2.6% to 3.2% on 1X2
and 2.9% to 3.5% on over/under 2.5. The second tier (E1) is the widest, but by three
tenths of a point, not by an order of magnitude. On this evidence the "lower
divisions are softer" hypothesis is not supported by margin: the book takes
approximately the same everywhere in this set.

The bound matters. This says the coverage-gradient hypothesis is **unsupported by
these margin summaries in this eight-division corpus**; it does not say the hypothesis
is false. Testing it properly needs varying forecastable information, model residuals
or market-relative log loss by division — none of which this table measures. It also
cannot separate the idea from the possibility that all eight competitions are too
large to be the market the hypothesis is about.

## Limits

- The closing quote has no observation timestamp in the source, so these are the
  recorded closing prices, not prices at a known time.
- Margin is not difficulty: a low-margin market can be perfectly efficient.
- One book per market. Pinnacle closing is one opinion, chosen for availability.
- Favourite accuracy here is a descriptive split; no test of difference between
  divisions has been run, and with these sample sizes overlapping intervals are
  likely.
