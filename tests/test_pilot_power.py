"""Tests for the resampling-based design sizing.

There is no variance-component formula any more: power comes from resampling real clusters
and running the actual test. These tests check that the simulation behaves like a test.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research import pilot_power  # noqa: E402


def clusters(shift: float = 0.0, seed: int = 3) -> list[np.ndarray]:
    rng = np.random.default_rng(seed)
    out = []
    for i in range(8):
        centre = shift + (0.01 if i % 2 else -0.01)
        out.append(rng.normal(centre, 0.20, size=300))
    return out


SIZES = np.array([300.0] * 8)


class DesignPowerTest(unittest.TestCase):
    def test_rejects_almost_always_for_a_large_effect(self):
        power = pilot_power.design_power(clusters(), SIZES, 0.10, sims=200)
        self.assertGreater(power, 0.95)

    def test_rejects_about_five_percent_at_a_true_null(self):
        # Centre the clusters, then test at zero: this is the calibration check.
        data = clusters()
        mean = float(sum(c.mean() for c in data) / len(data))
        power = pilot_power.design_power(data, SIZES, -mean, sims=400)
        self.assertLess(power, 0.12)
        self.assertGreater(power, 0.01)

    def test_power_increases_with_the_effect(self):
        data = clusters()
        small = pilot_power.design_power(data, SIZES, 0.005, sims=200)
        large = pilot_power.design_power(data, SIZES, 0.03, sims=200)
        self.assertGreater(large, small)

    def test_same_seed_is_reproducible(self):
        data = clusters()
        a = pilot_power.design_power(data, SIZES, 0.02, sims=100, seed=7)
        b = pilot_power.design_power(data, SIZES, 0.02, sims=100, seed=7)
        self.assertEqual(a, b)

    def test_different_seeds_differ_slightly(self):
        data = clusters()
        a = pilot_power.design_power(data, SIZES, 0.02, sims=100, seed=7)
        b = pilot_power.design_power(data, SIZES, 0.02, sims=100, seed=8)
        self.assertAlmostEqual(a, b, delta=0.15)


if __name__ == "__main__":
    unittest.main()
