"""Gate and ledger for GitHub Actions resource use.

The sponsor approved resource safeguards and asked for any behaviour the workflow cannot itself
enforce to be stated plainly. This script is the enforceable part, and the docstring records the
boundary.

**Enforced here:** a pause switch, a per-run minute ceiling compared against the workflow's job
timeout, a per-day run limit counted from a committed ledger, and an append-only record of runs.

**Not enforceable here, and not claimed:** GitHub's own minutes accounting, billing state, monthly
allowances, or anything that happens outside this repository. A limit in a file can be edited in
the same commit that exceeds it; it is a guard rail, not an access control.

    python scripts/ci_gate.py            # decide whether this run should proceed
    python scripts/ci_gate.py --record --note "..."   # append this run to the ledger
    python scripts/ci_gate.py --status   # print policy and usage without deciding

Exit codes: 0 proceed, 2 paused, 3 over budget, 1 bad configuration.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / ".github" / "ci-policy.json"
LEDGER = ROOT / "docs" / "ci" / "runs.jsonl"


def load_policy(path: Path = POLICY) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    for key in ("paused", "max_minutes_per_run", "max_runs_per_day"):
        if key not in data:
            raise ValueError(f"policy is missing {key}")
    return data


def read_ledger(path: Path = LEDGER) -> list[dict]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


def runs_today(entries: list[dict], today: dt.date) -> int:
    return sum(1 for e in entries if e.get("date") == today.isoformat())


def decide(policy: dict, entries: list[dict], today: dt.date,
           job_timeout_minutes: int = 15) -> tuple[int, str]:
    """Return (exit_code, message). Pure, so the policy can be tested without a runner."""
    if policy["paused"]:
        return 2, "paused by .github/ci-policy.json: substantive steps will be skipped"
    if policy["max_minutes_per_run"] > job_timeout_minutes:
        return 1, (f"policy allows {policy['max_minutes_per_run']} minutes per run but the job "
                   f"timeout is {job_timeout_minutes}; the effective cap is the timeout")
    used = runs_today(entries, today)
    if used >= policy["max_runs_per_day"]:
        return 3, (f"daily run limit reached: {used} of {policy['max_runs_per_day']} already "
                   f"recorded for {today.isoformat()}")
    return 0, f"proceeding: run {used + 1} of at most {policy['max_runs_per_day']} today"


def record(note: str, minutes: float = 0.0, path: Path = LEDGER) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "date": dt.datetime.now(dt.timezone.utc).date().isoformat(),
        "at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "note": note,
        "minutes": minutes,
    }
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")
    return entry


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Gate and record GitHub Actions resource use.")
    p.add_argument("--record", action="store_true", help="append this run to the ledger")
    p.add_argument("--note", default="run", help="what this run is for")
    p.add_argument("--minutes", type=float, default=0.0, help="observed duration")
    p.add_argument("--status", action="store_true", help="print policy and usage only")
    args = p.parse_args(argv)

    policy = load_policy()
    entries = read_ledger()
    today = dt.datetime.now(dt.timezone.utc).date()

    if args.status:
        print(json.dumps({"policy": policy, "runs_today": runs_today(entries, today),
                          "recorded_total": len(entries)}, indent=2))
        return 0

    if args.record:
        entry = record(args.note, args.minutes)
        print(f"recorded: {entry}")
        return 0

    code, message = decide(policy, entries, today)
    print(message)
    if code == 2:
        # Signal the workflow to skip the substantive steps without failing the build. The
        # GITHUB_OUTPUT file is how a step communicates with later steps; it exists only on a
        # runner, so writing it is guarded rather than assumed.
        import os
        out = os.environ.get("GITHUB_OUTPUT")
        if out:
            with open(out, "a", encoding="utf-8") as fh:
                fh.write("paused=true\n")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
