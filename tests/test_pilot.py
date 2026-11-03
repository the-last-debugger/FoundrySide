"""Tests for the pilot frame's classification and accounting.

The frame must not be able to bury a defect in a total. Each rejection category is
separately reachable here, so a broken clock cannot be counted as a missing price.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research import pilot  # noqa: E402

GOOD = {
    "_league": "E0", "_season": "2425",
    "Date": "16/08/2024", "Time": "20:00",
    "FTHG": "2", "FTAG": "1",
    "PC>2.5": "1.90", "PC<2.5": "1.95",
}


def row(**overrides):
    r = dict(GOOD)
    r.update(overrides)
    return r


class FrameTest(unittest.TestCase):
    def test_valid_row_is_framed_with_cutoff(self):
        framed, rejects = pilot.frame([row()])
        self.assertEqual(len(framed), 1)
        self.assertEqual(sum(len(v) for v in rejects.values()), 0)
        f = framed[0]
        self.assertEqual(f["phase"], "confirmatory")   # 2425 is a confirmatory season
        self.assertLess(f["cutoff_utc"], f["kickoff_utc"])
        self.assertAlmostEqual(f["p_market"], 0.5065, places=3)   # de-vigged 1.90/1.95

    def test_missing_price_is_its_own_category(self):
        framed, rejects = pilot.frame([row(**{"PC>2.5": ""})])
        self.assertEqual(framed, [])
        self.assertEqual(len(rejects["missing_ou_price"]), 1)
        self.assertEqual(len(rejects["clock"]), 0)

    def test_bad_clock_is_not_a_price_failure(self):
        framed, rejects = pilot.frame([row(**{"Time": "99:99"})])
        self.assertEqual(framed, [])
        self.assertEqual(len(rejects["clock"]), 1)
        self.assertEqual(len(rejects["missing_ou_price"]), 0)

    def test_bad_score_is_not_a_price_failure(self):
        framed, rejects = pilot.frame([row(**{"FTHG": ""})])
        self.assertEqual(framed, [])
        self.assertEqual(len(rejects["result"]), 1)
        self.assertEqual(len(rejects["missing_ou_price"]), 0)

    def test_phase_assignment_covers_every_season(self):
        seasons = {"2021": "pilot", "2122": "pilot", "2223": "pilot",
                   "2324": "confirmatory", "2425": "confirmatory"}
        for season, expected in seasons.items():
            framed, _ = pilot.frame([row(**{"_season": season})])
            self.assertEqual(framed[0]["phase"], expected, season)

    def test_unknown_season_is_unassigned(self):
        framed, _ = pilot.frame([row(**{"_season": "9999"})])
        self.assertEqual(framed[0]["phase"], "unassigned")


if __name__ == "__main__":
    unittest.main()
