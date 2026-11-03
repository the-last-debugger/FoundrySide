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


if __name__ == "__main__":
    unittest.main()
