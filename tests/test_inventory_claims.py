"""Guard: no user-obtainability claim may enter the price-inventory report.

The claim "the best quoted price beats the average" is a property of the quotes. The corpus has no
timestamps, no account terms and no limits, so it cannot support "a user could get this price" or
"shopping improves what a user pays". That overclaim has now been corrected three times — once in the
report, once in the generator, and once in the generator again after the first fix missed strings — so
it gets a test rather than another careful edit.
"""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "research" / "price_inventory.py"
REPORT = ROOT / "research" / "PRICE_INVENTORY.md"

# Phrases that assert obtainability, executability or user benefit from quoted snapshots.
FORBIDDEN = (
    "tradeable",
    "can get a better price",
    "price-shopping case",
    "shopping improves the price",
    "improves the price a user pays",
    "user could have got",
)


class PriceInventoryClaimTest(unittest.TestCase):
    def test_generator_makes_no_obtainability_claim(self):
        text = GENERATOR.read_text(encoding="utf-8").lower()
        for phrase in FORBIDDEN:
            self.assertNotIn(phrase.lower(), text,
                             f"generator asserts obtainability: {phrase!r}")

    def test_report_makes_no_obtainability_claim(self):
        text = REPORT.read_text(encoding="utf-8").lower()
        for phrase in FORBIDDEN:
            self.assertNotIn(phrase.lower(), text,
                             f"report asserts obtainability: {phrase!r}")

    def test_report_states_the_limit_where_the_number_appears(self):
        # The caveat must sit with the claim, not only in a later section.
        text = REPORT.read_text(encoding="utf-8")
        idx = text.find("6.51%")
        self.assertGreater(idx, 0, "the 6.51% figure is missing")
        window = text[idx:idx + 600].lower()
        self.assertTrue(
            "not a demonstrated obtainable price" in window
            or "not established" in window
            or "quoted-price difference" in window,
            "the 6.51% claim is not qualified where it appears",
        )


if __name__ == "__main__":
    unittest.main()
