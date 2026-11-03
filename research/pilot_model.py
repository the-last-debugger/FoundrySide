"""Out-of-fold pilot predictions: a simple, point-in-time goals model.

**Point-in-time, properly this time.** An earlier version sorted fixtures by kickoff and
applied a result to the feature state as soon as the match had started. That proves nothing
about availability: a match kicking off two hours before the target can still be in progress
at the target's T−90 cutoff. This version keeps results pending until they could plausibly
be *known* — kickoff plus three hours, which covers full time, stoppage and publication —
and applies only those available at the target fixture's cutoff. A result that is still
pending at the cutoff is invisible to the prediction, exactly as it would have been.

Only the **pilot** phase is processed. An earlier version also predicted and scored the
confirmatory seasons; that is confirmatory scoring, which is not authorised, and the rows
have been removed.

    python research/pilot_model.py

Writes research/pilot_deltas.csv and research/PILOT_PREDICTIONS.md.
"""

from __future__ import annotations

import csv
import hashlib
import math
import statistics
import sys
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research"))

import pilot          # noqa: E402
import report_stamp   # noqa: E402
import variance       # noqa: E402

OUT_CSV = ROOT / "research" / "pilot_deltas.csv"
OUT_MD = ROOT / "research" / "PILOT_PREDICTIONS.md"
MANIFEST = ROOT / "research" / "data_manifest.csv"

PRIOR_HOME = 1.45
PRIOR_AWAY = 1.15
SHRINK = 6.0
RESULT_DELAY = timedelta(hours=3)   # when a result could plausibly be known


def poisson_pmf(lam: float, k: int) -> float:
    return math.exp(-lam) * lam ** k / math.factorial(k)


def p_over_25(lam_home: float, lam_away: float) -> float:
    p_under = 0.0
    for h in range(3):
        for a in range(3 - h):
            p_under += poisson_pmf(lam_home, h) * poisson_pmf(lam_away, a)
    return max(0.0, min(1.0, 1.0 - p_under))


class TeamStats:
    def __init__(self) -> None:
        self.home_for = self.home_against = 0
        self.home_n = 0
        self.away_for = self.away_against = 0
        self.away_n = 0

    def rates(self, league_home: float, league_away: float):
        home_attack = (self.home_for + SHRINK * league_home) / (self.home_n + SHRINK)
        home_defence = (self.home_against + SHRINK * league_away) / (self.home_n + SHRINK)
        away_attack = (self.away_for + SHRINK * league_away) / (self.away_n + SHRINK)
        away_defence = (self.away_against + SHRINK * league_home) / (self.away_n + SHRINK)
        return home_attack, home_defence, away_attack, away_defence


def logloss(p: float, y: int) -> float:
    p = min(max(p, 1e-6), 1 - 1e-6)
    return -math.log(p) if y else -math.log(1 - p)


def predict(rows: list[dict]) -> list[dict]:
    """Pilot predictions in kickoff order, using only results available at the cutoff."""
    ordered = sorted(rows, key=lambda r: (r["league"], r["season"], r["kickoff_utc"]))
    teams: dict[tuple[str, str, str], TeamStats] = {}
    league_running: dict[tuple[str, str], list[float]] = {}
    pending: list[tuple[object, dict]] = []
    out: list[dict] = []

    def apply_result(f: dict) -> None:
        league, season = f["league"], f["season"]
        hs = teams.setdefault((league, season, f["home"]), TeamStats())
        as_ = teams.setdefault((league, season, f["away"]), TeamStats())
        hs.home_for += f["home_goals"]
        hs.home_against += f["away_goals"]
        hs.home_n += 1
        as_.away_for += f["away_goals"]
        as_.away_against += f["home_goals"]
        as_.away_n += 1
        running = league_running.setdefault((league, season), [0.0, 0.0, 0.0])
        running[0] += f["home_goals"]
        running[1] += f["away_goals"]
        running[2] += 1

    i = 0
    while i < len(ordered):
        key = (ordered[i]["league"], ordered[i]["season"], ordered[i]["kickoff_utc"])
        group = []
        while i < len(ordered) and (ordered[i]["league"], ordered[i]["season"],
                                    ordered[i]["kickoff_utc"]) == key:
            group.append(ordered[i])
            i += 1

        cutoff = group[0]["cutoff_utc"]
        # Only results that could be known by this cutoff may inform the prediction.
        still_pending = []
        for available_at, f in pending:
            if available_at <= cutoff:
                apply_result(f)
            else:
                still_pending.append((available_at, f))
        pending = still_pending

        league, season, _kick = key
        hg, ag, games = league_running.get((league, season), [0.0, 0.0, 0.0])
        lh = (hg + 40 * PRIOR_HOME) / (games + 40)
        la = (ag + 40 * PRIOR_AWAY) / (games + 40)

        for f in group:
            hs = teams.setdefault((league, season, f["home"]), TeamStats())
            as_ = teams.setdefault((league, season, f["away"]), TeamStats())
            hs_h_att, hs_h_def, _a1, _a2 = hs.rates(lh, la)
            _b1, _b2, as_a_att, as_a_def = as_.rates(lh, la)
            lam_h = max(0.2, min(4.0, hs_h_att * as_a_def / max(lh, 0.1)))
            lam_a = max(0.2, min(4.0, as_a_att * hs_h_def / max(la, 0.1)))
            row = dict(f)
            row["p_model"] = p_over_25(lam_h, lam_a)
            row["delta"] = logloss(row["p_market"], row["y"]) - logloss(row["p_model"], row["y"])
            out.append(row)
            pending.append((f["kickoff_utc"] + RESULT_DELAY, f))
        pending.sort(key=lambda item: item[0])
    return out


def summarise(rows: list[dict]) -> str:
    n = len(rows)
    model_ll = statistics.mean(logloss(r["p_model"], r["y"]) for r in rows)
    market_ll = statistics.mean(logloss(r["p_market"], r["y"]) for r in rows)
    mean = statistics.mean(r["delta"] for r in rows)
    sd = statistics.stdev(r["delta"] for r in rows)
    return "\n".join([
        "| Measure | Value |",
        "| --- | --- |",
        f"| Fixtures | {n:,} |",
        f"| Market log loss (pilot slice) | {market_ll:.4f} nats |",
        f"| Model log loss (pilot slice) | {model_ll:.4f} nats |",
        f"| Mean Δ (market − model) | {mean:+.4f} nats |",
        f"| SD of Δ | {sd:.4f} |",
    ])


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16] if path.exists() else "missing"


def main() -> int:
    framed, _rejects = pilot.frame(pilot.analyse.load())
    pilot_rows = predict([dict(r) for r in framed if r["phase"] == "pilot"])
    assert all(r["phase"] == "pilot" for r in pilot_rows)

    with OUT_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["phase", "cluster", "league", "season", "kickoff_utc",
                         "p_market", "p_model", "y", "delta"])
        for r in pilot_rows:
            writer.writerow(["pilot", r["cluster"], r["league"], r["season"],
                             r["kickoff_utc"].isoformat(), f"{r['p_market']:.6f}",
                             f"{r['p_model']:.6f}", r["y"], f"{r['delta']:.6f}"])

    by_cluster: dict[str, list[float]] = {}
    for r in pilot_rows:
        by_cluster.setdefault(r["cluster"], []).append(r["delta"])
    comp = variance.weighted_components(list(by_cluster.values()))
    comp_ci = variance.bootstrap_between(list(by_cluster.values()))

    doc = f"""{report_stamp.stamp(Path(__file__))}

# Pilot predictions — first out-of-fold Δ, pilot seasons only

Generated by `python research/pilot_model.py`.

- Input manifest: `research/data_manifest.csv` sha256 {sha(MANIFEST)}
- Output deltas: `research/pilot_deltas.csv` sha256 {sha(OUT_CSV)}
- Model: multiplicative goals model with shrinkage; results become visible at kickoff + 3h
  and are applied only when that time is at or before the fixture's own T−90 cutoff.

## Descriptive results, pilot slice only

{summarise(pilot_rows)}

## Variance components, for the fixture-weighted estimand

| Quantity | Value |
| --- | --- |
| σ_w (weighted within-cluster) | {comp['sigma_w']:.4f} |
| Between-cluster variance, untruncated | {comp['var_between']:+.6f} |
| σ_b (truncated at zero) | {comp['sigma_b']:.4f} |
| Bootstrap 95% interval for the between-cluster variance | [{comp_ci[0]:+.6f}, {comp_ci[1]:+.6f}] |
| Clusters | {int(comp['k'])} |

**The between-cluster variance is not measured as zero.** It is estimated at
{comp['var_between']:+.6f}, which is at or below the boundary; the truncated σ_b of
{comp['sigma_b']:.4f} exists so the power calculation has a non-negative input, not because
the data established that heterogeneity is absent. The interval above shows what the
sample actually supports.

## Timing limitation of the market comparison

The benchmark is a de-vigged **closing** price. The closing quote's observation time is not
recorded in the source, so this Δ compares a T−90 model against a market benchmark whose
information time is unknown and is certainly later than T−90. It is a useful descriptive
reference; it is **not** a matched-information-time comparison, and it cannot support a
claim that the model did or did not beat a price that was available at T−90.

## What this is

The first measured distribution of Δ in the project, on the pilot seasons, produced without
touching the confirmatory seasons.

## What this is not

- **Not an edge claim**, and not a matched-time market comparison (see above).
- **Not the confirmatory result.** The confirmatory seasons were not predicted.
- **Not a good model.** It is the simplest thing that produces an honest Δ.
"""
    OUT_MD.write_text(doc, encoding="utf-8")

    print(f"pilot rows={len(pilot_rows)}")
    print(f"market_ll={stats_market(pilot_rows):.4f} model_ll={stats_model(pilot_rows):.4f}")
    print(f"mean_delta={statistics.mean(r['delta'] for r in pilot_rows):+.4f} "
          f"sigma_w={comp['sigma_w']:.4f} var_between={comp['var_between']:+.6f}")
    print(f"wrote {OUT_CSV.relative_to(ROOT)} and {OUT_MD.relative_to(ROOT)}")
    return 0


def stats_market(rows):
    return statistics.mean(logloss(r["p_market"], r["y"]) for r in rows)


def stats_model(rows):
    return statistics.mean(logloss(r["p_model"], r["y"]) for r in rows)


if __name__ == "__main__":
    raise SystemExit(main())
