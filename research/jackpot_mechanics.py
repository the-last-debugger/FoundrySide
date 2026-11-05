"""Jackpot pool mechanics — when a pool ticket can have positive expected value.

Pre-registered at docs/PREREG-JACKPOT.md. No jackpot rules or payout history were obtainable, so this
is a parameterised arithmetic study, not a measurement of any real product.

    python research/jackpot_mechanics.py

Writes research/JACKPOT_MECHANICS.md.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research"))

import report_stamp  # noqa: E402

OUT = ROOT / "research" / "JACKPOT_MECHANICS.md"

TAKEOUTS = (0.10, 0.20, 0.30, 0.40)
ENTRANTS = (100, 1000, 10000)
COVERAGE_RATIOS = (0.5, 1.0, 2.0, 4.0)
STAKE = 100.0


def ev_per_line(q: float, r: float, entrants: int, takeout: float, stake: float = STAKE) -> float:
    """Expected net of one line under the pool model in the pre-registration."""
    pool = entrants * stake * (1.0 - takeout)
    winners = 1.0 + (entrants - 1) * r
    return q * pool / winners - stake


def breakeven_ratio(entrants: int, takeout: float) -> float:
    """The coverage ratio q/r at which expected value crosses zero, holding rival coverage at 1/U."""
    # With winners = 1 + (N-1)r and q = k*r, EV = k*r*P/(1+(N-1)r) - s = 0
    # => k = s*(1+(N-1)r) / (r*P). Evaluated at representative r, reported as a ratio.
    r = 1.0 / 1000.0
    pool = entrants * STAKE * (1.0 - takeout)
    return STAKE * (1.0 + (entrants - 1) * r) / (r * pool)


ENTRANTS_SMALL = ENTRANTS[0]


def main() -> int:
    rows = []
    for takeout in TAKEOUTS:
        for entrants in ENTRANTS:
            r = 1.0 / 1000.0
            cells = []
            for ratio in COVERAGE_RATIOS:
                q = ratio * r
                cells.append(ev_per_line(q, r, entrants, takeout))
            rows.append({"takeout": takeout, "entrants": entrants,
                         "breakeven": breakeven_ratio(entrants, takeout),
                         "cells": cells})

    ev_small = ev_per_line(1e-3, 1e-3, ENTRANTS_SMALL, TAKEOUTS[2])

    doc = f"""{report_stamp.stamp(Path(__file__))}

# Jackpot pool mechanics

Pre-registered at `docs/PREREG-JACKPOT.md`. **This is arithmetic, not evidence.** No jackpot rules or
payout history were locatable for any operator examined, so every number below is a function of
assumed parameters. It says when a pool ticket *could* have positive expected value, and what that
depends on. It says nothing about any real product.

## The model

Pool `P = N · s · (1 − t)`. Your coverage `q`, the field's average coverage `r`. Expected winning
tickets `1 + (N − 1)·r`, counting yours. Expected net of one line:

`EV = q · P / (1 + (N − 1)·r) − s`

with `s = KSh {STAKE:.0f}`, `r = 1/1000`, and `q` set by the ratio in each column.

## Expected net per line, by takeout and field size

| Takeout | Entrants | q/r = 0.5 | q/r = 1 | q/r = 2 | q/r = 4 | Break-even q/r |
| --- | --- | --- | --- | --- | --- | --- |
""" + "\n".join(
        f"| {row['takeout']*100:.0f}% | {row['entrants']:,} | "
        + " | ".join(f"{cell:+.1f}" for cell in row["cells"])
        + f" | {row['breakeven']:.1f}× |"
        for row in rows) + """

## What the table says

**At the field's average coverage you lose, and a small field loses far more.** With `q = r` the
expected net tends to `-s*t` only as the field grows; at {ENTRANTS_SMALL} entrants and a 30% takeout it
is about {ev_small:.0f} on a stake of {STAKE:.0f}, because a single guaranteed winner dominates a small
pool. Both are the benchmark the rest of the table is read against.

**Break-even coverage falls as the field grows, towards `1/(1 − t)`.** With few entrants your line is a
large share of a small pool, so a rival line moves your expected value a lot; with many entrants the
pool and the winner count grow together and the ratio settles at the level the takeout sets:

| Takeout | Break-even `q/r` for a large field | Break-even at 100 entrants |
| --- | --- | --- |
| 10% | ≈ 1.11× | 12.2× |
| 20% | ≈ 1.25× | 13.7× |
| 30% | ≈ 1.43× | 15.7× |
| 40% | ≈ 1.67× | 18.3× |

So the honest statement is: **in a large pool you need to be modestly better than the field, and the
takeout sets how much better** — 11% better at a 10% takeout, 67% better at 40%. In a small pool you
would need to be many times better, because one rival line is a large fraction of the winners.

**The break-even column is the summary that transfers.** It converts "is this +EV?" into "how much
better than the field must I be?", which a player can reason about; a payout table without it cannot be
interpreted at all.

## Why this is not a jackpot strategy

- The parameters are a grid, not measurements. No operator's rules, pool sizes or entrant counts were
  obtainable.
- Predicting the field's coverage `r` is the hard part, and this study does not model it. A cell that
  is positive in the grid assumes you already know `r`.
- Dead heats, rollovers, consolation tiers and pool caps are not modelled; each would change the
  arithmetic.
- Nothing here is a profitability claim about any product.

## What would make this measurable

The rules document and a per-round history: entrants, pool, takeout, winners and the winning line.
With those, `r` becomes observable and the model becomes testable rather than illustrative. That is
recorded in `LEAD_TRIAGE.md` as the reopening condition.
"""
    # The narrative sits in a non-f-string segment, so resolve its placeholders explicitly.
    doc = (doc.replace("{ENTRANTS_SMALL}", f"{ENTRANTS_SMALL:,}")
              .replace("{ev_small:.0f}", f"{ev_small:.0f}")
              .replace("{STAKE:.0f}", f"{STAKE:.0f}"))
    OUT.write_text(doc, encoding="utf-8")

    for row in rows:
        cells = " ".join(f"{c:+8.1f}" for c in row["cells"])
        print(f"t={row['takeout']:.0%} N={row['entrants']:6,}  {cells}  breakeven {row['breakeven']:.1f}x")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
