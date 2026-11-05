# Product demo — how to run it

A local market-companion application built on the held corpus. No accounts, no provider contact, no
bets, no deployment. It runs from the repository with the standard library only.

Two data paths, both stated where they appear: the app runs on **synthetic demo data** out of the box,
or on the **held corpus** after `scripts/fetch_corpus.py`, which retrieves public files under the
2026-11-05 permission and records provenance. The corpus is never committed.

## Run

```bash
python -m app.server
# → http://127.0.0.1:8765
```

Options: `--port 9000`, `--host 127.0.0.1`, `--limit 500` (cap fixtures loaded), `--demo` (synthetic).

**The held corpus is not committed** — `research/data/` is gitignored. Fetching it is permitted under
the 2026-11-05 public-data permission (free, lawful, no account, provenance recorded), and
`scripts/fetch_corpus.py` does exactly that. A clean checkout that has not run the fetcher still
starts in demo mode:

```bash
python -m app.server --demo      # clearly-labelled synthetic fixtures
```

The interface shows a banner whenever synthetic data is in use: the arithmetic is real, the prices are
not.

To run on real data, fetch the public corpus once:

```bash
python scripts/fetch_corpus.py          # 40 files, one request at a time, ~40s
python -m app.server                    # now reports mode=held, 14,802 fixtures
```

`fetch_corpus.py` writes `research/data/PROVENANCE.json` recording the source, the retrieval time, the
file list with fixture counts, the licence position (internal analysis only; no redistribution, P-03
open) and the fact that files are stored as received. It does not overwrite existing files without
`--force`, and it reports missing files rather than failing.

## What it does — one engine, seven tabs

| View | What it shows | Claim kinds used |
| --- | --- | --- |
| **Assess** | The recorded prices for a fixture and outcome, the de-vigged market probability, the price-implied probability, and the gap between the best recorded quote and the average | observed, estimated |
| **Market** | Every book we hold a quote for, with its own margin and de-vigged probabilities, plus the price spread per outcome. A negative margin on the Max row is labelled a synthetic artefact, not an arbitrage | observed, estimated |
| **Slip** | A combination across **different matches**: joint probability, gross return, net result and full-stake loss. A same-match pair is accepted only across different markets (result with over/under), and its joint is **not** estimated because the measured 1.49 ratio is a population average; two selections from one market are refused as mutually exclusive | estimated, hypothetical |
| **Stake & target** | Searches recorded quotes for single or two-leg combinations approaching a requested multiplier, within a tolerance, and reports the search scope. A target search, **not** a stake-structure comparison | observed, estimated, hypothetical |
| **Structures** | Two or more structures matched on the same net profit: stake at risk, gross, market-implied hit rate, expected loss and variance side by side. Backed by E25 | observed, estimated, hypothetical |
| **Jackpot arithmetic** | Pool size, your coverage, and expected winning tickets only if you supply a rival-coverage assumption | hypothetical |
| **Export** | Any assessment can be copied as a JSON or plain-text card that carries its claim kinds and caveats | — |
| **Journal** | Record an assessment as it was made, then settle recorded assessments against held results: accuracy and mean Brier, with the caveat that a hit rate is not an edge | observed |

Every number carries a tag: **observed** (a recorded quote), **estimated** (a model or a measured
constant applied to observed inputs), **hypothetical** (arithmetic over user-supplied parameters).

## Interface

Single page, no build step, no external assets. A header carries the product and a **mode badge** that
says whether you are looking at the held corpus or synthetic demo data. Seven tabs: Assess, Market, Slip, Structures,
Stake &amp; target, Jackpot, Journal.

Design choices that serve the honesty requirement rather than decoration:

- every value carries a **claim-kind tag** (observed / estimated / hypothetical) beside it;
- probability meters and price bars make magnitudes comparable at a glance, so a 0.3% and a 30%
  cannot be confused;
- results are ria-live regions, tabs are a proper 	ablist operable with arrow keys, Home and
  End, and prefers-reduced-motion is respected;
- loading states are labelled, so an empty panel reads as working rather than broken.

## What is genuinely implemented

- Proportional de-vig, overround, and per-book quote comparison over all 40 held files.
- Independence-based combination across different matches, with same-match and duplicate selections
  rejected outright rather than approximated.
- Target search over singles and same-day two-leg combinations, ranked by distance from the target.
- Pool arithmetic with explicit takeout and coverage.
- A single-page interface with no build step and no external assets.
- An exportable assessment card, in JSON or plain text, that carries the claim kinds and caveats so a
  price cannot travel without its qualifications.
- A polite public-corpus fetcher with recorded provenance.
- An assessment journal (local JSONL under ar/, gitignored) that stores the quote, claim kinds and
  caveats as recorded, and settles them against held results without ever rewriting the entry.

## What is not implemented, and why

- **Any predictive model.** The evidence says a forecast from this data is worse than the price
  (24 of 25 experiments negative). Shipping one as a recommendation would contradict the record.
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

Reproduced at the revision named in the CI line below, not copied from a previous run.

```bash
python -m unittest tests.test_app_engine tests.test_app_server tests.test_app_export \
                   tests.test_fetch_corpus tests.test_app_journal tests.test_app_market \
                   tests.test_app_explanations tests.test_app_structures
# Ran 76 tests … OK

python -m unittest discover -s tests
# Ran 308 tests … OK
```

The 75 product tests break down as: **23** engine, **12** server, **5** export, **4** fetcher,
**11** journal, **4** market, **7** explanations, **9** structures. The remaining 221 are the research suite that
predates the product (report stamps, claims, bridge, audit, reproducibility and the studies
themselves).

CI on the same revision: workflow run **130** on `3b6944a`, all steps green — test suite, bridge
consistency, repository audit, verification transcript. `.github` runs the full suite on every push.

## Growth management

The journal is append-only, which is a correctness property and also how a file grows without bound.
Re-recording the same fixture, outcome and quote adds no information, so duplicates can be removed
while every distinct record is kept in order:

`ash
python scripts/journal_tool.py --stats
python scripts/journal_tool.py --compact --dry-run
python scripts/journal_tool.py --compact
`

scripts/audit.py reports the corpus and journal footprint on every run and flags the thresholds where
growth needs a decision (50 MB of corpus, 5 MB of journal). The corpus itself is never committed:

esearch/data is gitignored and ar/ holds only local state.
