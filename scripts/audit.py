"""Repository audit — the consistency checks that keep being done by hand.

Every failure this project has had to correct repeatedly was a *cross-document* inconsistency: a count
that drifted, a claim that survived in a generated report, a revision erased by a rebase, a digest left
stale, a link to a document that moved. Each was found by a person reading carefully, which does not
scale and does not happen under time pressure.

    python scripts/audit.py            # human-readable report
    python scripts/audit.py --quiet    # only failures
    python scripts/audit.py --json     # machine-readable

Exit code is 0 when every check passes, 1 otherwise — so it can gate CI.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

DOCS = ROOT / "docs"
RESEARCH = ROOT / "research"
CONSOLIDATED = DOCS / "CONSOLIDATED_FINDINGS.md"
PROGRAMME = DOCS / "RESEARCH_PROGRAMME.md"
THREAD = DOCS / "COLLAB" / "THREAD.md"
DIGEST = DOCS / "REVIEW_DIGEST.md"

# Phrases that have had to be removed from documents more than once.
STALE_PHRASES = (
    "tradeable",
    "can get a better price",
    "shopping improves the price",
    "genuinely better than the average",
    "blocked in this environment",
)

MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\((?!https?://|#|mailto:)([^)\s]+)\)")


@dataclass
class Check:
    name: str
    ok: bool
    detail: str = ""


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)


def check_reports_cited() -> Check:
    reports = sorted(p.name for p in RESEARCH.glob("*.md"))
    summary = CONSOLIDATED.read_text(encoding="utf-8") if CONSOLIDATED.exists() else ""
    missing = [r for r in reports if r not in summary]
    return Check("every report is cited by the summary", not missing,
                 f"uncited: {', '.join(missing)}" if missing else f"{len(reports)} reports")


def check_generator_count() -> Check:
    from repro_sweep import GENERATORS
    counted = len(GENERATORS)
    texts = [PROGRAMME.read_text(encoding="utf-8") if PROGRAMME.exists() else ""]
    # Generated and historical documents are excluded: the digest quotes the queue rows verbatim, and
    # a row describing a past run ("23 generators") is a record of that run, not a current claim.
    skip = {"REVIEW_DIGEST.md", "REVIEW_QUEUE.md", "THREAD.md"}
    texts += [p.read_text(encoding="utf-8") for p in DOCS.glob("*.md") if p.name not in skip]
    stated = {int(m) for t in texts for m in re.findall(r"(\d+)\s+generators", t)}
    bad = sorted(n for n in stated if n != counted)
    return Check("generator count matches the sweep", not bad,
                 f"sweep has {counted}; documents claim {bad}" if bad else f"{counted} generators")


def check_experiment_registry() -> Check:
    if not PROGRAMME.exists():
        return Check("experiment registry is contiguous", False, "programme document missing")
    ids = sorted({int(m) for m in re.findall(r"\|\s*E(\d+)\s*\|", PROGRAMME.read_text(encoding="utf-8"))})
    if not ids:
        return Check("experiment registry is contiguous", False, "no experiments found")
    expected = list(range(1, max(ids) + 1))
    missing = [n for n in expected if n not in ids]
    return Check("experiment registry is contiguous", not missing,
                 f"missing E{missing}" if missing else f"E1–E{max(ids)}")


def check_stale_phrases() -> Check:
    hits = []
    for path in list(DOCS.glob("*.md")) + list(RESEARCH.glob("*.md")) + [ROOT / "README.md"]:
        if not path.exists():
            continue
        lowered = path.read_text(encoding="utf-8").lower()
        for phrase in STALE_PHRASES:
            if phrase in lowered:
                hits.append(f"{path.name}: {phrase}")
    return Check("no removed overclaims have returned", not hits, "; ".join(hits[:4]) if hits else "")


def check_revisions() -> Check:
    if not THREAD.exists():
        return Check("bridge revisions resolve", False, "thread missing")
    text = THREAD.read_text(encoding="utf-8")
    pattern = re.compile(r"(?:revision|commit|ref)\s*:?\s*`?([0-9a-f]{7,40})`?", re.I)
    tokens = sorted({m.group(1) for m in pattern.finditer(text)})
    from collab_note import ACKNOWLEDGED_MALFORMED  # noqa: F401  (import keeps module warm)
    known_rewritten = {"6a9f0e4", "09e562e", "1d0f3dd", "49701af", "4db2627", "88bb674", "a867e76"}
    bad = []
    for sha in tokens:
        if sha in known_rewritten:
            continue
        if _git("merge-base", "--is-ancestor", sha, "HEAD").returncode != 0:
            bad.append(sha)
    return Check("bridge revisions resolve", not bad, f"unreachable: {bad}" if bad else f"{len(tokens)} refs")


def check_digest_fresh() -> Check:
    if not DIGEST.exists():
        return Check("review digest is current", True, "no digest")
    import review_digest
    marker = "<!-- as-of: "
    index = DIGEST.read_text(encoding="utf-8").find(marker)
    as_of = (DIGEST.read_text(encoding="utf-8")[index + len(marker):].split("-->")[0].strip()
             if index >= 0 else None)
    original = review_digest.OUT
    try:
        with tempfile.TemporaryDirectory() as tmp:
            review_digest.OUT = Path(tmp) / "digest.md"
            review_digest.write(as_of)
            fresh = review_digest.OUT.read_text(encoding="utf-8")
    finally:
        review_digest.OUT = original
    current = DIGEST.read_text(encoding="utf-8")
    return Check("review digest is current", current == fresh,
                 "run python scripts/review_digest.py" if current != fresh else "")


def check_links() -> Check:
    broken = []
    for path in list(DOCS.glob("*.md")) + [ROOT / "README.md"]:
        if not path.exists():
            continue
        for target in MARKDOWN_LINK.findall(path.read_text(encoding="utf-8")):
            target = target.split("#", 1)[0].strip()
            if not target:
                continue
            candidate = (path.parent / target).resolve()
            if not candidate.exists():
                broken.append(f"{path.name} → {target}")
    return Check("document links resolve", not broken, "; ".join(broken[:4]) if broken else "")


def check_provenance() -> Check:
    data = RESEARCH / "data"
    if not data.exists():
        return Check("corpus provenance recorded", True, "corpus absent (demo mode only)")
    prov = data / "PROVENANCE.json"
    if not prov.exists():
        return Check("corpus provenance recorded", False, "data present without PROVENANCE.json")
    try:
        record = json.loads(prov.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return Check("corpus provenance recorded", False, "PROVENANCE.json is not valid JSON")
    files = len(record.get("files", []))
    return Check("corpus provenance recorded", files > 0,
                 f"{files} files, {record.get('total_fixtures', 0):,} fixtures" if files else "no files")


def check_malformed_headers() -> Check:
    from collab_note import malformed_headers
    bad = malformed_headers()
    return Check("every bridge entry parses", not bad, f"{len(bad)} unparsed" if bad else "")


CHECKS = (
    check_reports_cited,
    check_generator_count,
    check_experiment_registry,
    check_stale_phrases,
    check_revisions,
    check_digest_fresh,
    check_links,
    check_provenance,
    check_malformed_headers,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Repository consistency audit")
    parser.add_argument("--quiet", action="store_true", help="print failures only")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args()

    results = [check() for check in CHECKS]
    failures = [r for r in results if not r.ok]

    if args.json:
        print(json.dumps({"checks": [r.__dict__ for r in results],
                          "passed": len(results) - len(failures), "failed": len(failures)}, indent=2))
    else:
        for result in results:
            if args.quiet and result.ok:
                continue
            mark = "PASS" if result.ok else "FAIL"
            line = f"[{mark}] {result.name}"
            if result.detail:
                line += f" — {result.detail}"
            print(line)
        print(f"\n{len(results) - len(failures)}/{len(results)} checks passed")

    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
