"""Tests for the collaboration bridge invariants.

The last test is the one that matters: it runs the checker against the real
bridge, so an edit that makes the thread, queue and decisions inconsistent fails
the suite rather than being discovered by the next reader.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.collab_check import (  # noqa: E402
    check_coupling,
    check_decisions,
    load_queue,
    run_checks,
)
from scripts.collab_note import append, build_entry, parse_entries  # noqa: E402

FIXTURE_THREAD = """# Thread

### 2026-11-03T11:00:00Z · builder · note
First entry.
- ref: CRITIQUE.md

### 2026-11-03T11:10:00Z · oversight · review
RQ-001 reviewed.
- revision: abc1234
- ref: RQ-001
"""


class ParseEntriesTest(unittest.TestCase):
    def _thread(self, text=FIXTURE_THREAD) -> Path:
        tmp = Path(tempfile.mkdtemp()) / "THREAD.md"
        tmp.write_text(text, encoding="utf-8")
        return tmp

    def test_parses_every_entry(self):
        self.assertEqual(len(parse_entries(self._thread())), 2)

    def test_extracts_author_kind_and_fields(self):
        first, second = parse_entries(self._thread())
        self.assertEqual((first["author"], first["kind"]), ("builder", "note"))
        self.assertEqual(second["author"], "oversight")
        self.assertEqual(second["revision"], "abc1234")
        self.assertEqual(second["ref"], "RQ-001")

    def test_message_excludes_metadata_lines(self):
        first = parse_entries(self._thread())[0]
        self.assertEqual(first["message"], "First entry.")
        self.assertNotIn("revision:", first["message"])

    def test_missing_file_yields_no_entries(self):
        self.assertEqual(parse_entries(Path(tempfile.mkdtemp()) / "absent.md"), [])


class BuildEntryTest(unittest.TestCase):
    def test_rejects_unknown_author(self):
        with self.assertRaises(SystemExit):
            build_entry("stranger", "note", "hello")

    def test_rejects_empty_message(self):
        with self.assertRaises(SystemExit):
            build_entry("builder", "note", "   ")

    def test_appends_to_empty_file_with_preamble(self):
        target = Path(tempfile.mkdtemp()) / "THREAD.md"
        append(build_entry("builder", "note", "hello", stamp="2026-11-03T12:00:00Z"), target)
        text = target.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("# Thread"))
        self.assertEqual(len(parse_entries(target)), 1)


class QueueTest(unittest.TestCase):
    def _queue(self, body: str) -> Path:
        tmp = Path(tempfile.mkdtemp()) / "REVIEW_QUEUE.md"
        tmp.write_text("| ID | Change | Ref | Revision | State | Evidence | Reviewer |\n"
                       "| --- | --- | --- | --- | --- | --- | --- |\n" + body,
                       encoding="utf-8")
        return tmp

    def test_accepts_a_well_formed_row(self):
        rows, errors = load_queue(self._queue(
            "| RQ-001 | thing | a.md | - | draft | none | oversight |\n"))
        self.assertEqual(errors, [])
        self.assertEqual(rows[0]["id"], "RQ-001")

    def test_rejects_wrong_column_count(self):
        _, errors = load_queue(self._queue("| RQ-001 | thing | a.md | - | draft |\n"))
        self.assertTrue(any("expected 7 columns" in e for e in errors))

    def test_rejects_unknown_state(self):
        _, errors = load_queue(self._queue(
            "| RQ-001 | thing | a.md | - | shipped | none | oversight |\n"))
        self.assertTrue(any("unknown state" in e for e in errors))

    def test_rejects_duplicate_ids(self):
        _, errors = load_queue(self._queue(
            "| RQ-001 | a | x | - | draft | none | oversight |\n"
            "| RQ-001 | b | y | - | draft | none | oversight |\n"))
        self.assertTrue(any("duplicate" in e for e in errors))


class CouplingTest(unittest.TestCase):
    def test_verdict_without_review_is_an_error(self):
        rows = [{"id": "RQ-009", "revision": "abc1234", "state": "accepted"}]
        errors, _ = check_coupling(rows, [], verify_revisions=False)
        self.assertTrue(any("no oversight review covers" in e for e in errors))

    def test_review_at_a_different_revision_does_not_authorise(self):
        rows = [{"id": "RQ-009", "revision": "abc1234", "state": "accepted"}]
        entries = [{"author": "oversight", "kind": "review", "stamp": "t",
                    "revision": "def5678", "ref": "RQ-009", "message": "RQ-009"}]
        errors, _ = check_coupling(rows, entries, verify_revisions=False)
        self.assertTrue(any("no oversight review covers" in e for e in errors))

    def test_verdict_reviewed_at_same_revision_passes(self):
        rows = [{"id": "RQ-009", "revision": "abc1234", "state": "accepted"}]
        entries = [{"author": "oversight", "kind": "review", "stamp": "t",
                    "revision": "abc1234", "ref": "RQ-009", "message": "RQ-009"}]
        errors, _ = check_coupling(rows, entries, verify_revisions=False)
        self.assertEqual(errors, [])

    def test_ready_for_review_needs_no_verdict(self):
        rows = [{"id": "RQ-009", "revision": "-", "state": "ready_for_review"}]
        errors, _ = check_coupling(rows, [], verify_revisions=False)
        self.assertEqual(errors, [])


class DecisionsTest(unittest.TestCase):
    def _decisions(self, body: str) -> Path:
        tmp = Path(tempfile.mkdtemp()) / "DECISIONS.md"
        tmp.write_text(body, encoding="utf-8")
        return tmp

    def test_rejects_a_proposal_in_the_decision_log(self):
        path = self._decisions("## D-01\n\n**Decision:** x\n\n**Status:** proposed\n")
        self.assertTrue(any("marked proposed" in e for e in check_decisions(path)))

    def test_accepts_an_accepted_decision(self):
        path = self._decisions("## D-01\n\n**Decision:** x\n\n**Status:** accepted\n")
        self.assertEqual(check_decisions(path), [])

    def test_rejects_an_empty_decision_log(self):
        self.assertTrue(check_decisions(self._decisions("# Decisions\n\nnone yet\n")))


class RealBridgeTest(unittest.TestCase):
    """The real bridge must be internally consistent at all times."""

    def test_real_bridge_valid(self):
        collab = ROOT / "docs" / "COLLAB"
        errors, _, stats = run_checks(
            collab / "THREAD.md", collab / "REVIEW_QUEUE.md", collab / "DECISIONS.md",
            verify_revisions=False, check_history=False)
        self.assertEqual(errors, [], f"bridge errors: {errors}")
        self.assertGreaterEqual(stats["entries"], 1)
        self.assertGreaterEqual(stats["rows"], 1)


if __name__ == "__main__":
    unittest.main()
