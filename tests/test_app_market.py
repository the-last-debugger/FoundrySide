"""Guard: the market view must warn about the synthetic Max-row overround.

Taking the highest price for each outcome from different books produces a three-way book whose
implied probabilities sum to less than one. That looks like an arbitrage and is not one. The product
must say so wherever it shows per-book margins, because a negative margin displayed without the
warning is the most misleading number it could produce.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import demo_data, engine  # noqa: E402


class MarketCaveatTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = demo_data.synthetic_fixtures(3)[0]
        cls.view = engine.market_view(cls.fixture)

    def test_negative_margin_is_explained(self):
        margin = self.view["quotes"]["Max"]["overround"]
        joined = " ".join(self.view["caveats"]).lower()
        if margin < 0:
            self.assertIn("synthetic artefact", joined)
            self.assertIn("not an arbitrage", joined)
        else:
            # The caveat is unconditional, so it must be present either way.
            self.assertIn("max", joined)

    def test_caveat_mentions_executability(self):
        joined = " ".join(self.view["caveats"]).lower()
        self.assertTrue("not executable" in joined or "obtainable" in joined)

    def test_every_book_reports_its_own_margin(self):
        for name, quote in self.view["quotes"].items():
            self.assertIn("overround", quote, name)
            self.assertIn("implied", quote, name)
            self.assertAlmostEqual(sum(quote["implied"]), 1.0, places=6)

    def test_spread_is_labelled_observed(self):
        self.assertIn("observed", self.view["claims"]["best_vs_average"])


if __name__ == "__main__":
    unittest.main()
