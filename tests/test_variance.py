"""Tests for the cluster-level variance used in sizing.

The decomposition into within- and between-cluster components was removed after review:
the unequal-weight estimator was not defensible. What remains is the cluster-robust
variance of the fixture-weighted mean, which is what the confirmatory test divides by.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research import variance  # noqa: E402


class ClusterVarianceTest(unittest.TestCase):
    def test_matches_the_hand_computation_for_equal_clusters(self):
        # Four clusters, two values each: means 0.5 and 1.5 alternating.
        clusters = [[0.0, 1.0], [1.0, 2.0], [0.0, 1.0], [1.0, 2.0]]
        w = [0.25] * 4
        means = [0.5, 1.5, 0.5, 1.5]
        grand = 1.0
        expected = (4 / 3) * sum(wk ** 2 * (m - grand) ** 2 for wk, m in zip(w, means))
        self.assertAlmostEqual(variance.cluster_robust_var(clusters), expected, places=12)

    def test_weights_favour_the_large_cluster(self):
        # A large cluster with no spread should dominate the weighted within-SD: the
        # fixture-weighted value must sit far below the unweighted average of the three
        # cluster variances.
        clusters = [[1.0] * 400, [0.0, 2.0], [0.0, 2.0]]
        weighted = variance.sigma_w(clusters)
        unweighted = float(sum(variance.sigma_w([c]) for c in clusters) / 3)
        self.assertLess(weighted, unweighted)
        self.assertLess(weighted, 0.2)

    def test_variance_shrinks_as_clusters_agree(self):
        agreeing = [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]
        disagreeing = [[0.0, 0.0, 0.0], [1.0, 1.0, 1.0], [2.0, 2.0, 2.0]]
        self.assertLess(variance.cluster_robust_var(agreeing),
                        variance.cluster_robust_var(disagreeing))

    def test_bootstrap_interval_brackets_the_point_estimate(self):
        clusters = [[0.0, 0.1, -0.1], [0.02, 0.03, 0.01], [-0.05, 0.0, 0.05],
                    [0.1, 0.12, 0.08]]
        point = variance.cluster_robust_var(clusters)
        lo, hi = variance.bootstrap_var(clusters, replicates=300)
        self.assertLessEqual(lo, point * 3 + 1e-12)
        self.assertGreaterEqual(hi, point / 3 - 1e-12)

    def test_too_few_clusters_is_not_a_number(self):
        self.assertTrue(variance.cluster_robust_var([[1.0, 2.0]]) != variance.cluster_robust_var([[1.0, 2.0]]))


if __name__ == "__main__":
    unittest.main()
