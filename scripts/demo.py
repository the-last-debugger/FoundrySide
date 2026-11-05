"""End-to-end demonstration: start the product, exercise every view, print the transcript.

This is what to run when somebody asks "does it work?". It starts the real server on an ephemeral port,
calls every endpoint, and prints what came back with the claim kinds attached. Nothing is mocked except
the fixtures, which are labelled when synthetic.

    python scripts/demo.py                # held corpus if present, else synthetic
    python scripts/demo.py --demo         # force synthetic
    python scripts/demo.py --quiet        # exit code only

Exit code 0 means every view answered. The transcript is generated from the responses, not typed.
"""

from __future__ import annotations

import argparse
import json
import sys
import threading
import urllib.parse
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import demo_data, engine, server  # noqa: E402


def get(port: int, path: str) -> dict | str:
    with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=30) as response:
        body = response.read().decode("utf-8")
        if response.headers.get("Content-Type", "").startswith("application/json"):
            return json.loads(body)
        return body


def post(port: int, path: str, payload: dict) -> dict:
    request = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}", data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Exercise the product end to end")
    parser.add_argument("--demo", action="store_true", help="force synthetic fixtures")
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--limit", type=int, default=120)
    args = parser.parse_args()

    fixtures = None if args.demo else engine.load_fixtures(limit=args.limit)
    mode = "held"
    if not fixtures:
        fixtures = demo_data.synthetic_fixtures(args.limit)
        mode = "synthetic"

    # Keep the demonstration out of the real journal: a demo run should not look like user activity.
    import tempfile
    from app import journal
    journal.DEFAULT_PATH = Path(tempfile.mkdtemp()) / "demo-journal.jsonl"

    server.FIXTURES = fixtures
    server.MODE = mode
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()

    out = [] if args.quiet else [f"FoundrySide demo — {mode} data, {len(fixtures)} fixtures", "-" * 68]
    failures = 0

    def record(label: str, detail: str) -> None:
        out.append(f"{label:<22} {detail}")

    try:
        health = get(port, "/api/health")
        record("health", f"mode={health['mode']} fixtures={health['fixtures']} "
                         f"divs={','.join(health['divisions'][:4])}")

        first = get(port, "/api/fixtures?limit=2")["fixtures"]
        key = first[0]["key"]

        assessment = get(port, f"/api/assess?key={urllib.parse.quote(key)}&outcome=H")
        record("assess", f"{assessment['fixture'][:34]:<34} price={assessment['best_recorded_price']} "
                         f"market={assessment['market_implied']:.4f} "
                         f"caveats={len(assessment.get('caveats', []))}")

        market = get(port, f"/api/market?key={urllib.parse.quote(key)}")
        record("market", f"{len(market['quotes'])} books, "
                         f"spread H={market['best_vs_average']['H']*100:+.2f}%")

        structures = get(port, "/api/structures?target=200&odds=1.5,3,6")
        record("structures", ", ".join(f"{s['odds']}x→KSh{s['stake']:.0f}"
                                       for s in structures["structures"]))

        slip = post(port, "/api/slip", {"stake": 100, "legs": [{"fixture_key": key, "outcome": "H"}]})
        record("slip", f"price={slip['combined_odds']} gross=KSh{slip['gross_return']:.0f} "
                       f"net=KSh{slip['net_result']:.0f}")

        target = get(port, "/api/target?stake=100&target=8&tolerance=0.25")
        record("target", f"found={target['found']} matches={len(target['matches'])} "
                         f"scope={target['search_scope']['fixtures_used_for_pairs']}")

        jackpot = get(port, "/api/jackpot?entrants=1000&stake=100&takeout=0.3&lines=5")
        record("jackpot", f"pool=KSh{jackpot['pool']:.0f} coverage={jackpot['coverage']:.6f} "
                          f"winners={jackpot['expected_winning_tickets']}")

        explanations = get(port, "/api/explanations")
        record("explanations", f"{len(explanations['explanations'])} claims explained")

        card = get(port, f"/api/export?key={urllib.parse.quote(key)}&outcome=H&format=text")
        record("export", f"{len(card)} characters, limits_included={'Limits:' in card}")

        saved = post(port, "/api/journal", {"fixture_key": key, "outcome": "H"})
        review = get(port, "/api/journal/review")
        record("journal", f"saved={saved['saved']['fixture'][:22]} settled={review['settled']} "
                          f"pending={review['pending_result']}")

        page = get(port, "/")
        record("page", f"{len(page)} bytes, tabs={page.count('data-view=')}")
    except Exception as exc:
        failures += 1
        out.append(f"FAILED: {type(exc).__name__}: {exc}")
    finally:
        httpd.shutdown()
        httpd.server_close()

    if not args.quiet:
        out.append("-" * 68)
        out.append("every view answered" if not failures else f"{failures} failure(s)")
        print("\n".join(out))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
