"""Tests for the assessment journal.

The journal exists so advice can be checked later. These tests pin the two properties that make that
meaningful: entries are immutable once written, and settling reports accuracy without dressing it up as
an edge.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import demo_data, journal  # noqa: E402


class JournalTest(unittest.TestCase):
    def setUp(self):
        self.path = Path(tempfile.mkdtemp()) / "assessments.jsonl"

    def entry(self, key, outcome, probability, fixture=None):
        return {"fixture_key": key, "fixture": fixture or key, "outcome": outcome,
                "market_implied": probability, "best_recorded_price": 2.0}

    def test_save_and_load_round_trip(self):
        journal.save(self.entry("A|1|X|Y", "H", 0.5), self.path)
        entries = journal.load(self.path)
        self.assertEqual(len(entries), 1)
        self.assertIn("recorded_utc", entries[0])

    def test_entries_are_appended_not_replaced(self):
        for i in range(3):
            journal.save(self.entry(f"K{i}", "H", 0.4), self.path)
        self.assertEqual(len(journal.load(self.path)), 3)

    def test_entry_is_not_mutated_by_saving(self):
        original = self.entry("A|1|X|Y", "H", 0.5)
        snapshot = dict(original)
        journal.save(original, self.path)
        self.assertEqual(original, snapshot, "save must not add fields to the caller's dict")

    def test_review_settles_hits_and_reports_brier(self):
        fixtures = {fx.key: fx for fx in demo_data.synthetic_fixtures(5)}
        key = next(iter(fixtures))
        fx = fixtures[key]
        home, away = fx.score
        actual = "H" if home > away else ("A" if home < away else "D")
        journal.save(self.entry(key, actual, 0.6), self.path)
        result = journal.review(fixtures, self.path)
        self.assertEqual(result["settled"], 1)
        self.assertEqual(result["hits"], 1)
        self.assertAlmostEqual(result["accuracy"], 1.0)
        self.assertIsNotNone(result["mean_brier"])

    def test_missing_fixture_is_unresolved_not_dropped(self):
        journal.save(self.entry("not-a-real-key", "H", 0.5), self.path)
        result = journal.review({}, self.path)
        self.assertEqual(result["unresolved"], 1)
        self.assertEqual(result["settled"], 0)
        self.assertIsNone(result["accuracy"])

    def test_review_states_that_accuracy_is_not_an_edge(self):
        result = journal.review({}, self.path)
        joined = " ".join(result["caveats"]).lower()
        self.assertIn("not an edge", joined)
        self.assertIn("self-selected", joined)

    def test_corrupt_line_is_skipped(self):
        self.path.write_text('{"ok": 1}\nnot json\n', encoding="utf-8")
        entries = journal.load(self.path)
        self.assertEqual(len(entries), 1)


if __name__ == "__main__":
    unittest.main()
