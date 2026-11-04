"""Guards for the two error classes that recurred most often in this project.

1. **Free-form headers.** Six sponsor entries arrived with placeholder stamps, no stamp, or
   multi-word kinds. Each one used to become a parser error needing a hand-written acknowledgement,
   which is a cycle of work for a formatting variation. The parser now recovers fields instead, and
   these tests pin that.

2. **Quoted revisions that do not exist.** Twice a bridge entry or queue row carried a SHA that was
   invented or rewritten away by a rebase. A token in a revision context must resolve.
"""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from collab_note import parse_entries  # noqa: E402

THREAD = ROOT / "docs" / "COLLAB" / "THREAD.md"

# A hash-shaped token near a word that means "revision": `abc1234`, revision abc1234, commit abc1234.
REVISION_CONTEXT_RE = re.compile(
    r"(?:revision|revisions reviewed|commit|ref)\s*:?\s*`?([0-9a-f]{7,40})`?", re.IGNORECASE)


def thread_text() -> str:
    return THREAD.read_text(encoding="utf-8")


class LooseHeaderTest(unittest.TestCase):
    def parse(self, header: str) -> dict:
        path = Path(tempfile.mkdtemp()) / "THREAD.md"
        path.write_text(header + "\nBody.\n", encoding="utf-8")
        entries = parse_entries(path)
        self.assertEqual(len(entries), 1, "a free-form header must still become an entry")
        return entries[0]

    def test_placeholder_stamp_is_recovered(self):
        e = self.parse("### 2026-11-04T12:xx:xxZ · sponsor · evaluation request")
        self.assertEqual(e["author"], "sponsor")
        self.assertIn("2026-11-04", e["stamp"])

    def test_header_without_a_stamp_is_not_absorbed(self):
        e = self.parse("### Sponsor follow-up — Track B bootstrap denominator")
        self.assertEqual(e["author"], "sponsor")
        self.assertEqual(e["kind"], "note")
        self.assertTrue(e.get("loose"))

    def test_multi_word_kind_resolves_to_a_known_kind(self):
        e = self.parse("### 2026-11-04 · sponsor · workflow bottleneck review and operating direction")
        self.assertEqual(e["kind"], "direction")

    def test_date_and_author_never_become_the_kind(self):
        e = self.parse("### 2026-11-04T12:xx:xxZ · sponsor · evaluation request")
        self.assertIn(e["kind"], {"note", "response", "review"})
        self.assertNotIn("2026", e["kind"])
        self.assertNotEqual(e["kind"], "sponsor")

    def test_every_heading_in_the_real_thread_parses(self):
        headings = [line for line in thread_text().splitlines() if line.startswith("### ")]
        parsed = parse_entries()
        self.assertGreaterEqual(len(parsed), len(headings) - 0,
                                "every heading must become an entry, not body text")


class RevisionTokenTest(unittest.TestCase):
    def test_quoted_revisions_exist(self):
        tokens = {m.group(1) for m in REVISION_CONTEXT_RE.finditer(thread_text())}
        self.assertTrue(tokens, "no revision tokens found; the pattern may be stale")
        # One historical entry quoted a revision that was invented when it was written. The thread
        # is append-only, so the entry is preserved and a later correction entry names the real
        # commit; the token is exempted here with that reason rather than silently ignored.
        # Two distinct historical problems, both preserved on an append-only thread:
        #   - one invented revision, later corrected by an entry naming the real commit;
        #   - several revisions that were rewritten by rebases, so the SHA is no longer in history
        #     even though the content it described is. Reachability is the test, not existence:
        #     a dangling object passes cat-file locally and fails in a fresh clone, which is
        #     exactly how this guard false-passed before.
        historical = {
            "6a9f0e4": "invented in the bogey-team entry; corrected by the entry naming fc8b0ac",
            "09e562e": "rewritten by a rebase; the same change is in current history",
            "1d0f3dd": "rewritten by a rebase; the same change is in current history",
            "49701af": "rewritten by a rebase; the same change is in current history",
            "4db2627": "rewritten by a rebase; the same change is in current history",
            "88bb674": "rewritten by a rebase; the same change is in current history",
            "a867e76": "rewritten by a rebase; the same change is in current history",
        }
        missing = []
        for sha in sorted(tokens - set(historical)):
            exists = subprocess.run(["git", "cat-file", "-e", f"{sha}^{{commit}}"],
                                    cwd=ROOT, capture_output=True)
            if exists.returncode != 0:
                missing.append(sha)
                continue
            reachable = subprocess.run(["git", "merge-base", "--is-ancestor", sha, "HEAD"],
                                       cwd=ROOT, capture_output=True)
            if reachable.returncode != 0:
                missing.append(f"{sha} (not reachable from HEAD)")
        self.assertEqual(missing, [], f"bridge quotes revisions that do not exist: {missing}")


if __name__ == "__main__":
    unittest.main()
