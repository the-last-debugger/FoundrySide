"""Workstream 3: are the model's worst errors a pattern or a tail?

Two questions, both cheap and both deciding what to build next:

1. **After recalibration, what is left?** Re-run the reliability/resolution decomposition on the
   Platt-calibrated forecast. If reliability collapses and resolution is unchanged, the remaining
   deficit is information, and no further calibration work is worth doing.
2. **Are the worst errors systematic?** Take the highest-loss fixtures and ask whether they
   concentrate (a band, a division, a season, a disagreement with the market) or are just the
   tail of a broad distribution.

    python research/residual_study.py

Writes research/RESIDUAL_STUDY.md.
"""

from __future__ import annotations

import csv
import math
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research"))

import calibration_study as cs   # noqa: E402
import gap_diagnosis as gd       # noqa: E402
import report_stamp              # noqa: E402

OUT = ROOT / "research" / "RESIDUAL_STUDY.md"
DELTAS = ROOT / "research" / "pilot_deltas.csv"
TAIL = 0.02


def load() -> list[dict]:
    rows = []
    with DELTAS.open(encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            if r["phase"] != "pilot":
                continue
            rows.append({"season": r["season"], "cluster": r["cluster"],
                         "division": r["league"], "p_model": float(r["p_model"]),
                         "p_market": float(r["p_market"]), "y": int(r["y"]),
                         "kickoff": r["kickoff_utc"]})
    return rows


def with_calibrated(rows: list[dict]) -> list[dict]:
    """Leave-one-season-out Platt predictions; no fold sees its own outcomes."""
    for r in rows:
        r["p_cal"] = r["p_model"]
    for held in sorted({r["season"] for r in rows}):
        train = [{"p": r["p_model"], "y": r["y"]} for r in rows if r["season"] != held]
        a, b = cs.fit_platt(train)
        for r in rows:
            if r["season"] == held:
                r["p_cal"] = cs.sigmoid(a * cs.logit(r["p_model"]) + b)
    return rows


def loss(p: float, y: int) -> float:
    p = min(max(p, 1e-6), 1 - 1e-6)
    return -math.log(p) if y else -math.log(1 - p)


def decompose(rows: list[dict], key: str) -> dict[str, float]:
    """Reliability and resolution, plus the raw Brier and the within-bin remainder."""
    n = len(rows)
    base = statistics.mean(r["y"] for r in rows)
    bins: dict[int, list[dict]] = {}
    for r in rows:
        bins.setdefault(min(9, int(r[key] * 10)), []).append(r)
    reliability = resolution = 0.0
    for group in bins.values():
        w = len(group) / n
        predicted = statistics.mean(g[key] for g in group)
        observed = statistics.mean(g["y"] for g in group)
        reliability += w * (predicted - observed) ** 2
        resolution += w * (observed - base) ** 2
    binned = reliability - resolution + base * (1 - base)
    raw = statistics.mean((r[key] - r["y"]) ** 2 for r in rows)
    return {"reliability": reliability, "resolution": resolution,
            "brier_binned": binned, "brier_raw": raw, "within": raw - binned}


def table(rows: list[dict], key: str) -> str:
    lines = ["| Forecast | Reliability | Resolution | Brier (raw) |",
             "| --- | --- | --- | --- |"]
    for label, col in (("Raw model", "p_model"), ("Platt (out-of-fold)", "p_cal"),
                       ("Market", "p_market")):
        d = decompose(rows, col)
        lines.append(f"| {label} | {d['reliability']:.4f} | {d['resolution']:.4f} | "
                     f"{d['brier_raw']:.4f} |")
    return "\n".join(lines)


def tail_profile(rows: list[dict]) -> str:
    for r in rows:
        r["loss"] = loss(r["p_model"], r["y"])
        r["agree"] = (r["p_model"] >= 0.5) == (r["p_market"] >= 0.5)
    ordered = sorted(rows, key=lambda r: -r["loss"])
    cutoff = int(len(ordered) * TAIL)
    tail = ordered[:cutoff]

    def share(subset, pred):
        return sum(1 for r in subset if pred(r)) / len(subset)

    def band(r):
        return f"{int(r['p_model'] * 10) * 10}–{int(r['p_model'] * 10) * 10 + 10}%"

    lines = [f"| Property | Worst {int(TAIL * 100)}% | All fixtures |",
             "| --- | --- | --- |",
             f"| n | {len(tail)} | {len(rows)} |",
             f"| Disagrees with the market's side | {share(tail, lambda r: not r['agree']):.1%} | "
             f"{share(rows, lambda r: not r['agree']):.1%} |",
             f"| Model in 20–40% band | "
             f"{share(tail, lambda r: 0.2 <= r['p_model'] < 0.4):.1%} | "
             f"{share(rows, lambda r: 0.2 <= r['p_model'] < 0.4):.1%} |",
             f"| Over-predicted (model above the outcome) | "
             f"{share(tail, lambda r: r['p_model'] > r['y']):.1%} | "
             f"{share(rows, lambda r: r['p_model'] > r['y']):.1%} |"]

    by_band: dict[str, int] = {}
    for r in tail:
        by_band[band(r)] = by_band.get(band(r), 0) + 1
    lines += ["", "| Band | Share of the worst tail |", "| --- | --- |"]
    for b in sorted(by_band, key=lambda x: -by_band[x])[:5]:
        lines.append(f"| {b} | {by_band[b] / len(tail):.1%} |")
    return "\n".join(lines)


def main() -> int:
    rows = with_calibrated(load())
    raw_ll = statistics.mean(loss(r["p_model"], r["y"]) for r in rows)
    cal_ll = statistics.mean(loss(r["p_cal"], r["y"]) for r in rows)
    mkt_ll = statistics.mean(loss(r["p_market"], r["y"]) for r in rows)

    doc = f"""{report_stamp.stamp(Path(__file__))}

# Workstream 3 — what is left after recalibration, and what the worst errors are

Pilot seasons only. Platt calibration is fitted leave-one-season-out, so every `p_cal` is
out of fold.

## Log loss

| Forecast | Log loss |
| --- | --- |
| Raw model | {raw_ll:.4f} |
| Platt (out-of-fold) | {cal_ll:.4f} |
| Market | {mkt_ll:.4f} |

## Decomposition after calibration

{table(rows, 'p_model')}

The middle row of the first table is the one that matters: if recalibration collapses
reliability while resolution stays where it was, the remaining deficit is information and no
further calibration work can help.

## The worst {int(TAIL * 100)}% of fixtures

{tail_profile(rows)}

## Reading

The tail profile answers one question only: whether the large losses are a *class* of fixture
the model could be taught to handle, or the upper tail of a distribution that is simply wide.
Concentration on disagreeing-with-the-market fixtures would suggest the model is asserting a
view; concentration in a band would suggest overconfidence; neither would suggest a fix on its
own.

## Limits

- The tail is defined by the model's own loss, so it is selected on the outcome; the profile is
  descriptive, and a "pattern" in it is not evidence that the pattern is exploitable.
- Bins are equal-width; reliability and resolution depend on that choice.
- One model, one market, pilot only, with the closing-price timing caveat.
"""
    OUT.write_text(doc, encoding="utf-8")

    print(f"raw={raw_ll:.4f} platt={cal_ll:.4f} market={mkt_ll:.4f}")
    for label, col in (("raw", "p_model"), ("cal", "p_cal"), ("market", "p_market")):
        d = decompose(rows, col)
        print(f"{label}: rel={d['reliability']:.4f} res={d['resolution']:.4f} "
              f"brier={d['brier_raw']:.4f}")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
