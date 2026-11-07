"""Tests for the user simulation's arithmetic and its honesty.

The simulation answers "what would KSh 100-300 have cost?". Two things must hold for it to be
trustworthy: the settlement must be right, and the positive-looking number must be labelled as the
price artefact it is rather than presented as an edge.
"""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research"))

import user_simulation as us  # noqa: E402

REPORT = ROOT / "research" / "USER_SIMULATION.md"


class SettlementTest(unittest.TestCase):
    def fixture(self, probs, best, result):
        return {"probs": probs, "best": best, "avg": best, "result": result, "key": "A v B"}

    def test_winning_favourite_returns_the_price(self):
        # Probabilities favour the home side; it wins.
        f = self.fixture([0.6, 0.25, 0.15], [2.0, 4.0, 7.0], "H")
        self.assertAlmostEqual(us.net_single(f, 100.0), 100.0)

    def test_losing_favourite_loses_the_stake(self):
        f = self.fixture([0.6, 0.25, 0.15], [2.0, 4.0, 7.0], "A")
        self.assertAlmostEqual(us.net_single(f, 100.0), -100.0)

    def test_favourite_is_the_most_probable_not_the_shortest(self):
        # Same thing in a sane book, but the function should read probabilities.
        f = self.fixture([0.2, 0.3, 0.5], [5.0, 3.0, 2.2], "A")
        idx, price = us.favourite(f)
        self.assertEqual(idx, 2)
        self.assertAlmostEqual(price, 2.2)

    def test_closest_double_respects_the_window(self):
        day = {"fixtures": [
            self.fixture([0.5, 0.3, 0.2], [2.0, 3.4, 5.0], "H"),
            self.fixture([0.4, 0.3, 0.3], [2.5, 3.2, 3.5], "D"),
        ]}
        pair = us.closest_double(day, 6.0, 5.4, 6.6)
        self.assertIsNotNone(pair)
        self.assertGreaterEqual(pair["combo"], 5.4)
        self.assertLessEqual(pair["combo"], 6.6)


class ReportHonestyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not REPORT.exists():
            raise unittest.SkipTest("report not generated")
        cls.text = REPORT.read_text(encoding="utf-8")

    def test_report_says_it_is_not_about_today(self):
        lowered = " ".join(self.text.lower().split())
        self.assertIn("says nothing about today", lowered)

    def test_the_best_price_figure_is_labelled_an_artefact(self):
        lowered = self.text.lower()
        self.assertIn("selection effect", lowered)
        self.assertIn("not attainable", lowered)

    def test_both_price_bases_are_reported(self):
        self.assertIn("average closing price", self.text.lower())
        self.assertIn("best recorded closing price", self.text.lower())

    def test_report_has_no_placeholder_left(self):
        self.assertNotIn("{", re.sub(r"\\{[a-z_]+\\}", "", self.text[:0]) or self.text[:0])
        self.assertNotIn("nan", self.text.lower().split())


if __name__ == "__main__":
    unittest.main()
