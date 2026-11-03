"""Stamp generated reports with the hash of the script that produced them.

Twice now a report has been committed while its generator had moved on — the cluster-power
stability figures, and the pilot-sizing diagnostics before them. Both were caught by a
reviewer reading the artefact against the code, which is an expensive way to find a stale
file.

A hash of the generator, written into the artefact, makes the drift a failing test instead:
either the report matches the script that claims to have produced it, or the suite says so.

**Limit, stated:** this catches code drift, not data drift. A report regenerated against
new CSV files from an unchanged script will still verify. That is the right trade — the
cheap check catches the mistake that actually happened twice.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

PATTERN = re.compile(r"<!-- generated-by: (?P<name>\S+) sha256=(?P<digest>[0-9a-f]{12}) -->")


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


def stamp(script: Path) -> str:
    """A comment line to embed in the generated markdown."""
    return f"<!-- generated-by: {script.name} sha256={_digest(script)} -->"


def verify(markdown: Path) -> list[str]:
    """Problems with a report's stamp, empty when it matches its generator."""
    if not markdown.exists():
        return [f"{markdown.name}: report does not exist"]
    match = PATTERN.search(markdown.read_text(encoding="utf-8"))
    if not match:
        return [f"{markdown.name}: no generator stamp — add report_stamp.stamp(...)"]
    script = markdown.parent / match.group("name")
    if not script.exists():
        return [f"{markdown.name}: stamped by {match.group('name')}, which does not exist"]
    current = _digest(script)
    if current != match.group("digest"):
        return [f"{markdown.name}: generated from {script.name} at {match.group('digest')}, "
                f"but {script.name} is now {current} — regenerate the report"]
    return []
