# Pre-registration — is the 6.5% price improvement arithmetic or dispersion?

Committed before the analysis runs. Authorised scope: method and pre-registration only.

## Question

The corpus shows that taking the best closing price for a selection is 6.51% better than taking the
market average. For any set of quotes the maximum exceeds the mean **by construction**, so the
question is how much of that 6.51% is mechanical and how much reflects genuine cross-book dispersion
in de-vigged probabilities.

## Data and fields

Pilot and confirmatory seasons are **not** both used: this is an exploratory measurement on the
same corpus used throughout, three pilot seasons, 1X2 closing prices. Confirmatory slice untouched.

| Field | Role |
| --- | --- |
| `PSC*`, `B365C*` | the two books whose three-way closing prices are recorded individually — the only source of per-book de-vigged probabilities |
| `MaxC*`, `AvgC*` | the best and mean closing price across the provider's tracked books |
| `Bb1X2` | number of bookmakers behind each `Avg`/`Max`, i.e. `K` — observed, not assumed |

## Identification — what is and is not measurable

**Measured:** cross-book dispersion between **two books' de-vigged** probabilities, under the
proportional de-vig assumption, expressed as the SD of their logit difference divided by √2.

**Projected:** what that dispersion implies for `K` books, via order statistics,
`σ · E[max of K standard normals]`.

**Not measurable with these fields:** the separation of genuine opinion differences from differences
in margin *allocation* (which proportional de-vig only partly absorbs), dispersion across books whose
prices are not individually recorded, and whether any price was obtainable. The report must state
each of these where the number is used.

## Procedure

1. For each fixture, de-vig Pinnacle and Bet365 separately (proportional method) and take logits.
2. `σ₂` = SD over fixtures of `(logit_A − logit_B)/√2`, computed per division and pooled.
3. For each fixture, `E[max_K]` from its observed `Bb1X2` (tabulated for K ≤ 20).
4. Projected gap per fixture = `σ₂ · E[max_K]`; average it.
5. Observed gap per fixture = `mean(log MaxC − log AvgC)` over the three outcomes.
6. **Excess = observed − projected**, with a cluster bootstrap interval over division-seasons.

## Sensitivity

- `σ₂` scaled by 0.5 and 2.0.
- A regression of observed gap on `E[max_K]` across fixtures, whose slope should be near `σ₂` if the
  exchangeability assumption holds. Reported as a check, not as proof.
- Books copy each other, so the independence assumption **overstates** the projected gap and biases
  the excess downward — conservative for the claim.

## Decision rules, fixed now

| Excess | Reading | Consequence |
| --- | --- | --- |
| Interval contains zero | consistent with arithmetic | price-shopping claim **weakened**: present as arithmetic, not advantage |
| Interval entirely above zero | dispersion exceeds projection | claim **strengthened**, still subject to availability |
| Interval entirely below zero | observed below projection | **integrity check first** — confirm `Max` and `Avg` cover the same books before interpreting |

## Stop condition

One analysis, one report. No follow-up variant without a new authorisation.

## What this cannot support

No expected-value, profitability or user-advantage claim. No statement about obtainable prices. No
claim that the 6.5% is "fair-probability disagreement" — only that it is dispersion in de-vigged
probabilities under a stated assumption.
