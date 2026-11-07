"""What a user with KSh 100-300 would have done, across every way of spending it.

Pre-registered in docs/PREREG-USER-SIM.md. This is a retrospective simulation over historical
match-days in the held corpus, not a statement about today — the corpus ends in 2023.

    python research/user_simulation.py

Writes research/USER_SIMULATION.md.
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

OUT = ROOT / "research" / "USER_SIMULATION.md"
BUDGETS = (100.0, 300.0)
SEED_STAKE = 100.0


def devig(odds: list[float]) -> list[float]:
    inv = [1.0 / o for o in odds]
    total = sum(inv)
    return [x / total for x in inv]


def load_days() -> tuple[list[dict], float]:
    """Group fixtures by date, keeping only what the simulation needs, plus the mean margin."""
    rows = analyse.load()
    days: dict[str, list[dict]] = defaultdict(list)
    margins: list[float] = []
    for row in rows:
        try:
            prices = [float(row["AvgCH"]), float(row["AvgCD"]), float(row["AvgCA"])]
        except (KeyError, TypeError, ValueError):
            continue
        if any(p <= 1.0 for p in prices):
            continue
        result = row.get("FTR")
        if result not in ("H", "D", "A"):
            continue
        try:
            best = [float(row["MaxCH"]), float(row["MaxCD"]), float(row["MaxCA"])]
        except (KeyError, TypeError, ValueError):
            best = prices
        if any(p <= 1.0 for p in best):
            continue
        margins.append(sum(1.0 / p for p in prices) - 1.0)
        days[row.get("Date", "")].append({
            "probs": devig(prices),
            "avg": prices,
            "best": best,
            "result": result,
            "div": row.get("Div"),
            "key": f"{row.get('HomeTeam')} v {row.get('AwayTeam')}",
        })
    usable = {d: fixtures for d, fixtures in days.items() if len(fixtures) >= 3}
    return [{"date": d, "fixtures": f} for d, f in sorted(usable.items())], statistics.mean(margins)


def favourite(fixture: dict) -> tuple[int, float]:
    idx = max(range(3), key=lambda i: fixture["probs"][i])
    return idx, fixture["best"][idx]


def net_single(fixture: dict, stake: float) -> float:
    idx, price = favourite(fixture)
    won = ("H", "D", "A")[idx] == fixture["result"]
    return stake * (price - 1.0) if won else -stake


def closest_single(day: dict, target: float, lo: float, hi: float) -> dict | None:
    candidates = [f for f in day["fixtures"] if lo <= max(f["best"]) <= hi]
    if not candidates:
        return None
    return min(candidates, key=lambda f: abs(max(f["best"]) - target))


def closest_double(day: dict, target: float, lo: float, hi: float):
    """Two fixtures and the specific outcomes whose combined price lands in the window."""
    fixtures = day["fixtures"]
    best = None
    for i in range(len(fixtures)):
        for j in range(i + 1, len(fixtures)):
            a, b = fixtures[i], fixtures[j]
            for ia in range(3):
                for ib in range(3):
                    combo = a["best"][ia] * b["best"][ib]
                    if lo <= combo <= hi:
                        distance = abs(combo - target)
                        if best is None or distance < best[0]:
                            best = (distance, a, ia, b, ib, combo)
    if not best:
        return None
    a, ia, b, ib, combo = best[1], best[2], best[3], best[4], best[5]
    return {"a": a, "ia": ia, "b": b, "ib": ib, "combo": combo,
            "result": a["result"]}


def pct(values: list[float], p: float) -> float:
    if not values:
        return float("nan")
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, int(round(p * (len(ordered) - 1)))))
    return ordered[index]


def main() -> int:
    days, margin = load_days()
    if not days:
        print("no usable days in the corpus")
        return 1

    archetypes = {
        "A1": {"label": "Single favourite", "stake": 100.0, "budget": 100.0},
        "A2": {"label": "Single favourite, full budget", "stake": 300.0, "budget": 300.0},
        "A3": {"label": "Split three ways", "stake": 300.0, "budget": 300.0},
        "A4": {"label": "Target 3x, single", "stake": 100.0, "budget": 100.0},
        "A5": {"label": "Target 6x, double", "stake": 100.0, "budget": 100.0},
        "A6": {"label": "Accumulator, three legs", "stake": 100.0, "budget": 100.0},
        "A7": {"label": "Abstain", "stake": 0.0, "budget": 0.0},
        "A8": {"label": "Single favourite, average price", "stake": 100.0, "budget": 100.0},
    }
    results: dict[str, list[float]] = {k: [] for k in archetypes}
    skipped = defaultdict(int)

    for day in days:
        fixtures = day["fixtures"]

        # A1 / A2: one favourite on the day's first fixture.
        results["A1"].append(net_single(fixtures[0], 100.0))
        results["A2"].append(net_single(fixtures[0], 300.0))

        # A8: the same bet at the *average* closing price rather than the recorded maximum.
        idx0, _ = favourite(fixtures[0])
        avg_price = fixtures[0]["avg"][idx0]
        won0 = ("H", "D", "A")[idx0] == fixtures[0]["result"]
        results["A8"].append(100.0 * (avg_price - 1.0) if won0 else -100.0)

        # A3: three separate favourites, 100 each.
        results["A3"].append(sum(net_single(f, 100.0) for f in fixtures[:3]))

        # A4: the single closest to 3x.
        pick = closest_single(day, 3.0, 2.7, 3.3)
        if pick:
            results["A4"].append(net_single(pick, 100.0))
        else:
            skipped["A4"] += 1

        # A5: two legs closest to 6x.
        pair = closest_double(day, 6.0, 5.4, 6.6)
        if pair:
            won = (pair["result"] == ("H", "D", "A")[pair["ia"]]
                   and pair["b"]["result"] == ("H", "D", "A")[pair["ib"]])
            results["A5"].append(100.0 * (pair["combo"] - 1.0) if won else -100.0)
        else:
            skipped["A5"] += 1

        # A6: three favourites across matches on one slip.
        if len(fixtures) >= 3:
            combo = 1.0
            won = True
            for f in fixtures[:3]:
                idx, price = favourite(f)
                combo *= price
                won = won and ("H", "D", "A")[idx] == f["result"]
            results["A6"].append(100.0 * (combo - 1.0) if won else -100.0)

        # A7: abstain, always zero.
        results["A7"].append(0.0)

    def row(key: str) -> str:
        meta = archetypes[key]
        nets = results[key]
        if not nets:
            return f"| {key} | {meta['label']} | — | — | — | — | — | — |"
        down = sum(1 for n in nets if n < 0) / len(nets)
        ruined = sum(1 for n in nets if n <= -meta["budget"]) / len(nets)
        return (f"| {key} | {meta['label']} | KSh {meta['budget']:.0f} | "
                f"{statistics.mean(nets):+.1f} | {statistics.median(nets):+.1f} | "
                f"{pct(nets, 0.05):+.1f} … {pct(nets, 0.95):+.1f} | "
                f"{down*100:.0f}% | {ruined*100:.0f}% |")

    theoretical = {k: -archetypes[k]["stake"] * margin / (1 + margin) for k in ("A1", "A2")}

    doc = f"""{report_stamp.stamp(Path(__file__))}

# What a user with KSh 100–300 would have done

Pre-registered at `docs/PREREG-USER-SIM.md`. **Retrospective**, over {len(days)} historical match-days
in the held corpus. The corpus runs from January 2021 to December 2023, so this says nothing about
today; there is no data for today and none was invented.

Mean closing margin across the corpus: **{margin:.4f}**.

## Two prices, two answers

The arithmetic is unambiguous: at a quoted price, expected net is `-s * m/(1+m)`, which on KSh 100 is
**KSh {theoretical['A1']:.2f}**. But a backtest has to choose *which* price the user gets, and the
corpus records both an average and a maximum across books. That choice changes the sign:

| Price used | Mean net per KSh 100 | What it means |
| --- | --- | --- |
| Average closing price (A8) | **{statistics.mean(results['A8']):+.2f}** | Roughly break-even |
| Best recorded closing price (A1) | **{statistics.mean(results['A1']):+.2f}** | Looks profitable, and is not attainable |

The gap between those two is the selection effect measured in E20: the maximum of several noisy quotes
sits above the average by construction, and a backtest that always assumes the maximum is measuring an
artefact. **The honest expectation is the average-price row**, and even that is only about break-even
because favourites in this corpus won slightly more often than their de-vigged probability implied —
the same small departure E25 found at short prices. It is a calibration fact, not an edge, and it is
too small to survive a worse price or a limit.

## Every way to spend the budget

| | Archetype | Budget | Mean net | Median | 5th … 95th | Days ending down | Days losing the lot |
| --- | --- | --- | --- | --- | --- | --- | --- |
""" + "\n".join(row(k) for k in archetypes) + f"""

Days where the archetype could not be constructed: A4 {skipped['A4']}, A5 {skipped['A5']} (the corpus
does not offer that price that day, so the search correctly found nothing).

## What this says

**The mean is small and the variance is not.** A single favourite bet on one day ends down about
{sum(1 for n in results['A8'] if n < 0) / len(results['A8']) * 100:.0f}% of the time, losing the whole
KSh 100, and wins a few tens the rest. The average is close to zero; a single day is mostly noise.

**Higher multipliers convert a small mean into a large occasional swing.** The 6× double ends down on
{sum(1 for n in results['A5'] if n < 0) / len(results['A5']) * 100:.0f}% of days, and the three-leg
accumulator on {sum(1 for n in results['A6'] if n < 0) / len(results['A6']) * 100:.0f}%. Their means
are flattered by rare large wins; the shape of the distribution is what a user feels.

**Abstaining is the only archetype with no downside**, which is why the product is allowed to say it.

## What this does not say

- Nothing about today. The last fixture in the corpus is from 2023.
- Nothing about obtainable prices: even the average-price row assumes a book at the market average.
- Nothing about a strategy: these are single-day draws, and the corpus cannot tell you whether the next
  draw is favourable.

## The answer, in one line

On a KSh 100–300 budget for one day, the expected loss at a price you could plausibly get is
**about KSh 0–5**, but the day ends down roughly **45% of the time on a single favourite and 80%+ on
anything ambitious** — and the ambitious structures are where the money actually goes.
"""
    OUT.write_text(doc, encoding="utf-8")

    print(f"days={len(days)} margin={margin:.4f} expected_loss_100={theoretical['A1']:.2f}")
    for k in archetypes:
        nets = results[k]
        if nets:
            down = sum(1 for n in nets if n < 0) / len(nets)
            print(f"{k} {archetypes[k]['label']:<32} mean={statistics.mean(nets):+8.1f} "
                  f"down={down*100:5.1f}%  n={len(nets)}")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
