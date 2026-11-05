"""Tests that the demo server actually serves a working product.

The earlier lesson in this repository is that a claim of "it works" needs to be produced by something
that can fail. These tests start the real server on an ephemeral port and talk to it over HTTP.
"""

from __future__ import annotations

import json
import sys
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import engine, server  # noqa: E402


class ServerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        server.FIXTURES = engine.load_fixtures(limit=120)
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        cls.port = cls.httpd.server_address[1]
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def get(self, path):
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}{path}", timeout=10) as r:
            return r.status, r.read().decode("utf-8"), r.headers.get("Content-Type", "")

    def post(self, path, payload):
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            f"http://127.0.0.1:{self.port}{path}", data=data,
            headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(request, timeout=10) as r:
            return r.status, json.loads(r.read().decode("utf-8"))

    def test_index_serves_html(self):
        status, body, ctype = self.get("/")
        self.assertEqual(status, 200)
        self.assertIn("text/html", ctype)
        self.assertIn("market companion", body.lower())

    def test_health_reports_the_corpus(self):
        status, body, _ = self.get("/api/health")
        self.assertEqual(status, 200)
        payload = json.loads(body)
        self.assertTrue(payload["ok"])
        self.assertGreater(payload["fixtures"], 0)

    def test_fixtures_endpoint(self):
        status, body, _ = self.get("/api/fixtures?limit=5")
        payload = json.loads(body)
        self.assertEqual(len(payload["fixtures"]), 5)
        self.assertEqual(status, 200)

    def test_assess_endpoint_returns_claims(self):
        _, body, _ = self.get("/api/fixtures?limit=1")
        key = json.loads(body)["fixtures"][0]["key"]
        status, raw, _ = self.get(f"/api/assess?key={urllib.parse.quote(key)}&outcome=H")
        payload = json.loads(raw)
        self.assertEqual(status, 200)
        self.assertIn("claims", payload)
        self.assertGreater(payload["best_recorded_price"], 1.0)

    def test_unknown_fixture_is_an_error_not_a_crash(self):
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            self.get("/api/assess?key=nope&outcome=H")
        self.assertEqual(ctx.exception.code, 400)

    def test_slip_endpoint(self):
        _, body, _ = self.get("/api/fixtures?limit=2")
        fixtures = json.loads(body)["fixtures"]
        status, payload = self.post("/api/slip", {
            "stake": 100,
            "legs": [{"fixture_key": fixtures[0]["key"], "outcome": "H"},
                     {"fixture_key": fixtures[1]["key"], "outcome": "A"}],
        })
        self.assertEqual(status, 200)
        self.assertIn("joint_probability", payload)
        self.assertIn("gross_return", payload)

    def test_slip_rejects_empty(self):
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            self.post("/api/slip", {"stake": 100, "legs": []})
        self.assertEqual(ctx.exception.code, 400)

    def test_target_endpoint(self):
        status, body, _ = self.get("/api/target?stake=100&target=8&tolerance=0.25")
        payload = json.loads(body)
        self.assertEqual(status, 200)
        self.assertIn("verdict", payload)
        self.assertIn("matches", payload)

    def test_jackpot_endpoint(self):
        status, body, _ = self.get("/api/jackpot?entrants=1000&stake=100&takeout=0.3&lines=1")
        payload = json.loads(body)
        self.assertEqual(status, 200)
        self.assertAlmostEqual(payload["pool"], 70000.0, places=2)

    def test_path_traversal_is_refused(self):
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            self.get("/static/../server.py")
        self.assertIn(ctx.exception.code, (403, 404))


if __name__ == "__main__":
    unittest.main()
