"""The consolidated document's headline numbers must match the reports it cites.

`docs/CONSOLIDATED_FINDINGS.md` is the first thing a reviewer reads and the last thing to be
regenerated. If a report changes and the summary does not, the summary keeps asserting numbers
that no longer exist anywhere else. These tests pin the flagship figures to their sources.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


class ClaimsTest(unittest.TestCase):
    def test_baseline_and_dependence_figures(self):
        results = read("research/RESULTS_T0_T1_T3.md")
        summary = read("docs/CONSOLIDATED_FINDINGS.md")
        for figure in ("53.3", "1.49"):
            self.assertIn(figure, results, figure)
            self.assertIn(figure, summary, figure)

    def test_model_deficit_and_auc(self):
        gap = read("research/GAP_DIAGNOSIS.md")
        residual = read("research/RESIDUAL_STUDY.md")
        summary = read("docs/CONSOLIDATED_FINDINGS.md")
        self.assertIn("0.0246", gap)
        self.assertIn("0.0246", summary)
        self.assertIn("0.5623", residual)
        self.assertIn("0.5623", summary)
        self.assertIn("0.6073", residual)
        self.assertIn("0.6073", summary)

    def test_calibration_result(self):
        study = read("research/CALIBRATION_STUDY.md")
        summary = read("docs/CONSOLIDATED_FINDINGS.md")
        self.assertIn("0.0114", study)
        self.assertIn("0.0114", summary)

    def test_power_and_crossing_interval(self):
        power = read("research/PILOT_POWER.md")
        summary = read("docs/CONSOLIDATED_FINDINGS.md")
        self.assertIn("70.5", power)
        self.assertIn("70.5", summary)

    def test_favourite_longshot_verdict(self):
        test = read("research/FL_TEST.md")
        summary = read("docs/CONSOLIDATED_FINDINGS.md")
        self.assertIn("not supported", test.lower())
        self.assertIn("not supported", summary.lower())


if __name__ == "__main__":
    unittest.main()
