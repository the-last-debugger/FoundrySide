"""Tests for the stake-structure comparison in the product.

The comparison is the sponsor's question made operable: two structures matched on the same net profit.
The tests pin the arithmetic and, just as importantly, that no row can look like an opportunity.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import engine  # noqa: E402


class StructureComparisonTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = engine.compare_structures(200.0, [1.5, 2.0, 3.0, 4.0, 6.0], margin=0.05)
        cls.rows = cls.result["structures"]

    def test_every_row_targets_the_same_net(self):
        for row in self.rows:
            self.assertAlmostEqual(row["net"], 200.0, places=2)

    def test_stake_is_target_over_odds_minus_one(self):
        for row in self.rows:
            self.assertAlmostEqual(row["stake"], 200.0 / (row["odds"] - 1.0), places=2)

    def test_higher_odds_means_less_at_risk_and_lower_probability(self):
        by_odds = {row["odds"]: row for row in self.rows}
        self.assertGreater(by_odds[1.5]["stake"], by_odds[6.0]["stake"])
        self.assertGreater(by_odds[1.5]["market_implied"], by_odds[6.0]["market_implied"])

    def test_expected_loss_falls_with_odds_at_matched_net(self):
        by_odds = {row["odds"]: row for row in self.rows}
        self.assertGreater(by_odds[1.5]["expected_loss"], by_odds[6.0]["expected_loss"])

    def test_every_row_has_a_negative_expected_value(self):
        for row in self.rows:
            self.assertGreater(row["expected_loss"], 0.0,
                               "a quoted price with a margin cannot have positive EV")

    def test_variance_falls_with_odds_at_matched_net(self):
        by_odds = {row["odds"]: row for row in self.rows}
        self.assertGreater(by_odds[1.5]["variance"], by_odds[6.0]["variance"])

    def test_verdict_does_not_call_any_structure_better_value(self):
        verdict = self.result["verdict"].lower()
        self.assertIn("preference over distributions", verdict)
        for banned in ("better value", "guaranteed", "profitable"):
            self.assertNotIn(banned, verdict)

    def test_caveats_mention_the_margin_and_availability(self):
        joined = " ".join(self.result["caveats"]).lower()
        self.assertIn("margin", joined)
        self.assertIn("obtainable", joined)

    def test_rejects_impossible_inputs(self):
        with self.assertRaises(ValueError):
            engine.compare_structures(0, [2.0])
        with self.assertRaises(ValueError):
            engine.compare_structures(100, [])
        with self.assertRaises(ValueError):
            engine.compare_structures(100, [0.9])


if __name__ == "__main__":
    unittest.main()
