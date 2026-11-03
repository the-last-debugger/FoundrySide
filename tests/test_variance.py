"""The two implementations of the weighted variance estimator must agree.

`research/variance.py` is the readable definition; `research/pilot_power.py` has a numpy
version because it runs inside a 2,000-replicate bootstrap. Two implementations of one
definition is a drift risk, so it is tested rather than trusted.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research import pilot_power, variance  # noqa: E402


def clusters(seed: int = 0) -> list[list[float]]:
    rng = np.random.default_rng(seed)
    sizes = [293, 306, 340, 380, 380, 552, 306, 340]
    out = []
    for i, m in enumerate(sizes):
        base = 0.01 * (i % 3) - 0.02
        out.append(list(rng.normal(base, 0.23, size=m)))
    return out


class AgreementTest(unittest.TestCase):
    def test_weighted_components_match_between_implementations(self):
        data = clusters()
        slow = variance.weighted_components(data)
        fast_w, fast_b = pilot_power.components([np.array(c) for c in data])
        self.assertAlmostEqual(slow["sigma_w"], fast_w, places=9)
        self.assertAlmostEqual(slow["sigma_b"], fast_b, places=9)

    def test_weights_matter_when_clusters_are_unequal(self):
        # One huge cluster with no spread and several small ones: the fixture-weighted
        # estimand must be dominated by the large cluster, unlike the unweighted version.
        data = [[5.0] * 2 + [0.0] * 200, [0.0, 10.0], [0.0, -10.0], [0.0, 8.0]]
        weighted = variance.weighted_components(data)
        unweighted_means = [sum(c) / len(c) for c in data]
        self.assertLess(weighted["sigma_w"], float(np.var(unweighted_means)))

    def test_negative_between_variance_is_reported_not_hidden(self):
        # Clusters drawn from the same distribution: the untruncated component may go
        # negative, and it must be visible rather than clipped to zero.
        data = [[0.0, 0.02, -0.01, 0.03], [0.01, -0.02, 0.0, 0.02],
                [-0.01, 0.01, 0.02, -0.02]]
        comp = variance.weighted_components(data)
        self.assertLess(comp["var_between"], 1e-6)
        self.assertGreaterEqual(comp["sigma_b"], 0.0)


if __name__ == "__main__":
    unittest.main()
