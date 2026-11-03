"""Cluster-level quantities for the fixture-weighted estimand.

An earlier version decomposed the variance into `σ_w` and `σ_b` and used both to size the
confirmatory design. Review was right that the decomposition was not justified for unequal
clusters: applying an equal-cluster `K/(K−1)` correction to a weighted dispersion is not
generally unbiased when the weights differ, and two implementations agreeing only proved
they shared the same formula.

The decomposition is therefore **not used for sizing**. What is used is the design-based
variance of the fixture-weighted mean, which needs no components:

    V̂ = (K/(K−1)) · Σ w_k² (mean_k − mean)²,    w_k = m_k / n

That is the linearised cluster-robust variance, it respects the actual cluster sizes, and
it is the same quantity the confirmatory test divides by. Sizing now resamples real pilot
clusters rather than drawing from an assumed normal model, so no component has to be
estimated at all. `sigma_w` is still reported, as a descriptive within-cluster spread.
"""

from __future__ import annotations

import math
import random
import statistics


def weighted_mean(clusters: list[list[float]]) -> float:
    sizes = [len(c) for c in clusters]
    n = sum(sizes)
    return sum((m / n) * statistics.mean(c) for c, m in zip(clusters, sizes))


def sigma_w(clusters: list[list[float]]) -> float:
    """Weighted within-cluster SD. Descriptive; not used for sizing."""
    sizes = [len(c) for c in clusters]
    n = sum(sizes)
    var = sum((m / n) * statistics.variance(c) for c, m in zip(clusters, sizes) if len(c) > 1)
    return math.sqrt(max(var, 0.0))


def cluster_robust_var(clusters: list[list[float]]) -> float:
    """Variance of the fixture-weighted mean, cluster-robust and size-aware."""
    usable = [c for c in clusters if len(c) > 1]
    k = len(usable)
    if k < 2:
        return float("nan")
    sizes = [len(c) for c in usable]
    n = sum(sizes)
    w = [m / n for m in sizes]
    means = [statistics.mean(c) for c in usable]
    grand = sum(w_k * m_k for w_k, m_k in zip(w, means))
    return (k / (k - 1)) * sum(w_k ** 2 * (m_k - grand) ** 2
                              for w_k, m_k in zip(w, means))


def bootstrap_var(clusters: list[list[float]], replicates: int = 2000,
                  seed: int = 20261103) -> tuple[float, float]:
    """Percentile interval for the cluster-robust variance, resampling clusters."""
    rng = random.Random(seed)
    k = len(clusters)
    draws = []
    for _ in range(replicates):
        pick = [clusters[rng.randrange(k)] for _ in range(k)]
        draws.append(cluster_robust_var(pick))
    draws = [d for d in draws if math.isfinite(d)]
    if not draws:
        return (float("nan"), float("nan"))
    draws.sort()
    return (draws[int(0.025 * len(draws))], draws[int(0.975 * len(draws)) - 1])
