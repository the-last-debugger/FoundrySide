"""Guard the two implied-probability quantities in E25 against being conflated again.

The report previously showed 61.1% in one table and 61.5% in the prose for the same band, and an
expected-value figure computed from a rounded price. Both were arithmetically correct and
definitionally different, which is the kind of error that survives review: each number is defensible
in isolation. These tests check the report's internal consistency instead of trusting it.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "research" / "STAKE_STRUCTURES.md"
BAND_ROW = re.compile(r"^\| \d\.\d–\d\.\d \|")


class ReportConsistencyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = REPORT.read_text(encoding="utf-8")
        # Only the main table's rows have nine columns; the variance table has two and would
        # otherwise index out of range.
        cls.rows = [[c.strip() for c in line.strip("|").split("|")]
                    for line in cls.text.splitlines()
                    if BAND_ROW.match(line) and len(line.strip("|").split("|")) == 9]

    def test_band_rows_exist_with_the_expected_columns(self):
        self.assertEqual(len(self.rows), 5)
        for cells in self.rows:
            self.assertEqual(len(cells), 9, cells)

    def test_table_carries_both_implied_quantities(self):
        header = next(line for line in self.text.splitlines() if line.startswith("| Odds band |"))
        self.assertIn("Mean implied", header)
        self.assertIn("Implied at median", header)

    def test_median_prices_are_reported_to_two_decimals(self):
        for cells in self.rows:
            self.assertRegex(cells[2], r"^\d\.\d{2}$", f"median price: {cells[2]}")

    def test_realised_ev_matches_the_row_own_price_and_rate(self):
        # Rounded inputs mean a small tolerance is legitimate; a conflated definition would move the
        # figure by whole percentage points, which is what this check exists to catch.
        for cells in self.rows:
            price = float(cells[2])
            realised = float(cells[7].split("%")[0]) / 100.0
            reported = float(cells[8].rstrip("%")) / 100.0
            self.assertAlmostEqual(realised * price - 1.0, reported, delta=0.006, msg=str(cells))

    def test_worked_example_uses_the_computed_price(self):
        section = self.text[self.text.index("What the realised-EV column says"):]
        section = section[:section.index("## The answer")]
        self.assertIn("median price 1.56", section)
        self.assertNotIn("1.55", section)

    def test_calibration_section_compares_against_the_mean(self):
        section = self.text[self.text.index("Do the realised rates match"):]
        cut = section.index("What the realised-EV") if "What the realised-EV" in section else len(section)
        self.assertIn("mean implied", section[:cut])


if __name__ == "__main__":
    unittest.main()
