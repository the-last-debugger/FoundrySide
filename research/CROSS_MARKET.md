<!-- generated-by: cross_market.py sha256=fa3588204146 -->

# E7 — does the 1X2 market add information to the totals market?

Pilot seasons only. Baseline logistic on Pinnacle's de-vigged over/under 2.5 logit; treatment
adds the de-vigged draw probability from the same book's 1X2 prices, also as a logit. Fitted
leave-one-season-out.

## Result

| Model | Log loss | AUC |
| --- | --- | --- |
| Totals market only | 0.6744 | 0.6070 |
| + 1X2 draw probability | 0.6746 | 0.6066 |

- Improvement: **-0.0002** nats; cluster 95% interval **[-0.0004, +0.0000]**.
- AUC change: -0.0003.

## Per held-out season

| Held out | n | Totals only | + draw |
| --- | --- | --- | --- |
| 2021 | 2,980 | 0.6753 | 0.6754 |
| 2122 | 2,986 | 0.6726 | 0.6729 |
| 2223 | 2,975 | 0.6752 | 0.6754 |

## Reading

A positive interval would mean the two markets are not informationally identical and the totals
price leaves something on the table — the first genuine finding of the expedition and a concrete
place to look further. An interval containing zero means the two prices agree, which is what an
efficient pair of markets should do, and it closes another cheap avenue.

Either way the effect would have to be large enough to matter against a 0.0246-nat deficit. A
gain of a few thousandths would be a curiosity, not an advantage.

## Limits

- Two prices from one book. A different book's 1X2 might disagree, but cross-book disagreement
  already tested null in E4.
- The draw probability is a proxy for the goal environment, not a measurement of it.
- No quote timestamps, so the T−90 caveat applies to any claim about acting on this.
