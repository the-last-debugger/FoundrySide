<!-- generated-by: residual_gap.py sha256=c37db913aefa -->

# Where the remaining gap sits, after forward calibration

Pilot seasons, 8,941 fixtures. Calibration is fitted forward only, so no row is scored with
a map trained on its own season or later. **Positive means the model is worse** than the market on that split; the overall gap is **+0.0178 nats**.

## Market-probability band

| Split | n | Model worse by (nats) | Cluster 95% | q |
| --- | --- | --- | --- | --- |
| 20-30% | 19 | +0.0003 | [-0.1828, +0.1516] | 0.833 |
| 30-40% | 919 | +0.0279 | [+0.0150, +0.0401] | 0.168 |
| 40-50% | 3,510 | +0.0131 | [+0.0080, +0.0197] | 0.168 |
| 50-60% | 2,902 | +0.0086 | [+0.0027, +0.0142] | 0.007 |
| 60-70% | 1,289 | +0.0241 | [+0.0137, +0.0337] | 0.258 |
| 70-80% | 279 | +0.0955 | [+0.0573, +0.1219] | 0.000 |
| 80-90% | 23 | +0.2118 | [+0.0671, +0.3824] | 0.022 |

## Division

| Split | n | Model worse by (nats) | Cluster 95% | q |
| --- | --- | --- | --- | --- |
| D1 | 897 | +0.0224 | [+0.0179, +0.0306] | 0.574 |
| E0 | 1,139 | +0.0201 | [+0.0085, +0.0362] | 0.859 |
| E1 | 1,654 | +0.0100 | [+0.0070, +0.0141] | 0.001 |
| F1 | 1,138 | +0.0226 | [+0.0146, +0.0270] | 0.574 |
| I1 | 1,140 | +0.0132 | [+0.0031, +0.0279] | 0.859 |
| N1 | 917 | +0.0205 | [+0.0117, +0.0317] | 0.859 |
| P1 | 917 | +0.0201 | [+0.0062, +0.0431] | 0.859 |
| SP1 | 1,139 | +0.0191 | [+0.0046, +0.0324] | 0.859 |

## Season

| Split | n | Model worse by (nats) | Cluster 95% | q |
| --- | --- | --- | --- | --- |
| 2021 | 2,980 | +0.0258 | [+0.0186, +0.0331] | 0.049 |
| 2122 | 2,986 | +0.0142 | [+0.0069, +0.0223] | 0.354 |
| 2223 | 2,975 | +0.0134 | [+0.0098, +0.0171] | 0.049 |

## Was a forward map available

| Split | n | Model worse by (nats) | Cluster 95% | q |
| --- | --- | --- | --- | --- |
| no (no prior season) | 2,980 | +0.0258 | [+0.0185, +0.0331] | 0.055 |
| yes | 5,961 | +0.0138 | [+0.0100, +0.0180] | 0.055 |

## Disagreement direction

| Split | n | Model worse by (nats) | Cluster 95% | q |
| --- | --- | --- | --- | --- |
| model above market | 4,172 | +0.0157 | [+0.0101, +0.0226] | 0.563 |
| model below market | 4,769 | +0.0197 | [+0.0139, +0.0265] | 0.563 |

## Disagreement magnitude (logit)

| Split | n | Model worse by (nats) | Cluster 95% | q |
| --- | --- | --- | --- | --- |
| 0.10-0.30 | 2,824 | +0.0075 | [+0.0037, +0.0120] | 0.000 |
| 0.30-0.60 | 2,882 | +0.0132 | [+0.0052, +0.0200] | 0.231 |
| <0.10 | 1,599 | +0.0039 | [-0.0003, +0.0083] | 0.000 |
| >=0.60 | 1,636 | +0.0574 | [+0.0389, +0.0799] | 0.000 |

## Reading

The first row of the calibration split explains the season split: the earliest pilot season has no
prior seasons, so no forward map could be fitted for it and it stays raw. Its larger gap is a
property of the design, not evidence that the season was harder.

The disagreement splits are the product-relevant ones. If the gap is concentrated where the model
departs from the price, then the model's independent view is the liability and nothing is gained by
trusting it further; if the gap is uniform, the model is simply a slightly worse estimate of the
same thing everywhere.

A dimension whose q column does not clear the family is indistinguishable from noise in this search,
and the interval beside each row is the honest summary of its precision.

## Limits

- Every split is a search over the same pilot, so these are descriptions of where the loss sits,
  not confirmed subgroups.
- Cluster intervals resample division-seasons; a split defined by a fixture-level quantity inherits
  the cluster structure but does not model it.
- Closing prices without timestamps; the T−90 caveat applies to any claim about what was available.
