"""Run one monitored slip per persona per match-day, and settle the ones that have resolved.

Rules are chosen in `research/slip_rules.py` and pre-registered in `docs/PREREG-SLIPS.md`. Nothing here
claims an edge: the bootstrap intervals for every rule straddle zero. What this provides is a **record**
— slips written before the fixtures are played, settled afterwards, so the hit rate cannot be
reconstructed after the fact.

    python scripts/daily_slip.py --pick              # write today's slips (latest date in corpus)
    python scripts/daily_slip.py --settle            # settle any resolved pending slips
    python scripts/daily_slip.py --status            # running accuracy and calibration

Storage: var/slips.jsonl (gitignored). Each record keeps the best and average recorded price, the
market-implied probability, the rationale and the claim kinds.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "research"))

import slip_rules as rules  # noqa: E402

STORE = ROOT / "var" / "slips.jsonl"

PERSONAS = {
    "cautious": {"rule": "R1 favourite, single", "stake": 100.0,
                 "note": "One favourite, the least ambitious slip available"},
    "balanced": {"rule": "R2 favourite 1.60-2.20", "stake": 100.0,
                 "note": "A favourite at a price that pays something"},
    "ambitious": {"rule": "R4 two-leg double", "stake": 100.0,
                  "note": "Two favourites, a bigger return for a lower hit rate"},
}


def load_days() -> list[dict]:
    return rules.load_days()


def load_slips() -> list[dict]:
    if not STORE.exists():
        return []
    out = []
    for line in STORE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def save_slips(slips: list[dict]) -> None:
    STORE.parent.mkdir(parents=True, exist_ok=True)
    STORE.write_text("\n".join(json.dumps(s, sort_keys=True) for s in slips) + "\n",
                     encoding="utf-8")


def pick(date: str | None) -> int:
    days = load_days()
    if not days:
        print("no fixtures in the corpus")
        return 1
    target = date or days[-1]["date"]
    day = next((d for d in days if d["date"] == target), None)
    if day is None:
        print(f"no fixtures on {target}; latest is {days[-1]['date']}")
        return 1

    existing = load_slips()
    made = 0
    for persona, config in PERSONAS.items():
        if any(s["date"] == target and s["persona"] == persona for s in existing):
            print(f"{persona}: already recorded for {target}")
            continue
        picker = rules.RULES[config["rule"]]
        legs = picker(day["fixtures"])
        if not legs:
            print(f"{persona}: no slip constructible on {target}")
            continue
        record = {
            "date": target,
            "persona": persona,
            "rule": config["rule"],
            "stake": config["stake"],
            "recorded_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "status": "pending",
            "claims": {
                "legs": "observed — recorded closing quotes",
                "implied": "estimated — proportional de-vig of the average quote",
                "outcome": "not claimed: no prediction is being made beyond the market's own price",
            },
            "legs": [
                {
                    "fixture": leg["label"],
                    "selection": ("H", "D", "A")[leg["idx"]],
                    "price_best": leg["fixture"]["best"][leg["idx"]],
                    "price_avg": leg["fixture"]["avg"][leg["idx"]],
                    "implied": leg["fixture"]["probs"][leg["idx"]],
                }
                for leg in legs
            ],
        }
        existing.append(record)
        made += 1
        combo_best = 1.0
        combo_avg = 1.0
        for leg in legs:
            combo_best *= leg["fixture"]["best"][leg["idx"]]
            combo_avg *= leg["fixture"]["avg"][leg["idx"]]
        print(f"{persona}: {len(legs)} leg(s) on {target}, "
              f"best {combo_best:.2f}x / average {combo_avg:.2f}x, stake KSh {config['stake']:.0f}")

    save_slips(existing)
    print(f"recorded {made} slip(s); store has {len(existing)}")
    return 0


def settle() -> int:
    slips = load_slips()
    if not slips:
        print("nothing recorded yet; run --pick")
        return 0
    days = load_days()
    results = {}
    for day in days:
        for fixture in day["fixtures"]:
            results[(day["date"], fixture["label"])] = fixture["result"]

    changed = 0
    for slip in slips:
        if slip["status"] != "pending":
            continue
        outcomes = []
        for leg in slip["legs"]:
            outcome = results.get((slip["date"], leg["fixture"]))
            if outcome is None:
                outcomes = []
                break
            outcomes.append(outcome == leg["selection"])
        if not outcomes:
            continue
        won = all(outcomes)
        combo_best = 1.0
        combo_avg = 1.0
        for leg in slip["legs"]:
            combo_best *= leg["price_best"]
            combo_avg *= leg["price_avg"]
        slip["status"] = "won" if won else "lost"
        slip["settled_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        slip["net_best"] = round(slip["stake"] * (combo_best - 1) if won else -slip["stake"], 2)
        slip["net_avg"] = round(slip["stake"] * (combo_avg - 1) if won else -slip["stake"], 2)
        changed += 1
        print(f"{slip['date']} {slip['persona']}: {'WON' if won else 'lost'} "
              f"({slip['net_best']:+.0f} best / {slip['net_avg']:+.0f} average)")

    save_slips(slips)
    print(f"settled {changed} slip(s)")
    return 0


def status() -> int:
    slips = load_slips()
    if not slips:
        print("no slips recorded yet; run --pick")
        return 0
    pending = [s for s in slips if s["status"] == "pending"]
    settled = [s for s in slips if s["status"] in ("won", "lost")]
    print(f"slips: {len(slips)} total, {len(settled)} settled, {len(pending)} pending")
    if settled:
        print(f"{'persona':<12} {'n':>4} {'hit':>7} {'mean best':>10} {'mean avg':>9} "
              f"{'implied':>8} {'realised':>9}")
        for persona in PERSONAS:
            group = [s for s in settled if s["persona"] == persona]
            if not group:
                continue
            hits = sum(1 for s in group if s["status"] == "won")
            implied_values = []
            for slip in group:
                product = 1.0
                for leg in slip["legs"]:
                    product *= leg["implied"]
                implied_values.append(product)
            implied = statistics.mean(implied_values)
            print(f"{persona:<12} {len(group):>4} {hits/len(group)*100:>6.0f}% "
                  f"{statistics.mean(s['net_best'] for s in group):>+10.1f} "
                  f"{statistics.mean(s['net_avg'] for s in group):>+9.1f} "
                  f"{implied*100:>7.1f}% {hits/len(group)*100:>8.1f}%")
        print("\nThe implied column is what the market said; realised is what happened. A gap between "
              "them is\ncalibration drift in the market, not skill in the selection, and the sample "
              "is small for a long time.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Daily monitored slip")
    parser.add_argument("--pick", action="store_true")
    parser.add_argument("--settle", action="store_true")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--date", default=None)
    args = parser.parse_args()
    if args.pick:
        return pick(args.date)
    if args.settle:
        return settle()
    if args.status:
        return status()
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
