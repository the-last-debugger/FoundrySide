"""FoundrySide market companion — the shared assessment engine.

One engine, several views. Every number it returns is tagged with the kind of claim it makes, because
the product's central risk is that a price observation gets read as a probability edge:

    observed      a recorded quote or result in the held corpus
    estimated     a model or a measured constant applied to observed inputs
    hypothetical  a user-supplied scenario, arithmetic over assumed parameters

No function here claims profitability, expected value or an obtainable price. The corpus has no
timestamps, no account terms and no limits, so those claims are unavailable by construction.

Run the app with:  python -m app.server
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "research" / "data"

# Measured in this project, not assumed. See docs/CONSOLIDATED_FINDINGS.md.
# Same-match joint outcomes run ~1.49x the product of the marginals; different matches ≈ 1.0.
SAME_MATCH_DEPENDENCE = 1.49
CROSS_MATCH_DEPENDENCE = 1.00

OUTCOMES = ("H", "D", "A")
OUTCOME_LABEL = {"H": "Home", "D": "Draw", "A": "Away"}

BOOKS = {
    "B365": ("B365CH", "B365CD", "B365CA"),
    "Pinnacle": ("PSCH", "PSCD", "PSCA"),
    "Max": ("MaxCH", "MaxCD", "MaxCA"),
    "Avg": ("AvgCH", "AvgCD", "AvgCA"),
}


def _num(value) -> float | None:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) and out > 1.0 else None


def devig(odds: tuple[float, float, float] | list[float]) -> list[float]:
    """Proportional de-vig: implied probabilities renormalised to sum to one.

    This is an assumption about how a book spreads its margin, not a measurement of its beliefs.
    """
    inv = [1.0 / o for o in odds]
    total = sum(inv)
    return [x / total for x in inv]


def overround(odds) -> float:
    return sum(1.0 / o for o in odds) - 1.0


@dataclass
class Fixture:
    div: str
    date: str
    home: str
    away: str
    odds: dict[str, list[float]] = field(default_factory=dict)
    score: tuple[int, int] | None = None

    @property
    def key(self) -> str:
        return f"{self.div}|{self.date}|{self.home}|{self.away}"

    @property
    def label(self) -> str:
        return f"{self.home} v {self.away}"


def load_fixtures(limit: int | None = None) -> list[Fixture]:
    """Read the held corpus. Files are the ones already in the repository; nothing is fetched."""
    out: list[Fixture] = []
    for path in sorted(DATA.glob("*.csv")):
        div = path.stem.split("_")[0]
        with open(path, encoding="latin-1") as handle:
            for row in csv.DictReader(handle):
                odds: dict[str, list[float]] = {}
                for name, cols in BOOKS.items():
                    vals = [_num(row.get(c)) for c in cols]
                    if all(v is not None for v in vals):
                        odds[name] = vals  # type: ignore[assignment]
                if len(odds) < 2:
                    continue
                score = None
                try:
                    score = (int(row["FTHG"]), int(row["FTAG"]))
                except (KeyError, TypeError, ValueError):
                    pass
                out.append(Fixture(div=div, date=row.get("Date", ""),
                                   home=row.get("HomeTeam", ""), away=row.get("AwayTeam", ""),
                                   odds=odds, score=score))
                if limit and len(out) >= limit:
                    return out
    return out


def market_view(fixture: Fixture) -> dict:
    """What the recorded quotes imply, with the claim kinds separated."""
    if "Avg" not in fixture.odds:
        raise ValueError("fixture has no market-average quote")
    avg = fixture.odds["Avg"]
    fair = devig(avg)
    best = fixture.odds.get("Max", avg)
    best_probs = devig(best)

    quotes = {}
    for name, odds in fixture.odds.items():
        quotes[name] = {
            "odds": [round(o, 3) for o in odds],
            "overround": round(overround(odds), 4),
            "implied": [round(p, 4) for p in devig(odds)],
        }

    gap = [best[i] / avg[i] - 1.0 for i in range(3)]
    return {
        "fixture": fixture.label,
        "key": fixture.key,
        "division": fixture.div,
        "date": fixture.date,
        "score": fixture.score,
        "quotes": quotes,
        "market_implied": {o: round(fair[i], 4) for i, o in enumerate(OUTCOMES)},
        "best_quote_implied": {o: round(best_probs[i], 4) for i, o in enumerate(OUTCOMES)},
        "best_vs_average": {o: round(gap[i], 4) for i, o in enumerate(OUTCOMES)},
        "claims": {
            "quotes": "observed — recorded closing quotes in the held corpus",
            "market_implied": "estimated — proportional de-vig of the recorded average; an assumption",
            "best_vs_average": "observed arithmetic — a difference between recorded quotes, "
                               "not a price shown to be obtainable",
        },
        "caveats": [
            "No timestamps: these are closing snapshots, not prices available when a user acts.",
            "No account terms, limits or stakes: a quote is not proof of an obtainable price.",
            "The de-vigged probability is a model of the market's belief, not a forecast of ours.",
        ],
    }


def assess_selection(fixture: Fixture, outcome: str) -> dict:
    """A standalone assessment: the price, what it implies, and what it does not establish."""
    if outcome not in OUTCOMES:
        raise ValueError(f"outcome must be one of {OUTCOMES}")
    view = market_view(fixture)
    idx = OUTCOMES.index(outcome)
    quotes = {name: q["odds"][idx] for name, q in view["quotes"].items() if name != "Avg"}
    if not quotes:
        raise ValueError("no individual quotes for this fixture")
    best_book = max(quotes, key=lambda n: quotes[n])
    price = quotes[best_book]
    fair = view["market_implied"][outcome]
    implied = 1.0 / price

    return {
        "fixture": fixture.label,
        "outcome": outcome,
        "outcome_label": OUTCOME_LABEL[outcome],
        "best_recorded_price": price,
        "best_book": best_book,
        "all_prices": quotes,
        "market_implied": fair,
        "price_implied": round(implied, 4),
        "price_vs_market": round(implied - fair, 4),
        "claims": {
            "best_recorded_price": "observed — the highest recorded closing quote for this outcome",
            "market_implied": "estimated — de-vigged average quote under proportional de-vig",
            "price_implied": "observed arithmetic — 1/price, which includes the book's margin",
        },
        "assessment": (
            "The recorded best quote is above the market average. That is a property of the quotes. "
            "This corpus cannot show the price was obtainable, nor that it beats fair value."
        ),
        "abstain": False,
    }


def slip_view(legs: list[dict], stake: float) -> dict:
    """Combine legs across **different matches**, where independence is a reasonable assumption.

    Same-match combinations are rejected rather than approximated, because the 1X2 outcomes of one
    match are mutually exclusive: Home and Draw cannot both win. The 1.49 dependence figure measured
    in this project is an aggregate ratio of realised joint frequency to the product of marginals for
    *different markets* on the same match (1X2 versus over/under). It is not a conditional
    probability for two 1X2 selections, and applying it to them — which an earlier version of this
    function did — produces a meaningless number. It is kept as documentation, not as a multiplier.
    """
    if not legs:
        raise ValueError("a slip needs at least one leg")
    if stake <= 0:
        raise ValueError("stake must be positive")

    seen_pairs = set()
    seen_fixtures = set()
    for leg in legs:
        pair = (leg["fixture_key"], leg["outcome"])
        if pair in seen_pairs:
            raise ValueError(
                "duplicate selection: the same outcome twice on one match is one selection, not two")
        seen_pairs.add(pair)
        if leg["fixture_key"] in seen_fixtures:
            raise ValueError(
                "same-match combination unsupported: two 1X2 outcomes of one match are mutually "
                "exclusive, so their joint probability is zero, not a corrected product")
        seen_fixtures.add(leg["fixture_key"])

    naive = 1.0
    for leg in legs:
        naive *= leg["prob"]

    combined_odds = 1.0
    for leg in legs:
        combined_odds *= leg["price"]
    gross = stake * combined_odds

    return {
        "legs": len(legs),
        "naive_product": round(naive, 6),
        "joint_probability": round(naive, 6),
        "dependence_ratio": CROSS_MATCH_DEPENDENCE,
        "same_match": False,
        "combined_odds": round(combined_odds, 3),
        "stake": stake,
        "gross_return": round(gross, 2),
        "net_result": round(gross - stake, 2),
        "full_stake_loss": round(stake, 2),
        "claims": {
            "naive_product": "estimated — product of de-vigged market probabilities across matches",
            "joint_probability": "estimated — valid only because the legs are from different matches",
            "gross_return": "hypothetical — arithmetic on the recorded quotes and the user's stake",
        },
        "caveats": [
            "Independence across matches is assumed here. It is a reasonable approximation for "
            "different fixtures and is not tested by this view.",
            "Same-match combinations are refused: 1X2 outcomes on one match are mutually exclusive.",
            "The 1.49 same-match ratio in this project is an aggregate illustration for different "
            "markets on one match; it is not a valid multiplier for two 1X2 selections.",
            "Gross return uses recorded closing quotes, which are not shown to be obtainable.",
        ],
    }


def target_search(stake: float, target_multiplier: float, tolerance: float = 0.15,
                  fixtures: list[Fixture] | None = None, max_legs: int = 2,
                  pair_pool_limit: int = 400) -> dict:
    """Find the closest achievable combination to a user's requested multiplier.

    The target is a constraint to search against, never a promise. If nothing is close enough, the
    honest answer is that there is no responsible match.
    """
    if stake <= 0 or target_multiplier <= 1.0:
        raise ValueError("stake must be positive and the target multiplier above 1")
    pool = fixtures if fixtures is not None else load_fixtures()
    lo, hi = target_multiplier * (1 - tolerance), target_multiplier * (1 + tolerance)

    singles = []
    for fx in pool:
        if "Max" not in fx.odds:
            continue
        probs = devig(fx.odds["Avg"]) if "Avg" in fx.odds else devig(fx.odds["Max"])
        for i, outcome in enumerate(OUTCOMES):
            price = fx.odds["Max"][i]
            if lo <= price <= hi:
                singles.append({
                    "kind": "single", "legs": 1, "label": fx.label, "outcome": outcome,
                    "price": round(price, 3), "probability": round(probs[i], 4),
                    "fixture_key": fx.key,
                })

    doubles = []
    pool_with_prices = [fx for fx in pool if "Max" in fx.odds]
    usable = pool_with_prices[:pair_pool_limit]
    if max_legs >= 2:
        for a in range(len(usable)):
            for b in range(a + 1, len(usable)):
                fa, fb = usable[a], usable[b]
                if fa.date != fb.date:
                    continue
                probs_a = devig(fa.odds["Avg"]) if "Avg" in fa.odds else devig(fa.odds["Max"])
                probs_b = devig(fb.odds["Avg"]) if "Avg" in fb.odds else devig(fb.odds["Max"])
                for i, oa in enumerate(OUTCOMES):
                    for j, ob in enumerate(OUTCOMES):
                        combo = fa.odds["Max"][i] * fb.odds["Max"][j]
                        if lo <= combo <= hi:
                            doubles.append({
                                "kind": "double", "legs": 2,
                                "label": f"{fa.label} ({oa}) + {fb.label} ({ob})",
                                "outcome": f"{oa}+{ob}",
                                "price": round(combo, 3),
                                "probability": round(probs_a[i] * probs_b[j], 5),
                                "fixture_key": f"{fa.key}+{fb.key}",
                            })

    candidates = singles + doubles
    for cand in candidates:
        cand["distance"] = round(abs(math.log(cand["price"] / target_multiplier)), 4)
        cand["gross_return"] = round(stake * cand["price"], 2)
        cand["net_result"] = round(stake * cand["price"] - stake, 2)
    candidates.sort(key=lambda c: c["distance"])

    return {
        "stake": stake,
        "target_multiplier": target_multiplier,
        "tolerance": tolerance,
        "matches": candidates[:8],
        "found": bool(candidates),
        "search_scope": {
            "fixtures_considered": len(pool),
            "fixtures_with_prices": len(pool_with_prices),
            "fixtures_used_for_pairs": len(usable),
            "pair_pool_limited": len(pool_with_prices) > len(usable),
        },
        "claims": {
            "matches": "hypothetical — combinations of recorded quotes that approach the target",
            "probability": "estimated — product of de-vigged market probabilities; same-day legs "
                           "from different matches are treated as independent in this view",
        },
        "verdict": (
            "No responsible match within tolerance. The target is a constraint, not a promise: a "
            "multiplier the market does not offer is not made available by searching harder."
            if not candidates else
            "Closest matches are shown. A higher multiplier is not better value: it trades a smaller "
            "hit probability for a larger gross return, and the net result on a loss is the full stake."
        ),
        "caveats": [
            "Targets are user constraints. Nothing here implies the target is attainable or wise.",
            "Gross return is not profit; a losing slip returns nothing and costs the full stake.",
            "Doubles pair different matches on the same day only; same-match combinations are refused.",
            "The double search covers a bounded slice of the corpus, reported as search_scope; it is "
            "not an exhaustive search of every fixture.",
        ],
    }


def jackpot_view(entrants: int, stake: float, takeout: float, your_lines: int,
                 outcomes_per_match: int = 3, matches: int = 6,
                 rival_coverage: float | None = None) -> dict:
    """Pool arithmetic. Hypothetical by construction: this corpus holds no jackpot rules or history.

    Two quantities that an earlier version conflated:

    - **your coverage** — the share of possible lines you hold. This is about you, and needs no
      assumption about anyone else.
    - **expected winning tickets** — a pool-wide quantity. It depends on how many lines *other*
      entrants hold, which is not knowable from your own coverage. It is reported only when the caller
      supplies an explicit `rival_coverage` assumption, and never floored at one.
    """
    if entrants <= 0 or stake <= 0 or not 0 <= takeout < 1:
        raise ValueError("entrants and stake must be positive; takeout in [0,1)")
    if your_lines <= 0:
        raise ValueError("your_lines must be positive")
    if rival_coverage is not None and not 0 <= rival_coverage <= 1:
        raise ValueError("rival_coverage must be in [0,1]")

    pool = entrants * stake * (1 - takeout)
    universe = outcomes_per_match ** matches
    coverage = min(1.0, your_lines / universe)

    expected_winners = None
    if rival_coverage is not None:
        # Other entrants only; your own ticket is not a rival.
        expected_winners = round((entrants - 1) * rival_coverage, 2)

    return {
        "pool": round(pool, 2),
        "universe_of_lines": universe,
        "your_lines": your_lines,
        "coverage": round(coverage, 8),
        "rival_coverage": rival_coverage,
        "expected_winning_tickets": expected_winners,
        "claims": {
            "pool": "hypothetical — entrants x stake x (1 - takeout); the takeout is user-supplied",
            "coverage": "hypothetical — your lines over the line universe",
            "expected_winning_tickets": "hypothetical — requires the rival_coverage assumption; "
                                        "omitted when it is not supplied",
        },
        "verdict": (
            "Pool value depends on how many other entrants share it, which your own line count says "
            "nothing about. This corpus holds no jackpot rules or payout history, so none of this is "
            "a measured jackpot advantage."
        ),
        "caveats": [
            "No jackpot rules or per-round history were located; these are arithmetic, not evidence.",
            "Expected winners is omitted unless you supply a rival-coverage assumption.",
            "Dead heats, rollovers, consolation tiers and pool caps are not modelled.",
        ],
    }
