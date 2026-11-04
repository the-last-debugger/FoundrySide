# Actions resource ledger

A record of workflow runs, appended by `scripts/ci_gate.py --record` at the end of each successful
CI run. Machine-readable entries live in `docs/ci/runs.jsonl`; this file explains the scheme and
records manual observations.

## What is enforced, and by what

| Safeguard | Enforced by | Enforceable? |
| --- | --- | --- |
| One run per branch, superseded runs cancelled | `concurrency:` in the workflow | Yes, by GitHub |
| Per-run time ceiling | `timeout-minutes:` matched to `.github/ci-policy.json` | Yes; a test asserts they agree |
| Pause switch | `scripts/ci_gate.py` sets an output the later steps test | Yes, from inside the repo |
| Per-day run limit | gate counts `docs/ci/runs.jsonl` for the current UTC date | Yes, for runs that complete and record |
| Ledger of runs | `--record` step | Yes, but only when the run reaches that step |

## What is not enforced, and is not claimed

- **GitHub's own minutes accounting and billing.** Those live outside this repository. The ledger
  counts runs this workflow recorded, not minutes GitHub billed.
- **A limit edited in the same commit that exceeds it.** The policy is a file; anyone who can push
  can change it. This is a guard rail against accident, not an access control.
- **Runs that fail before the record step.** A cancelled or failed run consumes minutes but may
  leave no ledger entry, so the daily count can understate usage.
- **Monthly allowances or plan limits.** Not represented here at all.

## Current policy

From `.github/ci-policy.json`: not paused, 15 minutes per run, 20 runs per day. The job timeout is
15 minutes, so the minute ceiling and the timeout agree; a test fails if they stop agreeing.
