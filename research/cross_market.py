"""E7: does the 1X2 market tell us anything the total-goals market missed?

Both prices come from the same book at the same nominal moment, but they are separate markets
and need not carry identical information. The draw probability in particular is tightly linked to
total goals — 0-0 and 1-1 are draws, and a match priced as a likely draw is usually priced as a
low-scoring one.

If the O/U price already absorbs that, the draw probability adds nothing. If it does not, this is
incremental information available at the cutoff from data already held.

    python research/cross_market.py

Writes research/CROSS_MARKET.md.
"""

from __future__ import annotations

import math
import statistics
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research"))

import book_disagreement as bd   # noqa: E402
import analyse                   # noqa: E402
import report_stamp              # noqa: E402

OUT = ROOT / "research" / "CROSS_MARKET.md"
PILOT = ("2021", "2122", "2223")


def logit(p: float) -> float:
    p = min(max(p, 1e-6), 1 - 1e-6)
    return math.log(p / (1 - p))


def build() -> list[dict]:
    out = []
    for r in analyse.load():
        if r["_season"] not in PILOT:
            continue
        try:
            h, d, a = float(r["PSCH"]), float(r["PSCD"]), float(r["PSCA"])
            over, under = float(r["PC>2.5"]), float(r["PC<2.5"])
            hg, ag = int(r["FTHG"]), int(r["FTAG"])
        except (KeyError, TypeError, ValueError):
            continue
        prices = (h, d, a, over, under)
        if not all(math.isfinite(p) for p in prices) or min(prices) <= 1.0:
            continue
        inv = 1 / h + 1 / d + 1 / a
        p_draw = (1 / d) / inv
        p_over = 1 / over / (1 / over + 1 / under)
        out.append({"season": r["_season"], "cluster": f"{r['_league']}_{r['_season']}",
                    "x": logit(p_over), "draw": logit(p_draw), "p_draw": p_draw,
                    "y": 1 if hg + ag >= 3 else 0})
    return out


def design(rows: list[dict], extra: bool) -> np.ndarray:
    cols = [np.ones(len(rows)), np.array([r["x"] for r in rows])]
    if extra:
        cols.append(np.array([r["draw"] for r in rows]))
    return np.column_stack(cols)


def main() -> int:
    rows = build()
    seasons = sorted({r["season"] for r in rows})
    y = np.array([r["y"] for r in rows], dtype=float)
    Xb, Xt = design(rows, False), design(rows, True)

    oof_b, oof_t = np.zeros(len(rows)), np.zeros(len(rows))
    per_season = []
    for held in seasons:
        tr = np.array([i for i, r in enumerate(rows) if r["season"] != held])
        te = np.array([i for i, r in enumerate(rows) if r["season"] == held])
        bb, bt = bd.fit_logistic(Xb[tr], y[tr]), bd.fit_logistic(Xt[tr], y[tr])
        oof_b[te] = 1 / (1 + np.exp(-np.clip(Xb[te] @ bb, -30, 30)))
        oof_t[te] = 1 / (1 + np.exp(-np.clip(Xt[te] @ bt, -30, 30)))
        per_season.append((held, len(te),
                           float(np.mean([bd.logloss(p, yy) for p, yy in zip(oof_b[te], y[te])])),
                           float(np.mean([bd.logloss(p, yy) for p, yy in zip(oof_t[te], y[te])]))))

    base_ll = float(np.mean([bd.logloss(p, yy) for p, yy in zip(oof_b, y)]))
    treat_ll = float(np.mean([bd.logloss(p, yy) for p, yy in zip(oof_t, y)]))
    gain = base_ll - treat_ll

    by_cluster: dict[str, list[int]] = {}
    for i, r in enumerate(rows):
        by_cluster.setdefault(r["cluster"], []).append(i)
    keys = sorted(by_cluster)
    rng = np.random.default_rng(20261103)
    draws = []
    for _ in range(1000):
        flat = [i for k in (keys[rng.integers(0, len(keys))] for _ in keys) for i in by_cluster[k]]
        lb = np.mean([bd.logloss(oof_b[i], y[i]) for i in flat])
        lt = np.mean([bd.logloss(oof_t[i], y[i]) for i in flat])
        draws.append(float(lb - lt))
    draws.sort()
    lo, hi = draws[int(0.025 * len(draws))], draws[int(0.975 * len(draws)) - 1]

    auc_b = bd.auc(list(zip(oof_b.tolist(), y.astype(int).tolist())))
    auc_t = bd.auc(list(zip(oof_t.tolist(), y.astype(int).tolist())))

    doc = f"""{report_stamp.stamp(Path(__file__))}

# E7 — does the 1X2 market add information to the totals market?

Pilot seasons only. Baseline logistic on Pinnacle's de-vigged over/under 2.5 logit; treatment
adds the de-vigged draw probability from the same book's 1X2 prices, also as a logit. Fitted
leave-one-season-out.

## Result

| Model | Log loss | AUC |
| --- | --- | --- |
| Totals market only | {base_ll:.4f} | {auc_b:.4f} |
| + 1X2 draw probability | {treat_ll:.4f} | {auc_t:.4f} |

- Improvement: **{gain:+.4f}** nats; cluster 95% interval **[{lo:+.4f}, {hi:+.4f}]**.
- AUC change: {auc_t - auc_b:+.4f}.

## Per held-out season

| Held out | n | Totals only | + draw |
| --- | --- | --- | --- |
""" + "\n".join(f"| {s} | {n:,} | {a:.4f} | {b:.4f} |" for s, n, a, b in per_season) + f"""

## Reading

A positive interval would mean the two markets are not informationally identical and the totals
price leaves something on the table. An interval containing zero means **no incremental improvement
was detected in this pilot under this specification** — weaker than saying the two markets agree,
and much weaker than saying they are efficient. Two prices from one book, one corpus, three
seasons.

Either way the effect would have to be large enough to matter against a 0.0246-nat deficit. A
gain of a few thousandths would be a curiosity, not an advantage.

The cluster interval resamples fixed out-of-fold predictions, so it is conditional on the fitted
fold models and does **not** include model-estimation uncertainty. It bounds the sampling
variability of the comparison, not the uncertainty of the modelling choice.

## Limits

- Two prices from one book. A different book's 1X2 might disagree, but cross-book disagreement
  already tested null in E4.
- The draw probability is a proxy for the goal environment, not a measurement of it.
- No quote timestamps, so the T−90 caveat applies to any claim about acting on this.
"""
    OUT.write_text(doc, encoding="utf-8", newline="\n")

    print(f"base={base_ll:.4f} treat={treat_ll:.4f} gain={gain:+.4f} "
          f"ci=[{lo:+.4f},{hi:+.4f}] auc={auc_b:.4f}->{auc_t:.4f}")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
