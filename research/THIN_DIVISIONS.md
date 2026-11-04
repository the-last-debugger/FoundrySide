<!-- generated-by: thin_divisions.py sha256=1d5fb92f6c4a -->

# Thin-division market efficiency

Specification fixed at `docs/METHOD-THIN-DIVISIONS.md` before the run. **No model is involved**: the
subject is the de-vigged closing price itself. Files were read into memory only, never stored, merged
or added to the corpus; the confirmatory slice was not read.

## Per division — descriptive

Each row shows the market log loss, the fixture count, and the three individual season values. There
are **no intervals and no significance claims at division level**: each division contributes three
season-clusters, and a bootstrap over three units would not support one.

| Division | Market log loss (three seasons, individually) |
| --- | --- |
| E2 | 0.6888 (n=1,651; 0.6845, 0.6873, 0.6945) |
| E3 | 0.6744 (n=1,655; 0.6707, 0.6806, 0.6719) |
| EC | 0.6828 (n=1,533; 0.6922, 0.6871, 0.6709) |
| I2 | 0.6767 (n=1,139; 0.6769, 0.6757, 0.6773) |
| SP2 | 0.6523 (n=1,385; 0.6319, 0.6824, 0.6425) |
| F2 | 0.6680 (n=1,140; 0.6663, 0.6551, 0.6826) |
| D2 | 0.6703 (n=918; 0.6702, 0.6698, 0.6709) |
| B1 | 0.6689 (n=918; 0.6644, 0.6740, 0.6682) |
| T1 | 0.6802 (n=1,112; 0.6818, 0.6877, 0.6689) |
| SC0 | 0.6721 (n=683; 0.6720, 0.6790, 0.6652) |
| SC1 | 0.6818 (n=495; 0.6873, 0.6756, 0.6837) |
| SC2 | 0.6919 (n=470; 0.7097, 0.6950, 0.6779) |
| SC3 | 0.6976 (n=470; 0.7013, 0.7020, 0.6910) |

## Denominator accounting — where every document's number comes from

The assessment counts **source fixtures**; this report counts **scored observations**. They are not
the same sample and the difference is disclosed here rather than reconciled by assertion.

| Division | Raw | No usable two-sided O/U | No result | Scored |
| --- | --- | --- | --- | --- |
| E2 | 1,656 | 5 | 0 | 1,651 |
| E3 | 1,656 | 1 | 0 | 1,655 |
| EC | 1,535 | 2 | 0 | 1,533 |
| I2 | 1,140 | 1 | 0 | 1,139 |
| SP2 | 1,386 | 1 | 0 | 1,385 |
| F2 | 1,140 | 0 | 0 | 1,140 |
| D2 | 918 | 0 | 0 | 918 |
| B1 | 918 | 0 | 0 | 918 |
| T1 | 1,142 | 30 | 0 | 1,112 |
| SC0 | 684 | 1 | 0 | 683 |
| SC1 | 495 | 0 | 0 | 495 |
| SC2 | 470 | 0 | 0 | 470 |
| SC3 | 470 | 0 | 0 | 470 |

| Season | Raw | No price | No result | Scored |
| --- | --- | --- | --- | --- |
| 2021 | 4,418 | 10 | 0 | 4,408 |
| 2122 | 4,592 | 1 | 0 | 4,591 |
| 2223 | 4,600 | 30 | 0 | 4,570 |

Every exclusion is a missing or unusable two-sided Over 2.5 price, or a missing result; no row is
dropped for any other reason. Turkey 1 accounts for the largest single loss, consistent with its
lower price coverage in the assessment.

## Pooled comparison

| Set | Fixtures | Market log loss |
| --- | --- | --- |
| Eight existing divisions | 8,941 | 0.6742 |
| Thirteen additions | 13,569 | 0.6759 |
| Difference (additions − existing) | — | **+0.0017** |

Approximate division-season bootstrap interval for the **difference** (additions − existing),
resampling each set's clusters independently: **[-0.0048, +0.0084]**. The earlier version of
this report gave an interval for the additions' log loss alone, which is a different quantity; that
figure was [0.6709, 0.6806] and it is retained only as context.

**Spread of division-level differences** against the existing eight: minimum -0.0219,
maximum +0.0235, median +0.0025. The pooled figure alone would
conceal that range, which is why both are reported.

## Secondary metrics

| Division | Brier | Reliability | Resolution | Calibration slope |
| --- | --- | --- | --- | --- |
| E2 | 0.2478 | 0.0006 | 0.0033 | 0.791 |
| E3 | 0.2408 | 0.0012 | 0.0048 | 1.385 |
| EC | 0.2449 | 0.0003 | 0.0053 | 1.074 |
| I2 | 0.2418 | 0.0027 | 0.0047 | 1.058 |
| SP2 | 0.2300 | 0.0004 | 0.0040 | 1.168 |
| F2 | 0.2377 | 0.0009 | 0.0062 | 1.229 |
| D2 | 0.2388 | 0.0023 | 0.0040 | 1.138 |
| B1 | 0.2381 | 0.0019 | 0.0070 | 1.257 |
| T1 | 0.2437 | 0.0006 | 0.0055 | 1.034 |
| SC0 | 0.2396 | 0.0019 | 0.0105 | 0.998 |
| SC1 | 0.2443 | 0.0006 | 0.0049 | 1.158 |
| SC2 | 0.2494 | 0.0016 | 0.0016 | 0.432 |
| SC3 | 0.2523 | 0.0063 | 0.0035 | 0.321 |

## What this says and does not say

The difference of +0.0017 nats between the pooled additions and the existing eight is
below the 0.01-nat scale used elsewhere in the
project as a descriptive yardstick — which is a scale, not a test.

**It is not evidence of exploitable value.** Price quality is a property of the price, not of a
strategy: exploiting any of it would need prices a user can obtain, stakes, limits and a decision
rule, none of which this corpus records. Nothing here supports a claim of user advantage.

## Limits

- Three seasons per division; only a large difference would be visible, and small divisions are
  reported with their counts so the reader can discount them.
- The eight-division reference is a different set of competitions, not a matched control.
- Closing prices without timestamps; the T−90 caveat applies throughout.
- Internal analysis only; no redistributable dataset was created and P-03 remains open for any
  publication.
