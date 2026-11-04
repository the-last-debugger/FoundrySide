<!-- generated-by: fl_test.py sha256=87f9ead195b4 -->

# E11 — pre-registered favourite-longshot test

Specification committed at `docs/PREREG-FL.md` before this script existed. Selection seasons
2021 and 2122; test season 2223; threshold chosen by the pre-registered rule and
applied unmodified.

## Threshold selection (selection seasons only)

| Threshold | Fixtures | Gap |
| --- | --- | --- |
| 0.65 | 627 | +0.0133 |
| 0.70 | 228 | +0.0264 |
| 0.75 | 62 | +0.0697 |

Chosen threshold: **0.65** (lowest meeting both the 200-fixture floor and a positive
gap).

## Test (2223, held out)

| Quantity | Value | Cluster 95% |
| --- | --- | --- |
| Fixtures | 266 | — |
| Accuracy | 0.7180 | — |
| Mean implied | 0.6921 | — |
| Gap (accuracy − implied) | +0.0260 | [-0.0162, +0.0874] |
| Return per unit | -0.0040 | [-0.0620, +0.0809] |

## Verdict

**not supported.** The pre-registered decision rule required both intervals to exclude zero. Here the
gap interval is [-0.0162, +0.0874] and the return interval is [-0.0620, +0.0809]
on 266 held-out fixtures.

This is the answer the test was designed to give, and it is reported as it came out: no
re-specification, no threshold search on the test season, no additional exclusions.

## Limits

- One held-out season, roughly 266 fixtures at this threshold: low power, so a
  null cannot distinguish "no signal" from "signal too small to detect here".
- The threshold rule was applied to seasons that had already been read descriptively, so the
  selection seasons are not fully clean even though the test season is.
- One book, closing prices, no quote timestamps; the T−90 caveat stands.
