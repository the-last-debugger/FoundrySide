<!-- generated-by: forward_calibration.py sha256=a08fbe97800f -->

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

## The comparison that matters

| Estimator | Mean log loss |
| --- | --- |
| Raw model, all pilot rows | 0.6988 |
| Platt under leave-one-season-out | 0.6874 |
| Platt under forward-only transfer | 0.6876 |

Forward gain: **+0.0102 nats** per fold on average; LOSO gain over the
same raw baseline: **+0.0114**.

## Reading

The forward gain is the only one a user could actually have had. If it is close to the LOSO gain,
recalibration is deployable: a calibrator fitted on completed seasons transferred to the next one
without needing to see it. If it is materially smaller, part of the LOSO gain came from information
that was not available at the time, and the honest product claim is the smaller number.

Either way the market comparator is unchanged and the deficit is not closed by calibration alone.

## Limits

- Two forward folds from three pilot seasons: a small sample of transfers, and the first season
  cannot be predicted forward at all.
- The fitted slope is reported per fold so a reader can see whether the map is stable; a slope that
  swings between folds means the calibration is not a fixed property of the model.
- One corpus, one market, closing prices without timestamps.
