"""The planner: a stake and a multiplier in, slip options out.

The user says what they have and what they want to make — "KSh 100, 10x" — and this returns slips from
the most recent recorded match-day that land near that multiplier, with the probability the market
implies, the expected net, the downside and the variance.

Two things it deliberately does not do. It does not predict: the probability shown is the product of the
market's own de-vigged probabilities, because a fitted model did not beat that product out of time
(research/SLIP_MODEL.md). And it does not call a match on a day it has no prices for: with no fixtures
feed, "today" means the latest recorded match-day, and the response says so.
"""

from __future__ import annotations

import math
from datetime import datetime

from app import engine

MAX_OPTIONS = 6


def _parse_date(value: str) -> datetime | None:
    try:
        return datetime.strptime(value, "%d/%m/%Y")
    except (ValueError, TypeError):
        return None


def latest_day(fixtures: list[engine.Fixture]) -> tuple[str, list[engine.Fixture]]:
    """The most recent match-day in the corpus, with its fixtures."""
    dated = [(_parse_date(f.date), f) for f in fixtures]
    dated = [(d, f) for d, f in dated if d is not None]
    if not dated:
        return "", []
    newest = max(d for d, _ in dated)
    return newest.strftime("%d/%m/%Y"), [f for d, f in dated if d == newest]


def _selections(fixture: engine.Fixture) -> list[dict]:
    """Every priced outcome on a fixture, with its best price and market-implied probability."""
    if "Avg" not in fixture.odds:
        return []
    probs = engine.devig(fixture.odds["Avg"])
    best = fixture.odds.get("Max", fixture.odds["Avg"])
    out = []
    for i, outcome in enumerate(engine.OUTCOMES):
        out.append({
            "fixture": fixture, "outcome": outcome, "label": f"{fixture.label} ({outcome})",
            "price": best[i], "implied": probs[i],
        })
    return out


def plan(stake: float, target: float, tolerance: float = 0.15, max_legs: int = 3,
         fixtures: list[engine.Fixture] | None = None) -> dict:
    if stake <= 0 or target <= 1.0:
        raise ValueError("stake must be positive and the target multiplier above 1")
    pool = fixtures if fixtures is not None else engine.load_fixtures()
    if not pool:
        raise ValueError("no fixtures available")

    date, day = latest_day(pool)
    if not day:
        raise ValueError("no dated fixtures")

    lo, hi = target * (1 - tolerance), target * (1 + tolerance)
    selections = [s for f in day for s in _selections(f)]
    options = []

    # Singles.
    for s in selections:
        if lo <= s["price"] <= hi:
            options.append(_option([s], stake))

    # Two and three leg combinations across different fixtures.
    if max_legs >= 2:
        for i in range(len(selections)):
            for j in range(i + 1, len(selections)):
                a, b = selections[i], selections[j]
                if a["fixture"].key == b["fixture"].key:
                    continue
                combo = a["price"] * b["price"]
                if lo <= combo <= hi:
                    options.append(_option([a, b], stake))
                    continue
                if max_legs >= 3:
                    for k in range(j + 1, len(selections)):
                        c = selections[k]
                        if c["fixture"].key in (a["fixture"].key, b["fixture"].key):
                            continue
                        combo3 = combo * c["price"]
                        if lo <= combo3 <= hi:
                            options.append(_option([a, b, c], stake))

    options.sort(key=lambda o: abs(o["combined_price"] - target))
    chosen = options[:MAX_OPTIONS]

    return {
        "stake": stake,
        "target": target,
        "tolerance": tolerance,
        "match_day": date,
        "fixtures_on_day": len(day),
        "options": chosen,
        "found": bool(chosen),
        "claims": {
            "probability": "estimated — the product of the market's de-vigged probabilities, not a "
                           "forecast of ours; a fitted model did not beat this product out of time",
            "price": "observed — recorded closing quotes",
            "net": "hypothetical — arithmetic on the stake and the recorded price",
        },
        "verdict": (
            f"{len(chosen)} slip(s) land within {tolerance:.0%} of {target:g}× on the latest recorded "
            f"match-day ({date}). These are options, not recommendations: none has a demonstrated "
            f"edge, and the expected net at these prices is negative before any margin."
            if chosen else
            f"No slip on {date} lands within {tolerance:.0%} of {target:g}×. The honest answer is that "
            f"the market does not offer that multiplier from these fixtures."
        ),
        "caveats": [
            "This is the latest recorded match-day in the corpus, not today's fixtures: there is no "
            "fixtures feed, so nothing here can be placed.",
            "Probabilities are the market's own, multiplied. No model is applied beyond that product.",
            "Prices are recorded closing quotes, which no user is guaranteed to obtain.",
            "A target is a constraint you choose. The market does not owe you that multiplier.",
        ],
    }


def _option(legs: list[dict], stake: float) -> dict:
    price = 1.0
    implied = 1.0
    for leg in legs:
        price *= leg["price"]
        implied *= leg["implied"]
    gross = stake * price
    ev = implied * gross - stake
    return {
        "legs": [
            {"fixture": leg["fixture"].label, "selection": leg["outcome"],
             "price": round(leg["price"], 3), "implied": round(leg["implied"], 4)}
            for leg in legs
        ],
        "n_legs": len(legs),
        "combined_price": round(price, 3),
        "implied_probability": round(implied, 6),
        "gross_return": round(gross, 2),
        "net_if_won": round(gross - stake, 2),
        "loss_if_lost": round(stake, 2),
        "expected_net": round(ev, 2),
        "variance": round(implied * (1 - implied) * gross * gross, 2),
    }
