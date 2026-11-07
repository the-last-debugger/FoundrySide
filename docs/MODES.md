# Modes, in plain language

Every switch and view in the product, what it does, and what it can cost. Requested because the labels
read like engineering shorthand rather than things a person can act on.

## There are no "debug" or "don't care" modes

The product has **no debugging mode, no fast mode, and no mode that relaxes correctness**. Nothing in it
can be told to skip a check. The two things that look like modes are:

| Label in the product | What it actually is | Can it lose money? |
| --- | --- | --- |
| `--demo` | Runs on synthetic fixtures instead of the corpus | **No.** It shows the arithmetic; the prices are invented and labelled |
| `mode=held` | Runs on the corpus in `research/data` | **No.** Read-only, historical, no account |
| `--limit N` | Loads fewer fixtures, faster startup | No |
| `--port`, `--host` | Where the local server listens | No, unless exposed to a network it should not be |

The nearest thing to a dangerous mode is a **user deciding to bet after reading it**, which is outside
the software.

## The seven views, and the risk each implies

| View | What it tells you | Risk to money |
| --- | --- | --- |
| **Assess** | What a price implies, with the margin and its uncertainty | None on its own. Acting on it risks the stake |
| **Market** | Every book's price and margin, and where they disagree | None. A big spread is disagreement, not opportunity |
| **Structures** | The same net profit at different prices: what you risk versus how often it wins | None. It shows the trade-off, it does not recommend one |
| **Slip** | One selection's arithmetic: stake, gross, net, full-stake loss | None until placed. Combining legs is refused because the joint cannot be estimated |
| **Target** | Combinations close to a multiplier you ask for | None. A target is your constraint, not a promise |
| **Jackpot** | Pool arithmetic under assumptions you supply | None. It is arithmetic on your inputs |
| **Journal** | What was assessed and how it turned out | None. It records, it does not bet |

## Classifying by consequence, not by feature

That is the useful axis, and it has three classes:

1. **Information with no exposure** — Assess, Market, Structures, Target, Jackpot, Journal. These can be
   wrong, and the claim tags say how; none of them can lose money.
2. **A decision with exposure** — choosing to stake. Everything here only prices the decision; the
   stake is the user's.
3. **Advice the product refuses to give** — a predicted edge, an expected-value claim, a profit
   claim. Not disabled by a flag; simply not implemented.

## What "force the launch" would have meant

There was nothing to force: the product was runnable throughout. The modes above are all safe to run.
What was not available, and still is not, is any basis for saying a bet is likely to win — which is the
only thing that would have made launching it a financial risk rather than a demonstration.
