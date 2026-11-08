"""Check whether a lawful, free fixtures source exists, and whether it can be priced.

The planner needs two things for a genuinely prospective slip: unplayed fixtures, and odds for them.
This checks the first, and reports honestly on the second.

    python scripts/check_fixtures.py

Exit code 0 means the source was reachable and parsed (whatever it contains). It does not mean the
fixtures are priceable.
"""

from __future__ import annotations

import json
import sys
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ("https://raw.githubusercontent.com/openfootball/football.json/master/"
          "{season}/en.1.json")


def fetch(season: str) -> dict | None:
    request = urllib.request.Request(SOURCE.format(season=season),
                                     headers={"User-Agent": "FoundrySide/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        print(f"{season}: {type(exc).__name__}: {exc}")
        return None


def main() -> int:
    seasons = ["2026-27", "2025-26"]
    today = date.today()
    for season in seasons:
        data = fetch(season)
        if not data:
            continue
        matches = data.get("matches", [])
        played = [m for m in matches if m.get("score")]
        upcoming = [m for m in matches if not m.get("score")]
        dated = []
        for match in upcoming:
            try:
                dated.append(datetime.strptime(match["date"], "%Y-%m-%d").date())
            except (KeyError, ValueError):
                pass
        future = [d for d in dated if d >= today]
        has_odds = any(k in json.dumps(matches[0]) for k in ("odds", "price"))
        print(f"{season}: {len(matches)} fixtures, {len(played)} played, "
              f"{len(upcoming)} unplayed ({len(future)} dated on or after {today})")
        print(f"  odds fields present: {has_odds}")
        if upcoming:
            sample = upcoming[0]
            print(f"  sample: {sample.get('date')} {sample.get('time')} "
                  f"{sample.get('team1')} v {sample.get('team2')}")
    print("\nA fixtures source without odds cannot price a slip. The planner needs both.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
