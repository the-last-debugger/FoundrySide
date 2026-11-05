"""Tests for the stake-structure study's arithmetic.

The study's algebra has three claims that can be checked without the corpus: the stake needed for a
target net, the expected value under a margin, and the variance ordering. If any of those is wrong the
report's conclusions are wrong, so they are pinned here.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research"))

import stake_structures as ss  # noqa: E402


class StructureArithmeticTest(unittest.TestCase):
    def test_stake_makes_the_requested_net(self):
        for odds in (1.5, 2.0, 3.0, 6.0):
            s = ss.structures_for(odds, margin=0.0, target_net=200.0)
            self.assertAlmostEqual(s["net"], 200.0, places=6)
            self.assertAlmostEqual(s["stake"], 200.0 / (odds - 1.0), places=6)

    def test_implied_probability_uses_the_margin(self):
        self.assertAlmostEqual(ss.implied(2.0, 0.0), 0.5, places=9)
        self.assertLess(ss.implied(2.0, 0.05), 0.5)

    def test_expected_value_is_proportional_to_stake_not_odds(self):
        # EV = -s*m/(1+m): same stake, same expected loss, whatever the price.
        margin = 0.04
        a = ss.structures_for(1.5, margin, target_net=200.0)
        b = ss.structures_for(6.0, margin, target_net=200.0)
        self.assertAlmostEqual(a["ev"], -a["stake"] * margin / (1 + margin), places=6)
        self.assertAlmostEqual(b["ev"], -b["stake"] * margin / (1 + margin), places=6)
        # Matched on net upside, the higher-odds structure needs a smaller stake, so it loses
        # less in absolute expectation even though both are negative.
        self.assertGreater(b["ev"], a["ev"])

    def test_higher_odds_means_smaller_stake_and_lower_probability(self):
        a = ss.structures_for(2.0, 0.04, 200.0)
        b = ss.structures_for(4.0, 0.04, 200.0)
        self.assertGreater(a["stake"], b["stake"])
        self.assertGreater(a["prob"], b["prob"])

    def test_variance_falls_with_odds_at_matched_net(self):
        a = ss.structures_for(2.0, 0.04, 200.0)
        b = ss.structures_for(5.0, 0.04, 200.0)
        self.assertGreater(a["variance"], b["variance"])

    def test_downside_is_the_full_stake(self):
        s = ss.structures_for(3.0, 0.04, 200.0)
        self.assertAlmostEqual(s["downside"], s["stake"], places=9)

    def test_no_structure_has_positive_expected_value_under_a_margin(self):
        for odds in (1.3, 2.0, 3.0, 8.0):
            self.assertLess(ss.structures_for(odds, 0.04, 200.0)["ev"], 0.0)


class SeasonLabelTest(unittest.TestCase):
    def test_season_starts_in_july(self):
        self.assertEqual(ss.season_of("15/08/2021"), "2021")
        self.assertEqual(ss.season_of("15/04/2022"), "2021")

    def test_bad_dates_do_not_raise(self):
        self.assertEqual(ss.season_of("nonsense"), "unknown")


if __name__ == "__main__":
    unittest.main()
