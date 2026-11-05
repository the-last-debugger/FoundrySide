"""Tests for the generated documentation index.

Twenty of thirty-one documents were reachable only by listing the directory. The index fixes that, and
these tests keep it honest: it must list every document, it must be derived, and its roles must come
from the filename convention rather than being invented per file.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import doc_index  # noqa: E402

INDEX = ROOT / "docs" / "INDEX.md"


class DocIndexTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = INDEX.read_text(encoding="utf-8")
        cls.docs = sorted(p.name for p in (ROOT / "docs").glob("*.md") if p.name != "INDEX.md")

    def test_every_document_is_listed(self):
        missing = [name for name in self.docs if f"[{name}]" not in self.text]
        self.assertEqual(missing, [], f"unlisted documents: {missing}")

    def test_index_is_marked_generated(self):
        self.assertIn("generated-by: doc_index.py", self.text)

    def test_counts_match_the_directory(self):
        self.assertIn(f"**{len(self.docs)}** files", self.text)

    def test_roles_are_derived_from_the_filename(self):
        for name, role in (("PREREG-STAKE.md", "Preregistration"),
                           ("HANDOVER.md", "Entry point"),
                           ("RESEARCH_PROGRAMME.md", "Register")):
            self.assertIn(name, self.text)
            self.assertEqual(doc_index.role_for(name)[0], role, name)

    def test_regenerating_is_stable(self):
        # The index is deterministic: same directory, same content.
        self.assertEqual(doc_index.build(), self.text)


if __name__ == "__main__":
    unittest.main()
