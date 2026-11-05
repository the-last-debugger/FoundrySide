"""Preflight — the fast checks to run before committing.

`verify_all.py` is thorough: it clones the repository and regenerates every report, which takes about
twenty minutes. That is right for a release and wrong for a loop, so the checks that fail *often* were
being skipped. This runs them in a few seconds:

    python scripts/preflight.py

Exit code is 0 when everything passes. Nothing here needs the network or the corpus.
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable

STAGES = [
    ("tests", [PY, "-m", "unittest", "discover", "-s", "tests", "-q"]),
    ("bridge checker", [PY, "scripts/collab_check.py"]),
    ("repository audit", [PY, "scripts/audit.py", "--quiet"]),
]


def run(args: list[str]) -> tuple[bool, str, float]:
    started = time.time()
    proc = subprocess.run(args, cwd=ROOT, capture_output=True, text=True)
    output = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode == 0, output, time.time() - started


def main() -> int:
    failures = 0
    print("preflight\n" + "-" * 60)
    for label, args in STAGES:
        ok, output, elapsed = run(args)
        tail = [line for line in output.strip().splitlines() if line.strip()][-1:] or [""]
        print(f"[{'PASS' if ok else 'FAIL'}] {label} ({elapsed:.1f}s)  {tail[0][:70]}")
        if not ok:
            failures += 1
            for line in output.strip().splitlines():
                if any(marker in line for marker in ("FAIL:", "ERROR:", "ERROR ", "Traceback")):
                    print(f"       {line[:110]}")
    print("-" * 60)
    print("ready to commit" if not failures else f"{failures} stage(s) failed")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
