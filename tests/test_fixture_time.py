"""Tests for the fixture clock rules.

These are the cases that make the T-90 cutoff auditable rather than merely arithmetic:
a British Summer Time kickoff, a post-transition kickoff, the same-day buffer that stops
a 12:30 match counting for a 15:00 one, and the two clock anomalies that a naive
implementation silently mis-resolves.
"""

from __future__ import annotations

import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.fixture_time import (  # noqa: E402
    ClockError,
    audit,
    available_at_cutoff,
    clock_status,
    cutoff_utc,
    kickoff_utc,
)


class KickoffTest(unittest.TestCase):
    def test_summer_kickoff_uses_bst(self):
        # 20:00 local in August is UTC+1.
        self.assertEqual(kickoff_utc("16/08/2024", "20:00", "E0"),
                         datetime(2024, 8, 16, 19, 0, tzinfo=timezone.utc))

    def test_after_transition_uses_gmt(self):
        # 27 October 2024: clocks went back at 02:00, so 14:00 local is UTC.
        self.assertEqual(kickoff_utc("27/10/2024", "14:00", "E0"),
                         datetime(2024, 10, 27, 14, 0, tzinfo=timezone.utc))

    def test_continental_zone_differs_from_british(self):
        # 20:00 in Madrid is UTC+2 in August, so 18:00Z — one hour before London.
        self.assertEqual(kickoff_utc("16/08/2024", "20:00", "SP1"),
                         datetime(2024, 8, 16, 18, 0, tzinfo=timezone.utc))

    def test_unknown_league_is_rejected(self):
        with self.assertRaises(ClockError):
            kickoff_utc("16/08/2024", "20:00", "ZZ9")

    def test_unparseable_time_is_rejected(self):
        with self.assertRaises(ClockError):
            kickoff_utc("16/08/2024", "", "E0")


class AnomalyTest(unittest.TestCase):
    def test_spring_forward_gap_is_detected(self):
        naive = datetime(2024, 3, 31, 1, 30)      # 01:30 does not exist in London
        self.assertEqual(clock_status(naive, "E0"), "gap")

    def test_autumn_fold_is_detected(self):
        naive = datetime(2024, 10, 27, 1, 30)     # 01:30 happens twice
        self.assertEqual(clock_status(naive, "E0"), "ambiguous")

    def test_normal_time_is_ok(self):
        self.assertEqual(clock_status(datetime(2024, 10, 27, 14, 0), "E0"), "ok")


class CutoffTest(unittest.TestCase):
    def test_cutoff_is_ninety_minutes_before_kickoff(self):
        # 20:00 BST is 19:00Z, so the cutoff is 17:30Z.
        self.assertEqual(cutoff_utc("16/08/2024", "20:00", "E0"),
                         datetime(2024, 8, 16, 17, 30, tzinfo=timezone.utc))

    def test_same_day_early_match_is_not_available(self):
        # A 12:30 match finishes around 14:20; the 15:00 fixture's cutoff is 13:30.
        self.assertFalse(available_at_cutoff("16/08/2024", "12:30", "E0",
                                             "16/08/2024", "15:00", "E0"))

    def test_previous_day_match_is_available(self):
        self.assertTrue(available_at_cutoff("15/08/2024", "20:00", "E0",
                                            "16/08/2024", "15:00", "E0"))

    def test_midnight_adjacent_match_is_available(self):
        # 22:00 the night before finishes by 01:00, well before a 15:00 cutoff.
        self.assertTrue(available_at_cutoff("15/08/2024", "22:00", "E0",
                                            "16/08/2024", "15:00", "E0"))

    def test_dst_boundary_does_not_shift_the_cutoff(self):
        # The Sunday the clocks change: a 14:00 kickoff is 14:00Z, cutoff 12:30Z.
        self.assertEqual(cutoff_utc("27/10/2024", "14:00", "E0"),
                         datetime(2024, 10, 27, 12, 30, tzinfo=timezone.utc))


class AuditTest(unittest.TestCase):
    """The audit must account for every row, not just the parseable ones."""

    HEADER = "Date,Time,HomeTeam,AwayTeam\n"

    def _corpus(self, body: str) -> Path:
        import tempfile
        d = Path(tempfile.mkdtemp())
        (d / "E0_2425.csv").write_text(self.HEADER + body, encoding="utf-8")
        return d

    def test_clean_corpus_passes(self):
        d = self._corpus("16/08/2024,20:00,A,B\n17/08/2024,15:00,C,D\n")
        self.assertEqual(audit(d, expected=2), 0)

    def test_missing_time_fails_rather_than_skips(self):
        d = self._corpus("16/08/2024,,A,B\n17/08/2024,15:00,C,D\n")
        self.assertEqual(audit(d), 1)

    def test_missing_date_fails(self):
        d = self._corpus(",20:00,A,B\n")
        self.assertEqual(audit(d), 1)

    def test_row_count_mismatch_fails(self):
        d = self._corpus("16/08/2024,20:00,A,B\n")
        self.assertEqual(audit(d, expected=2), 1)

    def test_unmapped_league_fails(self):
        import tempfile
        d = Path(tempfile.mkdtemp())
        (d / "ZZ9_2425.csv").write_text(self.HEADER + "16/08/2024,20:00,A,B\n",
                                        encoding="utf-8")
        self.assertEqual(audit(d), 1)


if __name__ == "__main__":
    unittest.main()
