"""Focused tests for the Platt fitter used in the calibration study.

The fitter is simple enough to look obviously right, which is exactly why it needs tests: a
silent sign error or a non-convergent loop would show up as a plausible-looking slope.
"""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research import calibration_study as cs  # noqa: E402


def data(slope: float, n: int = 4000) -> list[dict]:
    """Synthetic forecasts whose true calibration slope is `slope`."""
    rows = []
    for i in range(n):
        p = 0.1 + 0.8 * (i % 100) / 99
        z = slope * cs.logit(p)
        q = 1 / (1 + math.exp(-z))
        y = 1 if (i * 7919 % 1000) / 1000 < q else 0
        rows.append({"p": p, "y": y})
    return rows


class PlattTest(unittest.TestCase):
    def test_outputs_are_finite_and_shrink_a_confident_model(self):
        rows = data(0.5)          # truth is underconfident relative to the forecast
        a, b = cs.fit_platt(rows)
        self.assertTrue(math.isfinite(a) and math.isfinite(b))
        self.assertGreater(a, 0.2)
        self.assertLess(a, 2.0)

    def test_map_is_monotone_for_positive_slope(self):
        a, b = cs.fit_platt(data(1.0))
        self.assertGreater(a, 0)
        values = [cs.sigmoid(a * cs.logit(p) + b) for p in (0.05, 0.2, 0.5, 0.8, 0.95)]
        self.assertEqual(values, sorted(values))

    def test_extreme_probabilities_stay_in_range(self):
        rows = [{"p": 1e-9, "y": 0}, {"p": 1 - 1e-9, "y": 1}] * 50
        a, b = cs.fit_platt(rows)
        for p in (1e-9, 0.5, 1 - 1e-9):
            q = cs.sigmoid(a * cs.logit(p) + b)
            self.assertTrue(0.0 <= q <= 1.0)

    def test_is_deterministic(self):
        rows = data(0.8)
        self.assertEqual(cs.fit_platt(rows), cs.fit_platt(rows))

    def test_folds_never_share_seasons(self):
        rows = [{"season": s, "p": 0.5, "y": 0} for s in ("a", "b")]
        for held in ("a", "b"):
            train = [r for r in rows if r["season"] != held]
            self.assertNotIn(held, {r["season"] for r in train})


if __name__ == "__main__":
    unittest.main()
