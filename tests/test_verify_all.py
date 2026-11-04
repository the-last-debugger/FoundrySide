"""Provenance tests for the verification transcript.

The defect these guard against was live: the script printed the commit and the dirty-file count and
then reported PASS regardless. A transcript that attests to a commit while describing a different
tree is worse than no transcript, so the failure mode has to be tested rather than assumed.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from verify_all import diagnostic_lines, provenance  # noqa: E402


class ProvenanceTest(unittest.TestCase):
    def test_clean_tree_and_stable_head_attests(self):
        ok, reason = provenance("abc123", "abc123", 0, allow_dirty=False)
        self.assertTrue(ok, reason)
        self.assertEqual(reason, "")

    def test_dirty_tree_refuses_without_opt_out(self):
        ok, reason = provenance("abc123", "abc123", 3, allow_dirty=False)
        self.assertFalse(ok)
        self.assertIn("3 uncommitted", reason)

    def test_dirty_tree_with_explicit_opt_out_attests(self):
        ok, reason = provenance("abc123", "abc123", 3, allow_dirty=True)
        self.assertTrue(ok, reason)

    def test_moving_head_refuses_even_when_clean(self):
        ok, reason = provenance("abc123", "def456", 0, allow_dirty=True)
        self.assertFalse(ok)
        self.assertIn("HEAD moved", reason)

    def test_moving_head_refuses_even_when_dirty_allowed(self):
        ok, reason = provenance("abc123", "def456", 2, allow_dirty=True)
        self.assertFalse(ok)
        self.assertIn("HEAD moved", reason)

    def test_reason_names_the_revision(self):
        _, reason = provenance("abcdef1234567890", "abcdef1234567890", 1, allow_dirty=False)
        self.assertIn("abcdef12", reason)

class DiagnosticsTest(unittest.TestCase):
    def test_success_shows_a_short_tail(self):
        out = "\n".join(f"line{i}" for i in range(50))
        self.assertEqual(diagnostic_lines(out, True), ["line48", "line49"])

    def test_failure_shows_enough_context_and_says_how_much_was_elided(self):
        out = "\n".join(f"line{i}" for i in range(100))
        shown = diagnostic_lines(out, False)
        self.assertEqual(len(shown), 26)          # note + 25 lines
        self.assertIn("earlier line(s) omitted", shown[0])

    def test_empty_output_is_stated_not_blank(self):
        self.assertEqual(diagnostic_lines("", False), ["(no output)"])

    def test_short_failure_output_is_shown_whole_without_a_note(self):
        out = "error: boom\nhint: check the path"
        self.assertEqual(diagnostic_lines(out, False), ["error: boom", "hint: check the path"])


if __name__ == "__main__":
    unittest.main()
