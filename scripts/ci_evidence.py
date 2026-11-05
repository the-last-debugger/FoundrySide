"""Record CI evidence from the GitHub API into a document, so it is never typed from memory.

The builder has twice written an identifier that did not exist — a commit SHA that a rebase erased, and
a workflow-run URL that was simply wrong. The first was fixed by resolving revisions from `origin/main`
instead of `HEAD`. This is the same class: an identifier should come from a command, not from
recollection.

    python scripts/ci_evidence.py            # write docs/CI_EVIDENCE.md
    python scripts/ci_evidence.py --print    # show and do not write

Requires unauthenticated network access to api.github.com. It is a documentation tool, not part of the
test suite, because tests must not depend on the network.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "CI_EVIDENCE.md"
API = "https://api.github.com/repos/the-last-debugger/FoundrySide/actions/runs"


def fetch_runs(limit: int = 12) -> list[dict]:
    request = urllib.request.Request(
        f"{API}?per_page={limit}", headers={"User-Agent": "FoundrySide-evidence/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return payload.get("workflow_runs", [])


def current_revision() -> str:
    import subprocess
    proc = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                          capture_output=True, text=True)
    return proc.stdout.strip()


def render(runs: list[dict], head: str = "") -> str:
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    lines = [
        "<!-- generated-by: ci_evidence.py; regenerate rather than edit -->",
        "",
        "# CI evidence",
        "",
        f"Recorded {stamp} from the GitHub Actions API. Regenerate with "
        "`python scripts/ci_evidence.py` rather than typing a run number or URL by hand — a quoted",
        "identifier that does not exist is worse than no identifier at all.",
        "",
        "| Run | Commit | Status | Conclusion | Link |",
        "| --- | --- | --- | --- | --- |",
    ]
    for run in runs:
        sha = (run.get("head_sha") or "")[:7]
        conclusion = run.get("conclusion") or run.get("status") or "unknown"
        lines.append(
            f"| {run.get('run_number')} | `{sha}` | {run.get('status')} | {conclusion} | "
            f"{run.get('html_url')} |")
    if head:
        matching = [run for run in runs if (run.get("head_sha") or "").startswith(head)]
        if matching:
            run = matching[0]
            state = ("successful" if run.get("conclusion") == "success"
                     else f"{run.get('status')}/{run.get('conclusion')}")
            lines += ["", f"**Current revision `{head}`: run {run.get('run_number')} is {state}.**"]
        else:
            lines += ["", f"**Current revision `{head}`: no workflow run recorded yet.** "
                          "Do not describe this revision as CI-verified."]
    lines += [
        "",
        "A `cancelled` conclusion is the concurrency safeguard cancelling a superseded run, not a",
        "failure: `.github/workflows/checks.yml` keeps one run per branch and cancels the older one.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Record CI evidence from GitHub Actions")
    parser.add_argument("--print", action="store_true", dest="print_only")
    parser.add_argument("--limit", type=int, default=12)
    args = parser.parse_args()

    try:
        runs = fetch_runs(args.limit)
    except Exception as exc:
        print(f"could not reach the GitHub API: {type(exc).__name__}: {exc}")
        return 1

    text = render(runs, current_revision())
    if args.print_only:
        print(text)
        return 0
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} with {len(runs)} runs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
