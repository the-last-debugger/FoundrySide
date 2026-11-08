"""A mixed-market slip for a small stake: what the corpus can price, and what it cannot.

The corpus holds final results, half-time scores and 1X2 / over-under 2.5 prices. It does **not** hold
prices for half-time markets or both-teams-to-score. So this builds a slip that mixes markets, prices the
recorded ones from the market and the derived ones from observed frequencies plus a stated margin, and
reports what the combination would have done historically.

It is a simulation on recorded fixtures. It is not a Betika price and cannot be placed.

    python research/mixed_slip.py --stake 30 --target 30
"""

from __future__ import annotations

import argparse
import csv
import glob
import itertools
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "research" / "data"

# Margins applied to markets whose prices the corpus does not record. A book's margin on these is
# typically larger than on the main lines.
DERIVED_MARGIN = 0.08


def load() -> list[dict]:
    rows = []
    for path in sorted(glob.glob(str(DATA / "*.csv"))):
        with open(path, encoding="latin-1") as handle:
            for raw in csv.DictReader(handle):
                try:
                    hg, ag = int(raw["FTHG"]), int(raw["FTAG"])
                    hhg, hag = int(raw["HTHG"]), int(raw["HTAG"])
                except (KeyError, TypeError, ValueError):
                    continue
                if raw.get("FTR") not in ("H", "D", "A"):
                    continue
                rows.append({
                    "date": raw.get("Date", ""), "div": raw.get("Div", ""),
                    "home": raw.get("HomeTeam", ""), "away": raw.get("AwayTeam", ""),
                    "hg": hg, "ag": ag, "hhg": hhg, "hag": hag,
                    "ftr": raw["FTR"],
                    "avg_h": raw.get("AvgCH"), "avg_d": raw.get("AvgCD"), "avg_a": raw.get("AvgCA"),
                    "avg_o": raw.get("Avg>2.5"), "avg_u": raw.get("Avg<2.5"),
                })
    return rows


def frequencies(rows: list[dict]) -> dict:
    n = len(rows)
    def rate(pred):
        return sum(1 for r in rows if pred(r)) / n
    return {
        "FT home": rate(lambda r: r["ftr"] == "H"),
        "FT draw": rate(lambda r: r["ftr"] == "D"),
        "FT away": rate(lambda r: r["ftr"] == "A"),
        "HT draw": rate(lambda r: r["hhg"] == r["hag"]),
        "HT over 0.5": rate(lambda r: r["hhg"] + r["hag"] > 0.5),
        "HT over 1.5": rate(lambda r: r["hhg"] + r["hag"] > 1.5),
        "GG": rate(lambda r: r["hg"] > 0 and r["ag"] > 0),
        "NG": rate(lambda r: not (r["hg"] > 0 and r["ag"] > 0)),
        "FT over 2.5": rate(lambda r: r["hg"] + r["ag"] > 2.5),
        "FT under 2.5": rate(lambda r: r["hg"] + r["ag"] < 2.5),
    }


def price_from_probability(p: float, margin: float = 0.0) -> float:
    return 1.0 / (p * (1.0 + margin))


def latest_day(rows: list[dict]) -> tuple[str, list[dict]]:
    from datetime import datetime
    dated = []
    for r in rows:
        try:
            dated.append((datetime.strptime(r["date"], "%d/%m/%Y"), r))
        except (ValueError, TypeError):
            pass
    if not dated:
        return "", []
    newest = max(d for d, _ in dated)
    return newest.strftime("%d/%m/%Y"), [r for d, r in dated if d == newest]


def legs_for(fixture: dict, freq: dict) -> list[dict]:
    """Every priced selection available on a fixture, with its probability and price."""
    legs = []
    for name, key, prob in (
        ("1X2", "H", None), ("1X2", "D", None), ("1X2", "A", None),
    ):
        price = fixture.get({"H": "avg_h", "D": "avg_d", "A": "avg_a"}[key])
        try:
            p = float(price)
        except (TypeError, ValueError):
            continue
        if p <= 1.0:
            continue
        implied = 1.0 / p
        legs.append({"market": name, "selection": key, "price": p, "prob": implied,
                     "basis": "market"})
    for name, key, col, freq_key in (
        ("O/U 2.5", "Over", "avg_o", "FT over 2.5"),
        ("O/U 2.5", "Under", "avg_u", "FT under 2.5"),
    ):
        raw = fixture.get(col)
        try:
            p = float(raw)
        except (TypeError, ValueError):
            continue
        if p <= 1.0:
            continue
        legs.append({"market": name, "selection": key, "price": p, "prob": 1.0 / p,
                     "basis": "market"})
    for name, key, freq_key in (
        ("GG/NG", "GG", "GG"), ("GG/NG", "NG", "NG"),
        ("HT result", "Draw", "HT draw"),
        ("HT O/U 1.5", "Over", "HT over 1.5"), ("HT O/U 1.5", "Under", None),
    ):
        if name == "HT result":
            p = freq[freq_key]
        elif name == "HT O/U 1.5" and key == "Under":
            p = 1.0 - freq["HT over 1.5"]
        else:
            p = freq[freq_key]
        if not (0 < p < 1):
            continue
        legs.append({"market": name, "selection": key, "price": price_from_probability(p, DERIVED_MARGIN),
                     "prob": p, "basis": "frequencies"})
    return legs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stake", type=float, default=30.0)
    parser.add_argument("--target", type=float, default=30.0)
    parser.add_argument("--legs", type=int, default=4)
    args = parser.parse_args()

    rows = load()
    freq = frequencies(rows)
    date, day = latest_day(rows)
    print(f"corpus {len(rows):,} fixtures | latest match-day {date} with {len(day)} fixtures")

    pool = []
    for fixture in day:
        for leg in legs_for(fixture, freq):
            leg = dict(leg)
            leg["fixture"] = f"{fixture['home']} v {fixture['away']}"
            pool.append(leg)

    best = None
    for combo in itertools.combinations(pool, args.legs):
        if len({c["fixture"] for c in combo}) != args.legs:
            continue
        if len({c["market"] for c in combo}) < 2:
            continue
        price = 1.0
        prob = 1.0
        for leg in combo:
            price *= leg["price"]
            prob *= leg["prob"]
        distance = abs(price - args.target)
        if best is None or distance < best[0]:
            best = (distance, combo, price, prob)

    if not best:
        print("no combination available on that day")
        return 1

    _, combo, price, prob = best
    print(f"\nSlip: {args.legs} legs, combined {price:.2f}x, estimated probability {prob*100:.2f}%")
    for leg in combo:
        print(f"  {leg['fixture']:<34} {leg['market']:<11} {leg['selection']:<5} "
              f"@ {leg['price']:6.2f}  ({leg['basis']}, {leg['prob']*100:4.1f}%)")
    gross = args.stake * price
    ev = prob * gross - args.stake
    print(f"\nStake KSh {args.stake:.0f} -> returns KSh {gross:.0f} if all leg it, "
          f"net KSh {gross - args.stake:+.0f}; expected net KSh {ev:+.2f}")
    print(f"Fair price at the estimated probability would be {1/prob:.2f}x")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
