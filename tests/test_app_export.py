"""Tests for the exportable assessment card.

The card exists so a price cannot travel without its qualifications, so the tests check that the
caveats and claim kinds survive the round trip.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import demo_data, engine  # noqa: E402


class AssessmentCardTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = demo_data.synthetic_fixtures(3)[0]
        cls.result = engine.assess_selection(cls.fixture, "H")
        cls.card = engine.assessment_card(cls.result)

    def test_card_carries_values_and_claims(self):
        self.assertEqual(self.card["kind"], "foundryside.assessment")
        self.assertIn("best_recorded_price", self.card["values"])
        self.assertIn("observed", self.card["claims"]["best_recorded_price"])
        self.assertIn("estimated", self.card["claims"]["market_implied"])

    def test_card_carries_caveats(self):
        joined = " ".join(self.card["caveats"]).lower()
        self.assertIn("obtainable", joined)
        self.assertIn("no expected-value", joined)

    def test_card_is_json_serialisable(self):
        json.dumps(self.card)  # must not raise

    def test_text_rendering_contains_the_limits(self):
        text = engine.render_card(self.card)
        self.assertIn("Limits:", text)
        self.assertIn("obtainable", text.lower())
        self.assertIn("[observed]", text)
        self.assertIn("[estimated]", text)

    def test_text_rendering_does_not_claim_profit(self):
        text = engine.render_card(self.card).lower()
        for banned in ("guaranteed", "will win", "profitable", "risk-free"):
            self.assertNotIn(banned, text)


if __name__ == "__main__":
    unittest.main()
