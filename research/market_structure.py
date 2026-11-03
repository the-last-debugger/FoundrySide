"""Market structure by division: margins and favourite accuracy.

The evaluation protocol selects over/under 2.5 for the first experiment. That choice was
made on *coverage* — whether a closing price exists — not on whether the market differs in
how hard it is to beat. This measures the second thing, from data already held.

It is descriptive. A margin is not an edge, and a division where favourites win more often is
not a division where a model can beat the price.

    python research/market_structure.py

Writes research/MARKET_STRUCTURE.md.
"""

from __future__ import annotations

import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research"))

import analyse        # noqa: E402
import report_stamp   # noqa: E402

OUT = ROOT / "research" / "MARKET_STRUCTURE.md"


def parse(row: dict) -> dict | None:
    """Usable fields from one source row, or None when a price or result is missing."""
    try:
        hg, ag = int(row["FTHG"]), int(row["FTAG"])
        one_x_two = [float(row["PSCH"]), float(row["PSCD"]), float(row["PSCA"])]
        over, under = float(row["PC>2.5"]), float(row["PC<2.5"])
    except (KeyError, TypeError, ValueError):
        return None
    if min(one_x_two) <= 1.0 or over <= 1.0 or under <= 1.0:
        return None
    return {"hg": hg, "ag": ag, "one_x_two": one_x_two, "over": over, "under": under}


def summarise(rows: list[dict]) -> dict[str, float]:
    one_x_two_margins, over_margins = [], []
    hits = 0
    for r in rows:
        one_x_two_margins.append(sum(1 / o for o in r["one_x_two"]) - 1)
        raw_over, raw_under = 1 / r["over"], 1 / r["under"]
        total = raw_over + raw_under
        over_margins.append(total - 1)
        p_over = raw_over / total
        actual_over = 1 if r["hg"] + r["ag"] >= 3 else 0
        # The favourite side is the one with the higher de-vigged probability.
        if (p_over >= 0.5) == bool(actual_over):
            hits += 1
    return {
        "n": float(len(rows)),
        "one_x_two_margin": statistics.mean(one_x_two_margins),
        "over_margin": statistics.mean(over_margins),
        "over_favourite_accuracy": hits / len(rows),
    }


def main() -> int:
    rows = analyse.load()
    by_div: dict[str, list[dict]] = {}
    for row in rows:
        parsed = parse(row)
        if parsed:
            by_div.setdefault(row["_league"], []).append(parsed)

    pooled = summarise([r for v in by_div.values() for r in v])
    lines = [
        report_stamp.stamp(Path(__file__)),
        "",
        "# Market structure by division",
        "",
        "Descriptive only. Margins and favourite accuracy are properties of the sampled",
        "closing prices, not measures of how beatable a division is.",
        "",
        "| Division | Fixtures | 1X2 margin | O/U 2.5 margin | O/U favourite accuracy |",
        "| --- | --- | --- | --- | --- |",
    ]
    for div in sorted(by_div):
        s = summarise(by_div[div])
        lines.append(f"| {div} | {int(s['n']):,} | {s['one_x_two_margin']:.2%} | "
                     f"{s['over_margin']:.2%} | {s['over_favourite_accuracy']:.1%} |")
    lines += [
        f"| **pooled** | **{int(pooled['n']):,}** | **{pooled['one_x_two_margin']:.2%}** | "
        f"**{pooled['over_margin']:.2%}** | **{pooled['over_favourite_accuracy']:.1%}** |",
        "",
        "## What the numbers say",
        "",
        "**Margins are close to uniform across these eight divisions** — 2.6% to 3.2% on 1X2",
        "and 2.9% to 3.5% on over/under 2.5. The second tier (E1) is the widest, but by three",
        "tenths of a point, not by an order of magnitude. On this evidence the \"lower",
        "divisions are softer\" hypothesis is not supported by margin: the book takes",
        "approximately the same everywhere in this set.",
        "",
        "That is a useful negative. A future coverage-gradient experiment cannot rest on",
        "\"smaller league, wider margin\" — the margin is not wider here. It would have to argue",
        "from information: fewer analysts, slower team news, thinner liquidity. None of those",
        "is measured by this table, and all eight divisions are large European competitions, so",
        "the corpus may simply not contain the kind of market the hypothesis is about.",
        "",
        "## Limits",
        "",
        "- The closing quote has no observation timestamp in the source, so these are the",
        "  recorded closing prices, not prices at a known time.",
        "- Margin is not difficulty: a low-margin market can be perfectly efficient.",
        "- One book per market. Pinnacle closing is one opinion, chosen for availability.",
        "- Favourite accuracy here is a descriptive split; no test of difference between",
        "  divisions has been run, and with these sample sizes overlapping intervals are",
        "  likely.",
    ]
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    for div in sorted(by_div):
        s = summarise(by_div[div])
        print(f"{div}: n={int(s['n'])} 1x2_margin={s['one_x_two_margin']:.3f} "
              f"ou_margin={s['over_margin']:.3f} fav={s['over_favourite_accuracy']:.3f}")
    print(f"pooled ou_margin={pooled['over_margin']:.3f}")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
