"""The handover must quote measured numbers, not remembered ones.

Every count in this project has drifted at least once, and each correction cost a review cycle. This
test makes the handover's numbers fail the build when they stop matching `scripts/status.py`.
"""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import status  # noqa: E402

HANDOVER = ROOT / "docs" / "HANDOVER.md"


class HandoverNumbersTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = HANDOVER.read_text(encoding="utf-8")
        # Read the recorded snapshot: collecting here would run the suite, which imports
        # this test, which would collect again.
        cls.state = status.collect(run_tests=False)

    def test_test_count_matches(self):
        count = self.state["tests"]["value"]
        self.assertIn(f"{count} tests", self.text,
                      f"handover should quote {count} tests (run python scripts/status.py)")

    def test_experiment_count_matches(self):
        count = self.state["experiments"]["value"]
        self.assertRegex(self.text, rf"{count} experiments",
                         f"handover should quote {count} experiments")

    def test_audit_check_count_matches(self):
        count = self.state["audit checks"]["value"]
        self.assertRegex(self.text, rf"{count} cross-document checks",
                         f"handover should quote {count} audit checks")

    def test_generator_count_matches(self):
        count = self.state["generators"]["value"]
        self.assertRegex(self.text, rf"{count}-generator",
                         f"handover should quote the {count}-generator sweep")

    def test_no_stale_counts_from_earlier_revisions(self):
        for stale in ("315 tests", "296 tests", "10 cross-document", "25 experiments", "34-generator"):
            self.assertNotIn(stale, self.text, f"handover still quotes {stale}")


if __name__ == "__main__":
    unittest.main()
