"""Validate the FoundrySide collaboration invariants across thread, queue and decisions.

Ported from the ODE bridge, which was itself adapted from OLPRS_v2. Same
invariants, same failure modes, one difference in policy: this repository has no
pre-checker history, so the append-only rule is enforced from the first commit
rather than grandfathered forward.

    python scripts/collab_check.py
    python scripts/collab_check.py --history-audit
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.collab_note import parse_entries  # noqa: E402

COLLAB = ROOT / "docs" / "COLLAB"

QUEUE_STATES = ("draft", "ready_for_review", "changes_requested", "accepted")
VERDICT_STATES = ("changes_requested", "accepted")
UNSET_REVISIONS = ("", "-", "pending")
RQ_RE = re.compile(r"RQ-\d+")
SHA_RE = re.compile(r"^[0-9a-f]{7,40}$")
PROPOSED_RE = re.compile(r"\*\*Status:\*\*\s*proposed", re.IGNORECASE)
DECISION_ID_RE = re.compile(r"^##\s+(D-\d+)\b")

QUEUE_COLUMNS = ("id", "change", "ref", "revision", "state", "evidence", "reviewer")


def load_queue(queue_path: Path) -> tuple[list[dict[str, str]], list[str]]:
    rows: list[dict[str, str]] = []
    errors: list[str] = []
    if not queue_path.exists():
        return rows, [f"queue file does not exist: {queue_path}"]
    seen: set[str] = set()
    for line in queue_path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells or cells[0] in {"ID", "---"} or set(cells[0]) <= {"-", " "}:
            continue
        if not RQ_RE.fullmatch(cells[0]):
            continue
        if len(cells) != len(QUEUE_COLUMNS):
            errors.append(f"{cells[0]}: expected {len(QUEUE_COLUMNS)} columns, found {len(cells)}")
            continue
        row = dict(zip(QUEUE_COLUMNS, cells))
        if row["id"] in seen:
            errors.append(f"{row['id']}: duplicate row id")
        seen.add(row["id"])
        if row["state"] not in QUEUE_STATES:
            errors.append(f"{row['id']}: unknown state {row['state']!r}")
        rows.append(row)
    if not rows:
        errors.append("queue contains no rows")
    return rows, errors


def _names_row(entry: dict[str, str], row_id: str) -> bool:
    return row_id in entry["message"] or row_id in entry["ref"]


def revision_exists(sha: str) -> bool | None:
    """True/False if this is a git repo, None when git is unavailable."""
    try:
        proc = subprocess.run(
            ["git", "-C", str(ROOT), "cat-file", "-e", f"{sha}^{{commit}}"],
            capture_output=True, text=True, timeout=15)
    except Exception:  # noqa: BLE001
        return None
    if proc.returncode == 0:
        return True
    # A repository with no commits at all cannot answer the question.
    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True, timeout=15)
    if head.returncode != 0:
        return None
    return False


def check_coupling(rows, entries, verify_revisions: bool = True):
    errors: list[str] = []
    warnings: list[str] = []
    known = {row["id"] for row in rows}
    reviews = [e for e in entries if e["author"] == "oversight" and e["kind"] == "review"]

    for entry in reviews:
        if not entry["revision"].strip():
            warnings.append(
                f"oversight review at {entry['stamp'] or 'unknown time'} records no "
                "revision and therefore cannot authorise any revision")
        named = set(RQ_RE.findall(entry["message"])) | set(RQ_RE.findall(entry["ref"]))
        if not named:
            # A general review of main is not a verdict on a row, and oversight
            # writes those. It is only a problem if it is later claimed as the
            # basis of a verdict, which is checked per-row below.
            warnings.append(
                f"oversight review at {entry['stamp'] or 'unknown time'} names no queue row "
                f"(treated as a general review, cannot authorise a row)")
        for item in sorted(named - known):
            errors.append(
                f"oversight review at {entry['stamp'] or 'unknown time'} names unknown row {item}")

    for row in rows:
        if row["state"] not in VERDICT_STATES:
            continue
        revision = row["revision"].strip()
        if revision in UNSET_REVISIONS:
            errors.append(
                f"{row['id']}: state {row['state']!r} needs a recorded revision; "
                "the builder fills it before oversight decides")
            continue
        if not SHA_RE.match(revision):
            errors.append(f"{row['id']}: revision {revision!r} is not a commit SHA")
            continue
        if verify_revisions:
            exists = revision_exists(revision)
            if exists is False:
                errors.append(f"{row['id']}: revision {revision} does not exist in this repository")
        if any(_names_row(e, row["id"]) and e["revision"] == revision for e in reviews):
            continue
        other = sorted({e["revision"].strip() or "(none)"
                        for e in reviews if _names_row(e, row["id"])})
        detail = (f"; reviews exist for {', '.join(other)}" if other
                  else "; no oversight review names this row")
        errors.append(f"{row['id']}: no oversight review covers revision {revision}{detail}")

    return errors, warnings


def check_decisions(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"decisions file does not exist: {path}"]
    current: str | None = None
    body: list[str] = []
    seen: set[str] = set()

    def flush() -> None:
        if current and PROPOSED_RE.search("\n".join(body)):
            errors.append(f"{current}: marked proposed; proposals belong in PROPOSALS.md")

    for line in path.read_text(encoding="utf-8").splitlines():
        m = DECISION_ID_RE.match(line)
        if m:
            flush()
            current = m.group(1)
            if current in seen:
                errors.append(f"{current}: duplicate decision id")
            seen.add(current)
            body = []
            continue
        if current is not None:
            if line.startswith("## "):
                flush()
                current, body = None, []
                continue
            body.append(line)
    flush()
    if not seen:
        errors.append("decisions file contains no decisions")
    return errors


def _as_utc(stamp: str):
    if not stamp:
        return None
    try:
        moment = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    except ValueError:
        return None
    return moment if moment.tzinfo else moment.replace(tzinfo=timezone.utc)


def check_chronology(entries) -> list[str]:
    warnings: list[str] = []
    previous = None
    for entry in entries:
        instant = _as_utc(entry["stamp"])
        if instant is None:
            continue
        if previous and instant < previous[1]:
            warnings.append(f"out-of-order timestamp: {entry['stamp']} "
                            f"({entry['author']} {entry['kind']}) follows {previous[0]}")
        previous = (entry["stamp"], instant)
    return warnings


def lines_removed(previous: str, current: str) -> list[str]:
    """Lines present in `previous` but not in `current`, honouring multiplicity.

    THREAD.md is append-only for every role. Enforcement needs to compare against
    the committed past, not just the current file: an entry that is edited or
    deleted leaves no trace in the working copy.
    """
    from collections import Counter

    def norm(text: str) -> Counter:
        # Strip a UTF-8 BOM and normalise line endings: neither is a content
        # change, and comparing them as one produces a wall of false positives
        # that would train everyone to ignore the check.
        text = text.lstrip("\ufeff")
        kept = (line.rstrip("\r") for line in text.split("\n"))
        return Counter(line for line in kept if line.strip())

    return sorted((norm(previous) - norm(current)).elements())


class GitUnavailable(RuntimeError):
    """Raised when git inspection cannot be completed.

    This is deliberately an exception rather than an empty result. A version that
    returned [] on any git failure would report "history is clean" whenever git was
    broken, the repository was missing or the path had moved. A check that fails
    open is worse than no check, because it is trusted.
    """


def _git(*args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(ROOT), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60)
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip().splitlines()
        raise GitUnavailable(detail[-1] if detail else f"git {' '.join(args)} failed")
    return proc.stdout


def check_thread_history(thread_path: Path, lookback: int = 1) -> list[str]:
    """Fail if any committed THREAD.md line has disappeared since the previous commit.

    This is the cheap check that runs on every invocation. It answers "did the most
    recent change to this file delete anything", which is the question that matters
    while work is in flight. `audit_thread_history` answers the wider one.
    """
    try:
        rel = thread_path.resolve().relative_to(ROOT)
    except ValueError:
        return []  # outside the repository: caller supplied a fixture, nothing to audit
    try:
        commits = _git("log", f"-{lookback + 1}", "--format=%H", "--", rel.as_posix()).split()
        if len(commits) < 2:
            return []
        previous = commits[1]
        prior = _git("show", f"{previous}:{rel.as_posix()}")
    except GitUnavailable as e:
        return [f"THREAD.md history could not be inspected (failing closed): {e}"]
    removed = lines_removed(prior,
                            thread_path.read_text(encoding="utf-8", errors="replace"))
    return [f"THREAD.md append-only violation: removed since {previous[:7]}: {line[:90]}"
            for line in removed]


# Commits whose THREAD.md edit is already known and documented stay visible in the
# audit as warnings rather than disappearing. Empty here by design: this repository
# has a clean history, and adding an entry should require an acknowledged breach.
KNOWN_HISTORY_EXCEPTIONS: dict[str, str] = {}


def _blob_at(sha: str, rel: str) -> str | None:
    """Contents of `rel` at commit `sha`, or None only when it is demonstrably absent.

    The distinction matters. `git show sha:path` fails both when the path does not
    exist in that commit and when the object is unreadable or the repository is
    corrupt. Treating every failure as "the file was not there yet" lets a real
    inspection failure pass as a clean history. Existence is therefore established
    separately with `ls-tree`, which can answer that question on its own.
    """
    listing = _git("ls-tree", "--name-only", sha, "--", rel)
    if not listing.strip():
        return None                      # demonstrably absent at this commit
    return _git("show", f"{sha}:{rel}")  # a failure here is a real error, not absence


def audit_thread_history(thread_path: Path) -> tuple[list[str], list[str]]:
    """Walk the whole committed history and report every deletion, oldest first.

    Returns (errors, warnings). Known exceptions become warnings rather than errors
    and are never hidden: a log that reports itself clean while containing a known
    breach is not auditable. Every inspection failure is an error.
    """
    errors: list[str] = []
    warnings: list[str] = []
    try:
        rel = thread_path.resolve().relative_to(ROOT)
    except ValueError:
        return [], []
    try:
        commits = _git("log", "--reverse", "--format=%H", "--", rel.as_posix()).split()
    except GitUnavailable as e:
        return [f"THREAD.md history audit could not be started (failing closed): {e}"], []
    if not commits:
        return [], []
    try:
        previous_text = None
        for sha in commits:
            try:
                current_text = _blob_at(sha, rel.as_posix())
            except GitUnavailable as e:
                errors.append(f"THREAD.md unreadable at {sha[:7]} (failing closed): {e}")
                continue
            if current_text is None:
                continue  # genuinely absent at this commit
            if previous_text is not None:
                for line in lines_removed(previous_text, current_text):
                    msg = f"THREAD.md append-only violation at {sha[:7]}: removed {line[:80]}"
                    if KNOWN_HISTORY_EXCEPTIONS and sha.startswith(tuple(KNOWN_HISTORY_EXCEPTIONS)):
                        warnings.append(f"acknowledged exception - {msg}")
                    else:
                        errors.append(msg)
            previous_text = current_text
        working = thread_path.read_text(encoding="utf-8", errors="replace")
        for line in lines_removed(previous_text or "", working):
            errors.append("THREAD.md append-only violation in the working tree: "
                          f"removed {line[:80]}")
    except GitUnavailable as e:
        errors.append(f"THREAD.md history audit could not be completed (failing closed): {e}")
    return errors, warnings


def run_checks(thread: Path, queue: Path, decisions: Path,
               verify_revisions: bool = True, check_history: bool = True,
               history_audit: bool = False):
    entries = parse_entries(thread)
    rows, errors = load_queue(queue)
    coupling_errors, warnings = check_coupling(rows, entries, verify_revisions)
    errors.extend(coupling_errors)
    errors.extend(check_decisions(decisions))
    if check_history:
        errors.extend(check_thread_history(thread))
    if history_audit:
        audit_errors, audit_warnings = audit_thread_history(thread)
        errors.extend(audit_errors)
        warnings.extend(audit_warnings)
    warnings.extend(check_chronology(entries))
    stats = {
        "entries": len(entries), "rows": len(rows),
        "accepted": sum(1 for r in rows if r["state"] == "accepted"),
        "changes_requested": sum(1 for r in rows if r["state"] == "changes_requested"),
    }
    return errors, warnings, stats


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Validate FoundrySide collaboration invariants.")
    p.add_argument("--thread", type=Path, default=COLLAB / "THREAD.md")
    p.add_argument("--queue", type=Path, default=COLLAB / "REVIEW_QUEUE.md")
    p.add_argument("--decisions", type=Path, default=COLLAB / "DECISIONS.md")
    p.add_argument("--no-revision-check", action="store_true",
                   help="skip verifying that revisions exist in git history")
    p.add_argument("--no-history", action="store_true",
                   help="skip the append-only check against the previous commit")
    p.add_argument("--history-audit", action="store_true",
                   help="walk the whole history and report every THREAD.md deletion")
    args = p.parse_args(argv)

    errors, warnings, stats = run_checks(
        args.thread, args.queue, args.decisions, not args.no_revision_check,
        not args.no_history, args.history_audit)
    for w in warnings:
        print(f"WARN {w}")
    for e in errors:
        print(f"ERROR {e}")
    print("entries={entries} rows={rows} accepted={accepted} "
          "changes_requested={changes_requested} warnings={w} errors={e}".format(
              w=len(warnings), e=len(errors), **stats))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
