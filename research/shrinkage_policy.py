"""Disagreement-aware shrinkage, per docs/PREREG-SHRINKAGE.md.

Implements the six policies exactly as pre-registered, fits parameters only on seasons strictly
before each evaluation season, and scores each later pilot season once.

    python research/shrinkage_policy.py

Writes research/SHRINKAGE_POLICY.md.
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
import report_stamp              # noqa: E402

OUT = ROOT / "research" / "SHRINKAGE_POLICY.md"
DELTAS = ROOT / "research" / "pilot_deltas.csv"
GRID = [round(x * 0.05, 2) for x in range(0, 31)]     # 0.00 .. 1.50
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
    return rows


def calibrated(rows: list[dict], upto: str) -> dict[int, float]:
    """Forward calibration using seasons strictly before `upto`; rows before that get their map."""
    seasons = sorted({r["season"] for r in rows})
    out = {id(r): r["p"] for r in rows}
    for held in seasons:
        # Include the target season itself: its map is fitted on prior seasons only, which is the
        # whole point. Breaking at equality left the evaluation season raw.
        if held > upto:
            break
        train = [{"p": r["p"], "y": r["y"]} for r in rows if r["season"] < held]
        if len(train) < 100:
            continue
        a, b = cs.fit_platt(train)
        for r in rows:
            if r["season"] == held:
                out[id(r)] = cs.sigmoid(a * cs.logit(r["p"]) + b)
    return out


def departure(r: dict, p_cal: float) -> float:
    return abs(cs.logit(p_cal) - cs.logit(r["p_market"]))


def blend(p_model: float, p_market: float, weight: float) -> float:
    return cs.sigmoid(weight * cs.logit(p_model) + (1 - weight) * cs.logit(p_market))


def policy_predictions(rows: list[dict], p_cal: dict[int, float], name: str,
                       param: float | None) -> list[float]:
    out = []
    for r in rows:
        pm = p_cal[id(r)]
        pk = r["p_market"]
        d = departure(r, pm)
        if name == "market":
            out.append(pk)
        elif name == "model":
            out.append(pm)
        elif name == "fixed 0.5":
            out.append(blend(pm, pk, 0.5))
        elif name == "shrink-linear":
            w = max(0.0, 1.0 - d / param) if param else 0.0
            out.append(blend(pm, pk, w))
        elif name == "shrink-threshold":
            out.append(pk if d > (param or 0.0) else pm)
        elif name == "market-fallback":
            out.append(pk if d > 0.6 else pm)
        else:
            raise ValueError(name)
    return out


def loss(rows: list[dict], preds: list[float]) -> float:
    return statistics.mean(cs.logloss(p, r["y"]) for p, r in zip(preds, rows))


def fit_param(rows: list[dict], name: str) -> float:
    """Grid search minimising log loss on the fitting rows only."""
    p_cal = calibrated(rows, "9999")
    best, best_loss = None, float("inf")
    for param in GRID:
        if param == 0 and name == "shrink-linear":
            continue
        value = loss(rows, policy_predictions(rows, p_cal, name, param))
        if value < best_loss:
            best, best_loss = param, value
    return float(best)



def decomposition(rows: list[dict], preds: list[float]) -> tuple[float, float]:
    """Binned reliability and resolution, as the pre-registration promised."""
    bins: dict[int, list[tuple[float, int]]] = {}
    for p, r in zip(preds, rows):
        bins.setdefault(min(9, int(p * 10)), []).append((p, r["y"]))
    n = len(rows)
    base = statistics.mean(r["y"] for r in rows)
    rel = res = 0.0
    for group in bins.values():
        w = len(group) / n
        mp = statistics.mean(p for p, _ in group)
        my = statistics.mean(y for _, y in group)
        rel += w * (mp - my) ** 2
        res += w * (my - base) ** 2
    return rel, res


def coverage(rows: list[dict], preds: list[float]) -> float:
    """Share of fixtures where the policy departs from the market by more than 0.01."""
    return statistics.mean(1.0 if abs(p - r["p_market"]) > 0.01 else 0.0
                           for p, r in zip(preds, rows))


def main() -> int:
    rows = load()
    seasons = sorted({r["season"] for r in rows})
    evaluation = seasons[1:]

    # Fit on all seasons before each evaluation season; score that season once.
    per_season = {}
    fitted = {}
    for held in evaluation:
        fit_rows = [r for r in rows if r["season"] < held]
        test_rows = [r for r in rows if r["season"] == held]
        params = {
            "shrink-linear": fit_param(fit_rows, "shrink-linear"),
            "shrink-threshold": fit_param(fit_rows, "shrink-threshold"),
        }
        fitted[held] = params
        p_cal_test = calibrated(rows, held)
        per_season[held] = {"n": len(test_rows)}
        for name in ("market", "model", "fixed 0.5", "market-fallback"):
            per_season[held][name] = loss(
                test_rows, policy_predictions(test_rows, p_cal_test, name, None))
        for name in ("shrink-linear", "shrink-threshold"):
            per_season[held][name] = loss(
                test_rows, policy_predictions(test_rows, p_cal_test, name, params[name]))

    names = ["market", "model", "fixed 0.5", "shrink-linear", "shrink-threshold",
             "market-fallback"]
    total_n = sum(per_season[s]["n"] for s in evaluation)
    aggregate = {n: sum(per_season[s][n] * per_season[s]["n"] for s in evaluation) / total_n
                 for n in names}

    # Cluster bootstrap on the improvement over the market, pooled over evaluation seasons.
    eval_rows = [r for r in rows if r["season"] in evaluation]
    p_cal_all = calibrated(rows, "9999")
    clusters: dict[str, list[int]] = {}
    for i, r in enumerate(eval_rows):
        clusters.setdefault(r["cluster"], []).append(i)
    keys = sorted(clusters)
    rng = np.random.default_rng(SEED)

    preds = {}
    for name in names:
        param = None
        preds[name] = policy_predictions(eval_rows, p_cal_all, name, param)

    gains = {n: [] for n in names}
    for _ in range(BOOTSTRAPS):
        flat = [i for k in (keys[rng.integers(0, len(keys))] for _ in keys) for i in clusters[k]]
        base = loss([eval_rows[i] for i in flat], [preds["market"][i] for i in flat])
        for n in names:
            gains[n].append(base - loss([eval_rows[i] for i in flat], [preds[n][i] for i in flat]))
    intervals = {n: (sorted(gains[n])[int(0.025 * BOOTSTRAPS)],
                     sorted(gains[n])[int(0.975 * BOOTSTRAPS) - 1]) for n in names}

    doc = f"""{report_stamp.stamp(Path(__file__))}

# Disagreement-aware shrinkage — pre-registered test

Specification committed at `docs/PREREG-SHRINKAGE.md` before this script existed. Six policies,
parameters fitted on prior seasons only, each evaluation season scored once.

## Per-season log loss

| Season | n | {' | '.join(names)} |
| --- | --- | {' | '.join('---' for _ in names)} |
""" + "\n".join(
        f"| {s} | {per_season[s]['n']:,} | "
        + " | ".join(f"{per_season[s][n]:.4f}" for n in names) + " |"
        for s in evaluation) + f"""

## Pooled over evaluation seasons

| Policy | Log loss | Gain vs market | Cluster 95% | Reliability | Resolution | Coverage |
| --- | --- | --- | --- | --- | --- | --- |
""" + "\n".join(
        f"| {n} | {aggregate[n]:.4f} | {aggregate['market'] - aggregate[n]:+.4f} | "
        f"[{intervals[n][0]:+.4f}, {intervals[n][1]:+.4f}] | "
        f"{decomposition(eval_rows, preds[n])[0]:.4f} | {decomposition(eval_rows, preds[n])[1]:.4f} | "
        f"{coverage(eval_rows, preds[n]):.1%} |"
        for n in names) + f"""

Fitted parameters: {', '.join(f"{s}: d0={fitted[s]['shrink-linear']:.2f}, t={fitted[s]['shrink-threshold']:.2f}" for s in evaluation)}.

## Verdict, against the pre-registered rule

The rule required a policy to beat **both** the market and the model, with a cluster interval on
its improvement over the market excluding zero.

""" + "\n".join(
        f"- **{n}**: {'beats market' if aggregate[n] < aggregate['market'] else 'does not beat market'}, "
        f"{'beats model' if aggregate[n] < aggregate['model'] else 'does not beat model'}, "
        f"interval {'excludes' if intervals[n][0] > 0 else 'includes'} zero."
        for n in names) + f"""

## Reading

If no policy satisfies both conditions, the pre-registered stop criterion applies: the line stops
and the next work is robustness of the E18 finding rather than further policy variants.

The fitted values matter for interpretation as much as the losses: an interior optimum says the
model carries some value up to a departure size, while a boundary hit says the fitting wanted to
shrink everything or nothing.

## Limits

- Two forward folds, one corpus; a rule that works on both is promising here, not validated.
- Closing prices without timestamps: this is accuracy against a closing benchmark, not executable
  value.
- The market baseline is the same de-vigged price used throughout; the confirmatory slice is
  untouched.
"""
    OUT.write_text(doc, encoding="utf-8", newline="\n")

    for n in names:
        print(f"{n}: {aggregate[n]:.4f} gain={aggregate['market'] - aggregate[n]:+.4f} "
              f"[{intervals[n][0]:+.4f},{intervals[n][1]:+.4f}]")
    print("fitted:", fitted)
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
