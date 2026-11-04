<!-- generated-by: model_family.py sha256=018ab6fe6ccc -->

# Is the low resolution a functional-form problem?

Pilot seasons only. The question is whether replacing independent Poisson goals with an
overdispersed total improves the model's forecasts against the unchanged market comparator.

## 1. Is there overdispersion?

| Quantity | Value |
| --- | --- |
| Matches | 8,941 |
| Mean total goals | 2.710 |
| Variance of total goals | 2.751 |
| Variance ÷ mean | 1.015 |
| Implied negative-binomial dispersion | 177.59 |
| Conditional Pearson dispersion (against model means) | 1.064 [1.032, 1.094] |
| Matches contributing | 8,941 |

Poisson requires the ratio to be 1. The **pooled** ratio is 1.015, which
looks indistinguishable from 1. That is misleading: each match has a different conditional mean,
so the pooled ratio mixes real heterogeneity in the means with the variance around them.

The conditional test is the right one, and it disagrees. Against the model's own match-specific
means, the Pearson dispersion is **1.064 [1.032, 1.094]** over 8,941
matches — mildly but significantly overdispersed, about six per cent excess variance. The
independent-Poisson form *is* mildly misspecified, and the pooled statistic hid it.

## 2. Does the better family fit the marginal distribution better?

| Quantity | Poisson | Negative binomial | Empirical |
| --- | --- | --- | --- |
| P(over 2.5) at the mean | 0.5088 | 0.5075 | 0.5068 |

## 3. Does it improve the forecasts?

| Forecast | Log loss | Brier |
| --- | --- | --- |
| Independent Poisson | 0.6988 | 0.2520 |
| Negative-binomial total | 0.6984 | 0.2519 |
| Market (closing) | 0.6742 | 0.2407 |

## Reading

The specification is mildly wrong, and correcting it is worth almost nothing. Overdispersion is
real at 1.064, but the negative binomial changes log loss by +0.00043
nats against a 0.0246 deficit. Both statements are true and the second is the one that matters:
a misspecified model can still be the best available one, and here fixing the distribution does
not fix the forecast. If the negative binomial does not beat Poisson out of sample,
the specification was not the binding constraint, and the model's resolution deficit is
informational rather than structural. That would close the model-family line of inquiry and leave
new data as the only remaining route to a market edge.

A gain too small to matter against a 0.0246-nat gap is the expected outcome and should be reported
as such, not as a vindication of either family.

## Limits

- The dispersion parameter is estimated from the same pilot data it is evaluated on. That is a
  mild optimism in favour of the negative binomial, which makes a null result stronger, not weaker.
- Both families use the same features and the same online update, so this isolates the
  distributional assumption alone.
- The closing-price timing caveat applies to the market column.
