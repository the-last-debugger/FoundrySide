"""Tests for the repository audit.

The audit exists because the same cross-document inconsistencies kept being found by hand. These tests
pin the checks that catch them, and one test asserts the real repository currently passes — so a
regression fails the suite rather than waiting for a person to notice.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import audit  # noqa: E402


class LinkCheckTest(unittest.TestCase):
    def test_broken_link_is_reported(self):
        tmp = Path(tempfile.mkdtemp())
        (tmp / "doc.md").write_text("[missing](nope.md)\n", encoding="utf-8")
        original_docs, original_root = audit.DOCS, audit.ROOT
        try:
            audit.DOCS = tmp
            audit.ROOT = tmp
            result = audit.check_links()
        finally:
            audit.DOCS, audit.ROOT = original_docs, original_root
        self.assertFalse(result.ok)
        self.assertIn("nope.md", result.detail)

    def test_valid_link_passes(self):
        tmp = Path(tempfile.mkdtemp())
        (tmp / "target.md").write_text("x", encoding="utf-8")
        (tmp / "doc.md").write_text("[ok](target.md)\n", encoding="utf-8")
        original_docs, original_root = audit.DOCS, audit.ROOT
        try:
            audit.DOCS = tmp
            audit.ROOT = tmp
            result = audit.check_links()
        finally:
            audit.DOCS, audit.ROOT = original_docs, original_root
        self.assertTrue(result.ok, result.detail)

    def test_external_links_are_ignored(self):
        tmp = Path(tempfile.mkdtemp())
        (tmp / "doc.md").write_text("[site](https://example.com/x)\n", encoding="utf-8")
        original_docs, original_root = audit.DOCS, audit.ROOT
        try:
            audit.DOCS = tmp
            audit.ROOT = tmp
            result = audit.check_links()
        finally:
            audit.DOCS, audit.ROOT = original_docs, original_root
        self.assertTrue(result.ok)


class StalePhraseTest(unittest.TestCase):
    def test_a_returned_overclaim_is_caught(self):
        tmp = Path(tempfile.mkdtemp())
        (tmp / "bad.md").write_text("This is the tradeable quantity.", encoding="utf-8")
        original_docs, original_research = audit.DOCS, audit.RESEARCH
        try:
            audit.DOCS = tmp
            audit.RESEARCH = tmp
            result = audit.check_stale_phrases()
        finally:
            audit.DOCS, audit.RESEARCH = original_docs, original_research
        self.assertFalse(result.ok)
        self.assertIn("tradeable", result.detail)


class RepositoryPassesTest(unittest.TestCase):
    def test_the_repository_passes_its_own_audit(self):
        failures = [check().name for check in audit.CHECKS if not check().ok]
        self.assertEqual(failures, [], f"audit failures: {failures}")


if __name__ == "__main__":
    unittest.main()
