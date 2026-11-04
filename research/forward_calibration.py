"""Forward-only calibration — is the Platt gain deployable, or an artefact of seeing the future?

The calibration study fits on two seasons and evaluates on the third, rotating. That is
leave-one-season-out, and it is stronger than training and testing on the same data, but it is not
what a product would do: LOSO lets a fold's calibrator be fitted on seasons that come *after* the
fold it is scored on.

This tests the deployable version. Fit on seasons strictly before the target, evaluate forward:

- 2021 alone predicts 2122;
- 2021 and 2122 predict 2223.

If the Platt gain survives forward transfer, a user could have had it at the time. If it only
appears under LOSO, it was partly hindsight.

    python research/forward_calibration.py

Writes research/FORWARD_CALIBRATION.md.
"""

from __future__ import annotations

import csv
import math
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research"))

import calibration_study as cs   # noqa: E402
import report_stamp              # noqa: E402

OUT = ROOT / "research" / "FORWARD_CALIBRATION.md"
DELTAS = ROOT / "research" / "pilot_deltas.csv"


def load() -> list[dict]:
    rows = []
    with DELTAS.open(encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            if r["phase"] != "pilot":
                continue
            rows.append({"season": r["season"], "p": float(r["p_model"]),
                         "p_market": float(r["p_market"]), "y": int(r["y"])})
    return rows


def main() -> int:
    rows = load()
    seasons = sorted({r["season"] for r in rows})

    folds = []
    for held in seasons[1:]:                      # nothing can predict the first season forward
        train = [r for r in rows if r["season"] < held]
        test = [r for r in rows if r["season"] == held]
        if not train or not test:
            continue
        a, b = cs.fit_platt([{"p": r["p"], "y": r["y"]} for r in train])
        raw_ll = statistics.mean(cs.logloss(r["p"], r["y"]) for r in test)
        cal_ll = statistics.mean(cs.logloss(cs.sigmoid(a * cs.logit(r["p"]) + b), r["y"])
                                 for r in test)
        mkt_ll = statistics.mean(cs.logloss(r["p_market"], r["y"]) for r in test)
        folds.append({"held": held, "n": len(test), "a": a, "b": b,
                      "raw": raw_ll, "cal": cal_ll, "market": mkt_ll})

    # The LOSO figure, for comparison - the same aggregate the calibration study reports.
    loso = []
    for held in seasons:
        train = [{"p": r["p"], "y": r["y"]} for r in rows if r["season"] != held]
        a, b = cs.fit_platt(train)
        test = [r for r in rows if r["season"] == held]
        loso.append(statistics.mean(cs.logloss(cs.sigmoid(a * cs.logit(r["p"]) + b), r["y"])
                                    for r in test))
    raw_all = statistics.mean(cs.logloss(r["p"], r["y"]) for r in rows)

    forward_gains = [f["raw"] - f["cal"] for f in folds]
    doc = f"""{report_stamp.stamp(Path(__file__))}

# Forward-only calibration — is the gain deployable?

The calibration study fits on two seasons and scores the third, rotating. That is stronger than an
in-sample fit but it is not what a product would do: leave-one-season-out allows the calibrator for
a given fold to be trained on seasons that come after it. This evaluates the deployable version,
training only on seasons that precede the target.

## Forward folds

| Trained on | Evaluated on | n | Raw model | Platt (forward) | Market | Gain |
| --- | --- | --- | --- | --- | --- | --- |
""" + "\n".join(
        f"| seasons before {f['held']} | {f['held']} | {f['n']:,} | {f['raw']:.4f} | "
        f"{f['cal']:.4f} | {f['market']:.4f} | {f['raw'] - f['cal']:+.4f} |"
        for f in folds) + f"""

## The comparison that matters

| Estimator | Mean log loss |
| --- | --- |
| Raw model, all pilot rows | {raw_all:.4f} |
| Platt under leave-one-season-out | {statistics.mean(loso):.4f} |
| Platt under forward-only transfer | {statistics.mean(f['cal'] for f in folds):.4f} |

Forward gain: **{statistics.mean(forward_gains):+.4f} nats** per fold on average; LOSO gain over the
same raw baseline: **{raw_all - statistics.mean(loso):+.4f}**.

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
"""
    OUT.write_text(doc, encoding="utf-8")

    for f in folds:
        print(f"train<{f['held']} on {f['held']}: raw={f['raw']:.4f} cal={f['cal']:.4f} "
              f"market={f['market']:.4f} gain={f['raw']-f['cal']:+.4f} slope={f['a']:.3f}")
    print(f"forward mean gain={statistics.mean(forward_gains):+.4f} "
          f"loso gain={raw_all - statistics.mean(loso):+.4f}")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
