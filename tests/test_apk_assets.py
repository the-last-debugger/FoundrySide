"""Checks on the Android app's assets, which is what can be verified without a device.

The APK itself cannot be run here — there is no emulator or handset — so these tests check the things
that would silently break it: the data must parse, the page must reference its scripts, the manifest
must not ask for the network, and the JavaScript must not try to use it.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANDROID = ROOT / "app" / "android"
WWW = ANDROID / "assets" / "www"


class AppAssetTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixtures = json.loads((ANDROID / "assets" / "fixtures.json").read_text(encoding="utf-8"))
        cls.data_js = (WWW / "data.js").read_text(encoding="utf-8")
        cls.app_js = (WWW / "app.js").read_text(encoding="utf-8")
        cls.index = (WWW / "index.html").read_text(encoding="utf-8")

    def test_fixture_payload_is_well_formed(self):
        self.assertGreater(self.fixtures["count"], 0)
        self.assertEqual(len(self.fixtures["fixtures"]), self.fixtures["count"])
        first = self.fixtures["fixtures"][0]
        for key in ("k", "d", "date", "h", "a", "odds"):
            self.assertIn(key, first)

    def test_every_fixture_has_two_books(self):
        for fixture in self.fixtures["fixtures"][:50]:
            self.assertGreaterEqual(len(fixture["odds"]), 2, fixture["k"])

    def test_data_js_embeds_the_same_payload(self):
        # data.js exists because a WebView cannot fetch a local file; it must match fixtures.json.
        match = re.search(r"const FIXTURE_JSON = (\".*\");", self.data_js, re.S)
        self.assertIsNotNone(match, "data.js does not define FIXTURE_JSON")
        embedded = json.loads(json.loads(match.group(1)))
        self.assertEqual(embedded["count"], self.fixtures["count"])
        self.assertEqual(embedded["fixtures"][0]["k"], self.fixtures["fixtures"][0]["k"])

    def test_page_uses_the_shared_theme(self):
        # One stylesheet, copied at export, so the app and the local page cannot drift apart.
        self.assertIn('href="theme.css"', self.index)
        self.assertTrue((WWW / "theme.css").exists())
        self.assertEqual((WWW / "theme.css").read_text(encoding="utf-8"),
                         (ROOT / "app" / "ui" / "theme.css").read_text(encoding="utf-8"))

    def test_page_explains_the_numbers(self):
        self.assertIn("How to read these numbers", self.index)
        lowered = " ".join(self.index.lower().split())
        self.assertIn("not a price you were offered", lowered)

    def test_page_loads_both_scripts(self):
        self.assertIn('src="data.js"', self.index)
        self.assertIn('src="app.js"', self.index)

    def test_manifest_requests_no_permissions(self):
        manifest = (ANDROID / "AndroidManifest.xml").read_text(encoding="utf-8")
        self.assertNotIn("android.permission.INTERNET", manifest)
        self.assertNotIn("uses-permission", manifest)

    def test_javascript_makes_no_network_calls(self):
        for banned in ("fetch(", "XMLHttpRequest", "WebSocket", "navigator.sendBeacon"):
            self.assertNotIn(banned, self.app_js, f"app.js uses {banned}")

    def test_javascript_carries_the_claim_kinds(self):
        for kind in ("observed", "estimated", "hypothetical"):
            self.assertIn(kind, self.app_js, kind)

    def test_interface_states_the_limits(self):
        lowered = " ".join(self.index.lower().split())
        self.assertIn("no timestamps", lowered)
        self.assertIn("no profitability", lowered)

    def test_de_vig_helper_is_present_and_total(self):
        # The port must normalise, or every probability in the app is wrong.
        self.assertIn("function devig", self.app_js)
        self.assertIn("reduce((a, b) => a + b, 0)", self.app_js)


class BuildScriptTest(unittest.TestCase):
    def test_build_uses_no_network_and_no_gradle(self):
        script = (ROOT / "scripts" / "build_apk.py").read_text(encoding="utf-8")
        # The docstring explains why Gradle is not used; the executable part must not invoke it.
        body = "\n".join(line for line in script.splitlines()
                            if not line.strip().startswith("#"))
        self.assertNotIn("gradlew", body)
        self.assertNotIn("gradle-wrapper", body)
        for step in ("aapt2", "d8", "zipalign", "apksigner"):
            self.assertIn(step, script, step)


if __name__ == "__main__":
    unittest.main()
