# Actions resource ledger

What the workflow's resource controls actually do, and — more importantly — what they do not.

## Enforced

| Safeguard | Enforced by | Verified by |
| --- | --- | --- |
| One run per branch; superseded runs cancelled | `concurrency: cancel-in-progress` | workflow text test |
| Per-run ceiling | `timeout-minutes: 15` | a test asserts it equals the policy value |
| Policy file is valid and consistent | `scripts/ci_gate.py --advisory` | six gate tests |

## Advisory, not enforced

**The pause switch.** `.github/ci-policy.json` carries `paused`, and the gate reports it, but it
does **not** gate any step. Every substantive step — dependencies, test suite, bridge consistency,
verification transcript — is unconditional. There is currently no discretionary scheduled or
research job for a pause to suppress, and the switch must never be able to skip essential checks.
The gate step is named `--advisory` for that reason and always exits zero.

**The per-day run limit.** This was claimed in an earlier version and has been withdrawn. The
ledger is written into a read-only checkout, so it does not survive the runner: each run starts
with an empty history and the count restarts at zero. A limit counted from a file that resets is
not a limit, so the number is reported as advisory only.

## Not represented at all

- **GitHub's minutes accounting, billing and monthly allowances.** Outside this repository; no
  claim is made about them.
- **Duration and failed-run capture.** A run that fails or is cancelled records nothing, so the
  counts understate usage.
- **Any alerting or budget notification.** None exists.

## A design that would enforce a daily cap, if it were ever wanted

Persisting across runs needs either write access to the repository (a bot commit of the ledger) or
a read-only query of the Actions API with `actions: read`, counting runs by date. Both are
deliberate permission changes and neither is implemented. This paragraph exists so the option is
recorded rather than rediscovered, not to imply it is active.

## Current policy

`.github/ci-policy.json`: not paused, 15 minutes per run, 20 runs per day (advisory). The job
timeout and the minute ceiling agree, and a test fails if they stop agreeing.
