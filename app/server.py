"""Local demo server for FoundrySide. Stdlib only, binds to localhost.

    python -m app.server            # http://127.0.0.1:8765
    python -m app.server --port 9000

No network access, no accounts, no data acquisition. It serves the held corpus through the shared
assessment engine and a small single-page interface.
"""

from __future__ import annotations

import argparse
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from app import engine, journal

UI = Path(__file__).resolve().parent / "ui"
FIXTURES: list[engine.Fixture] = []
MODE = "held"


def json_response(handler, payload, status=HTTPStatus.OK):
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def error(handler, message, status=HTTPStatus.BAD_REQUEST):
    json_response(handler, {"error": message}, status)


class Handler(BaseHTTPRequestHandler):
    server_version = "FoundrySide/0.1"

    def log_message(self, fmt, *args):  # keep the console readable
        return

    def do_GET(self):
        parsed = urlparse(self.path)
        path, query = parsed.path, parse_qs(parsed.query)

        if path in ("/", "/index.html"):
            return self._static("index.html", "text/html; charset=utf-8")
        if path.startswith("/static/"):
            name = path[len("/static/"):]
            ctype = {"js": "application/javascript; charset=utf-8",
                     "css": "text/css; charset=utf-8"}.get(name.rsplit(".", 1)[-1], "text/plain")
            return self._static(name, ctype)

        if path == "/api/health":
            return json_response(self, {"ok": True, "mode": MODE, "fixtures": len(FIXTURES),
                                        "divisions": sorted({f.div for f in FIXTURES})})

        if path == "/api/fixtures":
            div = (query.get("div") or [""])[0]
            limit = int((query.get("limit") or ["30"])[0])
            rows = [f for f in FIXTURES if not div or f.div == div][:limit]
            return json_response(self, {"fixtures": [
                {"key": f.key, "label": f.label, "division": f.div, "date": f.date,
                 "score": f.score} for f in rows]})

        if path == "/api/assess":
            key = (query.get("key") or [""])[0]
            outcome = (query.get("outcome") or ["H"])[0].upper()
            fx = next((f for f in FIXTURES if f.key == key), None)
            if fx is None:
                return error(self, "unknown fixture key")
            try:
                return json_response(self, engine.assess_selection(fx, outcome))
            except ValueError as exc:
                return error(self, str(exc))

        if path == "/api/journal":
            return json_response(self, {"entries": journal.load()})

        if path == "/api/journal/review":
            by_key = {f.key: f for f in FIXTURES}
            return json_response(self, journal.review(by_key))

        if path == "/api/structures":
            try:
                target = float((query.get("target") or ["200"])[0])
                raw = (query.get("odds") or ["1.5,2,3,4,6"])[0]
                levels = [float(x) for x in raw.split(",") if x.strip()]
                margin = float((query.get("margin") or ["0.05"])[0])
                return json_response(self, engine.compare_structures(target, levels, margin))
            except ValueError as exc:
                return error(self, f"target, odds and margin must be numbers: {exc}")

        if path == "/api/explanations":
            return json_response(self, {"explanations": engine.explanations()})

        if path == "/api/export":
            key = (query.get("key") or [""])[0]
            outcome = (query.get("outcome") or ["H"])[0].upper()
            fmt = (query.get("format") or ["json"])[0]
            fx = next((f for f in FIXTURES if f.key == key), None)
            if fx is None:
                return error(self, "unknown fixture key")
            try:
                card = engine.assessment_card(engine.assess_selection(fx, outcome))
            except ValueError as exc:
                return error(self, str(exc))
            if fmt == "text":
                body = engine.render_card(card).encode("utf-8")
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Content-Disposition", 'attachment; filename="assessment.txt"')
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            return json_response(self, card)

        if path == "/api/market":
            key = (query.get("key") or [""])[0]
            fx = next((f for f in FIXTURES if f.key == key), None)
            if fx is None:
                return error(self, "unknown fixture key")
            return json_response(self, engine.market_view(fx))

        if path == "/api/target":
            try:
                stake = float((query.get("stake") or ["100"])[0])
                target = float((query.get("target") or ["10"])[0])
                tol = float((query.get("tolerance") or ["0.15"])[0])
            except ValueError:
                return error(self, "stake, target and tolerance must be numbers")
            try:
                return json_response(self, engine.target_search(stake, target, tol, fixtures=FIXTURES))
            except ValueError as exc:
                return error(self, str(exc))

        if path == "/api/jackpot":
            try:
                payload = engine.jackpot_view(
                    entrants=int((query.get("entrants") or ["1000"])[0]),
                    stake=float((query.get("stake") or ["100"])[0]),
                    takeout=float((query.get("takeout") or ["0.3"])[0]),
                    your_lines=int((query.get("lines") or ["1"])[0]),
                    matches=int((query.get("matches") or ["6"])[0]),
                )
            except ValueError as exc:
                return error(self, str(exc))
            return json_response(self, payload)

        return error(self, "not found", HTTPStatus.NOT_FOUND)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/journal":
            length = int(self.headers.get("Content-Length") or 0)
            try:
                payload = json.loads(self.rfile.read(length) or b"{}")
                key = payload.get("fixture_key")
                outcome = (payload.get("outcome") or "").upper()
                fx = next((f for f in FIXTURES if f.key == key), None)
                if fx is None:
                    raise ValueError("unknown fixture key")
                if outcome not in engine.OUTCOMES:
                    raise ValueError("outcome must be H, D or A")
                assessment = engine.assess_selection(fx, outcome)
                record = journal.save({
                    "fixture_key": fx.key,
                    "fixture": fx.label,
                    "division": fx.div,
                    "outcome": outcome,
                    "best_recorded_price": assessment["best_recorded_price"],
                    "best_book": assessment["best_book"],
                    "market_implied": assessment["market_implied"],
                    "price_implied": assessment["price_implied"],
                    "claims": assessment["claims"],
                })
                return json_response(self, {"saved": record})
            except (ValueError, json.JSONDecodeError) as exc:
                return error(self, str(exc))

        if parsed.path != "/api/slip":
            return error(self, "not found", HTTPStatus.NOT_FOUND)
        length = int(self.headers.get("Content-Length") or 0)
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
            stake = float(payload.get("stake", 100))
            legs = payload.get("legs", [])
            if not isinstance(legs, list) or not legs:
                raise ValueError("provide at least one leg")
            normalised = []
            for leg in legs:
                fx = next((f for f in FIXTURES if f.key == leg.get("fixture_key")), None)
                if fx is None:
                    raise ValueError(f"unknown fixture: {leg.get('fixture_key')}")
                outcome = (leg.get("outcome") or "H").upper()
                if outcome not in engine.OUTCOMES:
                    raise ValueError("outcome must be H, D or A")
                idx = engine.OUTCOMES.index(outcome)
                price = (fx.odds.get("Max") or list(fx.odds.values())[0])[idx]
                probs = engine.devig(fx.odds["Avg"]) if "Avg" in fx.odds else engine.devig(
                    list(fx.odds.values())[0])
                normalised.append({"fixture_key": fx.key, "label": f"{fx.label} ({outcome})",
                                   "outcome": outcome, "price": price, "prob": probs[idx]})
            return json_response(self, engine.slip_view(normalised, stake))
        except (ValueError, json.JSONDecodeError) as exc:
            return error(self, str(exc))

    def _static(self, name: str, ctype: str):
        candidate = (UI / name).resolve()
        if not str(candidate).startswith(str(UI.resolve())) or not candidate.is_file():
            return error(self, "not found", HTTPStatus.NOT_FOUND)
        body = candidate.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> int:
    parser = argparse.ArgumentParser(description="FoundrySide local demo")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--limit", type=int, default=0, help="cap fixtures loaded (0 = all)")
    parser.add_argument("--demo", action="store_true",
                        help="run on clearly-labelled synthetic fixtures")
    args = parser.parse_args()

    global FIXTURES, MODE
    if args.demo:
        from app import demo_data
        FIXTURES = demo_data.synthetic_fixtures(120)
        MODE = "synthetic"
    else:
        FIXTURES = engine.load_fixtures(limit=args.limit or None)
        MODE = "held"
    if not FIXTURES:
        print("No fixtures found under research/data.")
        print("The held corpus is not committed to this repository. Run with --demo for synthetic,")
        print("clearly labelled data, or place the held CSV files in research/data/.")
        return 1

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"FoundrySide demo: http://{args.host}:{args.port}  ({len(FIXTURES):,} fixtures, {MODE})")
    print("Ctrl+C to stop. Local only; no external requests.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
