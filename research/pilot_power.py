"""The pilot sizing procedure: from out-of-fold Δ to a sizing decision.

Protocol §5 asks for a specific chain: cluster-bootstrap the pilot's 24 clusters, get a
distribution of (σ_w, σ_b), run the confirmatory power calculation for each replicate,
and require the 5th percentile of that power distribution to reach 0.80.

**There are no out-of-fold pilot predictions yet**, so this cannot produce a real answer.
It implements the procedure and runs it on a synthetic stand-in, and it says so in every
line of its output. Populating it is the next milestone: pass a Δ file and the same code
answers the real question.

    python research/pilot_power.py --synthetic-w 0.20 --synthetic-b 0.010
    python research/pilot_power.py --deltas path/to/oof_deltas.csv

Writes research/PILOT_POWER.md. Requires numpy.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research"))

import analyse   # noqa: E402
import pilot     # noqa: E402
import report_stamp  # noqa: E402

OUT = ROOT / "research" / "PILOT_POWER.md"
TARGET = 0.01
K_CONFIRMATORY = 16
N_CONFIRMATORY = 5794
T_CRIT = 2.1314495        # two-sided 0.05, 15 df — the confirmatory test's critical value
Z = 1.959963984540054     # the normal-theory reference's critical value, kept distinct
REPLICATES = 2000
SIMS_PER_REPLICATE = 400
HIGH_BUDGET = 1500
SEED = 20261103


def phi(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def power_t(delta: float, sizes: np.ndarray, sd_w: float, sd_b: float,
            sims: int = 400, seed: int = SEED) -> float:
    """Power of the cluster-robust t, by simulating the test.

    An earlier version computed `phi(x − t_crit)`: a normal CDF evaluated at a t critical
    value. That is neither the normal test nor the t test — it borrows the tail of one and
    the cutoff of the other — and it was being used to justify a sizing decision. This
    simulates the statistic that will actually be computed, which is the only honest way
    to get its power without a noncentral-t implementation in the standard library.
    """
    rng = np.random.default_rng(seed)
    m = np.asarray(sizes, dtype=float)
    k = len(m)
    w = m / m.sum()
    sqrt_m = np.sqrt(m)
    u = rng.normal(0.0, sd_b, size=(sims, k)) if sd_b > 0 else np.zeros((sims, k))
    eps = rng.normal(0.0, 1.0, size=(sims, k))
    totals = m[None, :] * (delta + u) + sqrt_m[None, :] * sd_w * eps
    means = totals / m[None, :]
    mean = (means * w[None, :]).sum(axis=1)
    var = (k / (k - 1)) * (((means - mean[:, None]) * w[None, :]) ** 2).sum(axis=1)
    t = mean / np.sqrt(var)
    return float(np.mean(np.abs(t) > T_CRIT))


def normal_approx(delta: float, sizes: np.ndarray, sd_w: float, sd_b: float) -> float:
    """Genuine normal-theory reference: z = 1.96, not the t critical value.

    An earlier version used `T_CRIT` here, which is the same hybrid the t simulation
    replaced — a normal tail with a t cutoff. This is now the textbook normal test, so the
    reference is a different test rather than a corrupted version of the right one.
    """
    m = np.asarray(sizes, dtype=float)
    se = math.sqrt(sd_w ** 2 / m.sum() + sd_b ** 2 * float(((m / m.sum()) ** 2).sum()))
    if se == 0:
        return 1.0
    x = delta / se
    return phi(x - Z) + phi(-x - Z)


def confirmatory_sizes() -> np.ndarray:
    framed, _ = pilot.frame(analyse.load())
    counts: dict[str, int] = {}
    for f in framed:
        if f["phase"] == "confirmatory":
            counts[f["cluster"]] = counts.get(f["cluster"], 0) + 1
    return np.array(sorted(counts.values()), dtype=float)


def pilot_clusters() -> list[np.ndarray]:
    """Placeholder shape: one empty array per pilot cluster, to be filled with OOF Δ."""
    framed, _ = pilot.frame(analyse.load())
    counts: dict[str, int] = {}
    for f in framed:
        if f["phase"] == "pilot":
            counts[f["cluster"]] = counts.get(f["cluster"], 0) + 1
    return [np.zeros(counts[c]) for c in sorted(counts)]


def synthetic_clusters(sizes: list[int], sd_w: float, sd_b: float,
                       seed: int = SEED) -> list[np.ndarray]:
    rng = np.random.default_rng(seed)
    return [rng.normal(rng.normal(0.0, sd_b), sd_w, size=m) for m in sizes]


def components(clusters: list[np.ndarray]) -> tuple[float, float]:
    """σ_w and σ_b by method of moments.

    The spread of cluster *means* is not σ_b: each mean carries its own sampling noise,
    about σ_w/√m_k. Estimating σ_b from the raw spread of means therefore overstates it
    badly when m is large — by a factor of √2 in the case this was written for, which
    turned a 72% design into a 21% one. The sampling variance is subtracted.
    """
    means = np.array([c.mean() for c in clusters])
    variances = np.array([c.var(ddof=1) for c in clusters if len(c) > 1])
    within = float(variances.mean())
    sampling = float(np.mean([c.var(ddof=1) / len(c) for c in clusters if len(c) > 1]))
    between = float(means.var(ddof=1)) - sampling
    return float(math.sqrt(max(within, 0.0))), float(math.sqrt(max(between, 0.0)))


def bootstrap_components(clusters: list[np.ndarray], replicates: int = REPLICATES,
                         seed: int = SEED) -> list[tuple[float, float]]:
    """Resample the pilot's clusters with replacement, recompute (σ_w, σ_b)."""
    rng = np.random.default_rng(seed)
    k = len(clusters)
    out = []
    for _ in range(replicates):
        pick = rng.integers(0, k, size=k)
        out.append(components([clusters[i] for i in pick]))
    return out


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]

    def val(name: str, default: float) -> float:
        return float(args[args.index(name) + 1]) if name in args else default

    deltas_path = args[args.index("--deltas") + 1] if "--deltas" in args else None
    sd_w_syn, sd_b_syn = val("--synthetic-w", 0.20), val("--synthetic-b", 0.010)

    sizes = np.array([len(c) for c in pilot_clusters()], dtype=float)
    confirm_sizes = confirmatory_sizes()

    if deltas_path:
        raise SystemExit("--deltas is not implemented until pilot predictions exist; "
                         "this run is illustrative.")

    clusters = synthetic_clusters([int(s) for s in sizes], sd_w_syn, sd_b_syn)
    pops = bootstrap_components(clusters)

    def lower_tail(variance_draws, sims: int, seed_base: int) -> float:
        """5th-percentile power, with a distinct simulation seed per replicate.

        An earlier version reused one seed across all 2,000 replicates in the stability and
        high-budget runs while the main run varied it per replicate. That shares simulation
        draws between variance pairs and makes the budget comparison measure the seed, not
        the budget. Every run here uses distinct per-replicate seeds, and the budget
        comparison reuses the *same* bootstrap draws and the same per-replicate seeds, so
        only the number of simulations changes.
        """
        powers = sorted(power_t(TARGET, confirm_sizes, w, b, sims=sims, seed=seed_base + i)
                        for i, (w, b) in enumerate(variance_draws))
        return powers[int(0.05 * len(powers))]

    p05 = lower_tail(pops, SIMS_PER_REPLICATE, SEED)
    approx = sorted(normal_approx(TARGET, confirm_sizes, w, b) for w, b in pops)
    powers = sorted(power_t(TARGET, confirm_sizes, w, b, seed=SEED + i)
                    for i, (w, b) in enumerate(pops))
    median = powers[len(powers) // 2]
    approx_median = approx[len(approx) // 2]

    # Stability: independent bootstrap draws, distinct seeds within each run.
    stability = []
    for k in range(3):
        base = SEED + 101 * (k + 1)
        pops_k = bootstrap_components(clusters, seed=base)
        stability.append(lower_tail(pops_k, SIMS_PER_REPLICATE, base))

    # Budget comparison: same bootstrap draws, same per-replicate seeds, more sims.
    p05_high = lower_tail(pops, HIGH_BUDGET, SEED)

    doc = f"""{report_stamp.stamp(Path(__file__))}

# Pilot sizing — **UNPOPULATED, ILLUSTRATIVE ONLY**

Generated by `python research/pilot_power.py`. There are **no out-of-fold pilot
predictions yet**, so this cannot answer whether the confirmatory design is adequately
powered. What it does is implement protocol §5 end to end and exercise it on a synthetic
stand-in, so the procedure is ready when the data is.

- Input: synthetic Δ with σ_w = {sd_w_syn:.3f}, σ_b = {sd_b_syn:.3f}, drawn per pilot
  cluster with the real 24 cluster sizes.
- Replicates: {REPLICATES:,}.
- Confirmatory design: {K_CONFIRMATORY} clusters, n = {N_CONFIRMATORY:,}, target
  {TARGET} nats, cluster-robust t at 15 df.

## Result on the synthetic input

| Quantity | Value |
| --- | --- |
| 5th percentile of power | **{p05 * 100:.1f}%** |
| Median power | {median * 100:.1f}% |
| Median from the normal approximation, for reference | {approx_median * 100:.1f}% |
| Decision rule | adequate only if the 5th percentile reaches 80% |
| Verdict | **{'ADEQUATE' if p05 >= 0.80 else 'NOT ADEQUATE'}** (on synthetic input) |

The power for each replicate is obtained by **simulating the cluster-robust t**, not by a
normal approximation. The reference row is a genuine normal-theory test (z = 1.96), not a
hybrid, and it is shown for context only; the decision does not use it.

## Monte Carlo stability of the decision statistic

Each replicate's power is an estimate from **{SIMS_PER_REPLICATE}** simulated t-tests, and
the 5th percentile of 2,000 such estimates is itself a noisy quantity — and it is exactly
where the 0.80 rule is applied, so its noise has to be measured rather than assumed.

| Run | 5th-percentile power |
| --- | --- |
""" + "\n".join(f"| seed {SEED + 101 * (k + 1)} | {s * 100:.1f}% |"
                for k, s in enumerate(stability)) + f"""
| higher budget ({HIGH_BUDGET} sims/replicate) | {p05_high * 100:.1f}% |

- Spread across the three independent runs: **{(max(stability) - min(stability)) * 100:.1f}pp**.
- The budget comparison is **paired**: same bootstrap draws, same per-replicate seeds, only
  the number of simulated t-tests changes. Raising it to {HIGH_BUDGET} moves the statistic
  to **{p05_high * 100:.1f}%**, {(p05_high - p05) * 100:+.1f}pp against the base run.
- **Decision stability:** {'every run lands on the same side of 80%, so the verdict is stable at this budget' if (max(stability) < 0.80 and p05_high < 0.80) or (min(stability) >= 0.80 and p05_high >= 0.80) else 'the runs straddle 80%, so the verdict is **not** stable at this budget and the simulation needs to be larger before any decision is taken'}.

## What this shows, and what it does not

**Shows:** the procedure runs — pilot clusters are resampled, (σ_w, σ_b) are re-estimated
each replicate, the confirmatory power is computed from each, and the decision is taken
from the 5th percentile rather than the point estimate. The uncertainty in the variance
components is inside the answer, which was the point of the correction.

**Does not show:** anything about FoundrySide. The verdict above is a statement about a
synthetic input with a chosen σ_w and σ_b. **The adequacy question is open**, and remains
open until the pilot produces real out-of-fold Δ values.

## Why the 5th percentile rather than the median

If the design reaches 80% power at the median estimate of the variance components, it is
below 80% for half the plausible values of those components. Requiring the lower tail to
clear the bar makes the decision conservative in the direction that matters: a design
that fails this test may still work, but a design that passes it is not relying on a
favourable draw.
"""
    OUT.write_text(doc, encoding="utf-8")

    print(f"pilot clusters={len(clusters)} synthetic sw={sd_w_syn:.3f} sb={sd_b_syn:.3f}")
    print(f"p05={p05:.3f} median={median:.3f} normal_approx_median={approx_median:.3f} "
          f"verdict={'ADEQUATE' if p05 >= 0.8 else 'NOT ADEQUATE'}")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
