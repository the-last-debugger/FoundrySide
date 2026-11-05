"""Check the JavaScript engine against the Python engine, fixture by fixture.

The Android app carries a JavaScript port of the engine because it runs offline: there is no Python on
a phone. A port drifts, and `docs/ANDROID.md` said so without doing anything about it. This does
something:

* exports a set of fixtures the two can share,
* runs the JavaScript under Node and has it compute de-vig, assessments and structure tables,
* recomputes the same quantities in Python and compares to a tolerance.

    python scripts/check_js_parity.py
    python scripts/check_js_parity.py --limit 50

Exit code 0 means the two engines agree on every compared quantity.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import engine  # noqa: E402

APP_JS = ROOT / "app" / "android" / "assets" / "www" / "app.js"
# Both engines round their public outputs identically, so the comparison is exact rather than fuzzy.
TOLERANCE = 1e-9

NODE_RUNNER = """
const fs = require('fs');
const path = process.argv[2];
const input = JSON.parse(fs.readFileSync(path, 'utf8'));
eval(fs.readFileSync(input.appJs, 'utf8'));
const fsApi = globalThis.__fs;
const out = input.fixtures.map(f => {
  const a = fsApi.assess(f, 'H');
  return {
    key: f.k,
    devig_avg: fsApi.devig(f.odds.Avg || f.odds.Max),
    overround_max: fsApi.overround(f.odds.Max || f.odds.Avg),
    price: a.price,
    book: a.book,
    market: a.market,
    price_implied: a.priceImplied,
  };
});
process.stdout.write(JSON.stringify({
  rows: out,
  structures: fsApi.compareStructures(200, [1.5, 3, 6], 0.05),
}));
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare the JS engine against Python")
    parser.add_argument("--limit", type=int, default=25)
    args = parser.parse_args()

    if not APP_JS.exists():
        print(f"missing {APP_JS}")
        return 1
    try:
        node_version = subprocess.run(["node", "--version"], capture_output=True, text=True)
    except FileNotFoundError:
        print("node is not installed; skipping parity check")
        return 0

    fixtures = engine.load_fixtures(limit=args.limit)
    if not fixtures:
        print("no fixtures available; run scripts/fetch_corpus.py")
        return 1

    payload = {
        "appJs": str(APP_JS),
        "fixtures": [
            {"k": f.key, "odds": {n: [round(o, 3) for o in p] for n, p in f.odds.items()}}
            for f in fixtures
        ],
    }

    with tempfile.TemporaryDirectory() as tmp:
        data_path = Path(tmp) / "input.json"
        runner = Path(tmp) / "runner.js"
        data_path.write_text(json.dumps(payload), encoding="utf-8")
        runner.write_text(NODE_RUNNER, encoding="utf-8")
        proc = subprocess.run(["node", str(runner), str(data_path)], capture_output=True, text=True)
        if proc.returncode != 0:
            print("node failed:")
            print((proc.stderr or "")[-1200:])
            return 1
        js = json.loads(proc.stdout)

    mismatches = []
    for fixture, js_row in zip(fixtures, js["rows"]):
        py = engine.assess_selection(fixture, "H")
        py_probs = engine.devig(fixture.odds["Avg"] if "Avg" in fixture.odds else fixture.odds["Max"])
        comparisons = [
            ("price", js_row["price"], py["best_recorded_price"]),
            ("market", js_row["market"], py["market_implied"]),
            ("price_implied", js_row["price_implied"], py["price_implied"]),
            ("overround", js_row["overround_max"],
             engine.overround(fixture.odds.get("Max", list(fixture.odds.values())[0]))),
        ]
        for name, a, b in comparisons:
            if abs(float(a) - float(b)) > TOLERANCE:
                mismatches.append(f"{fixture.key}: {name} js={a} py={b}")
        for i, (a, b) in enumerate(zip(js_row["devig_avg"], py_probs)):
            if abs(a - b) > TOLERANCE:
                mismatches.append(f"{fixture.key}: devig[{i}] js={a} py={b}")

    py_structures = engine.compare_structures(200.0, [1.5, 3.0, 6.0], 0.05)["structures"]
    for js_row, py_row in zip(js["structures"], py_structures):
        for field in ("stake", "gross", "market_implied", "expected_loss", "variance"):
            if abs(js_row[field] - py_row[field]) > max(TOLERANCE, abs(py_row[field]) * 1e-9):
                mismatches.append(f"structures {js_row['odds']}: {field} "
                                  f"js={js_row[field]} py={py_row[field]}")

    print(f"node {node_version.stdout.strip()}: compared {len(fixtures)} fixtures "
          f"and {len(py_structures)} structures")
    if mismatches:
        print(f"MISMATCHES ({len(mismatches)}):")
        for line in mismatches[:12]:
            print(f"  {line}")
        return 1
    print("engines agree")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
