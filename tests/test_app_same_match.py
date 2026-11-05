"""Tests for the one same-match combination the corpus can describe - and its limits.

The product accepts a result selection and an over/under selection from the same match, because those
are different markets and are not mutually exclusive. It refuses to *quantify* their joint, because the
measured 1.49 ratio is a population average that can imply probabilities above one. These tests pin
both halves of that decision.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import demo_data, engine  # noqa: E402


def has_totals(fixture) -> bool:
    return bool(fixture.totals)


class SameMatchTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixtures = [f for f in demo_data.synthetic_fixtures(30) if has_totals(f)]
        if not cls.fixtures:
            raise unittest.SkipTest("no synthetic fixture carries totals prices")
        cls.fixture = cls.fixtures[0]
        cls.other = next(f for f in demo_data.synthetic_fixtures(30) if f.key != cls.fixture.key)

    def leg(self, fixture, market, outcome, index):
        prices = fixture.odds["Max"] if market == "1X2" else fixture.totals["Max"]
        probs = engine.devig(fixture.odds["Avg"] if market == "1X2" else fixture.totals["Avg"])
        return {"fixture_key": fixture.key, "label": f"{fixture.label} {outcome}", "outcome": outcome,
                "market": market, "price": prices[index], "prob": probs[index]}

    def test_result_and_totals_from_one_match_is_accepted(self):
        result = engine.slip_view([self.leg(self.fixture, "1X2", "H", 0),
                                   self.leg(self.fixture, "OU", "O", 0)], 100)
        self.assertTrue(result["same_match"])

    def test_no_corrected_joint_is_published_for_same_match(self):
        result = engine.slip_view([self.leg(self.fixture, "1X2", "H", 0),
                                   self.leg(self.fixture, "OU", "O", 0)], 100)
        self.assertIsNone(result["joint_probability"],
                          "a population-average ratio must not be presented as this pair's joint")
        self.assertIsNone(result["dependence_ratio"])
        joined = " ".join(result["caveats"]).lower()
        self.assertIn("population average", joined)
        self.assertIn("not a conditional model", joined)

    def test_the_naive_product_is_still_reported(self):
        result = engine.slip_view([self.leg(self.fixture, "1X2", "H", 0),
                                   self.leg(self.fixture, "OU", "O", 0)], 100)
        self.assertGreater(result["naive_product"], 0.0)
        self.assertLessEqual(result["naive_product"], 1.0)

    def test_two_result_selections_from_one_match_are_refused(self):
        with self.assertRaises(ValueError) as ctx:
            engine.slip_view([self.leg(self.fixture, "1X2", "H", 0),
                              self.leg(self.fixture, "1X2", "D", 1)], 100)
        self.assertIn("mutually exclusive", str(ctx.exception))

    def test_two_totals_selections_from_one_match_are_refused(self):
        with self.assertRaises(ValueError):
            engine.slip_view([self.leg(self.fixture, "OU", "O", 0),
                              self.leg(self.fixture, "OU", "U", 1)], 100)

    def test_cross_match_pairs_keep_the_plain_product(self):
        result = engine.slip_view([self.leg(self.fixture, "1X2", "H", 0),
                                   self.leg(self.other, "1X2", "A", 2)], 100)
        self.assertFalse(result["same_match"])
        self.assertAlmostEqual(result["joint_probability"], result["naive_product"], places=9)
        self.assertEqual(result["dependence_ratio"], engine.CROSS_MATCH_DEPENDENCE)

    def test_market_view_exposes_totals_when_present(self):
        view = engine.market_view(self.fixture)
        self.assertIsNotNone(view["totals"])
        self.assertIn("Max", view["totals"])


if __name__ == "__main__":
    unittest.main()
