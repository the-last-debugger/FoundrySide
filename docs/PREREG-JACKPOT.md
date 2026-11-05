# Pre-registration — jackpot pool mechanics

Written before the run. This is a **parameterised arithmetic study**, not a measurement: no jackpot
rules or payout history were locatable (see `LEAD_TRIAGE.md`), so every quantity below is hypothetical
by construction and is labelled as such.

## Question

Under a pool model, when can a jackpot ticket have positive expected value, and what does that depend
on? The honest answer is a condition on parameters, not a verdict about any real product.

## Model, stated in full

- `N` entrants, each staking `s`, takeout `t`, so the pool is `P = N·s·(1 − t)`.
- Each entrant holds `c_i` lines out of a universe `U` of equally likely lines; your coverage is
  `c_you/U`.
- The winning line is uniform. If `k` tickets match it, each receives `P/k`.
- The relevant quantity for you is the expected net of one line: your chance of holding the winning
  line times the share you would receive.

Two quantities are **separately reported**, because an earlier version of this project conflated them:

1. **Your coverage** — `c_you/U`. Depends only on your own ticket.
2. **Expected winning tickets** — a pool-wide count. It depends on *other entrants'* coverage, which
   your own ticket says nothing about. It is computed only when a rival-coverage assumption `r` is
   supplied: `(N − 1)·r`.

## The comparison

With your coverage `q`, rival coverage `r`, and `N` entrants:

`EV per line = q · P / (1 + (N − 1)·r) − s`

The sweep reports this over takeout `t ∈ {0.1, 0.2, 0.3, 0.4}`, entrant counts `N ∈ {100, 1 000,
10 000}`, and the ratio `q/r` from 0.5 to 4, so the answer is a **condition**: a player needs coverage
above the field's average by enough to overcome the takeout.

## What is deliberately not claimed

- No claim about any real jackpot product, since no rules were obtainable.
- No claim that any of these parameter values are realistic; they are a grid.
- No claim that a positive-EV cell is exploitable: it requires predicting the field's coverage, which
  this study does not model.

## Decision rule, fixed in advance

Report the break-even coverage ratio `q/r` for each (takeout, N) cell, and state plainly that a
positive cell is a **condition satisfied by an assumed parameter set**, not an opportunity.

## Stop condition

One analysis, one report, one commit. No follow-up without new authorisation.
