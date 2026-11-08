"""Tests for the planner: stake and multiplier in, options out.

The planner is the feature the user asked for by name, so the properties that matter are checked
directly: every option lands near the requested multiplier, its probability is the market's product
rather than an invented model, its expected net is negative under the margin, and when the market does
not offer the multiplier the answer says so instead of forcing a slip.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import demo_data, engine, planner  # noqa: E402

FIXTURES = demo_data.synthetic_fixtures(60)

# The synthetic book prices everything near evens, so a 5x target is unreachable there: a single is
# ~3x and a pair is ~9x. Derive a feasible target from the data instead of assuming one.
_date, _day = planner.latest_day(FIXTURES)
_selections = [s for f in _day for s in planner._selections(f)]
FEASIBLE_TARGET = round(_selections[0]["price"] * _selections[1]["price"], 2)
TOLERANCE = 0.02


class PlannerTest(unittest.TestCase):
    def test_options_land_within_tolerance(self):
        result = planner.plan(100, FEASIBLE_TARGET, TOLERANCE, 2, FIXTURES)
        self.assertTrue(result["found"])
        for option in result["options"]:
            self.assertGreaterEqual(option["combined_price"],
                                    FEASIBLE_TARGET * (1 - TOLERANCE) - 1e-6)
            self.assertLessEqual(option["combined_price"],
                                 FEASIBLE_TARGET * (1 + TOLERANCE) + 1e-6)

    def test_probability_is_the_product_of_the_legs(self):
        result = planner.plan(100, FEASIBLE_TARGET, TOLERANCE, 2, FIXTURES)
        for option in result["options"]:
            product = 1.0
            for leg in option["legs"]:
                product *= leg["implied"]
            # Leg values are stored rounded, so compare at the precision they are stored with.
            self.assertAlmostEqual(option["implied_probability"], product, delta=1e-3)

    def test_combined_price_is_the_product_of_the_legs(self):
        result = planner.plan(100, FEASIBLE_TARGET, TOLERANCE, 2, FIXTURES)
        for option in result["options"]:
            product = 1.0
            for leg in option["legs"]:
                product *= leg["price"]
            self.assertAlmostEqual(option["combined_price"], product, delta=1e-3)

    def test_expected_net_is_negative_under_the_margin(self):
        # At a quoted price the market's own probability cannot make a slip positive in expectation.
        result = planner.plan(100, FEASIBLE_TARGET, TOLERANCE, 2, FIXTURES)
        for option in result["options"]:
            self.assertLess(option["expected_net"], 0.0, option)

    def test_downside_is_the_full_stake(self):
        result = planner.plan(100, FEASIBLE_TARGET, TOLERANCE, 2, FIXTURES)
        for option in result["options"]:
            self.assertAlmostEqual(option["loss_if_lost"], 100.0, places=2)

    def test_legs_never_share_a_fixture(self):
        result = planner.plan(100, FEASIBLE_TARGET, TOLERANCE, 2, FIXTURES)
        for option in result["options"]:
            fixtures = [leg["fixture"] for leg in option["legs"]]
            self.assertEqual(len(fixtures), len(set(fixtures)),
                             "two selections from one match are not independent")

    def test_impossible_multiplier_is_refused_honestly(self):
        result = planner.plan(100, 5000.0, 0.01, 2, FIXTURES)
        self.assertFalse(result["found"])
        self.assertIn("does not offer", result["verdict"])

    def test_response_states_the_match_day_and_its_limits(self):
        result = planner.plan(100, FEASIBLE_TARGET, TOLERANCE, 2, FIXTURES)
        self.assertTrue(result["match_day"])
        joined = " ".join(result["caveats"]).lower()
        self.assertIn("not today's fixtures", joined)
        self.assertIn("no fixtures feed", joined)

    def test_invalid_inputs_raise(self):
        for stake, target in ((0, FEASIBLE_TARGET), (100, 0.5), (-5, 2.0)):
            with self.assertRaises(ValueError):
                planner.plan(stake, target, 0.2, 2, FIXTURES)


if __name__ == "__main__":
    unittest.main()
