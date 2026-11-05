"""Tests for the jackpot pool model.

The study is arithmetic under assumptions, so the tests pin the arithmetic: the identities the report
relies on, and the limits it states. If these hold, the table means what the prose says it means.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research"))

import jackpot_mechanics as jm  # noqa: E402


class PoolModelTest(unittest.TestCase):
    def test_pool_is_entrants_times_stake_less_takeout(self):
        ev = jm.ev_per_line(q=0.0, r=0.0, entrants=1000, takeout=0.3)
        self.assertAlmostEqual(ev, -jm.STAKE, places=6)

    def test_average_coverage_loses_the_takeout_in_a_large_field(self):
        # q = r and a large field: expected net approaches -s*t.
        large = 1_000_000
        ev = jm.ev_per_line(q=1e-3, r=1e-3, entrants=large, takeout=0.3)
        self.assertAlmostEqual(ev, -jm.STAKE * 0.3, delta=0.5)

    def test_average_coverage_loses_much_more_in_a_small_field(self):
        small = jm.ev_per_line(q=1e-3, r=1e-3, entrants=100, takeout=0.3)
        self.assertLess(small, -jm.STAKE * 0.5,
                        "a small pool should punish average coverage far beyond the takeout")

    def test_breakeven_tends_to_one_over_one_minus_takeout(self):
        for takeout in (0.1, 0.2, 0.3, 0.4):
            self.assertAlmostEqual(jm.breakeven_ratio(1_000_000, takeout),
                                   1.0 / (1.0 - takeout), places=2)

    def test_breakeven_falls_as_the_field_grows(self):
        values = [jm.breakeven_ratio(n, 0.3) for n in (100, 1000, 10000)]
        self.assertGreater(values[0], values[1])
        self.assertGreater(values[1], values[2])

    def test_more_coverage_always_raises_expected_value(self):
        evs = [jm.ev_per_line(ratio * 1e-3, 1e-3, 1000, 0.3) for ratio in jm.COVERAGE_RATIOS]
        self.assertEqual(evs, sorted(evs))

    def test_report_states_it_is_arithmetic_not_evidence(self):
        text = (ROOT / "research" / "JACKPOT_MECHANICS.md").read_text(encoding="utf-8").lower()
        self.assertIn("arithmetic, not evidence", text)
        self.assertIn("no jackpot rules", text)

    def test_report_has_no_placeholder_left(self):
        text = (ROOT / "research" / "JACKPOT_MECHANICS.md").read_text(encoding="utf-8")
        self.assertNotIn("{ev_small", text)
        self.assertNotIn("{ENTRANTS_SMALL}", text)


if __name__ == "__main__":
    unittest.main()
