# Dispersion analysis — implementation blocker

**Status: stopped before scoring, returned for review.** The approval said that a material
implementation defect means stop rather than improvise, and this is one.

## The defect

`docs/PREREG-DISPERSION.md` §4 requires the number of books per fixture, `K`, to be **drawn from the
observed distribution of `Bb1X2`**, and §4a step 3 uses it to decide how many book quotes to simulate.

**`Bb1X2` is not present in the held data.** Checked exhaustively: all 40 corpus files
(8 divisions × 5 seasons) were opened and their headers read. **Zero** contain any column beginning
`Bb`.

The field names the provider's own notes describe are real — `Bb1X2` is documented as the number of
BetBrain bookmakers used for the averages and maximums — but that column is not in the files this
project holds. The corpus has `MaxC*` and `AvgC*` (the outputs of that aggregation) and `PSC*` /
`B365C*` (two individual books), and nothing that records how many books produced them.

## Why this is blocking rather than cosmetic

`S_sim` is the mean of `max/mean − 1` over simulated selection-snapshots. That statistic depends
directly on `K`: a maximum over 4 books sits closer to its mean than a maximum over 12. With `K`
unknown, `S_sim` is not defined, and the calibrated comparison the protocol exists to make cannot be
run.

Choosing a `K` now would be a change to the data-generating model **after** approval, made with
knowledge that the alternative is not running. That is precisely what the approval forbids.

## What was not done

No corpus scoring, no simulation, no parameter substitution. The analysis has not started.

## Options, for the sponsor to choose between

| Option | What it means | Cost |
| --- | --- | --- |
| **A. Fix `K` as a sensitivity grid** (e.g. 4, 6, 8, 10, 12) | `S_sim` becomes a range over assumed `K` rather than a single calibrated value; the protocol's decision rule already compares against a grid, so it absorbs this without changing the estimand | A protocol amendment, no new data |
| **B. Infer `K` from `Max − Avg`** | The gap between a maximum and a mean grows with `K` under a dispersion model; that relationship could in principle recover an implied `K` | Not preregistered, and circular: the same relationship is the thing being tested |
| **C. Stop the study** | The question survives, but cannot be answered with these fields | Zero |

I would choose **A** if the study is to proceed: it is a one-line change to the data-generating model,
it does not touch the estimand, the inclusion rules, the decision rules or the sensitivity logic, and
it makes the assumption explicit rather than hiding it. It does mean `S_sim` is reported as a band
over `K`, which weakens any claim that the model reproduces the statistic exactly — appropriately, in
my view, because the number of books behind `Max`/`Avg` genuinely is unknown here.

**B** should be rejected. It infers the parameter from the very quantity the study is testing.

## What this does not change

Track A stays closed, P-02 untouched, market-companion still queued. The blocker is a property of the
held fields, not of the question, and it was discovered before any result existed — which is the point
of pre-registration.
