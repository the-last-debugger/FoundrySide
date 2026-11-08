"""Tests for planning a typed-in card.

The card path is the only way to plan a genuinely unplayed fixture, so its input handling matters: a
BOM, a short odds list or a nonsensical price must fail clearly rather than produce a confident slip.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import plan_card  # noqa: E402


def write_card(payload: dict, *, bom: bool = False) -> Path:
    path = Path(tempfile.mkdtemp()) / "card.json"
    text = json.dumps(payload)
    path.write_text(("\ufeff" if bom else "") + text, encoding="utf-8")
    return path


class CardTest(unittest.TestCase):
    def test_reads_a_normal_card(self):
        path = write_card({"fixtures": [
            {"home": "A", "away": "B", "odds": [1.5, 4.0, 6.0]},
            {"home": "C", "away": "D", "odds": [2.0, 3.4, 3.6]},
        ]})
        fixtures = plan_card.load_card(path)
        self.assertEqual(len(fixtures), 2)
        self.assertEqual(fixtures[0].home, "A")

    def test_tolerates_a_byte_order_mark(self):
        # Windows editors add one; the parser must not treat it as a corrupt file.
        path = write_card({"fixtures": [{"home": "A", "away": "B", "odds": [1.5, 4.0, 6.0]}]},
                          bom=True)
        self.assertEqual(len(plan_card.load_card(path)), 1)

    def test_rejects_a_short_odds_list(self):
        path = write_card({"fixtures": [{"home": "A", "away": "B", "odds": [1.5, 4.0]}]})
        with self.assertRaises(SystemExit):
            plan_card.load_card(path)

    def test_rejects_a_price_at_or_below_one(self):
        path = write_card({"fixtures": [{"home": "A", "away": "B", "odds": [1.5, 4.0, 0.9]}]})
        with self.assertRaises(SystemExit):
            plan_card.load_card(path)

    def test_rejects_an_empty_card(self):
        path = write_card({"fixtures": []})
        with self.assertRaises(SystemExit):
            plan_card.load_card(path)

    def test_planned_card_options_are_priced_from_the_entered_odds(self):
        from app import planner
        path = write_card({"fixtures": [
            {"home": "A", "away": "B", "odds": [1.5, 4.0, 6.0]},
            {"home": "C", "away": "D", "odds": [1.6, 4.0, 5.5]},
        ]})
        fixtures = plan_card.load_card(path)
        result = planner.plan(100, 2.4, 0.1, 2, fixtures)
        self.assertTrue(result["found"], result["verdict"])
        for option in result["options"]:
            self.assertLess(option["expected_net"], 0.0)


if __name__ == "__main__":
    unittest.main()
