"""Export a self-contained slice of the corpus for the Android app.

The app runs offline: no server, no network. That means the engine has to come to the data, so this
writes a JSON file of fixtures the JavaScript can de-vig itself. It is a **slice**, not the corpus —
enough to demonstrate, small enough to live in an APK asset.

    python scripts/export_app_data.py                 # 600 fixtures
    python scripts/export_app_data.py --limit 1200
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import engine  # noqa: E402

OUT = ROOT / "app" / "android" / "assets" / "fixtures.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Export fixture data for the Android app")
    parser.add_argument("--limit", type=int, default=600)
    parser.add_argument("--out", default=str(OUT))
    parser.add_argument("--demo", action="store_true", help="use synthetic fixtures")
    args = parser.parse_args()

    if args.demo:
        from app import demo_data
        fixtures = demo_data.synthetic_fixtures(args.limit)
        source = "synthetic (demonstration)"
    else:
        fixtures = engine.load_fixtures(limit=args.limit)
        source = "held corpus"

    if not fixtures:
        print("no fixtures available; run scripts/fetch_corpus.py or pass --demo")
        return 1

    payload = {
        "source": source,
        "note": "Closing quotes only. No timestamps, no account terms, no limits.",
        "count": len(fixtures),
        "fixtures": [
            {
                "k": f.key, "d": f.div, "date": f.date, "h": f.home, "a": f.away,
                "odds": {name: [round(o, 3) for o in prices] for name, prices in f.odds.items()},
                "totals": {name: [round(o, 3) for o in prices] for name, prices in f.totals.items()},
            }
            for f in fixtures
        ],
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)}: {len(fixtures)} fixtures, {out.stat().st_size / 1024:.0f} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
