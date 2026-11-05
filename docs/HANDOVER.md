# Handover

One page. What exists, how to verify it, what it does not claim, and what to do next.

## What was asked, and what was delivered

| Direction | Outcome |
|---|---|
| Find a way to beat the closing price | **Closed.** 25 experiments; the model is worse than the market on log loss, ranking and the hard pick. `CONCLUSION.md` |
| Build a market-intelligence capability instead | **Delivered as a local demonstrator**, `app/`, seven tabs, no external assets |
| Answer the stake/multiplier question | **Answered.** E25: matched on net, higher odds risks less, wins less often, loses less in expectation; neither is better value |
| Keep the record honest | Guaranteed by tests, an audit, and pre-registrations committed before each run |

## Run it

```bash
python scripts/fetch_corpus.py      # public corpus + provenance (~40s, optional)
python -m app.server                # http://127.0.0.1:8765
python -m app.server --demo         # synthetic, clearly labelled, no download
```

Seven tabs: Assess, Market, Slip, Structures, Stake & target, Jackpot, Journal.

## Verify it

```bash
python -m unittest discover -s tests    # 296 tests
python scripts/audit.py                 # 10 cross-document checks
python scripts/collab_check.py          # bridge consistency
python scripts/verify_all.py --full     # tests + clone + 34-generator sweep (~21 min)
```

Latest CI: see `docs/CI_EVIDENCE.md`, regenerated from the Actions API rather than typed.

## What the numbers are

| Quantity | Value | Where |
|---|---|---|
| Model versus market, matched sample | 54.30% vs 57.66% accuracy, −0.0336 | `HIT_RATE_AUDIT.md` |
| Deployable recalibration gain | +0.0102 nats forward | `FORWARD_CALIBRATION.md` |
| Best quoted versus average quoted price | 6.51% per selection-snapshot | `PRICE_INVENTORY.md` |
| Same-match dependence (different markets) | 1.49× | `RESULTS_T0_T1_T3.md` |
| Thin divisions versus the eight | +0.0017 nats | `THIN_DIVISIONS.md` |
| Same net upside, stake at 1.5 vs 6 | KSh 357 vs KSh 41 | `STAKE_STRUCTURES.md` |

## What it does not claim

- **No edge.** No forecast here beats the price; the product is explicit that it shows the market, not a prediction.
- **No obtainable price.** The corpus has no timestamps, account terms or limits, so a recorded maximum is a historical fact.
- **No profitability.** Every expected-net figure is negative under a margin.
- **No jackpot advantage.** No rules or payout history were located; that view is arithmetic on user inputs.

## What is protected

- **P-02**, the 5,794-fixture confirmatory slice: untouched, unscored, unexamined.
- **The dispersion study**: pre-registered, amended for the missing `Bb1X2` field, **not run** — it needs fresh approval.
- **Track A**: closed, with written reopening conditions.

## Known gaps, in order of importance

1. **No timestamped prices.** Every honest caveat traces to this. It needs a licensed or clearly-permitted source; nothing searched was both.
2. **Jackpot rules are gated.** Operator pages are script-rendered behind age gates; reading them would need interactive acceptance of terms.
3. **Dependence is one measured ratio**, for different markets on one match; the product refuses same-match 1X2 combinations rather than approximating them.
4. **The demonstrator is local only.** No deployment, hosting or accounts, by boundary.

## Next best steps

1. **A lawful timestamped source** — the single thing that would unlock both the price claim and the dispersion study's `K`.
2. **Run the dispersion study** once approved; it is one bounded analysis and its inputs are now specified.
3. **A user study**, if decision support is to be claimed as benefit rather than asserted.

## Where the record lives

- `docs/CONSOLIDATED_FINDINGS.md` — the findings in one place
- `docs/RESEARCH_PROGRAMME.md` — the 25-experiment register
- `docs/COLLAB/THREAD.md` — the full review history
- `docs/COLLAB/REVIEW_QUEUE.md` + `docs/REVIEW_DIGEST.md` — what is accepted, what awaits review
- `docs/CI_EVIDENCE.md` — generated run history
