# Pre-registration — robustness and transfer of the disagreement finding

**Committed before the experiment runs.** Active task in `docs/RESEARCH_QUEUE.md`.

## The claim being tested

E18 reported that after forward calibration the model's deficit is concentrated where it departs
from the price: 0.0574 nats in the ≥0.60 logit departure band against 0.0039 in the <0.10 band,
pooled over the pilot. E18 also warned that every split there was a search over one pilot.

This asks whether that ordering **reproduces out of time and across divisions**. If it does not, E18
is a description of one pooled sample and must be labelled that way wherever it is cited.

## Design, fixed now

- **Seasons**: 2122 and 2223, the two that can be evaluated forward. Calibration for each is fitted
  on seasons strictly before it. The first pilot season is excluded, as in E18.
- **Bands**: near = departure < 0.10 on the logit scale; far = departure ≥ 0.60. Fixed from E18,
  not re-chosen.
- **Divisions**: all eight, reported descriptively with sample sizes.
- **Metric**: model log loss minus market log loss on the same fixtures; positive means the model
  is worse.

## What counts as reproduction, declared in advance

The pattern **reproduces** if, in **both** forward seasons:

1. the far-band deficit exceeds the near-band deficit; and
2. the far-band cluster interval excludes zero.

Anything else — including one season holding and the other not — is recorded as **not reproduced**,
and the citation of E18 in the summary must then be labelled a pooled pilot description.

Division-level cells are descriptive. With eight divisions split two ways, cells will be small; any
cell under 100 fixtures is reported with a literal "small sample" marker and is not used in any
conclusion.

## Uncertainty

Cluster bootstrap over division-seasons within each season's rows, 2,000 draws, 95% percentile
intervals. Per-division cells use the same resampling restricted to that division and inherit wider
intervals; they are not tested for significance against each other.

## Stop criterion

If reproduction fails, this line stops. The follow-up is not a fourth variant — it is correcting
every citation of E18 in the repository to say "pooled pilot description, not reproduced by season",
and moving to the next authorised item.

## What this cannot establish

- Whether the pattern holds outside this corpus.
- Any product consequence: the shrinkage test (E19) already found no policy that beats market-only,
  so even a reproduced disagreement pattern does not create a deployable edge.
- Executable value: closing prices without timestamps throughout.
