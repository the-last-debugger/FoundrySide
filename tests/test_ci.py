"""Guards for the CI configuration and repository hygiene.

The workflow is the one artefact that cannot be exercised from this environment — the GitHub API
and web host resolve to non-public addresses here — so a static check is the only way to stop it
drifting or disappearing silently. It verifies that the file exists and still runs the steps the
project depends on, rather than that GitHub accepted it.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "checks.yml"


class WorkflowTest(unittest.TestCase):
    def test_workflow_exists(self):
        self.assertTrue(WORKFLOW.exists(), "the CI workflow is missing")

    def test_workflow_runs_the_documented_steps(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        for required in ("actions/checkout", "actions/setup-python", "python-version: \"3.12\"",
                         "pip install -r requirements.txt", "unittest discover",
                         "scripts/collab_check.py", "scripts/verify_all.py --ci"):
            self.assertIn(required, text, f"workflow no longer runs: {required}")

    def test_workflow_is_bounded(self):
        # A workflow with no timeout can hang for the platform's default of six hours.
        self.assertIn("timeout-minutes:", WORKFLOW.read_text(encoding="utf-8"))

    def test_workflow_declares_read_only_permissions(self):
        self.assertIn("contents: read", WORKFLOW.read_text(encoding="utf-8"))


class EnvironmentTest(unittest.TestCase):
    def test_requirements_names_the_runtime_dependency(self):
        text = (ROOT / "requirements.txt").read_text(encoding="utf-8")
        self.assertIn("numpy", text)
        self.assertIn("3.12", text)


class RepositoryHygieneTest(unittest.TestCase):
    def test_the_corpus_is_not_tracked(self):
        # The corpus is third-party data; committing it would redistribute it and bloat the repo.
        import subprocess
        out = subprocess.run(["git", "ls-files", "research/data"], cwd=ROOT,
                             capture_output=True, text=True).stdout.strip()
        self.assertEqual(out, "", f"data files are tracked: {out[:200]}")

    def test_no_tracked_file_is_large(self):
        import subprocess
        files = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True,
                               text=True).stdout.splitlines()
        big = []
        for name in files:
            path = ROOT / name
            if path.is_file() and path.stat().st_size > 1_000_000:
                big.append((name, path.stat().st_size))
        self.assertEqual(big, [], f"tracked files over 1 MB: {big}")


if __name__ == "__main__":
    unittest.main()
