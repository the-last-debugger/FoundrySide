# Track B — evaluation design

Track A asks whether a forecast beats the closing price. Track B asks whether a **user decides
better** with a filtered, calibrated view than with the raw board. These are different products
and they need different measurements. This document specifies Track B's evaluation before any of
it is scored, so the success criteria cannot be chosen after seeing results.

## The product claim, stated narrowly

Given a fixture and a market price, the system either **abstains** or shows:

- the market's own de-vigged probability, rounded and labelled as the market's;
- a confidence band from the cluster-calibrated uncertainty, not a point estimate;
- the reason for abstaining when it abstains (low confidence, thin market, no comparable history).

It never asserts a probability better than the market's, because eleven experiments found no
information that would justify one. The honest product is **filtered access to a good forecast**,
not a superior forecast.

## What is measured

| Measure | Definition | Why it matters |
| --- | --- | --- |
| **Coverage** | share of fixtures where the system speaks | a product that always abstains is useless |
| **Accuracy at coverage** | hit rate among spoken fixtures | the user-facing quality claim |
| **Calibration of shown numbers** | reliability of the probabilities displayed, by bin | a shown 70% must be right 70% of the time |
| **Log-growth at fixed stake** | mean of `log(1 ± stake)` per fixture followed | the decision-theoretic value, margin included |
| **Regret vs oracle** | loss relative to always showing the true best option | how much the filter costs at most |

All five are already computed in `research/TRACK_B.md` for a threshold rule. What is missing is
the decision-theoretic layer: a **user model**.

## The user model, and its assumptions

The current growth column assumes a fixed 1% stake, flat, with no bankroll constraint. That is a
convenience, not a user. The design requires three stated assumptions:

1. **Stake rule** — fixed fraction (tested at 0.5%, 1%, 2%) rather than Kelly, because a real user
   does not size optimally and because Kelly on a negative-edge product recommends staking
   nothing.
2. **Risk preference** — log utility of wealth, standard for repeated small stakes.
3. **Action set** — bet the shown side, or abstain. No hedging, no parlays.

Under these, the product's value is the difference in expected log-growth between following the
filtered view and following the raw board. On the pilot data that difference is **negative at
every threshold** — the filter concentrates the margin rather than avoiding it. That is a result
about the product, and it belongs in the design, not in a footnote.

## What cannot be measured with this corpus

- **Behavioural lift**: whether a user actually decides better with a filtered view. That needs
  users, and this project has none.
- **Trust and comprehension**: whether showing a band instead of a number improves decisions.
- **The product's main benefit**: avoiding bad decisions through abstention, which is invisible in
  a corpus of already-placed closing prices.

So Track B's evaluation can establish the *arithmetic* of the offer — what it would pay — but not
its behavioural value. Any claim of user advantage requires a study this corpus cannot provide.

## Success criteria, fixed now

The product is **worth building** only if all three hold:

1. calibration of shown probabilities holds out of season (reliability within ±0.01 by bin);
2. log-growth at a 1% stake is non-negative at the chosen threshold with a cluster interval
   excluding a 0.001-nat loss;
3. coverage at that threshold is at least 5%, or the product speaks too rarely to be useful.

Measured against the pilot corpus (E10, 
esearch/TRACK_B.md), each criterion now has a number:

| Criterion | Measured | Verdict |
| --- | --- | --- |
| 1. calibration within ±0.01 by bin | largest quintile gap 1.6 pts at full coverage, **5.2 at 0.65**, 9.4 at 0.70 | **fails above 0.50** |
| 2. non-negative log-growth at 1% | −0.00002 at 0.65, +0.00000 at 0.70, interval spanning zero | **fails** |
| 3. coverage ≥ 5% | 10.0% at 0.65, 3.6% at 0.70 | passes at 0.65, fails above |

No threshold satisfies all three. The design therefore concludes the product is **not worth
building on this market**, on computed measures rather than on a prediction. The calibration
result is the decisive one and the least intuitive: filtering to confident selections makes the
displayed probability less accurate, because the surviving region is where the favourite-longshot
bias concentrates.

## Stop conditions

The design is abandoned if any of: criterion 2 fails on held-out seasons; calibration drifts; or
the sponsor declines to authorise the only route that could change it (new information). Recording
this now prevents a later re-specification from rescuing a product that the evidence does not
support.
