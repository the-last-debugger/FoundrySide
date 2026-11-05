"""Print the measured facts the documentation quotes.

Every count in the handover and the README has drifted at least once: experiments, generators, tests,
audit checks, reports. Each time the fix was to measure and copy, and each time someone had to remember
to do it. This prints them, so a document update is a copy rather than a recollection.

    python scripts/status.py
    python scripts/status.py --json
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def experiment_count() -> tuple[int, str]:
    text = (ROOT / "docs" / "RESEARCH_PROGRAMME.md").read_text(encoding="utf-8")
    ids = {int(m) for m in re.findall(r"\|\s*E(\d+)\s*\|", text)}
    return (max(ids) if ids else 0), "docs/RESEARCH_PROGRAMME.md"


def generator_count() -> tuple[int, str]:
    from repro_sweep import GENERATORS
    return len(GENERATORS), "scripts/repro_sweep.py"


def report_count() -> tuple[int, str]:
    return len(list((ROOT / "research").glob("*.md"))), "research/*.md"


def audit_count() -> tuple[int, str]:
    import audit
    return len(audit.CHECKS), "scripts/audit.py"


def test_count() -> tuple[int, str]:
    proc = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-q"],
                          cwd=ROOT, capture_output=True, text=True)
    match = re.search(r"Ran (\d+) tests", (proc.stdout or "") + (proc.stderr or ""))
    return (int(match.group(1)) if match else 0), "python -m unittest discover -s tests"


SNAPSHOT = ROOT / "docs" / "STATUS.json"


def read_snapshot_tests() -> tuple[int, str]:
    """Test count from the last recorded snapshot, so a test can ask without running the suite."""
    try:
        import json as _json
        return int(_json.loads(SNAPSHOT.read_text(encoding="utf-8"))["tests"]["value"]), \
            "docs/STATUS.json"
    except Exception:
        return 0, "docs/STATUS.json (missing)"


def clause_count() -> tuple[int, str]:
    import collab_note
    return len(collab_note.parse_entries()), "docs/COLLAB/THREAD.md"


def revision() -> tuple[str, str]:
    proc = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                          capture_output=True, text=True)
    return proc.stdout.strip(), "git"


def collect(run_tests: bool = True) -> dict[str, dict]:
    items = {
        "revision": revision(),
        "experiments": experiment_count(),
        "generators": generator_count(),
        "reports": report_count(),
        "audit checks": audit_count(),
        "tests": test_count() if run_tests else read_snapshot_tests(),
        "bridge entries": clause_count(),
    }
    return {name: {"value": value, "source": source} for name, (value, source) in items.items()}


def main() -> int:
    if "--json" in sys.argv:
        print(json.dumps(collect(), indent=2))
        return 0

    data = collect(run_tests=True)
    SNAPSHOT.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    width = max(len(name) for name in data)
    print("measured state\n" + "-" * 52)
    for name, item in data.items():
        print(f"{name:<{width}}  {str(item['value']):>6}   {item['source']}")
    print("-" * 52)
    print(f"Recorded to {SNAPSHOT.relative_to(ROOT)}; copy these into the documents rather than "
          f"typing a remembered number.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
