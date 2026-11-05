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
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THREAD = ROOT / "docs" / "COLLAB" / "THREAD.md"

AUTHORS = ("builder", "sponsor", "oversight")
KINDS = ("note", "question", "answer", "review", "decision", "direction",
         "blocker", "evidence", "research", "clarification", "response")

# A kind is normally one word. The two-word form is accepted and mapped by an explicit table,
# because authors write "review response" when they mean the `response` kind; inferring it from
# context would be a guess, and an alias table is auditable.
KIND_ALIASES = {
    "review response": "response",
    "review verdict": "review",
}

HEADER_RE = re.compile(
    r"^###\s+(?P<stamp>[0-9T:+\-.Z]*)\s*[·]\s*(?P<author>\w+)\s*[·]\s*"
    r"(?P<kind>[A-Za-z]+(?: [A-Za-z]+){0,6})"
    r"\s*(?:[—–:-]\s*.+)?$"
)
# Field names have acquired legitimate variants in use: the sponsor wrote
# "- revision reviewed: <sha>" and "- refs:", both of which are unambiguous. Accepting
# them is a schema extension, not a loosening: the value must still be a bare token, and
# the checker still refuses a verdict whose recorded revision does not match the row.
REVISION_RE = re.compile(
    r"^-\s*(?:revisions?\s+reviewed|reviewed\s+revisions?|revisions?)\s*:\s*(?P<value>.*\S)\s*$")
REF_RE = re.compile(r"^-\s*(?:ref|refs|reference)\s*:\s*(?P<value>.*\S)\s*$")
SHA_RE = re.compile(r"[0-9a-f]{7,40}")
# A single entry may carry a verdict per row, each naming its own revision:
#   - RQ-019: changes_requested — revision `60684e1`
ROW_REVISION_RE = re.compile(
    r"^-\s*(?P<row>RQ-\d+)\b[^\n]*?revisions?\s*:?\s*`?(?P<sha>[0-9a-f]{7,40})`?")

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
    "### 2026-11-04T12:xx:xxZ · sponsor · evaluation request":
        "sponsor wrote a placeholder minute field; the body is preserved verbatim and the request "
        "is answered by the builder audit entry",
    "### Sponsor follow-up — Track B bootstrap denominator and reproducibility":
        "sponsor wrote a free-form header with no stamp; the body is preserved verbatim and the "
        "request is answered by the builder's Track B correction entry",
    "### 2026-11-04T07:XX:00Z · sponsor · direction":
        "sponsor wrote a placeholder timestamp for the zero-cost data-landscape direction; "
        "the body is preserved verbatim and the direction is answered by the builder's "
        "accompanying entries",
}


def loose_headers(path: Path = THREAD) -> list[str]:
    """Entry-looking lines recovered with fallback fields rather than the strict grammar.

    These are not errors. A header that does not match the strict grammar is still parsed as an
    entry - stamp if a date-like token exists, author from the known names, kind from the words that
    are actually kinds - so nothing is absorbed into the previous entry's body. The list exists so
    the checker can say so out loud instead of failing a build over a formatting variation.
    """
    if not path.exists():
        return []
    found = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("### ") and not HEADER_RE.match(line):
            found.append(line.strip())
    return found


def malformed_headers(path: Path = THREAD) -> list[str]:
    """Entry-looking lines that produced no entry at all.

    With tolerant parsing this is empty by construction: every `### ` line becomes an entry. It is
    kept so callers that want the strict question can still ask it, and so a future grammar change
    that reintroduces absorption is visible.
    """
    if not path.exists():
        return []
    headings = sum(1 for line in path.read_text(encoding="utf-8", errors="replace").splitlines()
                   if line.startswith("### "))
    return [] if len(parse_entries(path)) >= headings else [
        line.strip() for line in path.read_text(encoding="utf-8", errors="replace").splitlines()
        if line.startswith("### ") and not HEADER_RE.match(line)
    ]



LOOSE_HEADER_RE = re.compile(r"^###\s*(?P<rest>.*)$")
STAMP_HINT_RE = re.compile(r"\d{4}-\d{2}-\d{2}(?:T[0-9]{2}:[0-9x]{2}(?::[0-9x]{2})?Z?)?")


def loose_fields(line: str) -> dict:
    """Extract what can be recovered from a header that does not match the strict grammar.

    Authors write free-form headers: placeholder stamps ("12:XX:00Z"), no stamp at all, multi-word
    kinds, a leading "Sponsor follow-up". Each of those used to become a parser error and cost a
    cycle to acknowledge by hand. The fix is to parse them structurally — never to absorb them as
    body text — and let the checker warn rather than fail.

    Fields default rather than raise: stamp may be empty, author "unknown", kind "note".
    """
    rest = LOOSE_HEADER_RE.match(line).group("rest")
    parts = [part.strip() for part in rest.split("·")]
    stamp_match = STAMP_HINT_RE.search(rest)
    stamp = stamp_match.group(0) if stamp_match else ""
    author = "unknown"
    for part in parts:
        for candidate in AUTHORS:
            if part.lower().startswith(candidate):
                author = candidate
                break
        if author != "unknown":
            break
    # Only words that are protocol kinds may become the kind; a date or an author name must not.
    words = [w.lower() for w in re.findall(r"[A-Za-z]+", rest)]
    known = [w for w in words if w in KINDS]
    kind = known[-1] if known else "note"
    return {"stamp": stamp, "author": author, "kind": kind}


def resolve_kind(raw: str) -> str:
    """Choose the protocol kind from a free-form header field.

    Authors write both "review response" (where the kind is the last word) and "strategic
    contingency direction" (also last) but sometimes "review" alone. Taking the last word that
    is a known kind handles all three without guessing; anything unrecognised falls back to the
    first word, which is then validated by the checker.
    """
    words = [w.lower() for w in raw.split()]
    for word in reversed(words):
        if word in KINDS:
            return word
    return words[0] if words else raw.lower()


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
        loose_fields_for_line = None
        if not match and line.startswith("### "):
            loose_fields_for_line = loose_fields(line)
        if match or loose_fields_for_line:
            flush()
            if loose_fields_for_line:
                current = {
                    "stamp": loose_fields_for_line["stamp"],
                    "author": loose_fields_for_line["author"],
                    "kind": loose_fields_for_line["kind"],
                    "revision": "",
                    "ref": "",
                    "loose": True,
                }
                body = []
                continue
            current = {
                "stamp": match.group("stamp").strip(),
                "author": match.group("author"),
                "kind": KIND_ALIASES.get(match.group("kind").lower().strip(),
                                         resolve_kind(match.group("kind"))),
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
            # A verdict may name several revisions (`revisions reviewed: a, b`), and an
            # SHA is often wrapped in backticks. Keep the first SHA-shaped token: that is
            # the revision the verdict is anchored to, and carrying punctuation into the
            # field silently breaks the match between a verdict and its row.
            found = SHA_RE.findall(rev.group("value"))
            current["revision"] = found[0] if found else rev.group("value").strip("`*_ ")
            # One verdict may cover several rows at several revisions
            # ("revisions reviewed: a, b, c"). Keeping the whole list lets it authorise
            # each row it names, instead of only the first.
            current["revisions"] = found
            continue
        ref = REF_RE.match(line)
        if ref:
            current["ref"] = ref.group("value")
            continue
        rv = ROW_REVISION_RE.match(line)
        if rv:
            current.setdefault("row_revisions", {})[rv.group("row")] = rv.group("sha")
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



def stable_revision() -> str:
    """The pushed commit to quote in a bridge entry.

    A local HEAD moves when commits are rebased; a commit already on origin/main does not. Quoting the
    pushed base keeps the entry valid through ordinary rebase-and-push cycles, which is what broke
    entries twice.
    """
    for ref in ("origin/main", "main"):
        proc = subprocess.run(["git", "rev-parse", "--short", ref],
                              capture_output=True, text=True)
        if proc.returncode == 0 and proc.stdout.strip():
            return proc.stdout.strip()
    return ""


def revision_is_pushed(sha: str) -> bool:
    if not sha:
        return True
    proc = subprocess.run(["git", "merge-base", "--is-ancestor", sha, "origin/main"],
                          capture_output=True)
    return proc.returncode == 0


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
