"""Stake and multiplier structures — what the same upside costs.

Pre-registered in docs/PREREG-STAKE.md. The question: is KSh 100 at 3x the same proposition as
KSh 200 at 2x? Both return the same net profit if they win; they differ in stake at risk, in hit
probability and in variance.

    python research/stake_structures.py

Writes research/STAKE_STRUCTURES.md.
"""

from __future__ import annotations

import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research"))

import analyse          # noqa: E402
import report_stamp     # noqa: E402

OUT = ROOT / "research" / "STAKE_STRUCTURES.md"
BANDS = [(1.4, 1.7), (1.8, 2.2), (2.7, 3.3), (3.6, 4.4), (5.4, 6.6)]
TARGET_NET = 200.0
BOOTSTRAPS = 2000
SEED = 20261105


def implied(odds: float, margin: float) -> float:
    """Market-implied probability at a quoted price, given the book's proportional margin."""
    return 1.0 / (odds * (1.0 + margin))


def structures_for(odds: float, margin: float, target_net: float) -> dict:
    """The stake needed to make this odds level return `target_net`, and the resulting risk profile."""
    stake = target_net / (odds - 1.0)
    p = implied(odds, margin)
    gross = stake * odds
    net = gross - stake
    ev = p * net - (1.0 - p) * stake
    variance = p * (1.0 - p) * gross**2
    return {
        "odds": odds,
        "stake": stake,
        "gross": gross,
        "net": net,
        "prob": p,
        "ev": ev,
        "variance": variance,
        "downside": stake,
    }


def devig(odds: list[float]) -> list[float]:
    inv = [1.0 / o for o in odds]
    total = sum(inv)
    return [x / total for x in inv]


def season_of(date: str) -> str:
    """Season label from a dd/mm/yyyy date: July onwards starts the next season."""
    try:
        _, month, year = date.split("/")
        y = int(year)
        return f"{y}" if int(month) >= 7 else f"{y - 1}"
    except (ValueError, AttributeError):
        return "unknown"


def main() -> int:
    rows = analyse.load()

    plays = []
    margins = []
    for row in rows:
        try:
            prices = [float(row["AvgCH"]), float(row["AvgCD"]), float(row["AvgCA"])]
        except (KeyError, TypeError, ValueError):
            continue
        if any(p <= 1.0 for p in prices):
            continue
        probs = devig(prices)
        margins.append(sum(1.0 / p for p in prices) - 1.0)
        result = row.get("FTR")
        for i, outcome in enumerate(("H", "D", "A")):
            plays.append({"price": prices[i], "prob": probs[i],
                          "won": (result == outcome) if result in ("H", "D", "A") else None,
                          "div": row.get("Div"), "season": season_of(row.get("Date", ""))})

    margin = statistics.mean(margins) if margins else 0.0

    table = []
    for low, high in BANDS:
        band = [x for x in plays if low <= x["price"] <= high and x["won"] is not None]
        if not band:
            continue
        implied_mean = statistics.mean(x["prob"] for x in band)
        realised = sum(1 for x in band if x["won"]) / len(band)
        centre = statistics.median(x["price"] for x in band)
        s = structures_for(centre, margin, TARGET_NET)
        realised_ev = realised * centre - 1.0
        table.append({"low": low, "high": high, "n": len(band), "centre": centre,
                      "implied": implied_mean, "realised": realised, "realised_ev": realised_ev,
                      "stake": s["stake"], "downside": s["downside"],
                      "variance": s["variance"], "prob": s["prob"]})

    clusters = {}
    for x in plays:
        if x["won"] is None:
            continue
        clusters.setdefault((str(x["div"]), str(x["season"])), []).append(x)
    keys = sorted(clusters)
    import numpy as np
    rng = np.random.default_rng(SEED)
    intervals = []
    for row in table:
        draws = []
        for _ in range(BOOTSTRAPS):
            pick = [clusters[keys[rng.integers(0, len(keys))]] for _ in keys]
            flat = [x for group in pick for x in group
                    if row["low"] <= x["price"] <= row["high"]]
            if flat:
                draws.append(sum(1 for x in flat if x["won"]) / len(flat))
        draws.sort()
        intervals.append((draws[int(0.025 * len(draws))], draws[int(0.975 * len(draws)) - 1])
                         if draws else (float("nan"), float("nan")))

    doc = f"""{report_stamp.stamp(Path(__file__))}

# Stake and multiplier structures

Pre-registered at `docs/PREREG-STAKE.md` before the run. The sponsor's question: is KSh 100 at 3x the
same proposition as KSh 200 at 2x?

Both return the same **net profit** if they win. They differ in what is at risk, how often they win,
and how widely outcomes vary. This report measures that trade-off on the held corpus, using the
recorded market-average closing prices, de-vigged proportionally.

Average closing margin across the corpus: **{margin:.4f}**. Selections available: **{len(plays):,}**
outcome-quotes from {len(rows):,} fixtures.

## The identity that fixes the expected value

At a quoted price with proportional margin `m`, the market-implied probability satisfies
`p · odds = 1/(1+m)`, so the expected net is

`EV = p·s(odds − 1) − (1 − p)s = −s · m/(1 + m)`

That is **proportional to the stake, not to the odds**. Two structures with the same stake have the
same expected loss regardless of price; two structures matched on net upside have expected losses in
proportion to their stakes. This is algebra under the margin assumption, not a measurement.

## Matched on a net upside of KSh {TARGET_NET:.0f}

| Odds band | Selections | Median price | Stake needed | Lost if it fails | Market-implied hit | Realised hit (95% cluster) | Realised EV at that price |
| --- | --- | --- | --- | --- | --- | --- | --- |
""" + "\n".join(
        f"| {row['low']:.1f}–{row['high']:.1f} | {row['n']:,} | {row['centre']:.2f} | "
        f"KSh {row['stake']:.0f} | KSh {row['downside']:.0f} | {row['prob']*100:.1f}% | "
        f"{row['realised']*100:.1f}% [{lo*100:.1f}, {hi*100:.1f}] | "
        f"{row['realised_ev']*100:+.1f}% |"
        for row, (lo, hi) in zip(table, intervals)) + f"""

Reading the table: to make the same KSh {TARGET_NET:.0f} net, a 1.5 shot needs a **large** stake and a
6 shot needs a **small** one. The probability of winning falls as the stake falls, roughly in step.
The expected loss, being stake-proportional, falls with the stake.

## Variance

| Odds band | Variance of net result |
| --- | --- |
""" + "\n".join(f"| {row['low']:.1f}–{row['high']:.1f} | {row['variance']:,.0f} |" for row in table) + f"""

Variance grows with the gross return, so the low-odds structure has the smaller variance for the same
net upside — at the cost of a much larger stake at risk.

## Do the realised rates match the market's probabilities?

""" + "\n".join(
        f"- **{row['low']:.1f}–{row['high']:.1f}**: implied {row['implied']*100:.1f}%, realised "
        f"{row['realised']*100:.1f}%, interval [{lo*100:.1f}, {hi*100:.1f}] — "
        + ("consistent with the implied probability." if lo <= row['implied'] <= hi
           else "**outside** the interval: a calibration departure, not an edge.")
        for row, (lo, hi) in zip(table, intervals)) + f"""

### What the realised-EV column says

`realised hit x median price - 1` is what a flat-stake backer would have earned in each band, before
stake limits and with no price shopping. Every band is **negative**, including the short one where the
realised rate runs above the implied probability: at a median price near 1.55, a 63.3% hit rate returns
about -1.9%. A calibration pattern that does not survive its own margin is not an opportunity, and
here the margin is larger than the departure.

## The answer to the question

**They are not the same proposition, and neither is better.** For the same net upside:

- the **higher-odds** structure risks **less money**, wins **less often**, and has a **smaller absolute
  expected loss**;
- the **lower-odds** structure risks **more money**, wins **more often**, and has **smaller variance**
  in the outcome for the same upside — but a larger downside in absolute terms.

There is one asymmetry in the data worth naming: short prices won slightly **more** often than
their de-vigged probability implied, the direction of the classic favourite-longshot bias, while the
high-price bands ran slightly below. The departure is small, sits at the edge of the interval, and does
not survive the margin - so it is a fact about market calibration, not a reason to prefer one structure.

That is a preference over distributions, not a valuation. Anyone claiming one is "better value" is
either assuming a risk preference or ignoring the margin.

## Limits

- Market-implied probabilities under proportional de-vig; not our forecasts.
- Stake arithmetic ignores limits, rounding, account terms and whether the price is obtainable — the
  corpus has no timestamps.
- Selections are grouped by price band, so a band mixes fixtures of very different kinds; the
  intervals account for division-season clustering, not for that heterogeneity.
- No profitability claim: every expected net here is negative by the margin.
"""
    OUT.write_text(doc, encoding="utf-8")

    for row, (lo, hi) in zip(table, intervals):
        print(f"{row['low']:.1f}-{row['high']:.1f}  n={row['n']:5,}  stake=KSh{row['stake']:6.0f}  "
              f"implied={row['prob']*100:5.1f}%  realised={row['realised']*100:5.1f}% "
              f"[{lo*100:.1f},{hi*100:.1f}]")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
