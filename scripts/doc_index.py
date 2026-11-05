"""Generate an index of the documentation.

Twenty of thirty-one documents were reachable only by listing the directory: cited from a research
report, or from the bridge, but not from anywhere a reader starts. This writes a single page that names
every document, its title, its role and its opening sentence, so the corpus is navigable without
knowing its structure in advance.

    python scripts/doc_index.py

Writes docs/INDEX.md.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUT = DOCS / "INDEX.md"

# Roles are inferred from the filename, which is the one convention this repository has kept.
RULES = (
    ("prereg", "Preregistration", "Written before a run; fixes the estimand"),
    ("proposal", "Proposal", "Scope and settlement of what the project would do"),
    ("critique", "Review", "A critique of the plan"),
    ("protocol", "Protocol", "The evaluation rules studies must follow"),
    ("blocker", "Blocker", "What stopped a study and what would unblock it"),
    ("feasibility", "Feasibility", "Whether a route can be assessed at all"),
    ("readiness", "Readiness", "What a gated study would need"),
    ("assessment", "Assessment", "A decision document"),
    ("contingency", "Fallback", "A recorded alternative, not a pivot"),
    ("triage", "Triage", "Which leads are alive and why"),
    ("queue", "Register", "What is active, next and deferred"),
    ("programme", "Register", "The experiment register"),
    ("handover", "Entry point", "One page: state, verification, next steps"),
    ("conclusion", "Entry point", "The research result and its limits"),
    ("findings", "Summary", "The evidence in one document"),
    ("demo", "Product", "How to run the demonstrator"),
    ("product", "Product", "Product direction and what it refuses to build"),
    ("decision", "Decision", "Options with costs"),
    ("ledger", "Record", "Assigned actions and their state"),
    ("parked", "Record", "Deliberately not being done"),
    ("source", "Data", "What sources exist and on what terms"),
    ("data", "Data", "What the corpus contains"),
    ("strategy", "Direction", "Where the project should go"),
    ("compute", "Constraint", "What the work costs to run"),
    ("index", "Navigation", "This page"),
)


def role_for(name: str) -> tuple[str, str]:
    lowered = name.lower()
    for key, role, purpose in RULES:
        if key in lowered:
            return role, purpose
    return "Document", ""


def first_heading(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def opening_line(text: str) -> str:
    """The first sentence of prose, skipping headings and metadata."""
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", "|", "-", "**", "<!--")):
            continue
        sentence = re.split(r"(?<=[.!?])\s", stripped, maxsplit=1)[0]
        return sentence[:160]
    return ""


def build() -> str:
    rows = []
    for path in sorted(DOCS.glob("*.md")):
        if path.name == OUT.name:
            continue
        text = path.read_text(encoding="utf-8")
        role, purpose = role_for(path.name)
        rows.append((path.name, first_heading(text) or path.stem, role, purpose,
                     opening_line(text)))

    counts: dict[str, int] = {}
    for row in rows:
        counts[row[2]] = counts.get(row[2], 0) + 1

    lines = [
        "<!-- generated-by: doc_index.py; regenerate rather than edit -->",
        "",
        "# Documentation index",
        "",
        f"Every document in `docs/`: **{len(rows)}** files. Generated, so it cannot fall behind the "
        "directory.",
        "",
        "| Document | Title | Role | What it is for |",
        "| --- | --- | --- | --- |",
    ]
    for name, title, role, purpose, _ in rows:
        lines.append(f"| [{name}]({name}) | {title} | {role} | {purpose} |")

    lines += ["", "## Opening line of each", ""]
    for name, _, _, _, opening in rows:
        if opening:
            lines.append(f"- **[{name}]({name})** — {opening}")

    lines += ["", "## By role", "", "| Role | Documents |", "| --- | --- |"]
    for role, count in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"| {role} | {count} |")

    return "\n".join(lines).rstrip("\n") + "\n"


def main() -> int:
    content = build()
    OUT.write_text(content, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}: {content.count(chr(10))} lines")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
