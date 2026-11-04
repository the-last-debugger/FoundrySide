<!-- generated-by: movement_study.py sha256=269e852fb70e -->

# Does price movement carry information?

Pilot seasons, 8,929 fixtures with both an opening and a closing Pinnacle over 2.5 price.
Movement is the change in the de-vigged logit between the snapshots. Each hypothesis is tested as an
increment over the closing price, so a finding means information the closing price did not contain.

| Hypothesis | Feature SD | Gain (nats) | Cluster 95% | Perm. p |
| --- | --- | --- | --- | --- |
| M1 signed movement | 0.1226 | -0.00022 | [-0.00041, -0.00004] | 0.826 |
| M2 movement size | 0.0782 | -0.00001 | [-0.00009, +0.00008] | 0.343 |

Baseline log loss of the closing price alone: **0.6743**. Mean signed movement
-0.0058; median absolute movement 0.0765.

## Reading

A positive gain with an interval excluding zero would mean the move anticipates the outcome — a
genuine decision-support finding, since a user acting before the close could use it. A null means
the closing price already contains whatever the move was about, which is what an efficient market
should do with information that arrives before the close.

Either way this cannot establish executable value: neither snapshot records its observation time, so
"opening" cannot be tied to T−90 or to any moment a user could act.

## Limits

- Two snapshots only; the path between them is unobserved, so a price that moved and reverted looks
  identical to one that did not move.
- Opening prices are football-data's first recorded price, not necessarily the market's opening.
- One book (Pinnacle) for the movement measure; others may move differently.
