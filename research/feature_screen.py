"""A single rigorous screen of every candidate feature family.

The earlier experiments (E4, E5, E7) each tested one family with one specification, one split
scheme and a bootstrap interval. That is enough to notice a large effect and not enough to call a
null. This harness tests every candidate under one protocol:

- **Same estimand everywhere.** Logistic on the market logit, treatment adds the family. Paired,
  so the comparison is like-for-like.
- **Leave-one-season-out.** Fit on two pilot seasons, evaluate on the third.
- **Cluster bootstrap** for the interval, resampling division-seasons.
- **Permutation null.** The feature is shuffled within season and the entire pipeline refitted;
  the p-value is the share of permutations whose gain matches or beats the observed one. A
  bootstrap interval answers "how precise is this estimate"; a permutation answers "could this
  gain have arisen with the feature carrying no information at all".
- **Multiplicity.** Benjamini-Hochberg across the families tested.
- **Per-fold sign check.** A gain that flips sign across seasons is noise regardless of its
  interval.

    python research/feature_screen.py

Writes research/FEATURE_SCREEN.md.
"""

from __future__ import annotations

import math
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research"))

import analyse        # noqa: E402
import report_stamp   # noqa: E402

OUT = ROOT / "research" / "FEATURE_SCREEN.md"
PILOT = ("2021", "2122", "2223")
PERMUTATIONS = 200
BOOTSTRAPS = 1000
SEED = 20261103
DEFAULT_REST = 14.0


def logit(p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


def logloss_vec(p: np.ndarray, y: np.ndarray) -> float:
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


def fast_auc(p: np.ndarray, y: np.ndarray) -> float:
    """Rank-based AUC (Mann-Whitney), O(n log n)."""
    order = np.argsort(p)
    ranks = np.empty(len(p), dtype=float)
    ranks[order] = np.arange(1, len(p) + 1)
    # average ranks for ties
    sorted_p = p[order]
    i = 0
    while i < len(sorted_p):
        j = i
        while j + 1 < len(sorted_p) and sorted_p[j + 1] == sorted_p[i]:
            j += 1
        if j > i:
            ranks[order[i:j + 1]] = (i + j + 2) / 2.0
        i = j + 1
    pos = y == 1
    n_pos, n_neg = int(pos.sum()), int((~pos).sum())
    if n_pos == 0 or n_neg == 0:
        return float("nan")
    return float((ranks[pos].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg))


def fit_logistic(X: np.ndarray, y: np.ndarray, ridge: float = 1e-6) -> np.ndarray:
    beta = np.zeros(X.shape[1])
    for _ in range(60):
        z = np.clip(X @ beta, -30, 30)
        p = 1 / (1 + np.exp(-z))
        w = p * (1 - p)
        grad = X.T @ (y - p) - ridge * beta
        hess = (X * w[:, None]).T @ X + ridge * np.eye(X.shape[1])
        try:
            step = np.linalg.solve(hess, grad)
        except np.linalg.LinAlgError:
            break
        beta += step
        if np.max(np.abs(step)) < 1e-9:
            break
    return beta


def predict(X: np.ndarray, beta: np.ndarray) -> np.ndarray:
    return 1 / (1 + np.exp(-np.clip(X @ beta, -30, 30)))


def build() -> tuple[list[dict], list[str]]:
    """One row per pilot fixture with every candidate feature, computed prior-only."""
    rows = []
    for r in analyse.load():
        try:
            date = datetime.strptime(r["Date"], "%d/%m/%Y")
            hg, ag = int(r["FTHG"]), int(r["FTAG"])
            po_over, po_under = float(r["PC>2.5"]), float(r["PC<2.5"])
            pb_over, pb_under = float(r["B365C>2.5"]), float(r["B365C<2.5"])
            h, d, a = float(r["PSCH"]), float(r["PSCD"]), float(r["PSCA"])
        except (KeyError, TypeError, ValueError):
            continue
        if min(po_over, po_under, pb_over, pb_under, h, d, a) <= 1.0:
            continue
        po = 1 / po_over / (1 / po_over + 1 / po_under)
        pb = 1 / pb_over / (1 / pb_over + 1 / pb_under)
        p_draw = (1 / d) / (1 / h + 1 / d + 1 / a)
        rows.append({"season": r["_season"], "league": r["_league"],
                     "cluster": f"{r['_league']}_{r['_season']}", "date": date,
                     "home": r["HomeTeam"], "away": r["AwayTeam"],
                     "goals": hg + ag, "x": float(logit(np.array([po]))[0]),
                     "y": 1 if hg + ag >= 3 else 0,
                     "d_book": abs(float(logit(np.array([po]))[0]) - float(logit(np.array([pb]))[0])),
                     "draw": float(logit(np.array([p_draw]))[0]),
                     "league_key": f"{r['_league']}_{r['_season']}"})
    rows.sort(key=lambda r: (r["league"], r["season"], r["date"]))

    last_seen: dict[tuple[str, str], datetime] = {}
    recent: dict[tuple[str, str], list[datetime]] = defaultdict(list)
    team_goals: dict[tuple[str, str], list[int]] = defaultdict(list)
    league_goals: dict[tuple[str, str], list[int]] = defaultdict(list)

    for r in rows:
        def rest(team: str) -> float:
            key = (r["league"], team)
            return (r["date"] - last_seen[key]).days if key in last_seen else DEFAULT_REST

        def load(team: str) -> int:
            key = (r["league"], team)
            return sum(1 for dd in recent[key] if (r["date"] - dd).days <= 14)

        def trend(team: str) -> float:
            hist = team_goals[(r["league"], team)][-5:]
            return float(np.mean(hist)) if hist else float(np.mean(league_goals[(r["league"], r["season"])] or [2.6]))

        rest_h, rest_a = rest(r["home"]), rest(r["away"])
        th, ta = trend(r["home"]), trend(r["away"])
        lg = league_goals[(r["league"], r["season"])][-60:]
        r["rest_diff"] = rest_h - rest_a
        r["min_rest"] = min(rest_h, rest_a)
        r["load14"] = float(load(r["home"]) + load(r["away"]))
        r["trend_sum"] = th + ta
        r["trend_diff"] = th - ta
        r["league_env"] = float(np.mean(lg)) if lg else 2.6

        for team in (r["home"], r["away"]):
            key = (r["league"], team)
            last_seen[key] = r["date"]
            recent[key].append(r["date"])
            team_goals[key].append(r["goals"])
        league_goals[(r["league"], r["season"])].append(r["goals"])

    features = ["d_book", "rest_diff", "min_rest", "load14", "draw",
                "trend_sum", "trend_diff", "league_env"]
    return [r for r in rows if r["season"] in PILOT], features


FAMILIES = {
    "F1 cross-book disagreement": ("d_book",),
    "F2 congestion (rest + load)": ("rest_diff", "min_rest", "load14"),
    "F3 cross-market (1X2 draw)": ("draw",),
    "F4 recent scoring trend": ("trend_sum", "trend_diff"),
    "F5 league scoring environment": ("league_env",),
    "F6 all of the above": ("d_book", "rest_diff", "min_rest", "load14", "draw",
                            "trend_sum", "trend_diff", "league_env"),
}


def oof_gain(rows: list[dict], cols: tuple[str, ...], y: np.ndarray,
             use: np.ndarray | None = None) -> tuple[float, np.ndarray, np.ndarray]:
    """Out-of-fold gain (baseline − treatment) and the two OOF prediction vectors."""
    seasons = sorted({r["season"] for r in rows})
    base = np.zeros(len(rows))
    treat = np.zeros(len(rows))
    x = np.array([r["x"] for r in rows])
    feats = np.column_stack([[r[c] for r in rows] for c in cols]) if cols else np.zeros((len(rows), 0))
    if use is not None:
        feats = feats[use] if len(use) == len(rows) else feats
    for held in seasons:
        tr = np.array([i for i, r in enumerate(rows) if r["season"] != held])
        te = np.array([i for i, r in enumerate(rows) if r["season"] == held])
        Xb = np.column_stack([np.ones(len(tr)), x[tr]])
        Xt = np.column_stack([np.ones(len(tr)), x[tr], feats[tr]])
        bb = fit_logistic(Xb, y[tr])
        bt = fit_logistic(Xt, y[tr])
        base[te] = predict(np.column_stack([np.ones(len(te)), x[te]]), bb)
        treat[te] = predict(np.column_stack([np.ones(len(te)), x[te], feats[te]]), bt)
    return logloss_vec(base, y) - logloss_vec(treat, y), base, treat


def main() -> int:
    rows, features = build()
    y = np.array([r["y"] for r in rows], dtype=float)
    base_full, _, _ = oof_gain(rows, (), y)

    by_cluster: dict[str, list[int]] = defaultdict(list)
    for i, r in enumerate(rows):
        by_cluster[r["cluster"]].append(i)
    keys = sorted(by_cluster)
    rng = np.random.default_rng(SEED)

    results = []
    for name, cols in FAMILIES.items():
        gain, base, treat = oof_gain(rows, cols, y)

        # Cluster bootstrap over the paired per-fixture log-loss difference.
        per_fixture = (np.log(np.clip(base, 1e-6, 1 - 1e-6) / np.clip(treat, 1e-6, 1 - 1e-6)))
        # logloss difference per fixture: -(y log p_b + (1-y) log(1-p_b)) + ...; simpler to
        # recompute from stored predictions inside the loop.
        draws = []
        for _ in range(BOOTSTRAPS):
            flat = [i for k in (keys[rng.integers(0, len(keys))] for _ in keys) for i in by_cluster[k]]
            lb = logloss_vec(base[flat], y[flat])
            lt = logloss_vec(treat[flat], y[flat])
            draws.append(lb - lt)
        draws.sort()
        lo, hi = draws[int(0.025 * len(draws))], draws[int(0.975 * len(draws)) - 1]

        # Permutation null: shuffle the feature columns within season, refit everything.
        null_gains = []
        seasons = sorted({r["season"] for r in rows})
        for _ in range(PERMUTATIONS):
            perm_rows = [dict(r) for r in rows]
            for season in seasons:
                idx = [i for i, r in enumerate(perm_rows) if r["season"] == season]
                for c in cols:
                    vals = [perm_rows[i][c] for i in idx]
                    rng.shuffle(vals)
                    for i, v in zip(idx, vals):
                        perm_rows[i][c] = v
            g, _, _ = oof_gain(perm_rows, cols, y)
            null_gains.append(g)
        null_gains = np.array(null_gains)
        p_value = float((np.sum(null_gains >= gain) + 1) / (PERMUTATIONS + 1))

        per_season = []
        for season in seasons:
            idx = np.array([i for i, r in enumerate(rows) if r["season"] == season])
            per_season.append(logloss_vec(base[idx], y[idx]) - logloss_vec(treat[idx], y[idx]))

        results.append({"name": name, "gain": gain, "lo": lo, "hi": hi, "p": p_value,
                        "folds": per_season,
                        "auc_base": fast_auc(base, y), "auc_treat": fast_auc(treat, y)})

    # Benjamini-Hochberg across the families screened.
    order = sorted(range(len(results)), key=lambda i: results[i]["p"])
    n = len(results)
    running = 1.0
    for rank in range(n - 1, -1, -1):
        i = order[rank]
        running = min(running, results[i]["p"] * n / (rank + 1))
        results[i]["q"] = running

    doc = f"""{report_stamp.stamp(Path(__file__))}

# Feature screen

Every candidate family tested under one protocol: market-conditioned logistic, leave-one-season-
out, cluster bootstrap for the interval, {PERMUTATIONS} within-season permutations for a null
distribution, and Benjamini-Hochberg across the {len(results)} families. `n = {len(rows):,}` pilot
fixtures.

| Family | Gain (nats) | Cluster 95% | Perm. p | BH q | Per-season gains | AUC base → treat |
| --- | --- | --- | --- | --- | --- | --- |
""" + "\n".join(
        f"| {r['name']} | {r['gain']:+.4f} | [{r['lo']:+.4f}, {r['hi']:+.4f}] | {r['p']:.3f} | "
        f"{r['q']:.3f} | " + ", ".join(f"{g:+.4f}" for g in r["folds"]) +
        f" | {r['auc_base']:.4f} → {r['auc_treat']:.4f} |"
        for r in results) + f"""

## How to read this

A family is evidence of information only if it clears **all** of: a positive gain, a cluster
interval excluding zero, a permutation p below the BH threshold, and the same sign in every
season. The permutation test is the one that matters most here: the bootstrap asks how precisely
the gain is estimated, while the permutation asks whether a gain of that size could arise with the
feature carrying no information at all — the right question for a screen of this kind.

The per-season column is a blunt stability check. A family whose gain flips sign across the three
held-out seasons is noise even if its aggregate interval looks convincing.

## Selection effects

The pilot has now been examined many times, and this screen adds {len(results)} more tests to that
history. The BH column corrects within this family of tests but not across the whole day's
searching. Treat any single positive here as a candidate requiring a fresh, independent check —
not as a discovery.

## Limits

- One corpus, one market, three pilot seasons. The confirmatory slice is untouched.
- Features are computed from the fixture list and prior results only; the schedule is public, so
  this is not look-ahead. Cup and European fixtures are absent, so congestion is understated.
- The closing prices carry no observation timestamp; the T−90 caveat applies to every claim about
  acting on these relationships.
"""
    OUT.write_text(doc, encoding="utf-8")

    for r in results:
        print(f"{r['name']}: gain={r['gain']:+.5f} ci=[{r['lo']:+.5f},{r['hi']:+.5f}] "
              f"p={r['p']:.3f} q={r['q']:.3f} folds={[round(g, 5) for g in r['folds']]}")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
