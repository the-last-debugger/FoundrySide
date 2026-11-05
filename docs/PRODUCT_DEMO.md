# Product demo — how to run it

A local market-companion application built on the held corpus. No network access, no accounts, no
data acquisition, no bets. It runs from the repository with the standard library only.

## Run

```bash
python -m app.server
# → http://127.0.0.1:8765
```

Options: `--port 9000`, `--host 127.0.0.1`, `--limit 500` (cap fixtures loaded).

Requires the held corpus at `research/data/*.csv` (already in the repository, 40 files). If that
directory is missing the server prints a message and exits rather than starting empty.

## What it does — one engine, four views

| View | What it shows | Claim kinds used |
| --- | --- | --- |
| **Assess** | The recorded prices for a fixture and outcome, the de-vigged market probability, the price-implied probability, and the gap between the best recorded quote and the average | observed, estimated |
| **Slip** | A combination's joint probability with a dependence correction instead of naive multiplication, plus gross return, net result and full-stake loss | estimated, hypothetical |
| **Stake & target** | Searches recorded quotes for single or two-leg combinations that approach a requested multiplier, within a tolerance; reports hit probability, gross, net and risk; says so when nothing is close | observed, estimated, hypothetical |
| **Jackpot arithmetic** | Pool size, coverage and expected winners as a function of entrants, takeout and lines held | hypothetical |

Every number carries a tag: **observed** (a recorded quote), **estimated** (a model or a measured
constant applied to observed inputs), **hypothetical** (arithmetic over user-supplied parameters).

## What is genuinely implemented

- Proportional de-vig, overround, and per-book quote comparison over all 40 held files.
- Dependence correction using the measured same-match ratio (1.49) versus the cross-match case (1.00).
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

26 tests: de-vig arithmetic, corpus loading, claim labelling, dependence behaviour, stake arithmetic,
target search including the no-match path, pool arithmetic, and HTTP-level checks that the server
serves the interface and its API, returns errors rather than crashing, and refuses path traversal.
