# Compute feasibility note

**Status: closed.** The sponsor halted the cloud investigation on this note's findings and
directed that work stay local and zero-cost. No account, console, billing, quota or
infrastructure action was taken at any point. Kept as the record of why, and of what would
reopen it.

Desk research only. **No account was created, no billing activated, no quota requested, no
instance was launched or deployed.** This records what the research actually needs and what a
cloud route would have to satisfy, so the decision can be made once rather than rediscovered.

## What this project actually costs to run

| Workload | Size |
| --- | --- |
| Corpus | 40 CSV files, 6.7 MB, 14,802 fixtures |
| Full regeneration | 23 scripts, ~10 minutes wall clock |
| Heaviest step | feature screen: 3,600 logistic refits, ~150 s |
| Bootstrap/permutation | up to 4,000 resamples per study |
| Peak memory | under 1 GB (all datasets fit in RAM many times over) |

Every experiment to date ran on a single ordinary machine, in pure Python with numpy. There has
been no point at which compute was the constraint on the research; the constraint was always
information.

## Minimum technical requirements

- Python 3.10+, numpy; no GPU, no database, no service dependencies.
- ~2 GB RAM, ~10 GB disk for corpus plus artefacts.
- Outbound HTTPS to one public source (`football-data.co.uk`) for retrieval.
- No inbound ports, no domain, no persistent storage beyond the repository.

That profile is satisfied by a free-tier micro instance, and also by the machine that already ran
it.

## Cloud options, as understood at desk-research level

| Route | What it would give | Caveats |
| --- | --- | --- |
| Free-tier micro instance | A always-on Linux box for scheduled reruns | Region restrictions, egress limits, and the free tier is time-limited in some configurations |
| Trial credit | Burst capacity for large Monte Carlo | Requires billing activation; credits expire; availability varies by account and country |
| Managed notebook | Convenience, sharing | Persistent storage and idle cost; overkill for a 10-minute pipeline |

These are recorded as **reported, not verified** — no console was opened and no quota or price was
checked. Any figure here should be re-checked before it is relied on.

## What would actually justify cloud compute

Not the current pipeline. It would matter only if:

1. Monte Carlo grew by orders of magnitude (e.g. nested cross-validation over many specifications);
2. a larger corpus arrived (more seasons, event data, or per-match lineups at scale);
3. scheduled reruns were wanted without a local machine being on.

None of those is true today, and the first two would themselves be sponsor decisions about data,
not compute.

## Recommendation

Keep compute local and free. Record cloud as a contingency with a known trigger — a workload that
no longer fits in minutes on one machine — rather than as a step to take now. If the sponsor's
account already carries usable credit, the only sensible use of it would be a long Monte Carlo
sensitivity run, which current evidence does not call for.

## Boundaries respected

No account creation, billing change, quota request, VM, deployment or paid usage. This note is
the only artefact of the investigation, which is the appropriate output for a feasibility question
whose answer is "not yet needed".

## If capacity ever has to be allocated between projects

The sponsor's standing rule is that any future Azure allocation between OLPRS and FoundrySide is
decided by **measured** resource demand rather than by preference. The numbers to compare are
those recorded at the top of this note: corpus size, regeneration wall clock, peak memory, and
whether the workload needs a GPU, an always-on host or inbound service. For FoundrySide today
those are 6.7 MB, ~10 minutes, under 1 GB, and none respectively.
