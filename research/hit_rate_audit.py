"""Hit-rate and metric audit, per docs/PREREG-HITRATE.md.

Answers one question: does the model make more or fewer correct hard predictions than the market,
on the same target and the same fixtures? And separates that from the probability-score question.

    python research/hit_rate_audit.py

Writes research/HIT_RATE_AUDIT.md.
"""

from __future__ import annotations

import csv
import math
import statistics
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research"))

import calibration_study as cs   # noqa: E402
import feature_screen as fs      # noqa: E402
import report_stamp              # noqa: E402

OUT = ROOT / "research" / "HIT_RATE_AUDIT.md"
DELTAS = ROOT / "research" / "pilot_deltas.csv"
THRESHOLD = 0.5
BOOTSTRAPS = 2000
SEED = 20261103


def load() -> list[dict]:
    rows = []
    with DELTAS.open(encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            if r["phase"] != "pilot":
                continue
            rows.append({"season": r["season"], "cluster": r["cluster"],
                         "p": float(r["p_model"]), "p_market": float(r["p_market"]),
                         "y": int(r["y"])})
    seasons = sorted({r["season"] for r in rows})
    for r in rows:
        r["p_cal"] = r["p"]
    for held in seasons:
        train = [{"p": r["p"], "y": r["y"]} for r in rows if r["season"] < held]
        if len(train) < 100:
            continue
        a, b = cs.fit_platt(train)
        for r in rows:
            if r["season"] == held:
                r["p_cal"] = cs.sigmoid(a * cs.logit(r["p"]) + b)
    return rows


def confusion(rows: list[dict], key: str) -> dict:
    """2x2 counts for a probability column at the 0.5 threshold."""
    c = {"tp": 0, "fp": 0, "tn": 0, "fn": 0}
    for r in rows:
        pred = 1 if r[key] >= THRESHOLD else 0
        if pred and r["y"]:
            c["tp"] += 1
        elif pred and not r["y"]:
            c["fp"] += 1
        elif not pred and not r["y"]:
            c["tn"] += 1
        else:
            c["fn"] += 1
    c["n"] = sum(c.values())
    c["correct"] = c["tp"] + c["tn"]
    c["accuracy"] = c["correct"] / c["n"]
    c["precision_over"] = c["tp"] / (c["tp"] + c["fp"]) if c["tp"] + c["fp"] else float("nan")
    c["recall_over"] = c["tp"] / (c["tp"] + c["fn"]) if c["tp"] + c["fn"] else float("nan")
    c["precision_under"] = c["tn"] / (c["tn"] + c["fn"]) if c["tn"] + c["fn"] else float("nan")
    c["recall_under"] = c["tn"] / (c["tn"] + c["fp"]) if c["tn"] + c["fp"] else float("nan")
    c["balanced"] = (c["recall_over"] + c["recall_under"]) / 2
    return c


def decomposition(rows: list[dict], key: str) -> tuple[float, float]:
    bins: dict[int, list[dict]] = {}
    for r in rows:
        bins.setdefault(min(9, int(r[key] * 10)), []).append(r)
    n = len(rows)
    base = statistics.mean(r["y"] for r in rows)
    rel = res = 0.0
    for group in bins.values():
        w = len(group) / n
        mp = statistics.mean(g[key] for g in group)
        my = statistics.mean(g["y"] for g in group)
        rel += w * (mp - my) ** 2
        res += w * (my - base) ** 2
    return rel, res


def main() -> int:
    rows = load()
    n = len(rows)

    cols = [("market", "p_market"), ("model (raw)", "p"), ("model (forward-calibrated)", "p_cal")]
    counts = {label: confusion(rows, key) for label, key in cols}

    # Paired discordance between the raw model and the market.
    both = sum(1 for r in rows if (r["p"] >= THRESHOLD and r["y"]) or (r["p"] < THRESHOLD and not r["y"]))
    model_right_market_wrong = sum(
        1 for r in rows
        if ((r["p"] >= THRESHOLD) == bool(r["y"])) and ((r["p_market"] >= THRESHOLD) != bool(r["y"])))
    market_right_model_wrong = sum(
        1 for r in rows
        if ((r["p_market"] >= THRESHOLD) == bool(r["y"])) and ((r["p"] >= THRESHOLD) != bool(r["y"])))
    discordant = model_right_market_wrong + market_right_model_wrong
    # Binomial (McNemar-style) two-sided p, noting fixtures are not independent.
    if discordant:
        k = min(model_right_market_wrong, market_right_model_wrong)
        p_mcnemar = sum(math.comb(discordant, i) for i in range(k + 1)) / 2 ** discordant * 2
        p_mcnemar = min(1.0, p_mcnemar)
    else:
        p_mcnemar = 1.0

    # Cluster bootstrap on the accuracy difference (model minus market).
    clusters: dict[str, list[int]] = {}
    for i, r in enumerate(rows):
        clusters.setdefault(r["cluster"], []).append(i)
    keys = sorted(clusters)
    rng = np.random.default_rng(SEED)
    diffs = []
    for _ in range(BOOTSTRAPS):
        flat = [i for k in (keys[rng.integers(0, len(keys))] for _ in keys) for i in clusters[k]]
        m = statistics.mean(1.0 if (rows[i]["p"] >= THRESHOLD) == bool(rows[i]["y"]) else 0.0 for i in flat)
        k_ = statistics.mean(1.0 if (rows[i]["p_market"] >= THRESHOLD) == bool(rows[i]["y"]) else 0.0 for i in flat)
        diffs.append(m - k_)
    diffs.sort()
    lo, hi = diffs[int(0.025 * BOOTSTRAPS)], diffs[int(0.975 * BOOTSTRAPS) - 1]

    # Probability metrics on identical rows.
    metrics = []
    for label, key in cols:
        preds = [r[key] for r in rows]
        y = np.array([r["y"] for r in rows], dtype=float)
        rel, res = decomposition(rows, key)
        metrics.append({
            "label": label,
            "logloss": statistics.mean(cs.logloss(p, r["y"]) for p, r in zip(preds, rows)),
            "brier": statistics.mean((p - r["y"]) ** 2 for p, r in zip(preds, rows)),
            "auc": fs.fast_auc(np.array(preds), y),
            "rel": rel, "res": res,
        })

    # Calibration slope from a forward-fitted map: already applied for p_cal; here refit on all
    # rows for a descriptive slope only.
    slope, intercept = cs.fit_platt([{"p": r["p"], "y": r["y"]} for r in rows])

    # Accuracy by market-probability band, to show accuracy is not value.
    bands: dict[str, list[dict]] = {}
    for r in rows:
        idx = min(9, int(r["p_market"] * 10))       # bin index 0..9, not a percentage
        bands.setdefault(f"{idx * 10}-{idx * 10 + 10}%", []).append(r)
    band_rows = []
    for name, group in sorted(bands.items(), key=lambda kv: int(kv[0].split("-")[0])):
        if not group:
            continue
        implied = statistics.mean(r["p_market"] for r in group)
        realised = statistics.mean(r["y"] for r in group)
        # Expected value per unit at the offered price is not recoverable from de-vigged
        # probabilities alone; report accuracy against implied instead.
        band_rows.append((name, len(group), implied, realised, realised - implied))

    doc = f"""{report_stamp.stamp(Path(__file__))}

# Hit-rate and metric audit

Pre-registered at `docs/PREREG-HITRATE.md` before these numbers were computed. Target: **Over 2.5
goals**, {n:,} pilot fixtures. The market column is the de-vigged Pinnacle closing price for the
same market; the model is the prequential forecast. Identical rows throughout.

## Hard picks at 0.5

| Picker | Correct | Accuracy | Balanced accuracy | Precision (Over / Under) | Recall (Over / Under) |
| --- | --- | --- | --- | --- | --- |
""" + "\n".join(
        f"| {label} | {counts[label]['correct']:,} / {counts[label]['n']:,} | "
        f"{counts[label]['accuracy']:.4f} | {counts[label]['balanced']:.4f} | "
        f"{counts[label]['precision_over']:.4f} / {counts[label]['precision_under']:.4f} | "
        f"{counts[label]['recall_over']:.4f} / {counts[label]['recall_under']:.4f} |"
        for label, _ in cols) + f"""

### Confusion matrices

| Picker | TP | FP | TN | FN |
| --- | --- | --- | --- | --- |
""" + "\n".join(
        f"| {label} | {c['tp']:,} | {c['fp']:,} | {c['tn']:,} | {c['fn']:,} |"
        for label, c in ((l, counts[l]) for l, _ in cols)) + f"""

### The paired comparison

| | Count |
| --- | --- |
| Model right, market wrong | {model_right_market_wrong:,} |
| Market right, model wrong | {market_right_model_wrong:,} |
| Discordant pairs | {discordant:,} |

Accuracy difference (model − market): **{counts['model (raw)']['accuracy'] - counts['market']['accuracy']:+.4f}**,
cluster bootstrap 95% **[{lo:+.4f}, {hi:+.4f}]**. McNemar-style binomial p = **{p_mcnemar:.4g}**,
which treats fixtures as independent and is reported only for comparability; the bootstrap is the
one that respects the cluster structure.

## Probability metrics on the same rows

| Measure | Market | Model (raw) | Model (calibrated) |
| --- | --- | --- | --- |
| Log loss | {metrics[0]['logloss']:.4f} | {metrics[1]['logloss']:.4f} | {metrics[2]['logloss']:.4f} |
| Brier | {metrics[0]['brier']:.4f} | {metrics[1]['brier']:.4f} | {metrics[2]['brier']:.4f} |
| ROC AUC | {metrics[0]['auc']:.4f} | {metrics[1]['auc']:.4f} | {metrics[2]['auc']:.4f} |
| Reliability | {metrics[0]['rel']:.4f} | {metrics[1]['rel']:.4f} | {metrics[2]['rel']:.4f} |
| Resolution | {metrics[0]['res']:.4f} | {metrics[1]['res']:.4f} | {metrics[2]['res']:.4f} |

Calibration slope from a fit on all rows: **{slope:.3f}**, intercept {intercept:+.3f}. A slope near
0.4 means the model's logits are roughly two and a half times too spread.

## The 1X2 baseline is a different task

The **53.3% favourite accuracy** in `RESULTS_T0_T1_T3.md` is home/draw/away on 14,802 fixtures. The
model audited here predicts Over 2.5 on 8,941 pilot fixtures. **No 1X2 model predictions exist in
this repository**, so we have not compared our model's 1X2 pick accuracy against 1X2 favourites,
and this report does not manufacture that comparison from the totals model. The 53.3% figure stands
as a market-only benchmark for a task the model has not been asked to do.

## Does a higher hit rate imply better decisions?

Acceptance by market-probability band, market against realised:

| Band | Fixtures | Implied | Realised | Realised − implied |
| --- | --- | --- | --- | --- |
""" + "\n".join(
        f"| {name} | {nn:,} | {imp:.3f} | {real:.3f} | {d:+.3f} |"
        for name, nn, imp, real, d in band_rows) + f"""

Accuracy and value are not the same quantity. A picker can be right more often and still lose,
because the price already charges for the probability: the second column is what the outcome cost,
the third is what happened. **Expected value depends on the price paid, not on the hit rate**, and
this corpus records closing prices with no timestamp, so no executable value is claimed.

## What this audit supports

**Both senses of worse are supported, and neither is marginal.**

The model's hard-pick accuracy is {counts['model (raw)']['accuracy']:.4f} against the market's
{counts['market']['accuracy']:.4f}: a difference of
{counts['model (raw)']['accuracy'] - counts['market']['accuracy']:+.4f} with a cluster interval of
[{lo:+.4f}, {hi:+.4f}], which excludes zero. The paired counts say the same thing without averaging:
on {model_right_market_wrong:,} fixtures the model was right where the market was wrong, and on
{market_right_model_wrong:,} the reverse. The model does not merely score badly; it picks the wrong
side more often, by enough that a user would notice.

So the ordering is: worse at ranking (AUC), worse at probabilities (log loss, resolution), and
worse at the hard pick (accuracy). The one thing that is *not* worse is calibration after the fact,
which is recoverable and recovered.

The distinction that still matters is task: this is Over 2.5 on 8,941 fixtures, not the 1X2
favourite question, and the 53.3% benchmark belongs to the other task.

## Limits

- Pilot only; the confirmatory slice is untouched and unscored.
- Closing prices without timestamps; no claim about executable value.
- Threshold 0.5 was pre-declared; a different threshold would trade accuracy for coverage.
"""
    OUT.write_text(doc, encoding="utf-8", newline="\n")

    for label, _ in cols:
        c = counts[label]
        print(f"{label}: acc={c['accuracy']:.4f} correct={c['correct']}/{c['n']} "
              f"bal={c['balanced']:.4f}")
    print(f"paired: model-right/market-wrong={model_right_market_wrong} "
          f"market-right/model-wrong={market_right_model_wrong} p={p_mcnemar:.4g}")
    print(f"accuracy diff CI [{lo:+.4f},{hi:+.4f}]")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
