"""Tests for the per-claim explanations.

The product's risk is that a number is read as a stronger claim than it is. The explanations exist to
prevent that, so the tests check that every explained claim says what it assumes and what it does not
show - especially for the two that are easiest to over-read: a historical maximum quote, and a
market-implied probability.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import demo_data, engine  # noqa: E402


class ExplanationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.explanations = engine.explanations()

    def test_every_explanation_has_three_parts(self):
        for key, item in self.explanations.items():
            for field in ("what", "assumes", "does_not_show"):
                self.assertIn(field, item, f"{key} is missing {field}")
                self.assertTrue(item[field].strip(), f"{key}.{field} is empty")

    def test_the_best_price_explains_it_is_not_obtainable(self):
        text = self.explanations["best_recorded_price"]["does_not_show"].lower()
        self.assertIn("obtain", text)
        self.assertIn("timestamp", text)

    def test_the_market_implied_explains_the_de_vig_assumption(self):
        item = self.explanations["market_implied"]
        self.assertIn("proportional", item["assumes"].lower())
        self.assertIn("not a prediction", item["does_not_show"].lower())

    def test_the_price_implied_explains_the_margin(self):
        item = self.explanations["price_implied"]
        self.assertIn("margin", item["what"].lower() + item["does_not_show"].lower())

    def test_the_slip_explanation_states_the_independence_assumption(self):
        self.assertIn("independence", self.explanations["joint_probability"]["assumes"].lower())

    def test_assessment_response_includes_the_explanations(self):
        result = engine.assess_selection(demo_data.synthetic_fixtures(2)[0], "H")
        self.assertIn("explanations", result)
        self.assertIn("best_recorded_price", result["explanations"])

    def test_no_explanation_claims_profitability(self):
        for key, item in self.explanations.items():
            joined = " ".join(item.values()).lower()
            for banned in ("guaranteed", "risk-free", "will profit", "sure win"):
                self.assertNotIn(banned, joined, key)


if __name__ == "__main__":
    unittest.main()
