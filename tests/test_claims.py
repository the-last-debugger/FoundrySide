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

    def test_feature_screen_figures_agree_between_report_and_programme(self):
        screen = read("research/FEATURE_SCREEN.md")
        programme = read("docs/RESEARCH_PROGRAMME.md")
        self.assertIn("0.900", screen)
        self.assertIn("0.900", programme)
        self.assertNotIn("q = 0.83", programme)

    def test_readme_does_not_describe_the_initial_design_as_pending(self):
        readme = read("README.md")
        for stale in ("waiting on a decision about the first experiment", "69.4", "84.1"):
            self.assertNotIn(stale, readme, stale)
        self.assertIn("70.5", readme)

    def test_no_document_claims_the_corpus_is_exhausted(self):
        for name in ("docs/CONSOLIDATED_FINDINGS.md", "docs/RESEARCH_PROGRAMME.md"):
            text = read(name).lower()
            self.assertNotIn("eliminated every information source", text, name)

    def test_no_volatile_queue_count_is_quoted(self):
        # The queue count changes with every review round, so the narrative must not quote one.
        import re as _re
        for name in ("docs/CONSOLIDATED_FINDINGS.md", "README.md"):
            self.assertIsNone(_re.search(r"\b\d+ items awaiting review", read(name)), name)

    def test_current_experiment_count_and_screen_figures(self):
        readme = read("README.md")
        programme = read("docs/RESEARCH_PROGRAMME.md")
        self.assertIn("Fourteen experiments", readme)
        self.assertNotIn("Eleven experiments", readme)
        self.assertIn("0.900", readme)
        self.assertNotIn("0.876", readme)
        self.assertIn("23 generators", programme)

    def test_programme_reports_conditional_dispersion(self):
        programme = read("docs/RESEARCH_PROGRAMME.md")
        self.assertIn("1.064", programme)
        self.assertNotIn("1.015", programme)


if __name__ == "__main__":
    unittest.main()
