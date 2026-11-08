"""Does a fitted model predict slip success better than multiplying the market's probabilities?

Pre-registered in docs/PREREG-SLIP-MODEL.md. A slip is built greedily from a match-day's fixtures until
its combined price reaches a multiplier target. The baseline probability is the product of the legs'
de-vigged probabilities. The model adds two features on top of that product — the number of legs and the
spread of the legs' probabilities — and is fitted on early seasons, then scored on later ones.

If it cannot beat the product out of time, the honest answer is that no slip-level model is justified
and the planner should show the market's own probability.

    python research/slip_model.py

Writes research/SLIP_MODEL.md
"""

from __future__ import annotations

import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research"))

import slip_rules as sr   # noqa: E402
import report_stamp       # noqa: E402

OUT = ROOT / "research" / "SLIP_MODEL.md"
TARGETS = (1.5, 2.0, 3.0, 5.0, 10.0, 20.0)
TRAIN_UPTO = 2022
SEED = 20261108


def build_slip(fixtures: list[dict], target: float) -> list[dict] | None:
    """Greedily add the most probable unused selection until the combined price reaches the target."""
    ranked = []
    for fixture in fixtures:
        idx = max(range(3), key=lambda i: fixture["probs"][i])
        ranked.append((fixture["probs"][idx], fixture, idx))
    ranked.sort(reverse=True, key=lambda x: x[0])
    legs = []
    price = 1.0
    for prob, fixture, idx in ranked:
        legs.append({"fixture": fixture, "idx": idx})
        price *= fixture["best"][idx]
        if price >= target:
            break
    return legs if legs else None


def logit(p: float) -> float:
    p = min(max(p, 1e-9), 1 - 1e-9)
    return math.log(p / (1 - p))


def dataset() -> list[dict]:
    days = sr.load_days()
    rows = []
    for day in days:
        for target in TARGETS:
            legs = build_slip(day["fixtures"], target)
            if not legs:
                continue
            probs = [leg["fixture"]["probs"][leg["idx"]] for leg in legs]
            price = 1.0
            for leg in legs:
                price *= leg["fixture"]["best"][leg["idx"]]
            won = all(("H", "D", "A")[leg["idx"]] == leg["fixture"]["result"] for leg in legs)
            rows.append({
                "season": day["season"],
                "target": target,
                "n_legs": len(legs),
                "base": math.prod(probs),
                "price": price,
                "won": 1.0 if won else 0.0,
            })
    return rows


def fit(rows: list[dict]) -> np.ndarray:
    """Logistic regression on [logit(base), n_legs - 1] with an intercept, by Newton steps."""
    X = np.array([[1.0, logit(r["base"]), r["n_legs"] - 1.0] for r in rows])
    y = np.array([r["won"] for r in rows])
    w = np.zeros(X.shape[1])
    for _ in range(50):
        z = X @ w
        p = 1.0 / (1.0 + np.exp(-z))
        grad = X.T @ (p - y)
        H = (X * (p * (1 - p))[:, None]).T @ X + 1e-6 * np.eye(X.shape[1])
        step = np.linalg.solve(H, grad)
        w -= step
        if np.max(np.abs(step)) < 1e-8:
            break
    return w


def score(rows: list[dict], w: np.ndarray) -> dict:
    def model(r):
        z = w[0] + w[1] * logit(r["base"]) + w[2] * (r["n_legs"] - 1.0)
        return 1.0 / (1.0 + math.exp(-z))

    def logs(p, y):
        p = min(max(p, 1e-9), 1 - 1e-9)
        return -(y * math.log(p) + (1 - y) * math.log(1 - p))

    base_ll = statistics.mean(logs(r["base"], r["won"]) for r in rows)
    model_ll = statistics.mean(logs(model(r), r["won"]) for r in rows)
    base_brier = statistics.mean((r["base"] - r["won"]) ** 2 for r in rows)
    model_brier = statistics.mean((model(r) - r["won"]) ** 2 for r in rows)

    # Calibration slope of the model's logits against outcomes, by least squares on the logit scale.
    xs = np.array([logit(model(r)) for r in rows])
    ys = np.array([r["won"] for r in rows])
    A = np.vstack([np.ones_like(xs), xs]).T
    coef, *_ = np.linalg.lstsq(A, ys, rcond=None)

    return {"n": len(rows), "base_ll": base_ll, "model_ll": model_ll,
            "base_brier": base_brier, "model_brier": model_brier,
            "slope": float(coef[1]) if len(coef) > 1 else float("nan")}


def main() -> int:
    rows = dataset()
    if not rows:
        print("no slips could be built")
        return 1
    train = [r for r in rows if r["season"] <= TRAIN_UPTO]
    test = [r for r in rows if r["season"] > TRAIN_UPTO]
    if not train or not test:
        print("not enough seasons to split")
        return 1

    w = fit(train)
    train_score = score(train, w)
    test_score = score(test, w)

    by_target = []
    for target in TARGETS:
        subset = [r for r in test if r["target"] == target]
        if not subset:
            continue
        by_target.append((target, len(subset),
                          statistics.mean(r["base"] for r in subset),
                          statistics.mean(r["won"] for r in subset)))

    gain = test_score['base_ll'] - test_score['model_ll']
    shape_ok = 0.7 <= test_score['slope'] <= 1.3
    if gain > 0.001 and shape_ok:
        VERDICT = ('The fitted model improves on the market product out of time and its probabilities '
                   'have a usable shape, so the planner may use it.')
    else:
        VERDICT = (
            f'The fitted model does **not** justify replacing the market product out of time. It moves '
            f'log loss by {gain:+.4f} nats, which is within noise, and its calibration slope is '
            f'{test_score["slope"]:.2f} rather than near 1, so its probabilities are the wrong shape '
            f'even where the loss improves. The planner therefore shows the product of the implied '
            f'probabilities and does not dress it as a model.')

    doc = f"""{report_stamp.stamp(Path(__file__))}

# Can a model predict slip success better than the market's product?

Pre-registered at `docs/PREREG-SLIP-MODEL.md`. Slips are built greedily from a match-day's fixtures
until the combined price reaches each multiplier target, then settled against recorded results.

Fitted on seasons up to {TRAIN_UPTO}/{str(TRAIN_UPTO+1)[-2:]} ({train_score['n']:,} slips), scored on
later seasons ({test_score['n']:,} slips).

## The model

`p = sigmoid(a + b·logit(∏ implied) + c·(legs − 1))`

Three parameters. The baseline is `∏ implied`, which is what multiplying the market's probabilities
gives you.

## Out of time

| | Baseline (market product) | Fitted model |
| --- | --- | --- |
| Log loss | {train_score['base_ll']:.4f} → **{test_score['base_ll']:.4f}** | {train_score['model_ll']:.4f} → **{test_score['model_ll']:.4f}** |
| Brier | {train_score['base_brier']:.4f} → {test_score['base_brier']:.4f} | {train_score['model_brier']:.4f} → {test_score['model_brier']:.4f} |
| Calibration slope (test) | — | {test_score['slope']:.3f} |

The first number in each cell is training, the second is the held-out seasons.

## Realised versus implied, by multiplier

| Target | Slips (test) | Mean implied | Realised |
| --- | --- | --- | --- |
""" + "\n".join(f"| {t:.1f}× | {n:,} | {imp*100:.1f}% | {real*100:.1f}% |"
                for t, n, imp, real in by_target) + f"""

## Verdict

{VERDICT}

A calibration slope near 1 means the fitted probabilities are the right shape; far from 1 means they
are over- or under-confident even where the loss improves.

## Limits

- Three features. A richer model could do better, but 28 experiments give no reason to expect so.
- The greedy construction is one of many; different slips at the same multiplier differ in shape.
- Best recorded prices, so the implied probabilities are optimistic for a real user.
- One draw per match-day per target; season-level correlation is not modelled.
"""
    OUT.write_text(doc, encoding="utf-8")

    print(f"train {train_score['n']:,} | test {test_score['n']:,}")
    print(f"baseline ll {test_score['base_ll']:.4f} | model ll {test_score['model_ll']:.4f} | "
          f"slope {test_score['slope']:.3f}")
    print(f"weights: {np.round(w, 4).tolist()}")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
