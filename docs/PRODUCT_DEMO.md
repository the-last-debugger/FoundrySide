# Product demo — how to run it

A local market-companion application built on the held corpus. No network access, no accounts, no
data acquisition, no bets. It runs from the repository with the standard library only.

## Run

```bash
python -m app.server
# → http://127.0.0.1:8765
```

Options: `--port 9000`, `--host 127.0.0.1`, `--limit 500` (cap fixtures loaded), `--demo` (synthetic).

**The held corpus is not committed** — `research/data/` is gitignored, and re-downloading it would be
new data acquisition, which the standing boundaries forbid. So a clean checkout runs in demo mode:

```bash
python -m app.server --demo      # clearly-labelled synthetic fixtures
```

The interface shows a banner whenever synthetic data is in use: the arithmetic is real, the prices are
not. With the held CSV files present in `research/data/`, `python -m app.server` uses them instead and
the banner disappears.

## What it does — one engine, four views

| View | What it shows | Claim kinds used |
| --- | --- | --- |
| **Assess** | The recorded prices for a fixture and outcome, the de-vigged market probability, the price-implied probability, and the gap between the best recorded quote and the average | observed, estimated |
| **Slip** | A combination across **different matches**: joint probability, gross return, net result and full-stake loss. Same-match and duplicate selections are refused, because 1X2 outcomes of one match are mutually exclusive | estimated, hypothetical |
| **Stake & target** | Searches recorded quotes for single or two-leg combinations approaching a requested multiplier, within a tolerance, and reports the search scope. A target search, **not** a stake-structure comparison | observed, estimated, hypothetical |
| **Jackpot arithmetic** | Pool size, coverage and expected winners as a function of entrants, takeout and lines held | hypothetical |

Every number carries a tag: **observed** (a recorded quote), **estimated** (a model or a measured
constant applied to observed inputs), **hypothetical** (arithmetic over user-supplied parameters).

## What is genuinely implemented

- Proportional de-vig, overround, and per-book quote comparison over all 40 held files.
- Independence-based combination across different matches, with same-match and duplicate selections
  rejected outright rather than approximated.
- Target search over singles and same-day two-leg combinations, ranked by distance from the target.
- Pool arithmetic with explicit takeout and coverage.
- A single-page interface with no build step and no external assets.

## What is not implemented, and why

- **Any predictive model.** The evidence says a forecast from this data is worse than the price
  (23 of 24 experiments negative). Shipping one as a recommendation would contradict the record.
- **Live or timestamped prices.** The corpus has no timestamps, so the product cannot say a price was
  obtainable when a user acts. This is a data gap, not a code gap.
- **Jackpot rules, rollovers, dead heats.** No rules or per-round history were located; the jackpot
  view is arithmetic on user inputs and is labelled hypothetical.
- **Accounts, stakes, limits, bet placement.** Out of scope by boundary, permanently.
- **A dependence model beyond one ratio.** The measured ratio is a single number; the product states
  that rather than implying a full covariance model.

## Honesty rules the interface enforces

1. No figure appears without a claim-kind tag.
2. The Assess view never calls the de-vigged probability a forecast.
3. The Slip view always shows the naive product beside the corrected one, so the correction is visible.
4. The Target view says plainly that a target is a constraint, not a promise.
5. Losing means losing the full stake, shown on its own line.
6. No profitability, expected-value or user-advantage claim appears anywhere.

## Tests

```bash
python -m unittest tests.test_app_engine tests.test_app_server
```

Run exactly: `python -m unittest tests.test_app_engine tests.test_app_server` → **33 tests**.

Breakdown: 23 engine tests (de-vig arithmetic, synthetic-corpus loading, claim labelling, provenance
marking, duplicate and incompatible slip rejection, cross-match combination, stake arithmetic, target
search including the no-match path, pool arithmetic) and 10 server tests (index serving, health and
mode, fixtures, assess, unknown fixture → 400, slip, empty slip → 400, target, jackpot, path
traversal refusal). The full repository suite is `python -m unittest discover -s tests` → **237
tests**, which includes these 33.
