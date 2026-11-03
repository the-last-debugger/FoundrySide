"""Sizing for the confirmatory design, by resampling real pilot clusters.

**No variance components.** An earlier version estimated `σ_w` and `σ_b` and plugged them
into a formula. Review correctly rejected that: the decomposition is not justified for
unequal clusters, and agreement between two implementations of the same formula proves
nothing about the formula. This version removes the decomposition entirely.

Method: resample 16 clusters with replacement from the 24 pilot clusters, resample fixtures
within each to the confirmatory cluster sizes, add the target effect, and run the actual
confirmatory test — the cluster-robust t on the fixture-weighted mean. Power is the
rejection rate. That uses the empirical Δ distribution including its shape, respects the
real cluster sizes, and needs no parametric component at all.

    python research/pilot_power.py --deltas research/pilot_deltas.csv

Writes research/PILOT_POWER.md.
"""

from __future__ import annotations

import csv
import hashlib
import math
import statistics
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research"))

import report_stamp  # noqa: E402

OUT = ROOT / "research" / "PILOT_POWER.md"

TARGET = 0.01
T_CRIT = 2.1314495        # two-sided 0.05, 15 df (16 clusters)
SIMS = 800
SEED = 20261103


def confirmatory_sizes() -> np.ndarray:
    """The confirmatory cluster sizes, taken from the frame rather than hard-coded."""
    import pilot  # local import keeps the module importable without the corpus

    framed, _ = pilot.frame(pilot.analyse.load())
    counts: dict[str, int] = {}
    for f in framed:
        if f["phase"] == "confirmatory":
            counts[f["cluster"]] = counts.get(f["cluster"], 0) + 1
    return np.array(sorted(counts.values()), dtype=float)


def load_deltas(path: Path) -> list[np.ndarray]:
    by_cluster: dict[str, list[float]] = {}
    with path.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            if row["phase"] != "pilot":
                continue
            by_cluster.setdefault(row["cluster"], []).append(float(row["delta"]))
    return [np.array(by_cluster[k]) for k in sorted(by_cluster)]


def _simulate(clusters: list[np.ndarray], sizes: np.ndarray, delta: float,
              sims: int = SIMS, seed: int = SEED) -> tuple[np.ndarray, np.ndarray]:
    """Simulate the confirmatory design; return (weighted mean, t statistic) per draw.

    Clusters are drawn **probability-proportional-to-size**, not uniformly. The estimand is
    the fixture-weighted mean, so each fixture should have an equal chance of being
    represented; drawing clusters uniformly would instead give each *cluster* an equal
    chance and target the unweighted mean of cluster means. When cluster means are
    associated with cluster size the two differ, and a uniform draw would leave the
    simulated null off-centre for the declared estimand.
    """
    rng = np.random.default_rng(seed)
    n_all = sum(len(c) for c in clusters)
    pilot_mean = float(sum(c.sum() for c in clusters) / n_all)
    centred = [c - pilot_mean for c in clusters]

    pool_sizes = np.array([len(c) for c in centred], dtype=float)
    probs = pool_sizes / pool_sizes.sum()
    k_pool = len(centred)
    k = len(sizes)
    w = sizes / sizes.sum()

    grands = np.empty(sims)
    stats = np.empty(sims)
    for s in range(sims):
        picked = rng.choice(k_pool, size=k, replace=True, p=probs)
        means = np.empty(k)
        for j, idx in enumerate(picked):
            draw = rng.choice(centred[idx], size=int(sizes[j]), replace=True)
            means[j] = draw.mean() + delta
        grand = float((w * means).sum())
        var = (k / (k - 1)) * float(((w * (means - grand)) ** 2).sum())
        grands[s] = grand
        stats[s] = grand / math.sqrt(var) if var > 0 else 0.0
    return grands, stats


def design_power(clusters: list[np.ndarray], sizes: np.ndarray, delta: float,
                 sims: int = SIMS, seed: int = SEED) -> float:
    """Rejection rate of the confirmatory t when the true effect is `delta`."""
    _grands, stats = _simulate(clusters, sizes, delta, sims, seed)
    return float(np.mean(np.abs(stats) > T_CRIT))


def simulated_mean(clusters: list[np.ndarray], sizes: np.ndarray, delta: float,
                   sims: int = SIMS, seed: int = SEED) -> float:
    """Mean of the simulated statistic — used to check the null sits where it should."""
    grands, _stats = _simulate(clusters, sizes, delta, sims, seed)
    return float(np.mean(grands))


def power_threshold(clusters: list[np.ndarray], sizes: np.ndarray,
                    target: float = 0.80, sims: int = 300,
                    hi: float = 0.05, steps: int = 6) -> tuple[float, float]:
    """Effect size at which power reaches `target`, by bisection.

    Returns (effect, bracket half-width). The bracket is the precision the simulation
    supports, so the number is quoted with it rather than to four decimals.
    """
    if design_power(clusters, sizes, hi, sims=sims) < target:
        return (float("nan"), float("nan"))
    low, high = 0.0, hi
    for _ in range(steps):
        mid = (low + high) / 2
        if design_power(clusters, sizes, mid, sims=sims) >= target:
            high = mid
        else:
            low = mid
    return (high, (high - low) / 2)


def mc_se(p: float, sims: int = SIMS) -> float:
    return math.sqrt(max(p * (1 - p), 1e-12) / sims)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16] if path.exists() else "missing"


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if "--deltas" not in args:
        raise SystemExit("--deltas is required: this sizing runs on measured pilot "
                         "predictions, and there is no synthetic mode any more.")
    deltas_path = Path(args[args.index("--deltas") + 1])

    clusters = load_deltas(deltas_path)
    if not clusters:
        raise SystemExit(f"no pilot rows found in {deltas_path}")

    sizes = confirmatory_sizes()
    power = design_power(clusters, sizes, TARGET)
    type_one = design_power(clusters, sizes, 0.0)
    stability = [design_power(clusters, sizes, TARGET, seed=SEED + 31 * (i + 1))
                 for i in range(2)]
    se = mc_se(power)
    threshold, bracket = power_threshold(clusters, sizes)
    null_mean = simulated_mean(clusters, sizes, 0.0)

    doc = f"""{report_stamp.stamp(Path(__file__))}

# Sizing for the confirmatory design

Generated by `python research/pilot_power.py`.

- Input: `{deltas_path.as_posix()}` sha256 {digest(deltas_path)}
- Pilot clusters: {len(clusters)}; confirmatory clusters: {len(sizes)}
- Simulations: {SIMS:,}; seed {SEED}
- Test: cluster-robust t on the fixture-weighted mean, 15 df, two-sided 5%

## Method, and why it is not a formula

The design is resampled rather than modelled. The pilot Δ are first **centred** on their
fixture-weighted mean, then the target effect is imposed. Each simulation draws 16 clusters
**with probability proportional to pilot cluster size** — the estimand is the fixture-weighted
mean, so each fixture should have an equal chance of being represented, and uniform
cluster sampling would target the unweighted mean of cluster means instead — resamples
fixtures within each to the confirmatory cluster sizes, and runs the confirmatory test.
Power is the fraction of simulations that reject.

Centring is not a detail. The pilot mean is about −0.025 — this model is behind the market —
so imposing +0.01 on uncentred data would test "still behind, slightly less" and a two-sided
test would reject on the existing disadvantage. An earlier version did exactly that and
reported 93.5%, which was not power for a 0.01-nat improvement. The centred procedure tests
what it claims to test.

This uses the empirical distribution of Δ — its shape, its skew, its heavy tails — and the
real cluster sizes. It needs **no** `σ_w`, no `σ_b`, and no assumption that either is
unbiased for unequal clusters. An earlier version estimated those components and plugged
them into a formula; review rejected the estimator and, rather than defend it, the
component decomposition has been removed from the sizing path altogether.

## Result

| Quantity | Value |
| --- | --- |
| Power at a {TARGET}-nat effect | **{power * 100:.1f}%** (MC SE ±{se * 100:.1f}pp) |
| Rejection rate under the null (centred residuals, no imposed effect) | {type_one * 100:.1f}% (nominally 5%) |
| Simulated null mean | {null_mean:+.5f} (should be ~0) |
| Effect at 80% power | {threshold:.4f} nats (±{bracket:.4f} bracket) |
| Independent runs, seeds {SEED + 31} and {SEED + 62} | {stability[0] * 100:.1f}%, {stability[1] * 100:.1f}% |
| Decision rule | adequate if power reaches 80% |

**Verdict: {'ADEQUATE' if power >= 0.80 else 'NOT ADEQUATE'}** at this spread — one model's.

This is the third number this document has carried, and the sequence matters. It was 84%
when the sizing used an estimated variance component, 93.5% when the decomposition was
removed but the pilot mean was not centred, and 66.6% once the centring was fixed. The 93.5%
was not power at all — it was the model's existing disadvantage to the market, detected by a
two-sided test. The current figure is the only one that tests the stated effect.

## What this does not show

- **Not an effect.** The {TARGET}-nat shift is imposed, not measured. This says the design
  could detect such an effect if it existed; it says nothing about whether it does.
- **One model's spread.** These are the Δ values of a model that is worse than the market.
  A competitive model would likely have smaller variance, making this estimate
  conservative; a differently-shaped one would not necessarily.
- **The type-I figure is a check, not a result.** At zero effect the test should reject
  about 5% of the time; a figure far from that would mean the simulated test is miscalibrated.
"""
    OUT.write_text(doc, encoding="utf-8")

    print(f"clusters={len(clusters)} power={power:.3f} se={se:.3f} type_one={type_one:.3f}")
    print(f"stability={[round(x, 3) for x in stability]}")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
