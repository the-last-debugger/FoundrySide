"""Workstream 1: does recalibration close the gap, or does the model lack information?

The gap diagnosis said the model is both miscalibrated and much less resolved than the market.
This tests the first half: if a monotone recalibration of the model's probabilities recovers
most of the log-loss gap, the failure is a mapping problem. If it recovers almost nothing, the
probabilities were already ordered correctly and the information is simply not there.

**Fit and evaluation never share outcomes.** The calibrator is fitted on two pilot seasons and
evaluated on the third, rotated over all three (leave-one-season-out). Every calibrated
prediction in the report is out-of-fold.

    python research/calibration_study.py

Writes research/CALIBRATION_STUDY.md.
"""

from __future__ import annotations

import csv
import math
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research"))

import gap_diagnosis  # noqa: E402
import report_stamp   # noqa: E402

OUT = ROOT / "research" / "CALIBRATION_STUDY.md"
DELTAS = ROOT / "research" / "pilot_deltas.csv"


def load() -> list[dict]:
    rows = []
    with DELTAS.open(encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            if r["phase"] != "pilot":
                continue
            rows.append({"season": r["season"], "cluster": r["cluster"],
                         "p": float(r["p_model"]), "y": int(r["y"])})
    return rows


def logit(p: float) -> float:
    p = min(max(p, 1e-6), 1 - 1e-6)
    return math.log(p / (1 - p))


def sigmoid(z: float) -> float:
    return 1 / (1 + math.exp(-max(-30.0, min(30.0, z))))


def logloss(p: float, y: int) -> float:
    p = min(max(p, 1e-6), 1 - 1e-6)
    return -math.log(p) if y else -math.log(1 - p)


def fit_platt(rows: list[dict]) -> tuple[float, float]:
    """Logistic calibration a·logit(p) + b, by Newton's method on two parameters."""
    a, b = 1.0, 0.0
    for _ in range(60):
        g_a = g_b = 0.0
        h_aa = h_ab = h_bb = 0.0
        for r in rows:
            z = a * logit(r["p"]) + b
            q = sigmoid(z)
            err = q - r["y"]
            x = logit(r["p"])
            w = q * (1 - q)
            g_a += err * x
            g_b += err
            h_aa += w * x * x
            h_ab += w * x
            h_bb += w
        det = h_aa * h_bb - h_ab * h_ab
        if abs(det) < 1e-12:
            break
        da = (h_bb * g_a - h_ab * g_b) / det
        db = (h_aa * g_b - h_ab * g_a) / det
        a -= da
        b -= db
        if abs(da) < 1e-9 and abs(db) < 1e-9:
            break
    return a, b


def fit_isotonic(rows: list[dict]) -> list[tuple[float, float]]:
    """Pool-adjacent-violators on (p, y), returning a step function as breakpoints."""
    ordered = sorted(rows, key=lambda r: r["p"])
    blocks: list[list[float]] = []      # [sum_p, sum_y, count]
    for r in ordered:
        blocks.append([r["p"], float(r["y"]), 1.0])
        while len(blocks) > 1 and (blocks[-2][1] / blocks[-2][2]) > (blocks[-1][1] / blocks[-1][2]):
            p2, y2, c2 = blocks.pop()
            p1, y1, c1 = blocks.pop()
            blocks.append([p1 + p2, y1 + y2, c1 + c2])
    out, total = [], 0.0
    for _p, y, c in blocks:
        total += c
        out.append((total, y / c))
    return out


def apply_isotonic(steps: list[tuple[float, float]], p: float) -> float:
    for boundary, value in steps:
        if p <= boundary:
            return value
    return steps[-1][1]


def evaluate(rows: list[dict], key: str) -> dict[str, float]:
    n = len(rows)
    ll = statistics.mean(logloss(r[key], r["y"]) for r in rows)
    brier = statistics.mean((r[key] - r["y"]) ** 2 for r in rows)
    base = statistics.mean(r["y"] for r in rows)
    return {"logloss": ll, "brier": brier, "uncertainty": base * (1 - base), "n": float(n)}


def main() -> int:
    rows = load()
    seasons = sorted({r["season"] for r in rows})

    for r in rows:
        r["platt"] = r["p"]
        r["isotonic"] = r["p"]

    fold_report = []
    for held in seasons:
        train = [r for r in rows if r["season"] != held]
        test = [r for r in rows if r["season"] == held]
        a, b = fit_platt(train)
        steps = fit_isotonic(train)
        for r in test:
            r["platt"] = sigmoid(a * logit(r["p"]) + b)
            r["isotonic"] = apply_isotonic(steps, r["p"])
        fold_report.append((held, len(test), a, b,
                            evaluate(test, "p")["logloss"],
                            evaluate(test, "platt")["logloss"],
                            evaluate(test, "isotonic")["logloss"]))

    raw = evaluate(rows, "p")
    platt = evaluate(rows, "platt")
    iso = evaluate(rows, "isotonic")

    lines = [
        report_stamp.stamp(Path(__file__)),
        "",
        "# Calibration study — does recalibrating recover the gap?",
        "",
        "Out-of-fold by construction: the calibrator is fitted on two pilot seasons and",
        "evaluated on the third, rotated over all three. No calibrated prediction in this",
        "report was produced by a map that had seen its own outcome.",
        "",
        "| Forecast | Log loss | Brier |",
        "| --- | --- | --- |",
        f"| Raw model | {raw['logloss']:.4f} | {raw['brier']:.4f} |",
        f"| Platt (a·logit+b) | {platt['logloss']:.4f} | {platt['brier']:.4f} |",
        f"| Isotonic | {iso['logloss']:.4f} | {iso['brier']:.4f} |",
        "",
        "## Per held-out season",
        "",
        "| Held out | n | Platt a | Platt b | Raw | Platt | Isotonic |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for held, n, a, b, r_ll, p_ll, i_ll in fold_report:
        lines.append(f"| {held} | {n:,} | {a:.3f} | {b:+.3f} | {r_ll:.4f} | {p_ll:.4f} | "
                     f"{i_ll:.4f} |")

    best = min(("raw", raw["logloss"]), ("platt", platt["logloss"]),
               ("isotonic", iso["logloss"]), key=lambda kv: kv[1])
    gain = raw["logloss"] - best[1]
    lines += [
        "",
        "## Reading",
        "",
        f"Best calibrated variant: **{best[0]}**, {gain:+.4f} nats against the raw model.",
        f"Platt moves log loss by {raw['logloss'] - platt['logloss']:+.4f} and isotonic by "
        f"{raw['logloss'] - iso['logloss']:+.4f}.",
        "",
        "Interpretation depends on the size of that gain relative to the gap to the market",
        "(about 0.025 nats). A calibration gain of a few thousandths leaves the gap essentially",
        "where it was, which is the resolution failure the decomposition described. A gain",
        "close to the whole gap would mean the model had the ordering and lost it in the",
        "mapping — a very different diagnosis.",
        "",
        "## Limits",
        "",
        "- Three seasons means three folds; the fold-to-fold spread is the honest uncertainty,",
        "  and there is no confidence interval on the aggregate beyond that.",
        "- The calibrator is fitted on two seasons that were themselves collected online under",
        "  the same T−90 proxy, so any timing error is shared by fit and evaluation.",
        "- Isotonic is flexible enough to fit noise at this sample size; its per-fold numbers",
        "  should be read against Platt's rather than on their own.",
        "- The market comparator is unchanged and is a closing price with no observation",
        "  timestamp.",
    ]
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"raw={raw['logloss']:.4f} platt={platt['logloss']:.4f} iso={iso['logloss']:.4f}")
    print(f"best={best[0]} gain={gain:+.4f}")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
