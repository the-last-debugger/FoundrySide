"""Tests for the corpus fetcher: no network, no surprises.

The fetcher is the only component in the repository that talks to an external host, so its behaviour
is pinned here with a stub: it records provenance, it does not overwrite unless asked, and it reports
failures instead of raising.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import fetch_corpus  # noqa: E402

SAMPLE = "Div,Date,HomeTeam,AwayTeam,FTHG,FTAG,MaxCH,AvgCH\nE0,01/08/2023,A,B,1,0,2.5,2.4\n"


class FetcherTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self._orig_data = fetch_corpus.DATA
        self._orig_prov = fetch_corpus.PROVENANCE
        self._orig_fetch = fetch_corpus.fetch
        fetch_corpus.DATA = self.tmp
        fetch_corpus.PROVENANCE = self.tmp / "PROVENANCE.json"

    def tearDown(self):
        fetch_corpus.DATA = self._orig_data
        fetch_corpus.PROVENANCE = self._orig_prov
        fetch_corpus.fetch = self._orig_fetch

    def run_fetcher(self, argv):
        old_argv = sys.argv
        sys.argv = ["fetch_corpus.py", "--delay", "0"] + argv
        try:
            return fetch_corpus.main()
        finally:
            sys.argv = old_argv

    def test_writes_file_and_provenance(self):
        fetch_corpus.fetch = lambda season, league, timeout=30: SAMPLE
        code = self.run_fetcher(["--seasons", "2324", "--leagues", "E0"])
        self.assertEqual(code, 0)
        self.assertTrue((self.tmp / "E0_2324.csv").exists())
        record = json.loads((self.tmp / "PROVENANCE.json").read_text(encoding="utf-8"))
        self.assertEqual(record["source"], "football-data.co.uk")
        self.assertEqual(record["total_fixtures"], 1)
        self.assertIn("P-03", record["licence"])
        self.assertIn("retrieved_utc", record)

    def test_does_not_overwrite_without_force(self):
        target = self.tmp / "E0_2324.csv"
        target.write_text("existing", encoding="latin-1")
        called = {"n": 0}

        def fake(season, league, timeout=30):
            called["n"] += 1
            return SAMPLE

        fetch_corpus.fetch = fake
        self.run_fetcher(["--seasons", "2324", "--leagues", "E0"])
        self.assertEqual(called["n"], 0, "existing files must not be re-downloaded by default")
        self.assertEqual(target.read_text(encoding="latin-1"), "existing")

    def test_missing_file_is_recorded_not_raised(self):
        fetch_corpus.fetch = lambda season, league, timeout=30: None
        code = self.run_fetcher(["--seasons", "2324", "--leagues", "E0"])
        self.assertEqual(code, 1)
        record = json.loads((self.tmp / "PROVENANCE.json").read_text(encoding="utf-8"))
        self.assertEqual(record["files"][0]["status"], "missing")

    def test_empty_response_is_not_saved(self):
        fetch_corpus.fetch = lambda season, league, timeout=30: ""
        self.run_fetcher(["--seasons", "2324", "--leagues", "E0"])
        self.assertFalse((self.tmp / "E0_2324.csv").exists())


if __name__ == "__main__":
    unittest.main()
