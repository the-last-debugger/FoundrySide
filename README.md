# FoundrySide

A research repository, not an application. The project is in its pre-proposal phase
and `DECISIONS.md` D-01 records that it is **not authorised to build** until a formal
proposal is reviewed and approved.

## The four documents, in reading order

| Document | What it is |
| --- | --- |
| `PRE_PROPOSAL.md` | The sponsor's vision: what FoundrySide is meant to investigate. Written first, unchanged. |
| `CRITIQUE.md` | A review of it: eleven findings, what to keep, what to cut, and what the prior art already answers. |
| `PROPOSAL_SETTLEMENT.md` | The fast path to a decidable proposal: three questions, ten decisions with defaults, four one-day tests. |
| `docs/COLLAB/` | The bridge: thread, review queue, decisions, proposals. Start at `docs/COLLAB/README.md`. |

## The state of the argument

`PRE_PROPOSAL.md` proposes a laboratory that investigates markets, accumulators and
jackpots across four sports, ideally at zero recurring cost, and asks for thirteen
research reports before a proposal.

`CRITIQUE.md` argues that the vision is sound and the sequence is not: the document
has no falsifier, no null model, no cost unit, and does not cite the sponsor's own
prior results — 10,329 resolved signals on a *virtual* league, which answered its
central question for that domain and leave the real-world version open.

`PROPOSAL_SETTLEMENT.md` is the proposed way out: settle ten decisions (nine of them
by default), draft the proposal the same day, and let four one-day tests de-risk it
instead of gating it.

## What the project is waiting on

A sponsor decision on the ten-item register in `PROPOSAL_SETTLEMENT.md` §2, which is
**under review, not approved**. The sponsor's 2026-11-03 response accepted the
OLPRS domain correction, declined to accept D-04–D-13 wholesale, declined to fix D-05
before T0, and asked whether D-04/D-06 narrow the ambition. `PROPOSAL_SETTLEMENT.md` §0
answers that: they are phase-one constraints, the ambition is unchanged, and the
expansion ladder states what would earn each wider scope. The bar is now a rule to be
pre-registered before scoring, with its number computed after T0.

## Running the bridge checks

```powershell
$py = "C:\Users\tuyaa\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe"

& $py -m unittest discover -s tests -v
& $py scripts\collab_check.py
```

`collab_check.py` fails when the thread has lost a line, when the review queue claims
a verdict that no oversight entry records, or when a proposal has been filed as a
decision. Run it before every push.
