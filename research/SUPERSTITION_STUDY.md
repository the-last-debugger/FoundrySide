<!-- generated-by: superstition_study.py sha256=d12ece2211a9 -->

# Superstition study — calendar folklore against the price

Pilot seasons only, 8,941 fixtures. Each hypothesis is an increment over the **market
price**, so a finding would mean the price missed something a user could have known before
kickoff — not merely that the calendar correlates with outcomes.

| Hypothesis | Cases | Base rate | Gain (nats) | Cluster 95% | Perm. p | BH q |
| --- | --- | --- | --- | --- | --- | --- |
| H1 full moon (±1 day) | 667 | 7.5% | -0.00006 | [-0.00029, +0.00018] | 0.493 | 0.950 |
| H2 Friday the 13th | 11 | 0.1% | -0.00275 | [-0.00694, +0.00014] | 0.886 | 0.950 |
| H3 the 13th of any month | 336 | 3.8% | -0.00042 | [-0.00071, -0.00019] | 0.950 | 0.950 |
| H4 weekend kickoff | 6,414 | 71.7% | -0.00015 | [-0.00032, -0.00000] | 0.721 | 0.950 |

Baseline log loss of the market price alone: **0.6744**.

## Reading

**Read the Cases column first.** Friday the 13th occurs about once a year, so this corpus holds
fewer than a dozen such fixtures; that row cannot distinguish an effect from noise in either
direction and should be treated as untested rather than as a null. The other three have enough
cases to be informative.

A gain is information the price did not have. A negative gain means the indicator adds noise —
its inclusion costs accuracy. A gain whose interval straddles zero, whose permutation p is
unremarkable, and whose BH q does not clear the family is a null, and the honest conclusion is
that the belief is either already priced or not true in this corpus.

The permutation null shuffles the indicator within division-seasons, preserving the joint
structure and the cluster geometry; the p-value is therefore "how often would a gain this large
arise if the label carried no information", not a claim about the population.

## Why calendar folklore is the right first test

It is deterministic: the date of a full moon or a Friday the 13th is known years ahead, so there
is no availability question and no look-ahead risk. It is also exactly what a superstition ought to
be — a belief about a date, testable without knowing anything about the teams. If a belief cannot
show up here, its problem is not the data pipeline.

## What this does not test

- Beliefs that need information the corpus lacks: referee appointments, kit colours, managerial
  birthdays, crowd size, pundit predictions.
- "Bogey team" effects, which are a head-to-head belief rather than a calendar one and need a
  separate design with pair-level clustering.
- Anything requiring a later cutoff than T−90.

## Limits

- The full moon is computed from a mean synodic month with one epoch, accurate to a few hours;
  the ±1-day window absorbs the error but also weakens the test.
- One corpus, three pilot seasons, one market. The confirmatory slice is untouched.
- Multiple testing across four hypotheses is controlled within this family, not across the
  expedition's whole history.
