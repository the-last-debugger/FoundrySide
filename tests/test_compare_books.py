"""Tests for the bookmaker comparison.

The comparison is the lawful substitute for scraping (docs/ODDS_SOURCES.md), so what matters is that it
reads the card correctly, identifies the cheapest book by margin, and never presents the synthetic
best-per-outcome price as an obtainable one.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import compare_books as cb  # noqa: E402

CARD = """Arsenal | Leeds | 1.55 | 4.20 | 6.50 | Betika
Arsenal | Leeds | 1.50 | 4.30 | 6.80 | Odibets
Arsenal | Leeds | 1.48 | 4.10 | 7.00 | Mozzart
"""


class ParseTest(unittest.TestCase):
    def test_groups_by_fixture_and_book(self):
        card = cb.parse(CARD)
        self.assertEqual(list(card), ["Arsenal v Leeds"])
        self.assertEqual(set(card["Arsenal v Leeds"]), {"Betika", "Odibets", "Mozzart"})

    def test_a_nameless_line_gets_a_book_label(self):
        card = cb.parse("A | B | 2.0 | 3.4 | 3.6\n")
        self.assertEqual(len(card["A v B"]), 1)

    def test_rejects_a_short_line(self):
        with self.assertRaises(ValueError):
            cb.parse("A | B | 2.0\n")

    def test_rejects_a_price_at_or_below_one(self):
        with self.assertRaises(ValueError):
            cb.parse("A | B | 2.0 | 3.4 | 0.9\n")

    def test_rejects_an_empty_card(self):
        with self.assertRaises(ValueError):
            cb.parse("\n\n")


class CompareTest(unittest.TestCase):
    def setUp(self):
        self.rows = cb.compare(cb.parse(CARD))

    def test_best_price_per_outcome_is_the_maximum(self):
        best = self.rows[0]["best"]
        self.assertAlmostEqual(best["H"]["price"], 1.55)
        self.assertEqual(best["H"]["book"], "Betika")
        self.assertAlmostEqual(best["D"]["price"], 4.30)
        self.assertEqual(best["D"]["book"], "Odibets")
        self.assertAlmostEqual(best["A"]["price"], 7.00)
        self.assertEqual(best["A"]["book"], "Mozzart")

    def test_cheapest_book_is_the_lowest_margin(self):
        # Betika's prices imply the smallest margin, so it is the cheapest book here.
        self.assertEqual(self.rows[0]["single_book_best"], "Betika")

    def test_margins_match_the_prices(self):
        for books in self.rows[0]["books"].values():
            expected = sum(1 / p for p in books["odds"]) - 1
            self.assertAlmostEqual(books["margin"], expected, places=9)

    def test_the_synthetic_best_is_not_a_single_book(self):
        # No book offers all three best prices; the report says so.
        best = self.rows[0]["best"]
        books = set()
        for outcome in ("H", "D", "A"):
            books.add(best[outcome]["book"])
        self.assertGreater(len(books), 1)


if __name__ == "__main__":
    unittest.main()
