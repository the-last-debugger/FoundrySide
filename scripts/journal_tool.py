"""Journal growth management.

The assessment journal is append-only by design: an entry is a record of what was said at a moment and
must not be rewritten. That is a correctness property, and it is also how a file grows without bound.
The two are reconciled by compaction at the *duplicate* level: re-recording the same fixture, outcome
and quote adds no information, so those copies are removed and everything distinct is kept, in order.

    python scripts/journal_tool.py --stats
    python scripts/journal_tool.py --compact
    python scripts/journal_tool.py --compact --dry-run
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import journal  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect or compact the assessment journal")
    parser.add_argument("--stats", action="store_true", help="report size and duplicates")
    parser.add_argument("--compact", action="store_true", help="remove duplicate records")
    parser.add_argument("--dry-run", action="store_true", help="report what compaction would do")
    parser.add_argument("--path", default=None, help="journal path (default: var/assessments.jsonl)")
    args = parser.parse_args()

    path = Path(args.path) if args.path else None

    if not args.stats and not args.compact:
        parser.error("choose --stats, --compact, or both")

    if args.stats or (args.compact and args.dry_run):
        info = journal.stats(path)
        if not info["exists"]:
            print("journal: not created yet")
        else:
            print(f"journal: {info['entries']} entries, {info['distinct']} distinct, "
                  f"{info['bytes'] / 1024:.1f} KB, {info['duplicates']} duplicate(s)")

    if args.compact:
        if args.dry_run:
            info = journal.stats(path)
            print(f"dry run: would remove {info['duplicates']} duplicate record(s)")
        else:
            result = journal.compact(path)
            print(f"compacted: {result['before']} → {result['after']} "
                  f"({result['removed']} removed)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
