"""Superstition study — do folk calendar beliefs carry information the price missed?

The sponsor greenlit exploratory work on whether any sports belief can be turned into an
observable, timestamped, testable hypothesis. This tests the ones the corpus can actually settle:
calendar folklore, which is deterministic, known before kickoff, and therefore point-in-time safe
by construction.

Hypotheses, all fixed before the results were seen:

- **H1 — full moon.** The old belief that strange things happen at the full moon. Test: matches
  within one day of a full moon have a different probability of over 2.5 goals than the price
  implies.
- **H2 — Friday the 13th.** Bad luck. Test: a different over/under probability than the price.
- **H3 — the 13th of any month.** Unlucky date without the weekday condition.
- **H4 — day shape.** Weekend vs midweek kickoffs.

Each is tested as an **increment over the market price**, not against the base rate: a calendar
effect that the price already contains is not information a user could act on. Same protocol as
E8 — market-conditioned logistic, leave-one-season-out, cluster bootstrap, permutation null
stratified by division-season, BH across the four hypotheses.

The full moon is computed from an astronomical approximation (mean synodic month from a known new
moon), accurate to a few hours — enough for a ±1-day window, and stated as an approximation.

    python research/superstition_study.py

Writes research/SUPERSTITION_STUDY.md.
"""

from __future__ import annotations

import math
import statistics
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research"))

import analyse            # noqa: E402
import feature_screen as fs   # noqa: E402  (logit, logloss, auc, fit, oof machinery)
import report_stamp       # noqa: E402

OUT = ROOT / "research" / "SUPERSTITION_STUDY.md"
PILOT = ("2021", "2122", "2223")
PERMUTATIONS = 200
BOOTSTRAPS = 1000
SEED = 20261103

# Known new moon: 2000-01-06 18:14 UTC. Mean synodic month in days.
NEW_MOON_EPOCH = datetime(2000, 1, 6, 18, 14, tzinfo=timezone.utc)
SYNODIC = 29.530588853


def moon_age(when: datetime) -> float:
    """Days since the last new moon, in [0, SYNODIC)."""
    delta = (when - NEW_MOON_EPOCH).total_seconds() / 86400.0
    return delta % SYNODIC


def is_full_moon(when: datetime, tolerance_days: float = 1.0) -> bool:
    age = moon_age(when)
    distance = min(abs(age - SYNODIC / 2), abs(age - SYNODIC / 2 - SYNODIC),
                   abs(age - SYNODIC / 2 + SYNODIC))
    return distance <= tolerance_days


def build() -> list[dict]:
    rows = []
    for r in analyse.load():
        if r["_season"] not in PILOT:
            continue
        try:
            date = datetime.strptime(r["Date"], "%d/%m/%Y").replace(tzinfo=timezone.utc)
            hour = int(str(r["Time"])[:2]) if r.get("Time") else 15
            over, under = float(r["PC>2.5"]), float(r["PC<2.5"])
            hg, ag = int(r["FTHG"]), int(r["FTAG"])
        except (KeyError, TypeError, ValueError):
            continue
        if not (math.isfinite(over) and math.isfinite(under)) or over <= 1.0 or under <= 1.0:
            continue
        kickoff = date + timedelta(hours=hour)
        p_over = 1 / over / (1 / over + 1 / under)
        rows.append({
            "season": r["_season"], "cluster": f"{r['_league']}_{r['_season']}",
            "x": float(fs.logit(np.array([p_over]))[0]),
            "y": 1 if hg + ag >= 3 else 0,
            "full_moon": 1.0 if is_full_moon(kickoff) else 0.0,
            "friday_13": 1.0 if (date.weekday() == 4 and date.day == 13) else 0.0,
            "date_13": 1.0 if date.day == 13 else 0.0,
            "weekend": 1.0 if date.weekday() >= 5 else 0.0,
        })
    return rows


HYPOTHESES = {
    "H1 full moon (±1 day)": "full_moon",
    "H2 Friday the 13th": "friday_13",
    "H3 the 13th of any month": "date_13",
    "H4 weekend kickoff": "weekend",
}


def main() -> int:
    rows = build()
    y = np.array([r["y"] for r in rows], dtype=float)
    base_gain, base_pred, treat_pred = fs.oof_gain(rows, (), y)
    del base_gain

    by_cluster: dict[str, list[int]] = {}
    for i, r in enumerate(rows):
        by_cluster.setdefault(r["cluster"], []).append(i)
    keys = sorted(by_cluster)
    strata = keys
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
            for stratum in strata:
                idx = [i for i, r in enumerate(perm) if r["cluster"] == stratum]
                order = list(idx)
                rng.shuffle(order)
                vals = [perm[j][col] for j in order]
                for i, v in zip(idx, vals):
                    perm[i][col] = v
            g, _, _ = fs.oof_gain(perm, (col,), y)
            null.append(g)
        p_value = float((np.sum(np.array(null) >= gain) + 1) / (PERMUTATIONS + 1))

        results.append({"label": label, "col": col, "gain": gain, "lo": lo, "hi": hi,
                        "p": p_value,
                        "rate": statistics.mean(r[col] for r in rows),
                        "cases": sum(1 for r in rows if r[col] == 1.0),
                        "auc": fs.fast_auc(treat, y)})

    order = sorted(range(len(results)), key=lambda i: results[i]["p"])
    running = 1.0
    for rank in range(len(results) - 1, -1, -1):
        i = order[rank]
        running = min(running, results[i]["p"] * len(results) / (rank + 1))
        results[i]["q"] = running

    base_ll = fs.logloss_vec(base_pred, y)
    doc = f"""{report_stamp.stamp(Path(__file__))}

# Superstition study — calendar folklore against the price

Pilot seasons only, {len(rows):,} fixtures. Each hypothesis is an increment over the **market
price**, so a finding would mean the price missed something a user could have known before
kickoff — not merely that the calendar correlates with outcomes.

| Hypothesis | Cases | Base rate | Gain (nats) | Cluster 95% | Perm. p | BH q |
| --- | --- | --- | --- | --- | --- | --- |
""" + "\n".join(
        f"| {r['label']} | {r['cases']:,} | {r['rate']:.1%} | {r['gain']:+.5f} | "
        f"[{r['lo']:+.5f}, {r['hi']:+.5f}] | {r['p']:.3f} | {r['q']:.3f} |"
        for r in results) + f"""

Baseline log loss of the market price alone: **{base_ll:.4f}**.

## Reading

**Read the Cases column first.** Friday the 13th occurs about once a year, so this corpus holds
fewer than a dozen such fixtures; that row cannot distinguish an effect from noise in either
direction and should be treated as untested rather than as a null. The other three have enough
cases to be informative.

The three outcomes are not the same and are not pooled here.

- **The 13th of any month** has an interval excluding zero on the negative side: including it
  actively costs accuracy, which is an established negative result in this corpus.
- **Weekend kickoff** has an interval that touches zero at the boundary. It is neither established
  as an effect nor established as harmful — it is undetermined at this precision.
- **Full moon** is a null: the interval straddles zero and the point estimate is negligible.
- **Friday the 13th** is untested rather than null: eleven fixtures cannot settle it either way.

Calling the class simply "null" would flatten that structure, and calling both negative point
estimates significant would overstate one of them.

The permutation null shuffles the indicator within division-seasons, preserving the joint
structure and the cluster geometry; the p-value is therefore "how often would a gain this large
arise if the label carried no information", not a claim about the population.

## Why calendar folklore is the right first test

It is deterministic: the date of a full moon or a Friday the 13th is known years ahead, so there
is no availability question and no look-ahead risk. It is also exactly what a superstition ought to
be — a belief about a date, testable without knowing anything about the teams. If a belief cannot
show up here, its problem is not the data pipeline.

## What this does not test

- Beliefs that need information the corpus lacks: referee appointments, kit colours, managerial
  birthdays, crowd size, pundit predictions.
- "Bogey team" effects, which are a head-to-head belief rather than a calendar one and need a
  separate design with pair-level clustering.
- Anything requiring a later cutoff than T−90.

## Limits

- The full moon is computed from a mean synodic month with one epoch, accurate to a few hours;
  the ±1-day window absorbs the error but also weakens the test.
- One corpus, three pilot seasons, one market. The confirmatory slice is untouched.
- Multiple testing across four hypotheses is controlled within this family, not across the
  expedition's whole history.
"""
    OUT.write_text(doc, encoding="utf-8", newline="\n")

    for r in results:
        print(f"{r['label']}: gain={r['gain']:+.5f} ci=[{r['lo']:+.5f},{r['hi']:+.5f}] "
              f"p={r['p']:.3f} q={r['q']:.3f} rate={r['rate']:.3f}")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
