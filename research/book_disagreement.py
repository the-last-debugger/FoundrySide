"""Workstream 4, experiment 1: does cross-book disagreement carry information?

The benchmark is one book's closing price. The data hold a second book's closing price for the
same market, and the two disagree on some fixtures. If that disagreement predicts the outcome
after conditioning on the first book's probability, it is information the benchmark does not
contain — the first genuine candidate for added resolution.

Design:

- Outcome: over/under 2.5. Both prices de-vigged.
- Baseline: logistic on `logit(p_pinnacle)` — the market, restated.
- Treatment: adds `|logit(p_pinnacle) − logit(p_bet365)|`.
- Split: leave-one-season-out. Fit on two seasons, evaluate on the third.
- Metrics: log loss (primary) and AUC (rank-only, so a monotone map cannot flatter it).
- Uncertainty: cluster bootstrap over division-seasons on the paired difference.

    python research/book_disagreement.py

Writes research/BOOK_DISAGREEMENT.md.
"""

from __future__ import annotations

import math
import statistics
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research"))

import analyse        # noqa: E402
import report_stamp   # noqa: E402

OUT = ROOT / "research" / "BOOK_DISAGREEMENT.md"
DELTAS = ROOT / "research" / "pilot_deltas.csv"
PILOT = ("2021", "2122", "2223")


def logit(p: float) -> float:
    p = min(max(p, 1e-6), 1 - 1e-6)
    return math.log(p / (1 - p))


def sigmoid(z: float) -> float:
    return 1 / (1 + math.exp(-max(-30.0, min(30.0, z))))


def logloss(p: float, y: int) -> float:
    p = min(max(p, 1e-6), 1 - 1e-6)
    return -math.log(p) if y else -math.log(1 - p)


def auc(pairs: list[tuple[float, int]]) -> float:
    """Rank-based AUC; insensitive to any monotone recalibration."""
    pos = [p for p, y in pairs if y == 1]
    neg = [p for p, y in pairs if y == 0]
    if not pos or not neg:
        return float("nan")
    wins = 0.0
    for p in pos:
        for q in neg:
            wins += 1.0 if p > q else 0.5 if p == q else 0.0
    return wins / (len(pos) * len(neg))


def fit_logistic(X: np.ndarray, y: np.ndarray, ridge: float = 1e-6) -> np.ndarray:
    """Newton-Raphson for a small logistic model; ridge keeps degenerate designs finite."""
    k = X.shape[1]
    beta = np.zeros(k)
    for _ in range(80):
        z = X @ beta
        p = 1 / (1 + np.exp(-np.clip(z, -30, 30)))
        w = p * (1 - p)
        grad = X.T @ (y - p) - ridge * beta
        hess = (X * w[:, None]).T @ X + ridge * np.eye(k)
        try:
            step = np.linalg.solve(hess, grad)
        except np.linalg.LinAlgError:
            break
        beta = beta + step
        if np.max(np.abs(step)) < 1e-9:
            break
    return beta


def load() -> list[dict]:
    """Pilot fixtures with both books' de-vigged P(over 2.5)."""
    rows, _ = analyse.load(), None
    out = []
    for r in rows:
        if r["_season"] not in PILOT:
            continue
        try:
            po_over, po_under = float(r["PC>2.5"]), float(r["PC<2.5"])
            pb_over, pb_under = float(r["B365C>2.5"]), float(r["B365C<2.5"])
            hg, ag = int(r["FTHG"]), int(r["FTAG"])
        except (KeyError, TypeError, ValueError):
            continue
        if min(po_over, po_under, pb_over, pb_under) <= 1.0:
            continue
        po = 1 / po_over / (1 / po_over + 1 / po_under)
        pb = 1 / pb_over / (1 / pb_over + 1 / pb_under)
        out.append({
            "season": r["_season"], "cluster": f"{r['_league']}_{r['_season']}",
            "x": logit(po), "d": abs(logit(po) - logit(pb)),
            "y": 1 if hg + ag >= 3 else 0,
        })
    return out


def design(rows: list[dict], with_disagreement: bool) -> tuple[np.ndarray, np.ndarray]:
    cols = [np.ones(len(rows)), np.array([r["x"] for r in rows])]
    if with_disagreement:
        cols.append(np.array([r["d"] for r in rows]))
    return np.column_stack(cols), np.array([r["y"] for r in rows], dtype=float)


def main() -> int:
    rows = load()
    seasons = sorted({r["season"] for r in rows})

    base_ll, treat_ll = [], []
    base_auc_pairs: list[tuple[float, int]] = []
    treat_auc_pairs: list[tuple[float, int]] = []
    coefficients = []
    per_season = []

    for held in seasons:
        train = [r for r in rows if r["season"] != held]
        test = [r for r in rows if r["season"] == held]
        Xb, yb = design(train, False)
        Xt, yt = design(train, True)
        bb = fit_logistic(Xb, yb)
        bt = fit_logistic(Xt, yt)
        coefficients.append((held, bt))

        Xb_test, y_test = design(test, False)
        Xt_test, _ = design(test, True)
        pb = 1 / (1 + np.exp(-np.clip(Xb_test @ bb, -30, 30)))
        pt = 1 / (1 + np.exp(-np.clip(Xt_test @ bt, -30, 30)))
        ll_b = float(np.mean([logloss(p, y) for p, y in zip(pb, y_test)]))
        ll_t = float(np.mean([logloss(p, y) for p, y in zip(pt, y_test)]))
        per_season.append((held, len(test), ll_b, ll_t))
        base_ll.append(ll_b)
        treat_ll.append(ll_t)
        base_auc_pairs += list(zip(pb.tolist(), y_test.astype(int).tolist()))
        treat_auc_pairs += list(zip(pt.tolist(), y_test.astype(int).tolist()))

    # Cluster bootstrap on the paired per-fixture difference.
    deltas = np.array([a - b for a, b in zip(base_ll, treat_ll)])  # per season, coarse
    rng = np.random.default_rng(20261103)
    by_cluster: dict[str, list[int]] = {}
    for i, r in enumerate(rows):
        by_cluster.setdefault(r["cluster"], []).append(i)

    X_all_b, y_all = design(rows, False)
    X_all_t, _ = design(rows, True)
    # Out-of-fold predictions for the bootstrap: refit per fold, store per fixture.
    oof_b = np.zeros(len(rows))
    oof_t = np.zeros(len(rows))
    for held in seasons:
        idx_train = np.array([i for i, r in enumerate(rows) if r["season"] != held])
        idx_test = np.array([i for i, r in enumerate(rows) if r["season"] == held])
        bb_ = fit_logistic(X_all_b[idx_train], y_all[idx_train])
        bt_ = fit_logistic(X_all_t[idx_train], y_all[idx_train])
        oof_b[idx_test] = 1 / (1 + np.exp(-np.clip(X_all_b[idx_test] @ bb_, -30, 30)))
        oof_t[idx_test] = 1 / (1 + np.exp(-np.clip(X_all_t[idx_test] @ bt_, -30, 30)))

    def diff_mean(indices) -> float:
        lb = np.mean([logloss(oof_b[i], y_all[i]) for i in indices])
        lt = np.mean([logloss(oof_t[i], y_all[i]) for i in indices])
        return float(lb - lt)

    keys = sorted(by_cluster)
    draws = []
    for _ in range(1000):
        picked = [keys[rng.integers(0, len(keys))] for _ in keys]
        flat = [i for k in picked for i in by_cluster[k]]
        draws.append(diff_mean(flat))
    draws.sort()
    lo, hi = draws[int(0.025 * len(draws))], draws[int(0.975 * len(draws)) - 1]

    base_auc = auc(base_auc_pairs)
    treat_auc = auc(treat_auc_pairs)
    gain = float(np.mean(base_ll) - np.mean(treat_ll))

    doc = f"""{report_stamp.stamp(Path(__file__))}

# Workstream 4, experiment 1 — does cross-book disagreement carry information?

Pilot seasons only. Both books' over/under 2.5 closing prices de-vigged; the baseline is a
logistic on Pinnacle's logit, the treatment adds the absolute difference between the two books'
logits. Fitted leave-one-season-out; no fold is scored by a model that saw its outcomes.

## Result

| Model | Log loss (out-of-fold) | AUC |
| --- | --- | --- |
| Market only | {statistics.mean(base_ll):.4f} | {base_auc:.4f} |
| Market + disagreement | {statistics.mean(treat_ll):.4f} | {treat_auc:.4f} |

- Log-loss improvement from the disagreement term: **{gain:+.4f}** nats.
- Cluster-bootstrap 95% interval on that paired improvement: **[{lo:+.4f}, {hi:+.4f}]**.
- AUC change: {treat_auc - base_auc:+.4f}.

## Per held-out season

| Held out | n | Market only | + disagreement |
| --- | --- | --- | --- |
""" + "\n".join(f"| {s} | {n:,} | {a:.4f} | {b:.4f} |" for s, n, a, b in per_season) + f"""

## Fitted coefficients (disagreement model)

| Held out | intercept | logit(p_pinnacle) | disagreement |
| --- | --- | --- | --- |
""" + "\n".join(f"| {s} | {c[0]:+.4f} | {c[1]:+.4f} | {c[2]:+.4f} |" for s, c in coefficients) + f"""

## Reading

The interval is the test. If it excludes zero, cross-book disagreement carries information the
single benchmark does not, and it is the first candidate for added resolution. If it straddles
zero, the two books disagree noisily and the experiment is a negative result worth recording:
it rules out one cheap source of extra information rather than leaving it plausible.

The AUC column is the guard against a calibration artefact: a term that only rescales the
probability cannot move the ranking, so an AUC gain is the signature of real separation.

## Limits

- Two books, one market, one corpus. "Disagreement" here means these two feeds, not the market.
- The 0.01-nat target is unchanged; this experiment asks whether information exists, not whether
  it is large enough to trade.
- Closing prices carry no observation timestamp, so the comparison is between two prices whose
  collection times are unknown, and the T−90 caveat applies to any claim about acting on them.
"""
    OUT.write_text(doc, encoding="utf-8")

    print(f"base_ll={statistics.mean(base_ll):.4f} treat_ll={statistics.mean(treat_ll):.4f} "
          f"gain={gain:+.4f} ci=[{lo:+.4f},{hi:+.4f}]")
    print(f"auc base={base_auc:.4f} treat={treat_auc:.4f}")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
