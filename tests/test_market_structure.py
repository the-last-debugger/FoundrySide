"""Parser guards for the market-structure analysis.

A NaN or infinite price passes a `<= 1.0` check — NaN compares false against everything —
and then contaminates any mean it touches. These tests exist so the guard is proven rather
than assumed.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research import market_structure  # noqa: E402

BASE = {
    "FTHG": "2", "FTAG": "1",
    "PSCH": "1.90", "PSCD": "3.40", "PSCA": "3.80",
    "PC>2.5": "1.95", "PC<2.5": "1.90",
}


def row(**over):
    r = dict(BASE)
    r.update(over)
    return r


class ParseTest(unittest.TestCase):
    def test_valid_row_parses(self):
        self.assertIsNotNone(market_structure.parse(row()))

    def test_missing_field_is_rejected(self):
        self.assertIsNone(market_structure.parse(row(**{"PSCH": ""})))
        self.assertIsNone(market_structure.parse(row(**{"FTHG": ""})))

    def test_nan_is_rejected(self):
        for field in ("PSCH", "PSCD", "PSCA", "PC>2.5", "PC<2.5"):
            self.assertIsNone(market_structure.parse(row(**{field: "nan"})), field)

    def test_infinities_are_rejected(self):
        for field in ("PSCH", "PC>2.5"):
            self.assertIsNone(market_structure.parse(row(**{field: "inf"})), field)
            self.assertIsNone(market_structure.parse(row(**{field: "-inf"})), field)

    def test_below_unit_odds_are_rejected(self):
        self.assertIsNone(market_structure.parse(row(**{"PC>2.5": "1.00"})))
        self.assertIsNone(market_structure.parse(row(**{"PSCH": "0.5"})))


class SummaryTest(unittest.TestCase):
    def test_a_single_row_summarises_cleanly(self):
        s = market_structure.summarise([market_structure.parse(row())])
        self.assertEqual(int(s["n"]), 1)
        self.assertGreater(s["over_margin"], 0)
        self.assertTrue(0.0 <= s["over_favourite_accuracy"] <= 1.0)


if __name__ == "__main__":
    unittest.main()
