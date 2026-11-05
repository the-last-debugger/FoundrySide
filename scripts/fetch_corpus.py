"""Fetch the public corpus into research/data, with recorded provenance.

The files are football-data.co.uk division CSVs: free, publicly published, no account, no payment, no
contact. The day-pass of 2026-11-05 explicitly permits this class of source provided access
conditions are respected and provenance is recorded, so:

* one request at a time with a polite delay, no parallelism, no retries hammering the host;
* no attempt to bypass anything — if a file 404s it is recorded as missing;
* a provenance record written next to the data: source, retrieval date, licence note, transforms.

The data directory is gitignored, so this writes files but never commits them.

    python scripts/fetch_corpus.py            # skip files already present
    python scripts/fetch_corpus.py --force    # re-download
    python scripts/fetch_corpus.py --seasons 2021 2122 2223
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "research" / "data"
PROVENANCE = DATA / "PROVENANCE.json"

BASE = "https://football-data.co.uk/mmz4281/{season}/{league}.csv"
LEAGUES = ["E0", "E1", "D1", "F1", "I1", "N1", "P1", "SP1"]
SEASONS = ["2021", "2122", "2223", "2324", "2425"]
DELAY_SECONDS = 1.0

LICENCE_NOTE = (
    "INTERPRETATION, NOT A LEGAL DETERMINATION. The files are published free of charge at "
    "https://football-data.co.uk/mmz4281/<season>/<league>.csv with no account or payment required. "
    "The site footer at https://football-data.co.uk/ states '© Football-Data. Liability Disclaimer. "
    "All Rights Reserved', and no licence text granting redistribution was located at "
    "https://football-data.co.uk/notes.txt, /data.php or /disclaimer.php (terms.php and terms.txt "
    "return 404). On that basis this project treats the files as usable for internal analysis only and "
    "does not commit or redistribute them. A public URL and a rights-reserved footer do not by "
    "themselves establish a licence grant; the position is recorded as unresolved uncertainty, and "
    "P-03 in docs/COLLAB/PROPOSALS.md remains open."
)


def fetch(season: str, league: str, timeout: int = 30) -> str | None:
    url = BASE.format(season=season, league=league)
    request = urllib.request.Request(url, headers={"User-Agent": "FoundrySide-research/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read().decode("latin-1")
    except urllib.error.HTTPError as exc:
        print(f"  {league} {season}: HTTP {exc.code}")
    except Exception as exc:  # network failure: record and continue
        print(f"  {league} {season}: {type(exc).__name__}")
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch the public corpus with provenance")
    parser.add_argument("--force", action="store_true", help="re-download existing files")
    parser.add_argument("--seasons", nargs="*", default=SEASONS)
    parser.add_argument("--leagues", nargs="*", default=LEAGUES)
    parser.add_argument("--delay", type=float, default=DELAY_SECONDS)
    args = parser.parse_args()

    DATA.mkdir(parents=True, exist_ok=True)
    records = []
    fetched = skipped = failed = 0

    for season in args.seasons:
        for league in args.leagues:
            target = DATA / f"{league}_{season}.csv"
            if target.exists() and not args.force:
                skipped += 1
                try:
                    existing = list(csv.DictReader(io.StringIO(target.read_text(encoding="latin-1"))))
                    records.append({"league": league, "season": season, "status": "present",
                                    "fixtures": len(existing)})
                except Exception:
                    records.append({"league": league, "season": season, "status": "present"})
                continue
            print(f"fetching {league} {season}")
            text = fetch(season, league)
            if text is None:
                failed += 1
                records.append({"league": league, "season": season, "status": "missing"})
                continue
            rows = list(csv.DictReader(io.StringIO(text)))
            if not rows:
                failed += 1
                records.append({"league": league, "season": season, "status": "empty"})
                continue
            target.write_text(text, encoding="latin-1")
            fetched += 1
            records.append({"league": league, "season": season, "status": "fetched",
                            "fixtures": len(rows), "bytes": len(text)})
            time.sleep(args.delay)

    PROVENANCE.write_text(json.dumps({
        "source": "football-data.co.uk",
        "url_pattern": BASE,
        "retrieved_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "leagues": args.leagues,
        "seasons": args.seasons,
        "licence": LICENCE_NOTE,
        "transformations": "none — files stored as received; parsing happens at read time",
        "total_fixtures": sum(r.get("fixtures", 0) for r in records),
        "files": records,
    }, indent=2), encoding="utf-8")

    print(f"\nfetched {fetched}, skipped {skipped}, failed {failed}")
    try:
        shown = PROVENANCE.relative_to(ROOT)
    except ValueError:  # tests point DATA at a temporary directory
        shown = PROVENANCE
    print(f"provenance: {shown}")
    return 0 if fetched or skipped else 1


if __name__ == "__main__":
    raise SystemExit(main())
