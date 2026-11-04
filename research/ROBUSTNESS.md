<!-- generated-by: robustness.py sha256=aee891addbae -->

# Robustness of the disagreement finding

Pre-registered at `docs/PREREG-ROBUSTNESS.md`. Bands fixed from E18: near = departure under 0.10 on
the logit scale, far = 0.60 or more. Positive means the model is worse than the market.

## By forward season

| Season | Near band | Far band | Pattern |
| --- | --- | --- | --- |
| 2122 | +0.0004 [-0.0008, +0.0015] (n=768) | +0.0905 [+0.0414, +0.1406] (n=180) | holds |
| 2223 | -0.0003 [-0.0030, +0.0021] (n=786) | +0.0840 [+0.0455, +0.1410] (n=181) | holds |

**Verdict: reproduced in both forward seasons.** The pre-registered rule required the far-band deficit to exceed the
near-band deficit and its interval to exclude zero, in both seasons.

## By division (descriptive)

| Division | Near band | Far band |
| --- | --- | --- |
| D1 | -0.0047 [-0.0090, -0.0005] (n=151) | +0.1986 [+0.1942, +0.2025] (small sample) (n=45) |
| E0 | +0.0000 [-0.0020, +0.0018] (n=230) | +0.0841 [+0.0354, +0.1389] (small sample) (n=34) |
| E1 | +0.0004 [-0.0008, +0.0018] (n=350) | +0.0862 [-0.3456, +0.1726] (small sample) (n=6) |
| F1 | +0.0015 [+0.0013, +0.0017] (n=195) | +0.1006 [+0.0564, +0.1428] (small sample) (n=45) |
| I1 | -0.0008 [-0.0009, -0.0008] (n=196) | +0.0287 [+0.0280, +0.0297] (small sample) (n=40) |
| N1 | -0.0026 [-0.0055, -0.0003] (n=151) | +0.0732 [+0.0460, +0.1046] (small sample) (n=84) |
| P1 | +0.0034 [+0.0021, +0.0048] (n=128) | +0.1473 [+0.1128, +0.1772] (small sample) (n=41) |
| SP1 | +0.0033 [-0.0002, +0.0073] (n=153) | +0.0199 [-0.0103, +0.0409] (small sample) (n=66) |

Division cells are descriptive and several are small; a cell under 100 fixtures is marked and
is not used in any conclusion. With eight divisions split into two bands these intervals are wide by
construction, and no division is tested against another.

## What this supports

The ordering reproduces in both forward seasons, so E18 can be cited as a seasonal-robust pattern within this pilot rather than a pooled artefact.

Either way, E19 stands: no shrinkage policy beat market-only, so a disagreement pattern — reproduced
or not — does not create a deployable edge on this corpus.

## Limits

- Two forward seasons from one corpus; reproduction here is not external validity.
- The bands were fixed from E18 by design, which is honest but means E18 and this test are not
  independent evidence about the band boundaries themselves.
- Closing prices without timestamps throughout.
