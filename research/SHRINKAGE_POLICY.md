<!-- generated-by: shrinkage_policy.py sha256=200b9059b122 -->

# Disagreement-aware shrinkage — pre-registered test

Specification committed at `docs/PREREG-SHRINKAGE.md` before this script existed. Six policies,
parameters fitted on prior seasons only, each evaluation season scored once.

## Per-season log loss

| Season | n | market | model | fixed 0.5 | shrink-linear | shrink-threshold | market-fallback |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2122 | 2,986 | 0.6725 | 0.6867 | 0.6765 | 0.6739 | 0.6726 | 0.6812 |
| 2223 | 2,975 | 0.6751 | 0.6886 | 0.6788 | 0.6750 | 0.6750 | 0.6835 |

## Pooled over evaluation seasons

| Policy | Log loss | Gain vs market | Cluster 95% | Reliability | Resolution | Coverage |
| --- | --- | --- | --- | --- | --- | --- |
| market | 0.6738 | +0.0000 | [+0.0000, +0.0000] | 0.0002 | 0.0087 | 0.0% |
| model | 0.6876 | -0.0138 | [-0.0181, -0.0101] | 0.0001 | 0.0021 | 89.0% |
| fixed 0.5 | 0.6776 | -0.0038 | [-0.0057, -0.0022] | 0.0012 | 0.0084 | 78.4% |
| shrink-linear | 0.6744 | -0.0006 | [+0.0000, +0.0000] | 0.0002 | 0.0087 | 0.0% |
| shrink-threshold | 0.6738 | -0.0000 | [+0.0000, +0.0000] | 0.0002 | 0.0087 | 0.0% |
| market-fallback | 0.6823 | -0.0085 | [-0.0113, -0.0057] | 0.0003 | 0.0047 | 83.0% |

Fitted parameters: 2122: d0=0.60, t=0.10, 2223: d0=0.25, t=0.10.

## Verdict, against the pre-registered rule

The rule required a policy to beat **both** the market and the model, with a cluster interval on
its improvement over the market excluding zero.

- **market**: does not beat market, beats model, interval includes zero.
- **model**: does not beat market, does not beat model, interval includes zero.
- **fixed 0.5**: does not beat market, beats model, interval includes zero.
- **shrink-linear**: does not beat market, beats model, interval includes zero.
- **shrink-threshold**: does not beat market, beats model, interval includes zero.
- **market-fallback**: does not beat market, beats model, interval includes zero.

## Reading

If no policy satisfies both conditions, the pre-registered stop criterion applies: the line stops
and the next work is robustness of the E18 finding rather than further policy variants.

The fitted values matter for interpretation as much as the losses: an interior optimum says the
model carries some value up to a departure size, while a boundary hit says the fitting wanted to
shrink everything or nothing.

## Limits

- Two forward folds, one corpus; a rule that works on both is promising here, not validated.
- Closing prices without timestamps: this is accuracy against a closing benchmark, not executable
  value.
- The market baseline is the same de-vigged price used throughout; the confirmatory slice is
  untouched.
