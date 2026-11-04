"""Tests for the audit's price classifier.

The earlier audit checked only the over side, so a row with a valid over price and a broken under
price counted as complete. These tests pin both sides and the non-finite cases.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research import data_audit  # noqa: E402


def row(**over):
    r = {"PC>2.5": "1.95", "PC<2.5": "1.90"}
    r.update(over)
    return r


class ClassifyTest(unittest.TestCase):
    def test_complete_pair_is_ok(self):
        self.assertEqual(data_audit.classify_price(row()), "ok")

    def test_either_side_missing_is_missing(self):
        self.assertEqual(data_audit.classify_price(row(**{"PC>2.5": ""})), "missing")
        self.assertEqual(data_audit.classify_price(row(**{"PC<2.5": ""})), "missing")
        self.assertEqual(data_audit.classify_price({"PC>2.5": "1.9"}), "missing")

    def test_non_finite_is_invalid_on_either_side(self):
        for field in ("PC>2.5", "PC<2.5"):
            for value in ("nan", "inf", "-inf"):
                self.assertEqual(data_audit.classify_price(row(**{field: value})), "invalid",
                                 f"{field}={value}")

    def test_below_unit_is_invalid_on_either_side(self):
        self.assertEqual(data_audit.classify_price(row(**{"PC>2.5": "1.00"})), "invalid")
        self.assertEqual(data_audit.classify_price(row(**{"PC<2.5": "0.5"})), "invalid")

    def test_blank_or_absent_is_missing(self):
        self.assertEqual(data_audit.classify_price(row(**{"PC<2.5": ""})), "missing")
        self.assertEqual(data_audit.classify_price(row(**{"PC<2.5": "   "})), "missing")
        self.assertEqual(data_audit.classify_price({"PC>2.5": "1.9"}), "missing")

    def test_present_but_unparseable_is_invalid(self):
        # A present n/a is a broken value, not an absence.
        self.assertEqual(data_audit.classify_price(row(**{"PC<2.5": "n/a"})), "invalid")
        self.assertEqual(data_audit.classify_price(row(**{"PC>2.5": "-"})), "invalid")


if __name__ == "__main__":
    unittest.main()
