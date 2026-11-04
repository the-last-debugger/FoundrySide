"""The review digest must be current.

`docs/REVIEW_DIGEST.md` is generated from the queue, and the queue changes every review round. A
generated document that nothing regenerates drifts silently — the same failure the report stamps
exist to prevent for research artefacts. This test regenerates the digest and fails if the
committed file differs.
"""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIGEST = ROOT / "docs" / "REVIEW_DIGEST.md"


class DigestTest(unittest.TestCase):
    def test_digest_is_current(self):
        before = DIGEST.read_text(encoding="utf-8")
        proc = subprocess.run([sys.executable, str(ROOT / "scripts" / "review_digest.py")],
                              cwd=str(ROOT), capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        after = DIGEST.read_text(encoding="utf-8")
        if before != after:
            self.fail("docs/REVIEW_DIGEST.md is stale: run `python scripts/review_digest.py` "
                      "and commit the result")

    def test_digest_reports_the_queue_size(self):
        # Guards against generating an empty file if the queue parser breaks.
        digest = DIGEST.read_text(encoding="utf-8")
        self.assertIn("rows:", digest)
        self.assertIn("accepted", digest)


if __name__ == "__main__":
    unittest.main()
