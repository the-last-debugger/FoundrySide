"""Tests for manifest timestamp preservation.

The defect this guards against was live: regenerating against byte-identical data rewrote all
eighty manifest rows with the current clock, so every rerun looked like a data change and the
reports that quote the manifest hash churned with it.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research"))

from analyse import pick_stamp  # noqa: E402


class StampTest(unittest.TestCase):
    def test_unchanged_hash_keeps_the_first_seen_time(self):
        previous = {"E0_2021.csv": ("abc123", "2026-11-03T14:58:11Z")}
        self.assertEqual(pick_stamp(previous, "E0_2021.csv", "abc123", "2026-11-04T00:00:00Z"),
                         "2026-11-03T14:58:11Z")

    def test_changed_hash_takes_the_new_time(self):
        previous = {"E0_2021.csv": ("abc123", "2026-11-03T14:58:11Z")}
        self.assertEqual(pick_stamp(previous, "E0_2021.csv", "def456", "2026-11-04T00:00:00Z"),
                         "2026-11-04T00:00:00Z")

    def test_new_file_takes_the_new_time(self):
        self.assertEqual(pick_stamp({}, "E1_2021.csv", "abc", "2026-11-04T00:00:00Z"),
                         "2026-11-04T00:00:00Z")

    def test_missing_previous_entry_is_not_an_error(self):
        self.assertEqual(pick_stamp({"other": ("h", "t")}, "E0_2021.csv", "abc", "now"), "now")


if __name__ == "__main__":
    unittest.main()
