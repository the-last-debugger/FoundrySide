"""Generate an index of the bridge thread.

`docs/COLLAB/THREAD.md` is append-only and now half a megabyte. That is correct — it is the record —
but it is not readable as a whole, so a reviewer has to grep it. This script derives a navigable index
without touching the thread itself:

* counts by author and kind,
* every entry with its stamp, author, kind and the file it references,
* a per-reference grouping, so "what was said about this file" is one lookup.

    python scripts/thread_index.py

Writes docs/COLLAB/THREAD_INDEX.md.
"""

from __future__ import annotations

import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import collab_note  # noqa: E402

OUT = ROOT / "docs" / "COLLAB" / "THREAD_INDEX.md"
THREAD = ROOT / "docs" / "COLLAB" / "THREAD.md"
KNOWN_AUTHORS = {"builder", "sponsor", "oversight"}


def summarise(body: str, limit: int = 110) -> str:
    """First meaningful line of an entry, flattened for a table cell."""
    for line in (body or "").splitlines():
        text = line.strip()
        if not text or text.startswith(("### ", "|", "-", "**")):
            continue
        text = " ".join(text.split())
        return text if len(text) <= limit else text[: limit - 1] + "…"
    return ""


def build(entries: list[dict]) -> str:
    by_author = Counter(e.get("author") or "unknown" for e in entries)
    by_kind = Counter(e.get("kind") or "unclassified" for e in entries)
    by_ref = defaultdict(list)
    for entry in entries:
        ref = (entry.get("ref") or "").strip()
        if ref:
            by_ref[ref].append(entry)

    lines = [
        "<!-- generated-by: thread_index.py; regenerate rather than edit -->",
        "",
        "# Bridge index",
        "",
        # Size is measured from normalised text, not the file on disk: a CRLF checkout is larger than
        # an LF one, so a byte count would make the generated index differ between environments.
        f"Derived from `THREAD.md` "
        f"({len(THREAD.read_text(encoding='utf-8')) / 1024:.0f} KB, {len(entries)} entries). "
        "The thread is append-only and is the record; this index is a navigation aid and is regenerated.",
        "",
        "## By author and kind",
        "",
        "| Author | Entries |",
        "| --- | --- |",
    ]
    for author, count in by_author.most_common():
        lines.append(f"| {author} | {count} |")
    unknown = sorted(a for a in by_author if a not in KNOWN_AUTHORS)
    if unknown:
        lines += ["",
                  "Authors outside the expected set appear exactly as written in the header. "
                  "They are shown rather than normalised, because rewriting the record would hide "
                  "a malformed entry instead of revealing it: " + ", ".join(unknown) + "."]
    lines += ["", "| Kind | Entries |", "| --- | --- |"]
    for kind, count in by_kind.most_common():
        lines.append(f"| {kind} | {count} |")

    lines += ["", "## Most recent entries", "",
              "| Stamp | Author | Kind | Ref | Opening line |",
              "| --- | --- | --- | --- | --- |"]
    for entry in entries[-40:][::-1]:
        stamp = (entry.get("stamp") or "—")[:19]
        ref = (entry.get("ref") or "—").strip("`")
        lines.append(f"| {stamp} | {entry.get('author') or 'unknown'} | "
                     f"{entry.get('kind') or '—'} | {ref} | {summarise(entry.get('body', ''))} |")

    lines += ["", "## By referenced file", "",
              "Files that have been discussed most, with the newest entries first.", ""]
    for ref, group in sorted(by_ref.items(), key=lambda kv: len(kv[1]), reverse=True)[:25]:
        lines.append(f"**{ref}** — {len(group)} entr{'y' if len(group) == 1 else 'ies'}")
        lines.append("")
        for entry in group[-3:][::-1]:
            lines.append(f"- {(entry.get('stamp') or '—')[:19]} · {entry.get('author')} · "
                         f"{summarise(entry.get('body', ''), 90)}")
        lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


def main() -> int:
    entries = collab_note.parse_entries()
    if not entries:
        print("no entries parsed; is THREAD.md present?")
        return 1
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(build(entries), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}: {len(entries)} entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
