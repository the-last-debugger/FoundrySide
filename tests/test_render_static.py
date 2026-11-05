"""Tests for the static snapshot renderer.

The snapshot is how a reviewer sees the product without running it, so it must be generated from the
engine rather than written by hand, and it must carry the same claim kinds and caveats the running
product shows.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import render_static  # noqa: E402


class StaticSnapshotTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = Path(tempfile.mkdtemp()) / "snapshot.html"
        render_static.main(["--demo", "--out", str(cls.path)])
        cls.html = cls.path.read_text(encoding="utf-8")

    def test_renders_without_the_corpus(self):
        self.assertGreater(len(self.html), 2000)
        self.assertIn("static snapshot", self.html.lower())

    def test_carries_the_claim_kinds(self):
        for kind in ("obs", "est"):
            self.assertIn(f"tag {kind}", self.html, kind)

    def test_carries_caveats(self):
        self.assertIn("caveat", self.html)
        self.assertIn("obtainable", " ".join(self.html.lower().split()))

    def test_carries_the_no_claim_footer(self):
        # Normalise whitespace: the footer wraps mid-phrase in the rendered HTML.
        lowered = " ".join(self.html.lower().split())
        self.assertIn("no profitability", lowered)
        self.assertIn("timestamps", lowered)

    def test_shows_the_three_views(self):
        for section in ("Assess", "Market", "Structures"):
            self.assertIn(section, self.html)

    def test_demo_mode_is_labelled_as_synthetic(self):
        self.assertIn("synthetic demonstration fixtures", self.html.lower())

    def test_no_external_assets(self):
        # The page must render offline: no scripts, no fonts, no remote images.
        self.assertNotIn("<script", self.html)
        self.assertNotIn("http://", self.html)
        self.assertNotIn("https://", self.html)


if __name__ == "__main__":
    unittest.main()
