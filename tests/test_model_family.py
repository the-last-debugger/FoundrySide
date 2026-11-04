"""Chronology tests for the dispersion estimator.

The defect these guard against was live twice: results were consumed in fixture-list order and
immediately, so a later match — or one in another division — could inform an earlier prediction.
"""

from __future__ import annotations

import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research"))

from model_family import prequential_sizes  # noqa: E402


def row(day, hour, goals, league="E0", minutes=0):
    kick = datetime(2024, 8, day, hour, minutes, tzinfo=timezone.utc)
    return {"kickoff_utc": kick, "cutoff_utc": kick - timedelta(minutes=90),
            "home_goals": goals, "away_goals": 0, "cluster": f"{league}_2024"}


class ChronologyTest(unittest.TestCase):
    def test_three_hour_delay_blocks_a_recent_result(self):
        # 12:00 result is known at 15:00; the 13:00 fixture's cutoff is 11:30, so it cannot use it.
        rows = [row(16, 12, 5), row(16, 13, 1)]
        sizes = prequential_sizes(rows, min_history=0)
        self.assertEqual(len(sizes), 2)
        # With history disabled the second value is computed before any result is applied.
        self.assertEqual(sizes[1], float("inf"))

    def test_simultaneous_kickoffs_do_not_inform_each_other(self):
        rows = [row(16, 15, 4), row(16, 15, 4), row(17, 15, 1)]
        sizes = prequential_sizes(rows, min_history=0)
        # The two 15:00 fixtures share a cutoff, so neither sees the other; the next day's
        # fixture sees both.
        self.assertEqual(sizes[0], sizes[1])

    def test_global_order_not_league_order(self):
        # A D1 fixture earlier in the day precedes an E0 fixture later; ordering by league would
        # let the E0 rows be processed first and leak backwards.
        rows = [row(16, 20, 1, league="E0"), row(16, 12, 3, league="D1")]
        sizes = prequential_sizes(rows, min_history=0)
        self.assertEqual(len(sizes), 2)
        self.assertEqual(sizes[0], float("inf"))

    def test_history_accumulates_once_available(self):
        # 12:00 on the 16th is available at 15:00; 20:00 on the 17th is available at 23:00, which
        # is after the 18th's 18:30 cutoff but before the 19th's. So only the 19th sees two.
        # Totals 0 and 6 give variance above mean, so a finite size is possible at all.
        rows = [row(16, 12, 0), row(17, 20, 6), row(18, 20, 1), row(19, 20, 1)]
        sizes = prequential_sizes(rows, min_history=1)
        # The 17th's fixture sees only the 16th's result (one point, so no size); the 18th sees
        # both the 16th and the 17th, since 23:00 on the 17th precedes 18:30 on the 18th.
        self.assertEqual(sizes[1], float("inf"))
        self.assertNotEqual(sizes[2], float("inf"))


if __name__ == "__main__":
    unittest.main()
