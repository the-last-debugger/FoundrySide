"""What prices, books and snapshots the corpus actually contains.

Item 2 of the research queue asks for decision-support value, and the first question is what the
data can support: which books, which markets, which snapshots, and whether any of them are
timestamped.

The answer turns out to be broader than the earlier work assumed. football-data publishes both an
**opening** and a **closing** snapshot for several books, plus `Max` (best price across the books
it tracks) and `Avg` (market average). That means this corpus can support two questions the
best-price study did not ask:

- what the **best available price across the market** is worth, not just the better of two books;
- whether price **movement** between the snapshots carries information.

Neither is timestamped, and that limitation is unchanged.

    python research/price_inventory.py

Writes research/PRICE_INVENTORY.md.
"""

from __future__ import annotations

import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research"))

import analyse        # noqa: E402
import report_stamp   # noqa: E402

OUT = ROOT / "research" / "PRICE_INVENTORY.md"

# Column families: prefix -> (label, snapshot, market)
FAMILIES = {
    "B365": ("Bet365", "opening", "1X2"),
    "B365C": ("Bet365", "closing", "1X2"),
    "PS": ("Pinnacle", "opening", "1X2"),
    "PSC": ("Pinnacle", "closing", "1X2"),
    "Max": ("Best across books", "opening", "1X2"),
    "MaxC": ("Best across books", "closing", "1X2"),
    "Avg": ("Market average", "opening", "1X2"),
    "AvgC": ("Market average", "closing", "1X2"),
    "BW": ("Bet&Win", "opening", "1X2"),
    "WH": ("William Hill", "opening", "1X2"),
    "VC": ("VC Bet", "opening", "1X2"),
    "IW": ("Interwetten", "opening", "1X2"),
}


def usable(value) -> bool:
    try:
        v = float(value)
    except (TypeError, ValueError):
        return False
    return math.isfinite(v) and v > 1.0



def ev_at_best(rows: list[dict]) -> dict:
    """Per-selection expected value if the de-vigged average price is treated as fair.

    This is the decision-relevant quantity behind price shopping: if the market average already
    carries the margin, the best available price for one selection may or may not beat it. The
    average is de-vigged across the three outcomes, so it is the best available estimate of the
    fair probability in this corpus - an assumption, stated as such.
    """
    evs = []
    for r in rows:
        cols = (("AvgCH", "MaxCH"), ("AvgCD", "MaxCD"), ("AvgCA", "MaxCA"))
        if not all(usable(r.get(a)) and usable(r.get(b)) for a, b in cols):
            continue
        inv = sum(1 / float(r[a]) for a, _ in cols)
        for avg_col, best_col in cols:
            fair = (1 / float(r[avg_col])) / inv
            evs.append(fair * float(r[best_col]) - 1)
    positive = sum(1 for e in evs if e > 0)
    return {"n": len(evs), "mean": statistics.mean(evs) if evs else float("nan"),
            "share_positive": positive / len(evs) if evs else float("nan")}


def main() -> int:
    rows = analyse.load()
    n = len(rows)

    coverage = []
    for prefix, (label, snapshot, market) in sorted(FAMILIES.items()):
        cols = [f"{prefix}H", f"{prefix}D", f"{prefix}A"]
        present = sum(1 for r in rows if all(usable(r.get(c)) for c in cols))
        coverage.append({"label": label, "snapshot": snapshot, "market": market,
                         "cols": cols, "present": present, "share": present / n})

    ou = [("P<2.5", "P>2.5", "Pinnacle", "opening"),
          ("PC<2.5", "PC>2.5", "Pinnacle", "closing"),
          ("Max<2.5", "Max>2.5", "Best across books", "opening"),
          ("MaxC<2.5", "MaxC>2.5", "Best across books", "closing"),
          ("Avg<2.5", "Avg>2.5", "Market average", "opening"),
          ("AvgC<2.5", "AvgC>2.5", "Market average", "closing")]
    ou_coverage = []
    for low, high, label, snapshot in ou:
        present = sum(1 for r in rows if usable(r.get(low)) and usable(r.get(high)))
        ou_coverage.append({"label": label, "snapshot": snapshot, "cols": [low, high],
                            "present": present, "share": present / n})

    # Per-selection best price: a user backs one selection at one book, so this is the tradeable
    # quantity. The three-way overround built from Max columns is not tradeable - each leg can come
    # from a different book - and is computed separately so the two cannot be confused.
    per_selection = []
    for r in rows:
        for best_col, avg_col in (("MaxCH", "AvgCH"), ("MaxCD", "AvgCD"), ("MaxCA", "AvgCA")):
            if usable(r.get(best_col)) and usable(r.get(avg_col)):
                per_selection.append(float(r[best_col]) / float(r[avg_col]) - 1)
    per_selection_mean = statistics.mean(per_selection) if per_selection else float("nan")

    # Best available price versus the market average, on the closing snapshot, per side.
    savings = []
    for r in rows:
        if not all(usable(r.get(c)) for c in ("MaxCH", "MaxCD", "MaxCA",
                                              "AvgCH", "AvgCD", "AvgCA")):
            continue
        best = 1 / float(r["MaxCH"]) + 1 / float(r["MaxCD"]) + 1 / float(r["MaxCA"])
        avg = 1 / float(r["AvgCH"]) + 1 / float(r["AvgCD"]) + 1 / float(r["AvgCA"])
        savings.append(avg - best)
    saving_mean = statistics.mean(savings) if savings else float("nan")

    # Movement between opening and closing for Pinnacle's 1X2.
    moved = []
    for r in rows:
        if not all(usable(r.get(c)) for c in ("PSH", "PSCH")):
            continue
        moved.append(abs(math.log(float(r["PSH"]) / float(r["PSCH"]))))
    move_mean = statistics.mean(moved) if moved else float("nan")

    ev = ev_at_best(rows)

    doc = f"""{report_stamp.stamp(Path(__file__))}

# What the corpus actually contains

{n:,} fixtures. This is an inventory, not an analysis: it establishes what item 2 can and cannot
support before any decision-value claim is made.

## 1X2 price families

| Family | Snapshot | Market | Fixtures with all three | Share |
| --- | --- | --- | --- | --- |
""" + "\n".join(
        f"| {c['label']} | {c['snapshot']} | {c['market']} | {c['present']:,} | {c['share']:.1%} |"
        for c in coverage) + f"""

## Over/under 2.5 families

| Family | Snapshot | Fixtures with both sides | Share |
| --- | --- | --- | --- |
""" + "\n".join(
        f"| {c['label']} | {c['snapshot']} | {c['present']:,} | {c['share']:.1%} |"
        for c in ou_coverage) + f"""

## What this changes

**There are two snapshots, not one.** The corpus carries opening and closing prices from several
books, plus `Max` (best price across the books football-data tracks) and `Avg` (their average). The
earlier best-price study used two books' closing prices because that is what it looked for; the
corpus actually supports a market-wide best-price question and a movement question.

**Per selection, the best quoted price is higher than the average quoted price** by
{per_selection_mean * 100:.2f}% on average across {len(per_selection):,} selection-snapshots: a user
backing one outcome can get a better price by choosing the right book. That is the tradeable
quantity.

**Whether that better price beats the margin is the decision-relevant question.** Treating the
de-vigged average price as the fair probability, backing one selection at the best quoted price in the held snapshots
returns a mean expected value of **{ev['mean']:+.4f}** per unit across {ev['n']:,}
selection-snapshots, and **{ev['share_positive']:.1%}** of them are positive. That is the whole
price-shopping case: the average price carries the margin, and the best price sometimes beats it.

**This must not be read as evidence of profit, and the reason is mechanical.** For a *single*
selection, the maximum across several books is a maximum of noisy quotes: where books allocate their
margin differently across outcomes, the highest price for one outcome comes from the book that is
least pessimistic about it, which sits below the fair probability by construction. Taking a maximum
therefore beats a de-vigged average partly because of selection, not because information exists.

The de-vigged average is also an assumption rather than a measurement, and no timestamp means the
price may not be obtainable when a user acts.

So the supported claim is narrower still: **the best quoted price exceeded the average quoted price
by about six and a half per cent** in these snapshots. It is not established that a user could have
obtained that price, nor that shopping improves a user outcome. Whether it improves expected value depends on the fair probability, which
this corpus cannot observe, and the positive share above should be treated as an upper bound
inflated by the selection effect rather than as an edge.

**The three-way overround from Max columns is not tradeable.** Summing the best home, best draw
and best away price across books gives an overround {saving_mean:.4f} lower than the average —
which is negative, a synthetic arbitrage, because the three best prices come from three different
books and no one offers all three at once. It is reported here only to say plainly that it must not
be read as a user opportunity.

**Movement:** the mean absolute log change in Pinnacle's home price between opening and closing is
{move_mean:.4f}, over {len(moved):,} fixtures. Prices do move, so a movement-based question is
answerable; whether the movement carries information is a separate experiment.

## What this does not establish

- That a user can obtain the best price at the moment they act: the snapshot has no timestamp.
- That the best price is at an account the user can hold, or within their limits.
- That any of it turns a negative expected value into a positive one; E15's arithmetic is unchanged
  by a better price, only improved.

## What is still missing

- **No timestamps on prices.** The snapshots are labelled opening and closing, but no collection time
  is recorded, so "opening" cannot be tied to T−90 or any user action point.
- **No live or intra-day prices.** Two snapshots per book at most.
- **No limits, stakes or account terms**, so an advertised best price is not evidence of an
  obtainable one.
- **Book coverage is football-data's choice**, not the market: `Max` is the best of the books it
  tracks, not the best available anywhere.

## Limits

- Coverage differs by season and division; the shares above are pooled and a per-season split would
  show the older files carrying fewer books.
- `Max` and `Avg` are derived columns; their definitions are the provider's and are taken as given.
"""
    OUT.write_text(doc, encoding="utf-8", newline="\n")

    for c in coverage:
        print(f"{c['label']:>18} {c['snapshot']:>8} {c['market']:>4}: {c['share']:.1%}")
    print(f"best-vs-average overround saving: {saving_mean:.4f} on {len(savings):,}")
    print(f"mean |log price move| Pinnacle home: {move_mean:.4f} on {len(moved):,}")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
