"""Tests for the primitives the feature screen depends on.

A wrong AUC or a non-convergent logistic fit would make every verdict in the screen meaningless,
and both are easy to get subtly wrong — rank computation with ties, or a Newton loop that stops
before the optimum.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research import feature_screen as fs  # noqa: E402


def slow_auc(p: np.ndarray, y: np.ndarray) -> float:
    pos = p[y == 1]
    neg = p[y == 0]
    wins = 0.0
    for a in pos:
        for b in neg:
            wins += 1.0 if a > b else 0.5 if a == b else 0.0
    return wins / (len(pos) * len(neg))


class AucTest(unittest.TestCase):
    def test_matches_the_definition(self):
        rng = np.random.default_rng(0)
        for _ in range(5):
            n = 200
            y = (rng.random(n) < 0.4).astype(float)
            p = np.clip(0.2 + 0.5 * y + rng.normal(0, 0.15, n), 0.01, 0.99)
            self.assertAlmostEqual(fs.fast_auc(p, y), slow_auc(p, y), places=10)

    def test_ties_count_half(self):
        p = np.array([0.5, 0.5, 0.5, 0.5])
        y = np.array([1.0, 1.0, 0.0, 0.0])
        self.assertAlmostEqual(fs.fast_auc(p, y), 0.5, places=12)

    def test_perfect_and_inverted(self):
        y = np.array([1.0, 1.0, 0.0, 0.0])
        self.assertAlmostEqual(fs.fast_auc(np.array([0.9, 0.8, 0.2, 0.1]), y), 1.0)
        self.assertAlmostEqual(fs.fast_auc(np.array([0.1, 0.2, 0.8, 0.9]), y), 0.0)


class LogisticTest(unittest.TestCase):
    def test_recovers_a_known_slope(self):
        rng = np.random.default_rng(1)
        x = rng.normal(0, 1, 4000)
        z = 0.8 * x - 0.2
        y = (rng.random(4000) < 1 / (1 + np.exp(-z))).astype(float)
        beta = fs.fit_logistic(np.column_stack([np.ones_like(x), x]), y)
        self.assertAlmostEqual(beta[1], 0.8, delta=0.12)
        self.assertAlmostEqual(beta[0], -0.2, delta=0.12)

    def test_predictions_stay_in_range(self):
        rng = np.random.default_rng(2)
        X = np.column_stack([np.ones(100), rng.normal(0, 5, 100)])
        y = (rng.random(100) < 0.5).astype(float)
        p = fs.predict(X, fs.fit_logistic(X, y))
        self.assertTrue(np.all((p >= 0) & (p <= 1)))


class LogLossTest(unittest.TestCase):
    def test_near_zero_for_perfect_certainty(self):
        # Predictions are clipped at 1e-6, so "perfect" costs about 1e-6 nats, not zero.
        self.assertLess(fs.logloss_vec(np.array([1.0, 0.0]), np.array([1.0, 0.0])), 1e-5)

    def test_symmetric_in_the_outcome(self):
        a = fs.logloss_vec(np.array([0.7]), np.array([1.0]))
        b = fs.logloss_vec(np.array([0.3]), np.array([0.0]))
        self.assertAlmostEqual(a, b, places=12)


if __name__ == "__main__":
    unittest.main()
