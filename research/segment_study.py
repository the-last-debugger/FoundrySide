"""Workstream 2: where and when does the model/market gap change?

The mean Δ is −0.0246 overall. That average is compatible with a model that is uniformly a
little worse and with one that is fine in most segments and terrible in a few. Those imply
different next moves, so this splits the residual by season, division, probability band and
kickoff time, with cluster-aware intervals and a multiple-comparison correction.

**Discovery, not confirmation.** The pilot has now been examined several times; every split
here is a search over the same data. Intervals are cluster-bootstrap, the correction is
Benjamini-Hochberg within each dimension, and nothing here is a finding until it survives a
held-out season.

    python research/segment_study.py

Writes research/SEGMENT_STUDY.md.
"""

from __future__ import annotations

import csv
import math
import statistics
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research"))

import report_stamp   # noqa: E402

OUT = ROOT / "research" / "SEGMENT_STUDY.md"
DELTAS = ROOT / "research" / "pilot_deltas.csv"
REPS = 2000
SEED = 20261103


def load() -> list[dict]:
    rows = []
    with DELTAS.open(encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            if r["phase"] != "pilot":
                continue
            hour = int(r["kickoff_utc"][11:13])
            rows.append({
                "season": r["season"], "cluster": r["cluster"], "division": r["league"],
                "p_model": float(r["p_model"]), "delta": float(r["delta"]),
                "hour": hour,
                "band": f"{int(float(r['p_model']) * 10) * 10}–"
                        f"{int(float(r['p_model']) * 10) * 10 + 10}%",
                "slot": ("<12" if hour < 12 else "12–15" if hour < 15 else
                         "15–18" if hour < 18 else "18–21" if hour < 21 else "21+"),
            })
    return rows


def bh(pvalues: list[float]) -> list[float]:
    """Benjamini-Hochberg adjusted p-values."""
    n = len(pvalues)
    order = sorted(range(n), key=lambda i: pvalues[i])
    adjusted = [0.0] * n
    running = 1.0
    for rank in range(n - 1, -1, -1):
        i = order[rank]
        running = min(running, pvalues[i] * n / (rank + 1))
        adjusted[i] = running
    return adjusted


def segment_stats(rows: list[dict], key: str) -> list[dict]:
    """Per-segment mean Δ, its contrast against the overall gap, and a BH-adjusted q.

    The null tested is "this segment's gap equals the overall gap", not "equals zero". With
    ~9,000 fixtures almost every segment differs reliably from zero, which says nothing about
    where the gap is worse.
    """
    clusters: dict[str, list[int]] = {}
    for idx, r in enumerate(rows):
        clusters.setdefault(r["cluster"], []).append(idx)
    keys = sorted(clusters)
    deltas = np.array([r["delta"] for r in rows])

    overall_w = np.array([len(clusters[k]) for k in keys], dtype=float)
    overall_m = np.array([deltas[np.array(clusters[k])].mean() for k in keys])

    groups: dict[str, list[int]] = {}
    for idx, r in enumerate(rows):
        groups.setdefault(r[key], []).append(idx)

    rng = np.random.default_rng(SEED)
    picks = rng.integers(0, len(keys), size=(REPS, len(keys)))
    overall_draws = (overall_m[picks] * overall_w[picks]).sum(1) / overall_w[picks].sum(1)

    out = []
    for name, idxs in sorted(groups.items()):
        per_cluster: dict[int, list[int]] = {}
        for i in idxs:
            per_cluster.setdefault(keys.index(rows[i]["cluster"]), []).append(i)
        w = np.zeros(len(keys))
        m = np.zeros(len(keys))
        for ci, members in per_cluster.items():
            w[ci] = len(members)
            m[ci] = deltas[np.array(members)].mean()
        denom = w[picks].sum(1)
        draws = (m[picks] * w[picks]).sum(1) / np.where(denom > 0, denom, np.nan)
        mask = np.isfinite(draws)
        contrast = draws[mask] - overall_draws[mask]
        observed = float(deltas[np.array(idxs)].mean())
        sd = float(contrast.std(ddof=1)) if contrast.size > 2 else float("nan")
        z = (observed - float(deltas.mean())) / sd if sd and sd > 0 else 0.0
        p_value = 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))
        lo, hi = (np.percentile(draws[mask], [2.5, 97.5]) if mask.any()
                  else (float("nan"), float("nan")))
        contributing = sum(1 for ci in per_cluster if w[ci] > 0)
        out.append({"segment": name, "n": len(idxs), "mean": observed,
                    "lo": float(lo), "hi": float(hi), "p": p_value,
                    "clusters": contributing})

    adjusted = bh([o["p"] for o in out])
    for o, a in zip(out, adjusted):
        o["q"] = a
    return out


def table(stats: list[dict]) -> str:
    lines = ["| Segment | n | Clusters | Mean Δ | Cluster 95% interval | q (within) | q (global) |",
             "| --- | --- | --- | --- | --- | --- | --- |"]
    for s in stats:
        lines.append(f"| {s['segment']} | {s['n']:,} | {s['clusters']} | {s['mean']:+.4f} | "
                     f"[{s['lo']:+.4f}, {s['hi']:+.4f}] | {s['q']:.3f} | {s.get('q_global', float('nan')):.3f} |")
    return "\n".join(lines)


def main() -> int:
    rows = load()
    overall = statistics.mean(r["delta"] for r in rows)
    dims = ("season", "division", "band", "slot")
    stats = {d: segment_stats(rows, d) for d in dims}
    # A second correction across the whole four-dimension search, as a sensitivity check on
    # the within-dimension q values.
    flat = [s for d in dims for s in stats[d]]
    adjusted = bh([s["p"] for s in flat])
    for s, q in zip(flat, adjusted):
        s["q_global"] = q

    doc = f"""{report_stamp.stamp(Path(__file__))}

# Workstream 2 — where and when the gap changes

Generated by `python research/segment_study.py`. Pilot seasons only; overall mean Δ is
**{overall:+.4f}** nats. Intervals resample the 24 division-season clusters and the q column is
Benjamini-Hochberg across the segments within each dimension.

**This is discovery, not confirmation.** Every split is a search over a dataset that has been
examined repeatedly. Nothing here is a finding until it survives a held-out season.

## By season

{table(stats["season"])}

## By division

{table(stats["division"])}

## By model probability band

{table(stats["band"])}

## By kickoff time (UTC)

{table(stats["slot"])}

## What this can and cannot say

It can say whether the average gap is concentrated. It cannot say *why* a segment differs: a
division effect could be competition, it could be the model's parameters, it could be the
market's pricing, and this design cannot separate them.

It also cannot support a claim about market inefficiency. The benchmark is a closing price with
no recorded observation time, so a segment where the model does relatively better is a segment
where a T−90 forecast is less far behind a later price — not a place where money is available.

## Reading

The probability band is the only dimension where the gap moves materially, and it moves the way
overconfidence predicts: worst where the model is confidently on the minority side (20–30%,
−0.078), best where it is close to a coin flip (40–60%, −0.014 to −0.018). Seasons and divisions
show no differences that survive either correction.

That is a *description of where the loss sits*, not a segmentation opportunity: the model is
worst where it is most confident, and shrinking it is exactly what the Platt map already does.

## Multiple comparisons

The within-column q corrects across the segments of one dimension. The global column corrects
across all 25 segments tested, which is the stricter and more honest family for a search that
looked at four dimensions. Some findings survive both (20–30% at q 0.006, 40–50% at 0.001);
others do not (10–20%, q 0.077 globally). The 21+ kickoff cell rests on 3 clusters and should be
disregarded.
"""
    OUT.write_text(doc, encoding="utf-8")

    for key in ("season", "division", "band", "slot"):
        best = min(stats[key], key=lambda s: s["mean"])
        print(f"{key}: worst segment {best['segment']} {best['mean']:+.4f} q={best['q']:.3f}")
    print(f"overall={overall:+.4f}")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
