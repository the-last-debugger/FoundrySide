"""Tests for the pilot model: probability sanity and, crucially, no look-ahead.

The point-in-time rule is the one property that would silently invalidate every downstream
number, so it gets a direct test: changing a later result must not change an earlier
prediction.
"""

from __future__ import annotations

import copy
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research import pilot_model  # noqa: E402

BASE = datetime(2024, 8, 16, 14, 0, tzinfo=timezone.utc)


def fixture(home, away, kick, hg, ag):
    return {
        "league": "E0", "season": "2425", "cluster": "E0_2425",
        "kickoff_utc": kick, "cutoff_utc": kick - timedelta(minutes=90),
        "p_market": 0.5, "y": 1 if hg + ag >= 3 else 0,
        "home": home, "away": away, "home_goals": hg, "away_goals": ag,
        "phase": "pilot",
    }


def frame():
    teams = ["A", "B", "C", "D"]
    rows = []
    for round_no in range(4):
        kick = BASE + timedelta(days=7 * round_no)
        for i in range(2):
            rows.append(fixture(teams[i], teams[i + 2], kick, 2, 1))
    return rows


class ProbabilityTest(unittest.TestCase):
    def test_probability_is_a_probability(self):
        for lam_h, lam_a in ((1.2, 1.0), (0.5, 2.5), (3.0, 0.4), (0.2, 0.2)):
            p = pilot_model.p_over_25(lam_h, lam_a)
            self.assertGreater(p, 0.0)
            self.assertLess(p, 1.0)

    def test_more_expected_goals_means_more_over(self):
        self.assertGreater(pilot_model.p_over_25(2.0, 1.5),
                           pilot_model.p_over_25(1.0, 0.8))


class NoLookAheadTest(unittest.TestCase):
    def test_changing_a_later_result_does_not_change_earlier_predictions(self):
        rows = frame()
        original = pilot_model.predict_phase(copy.deepcopy(rows), "pilot")

        altered = frame()
        altered[-1]["home_goals"], altered[-1]["away_goals"] = 6, 6
        altered[-1]["y"] = 1
        changed = pilot_model.predict_phase(altered, "pilot")

        # The final fixture is predicted before its own result is applied, so even its
        # prediction must be identical; only the (unused) later state differs.
        self.assertEqual([r["p_model"] for r in original],
                         [r["p_model"] for r in changed])

    def test_simultaneous_matches_do_not_inform_each_other(self):
        rows = frame()
        rows[0]["home_goals"], rows[0]["away_goals"] = 7, 0
        rows[0]["y"] = 1
        preds = pilot_model.predict_phase(rows, "pilot")
        # Rows 0 and 1 share a kickoff, so they must be predicted from the same state.
        self.assertEqual(preds[0]["lam_home"], preds[1]["lam_home"])

    def test_predictions_use_only_prior_matches(self):
        preds = pilot_model.predict_phase(frame(), "pilot")
        # The very first match has no history, so it must equal the prior-based estimate.
        self.assertAlmostEqual(preds[0]["lam_home"], 1.45, places=1)


if __name__ == "__main__":
    unittest.main()
