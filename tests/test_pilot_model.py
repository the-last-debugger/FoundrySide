"""Tests for the pilot model: probability sanity, cutoff integrity, and boundary hygiene.

The cutoff test is the one that matters. An earlier version proved that a later kickoff
could not change an earlier prediction, which is not the same claim: a match that kicked
off two hours before the target is still in progress at the target's T−90 cutoff, so its
result must be invisible.
"""

from __future__ import annotations

import csv
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research import pilot_model  # noqa: E402

BASE = datetime(2024, 8, 16, 12, 0, tzinfo=timezone.utc)


def fixture(home, away, kick, hg, ag):
    return {
        "league": "E0", "season": "2425", "cluster": "E0_2425",
        "kickoff_utc": kick, "cutoff_utc": kick - timedelta(minutes=90),
        "p_market": 0.5, "y": 1 if hg + ag >= 3 else 0,
        "home": home, "away": away, "home_goals": hg, "away_goals": ag,
        "phase": "pilot",
    }


class ProbabilityTest(unittest.TestCase):
    def test_probability_is_a_probability(self):
        for lam_h, lam_a in ((1.2, 1.0), (0.5, 2.5), (3.0, 0.4), (0.2, 0.2)):
            p = pilot_model.p_over_25(lam_h, lam_a)
            self.assertGreater(p, 0.0)
            self.assertLess(p, 1.0)

    def test_more_expected_goals_means_more_over(self):
        self.assertGreater(pilot_model.p_over_25(2.0, 1.5),
                           pilot_model.p_over_25(1.0, 0.8))


class CutoffTest(unittest.TestCase):
    def test_result_still_in_progress_at_cutoff_is_invisible(self):
        # Prior match kicks off 2h before the target: available at +3h, i.e. one hour
        # *after* the target's cutoff. It must not influence the prediction.
        prior = fixture("A", "B", BASE, 5, 0)
        target = fixture("C", "D", BASE + timedelta(hours=2), 1, 1)
        preds = pilot_model.predict([prior, target])
        self.assertAlmostEqual(preds[1]["p_model"], preds[0]["p_model"], places=9)

    def test_result_known_before_cutoff_is_used(self):
        # Prior match 6h earlier: available at +3h, well before the target's cutoff.
        prior = fixture("A", "B", BASE, 5, 0)
        target = fixture("C", "D", BASE + timedelta(hours=6), 1, 1)
        preds = pilot_model.predict([prior, target])
        self.assertNotAlmostEqual(preds[1]["p_model"], preds[0]["p_model"], places=6)

    def test_simultaneous_matches_do_not_inform_each_other(self):
        rows = [fixture("A", "B", BASE, 7, 0), fixture("C", "D", BASE, 0, 4)]
        preds = pilot_model.predict(rows)
        self.assertEqual(preds[0]["p_model"], preds[1]["p_model"])


class BoundaryTest(unittest.TestCase):
    def test_committed_artefact_is_pilot_only(self):
        """No confirmatory row may appear in the pilot artefact."""
        path = ROOT / "research" / "pilot_deltas.csv"
        if not path.exists():
            self.skipTest("pilot artefact not generated")
        with path.open(encoding="utf-8", newline="") as fh:
            phases = {row["phase"] for row in csv.DictReader(fh)}
        self.assertEqual(phases, {"pilot"})


if __name__ == "__main__":
    unittest.main()
