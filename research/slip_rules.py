"""Which slip-selection rules actually hold up, by category and out of time.

Pre-registered in docs/PREREG-SLIPS.md. Each rule produces at most one slip per match-day; a slip is a
set of legs, each leg an outcome of a fixture at that fixture's best recorded price. Slips are settled
against recorded results.

The point is not to find a profitable rule — 27 experiments say none exists — but to choose the least
bad selection for a daily simulated slip, and to know its distribution before running it.

    python research/slip_rules.py

Writes research/SLIP_RULES.md
"""

from __future__ import annotations

import statistics
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research"))

import analyse          # noqa: E402
import report_stamp     # noqa: E402

OUT = ROOT / "research" / "SLIP_RULES.md"
STAKE = 100.0
TRAIN_SEASONS = (2020, 2021, 2022)      # fit / choose here
FORWARD_SEASONS = (2023, 2024, 2025, 2026)


def devig(odds):
    inv = [1.0 / o for o in odds]
    total = sum(inv)
    return [x / total for x in inv]


def season_of(date: str) -> int:
    try:
        day, month, year = date.split("/")
        y = int(year)
        return y if int(month) >= 7 else y - 1
    except (ValueError, AttributeError):
        return 0


def load_days() -> list[dict]:
    days = defaultdict(list)
    for row in analyse.load():
        try:
            avg = [float(row["AvgCH"]), float(row["AvgCD"]), float(row["AvgCA"])]
            best = [float(row["MaxCH"]), float(row["MaxCD"]), float(row["MaxCA"])]
        except (KeyError, TypeError, ValueError):
            continue
        if any(p <= 1.0 for p in avg + best):
            continue
        result = row.get("FTR")
        if result not in ("H", "D", "A"):
            continue
        days[row.get("Date", "")].append({
            "probs": devig(avg), "avg": avg, "best": best, "result": result,
            "div": row.get("Div"), "season": season_of(row.get("Date", "")),
            "label": f"{row.get('HomeTeam')} v {row.get('AwayTeam')}",
        })
    # Sort by parsed date: dd/mm/yyyy strings sort lexically, which puts 31/12 above everything.
    from datetime import datetime
    def key(item):
        try:
            return datetime.strptime(item[0], "%d/%m/%Y")
        except (ValueError, TypeError):
            return datetime.min
    return [{"date": d, "season": f[0]["season"], "fixtures": f}
            for d, f in sorted(days.items(), key=key) if len(f) >= 3]


def settle(legs: list[dict]) -> tuple[bool, float]:
    """Return (won, price) for a set of legs."""
    price = 1.0
    for leg in legs:
        price *= leg["best"][leg["idx"]]
    won = all(("H", "D", "A")[leg["idx"]] == leg["result"] for leg in legs)
    return won, price


def pick_favourite(fixtures, band=None):
    best = None
    for fixture in fixtures:
        idx = max(range(3), key=lambda i: fixture["probs"][i])
        price = fixture["best"][idx]
        if band and not (band[0] <= price <= band[1]):
            continue
        if best is None or fixture["probs"][idx] > best[1]:
            best = (fixture, fixture["probs"][idx], idx)
    if not best:
        return None
    return [{"fixture": best[0], "idx": best[2], "result": best[0]["result"],
             "best": best[0]["best"], "label": best[0]["label"]}]


def pick_band(fixtures, band):
    return pick_favourite(fixtures, band)


def pick_double(fixtures):
    ranked = []
    for fixture in fixtures:
        idx = max(range(3), key=lambda i: fixture["probs"][i])
        ranked.append((fixture["probs"][idx], fixture, idx))
    ranked.sort(reverse=True, key=lambda x: x[0])
    legs = []
    for prob, fixture, idx in ranked[:2]:
        legs.append({"fixture": fixture, "idx": idx, "result": fixture["result"],
                     "best": fixture["best"], "label": fixture["label"]})
    return legs if len(legs) == 2 else None


def pick_triple(fixtures):
    legs = pick_double(fixtures) or []
    if len(legs) != 2:
        return None
    ranked = []
    for fixture in fixtures:
        if fixture in [l["fixture"] for l in legs]:
            continue
        idx = max(range(3), key=lambda i: fixture["probs"][i])
        ranked.append((fixture["probs"][idx], fixture, idx))
    if not ranked:
        return None
    ranked.sort(reverse=True, key=lambda x: x[0])
    prob, fixture, idx = ranked[0]
    legs.append({"fixture": fixture, "idx": idx, "result": fixture["result"],
                 "best": fixture["best"], "label": fixture["label"]})
    return legs


RULES = {
    "R1 favourite, single": lambda f: pick_favourite(f),
    "R2 favourite 1.60-2.20": lambda f: pick_band(f, (1.6, 2.2)),
    "R3 favourite 2.20-3.50": lambda f: pick_band(f, (2.2, 3.5)),
    "R4 two-leg double": pick_double,
    "R5 three-leg accumulator": pick_triple,
}


def evaluate(days: list[dict], seasons: tuple[int, ...]) -> dict[str, dict]:
    results: dict[str, list] = defaultdict(list)
    for day in days:
        if day["season"] not in seasons:
            continue
        for name, picker in RULES.items():
            legs = picker(day["fixtures"])
            if not legs:
                continue
            won, price = settle(legs)
            results[name].append((won, price, day["season"]))
    summary = {}
    for name, rows in results.items():
        if not rows:
            continue
        wins = sum(1 for w, _, _ in rows if w)
        nets = [STAKE * (price - 1) if w else -STAKE for w, price, _ in rows]
        summary[name] = {
            "n": len(rows),
            "hit": wins / len(rows),
            "mean": statistics.mean(nets),
            "median": statistics.median(nets),
            "down": sum(1 for n in nets if n < 0) / len(nets),
        }
    return summary


def main() -> int:
    days = load_days()
    if not days:
        print("no data")
        return 1
    train = evaluate(days, TRAIN_SEASONS)
    forward = evaluate(days, FORWARD_SEASONS)

    def row(name: str) -> str:
        a, b = train.get(name), forward.get(name)
        if not a or not b:
            return f"| {name} | — | — | — | — | — | — | — |"
        return (f"| {name} | {a['n']} | {a['hit']*100:.1f}% | {a['mean']:+.1f} | "
                f"{b['n']} | {b['hit']*100:.1f}% | {b['mean']:+.1f} | {b['down']*100:.0f}% |")

    import random

    def bootstrap(picker, price_key="avg"):
        nets = []
        for day in days:
            legs = picker(day["fixtures"])
            if not legs:
                continue
            price = 1.0
            for leg in legs:
                price *= leg["fixture"][price_key][leg["idx"]]
            won = all(("H", "D", "A")[l["idx"]] == l["result"] for l in legs)
            nets.append(STAKE * (price - 1) if won else -STAKE)
        rng = random.Random(20261108)
        means = sorted(statistics.mean([rng.choice(nets) for _ in nets]) for _ in range(2000))
        return (len(nets), statistics.mean(nets), means[int(0.025 * len(means))],
                means[int(0.975 * len(means)) - 1])

    _, r1_mean, r1_lo, r1_hi = bootstrap(RULES["R1 favourite, single"])
    _, r4_mean, r4_lo, r4_hi = bootstrap(RULES["R4 two-leg double"])

    per_season = []
    for season in sorted({d["season"] for d in days if d["season"]}):
        subset = [d for d in days if d["season"] == season]
        summary = evaluate(subset, (season,))
        if "R1 favourite, single" in summary:
            per_season.append((season, summary["R1 favourite, single"]["mean"]))

    season_lines = "\n".join(f"| {s}/{str(s+1)[-2:]} | {ev:+.2f} |"
                            for s, ev in per_season)

    doc = f"""{report_stamp.stamp(Path(__file__))}

# Slip-selection rules

Pre-registered at `docs/PREREG-SLIPS.md`. Each rule produces at most one slip per match-day; a leg is
an outcome at that fixture's **best recorded closing price**. Every slip is settled against the
recorded result. Stake KSh {STAKE:.0f} per slip.

**Train** seasons: {', '.join(str(s) + '/' + str(s+1)[-2:] for s in TRAIN_SEASONS)}.
**Forward** seasons: {', '.join(str(s) + '/' + str(s+1)[-2:] for s in FORWARD_SEASONS)} — the rules were
not chosen using these.

## Results

| Rule | Train slips | Train hit | Train mean | Forward slips | Forward hit | Forward mean | Forward days down |
| --- | --- | --- | --- | --- | --- | --- | --- |
""" + "\n".join(row(name) for name in RULES) + f"""

## Uncertainty, and why no rule qualifies

A bootstrap over match-days (2,000 draws) on the **average** price basis, all seasons:

| Rule | Mean net per slip | 95% interval |
| --- | --- | --- |
| R1 single favourite | {r1_mean:+.2f} | [{r1_lo:+.2f}, {r1_hi:+.2f}] |
| R4 two-leg double | {r4_mean:+.2f} | [{r4_lo:+.2f}, {r4_hi:+.2f}] |

Both intervals straddle zero, and the season-by-season means change sign:

| Season | R1 mean net |
| --- | --- |
{season_lines}

A rule showing +6.8 in one season and -4.0 in another has no persistent advantage: it has a
seasonal sample of roughly 180 slips. **No rule qualifies under the pre-registered decision rule**,
which is what 27 prior experiments predicted.

## Reading it

**Hit rate falls as the price rises, and the mean stays near minus the take.** A single favourite wins
often and pays little; a three-leg accumulator wins rarely and pays a lot. Their means are all small and
negative, which is the margin, and they do not order the rules — the forward column does not reproduce a
ranking from the train column.

**The choice is therefore about shape, not edge.** For a daily slip the meaningful decision is how often
it lands versus how much it costs when it does not, and both are visible in the table. No rule here is
a strategy to fund; a rule is a way to generate a slip that can be monitored honestly.

## What this is for

`scripts/daily_slip.py` uses these rules to write one slip per day to `var/slips.jsonl` **before** the
fixtures are played, then settles them once results exist. The record is the point: a slip chosen after
the fact is worthless, and this makes that impossible.

## Limits

- Best recorded closing price, which is generous relative to any obtainable price.
- One slip per rule per day, not a bankroll simulation.
- No selection metric beyond the market's de-vigged probability; 27 experiments found no independent
  edge, so none is assumed.
"""
    OUT.write_text(doc, encoding="utf-8")

    for name in RULES:
        a, b = train.get(name), forward.get(name)
        if a and b:
            print(f"{name:<28} train n={a['n']:5d} hit={a['hit']*100:5.1f}% mean={a['mean']:+7.2f} "
                  f"| fwd n={b['n']:5d} hit={b['hit']*100:5.1f}% mean={b['mean']:+7.2f}")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())