"""Tests for the daily monitored slip.

The value of this system is the record, not an edge. So the tests check the properties that make the
record trustworthy: slips are written before results are known, settlement is correct, a day cannot be
recorded twice, and the monitor reports the market-implied probability alongside the realised rate.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "research"))

import daily_slip  # noqa: E402

try:
    import slip_rules
    HAS_DATA = bool(slip_rules.load_days())
except Exception:
    HAS_DATA = False


class SlipStoreTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp()) / "slips.jsonl"
        self._orig = daily_slip.STORE
        daily_slip.STORE = self.tmp

    def tearDown(self):
        daily_slip.STORE = self._orig

    def test_empty_store_is_not_an_error(self):
        self.assertEqual(daily_slip.load_slips(), [])

    def test_round_trip(self):
        slips = [{"date": "01/01/2026", "persona": "cautious", "status": "pending",
                  "legs": [], "stake": 100.0}]
        daily_slip.save_slips(slips)
        self.assertEqual(len(daily_slip.load_slips()), 1)

    def test_status_on_empty_store_is_graceful(self):
        self.assertEqual(daily_slip.status(), 0)


@unittest.skipUnless(HAS_DATA, "corpus not present")
class SlipCycleTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp()) / "slips.jsonl"
        self._orig = daily_slip.STORE
        daily_slip.STORE = self.tmp
        self.days = slip_rules.load_days()

    def tearDown(self):
        daily_slip.STORE = self._orig

    def test_pick_writes_one_slip_per_persona_for_the_latest_day(self):
        daily_slip.pick(None)
        slips = daily_slip.load_slips()
        self.assertEqual(len(slips), len(daily_slip.PERSONAS))
        self.assertTrue(all(s["status"] == "pending" for s in slips))
        latest = self.days[-1]["date"]
        self.assertTrue(all(s["date"] == latest for s in slips),
                        "slips must be written for the most recent match-day in the corpus")

    def test_pick_is_idempotent_for_a_day(self):
        daily_slip.pick(None)
        before = len(daily_slip.load_slips())
        daily_slip.pick(None)
        self.assertEqual(len(daily_slip.load_slips()), before, "a day must not be recorded twice")

    def test_each_slip_records_both_price_bases_and_the_implied_probability(self):
        daily_slip.pick(None)
        for slip in daily_slip.load_slips():
            for leg in slip["legs"]:
                self.assertIn("price_best", leg)
                self.assertIn("price_avg", leg)
                self.assertGreaterEqual(leg["implied"], 0.0)
                self.assertLessEqual(leg["implied"], 1.0)
            self.assertIn("claims", slip)

    def test_settlement_resolves_a_known_day(self):
        daily_slip.pick(None)
        daily_slip.settle()
        slips = daily_slip.load_slips()
        self.assertTrue(all(s["status"] in ("won", "lost") for s in slips))
        for slip in slips:
            self.assertIn("net_best", slip)
            self.assertIn("net_avg", slip)

    def test_status_runs_after_settlement(self):
        daily_slip.pick(None)
        daily_slip.settle()
        self.assertEqual(daily_slip.status(), 0)


if __name__ == "__main__":
    unittest.main()
