"""Compare bookmakers from a pasted card.

The sites do not serve prices to a fetch (docs/ODDS_SOURCES.md), so the user supplies what they can see
and this does the comparison: per fixture, per outcome, the best price and who offers it, plus each
site's margin. That answers "which site should I use for this match" without scraping anything.

    python scripts/compare_books.py card.txt

Card format, one line per site per fixture — the site name is optional:

    Arsenal | Leeds | 1.55 | 4.20 | 6.50 | Betika
    Arsenal | Leeds | 1.50 | 4.30 | 6.80 | Odibets

A line with four fields is treated as a single unnamed book.
"""

from __future__ import annotations

import sys
from pathlib import Path

OUTCOMES = ("H", "D", "A")


def parse(text: str) -> dict:
    """Return {fixture: {book: [h, d, a]}} preserving insertion order."""
    card: dict[str, dict[str, list[float]]] = {}
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 5:
            raise ValueError(f"line {number}: need at least home, away and three prices")
        home, away = parts[0], parts[1]
        try:
            odds = [float(p) for p in parts[2:5]]
        except ValueError as exc:
            raise ValueError(f"line {number}: prices must be numbers ({exc})") from exc
        if any(o <= 1.0 for o in odds):
            raise ValueError(f"line {number}: every price must be above 1.0")
        book = parts[5] if len(parts) > 5 and parts[5] else f"book{number}"
        card.setdefault(f"{home} v {away}", {})[book] = odds
    if not card:
        raise ValueError("no fixtures found")
    return card


def overround(odds: list[float]) -> float:
    return sum(1 / o for o in odds) - 1


def compare(card: dict) -> list[dict]:
    rows = []
    for fixture, books in card.items():
        best = {}
        for i, outcome in enumerate(OUTCOMES):
            best[outcome] = max(((prices[i], book) for book, prices in books.items()),
                                key=lambda x: x[0])
        rows.append({
            "fixture": fixture,
            "books": {book: {"odds": prices, "margin": overround(prices)}
                      for book, prices in books.items()},
            "best": {o: {"price": best[o][0], "book": best[o][1]} for o in OUTCOMES},
            "single_book_best": min(books, key=lambda b: overround(books[b])),
        })
    return rows


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    path = Path(sys.argv[1])
    card = parse(path.read_text(encoding="utf-8-sig"))
    rows = compare(card)

    for row in rows:
        print(f"\n{row['fixture']}")
        for book, data in row["books"].items():
            prices = " / ".join(f"{p:.2f}" for p in data["odds"])
            print(f"  {book:<12} {prices}   margin {data['margin']*100:+.2f}%")
        parts = [f"{o}: {row['best'][o]['price']:.2f} ({row['best'][o]['book']})"
                 for o in OUTCOMES]
        print("  best per outcome -> " + ", ".join(parts))

    print("\nBest per outcome across sites is a synthetic price: no single book offers all three. "
          "The lowest margin\nis the cheapest book overall, which is a real, checkable comparison.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
