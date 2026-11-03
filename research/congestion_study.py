"""Workstream 4, experiment 2: does schedule congestion carry information?

Rest and fixture congestion affect goals in football, and the fixture list is known before
kickoff — so if the market underweights them, they are information available at T−90. This
conditions on the market price and asks whether congestion adds anything to it.

Features, all computed from fixtures already played (the schedule is public, so using it is not
look-ahead):

- `rest_diff`: days since the home team's last match minus the away team's.
- `min_rest`: the shorter of the two rests, a proxy for a side playing tired.

Design identical to the cross-book test: baseline logistic on `logit(p_pinnacle)`, treatment adds
the features, fitted leave-one-season-out, scored on log loss and AUC with a cluster interval.

    python research/congestion_study.py

Writes research/CONGESTION_STUDY.md.
"""

from __future__ import annotations

import math
import statistics
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research"))

import book_disagreement as bd   # noqa: E402  (logistic, AUC, logloss)
import analyse                   # noqa: E402
import report_stamp              # noqa: E402

OUT = ROOT / "research" / "CONGESTION_STUDY.md"
PILOT = ("2021", "2122", "2223")
DEFAULT_REST = 14.0


def logit(p: float) -> float:
    p = min(max(p, 1e-6), 1 - 1e-6)
    return math.log(p / (1 - p))


def build() -> list[dict]:
    rows = analyse.load()
    # Order every league-season by date so "last match" is a prior fixture, never a later one.
    parsed = []
    for r in rows:
        try:
            date = datetime.strptime(r["Date"], "%d/%m/%Y")
            hg, ag = int(r["FTHG"]), int(r["FTAG"])
            o_over, o_under = float(r["PC>2.5"]), float(r["PC<2.5"])
        except (KeyError, TypeError, ValueError):
            continue
        if o_over <= 1.0 or o_under <= 1.0:
            continue
        p = 1 / o_over / (1 / o_over + 1 / o_under)
        parsed.append({"season": r["_season"], "league": r["_league"],
                       "cluster": f"{r['_league']}_{r['_season']}",
                       "date": date, "home": r["HomeTeam"], "away": r["AwayTeam"],
                       "x": logit(p), "y": 1 if hg + ag >= 3 else 0})
    parsed.sort(key=lambda r: (r["league"], r["season"], r["date"]))

    last_seen: dict[tuple[str, str], datetime] = {}
    recent: dict[tuple[str, str], list[datetime]] = defaultdict(list)
    out = []
    for r in parsed:
        def rest(team: str) -> float:
            key = (r["league"], team)
            return (r["date"] - last_seen[key]).days if key in last_seen else DEFAULT_REST

        def played(team: str) -> int:
            key = (r["league"], team)
            return sum(1 for d in recent[key] if (r["date"] - d).days <= 14)

        rest_h, rest_a = rest(r["home"]), rest(r["away"])
        r["rest_diff"] = rest_h - rest_a
        r["min_rest"] = min(rest_h, rest_a)
        r["congestion"] = played(r["home"]) + played(r["away"])

        for team in (r["home"], r["away"]):
            key = (r["league"], team)
            last_seen[key] = r["date"]
            recent[key].append(r["date"])
        if r["season"] in PILOT:
            out.append(r)
    return out


def design(rows: list[dict], extra: tuple[str, ...]) -> np.ndarray:
    cols = [np.ones(len(rows)), np.array([r["x"] for r in rows])]
    for name in extra:
        cols.append(np.array([r[name] for r in rows], dtype=float))
    return np.column_stack(cols)


def main() -> int:
    rows = build()
    seasons = sorted({r["season"] for r in rows})
    extra = ("rest_diff", "min_rest", "congestion")

    base_ll, treat_ll = [], []
    base_pairs: list[tuple[float, int]] = []
    treat_pairs: list[tuple[float, int]] = []
    per_season = []

    oof_base = np.zeros(len(rows))
    oof_treat = np.zeros(len(rows))
    y_all = np.array([r["y"] for r in rows], dtype=float)
    Xb, Xt = design(rows, ()), design(rows, extra)

    for held in seasons:
        tr = np.array([i for i, r in enumerate(rows) if r["season"] != held])
        te = np.array([i for i, r in enumerate(rows) if r["season"] == held])
        bb = bd.fit_logistic(Xb[tr], y_all[tr])
        bt = bd.fit_logistic(Xt[tr], y_all[tr])
        oof_base[te] = 1 / (1 + np.exp(-np.clip(Xb[te] @ bb, -30, 30)))
        oof_treat[te] = 1 / (1 + np.exp(-np.clip(Xt[te] @ bt, -30, 30)))
        ll_b = float(np.mean([bd.logloss(p, y) for p, y in zip(oof_base[te], y_all[te])]))
        ll_t = float(np.mean([bd.logloss(p, y) for p, y in zip(oof_treat[te], y_all[te])]))
        base_ll.append(ll_b)
        treat_ll.append(ll_t)
        per_season.append((held, len(te), ll_b, ll_t))
        base_pairs += list(zip(oof_base[te].tolist(), y_all[te].astype(int).tolist()))
        treat_pairs += list(zip(oof_treat[te].tolist(), y_all[te].astype(int).tolist()))

    by_cluster: dict[str, list[int]] = {}
    for i, r in enumerate(rows):
        by_cluster.setdefault(r["cluster"], []).append(i)
    keys = sorted(by_cluster)
    rng = np.random.default_rng(20261103)
    draws = []
    for _ in range(1000):
        flat = [i for k in (keys[rng.integers(0, len(keys))] for _ in keys) for i in by_cluster[k]]
        lb = np.mean([bd.logloss(oof_base[i], y_all[i]) for i in flat])
        lt = np.mean([bd.logloss(oof_treat[i], y_all[i]) for i in flat])
        draws.append(float(lb - lt))
    draws.sort()
    lo, hi = draws[int(0.025 * len(draws))], draws[int(0.975 * len(draws)) - 1]

    gain = statistics.mean(base_ll) - statistics.mean(treat_ll)
    auc_b, auc_t = bd.auc(base_pairs), bd.auc(treat_pairs)

    doc = f"""{report_stamp.stamp(Path(__file__))}

# Workstream 4, experiment 2 — does congestion carry information?

Pilot seasons only. Baseline is a logistic on Pinnacle's de-vigged logit; the treatment adds
rest difference, minimum rest and matches played in the previous 14 days. Fitted
leave-one-season-out.

## Result

| Model | Log loss | AUC |
| --- | --- | --- |
| Market only | {statistics.mean(base_ll):.4f} | {auc_b:.4f} |
| Market + congestion | {statistics.mean(treat_ll):.4f} | {auc_t:.4f} |

- Improvement: **{gain:+.4f}** nats; cluster 95% interval **[{lo:+.4f}, {hi:+.4f}]**.
- AUC change: {auc_t - auc_b:+.4f}.

## Per held-out season

| Held out | n | Market only | + congestion |
| --- | --- | --- | --- |
""" + "\n".join(f"| {s} | {n:,} | {a:.4f} | {b:.4f} |" for s, n, a, b in per_season) + f"""

## Reading

A positive interval excluding zero would make schedule load the first demonstrated source of
information beyond the price. An interval containing zero is a negative result for this feature
family and is recorded as such: congestion is priced, or it does not matter at this level of
detail, and either way it is not the route to added resolution.

## Limits

- Rest is measured from the fixture corpus, so a team's first match of a season gets a default
  rest of {DEFAULT_REST:.0f} days rather than its true off-season break.
- Cup and European fixtures are not in the corpus, so congestion is understated for teams that
  played them. That biases the feature toward zero, which makes a null result weaker evidence
  than it looks — stated here rather than discovered later.
- The closing price has no observation timestamp; the T−90 caveat applies.
"""
    OUT.write_text(doc, encoding="utf-8")

    print(f"base={statistics.mean(base_ll):.4f} treat={statistics.mean(treat_ll):.4f} "
          f"gain={gain:+.4f} ci=[{lo:+.4f},{hi:+.4f}] auc={auc_b:.4f}->{auc_t:.4f}")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
