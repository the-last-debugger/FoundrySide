<!-- generated-by: model_family.py sha256=193f27d6ddcc -->

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

Poisson requires the ratio to be 1. It is 1.015 — indistinguishable from 1
at this sample size. The independent-Poisson assumption is therefore **not** materially
misspecified for totals, contrary to the usual football folklore, and the negative-binomial
variant has almost nothing to correct.

## 2. Does the better family fit the marginal distribution better?

| Quantity | Poisson | Negative binomial | Empirical |
| --- | --- | --- | --- |
| P(over 2.5) at the mean | 0.5088 | 0.5075 | 0.5068 |

## 3. Does it improve the forecasts?

| Forecast | Log loss | Brier |
| --- | --- | --- |
| Independent Poisson | 0.6988 | 0.2520 |
| Negative-binomial total | 0.6985 | 0.2519 |
| Market (closing) | 0.6742 | 0.2407 |

## Reading

The specification is not the problem. With the ratio at 1.015 and the
negative binomial improving log loss by a few hundredths of a thousandth of a nat, the
independent-Poisson form is adequate for totals. Its resolution deficit is informational. If the negative binomial does not beat Poisson out of sample,
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
