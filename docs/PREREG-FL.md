# Pre-registration — favourite-longshot signal in the totals market

**Written and committed before the test was run.** The commit that adds this file precedes the
commit that adds results; that ordering is the point.

## Why this test exists

In the descriptive Track B table (E10), accuracy exceeded the de-vigged implied probability at
thresholds of 0.70 and above. That is the signature of the favourite-longshot bias, a
well-documented regularity in football prices, and it is the only positive signal the expedition
has produced. It must get a fair hearing rather than a dismissal — but it appeared *after* the
thresholds were chosen and the table was read, so testing it on the same rows that suggested it
would be circular.

## Design

The pilot seasons are split by time:

- **Selection seasons:** 2021 and 2122. Used only to choose a single threshold by a fixed rule.
- **Test season:** 2223. Used once, after the threshold is fixed, and never used for selection.

### Threshold selection rule (applied to the selection seasons only)

Consider thresholds 0.65, 0.70, 0.75. Choose the **lowest** threshold that satisfies both:

1. at least 200 fixtures in the selection seasons meet it; and
2. the accuracy-minus-implied gap at that threshold is positive.

If no threshold satisfies both, the test stops here and reports that the signal did not reproduce
in the selection seasons — a negative result, recorded as such.

### Test (2223 only)

Apply the chosen threshold, unmodified, to the held-out season. Two quantities:

- **Gap:** mean(correct) − mean(implied probability of the selected side).
- **Return:** mean(correct × odds − 1), row-level.

Uncertainty: cluster bootstrap over division-seasons within the test season, 2,000 draws, 95%
percentile interval. No further threshold search, no further exclusions, no re-specification.

### Decision rule, fixed in advance

The signal counts as **supported** only if, in the held-out season:

- the gap interval excludes zero, **and**
- the return interval excludes zero.

Anything else is recorded as **not supported**. A positive point estimate with an interval
spanning zero is not a weakened version of support; it is a null.

## What a supported result would and would not mean

Would mean: in one held-out season of one corpus, short-priced totals selections returned more
than their implied probability, consistently enough to survive clustered uncertainty.

Would **not** mean: an exploitable edge. It would still be one book's closing prices with no
observation timestamp, one market family, three seasons, and no stake sizing or liquidity
consideration. It would justify a separate, better-powered study — not execution.

## Known limitations, stated before the result is known

- The threshold came from exploratory reading of the full pilot, so the selection seasons are not
  clean of that reading even though the test season is.
- The test season is one season: roughly 3,000 fixtures, of which perhaps 300 meet a 0.70
  threshold. Power is low, and a null will not distinguish "no signal" from "signal too small to
  detect here".
- Closing prices, no quote timestamps: the T−90 caveat stands.
- Multiple testing: the pilot has been searched extensively. This test is one more look, not a
  correction for the history.
