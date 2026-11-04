"""Bogey-team study — does the history between two specific clubs predict beyond the price?

"X always beats Y" and "these two always produce goals" are the most common football beliefs that
have a mechanism: repeated matchups can encode a persistent stylistic mismatch that a team-level
rating averages away. Unlike calendar folklore this is not deterministic, so it needs the full
availability discipline.

Two hypotheses, fixed before the results:

- **B1 — goals.** Prior meetings between the same pair have an over/under 2.5 rate that predicts
  this meeting beyond the market price.
- **B2 — result.** The home side's win rate in prior meetings predicts this meeting beyond price.

Both features are shrunk toward the base rate so that two prior meetings do not dominate, and both
are built with the pending-result queue: a meeting enters the pair's history only when
kickoff + 3h precedes the target fixture's cutoff.

Pair-level clustering is the point. The unit of the belief is the fixture pair, not the division,
so the permutation null is stratified by division-season and the bootstrap resamples
division-seasons; a pair-level effect that survives division-season resampling is the strong
version of the claim.

    python research/bogey_team.py

Writes research/BOGEY_TEAM.md.
"""

from __future__ import annotations

import math
import statistics
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research"))

import analyse            # noqa: E402
import feature_screen as fs   # noqa: E402
import fixture_time       # noqa: E402
import report_stamp       # noqa: E402

OUT = ROOT / "research" / "BOGEY_TEAM.md"
PILOT = ("2021", "2122", "2223")
PERMUTATIONS = 200
BOOTSTRAPS = 1000
SEED = 20261103
PRIOR_WEIGHT = 4.0     # shrinks a pair's rate toward the base rate


def build() -> list[dict]:
    raw = []
    for r in analyse.load():
        if r["_season"] not in PILOT:
            continue
        try:
            kickoff = fixture_time.kickoff_utc(r["Date"], r["Time"], r["_league"])
            cutoff = fixture_time.cutoff_utc(r["Date"], r["Time"], r["_league"])
            hg, ag = int(r["FTHG"]), int(r["FTAG"])
            over, under = float(r["PC>2.5"]), float(r["PC<2.5"])
        except (KeyError, TypeError, ValueError, fixture_time.ClockError):
            continue
        if not (math.isfinite(over) and math.isfinite(under)) or over <= 1.0 or under <= 1.0:
            continue
        p_over = 1 / over / (1 / over + 1 / under)
        raw.append({"season": r["_season"], "league": r["_league"],
                    "cluster": f"{r['_league']}_{r['_season']}",
                    "kickoff": kickoff, "cutoff": cutoff,
                    "home": r["HomeTeam"], "away": r["AwayTeam"],
                    "x": float(fs.logit(np.array([p_over]))[0]),
                    "y": 1 if hg + ag >= 3 else 0,
                    "over": 1 if hg + ag >= 3 else 0,
                    "home_win": 1 if hg > ag else 0,
                    "goals": hg + ag})
    raw.sort(key=lambda r: r["kickoff"])

    # Per-pair history, keyed by the unordered pair inside a division.
    history: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    pending: list[tuple[datetime, int, dict]] = []
    out = []
    for r in raw:
        due = [p for p in pending if p[0] <= r["cutoff"]]
        pending = [p for p in pending if p[0] > r["cutoff"]]
        for _at, _i, row in due:
            key = (row["league"], *sorted((row["home"], row["away"])))
            history[key].append(row)

        key = (r["league"], *sorted((r["home"], r["away"])))
        prior = history.get(key, [])
        n = len(prior)
        over_rate = (sum(p["over"] for p in prior) + PRIOR_WEIGHT * 0.5) / (n + PRIOR_WEIGHT)
        home_rate = (sum(p["home_win"] for p in prior) + PRIOR_WEIGHT * 0.5) / (n + PRIOR_WEIGHT)
        r["h2h_over"] = over_rate
        r["h2h_home"] = home_rate
        r["h2h_n"] = n
        out.append(r)
        pending.append((r["kickoff"] + timedelta(hours=3), len(out), r))
    return out


HYPOTHESES = {
    "B1 pair goals history": "h2h_over",
    "B2 pair result history": "h2h_home",
}


def main() -> int:
    rows = build()
    y = np.array([r["y"] for r in rows], dtype=float)
    _, base_pred, _ = fs.oof_gain(rows, (), y)
    base_ll = fs.logloss_vec(base_pred, y)

    by_cluster: dict[str, list[int]] = defaultdict(list)
    for i, r in enumerate(rows):
        by_cluster[r["cluster"]].append(i)
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
        # Pair-level bootstrap: the belief's unit is the fixture pair, so resampling whole
        # competitions understates pair dependence. This is the stringent interval.
        by_pair: dict[str, list[int]] = defaultdict(list)
        for i, r in enumerate(rows):
            by_pair[f"{r['league']}|{sorted((r['home'], r['away']))[0]}|{sorted((r['home'], r['away']))[1]}"].append(i)
        pair_keys = sorted(by_pair)
        pair_draws = []
        for _ in range(BOOTSTRAPS):
            flat = [i for k in (pair_keys[rng.integers(0, len(pair_keys))] for _ in pair_keys)
                    for i in by_pair[k]]
            pair_draws.append(fs.logloss_vec(base[flat], y[flat]) - fs.logloss_vec(treat[flat], y[flat]))
        pair_draws.sort()
        results.append({"label": label, "gain": gain, "lo": lo, "hi": hi, "p": p_value,
                        "plo": pair_draws[int(0.025 * len(pair_draws))],
                        "phi": pair_draws[int(0.975 * len(pair_draws)) - 1]})

    order = sorted(range(len(results)), key=lambda i: results[i]["p"])
    running = 1.0
    for rank in range(len(results) - 1, -1, -1):
        i = order[rank]
        running = min(running, results[i]["p"] * len(results) / (rank + 1))
        results[i]["q"] = running

    with_history = sum(1 for r in rows if r["h2h_n"] >= 2)
    doc = f"""{report_stamp.stamp(Path(__file__))}

# Bogey-team study — does head-to-head history predict beyond the price?

Pilot seasons only, {len(rows):,} fixtures. {with_history:,} have at least two prior meetings
between the same pair; the rest fall back to the shrunk base rate, so the feature is effectively
absent for them and the estimate is driven by the fixtures where the belief could apply.

| Hypothesis | Gain (nats) | Division-season 95% | Pair 95% | Perm. p | BH q |
| --- | --- | --- | --- | --- | --- |
""" + "\n".join(
        f"| {r['label']} | {r['gain']:+.5f} | [{r['lo']:+.5f}, {r['hi']:+.5f}] | "
        f"[{r['plo']:+.5f}, {r['phi']:+.5f}] | {r['p']:.3f} | {r['q']:.3f} |" for r in results) + f"""

Baseline log loss of the market price alone: **{base_ll:.4f}**.

## Reading

The belief deserves a fair hearing because it has a mechanism: repeated matchups could encode a
stylistic mismatch that team-level ratings average away. If that mechanism exists and the price
does not carry it, the feature should show a positive gain.

A null here is informative in a way the calendar null was not, because the feature has a plausible
causal story. It would mean either the mechanism is absent, or the market already prices it —
and this design cannot distinguish those two. What it can say is whether a user with that belief
would have profited from acting on it beyond the price, and that is the question that matters.

## Method notes

- Histories are availability-gated: a meeting enters the pair record only when kickoff + 3h is at
  or before the target cutoff, enforced by a pending queue ordered by kickoff.
- Rates are shrunk toward 0.5 with a prior weight of {PRIOR_WEIGHT:.0f}, so a pair with one prior
  meeting does not dominate.
- Resampling is by division-season, not by pair: a pair-level effect that survives resampling whole
  competitions is the strong claim, and the weaker one would need pair-level clusters with very few
  observations each.

## Limits

- Three seasons give most pairs two to six meetings. That is enough to estimate a persistent effect
  only if it is large, and the power here is correspondingly low.
- One market, one corpus, closing prices without timestamps; the T−90 caveat applies.
- "Bogey" in the folklore sense often means a single famous upset, which this design cannot detect
  and would not want to.
"""
    OUT.write_text(doc, encoding="utf-8")

    for r in results:
        print(f"{r['label']}: gain={r['gain']:+.5f} ci=[{r['lo']:+.5f},{r['hi']:+.5f}] "
              f"p={r['p']:.3f} q={r['q']:.3f}")
    print(f"pairs with >=2 meetings: {with_history:,} of {len(rows):,}")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
