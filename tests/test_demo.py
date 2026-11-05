"""The demonstration must actually demonstrate.

`scripts/demo.py` is what to run when somebody asks whether the product works. A demo that prints a
transcript but exercises nothing would be worse than no demo, so this test runs it and checks the
evidence it produces.
"""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DemoTest(unittest.TestCase):
    def test_demo_runs_every_view_and_exits_clean(self):
        proc = subprocess.run([sys.executable, "scripts/demo.py", "--demo"],
                              cwd=ROOT, capture_output=True, text=True, timeout=180)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        transcript = proc.stdout
        for view in ("health", "assess", "market", "structures", "slip", "target",
                     "jackpot", "explanations", "export", "journal", "page"):
            self.assertIn(view, transcript, view)
        self.assertIn("every view answered", transcript)

    def test_demo_transcript_carries_the_mode_and_caveats(self):
        proc = subprocess.run([sys.executable, "scripts/demo.py", "--demo"],
                              cwd=ROOT, capture_output=True, text=True, timeout=180)
        self.assertIn("synthetic", proc.stdout.lower())
        # The assess line reports how many caveats came back; zero would mean the limits vanished.
        assess_line = next(line for line in proc.stdout.splitlines() if line.startswith("assess"))
        self.assertNotIn("caveats=0", assess_line)

    def test_demo_does_not_write_to_the_real_journal(self):
        journal = ROOT / "var" / "assessments.jsonl"
        before = journal.read_text(encoding="utf-8") if journal.exists() else None
        subprocess.run([sys.executable, "scripts/demo.py", "--demo", "--quiet"],
                       cwd=ROOT, capture_output=True, text=True, timeout=180)
        after = journal.read_text(encoding="utf-8") if journal.exists() else None
        self.assertEqual(before, after, "the demonstration must not look like user activity")


if __name__ == "__main__":
    unittest.main()
