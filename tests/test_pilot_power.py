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


class CentringTest(unittest.TestCase):
    """The simulation must test the imposed effect, not the pilot's existing mean."""

    def test_power_is_invariant_to_a_common_offset(self):
        # Adding a constant to every pilot Δ must not change power: the centring step
        # removes it, so the same seed gives the same answer exactly.
        base = clusters()
        shifted = [c + 7.0 for c in base]
        a = pilot_power.design_power(base, SIZES, 0.02, sims=150, seed=11)
        b = pilot_power.design_power(shifted, SIZES, 0.02, sims=150, seed=11)
        self.assertEqual(a, b)

    def test_effect_direction_is_symmetric(self):
        # A two-sided test: +d and −d of the same size should have similar power.
        data = clusters()
        up = pilot_power.design_power(data, SIZES, 0.02, sims=300, seed=5)
        down = pilot_power.design_power(data, SIZES, -0.02, sims=300, seed=5)
        self.assertAlmostEqual(up, down, delta=0.06)

    def test_a_deliberately_shifted_pilot_does_not_inflate_null_rejection(self):
        # A pilot sitting far from zero must still reject at about 5% under the null.
        data = [c - 0.5 for c in clusters()]
        null = pilot_power.design_power(data, SIZES, 0.0, sims=400, seed=9)
        self.assertLess(null, 0.12)


class EstimandTest(unittest.TestCase):
    """Resampling must target the fixture-weighted mean, not the unweighted mean of means."""

    def test_null_is_centred_when_means_are_associated_with_size(self):
        rng = np.random.default_rng(5)
        sizes = [400, 300, 250, 200, 150, 100, 80, 60]
        means = [0.06, 0.04, 0.02, 0.005, -0.01, -0.03, -0.04, -0.05]
        clusters = [rng.normal(m, 0.18, size=s) for m, s in zip(means, sizes)]
        null_mean = pilot_power.simulated_mean(clusters, SIZES, 0.0, sims=500)
        self.assertLess(abs(null_mean), 0.012)

    def test_the_two_estimands_differ_for_this_data(self):
        # Documents why the sampling scheme matters: the unweighted mean of cluster means
        # is materially different from the fixture-weighted mean here.
        sizes = [400, 300, 250, 200, 150, 100, 80, 60]
        means = [0.06, 0.04, 0.02, 0.005, -0.01, -0.03, -0.04, -0.05]
        weighted = sum(s * m for s, m in zip(sizes, means)) / sum(sizes)
        unweighted = sum(means) / len(means)
        self.assertGreater(abs(unweighted - weighted), 0.015)

    def test_threshold_is_reproducible(self):
        data = clusters()
        a = pilot_power.power_threshold(data, SIZES, sims=120)
        b = pilot_power.power_threshold(data, SIZES, sims=120)
        self.assertEqual(a, b)
        self.assertGreater(a[0], 0.0)


class DesignPowerTest(unittest.TestCase):
    def test_rejects_almost_always_for_a_large_effect(self):
        power = pilot_power.design_power(clusters(), SIZES, 0.10, sims=200)
        self.assertGreater(power, 0.95)

    def test_rejects_about_five_percent_at_a_true_null(self):
        # design_power centres internally, so a zero effect is a true null.
        data = clusters()
        power = pilot_power.design_power(data, SIZES, 0.0, sims=400)
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
        a = pilot_power.design_power(data, SIZES, 0.02, sims=200, seed=7)
        b = pilot_power.design_power(data, SIZES, 0.02, sims=200, seed=8)
        self.assertNotEqual(a, b)
        self.assertAlmostEqual(a, b, delta=0.2)


if __name__ == "__main__":
    unittest.main()
