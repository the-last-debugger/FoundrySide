# FoundrySide

A research repository with a local demonstrator.

Historically this was research only: `DECISIONS.md` D-01 recorded that building was not authorised,
and D-10 authorised independent research and research scripts. That is still the permanent position —
**no deployment, no hosting, no accounts, no real-money functionality, ever, under these boundaries.**

The 2026-11-05 day-pass (D-16) added a **time-boxed** exception for local implementation and testing at
KSh 0 cost, so that the findings could be demonstrated rather than only described. It expires after
that day's review. `docs/CONCLUSION.md` records the research result; `docs/PRODUCT_DEMO.md` describes
what the demonstrator does and does not claim.

## Start here

If you are reading this after the 2026-11-05 build, read **[docs/HANDOVER.md](docs/HANDOVER.md)** first: one page covering what exists, how to verify it, what it does not claim, and what to do next.

## Current status

**Track A (prediction) is closed.** The model is worse than the market price on every axis tested;
`docs/CONCLUSION.md` records what that does and does not establish.

**The product slice is a local demonstrator.** A seven-tab market companion runs from `python -m
app.server` over the held corpus or clearly-labelled synthetic data. It shows what recorded prices
imply — per-book margins, de-vigged probabilities, quote spreads, dependence-aware slips, target
search, pool arithmetic and an assessment journal — and it refuses to claim an edge it does not have.

**Building was authorised for one day.** The 2026-11-05 day-pass (D-16) permits local implementation
and testing within KSh 0 cost. It expires after today's review: no deployment, no hosting, no
accounts, no provider contact, no publication and no real-money functionality, then or now.

## The documents, in reading order

| Document | What it is |
| --- | --- |
| `PRE_PROPOSAL.md` | The sponsor's vision: what FoundrySide is meant to investigate. Written first, unchanged. |
| `CRITIQUE.md` | A review of it: eleven findings, what to keep, what to cut, and what the prior art already answers. |
| `PROPOSAL_SETTLEMENT.md` | The fast path to a decidable proposal: three questions, ten decisions, the scope ladder. |
| `PROPOSAL.md` | **The formal research-phase proposal** — scope, data position, evaluation rules, deliverables, gates. |
| `research/RESULTS_T0_T1_T3.md` | The first measured results: real baseline, data coverage, accumulator dependence. |
| `docs/CONSOLIDATED_FINDINGS.md` | **The state of the project in one document** — what was measured, what was tested, what would change the answer. |
| `docs/COLLAB/` | The bridge: thread, review queue, decisions, proposals. Start at `docs/COLLAB/README.md`. |
| docs/CONCLUSION.md | **Track A is closed** — what was established, what was not, and the reopening conditions |
| docs/STRATEGIC_ASSESSMENT.md | Where the project goes next: market intelligence rather than a prediction engine, and the ranked questions |
| docs/PRODUCT_DIRECTION.md | The product argument as written before the build: one engine, three views, four claim kinds, and what it refuses to build. **Historical** — the implementation grew to seven tabs plus export; `docs/PRODUCT_DEMO.md` is current |
| docs/PREREG-DISPERSION.md | The one authorised study, specified before scoring: is the quote gap consistent with a calibrated dispersion model |

## Run the product

`ash
python -m app.server      # http://127.0.0.1:8765
`

A local market-companion app over the held corpus: assess a selection, build a slip with a dependence
correction, search for a stake-and-target combination, and see pool arithmetic. Every number is tagged
observed, estimated or hypothetical. See [docs/PRODUCT_DEMO.md](docs/PRODUCT_DEMO.md).

## Where the argument stands

The vision is sound and the first phase is deliberately narrow. Phase one tests the
**instrument** — lawful data, a measured baseline, pre-registered scoring, correction —
not the ambition. The ambition is unchanged and carried by the expansion ladder in
`PROPOSAL_SETTLEMENT.md` §0.

Three things are now measured rather than argued:

- **14,802 real fixtures** across 8 divisions and 5 seasons, 100% with closing 1X2 prices
  (Pinnacle closing), sha256 manifest in `research/data_manifest.csv`.
- **The real favourite baseline is 53.3%** (95% CI 52.5–54.1), not the 51.5% imported
  from a virtual league. That number is withdrawn; importing it would have set a bar that
  is too easy.
- **Same-match accumulator legs cannot be multiplied**: realised joint 40.9% against a
  product of marginals of 27.5%, a ratio of 1.49× (1.47–1.51), consistent in all eight
  divisions.

## What has been established

Twenty-five experiments, all recorded in [CONSOLIDATED_FINDINGS.md](docs/CONSOLIDATED_FINDINGS.md):

- **Calibration is recoverable.** An out-of-fold Platt map recovers 0.0114 of the 0.0246-nat
  deficit, but the model still carries about a quarter of the market's separation (AUC 0.562
  against 0.607). Half the gap is mapping, half is missing information.
- **No information source tested adds anything to the closing price.** Cross-book disagreement,
  schedule congestion, cross-market totals, recent scoring and league environment were screened
  under one protocol with permutation nulls; all six families were null (BH q = 0.900).
- **Three further mechanism classes were tested and none survived.** Calendar folklore, head-to-head
  history and style mismatch were each tested against the price; every positive point estimate
  failed its own stress test, and the intuitively plausible attack/defence interaction was negative.
- **The one positive signal failed its own pre-registered test.** A favourite-longshot gap
  appeared at high thresholds; pre-registered and applied to a held-out season, it was not
  supported (gap +0.026, interval spanning zero, negative return).
- **Track B's arithmetic is negative for the tested product.** A filtered view raises hit rate but
  costs 0.0003 nats of log-wealth per fixture at a 1% stake, filtering recovers most of that
  (policy growth −0.00002, interval [−0.00006, +0.00003]) and yet makes the displayed probability
  less accurate, not more. [The design](docs/TRACK_B_DESIGN.md) therefore concludes
  that this abstention product, measured this way, is not worth building on this market — it does
  not settle the broader question of whether a user decides better with decision support, which
  closing-price data cannot evaluate.

## What the project is waiting on

A sponsor decision, not an experiment. The corpus has been tested for information three
independent ways and the answers agree: reaching further needs data it does not contain — faster
pre-kickoff information, thinner markets, or a different comparison — and each costs money, time
or legal exposure.

The sizing question remains open for whenever a confirmatory test is authorised: at the model's
current spread the two-season window has **70.5%** power for a 0.01-nat effect at the calibrated
cutoff, and the 80% crossing sits at **0.0116–0.0130 nats**. A third confirmatory season (24
clusters) would raise power to **86.6%**.

No confirmatory scoring has happened, none will without a freeze, and the target is unchanged.

## Environment

Python 3.12 with numpy; nothing else is imported. 
equirements.txt pins nothing beyond

umpy>=2.0 deliberately — the code is standard-library otherwise, and a lock file would rot
faster than the dependency moves. The test suite runs without the corpus: the tests build their
own fixtures, and the corpus is third-party data that is retrieved rather than committed.

Continuous integration runs the data-free checks on every push (.github/workflows/checks.yml):
the suite, the bridge checker, and a verification transcript. It does not regenerate reports —
that needs the corpus and about fifteen minutes, and runs locally with
python scripts/verify_all.py --full.

## CI evidence

`ash
python scripts/ci_evidence.py    # rewrite docs/CI_EVIDENCE.md from the Actions API
`

Run numbers, commit SHAs and links come from a command rather than from memory. That is a direct
response to two incidents: a bridge entry quoting a revision a rebase had erased, and a CI link that
did not exist.

## Auditing the repository

`ash
python scripts/audit.py          # nine cross-document checks; non-zero exit on failure
python scripts/audit.py --json   # machine-readable
`

It checks the things that kept needing a person: report citations, generator and experiment counts,
retracted claims reappearing, revision reachability, digest freshness, link rot, corpus provenance and
bridge parseability. It runs in CI and as a stage of scripts/verify_all.py.

## Reproducing the measurements

```powershell
$py = "C:\Users\tuyaa\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe"

& $py research\analyse.py          # regenerates RESULTS_T0_T1_T3.md and the manifest
& $py -m unittest discover -s tests -v
& $py scripts\collab_check.py
& $py scripts\repro_sweep.py       # regenerate every report, report drift
& $py scripts\verify_all.py --full # every check in one transcript, with commit and artefact hash
```

`research/analyse.py` is standard-library only and reads whatever CSVs are in
`research/data/`. The data itself is not committed — it is 6.7 MB of third-party files —
so a fresh clone needs the retrieval step recorded in `research/data_manifest.csv`
before the analysis can rerun. `collab_check.py` fails when the thread has lost a line,
when the queue claims a verdict no oversight entry records, or when a proposal has been
filed as a decision.
