"""One command that produces independently checkable evidence.

The independent audit noted that the test and sweep counts are "builder-reported evidence". They
are, because the reviewer has to trust a message rather than run something. This script exists so
that is no longer necessary: it runs every check, records what it ran, and prints a transcript
with the commit it applies to.

    python scripts/verify_all.py

Exit code is zero only if every stage passes. Nothing here is recorded by hand; the counts come
from the runs.
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable


def run(label: str, args: list[str], timeout: int = 1800) -> tuple[bool, str, float]:
    started = time.time()
    proc = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
    elapsed = time.time() - started
    output = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode == 0, output, elapsed


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True).stdout.strip()


def artefact_digest() -> str:
    """One hash over every generated report, so a reader can compare two runs."""
    h = hashlib.sha256()
    for path in sorted((ROOT / "research").glob("*.md")):
        h.update(path.name.encode())
        h.update(path.read_bytes())
    return h.hexdigest()[:16]


def main() -> int:
    stages = [
        ("test suite", [PY, "-m", "unittest", "discover", "-s", "tests"]),
        ("bridge checker", [PY, "scripts/collab_check.py"]),
        ("report stamps and claims", [PY, "-m", "unittest", "tests.test_reports",
                                      "tests.test_claims", "tests.test_docs_integrity"]),
    ]
    if "--full" in sys.argv:
        # The sweep regenerates every report and takes about twelve minutes; it is opt-in so
        # this command stays usable while working.
        stages.append(("full regeneration sweep", [PY, "scripts/repro_sweep.py"]))

    print("FoundrySide verification transcript")
    print("=" * 60)
    print(f"commit      {git('rev-parse', '--short', 'HEAD')}")
    print(f"branch      {git('rev-parse', '--abbrev-ref', 'HEAD')}")
    print(f"dirty files {len([l for l in git('status', '--porcelain').splitlines() if l.strip()])}")
    print(f"artefacts   sha256:{artefact_digest()} over {len(list((ROOT / 'research').glob('*.md')))} reports")
    if "--full" not in sys.argv:
        print("scope       quick checks only; pass --full to include the 23-generator sweep")
    print()

    failures = 0
    for label, args in stages:
        ok, output, elapsed = run(label, args)
        tail = [line for line in output.splitlines() if line.strip()][-2:]
        print(f"[{'PASS' if ok else 'FAIL'}] {label} ({elapsed:.1f}s)")
        for line in tail:
            print(f"       {line}")
        if not ok:
            failures += 1

    print()
    print("=" * 60)
    if failures:
        print(f"RESULT: {failures} stage(s) failed")
        return 1
    print("RESULT: all stages passed")
    print("This transcript is produced by running the commands above; nothing in it is hand-entered.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
