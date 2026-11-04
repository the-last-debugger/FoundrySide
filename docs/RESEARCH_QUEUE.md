# Research queue

Priorities set by the sponsor. Status is updated as work lands; the ledger of record is the
**experiment register** in `RESEARCH_PROGRAMME.md` and the reports themselves.

| # | Item | Priority | Status |
| --- | --- | --- | --- |
| 1 | **Disagreement-aware decision policy** — shrink toward the market as departure grows; market-only fallback; pre-declared thresholds fitted on prior seasons only | **highest** | **in progress** (`PREREG-SHRINKAGE.md`) |
| 2 | **Decision-support value, separately from accuracy** — best price, price disagreement, abstention, stake/slip risk; first establish what price snapshots and coverage actually exist | high | not started; the snapshot inventory is partly done in `SOURCE_TIMING.md` and `BEST_PRICE.md` |
| 3 | **Robustness and transfer** — does the disagreement pattern and any shrinkage rule survive across forward seasons and divisions, with small-sample honesty | medium | not started; depends on 1 |

## Rules for every item

- A short pre-registered question, method, leakage controls, baselines, metrics and stop criterion,
  written and committed **before** the experiment runs.
- Parameters fitted only on prior data within each forward fold; the evaluation season is untouched.
- The frozen confirmatory slice is never touched, and no confirmatory scoring occurs.
- Exploratory findings are labelled as such and kept separate from confirmatory evidence.
- Small, cheap, falsifiable first; reuse existing infrastructure; no new data requests or spend.
- If the corpus cannot support a question, say which question it cannot support and what minimum
  evidence would be needed, rather than manufacturing a result.

## Open checkpoints

None that block work. Item 2 contains a data-access question — which timestamped price snapshots
exist — that is already recorded as blocked in `SOURCE_TIMING.md`; the analysis proceeds on closing
prices with that limitation stated.
