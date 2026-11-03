"""Point-in-time tests for the feature screen's histories.

Two cases decide whether the feature families are safe to interpret:

- a same-date earlier kickoff whose result is not yet knowable at the target's cutoff;
- a same-date earlier kickoff whose result *is* knowable.

The first version of the builder sorted by date and applied results immediately, so it failed the
first case while passing the second — which is why an availability test is not the same as an
ordering test.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research import feature_screen as fs  # noqa: E402


def raw(date, time, home, away, hg, ag, season="2122", league="E0"):
    return {"_league": league, "_season": season, "Date": date, "Time": time,
            "HomeTeam": home, "AwayTeam": away, "FTHG": str(hg), "FTAG": str(ag),
            "PC>2.5": "1.95", "PC<2.5": "1.90",
            "B365C>2.5": "1.92", "B365C<2.5": "1.92",
            "PSCH": "1.90", "PSCD": "3.40", "PSCA": "3.80"}


class AvailabilityTest(unittest.TestCase):
    def build(self, rows):
        original = fs.analyse.load
        fs.analyse.load = lambda: rows
        try:
            return fs.build()[0]
        finally:
            fs.analyse.load = original

    def test_same_date_result_is_invisible_when_not_yet_available(self):
        # 12:00 match, then 13:00 match: the first is only knowable at 15:00, after the
        # second's 11:30 cutoff. The second must see no history at all.
        rows = [raw("16/08/2024", "12:00", "X", "Y", 5, 0),
                raw("16/08/2024", "13:00", "X", "Z", 1, 1)]
        built = self.build(rows)
        self.assertEqual(len(built), 2)
        self.assertAlmostEqual(built[1]["trend_sum"], 5.2, places=6)

    def test_result_is_visible_when_available_before_the_cutoff(self):
        # 08:00 match, available at 11:00, before the 13:00 match's 11:30 cutoff.
        rows = [raw("16/08/2024", "08:00", "X", "Y", 5, 0),
                raw("16/08/2024", "13:00", "X", "Z", 1, 1)]
        built = self.build(rows)
        self.assertGreater(built[1]["trend_sum"], 5.2)

    def test_simultaneous_kickoffs_share_one_state(self):
        rows = [raw("16/08/2024", "15:00", "X", "Y", 4, 0),
                raw("16/08/2024", "15:00", "Z", "W", 1, 1)]
        built = self.build(rows)
        self.assertEqual(built[0]["rest_diff"], built[1]["rest_diff"])


if __name__ == "__main__":
    unittest.main()
