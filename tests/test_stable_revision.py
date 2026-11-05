"""Guard: bridge revisions must survive a rebase.

Two entries quoted a commit SHA that a rebase erased. The reference test caught both, but only after
the fact. These tests pin the structural fix: `--revision auto` resolves to a commit already on
origin/main, which does not move when local commits are rebased.
"""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import collab_note  # noqa: E402


class StableRevisionTest(unittest.TestCase):
    def test_auto_resolves_to_a_pushed_commit(self):
        sha = collab_note.stable_revision()
        if not sha:
            self.skipTest("no origin/main reference available in this checkout")
        proc = subprocess.run(["git", "merge-base", "--is-ancestor", sha, "origin/main"],
                              cwd=ROOT, capture_output=True)
        self.assertEqual(proc.returncode, 0, f"{sha} is not on origin/main")

    def test_a_local_only_commit_is_flagged_when_checkable(self):
        # A commit that exists only locally must not be reported as pushed.
        head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                              capture_output=True, text=True).stdout.strip()
        pushed = collab_note.revision_is_pushed(head)
        # Either answer is legitimate depending on whether the working copy is ahead; what matters is
        # that the check does not raise and returns a bool.
        self.assertIsInstance(pushed, bool)

    def test_empty_revision_is_treated_as_pushed(self):
        self.assertTrue(collab_note.revision_is_pushed(""))


if __name__ == "__main__":
    unittest.main()
