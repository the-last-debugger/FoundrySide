"""Every generated report must match the script that claims to have produced it.

This exists because it happened twice: a stability fix landed in the code while the
committed report still carried the previous numbers, and only a reviewer reading the two
against each other noticed.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research import report_stamp  # noqa: E402

REPORTS = (
    "RESULTS_T0_T1_T3.md",
    "LOGLOSS_POWER.md",
    "CLUSTER_POWER.md",
    "PILOT_POWER.md",
    "PILOT_PREDICTIONS.md",
    "MARKET_STRUCTURE.md",
    "GAP_DIAGNOSIS.md",
    "CALIBRATION_STUDY.md",
)


class StampTest(unittest.TestCase):
    def test_reports_match_their_generators(self):
        problems: list[str] = []
        for name in REPORTS:
            problems.extend(report_stamp.verify(ROOT / "research" / name))
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
