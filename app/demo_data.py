"""Synthetic fixtures for demo mode.

The held corpus is not committed to the repository (it is gitignored, and re-downloading it would be
new data acquisition, which the standing boundaries forbid). So the app needs a way to run from a
clean checkout. This module generates plausible three-way markets with a **clearly labelled**
provenance of "synthetic", and the interface shows a banner whenever they are in use.

Nothing here is evidence. It exists so the product can be demonstrated and tested without pretending
a made-up price is a recorded one.
"""

from __future__ import annotations

import random

from app.engine import Fixture

TEAMS = [
    "Arsenal", "Aston Villa", "Bournemouth", "Brentford", "Brighton", "Chelsea", "Crystal Palace",
    "Everton", "Fulham", "Leeds", "Leicester", "Liverpool", "Man City", "Man United", "Newcastle",
    "Nottingham Forest", "Southampton", "Tottenham", "West Ham", "Wolves", "Bayern Munich",
    "Dortmund", "Leipzig", "Leverkusen", "Inter", "Milan", "Juventus", "Napoli", "Roma", "Lazio",
]

DIVISIONS = ["SYN-ENG", "SYN-GER", "SYN-ITA"]


def _prices_from_probabilities(probs: list[float], margin: float) -> list[float]:
    """Turn probabilities into quoted odds with a proportional margin."""
    return [round(1.0 / (p * (1.0 + margin)), 2) for p in probs]


def synthetic_fixtures(n: int = 120, seed: int = 20261105) -> list[Fixture]:
    rng = random.Random(seed)
    out: list[Fixture] = []
    for i in range(n):
        div = DIVISIONS[i % len(DIVISIONS)]
        home = rng.choice(TEAMS)
        away = rng.choice([t for t in TEAMS if t != home])
        strength = rng.gauss(0.0, 0.55)
        raw = [1.0 + max(0.05, strength * 0.35), 1.0, 1.0 + max(0.05, -strength * 0.35)]
        total = sum(raw)
        probs = [r / total for r in raw]

        books = {}
        for name, margin in (("B365", 0.045), ("Pinnacle", 0.022), ("Max", 0.0), ("Avg", 0.035)):
            jitter = [p * (1 + rng.gauss(0, 0.012)) for p in probs]
            scale = sum(jitter)
            books[name] = _prices_from_probabilities([j / scale for j in jitter], margin)

        # Max must exceed the average by construction, as it does in the real corpus.
        books["Max"] = [round(max(books[k][j] for k in ("B365", "Pinnacle", "Avg")), 2)
                        for j in range(3)]

        # Over/under 2.5, so demo mode can exercise the same-match cross-market case.
        over = 0.45 + 0.25 * (strength / 3.0)
        over = min(0.8, max(0.2, over))
        totals = {}
        for name, margin in (("Max", 0.0), ("Avg", 0.03)):
            pair = [1.0 / (over * (1 + margin)), 1.0 / ((1 - over) * (1 + margin))]
            totals[name] = [round(x, 2) for x in pair]

        out.append(Fixture(
            div=div,
            # Match-days, not one fixture per day: a slip needs several matches on the same date.
            date=f"{1 + (i // 8) % 28:02d}/0{1 + (i // 8) % 9}/2023",
            home=home,
            away=away,
            odds=books,
            totals=totals,
            score=(rng.randint(0, 3), rng.randint(0, 3)),
        ))
    return out
