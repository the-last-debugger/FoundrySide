"""Style-mismatch study — do team *shapes* interact in a way the price misses?

Additive ratings say a match's goals are attack × defence and nothing else. Football people say
shapes interact: a side that scores heavily meets a side that concedes heavily and the result is
not what the two averages suggest. That is a real mechanism rather than folklore, and it is
testable with nothing but results.

Three hypotheses, fixed before the results:

- **S1 — attack/defence interaction.** The product of the home side's attacking excess and the
  away side's defensive excess carries information beyond the price.
- **S2 — home/away asymmetry.** A club whose home and away scoring rates diverge sharply is
  differently predictable than its average suggests.
- **S3 — scoring volatility.** A club whose goals vary widely from match to match behaves
  differently from one whose do not, at the same mean.

All features are built from completed matches only, gated by the pending-result queue at each
fixture's cutoff.

    python research/style_mismatch.py

Writes research/STYLE_MISMATCH.md.
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

OUT = ROOT / "research" / "STYLE_MISMATCH.md"
PILOT = ("2021", "2122", "2223")
PERMUTATIONS = 200
BOOTSTRAPS = 1000
SEED = 20261103
WINDOW = 10
SHRINK = 5.0


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
                    "hf": hg, "af": ag})
    raw.sort(key=lambda r: r["kickoff"])

    # Per-team histories: goals scored and conceded, split by venue.
    scored_home: dict[tuple[str, str], list[int]] = defaultdict(list)
    scored_away: dict[tuple[str, str], list[int]] = defaultdict(list)
    conc_home: dict[tuple[str, str], list[int]] = defaultdict(list)
    conc_away: dict[tuple[str, str], list[int]] = defaultdict(list)
    all_scored: dict[tuple[str, str], list[int]] = defaultdict(list)
    league_mean: dict[tuple[str, str], list[int]] = defaultdict(list)

    pending: list[tuple[datetime, dict]] = []
    out = []
    for r in raw:
        due = [p for p in pending if p[0] <= r["cutoff"]]
        pending = [p for p in pending if p[0] > r["cutoff"]]
        for _at, row in due:
            lk = (row["league"], row["season"])
            league_mean[lk].append(row["hf"] + row["af"])
            for team, scored, conc, venue in (
                    (row["home"], row["hf"], row["af"], "h"),
                    (row["away"], row["af"], row["hf"], "a")):
                key = (row["league"], team)
                (scored_home if venue == "h" else scored_away)[key].append(scored)
                (conc_home if venue == "h" else conc_away)[key].append(conc)
                all_scored[key].append(scored)

        baseline = statistics.mean(league_mean[(r["league"], r["season"])]) if league_mean[(r["league"], r["season"])] else 2.6
        half = baseline / 2

        def att(team: str, venue: str) -> float:
            hist = (scored_home if venue == "h" else scored_away)[(r["league"], team)][-WINDOW:]
            if not hist:
                return 0.0
            return (sum(hist) + SHRINK * half) / (len(hist) + SHRINK) - half

        def dfn(team: str, venue: str) -> float:
            hist = (conc_home if venue == "h" else conc_away)[(r["league"], team)][-WINDOW:]
            if not hist:
                return 0.0
            return (sum(hist) + SHRINK * half) / (len(hist) + SHRINK) - half

        home_att, away_df = att(r["home"], "h"), dfn(r["away"], "a")
        r["s_attack"] = home_att * away_df

        hs = scored_home[(r["league"], r["home"])][-WINDOW:]
        as_ = scored_away[(r["league"], r["home"])][-WINDOW:]
        r["s_asym"] = ((statistics.mean(hs) if hs else half)
                       - (statistics.mean(as_) if as_ else half))

        hist = all_scored[(r["league"], r["home"])][-WINDOW:]
        r["s_vol"] = statistics.pstdev(hist) if len(hist) >= 3 else 0.0

        out.append(r)
        pending.append((r["kickoff"] + timedelta(hours=3), r))
        pending.sort(key=lambda p: p[0])
    return out


HYPOTHESES = {
    "S1 attack/defence interaction": "s_attack",
    "S2 home/away asymmetry": "s_asym",
    "S3 scoring volatility": "s_vol",
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
        results.append({"label": label, "gain": gain, "lo": lo, "hi": hi, "p": p_value,
                        "sd": statistics.pstdev([r[col] for r in rows])})

    order = sorted(range(len(results)), key=lambda i: results[i]["p"])
    running = 1.0
    for rank in range(len(results) - 1, -1, -1):
        i = order[rank]
        running = min(running, results[i]["p"] * len(results) / (rank + 1))
        results[i]["q"] = running

    doc = f"""{report_stamp.stamp(Path(__file__))}

# Style-mismatch study — do team shapes interact beyond additive ratings?

Pilot seasons only, {len(rows):,} fixtures. Each feature enters a market-conditioned logistic, so
a gain means information the closing price did not contain.

| Hypothesis | Feature SD | Gain (nats) | Cluster 95% | Perm. p | BH q |
| --- | --- | --- | --- | --- | --- |
""" + "\n".join(
        f"| {r['label']} | {r['sd']:.3f} | {r['gain']:+.5f} | "
        f"[{r['lo']:+.5f}, {r['hi']:+.5f}] | {r['p']:.3f} | {r['q']:.3f} |"
        for r in results) + f"""

Baseline log loss of the market price alone: **{base_ll:.4f}**.

## Reading

S1 is the interesting one: it is the formal version of "a good attack against a bad defence
produces more than the ratings suggest", and unlike the calendar beliefs it has a mechanism.
S2 and S3 are controls for the same idea expressed as venue asymmetry and consistency.

A gain of zero with a tight interval means the market already prices the interaction or the
interaction is not there. A gain that is positive but an order of magnitude below the 0.0246
deficit is a curiosity, not a route.

## Method

- Features use only completed matches, gated by the pending-result queue at each cutoff.
- Attack and defence excess are shrunk toward the league mean with a prior weight of {SHRINK:.0f}
  over a {WINDOW}-match window, so a promoted side with two matches does not dominate.
- Permutation is stratified by division-season, preserving cluster geometry.

## Limits

- Ten matches is a short window for a style estimate; longer windows would dilute a change of
  manager or squad.
- One corpus, one market, closing prices without timestamps; the T−90 caveat applies.
- Style is inferred from goals alone, which cannot separate a high press from a direct long-ball
  side; this tests the *interaction* that goals can express, not the tactical taxonomy.
"""
    OUT.write_text(doc, encoding="utf-8", newline="\n")

    for r in results:
        print(f"{r['label']}: gain={r['gain']:+.5f} ci=[{r['lo']:+.5f},{r['hi']:+.5f}] "
              f"p={r['p']:.3f} q={r['q']:.3f}")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
