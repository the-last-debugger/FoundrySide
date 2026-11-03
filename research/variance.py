"""Variance components for the fixture-weighted estimand, with unequal clusters.

The confirmatory estimand is the fixture-weighted mean Δ: every fixture counts equally, so
a large division-season carries more weight than a small one. An earlier version of the
pilot reported components from an *unweighted* mean of cluster variances and an unweighted
variance of cluster means, which is the equal-cluster-size estimator. With clusters
running 293–552 fixtures that is not the estimand's variance.

Definitions used here, with `w_k = m_k / n`:

    mean        = Σ w_k · mean_k
    σ²_w        = Σ w_k · var_k                       (weighted within-cluster)
    B           = (K/(K−1)) · Σ w_k² (mean_k − mean)²   (between part of Var(mean))
    σ²_b        = (B − Σ w_k² · var_k / m_k) / Σ w_k²  (removes sampling noise)

Dividing by `Σ w_k²` — not by the cluster count — is what makes this correct for unequal
clusters; with equal weights it reduces to `K · B`.

`σ²_b` can come out **negative** — that is what a boundary estimate looks like before it is
truncated, and it means the data are consistent with no between-cluster variation at all.
Truncating to zero and calling the component "measured" would overstate what the sample
supports, so the untruncated value is returned alongside the truncated one.
"""

from __future__ import annotations

import math
import statistics


def weighted_components(clusters: list[list[float]]) -> dict[str, float]:
    """Components for the fixture-weighted mean, from per-cluster Δ samples."""
    usable = [c for c in clusters if len(c) > 1]
    k = len(usable)
    if k < 2:
        return {"k": float(k), "mean": float("nan"), "sigma_w": float("nan"),
                "var_between": float("nan"), "sigma_b": float("nan"),
                "boundary": 1.0}

    sizes = [len(c) for c in usable]
    n = sum(sizes)
    w = [m / n for m in sizes]
    means = [statistics.mean(c) for c in usable]
    variances = [statistics.variance(c) for c in usable]

    grand = sum(w_k * m_k for w_k, m_k in zip(w, means))
    sigma2_w = sum(w_k * v for w_k, v in zip(w, variances))
    # The between part of Var(mean) is B = Σ w_k² (μ_k − μ)². Under the model
    # μ_k ~ (μ, σ_b²) that equals σ_b² · Σ w_k², so σ_b² = B / Σ w_k². Dividing by the
    # sum of squared weights — rather than by the cluster count — is what makes this
    # correct for unequal clusters; with equal weights it reduces to K · B.
    var_mean_between = ((k / (k - 1)) * sum(w_k ** 2 * (m_k - grand) ** 2
                                            for w_k, m_k in zip(w, means)))
    sampling = sum(w_k ** 2 * v / m for w_k, v, m in zip(w, variances, sizes))
    sum_w2 = sum(w_k ** 2 for w_k in w)
    raw = (var_mean_between - sampling) / sum_w2

    return {
        "k": float(k),
        "n": float(n),
        "mean": grand,
        "sigma_w": math.sqrt(max(sigma2_w, 0.0)),
        "var_between": raw,
        "sigma_b": math.sqrt(max(raw, 0.0)),
        "boundary": 1.0 if raw <= 0 else 0.0,
    }


def bootstrap_between(clusters: list[list[float]], replicates: int = 2000,
                      seed: int = 20261103) -> tuple[float, float]:
    """Percentile interval for the between-cluster variance component.

    The point estimate can sit at or below zero; an interval is the only honest way to say
    how far below the data allow it to be.
    """
    import random

    rng = random.Random(seed)
    k = len(clusters)
    draws = []
    for _ in range(replicates):
        pick = [clusters[rng.randrange(k)] for _ in range(k)]
        draws.append(weighted_components(pick)["var_between"])
    draws = [d for d in draws if math.isfinite(d)]
    if not draws:
        return (float("nan"), float("nan"))
    draws.sort()
    return (draws[int(0.025 * len(draws))], draws[int(0.975 * len(draws)) - 1])
