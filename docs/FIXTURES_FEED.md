# The fixtures gap, with evidence

The planner can price a slip but cannot see an unplayed fixture. This records exactly what is and is
not obtainable, so the limitation is a documented finding rather than a vague caveat.

Reproduce with `python scripts/check_fixtures.py`.

## What exists, free and lawful

`https://raw.githubusercontent.com/openfootball/football.json/master/<season>/en.1.json` — a public
GitHub repository of football data, no account, no key, no terms to accept.

Checked 2026-11-08:

| Season | Fixtures | Played | Unplayed | Dated on or after today | Odds present |
| --- | --- | --- | --- | --- | --- |
| 2026-27 | 380 | 50 | **330** | **280** | **No** |
| 2025-26 | 380 | 380 | 0 | 0 | No |

Each fixture carries `round`, `date`, `time`, `team1`, `team2` and, once played, a score. There is **no
odds field of any kind**.

## The consequence, stated plainly

A fixture list without prices cannot price a slip. The planner needs a probability for each outcome,
and this project's only lawful source of probabilities is the recorded closing odds from
football-data.co.uk — which are published **after** a match is played.

So the product can either:

- **price a slip on recorded fixtures** (what it does today: the latest match-day in the corpus), or
- **list an unplayed fixture** (what the openfootball file allows), but not price it.

It cannot do both, and nothing in this repository pretends otherwise.

## What would close the gap

A lawful, free, **pre-match** odds source. The categories to examine, in order of plausibility:

1. **A public odds API with a free tier** — several exist, but all require an account and an API key,
   which is outside the standing permission.
2. **A bookmaker's public price page** — present in public HTML, but reading it at scale is scraping,
   and the terms of the sites examined do not clearly permit it.
3. **A public dataset refreshed daily** — none found; the openfootball family carries results and
   fixtures, not prices.
4. **Manual entry** — a user typing the prices they can see. Honest, lawful, and small: it would let
   the planner run on a real unplayed card without any acquisition at all.

Option 4 is the only one available under the current boundaries, and it is a genuine product feature
rather than a workaround: the user is the one with the screen open, and their input makes the plan
prospective.

## What this does not change

The record remains honest either way. A plan made against recorded fixtures is a demonstration; a plan
made against manually entered prices for an unplayed card is a testable claim, and the journal would
settle it after the fact.
