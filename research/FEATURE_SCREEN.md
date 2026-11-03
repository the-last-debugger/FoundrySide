<!-- generated-by: feature_screen.py sha256=614ab77adafd -->

# Feature screen

Every candidate family tested under one protocol: market-conditioned logistic, leave-one-season-
out, cluster bootstrap for the interval, 200 within-season permutations for a null
distribution, and Benjamini-Hochberg across the 6 families. `n = 8,938` pilot
fixtures.

| Family | Gain (nats) | Cluster 95% | Perm. p | BH q | Per-season gains | AUC base → treat |
| --- | --- | --- | --- | --- | --- | --- |
| F1 cross-book disagreement | -0.0001 | [-0.0002, +0.0001] | 0.562 | 0.831 | -0.0000, -0.0000, -0.0002 | 0.6072 → 0.6071 |
| F2 congestion (rest + load) | -0.0012 | [-0.0027, -0.0003] | 0.831 | 0.831 | -0.0001, -0.0000, -0.0035 | 0.6072 → 0.6057 |
| F3 cross-market (1X2 draw) | -0.0002 | [-0.0005, +0.0000] | 0.816 | 0.831 | -0.0000, -0.0004, -0.0001 | 0.6072 → 0.6068 |
| F4 recent scoring trend | -0.0001 | [-0.0003, +0.0000] | 0.378 | 0.831 | -0.0001, -0.0001, -0.0001 | 0.6072 → 0.6068 |
| F5 league scoring environment | -0.0000 | [-0.0002, +0.0001] | 0.348 | 0.831 | +0.0000, -0.0001, +0.0000 | 0.6072 → 0.6071 |
| F6 all of the above | -0.0016 | [-0.0029, -0.0004] | 0.761 | 0.831 | -0.0002, -0.0007, -0.0039 | 0.6072 → 0.6049 |

## How to read this

A family is evidence of information only if it clears **all** of: a positive gain, a cluster
interval excluding zero, a permutation p below the BH threshold, and the same sign in every
season. The permutation test is the one that matters most here: the bootstrap asks how precisely
the gain is estimated, while the permutation asks whether a gain of that size could arise with the
feature carrying no information at all — the right question for a screen of this kind.

The per-season column is a blunt stability check. A family whose gain flips sign across the three
held-out seasons is noise even if its aggregate interval looks convincing.

## Selection effects

The pilot has now been examined many times, and this screen adds 6 more tests to that
history. The BH column corrects within this family of tests but not across the whole day's
searching. Treat any single positive here as a candidate requiring a fresh, independent check —
not as a discovery.

## Limits

- One corpus, one market, three pilot seasons. The confirmatory slice is untouched.
- Features are computed from the fixture list and prior results only; the schedule is public, so
  this is not look-ahead. Cup and European fixtures are absent, so congestion is understated.
- The closing prices carry no observation timestamp; the T−90 caveat applies to every claim about
  acting on these relationships.
