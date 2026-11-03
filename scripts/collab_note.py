"""Append entries to docs/COLLAB/THREAD.md without breaking its shape.

Ported from the ODE and OLPRS_v2 bridges. Same entry format, same authors, same
kinds: the protocol is deliberately identical across the three repositories so a
reader of one can read the others.

    python scripts/collab_note.py --author builder --kind evidence \\
        --message "9 tests pass" --revision e590f9c

    python scripts/collab_note.py --check
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THREAD = ROOT / "docs" / "COLLAB" / "THREAD.md"

AUTHORS = ("builder", "sponsor", "oversight")
KINDS = ("note", "question", "answer", "review", "decision", "direction",
         "blocker", "evidence", "research", "clarification", "response")

HEADER_RE = re.compile(
    r"^###\s+(?P<stamp>[0-9T:+\-.Z]*)\s*[·]\s*(?P<author>\w+)\s*[·]\s*(?P<kind>\w+)\s*$"
)
# Field names have acquired legitimate variants in use: the sponsor wrote
# "- revision reviewed: <sha>" and "- refs:", both of which are unambiguous. Accepting
# them is a schema extension, not a loosening: the value must still be a bare token, and
# the checker still refuses a verdict whose recorded revision does not match the row.
REVISION_RE = re.compile(
    r"^-\s*(?:revision|revision reviewed|reviewed revision)\s*:\s*(?P<value>\S*)\s*$")
REF_RE = re.compile(r"^-\s*(?:ref|refs|reference)\s*:\s*(?P<value>.*\S)\s*$")

# A header that starts with '### ' but does not match HEADER_RE used to be treated as
# body text of the preceding entry. That is a fail-open parse: the entry disappears
# from the record, its author and kind are lost, and the checker reports a clean
# thread. Malformed headers are therefore surfaced explicitly. Entries acknowledged
# here stay visible as warnings on every run rather than being hidden or rewritten,
# because THREAD.md is append-only and the malformed line is part of the history.
ACKNOWLEDGED_MALFORMED = {
    "### 2026-11-03T12:XX:00Z · sponsor · response":
        "sponsor wrote a placeholder timestamp; the entry is parsed as body of the "
        "preceding builder entry and is restated by the builder answer entry of "
        "2026-11-03T12:20Z",
}


def malformed_headers(path: Path = THREAD) -> list[str]:
    """Entry-looking lines that do not satisfy the header grammar, in file order."""
    if not path.exists():
        return []
    found = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("### ") and not HEADER_RE.match(line):
            found.append(line.strip())
    return found


def parse_entries(path: Path = THREAD) -> list[dict[str, str]]:
    """Parse the append-only thread into structured entries.

    Entries are delimited by `### ` headers. Anything before the first header (the
    document title and preamble) is ignored, as is any trailing content inside an
    entry that is neither `- revision:` nor `- ref:`.
    """
    if not path.exists():
        return []
    entries: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    body: list[str] = []

    def flush() -> None:
        if current is None:
            return
        current["message"] = "\n".join(body).strip()
        entries.append(current)

    for line in path.read_text(encoding="utf-8").splitlines():
        match = HEADER_RE.match(line)
        if match:
            flush()
            current = {
                "stamp": match.group("stamp").strip(),
                "author": match.group("author"),
                "kind": match.group("kind"),
                "revision": "",
                "ref": "",
            }
            body = []
            continue
        if current is None:
            continue
        if line.startswith("### "):
            flush()
            current, body = None, []
            continue
        rev = REVISION_RE.match(line)
        if rev:
            # A SHA is often written as `abc1234` in prose. The emphasis is formatting,
            # not data, and carrying it into the field silently breaks the match between
            # a verdict and the row it authorises.
            current["revision"] = rev.group("value").strip("`*_ ")
            continue
        ref = REF_RE.match(line)
        if ref:
            current["ref"] = ref.group("value")
            continue
        body.append(line)
    flush()
    return entries


def build_entry(author: str, kind: str, message: str,
                revision: str | None = None, ref: str | None = None,
                stamp: str | None = None) -> str:
    if author not in AUTHORS:
        raise SystemExit(f"author must be one of: {', '.join(AUTHORS)}")
    if kind not in KINDS:
        raise SystemExit(f"kind must be one of: {', '.join(KINDS)}")
    if not message.strip():
        raise SystemExit("message must not be empty")
    stamp = stamp or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [f"### {stamp} · {author} · {kind}", message.strip()]
    if revision:
        lines.append(f"- revision: {revision}")
    if ref:
        lines.append(f"- ref: {ref}")
    return "\n".join(lines)


def append(entry: str, path: Path = THREAD) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text(encoding="utf-8").rstrip() if path.exists() else ""
    if not existing:
        existing = ("# Thread\n\nAppend-only chronological log for the builder, "
                    "sponsor and oversight. New entries are appended by\n"
                    "`scripts/collab_note.py`; existing entries are never edited.\n")
    path.write_text(existing + "\n\n" + entry + "\n", encoding="utf-8")


def check(path: Path = THREAD) -> int:
    entries = parse_entries(path)
    problems = 0
    for entry in entries:
        if entry["author"] not in AUTHORS:
            print(f"ERROR unknown author {entry['author']!r} at {entry['stamp']}")
            problems += 1
        if entry["kind"] not in KINDS:
            print(f"ERROR unknown kind {entry['kind']!r} at {entry['stamp']}")
            problems += 1
        if not entry["message"]:
            print(f"ERROR empty message at {entry['stamp']}")
            problems += 1
        if entry["kind"] in ("review", "evidence") and not entry["revision"]:
            print(f"WARN {entry['kind']} at {entry['stamp']} records no revision")
    for header in malformed_headers(path):
        if header in ACKNOWLEDGED_MALFORMED:
            print(f"WARN malformed header (acknowledged): {header}")
        else:
            print(f"ERROR malformed header: {header}")
            problems += 1
    print(f"entries={len(entries)} problems={problems}")
    return 0 if problems == 0 else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Append or validate collab thread entries.")
    parser.add_argument("--author", choices=AUTHORS)
    parser.add_argument("--kind", choices=KINDS)
    parser.add_argument("--message")
    parser.add_argument("--revision")
    parser.add_argument("--ref")
    parser.add_argument("--stamp")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--thread", type=Path, default=THREAD)
    args = parser.parse_args(argv)

    if args.check:
        return check(args.thread)
    if not (args.author and args.kind and args.message):
        parser.error("--author, --kind and --message are required unless --check is used")
    append(build_entry(args.author, args.kind, args.message, args.revision,
                       args.ref, args.stamp), args.thread)
    print("appended")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
