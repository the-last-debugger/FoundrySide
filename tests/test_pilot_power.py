"""Tests for the pilot sizing estimator.

The first version estimated σ_b from the raw spread of cluster means and turned a 72%
design into a 21% one. These tests exist so that cannot come back: with no real
between-cluster effect the estimate must be near zero, not σ_w/√m.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research import pilot_power  # noqa: E402


class ComponentsTest(unittest.TestCase):
    def test_sampling_noise_is_not_mistaken_for_between_cluster_spread(self):
        rng = np.random.default_rng(1)
        # No cluster effect at all: every cluster is drawn from the same distribution.
        clusters = [rng.normal(0.0, 0.20, size=400) for _ in range(40)]
        sd_w, sd_b = pilot_power.components(clusters)
        self.assertAlmostEqual(sd_w, 0.20, delta=0.02)
        # Naive std of means would be ~0.20/sqrt(400) = 0.010; the corrected estimate
        # must be near zero.
        self.assertLess(sd_b, 0.004)

    def test_recovers_a_known_cluster_effect(self):
        rng = np.random.default_rng(2)
        clusters = [rng.normal(rng.normal(0.0, 0.02), 0.20, size=500) for _ in range(40)]
        sd_w, sd_b = pilot_power.components(clusters)
        self.assertAlmostEqual(sd_w, 0.20, delta=0.02)
        self.assertAlmostEqual(sd_b, 0.02, delta=0.010)

    def test_power_falls_as_between_cluster_variance_rises(self):
        sizes = np.array([300.0] * 16)
        p_low = pilot_power.power_t(0.01, sizes, 0.20, 0.0)
        p_high = pilot_power.power_t(0.01, sizes, 0.20, 0.02)
        self.assertGreater(p_low, p_high)
        self.assertGreater(p_low, 0.9)
        self.assertLess(p_high, 0.6)

    def test_power_is_simulated_not_approximated(self):
        # Different seeds must give slightly different numbers: a closed-form value would
        # be identical every time.
        sizes = np.array([300.0] * 16)
        a = pilot_power.power_t(0.01, sizes, 0.20, 0.01, sims=200, seed=1)
        b = pilot_power.power_t(0.01, sizes, 0.20, 0.01, sims=200, seed=2)
        self.assertNotEqual(a, b)
        self.assertAlmostEqual(a, b, delta=0.12)


if __name__ == "__main__":
    unittest.main()
