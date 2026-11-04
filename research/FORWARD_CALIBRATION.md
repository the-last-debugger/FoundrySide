<!-- generated-by: forward_calibration.py sha256=a1f1185cd14d -->

# Forward-only calibration — is the gain deployable?

The calibration study fits on two seasons and scores the third, rotating. That is stronger than an
in-sample fit but it is not what a product would do: leave-one-season-out allows the calibrator for
a given fold to be trained on seasons that come after it. This evaluates the deployable version,
training only on seasons that precede the target.

## Forward folds

| Trained on | Evaluated on | n | Raw model | Platt (forward) | Market | Gain |
| --- | --- | --- | --- | --- | --- | --- |
| seasons before 2122 | 2122 | 2,986 | 0.6950 | 0.6867 | 0.6725 | +0.0083 |
| seasons before 2223 | 2223 | 2,975 | 0.7007 | 0.6886 | 0.6751 | +0.0121 |

## Matched-fold comparison

The forward folds cover two seasons, so comparing their mean against an all-season LOSO mean
compares different populations. These are the same rows under both estimators.

| Season | n | Raw | Platt, LOSO | Platt, forward | Forward gain | LOSO gain |
| --- | --- | --- | --- | --- | --- | --- |
| 2122 | 2,986 | 0.6950 | 0.6866 | 0.6867 | +0.0083 | +0.0084 |
| 2223 | 2,975 | 0.7007 | 0.6886 | 0.6886 | +0.0121 | +0.0121 |

| Estimator, matched folds | Unweighted fold mean | Sample-weighted |
| --- | --- | --- |
| Raw | 0.6979 | 0.6978 |
| Platt, forward | 0.6876 | 0.6876 |
| Platt, LOSO on the same rows | 0.6876 | 0.6876 |

Forward gain on matched rows: **+0.0102 nats** unweighted,
+0.0102
weighted. LOSO gain on the same rows:
+0.0103 unweighted,
+0.0103 weighted.

All-season reference (a different population): raw 0.6988, LOSO 0.6874,
gain +0.0114.

## Reading

On the matched rows the two estimators agree almost exactly: forward transfers lose essentially
nothing against a leave-one-season-out fit on the same seasons. That is the result to quote, and it
is narrower than the earlier "nine tenths" reading, which compared a two-season forward mean with
a three-season LOSO mean and was not like-for-like.

**Transfer is observed in this pilot, not broadly validated.** Two forward folds from one corpus is
a demonstration that the map transfers here, not a guarantee that it transfers across eras,
divisions or a different model family.

Either way the market comparator is unchanged and the deficit is not closed by calibration alone.

## Limits

- Two forward folds from three pilot seasons: a small sample of transfers, and the first season
  cannot be predicted forward at all.
- The fitted slope is reported per fold so a reader can see whether the map is stable; a slope that
  swings between folds means the calibration is not a fixed property of the model.
- One corpus, one market, closing prices without timestamps.
