"""One command that produces independently checkable evidence, and refuses to fake it.

The independent audit noted that the test and sweep counts are "builder-reported evidence". This
script exists so a reviewer can run one command and see the counts come from the runs.

Fail-closed provenance. An earlier version printed the commit and the number of dirty files and
then reported PASS regardless, which is the defect this version fixes: a transcript that says
"all stages passed" while the working tree does not match the commit it names is worse than no
transcript. Now:

- a dirty tree fails the run, because the evidence would not correspond to any commit;
- a HEAD that moves during the run fails it, for the same reason;
- each stage has an explicit timeout, so a hang is a failure rather than a wait.

    python scripts/verify_all.py            # quick: tests, bridge, claims
    python scripts/verify_all.py --full     # adds the regeneration sweep
    python scripts/verify_all.py --ci       # data-free, no sweep, for CI
    python scripts/verify_all.py --allow-dirty   # explicit opt-out, labelled in the transcript

Exit code is zero only if every stage passes and provenance holds.
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
STAGE_TIMEOUT = 1800


class GitError(RuntimeError):
    """A Git inspection command failed, so provenance cannot be established."""


def git(*args: str) -> str:
    """Run a Git command and fail loudly if it fails.

    Returning stdout regardless of the return code was the fail-open hole: a broken repository
    would yield empty strings, and two empty HEAD values compare equal, so the provenance check
    would pass on no evidence at all.
    """
    proc = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    if proc.returncode != 0:
        raise GitError(f"git {' '.join(args)} failed ({proc.returncode}): "
                       f"{(proc.stderr or proc.stdout).strip()}")
    return proc.stdout.strip()


def dirty_files() -> list[str]:
    return [line for line in git("status", "--porcelain").splitlines() if line.strip()]



def diagnostic_lines(output: str, ok: bool, success: int = 2, failure: int = 25) -> list[str]:
    """How much of a stage's output to show.

    A passing stage needs a line or two; a failing one needs enough context to act on. Printing
    the tail for both is how a real failure gets summarised as a single unhelpful line.
    """
    lines = [line for line in output.splitlines() if line.strip()]
    if not lines:
        return ["(no output)"]
    limit = success if ok else failure
    shown = lines[-limit:]
    if not ok and len(lines) > limit:
        shown = [f"... {len(lines) - limit} earlier line(s) omitted"] + shown
    return shown


def provenance(head_before: str, head_after: str, dirty: int,
               allow_dirty: bool) -> tuple[bool, str]:
    """Decide whether a transcript may attest to a commit. Pure, so it can be tested.

    Fails closed: an uncommitted tree or a moving HEAD means the evidence does not correspond to
    the revision named at the top of the transcript.
    """
    if head_before != head_after:
        return False, f"HEAD moved during the run ({head_before[:8]} -> {head_after[:8]})"
    if dirty and not allow_dirty:
        return False, (f"{dirty} uncommitted change(s): the transcript would attest to "
                       f"{head_before[:8]} but describe a tree that is not that commit. "
                       f"Commit them, or pass --allow-dirty to label the run as unattested.")
    return True, ""


def run(args: list[str], timeout: int = STAGE_TIMEOUT) -> tuple[bool, str, float]:
    started = time.time()
    try:
        proc = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
        ok = proc.returncode == 0
        output = (proc.stdout or "") + (proc.stderr or "")
    except subprocess.TimeoutExpired:
        ok = False
        output = f"timed out after {timeout}s"
    return ok, output, time.time() - started


def artefact_digest() -> str:
    h = hashlib.sha256()
    for path in sorted((ROOT / "research").glob("*.md")):
        h.update(path.name.encode())
        h.update(path.read_bytes())
    return h.hexdigest()[:16]



def clone_stage() -> tuple[bool, str, float]:
    """Run the suite in a fresh clone, which is the condition CI sees.

    Local runs can pass on objects that only exist as dangling references in this working copy -
    a rebased commit is reachable by `git cat-file` here and absent in a clone. That difference has
    produced three red CI runs, so the clone is part of ordinary verification rather than a thing
    to remember.
    """
    started = time.time()
    import shutil
    import tempfile

    tmp = Path(tempfile.mkdtemp(prefix="dsh-clone-"))
    try:
        subprocess.run(["git", "clone", "--quiet", f"file://{ROOT.as_posix()}", str(tmp)],
                       capture_output=True, text=True, timeout=300)
        proc = subprocess.run([PY, "-m", "unittest", "discover", "-s", "tests"],
                              cwd=tmp, capture_output=True, text=True, timeout=STAGE_TIMEOUT)
        ok = proc.returncode == 0
        output = (proc.stdout or "") + (proc.stderr or "")
    except subprocess.TimeoutExpired:
        ok, output = False, "clone stage timed out"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return ok, output, time.time() - started


def main() -> int:
    argv = sys.argv[1:]
    ci = "--ci" in argv
    allow_dirty = "--allow-dirty" in argv

    try:
        head_before = git("rev-parse", "HEAD")
        dirty = dirty_files()
    except GitError as exc:
        print("REFUSING TO RUN")
        print(f"  cannot establish provenance: {exc}")
        return 1

    ok, reason = provenance(head_before, head_before, len(dirty), allow_dirty or ci)
    if not ok:
        print("REFUSING TO RUN")
        print(f"  {reason}")
        return 1

    stages = [
        ("test suite", [PY, "-m", "unittest", "discover", "-s", "tests"]),
        ("bridge checker", [PY, "scripts/collab_check.py"]),
        ("report stamps, claims, integrity",
         [PY, "-m", "unittest", "tests.test_reports", "tests.test_claims",
          "tests.test_docs_integrity"]),
    ]
    if "--clone" in argv:
        stages.append(("fresh-clone suite", "CLONE"))
    if "--full" in argv:
        stages.append(("full regeneration sweep", [PY, "scripts/repro_sweep.py"]))

    print("FoundrySide verification transcript")
    print("=" * 62)
    print(f"commit      {head_before[:12]}")
    print(f"branch      {git('rev-parse', '--abbrev-ref', 'HEAD')}")
    print(f"dirty files {len(dirty)}"
          + ("  (ALLOWED: --allow-dirty, run is unattested)" if dirty else ""))
    print(f"artefacts   sha256:{artefact_digest()} over "
          f"{len(list((ROOT / 'research').glob('*.md')))} reports")
    if ci:
        print("scope       CI mode: data-free checks only")
    elif "--full" not in argv:
        print("scope       quick checks only; pass --full to include the regeneration sweep")
    print()

    started = time.time()
    failures = 0
    for label, args in stages:
        if args == "CLONE":
            ok, output, elapsed = clone_stage()
        else:
            ok, output, elapsed = run(args)
        tail = diagnostic_lines(output, ok)
        print(f"[{'PASS' if ok else 'FAIL'}] {label} ({elapsed:.1f}s)")
        for line in tail:
            print(f"       {line}")
        if not ok:
            failures += 1

    try:
        head_after = git("rev-parse", "HEAD")
    except GitError as exc:
        print(f"PROVENANCE FAILURE: cannot re-read HEAD after the run: {exc}")
        return 1
    ok, reason = provenance(head_before, head_after, len(dirty), allow_dirty or ci)

    print()
    print("=" * 62)
    if not ok:
        print(f"PROVENANCE FAILURE: {reason}")
        return 1
    if failures:
        print(f"RESULT: {failures} stage(s) failed after {time.time() - started:.0f}s")
        return 1
    print(f"RESULT: all stages passed in {time.time() - started:.0f}s")
    print("Nothing in this transcript is hand-entered; every count comes from the run above.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
