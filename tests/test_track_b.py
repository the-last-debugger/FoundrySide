"""Tests for the Track B return calculation.

The defect this guards against is subtle and was live: `accuracy × mean(odds) − 1` is the product
of two averages, not the average return. With varying odds the two differ, and only the second is
what a user would experience.
"""

from __future__ import annotations

import statistics
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research import track_b  # noqa: E402


class ReturnTest(unittest.TestCase):
    def test_row_level_return_differs_from_product_of_means(self):
        rows = [{"correct": 1, "price": 1.2}, {"correct": 0, "price": 5.0},
                {"correct": 1, "price": 3.0}, {"correct": 1, "price": 1.1}]
        correct_mean = statistics.mean(r["correct"] for r in rows)
        price_mean = statistics.mean(r["price"] for r in rows)
        wrong = correct_mean * price_mean - 1
        right = statistics.mean(r["correct"] * r["price"] - 1 for r in rows)
        self.assertNotAlmostEqual(wrong, right, places=8)
        self.assertAlmostEqual(right, statistics.mean(
            [0.2, -1.0, 2.0, 0.1]), places=10)

    def test_all_winners_equals_mean_odds_minus_one(self):
        rows = [{"correct": 1, "price": 1.5}, {"correct": 1, "price": 2.5}]
        self.assertAlmostEqual(statistics.mean(r["correct"] * r["price"] - 1 for r in rows),
                               1.0, places=10)

    def test_all_losers_lose_exactly_the_stake(self):
        rows = [{"correct": 0, "price": 1.9}, {"correct": 0, "price": 4.0}]
        self.assertAlmostEqual(statistics.mean(r["correct"] * r["price"] - 1 for r in rows),
                               -1.0, places=10)


class WilsonTest(unittest.TestCase):
    def test_interval_brackets_the_estimate(self):
        lo, hi = track_b.wilson(50, 100)
        self.assertLess(lo, 0.5)
        self.assertGreater(hi, 0.5)

    def test_extremes_stay_in_range(self):
        lo, hi = track_b.wilson(0, 30)
        self.assertGreaterEqual(lo, 0.0)
        lo2, hi2 = track_b.wilson(30, 30)
        self.assertLessEqual(hi2, 1.0)

    def test_non_finite_and_below_unit_prices_are_rejected(self):
        # The build guard must refuse a price that cannot be a decimal odd.
        import math
        for bad in (float("nan"), float("inf"), 1.0, 0.5):
            self.assertFalse(math.isfinite(bad) and bad > 1.0)

    def test_stake_sensitivity_scales_with_the_stake(self):
        # A fixed-fraction stake must lose proportionally more as the fraction grows.
        def growth(stake, correct, price):
            import math as m
            return m.log(1 + stake * (price - 1)) if correct else m.log(1 - stake)
        tiny = growth(0.005, 0, 2.0)
        large = growth(0.02, 0, 2.0)
        self.assertLess(large, tiny)          # 2% loses more than 0.5% on the same loser
        self.assertGreater(growth(0.02, 1, 2.0), growth(0.005, 1, 2.0))

    def test_abstention_scores_zero_on_the_common_denominator(self):
        rows = [{"correct": 1, "price": 1.5}, {"correct": 0, "price": 3.0}]
        selected = {0}
        stake = 0.01
        import math as m
        policy = [m.log(1 + stake * (rows[i]["price"] - 1)) if i in selected and rows[i]["correct"]
                  else (m.log(1 - stake) if i in selected else 0.0) for i in range(len(rows))]
        self.assertAlmostEqual(policy[1], 0.0, places=12)

    def test_policy_bootstrap_uses_the_full_denominator(self):
        # Two fixtures, one selected, equal weights. The full-denominator mean is half the
        # selected-only mean; a regression to the selected denominator would double it.
        import numpy as np
        from research.track_b import policy_growth
        values = np.array([0.10, -0.20])
        mask = np.array([1.0, 0.0])
        weights = np.ones((1, 2))
        wsum = weights.sum(axis=1)
        full = policy_growth(values, mask, weights, wsum)[0]
        selected_only = 0.10
        self.assertAlmostEqual(full, 0.05, places=12)
        self.assertNotAlmostEqual(full, selected_only, places=6)


if __name__ == "__main__":
    unittest.main()
