<!-- generated-by: feature_screen.py sha256=5e209d7286ee -->

# Feature screen

Every candidate family tested under one protocol: market-conditioned logistic, leave-one-season-
out, cluster bootstrap for the interval, 200 within-season permutations for a null
distribution, and Benjamini-Hochberg across the 6 families. `n = 8,938` pilot
fixtures.

| Family | Gain (nats) | Cluster 95% | Perm. p | BH q | Per-season gains | AUC base → treat |
| --- | --- | --- | --- | --- | --- | --- |
| F1 cross-book disagreement | -0.0001 | [-0.0002, +0.0001] | 0.557 | 0.900 | -0.0000, -0.0000, -0.0002 | 0.6072 → 0.6071 |
| F2 congestion (rest + load) | -0.0013 | [-0.0027, -0.0002] | 0.900 | 0.900 | -0.0002, -0.0000, -0.0036 | 0.6072 → 0.6056 |
| F3 cross-market (1X2 draw) | -0.0002 | [-0.0004, -0.0000] | 0.806 | 0.900 | -0.0000, -0.0004, -0.0001 | 0.6072 → 0.6068 |
| F4 recent scoring trend | -0.0002 | [-0.0003, +0.0000] | 0.542 | 0.900 | -0.0002, -0.0002, -0.0001 | 0.6072 → 0.6067 |
| F5 league scoring environment | +0.0000 | [-0.0002, +0.0002] | 0.388 | 0.900 | +0.0001, -0.0003, +0.0001 | 0.6072 → 0.6072 |
| F6 all of the above | -0.0017 | [-0.0031, -0.0006] | 0.736 | 0.900 | -0.0002, -0.0010, -0.0038 | 0.6072 → 0.6048 |

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
