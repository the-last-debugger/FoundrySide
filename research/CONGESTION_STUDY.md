<!-- generated-by: congestion_study.py sha256=0d132c1bde3b -->

# Workstream 4, experiment 2 — does congestion carry information?

Pilot seasons only. Baseline is a logistic on Pinnacle's de-vigged logit; the treatment adds
rest difference, minimum rest and matches played in the previous 14 days. Fitted
leave-one-season-out.

## Result

| Model | Log loss | AUC |
| --- | --- | --- |
| Market only | 0.6744 | 0.6070 |
| Market + congestion | 0.6756 | 0.6055 |

- Improvement: **-0.0012** nats; cluster 95% interval **[-0.0024, -0.0002]**.
- AUC change: -0.0015.

## Per held-out season

| Held out | n | Market only | + congestion |
| --- | --- | --- | --- |
| 2021 | 2,980 | 0.6753 | 0.6754 |
| 2122 | 2,986 | 0.6726 | 0.6727 |
| 2223 | 2,975 | 0.6752 | 0.6787 |

## Reading

A positive interval excluding zero would make schedule load the first demonstrated source of
information beyond the price. An interval containing zero is a negative result for this feature
family and is recorded as such: congestion is priced, or it does not matter at this level of
detail, and either way it is not the route to added resolution.

## Limits

- Rest is measured from the fixture corpus, so a team's first match of a season gets a default
  rest of 14 days rather than its true off-season break.
- Cup and European fixtures are not in the corpus, so congestion is understated for teams that
  played them. That biases the feature toward zero, which makes a null result weaker evidence
  than it looks — stated here rather than discovered later.
- The closing price has no observation timestamp; the T−90 caveat applies.
