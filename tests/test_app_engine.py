"""Tests for the product engine.

These check arithmetic and claim labelling. They do not check that the product is *useful* — that is a
user question — and they deliberately do not assert anything about profitability.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import engine  # noqa: E402


class DevigTest(unittest.TestCase):
    def test_probabilities_sum_to_one(self):
        probs = engine.devig([2.0, 3.5, 4.0])
        self.assertAlmostEqual(sum(probs), 1.0, places=12)

    def test_margin_is_preserved_by_the_assumption(self):
        odds = [2.0, 3.5, 4.0]
        self.assertGreater(engine.overround(odds), 0)
        self.assertAlmostEqual(sum(engine.devig(odds)), 1.0, places=12)

    def test_shorter_price_means_higher_probability(self):
        probs = engine.devig([1.5, 4.0, 7.0])
        self.assertGreater(probs[0], probs[1])
        self.assertGreater(probs[1], probs[2])


class CorpusTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixtures = engine.load_fixtures(limit=40)

    def test_corpus_loads(self):
        self.assertGreater(len(self.fixtures), 0)
        for fx in self.fixtures:
            self.assertGreaterEqual(len(fx.odds), 2)

    def test_market_view_states_claim_kinds(self):
        view = engine.market_view(self.fixtures[0])
        self.assertIn("observed", view["claims"]["quotes"])
        self.assertIn("estimated", view["claims"]["market_implied"])
        self.assertEqual(len(view["market_implied"]), 3)

    def test_best_quote_is_at_least_the_average(self):
        # Arithmetic, not evidence: a maximum cannot sit below a mean.
        for fx in self.fixtures[:10]:
            for outcome in engine.OUTCOMES:
                idx = engine.OUTCOMES.index(outcome)
                self.assertGreaterEqual(fx.odds["Max"][idx], fx.odds["Avg"][idx] - 1e-9)

    def test_assessment_does_not_claim_profitability(self):
        result = engine.assess_selection(self.fixtures[0], "H")
        text = (result["assessment"] + " " + str(result["claims"])).lower()
        for banned in ("guaranteed", "risk-free", "profitable", "sure thing"):
            self.assertNotIn(banned, text)


class SlipTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixtures = engine.load_fixtures(limit=60)

    def leg(self, fixture, outcome="H"):
        idx = engine.OUTCOMES.index(outcome)
        probs = engine.devig(fixture.odds["Avg"])
        return {"fixture_key": fixture.key, "label": fixture.label, "outcome": outcome,
                "price": fixture.odds["Max"][idx], "prob": probs[idx]}

    def test_cross_match_slip_multiplies(self):
        a, b = self.fixtures[0], self.fixtures[1]
        result = engine.slip_view([self.leg(a), self.leg(b)], 100)
        self.assertFalse(result["same_match"])
        self.assertAlmostEqual(result["dependence_ratio"], engine.CROSS_MATCH_DEPENDENCE)
        self.assertAlmostEqual(result["joint_probability"], result["naive_product"], places=9)

    def test_same_match_slip_is_corrected(self):
        a = self.fixtures[0]
        result = engine.slip_view([self.leg(a, "H"), self.leg(a, "D")], 100)
        self.assertTrue(result["same_match"])
        self.assertAlmostEqual(result["dependence_ratio"], engine.SAME_MATCH_DEPENDENCE)
        self.assertGreater(result["joint_probability"], result["naive_product"])

    def test_stake_arithmetic_is_explicit(self):
        result = engine.slip_view([self.leg(self.fixtures[0])], 100)
        self.assertAlmostEqual(result["gross_return"], 100 * result["combined_odds"], places=2)
        self.assertAlmostEqual(result["net_result"], result["gross_return"] - 100, places=2)
        self.assertAlmostEqual(result["full_stake_loss"], 100, places=2)

    def test_rejects_bad_stake(self):
        with self.assertRaises(ValueError):
            engine.slip_view([self.leg(self.fixtures[0])], 0)


class TargetTest(unittest.TestCase):
    def test_finds_matches_near_the_target(self):
        fixtures = engine.load_fixtures(limit=300)
        result = engine.target_search(100, 10.0, 0.2, fixtures=fixtures)
        self.assertTrue(result["found"])
        for match in result["matches"]:
            self.assertLessEqual(abs(match["price"] / 10.0 - 1), 0.2 + 1e-9)

    def test_reports_no_match_honestly(self):
        fixtures = engine.load_fixtures(limit=60)
        result = engine.target_search(100, 5000.0, 0.01, fixtures=fixtures)
        self.assertFalse(result["found"])
        self.assertIn("not a promise", result["verdict"])

    def test_rejects_impossible_targets(self):
        with self.assertRaises(ValueError):
            engine.target_search(100, 0.5)


class JackpotTest(unittest.TestCase):
    def test_pool_and_coverage_arithmetic(self):
        result = engine.jackpot_view(entrants=1000, stake=100, takeout=0.3, your_lines=1)
        self.assertAlmostEqual(result["pool"], 1000 * 100 * 0.7, places=2)
        self.assertLess(result["coverage"], 0.01)

    def test_more_lines_increases_coverage(self):
        one = engine.jackpot_view(1000, 100, 0.3, 1)
        many = engine.jackpot_view(1000, 100, 0.3, 10)
        self.assertGreater(many["coverage"], one["coverage"])


if __name__ == "__main__":
    unittest.main()
