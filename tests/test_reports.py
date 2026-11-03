"""Every generated report must match the script that claims to have produced it.

This exists because it happened twice: a fix landed in the code while the committed report
still carried the previous numbers, and only a reviewer reading the two against each other
noticed.

The list is **discovered**, not maintained: any markdown in `research/` carrying a generator
stamp is checked. An earlier hand-maintained tuple silently stopped growing because the anchor
it was inserted against had moved, which is the same class of failure this test exists to catch.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research import report_stamp  # noqa: E402


def stamped_reports() -> list[Path]:
    return sorted(p for p in (ROOT / "research").glob("*.md")
                  if report_stamp.PATTERN.search(p.read_text(encoding="utf-8", errors="replace")))


class StampTest(unittest.TestCase):
    def test_at_least_the_core_reports_are_stamped(self):
        names = {p.name for p in stamped_reports()}
        for expected in ("PILOT_POWER.md", "PILOT_PREDICTIONS.md", "GAP_DIAGNOSIS.md",
                         "CALIBRATION_STUDY.md", "SEGMENT_STUDY.md", "RESIDUAL_STUDY.md",
                         "BOOK_DISAGREEMENT.md", "CONGESTION_STUDY.md", "DATA_AUDIT.md",
                         "MARKET_STRUCTURE.md", "RESULTS_T0_T1_T3.md", "LOGLOSS_POWER.md",
                         "CLUSTER_POWER.md"):
            self.assertIn(expected, names)

    def test_every_stamped_report_matches_its_generator(self):
        problems: list[str] = []
        for path in stamped_reports():
            problems.extend(report_stamp.verify(path))
        self.assertEqual(problems, [], "\n".join(problems))

    def test_a_missing_report_is_reported(self):
        problems = report_stamp.verify(ROOT / "research" / "NOT_A_REPORT.md")
        self.assertTrue(problems)

    def test_stamp_changes_when_the_script_changes(self):
        import tempfile

        d = Path(tempfile.mkdtemp())
        script = d / "gen.py"
        script.write_text("x = 1\n", encoding="utf-8")
        report = d / "OUT.md"
        report.write_text(report_stamp.stamp(script) + "\n# Report\n", encoding="utf-8")
        self.assertEqual(report_stamp.verify(report), [])
        script.write_text("x = 2\n", encoding="utf-8")
        self.assertTrue(report_stamp.verify(report))


if __name__ == "__main__":
    unittest.main()
