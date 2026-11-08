"""Plan a slip on a card you type in.

The corpus has no prices for unplayed fixtures, and no lawful free feed was found (docs/FIXTURES_FEED.md).
So the user supplies what they can see — the fixtures and the prices on their screen — and the planner
does the arithmetic. That makes a plan genuinely prospective: it is written before kickoff.

    python scripts/plan_card.py card.json --stake 100 --target 10

card.json:
    {"fixtures": [
      {"home": "Arsenal", "away": "Leeds", "odds": [1.55, 4.2, 6.5]},
      {"home": "Bayern",  "away": "Mainz", "odds": [1.25, 6.0, 11.0]}
    ]}

Odds are home, draw, away. No stake is placed and nothing is sent anywhere.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import engine, planner  # noqa: E402


def load_card(path: Path) -> list[engine.Fixture]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    fixtures = []
    for i, item in enumerate(payload.get("fixtures", [])):
        prices = item.get("odds") or []
        if len(prices) != 3 or any(float(p) <= 1.0 for p in prices):
            raise SystemExit(f"fixture {i}: need three decimal odds above 1.0")
        fixtures.append(engine.Fixture(
            div=item.get("competition", "CARD"),
            date=item.get("date", "01/01/2000"),
            home=item["home"], away=item["away"],
            odds={"Avg": [float(p) for p in prices], "Max": [float(p) for p in prices]},
            totals={},
        ))
    if not fixtures:
        raise SystemExit("card has no fixtures")
    return fixtures


def main() -> int:
    parser = argparse.ArgumentParser(description="Plan a slip on a typed-in card")
    parser.add_argument("card", help="JSON file of fixtures and odds")
    parser.add_argument("--stake", type=float, default=100.0)
    parser.add_argument("--target", type=float, default=10.0)
    parser.add_argument("--tolerance", type=float, default=0.15)
    parser.add_argument("--max-legs", type=int, default=3)
    parser.add_argument("--json", action="store_true",
                        help="emit the plan as JSON so another surface can consume it")
    args = parser.parse_args()

    fixtures = load_card(Path(args.card))
    result = planner.plan(args.stake, args.target, args.tolerance, args.max_legs, fixtures)
    # The caveats the planner ships describe the corpus; on a typed card they would be wrong.
    result["caveats"] = [
        "Prices are the ones you entered. Nothing here verifies that they are live or obtainable.",
        "Probabilities are the market's own, multiplied. No model is applied beyond that product.",
        "This plan is written before kickoff, so it can be checked afterwards against the result.",
    ]

    if args.json:
        import json as _json
        print(_json.dumps(result, indent=2, default=str))
        return 0

    print(f"card: {len(fixtures)} fixtures | stake KSh {args.stake:.0f} | target {args.target:g}x")
    if not result["found"]:
        print(result["verdict"])
        return 0
    for option in result["options"]:
        legs = " + ".join(f"{l['fixture']} ({l['selection']} @{l['price']:.2f})"
                          for l in option["legs"])
        print(f"  {option['combined_price']:.2f}x  p={option['implied_probability']:.3f}  "
              f"net={option['net_if_won']:+.0f}  EV={option['expected_net']:+.2f}")
        print(f"    {legs}")
    print(result["caveats"][0])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
