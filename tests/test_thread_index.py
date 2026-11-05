"""Tests for the generated bridge index.

The index is a navigation aid over an append-only record. The tests check that it is derived, not
typed: the counts must match the parser, and a malformed historical entry must be shown rather than
silently normalised away.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import collab_note  # noqa: E402
import thread_index  # noqa: E402

INDEX = ROOT / "docs" / "COLLAB" / "THREAD_INDEX.md"


class ThreadIndexTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries = collab_note.parse_entries()
        cls.text = INDEX.read_text(encoding="utf-8")

    def test_index_is_derived_from_the_thread(self):
        self.assertIn(f"{len(self.entries)} entries", self.text)

    def test_author_counts_match_the_parser(self):
        from collections import Counter
        counts = Counter(e.get("author") or "unknown" for e in self.entries)
        for author, count in counts.items():
            self.assertIn(f"| {author} | {count} |", self.text, f"missing count for {author}")

    def test_unexpected_author_is_surfaced_not_hidden(self):
        unexpected = {e.get("author") for e in self.entries} - thread_index.KNOWN_AUTHORS
        if unexpected:
            self.assertIn("outside the expected set", self.text)
            for author in unexpected:
                self.assertIn(author, self.text)

    def test_index_lists_recent_entries_with_references(self):
        self.assertIn("Most recent entries", self.text)
        self.assertIn("By referenced file", self.text)

    def test_index_does_not_alter_the_thread(self):
        # The index is a separate file; the thread is the record and must stay append-only.
        thread = (ROOT / "docs" / "COLLAB" / "THREAD.md").read_text(encoding="utf-8")
        self.assertNotIn("generated-by: thread_index.py", thread)


if __name__ == "__main__":
    unittest.main()
