"""Does price movement carry information the closing price missed?

Queue item 2 is about decision support. One route needs no new data: the corpus holds an **opening**
and a **closing** price for the same market. If the move between them predicts the outcome beyond
the closing price, then a user who acted early on movement would have information; if it does not,
movement is noise and the closing price is all there is.

Two hypotheses, fixed before the result:

- **M1** — the de-vigged move in the over 2.5 price, opening to closing, predicts the outcome beyond
  the closing price.
- **M2** — the *size* of the move, regardless of direction, predicts it. A large repricing may signal
  that information arrived, without saying which way it points.

Both are tested as increments over the closing price, out of fold, with a cluster-stratified
permutation null.

    python research/movement_study.py

Writes research/MOVEMENT_STUDY.md.
"""

from __future__ import annotations

import math
import statistics
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research"))

import analyse            # noqa: E402
import feature_screen as fs   # noqa: E402
import report_stamp       # noqa: E402

OUT = ROOT / "research" / "MOVEMENT_STUDY.md"
PILOT = ("2021", "2122", "2223")
BOOTSTRAPS = 1000
PERMUTATIONS = 200
SEED = 20261103


def devig(over: float, under: float) -> float:
    return (1 / over) / (1 / over + 1 / under)


def usable(*values) -> bool:
    try:
        return all(math.isfinite(float(v)) and float(v) > 1.0 for v in values)
    except (TypeError, ValueError):
        return False


def build() -> list[dict]:
    rows = []
    for r in analyse.load():
        if r["_season"] not in PILOT:
            continue
        if not usable(r.get("P>2.5"), r.get("P<2.5"), r.get("PC>2.5"), r.get("PC<2.5")):
            continue
        try:
            hg, ag = int(r["FTHG"]), int(r["FTAG"])
        except (TypeError, ValueError):
            continue
        p_open = devig(float(r["P>2.5"]), float(r["P<2.5"]))
        p_close = devig(float(r["PC>2.5"]), float(r["PC<2.5"]))
        move = float(fs.logit(np.array([p_close]))[0]) - float(fs.logit(np.array([p_open]))[0])
        rows.append({"season": r["_season"], "cluster": f"{r['_league']}_{r['_season']}",
                     "x": float(fs.logit(np.array([p_close]))[0]),
                     "move": move, "move_abs": abs(move),
                     "y": 1 if hg + ag >= 3 else 0})
    return rows


HYPOTHESES = {"M1 signed movement": "move", "M2 movement size": "move_abs"}


def main() -> int:
    rows = build()
    y = np.array([r["y"] for r in rows], dtype=float)
    _, base_pred, _ = fs.oof_gain(rows, (), y)
    base_ll = fs.logloss_vec(base_pred, y)

    by_cluster: dict[str, list[int]] = {}
    for i, r in enumerate(rows):
        by_cluster.setdefault(r["cluster"], []).append(i)
    keys = sorted(by_cluster)
    rng = np.random.default_rng(SEED)

    results = []
    for label, col in HYPOTHESES.items():
        gain, base, treat = fs.oof_gain(rows, (col,), y)
        draws = []
        for _ in range(BOOTSTRAPS):
            flat = [i for k in (keys[rng.integers(0, len(keys))] for _ in keys)
                    for i in by_cluster[k]]
            draws.append(fs.logloss_vec(base[flat], y[flat]) - fs.logloss_vec(treat[flat], y[flat]))
        draws.sort()
        lo, hi = draws[int(0.025 * len(draws))], draws[int(0.975 * len(draws)) - 1]

        null = []
        for _ in range(PERMUTATIONS):
            perm = [dict(r) for r in rows]
            for stratum in keys:
                idx = [i for i, r in enumerate(perm) if r["cluster"] == stratum]
                order = list(idx)
                rng.shuffle(order)
                vals = [perm[j][col] for j in order]
                for i, v in zip(idx, vals):
                    perm[i][col] = v
            g, _, _ = fs.oof_gain(perm, (col,), y)
            null.append(g)
        p_value = float((np.sum(np.array(null) >= gain) + 1) / (PERMUTATIONS + 1))
        results.append({"label": label, "gain": gain, "lo": lo, "hi": hi, "p": p_value,
                        "sd": statistics.pstdev([r[col] for r in rows])})

    moves = [r["move"] for r in rows]
    doc = f"""{report_stamp.stamp(Path(__file__))}

# Does price movement carry information?

Pilot seasons, {len(rows):,} fixtures with both an opening and a closing Pinnacle over 2.5 price.
Movement is the change in the de-vigged logit between the snapshots. Each hypothesis is tested as an
increment over the closing price, so a finding means information the closing price did not contain.

| Hypothesis | Feature SD | Gain (nats) | Cluster 95% | Perm. p |
| --- | --- | --- | --- | --- |
""" + "\n".join(
        f"| {r['label']} | {r['sd']:.4f} | {r['gain']:+.5f} | "
        f"[{r['lo']:+.5f}, {r['hi']:+.5f}] | {r['p']:.3f} |" for r in results) + f"""

Baseline log loss of the closing price alone: **{base_ll:.4f}**. Mean signed movement
{statistics.mean(moves):+.4f}; median absolute movement {statistics.median(abs(m) for m in moves):.4f}.

## Reading

A positive gain with an interval excluding zero would mean the move anticipates the outcome — a
genuine decision-support finding, since a user acting before the close could use it. A null means
the closing price already contains whatever the move was about, which is what an efficient market
should do with information that arrives before the close.

Either way this cannot establish executable value: neither snapshot records its observation time, so
"opening" cannot be tied to T−90 or to any moment a user could act.

## Limits

- Two snapshots only; the path between them is unobserved, so a price that moved and reverted looks
  identical to one that did not move.
- Opening prices are football-data's first recorded price, not necessarily the market's opening.
- One book (Pinnacle) for the movement measure; others may move differently.
"""
    OUT.write_text(doc, encoding="utf-8", newline="\n")

    for r in results:
        print(f"{r['label']}: gain={r['gain']:+.5f} ci=[{r['lo']:+.5f},{r['hi']:+.5f}] p={r['p']:.3f}")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
