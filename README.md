# FoundrySide

A research repository, not an application. The project is in its research phase;
`DECISIONS.md` D-01 records that it is **not authorised to build** an application, while
D-10 authorises independent research, experiments and research scripts.

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
  product of marginals of 27.5%, a ratio of 1.49× (1.46–1.52), consistent in all eight
  divisions.

## What the project is waiting on

A decision on the first experiment's design. The protocol now measures what it previously
assumed: at the first pilot model's spread, the two-season window has **69.4%** power for a
0.01-nat effect — below the 80% rule — and the 80% crossing sits at **0.0116–0.0130 nats**.
Three options, all costing something:

| Option | Effect |
| --- | --- |
| Raise the target effect to ~0.012 | Leaves the sample as is; changes what the experiment claims |
| Add a third confirmatory season (24 clusters) | Power rises to 84.1% |
| Add markets to the family | Raises n, enlarges the multiple-testing family |

No confirmatory scoring has happened, and none will without a freeze.

## Reproducing the measurements

```powershell
$py = "C:\Users\tuyaa\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe"

& $py research\analyse.py          # regenerates RESULTS_T0_T1_T3.md and the manifest
& $py -m unittest discover -s tests -v
& $py scripts\collab_check.py
& $py scripts\repro_sweep.py       # regenerate every report, report drift
```

`research/analyse.py` is standard-library only and reads whatever CSVs are in
`research/data/`. The data itself is not committed — it is 6.7 MB of third-party files —
so a fresh clone needs the retrieval step recorded in `research/data_manifest.csv`
before the analysis can rerun. `collab_check.py` fails when the thread has lost a line,
when the queue claims a verdict no oversight entry records, or when a proposal has been
filed as a decision.
