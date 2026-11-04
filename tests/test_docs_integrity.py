"""Documents must not cite things that do not exist.

Two failure modes this catches, both cheap and both embarrassing in a repository whose whole
argument is about provenance:

- a path cited in a summary that was renamed or never created;
- a review row pointing at a revision that is not in the history.

It does not check that a cited claim is *true* — the claims test covers the headline numbers. This
checks only that the references resolve.
"""

from __future__ import annotations

import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOCS = ("README.md", "docs/CONSOLIDATED_FINDINGS.md", "docs/RESEARCH_PROGRAMME.md",
        "docs/TRACK_B_DESIGN.md", "docs/PREREG-FL.md")

# Backticked repository paths, e.g. `research/GAP_DIAGNOSIS.md`.
PATH_RE = re.compile(r"`((?:research|docs|scripts|tests)/[A-Za-z0-9_./-]+\.(?:md|py|csv))`")
SHA_RE = re.compile(r"\| ([0-9a-f]{7,40}) \|")


def doc_text(name: str) -> str:
    return (ROOT / name).read_text(encoding="utf-8")


class ReferencesTest(unittest.TestCase):
    def test_cited_paths_exist(self):
        missing = []
        for name in DOCS:
            for path in set(PATH_RE.findall(doc_text(name))):
                if not (ROOT / path).exists():
                    missing.append(f"{name} -> {path}")
        self.assertEqual(missing, [], "\n".join(missing))

    def test_queue_revisions_exist(self):
        shallow = subprocess.run(["git", "rev-parse", "--is-shallow-repository"],
                                 cwd=ROOT, capture_output=True, text=True).stdout.strip()
        if shallow == "true":
            self.skipTest("shallow clone: revision history is absent, so this check is vacuous. "
                          "CI checks out with fetch-depth: 0 for this reason.")
        queue = doc_text("docs/COLLAB/REVIEW_QUEUE.md")
        shas = set(SHA_RE.findall(queue))
        self.assertTrue(shas, "no revisions found in the queue; the pattern may be stale")
        missing = []
        for sha in sorted(shas):
            proc = subprocess.run(["git", "cat-file", "-e", f"{sha}^{{commit}}"],
                                  cwd=ROOT, capture_output=True)
            if proc.returncode != 0:
                missing.append(sha)
        self.assertEqual(missing, [], f"queue cites revisions not in history: {missing}")

    def test_queue_ids_are_unique(self):
        queue = doc_text("docs/COLLAB/REVIEW_QUEUE.md")
        ids = re.findall(r"\| (RQ-\d+) \|", queue)
        duplicates = {i for i in ids if ids.count(i) > 1}
        self.assertEqual(duplicates, set(), f"duplicate rows: {sorted(duplicates)}")

    def test_every_queue_row_has_a_state(self):
        states = {"draft", "ready_for_review", "changes_requested", "accepted"}
        rows = [line for line in doc_text("docs/COLLAB/REVIEW_QUEUE.md").splitlines()
                if line.startswith("| RQ-")]
        self.assertTrue(rows)
        for line in rows:
            cells = [c.strip() for c in line.strip("|").split("|")]
            self.assertIn(cells[4], states, f"unexpected state in: {line[:60]}")

    def test_every_report_is_cited_by_the_summary(self):
        summary = doc_text("docs/CONSOLIDATED_FINDINGS.md")
        missing = [p.name for p in sorted((ROOT / "research").glob("*.md"))
                   if p.name not in summary]
        self.assertEqual(missing, [], f"reports absent from the source map: {missing}")

    def test_documented_generator_count_matches_the_sweep(self):
        # A hand-written count drifted from the real inventory twice (23 vs 25). The number in the
        # programme must equal the number of generators the sweep actually runs.
        sys.path.insert(0, str(ROOT / "scripts"))
        from repro_sweep import GENERATORS
        programme = doc_text("docs/RESEARCH_PROGRAMME.md")
        lines = [l for l in programme.splitlines() if "generator" in l.lower()]
        self.assertTrue(lines, "the programme should state the sweep size")
        self.assertTrue(any(str(len(GENERATORS)) in l for l in lines),
                        f"no line records {len(GENERATORS)} generators")

    def test_sweep_docstring_does_not_claim_a_second_run_check(self):
        text = (ROOT / "scripts" / "repro_sweep.py").read_text(encoding="utf-8")
        body = text.split('"""')[1] if '"""' in text else text
        self.assertNotIn("second run", body.replace("second-run", "second_run").lower()
                         if False else body.lower())


if __name__ == "__main__":
    unittest.main()
