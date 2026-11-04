<!-- generated-by: book_disagreement.py sha256=7900e5629f40 -->

# Workstream 4, experiment 1 — does cross-book disagreement carry information?

Pilot seasons only. Both books' over/under 2.5 closing prices de-vigged; the baseline is a
logistic on Pinnacle's logit, the treatment adds the absolute difference between the two books'
logits. Fitted leave-one-season-out; no fold is scored by a model that saw its outcomes.

## Result

| Model | Log loss (out-of-fold) | AUC |
| --- | --- | --- |
| Market only | 0.6743 | 0.6072 |
| Market + disagreement | 0.6743 | 0.6071 |

- Log-loss improvement from the disagreement term: **-0.0001** nats.
- Cluster-bootstrap 95% interval on that paired improvement: **[-0.0002, +0.0001]**.
- AUC change: -0.0001.

## Per held-out season

| Held out | n | Market only | + disagreement |
| --- | --- | --- | --- |
| 2021 | 2,978 | 0.6749 | 0.6749 |
| 2122 | 2,985 | 0.6727 | 0.6727 |
| 2223 | 2,975 | 0.6752 | 0.6754 |

## Fitted coefficients (disagreement model)

| Held out | intercept | logit(p_pinnacle) | disagreement |
| --- | --- | --- | --- |
| 2021 | +0.0258 | +1.0944 | -0.7493 |
| 2122 | -0.0187 | +0.9952 | +0.0321 |
| 2223 | +0.0065 | +1.0467 | -1.0219 |

## Reading

The interval is the test. If it excludes zero, cross-book disagreement carries information the
single benchmark does not, and it is the first candidate for added resolution. If it straddles
zero, the two books disagree noisily and the experiment is a negative result worth recording:
it rules out one cheap source of extra information rather than leaving it plausible.

The AUC column is the guard against a calibration artefact: a term that only rescales the
probability cannot move the ranking, so an AUC gain is the signature of real separation.

## Limits

- Two books, one market, one corpus. "Disagreement" here means these two feeds, not the market.
- The 0.01-nat target is unchanged; this experiment asks whether information exists, not whether
  it is large enough to trade.
- Closing prices carry no observation timestamp, so the comparison is between two prices whose
  collection times are unknown, and the T−90 caveat applies to any claim about acting on them.
