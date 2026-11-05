"""Tests for the JavaScript/Python parity check.

The Android app carries a JavaScript port of the engine. A port drifts, and the documentation said so
without doing anything about it. The check compares the two on shared fixtures; these tests make sure
the check itself cannot pass vacuously.
"""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_js_parity  # noqa: E402


class ParityCheckTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.has_node = subprocess.run(["node", "--version"], capture_output=True).returncode == 0

    def test_javascript_exports_the_engine_surface(self):
        if not self.has_node:
            self.skipTest("node not installed")
        proc = subprocess.run(
            ["node", "-e",
             "const fs=require('fs');"
             f"eval(fs.readFileSync({str(check_js_parity.APP_JS)!r},'utf8'));"
             "process.stdout.write(Object.keys(globalThis.__fs).sort().join(','));"],
            capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        for name in ("assess", "compareStructures", "devig", "overround", "slip"):
            self.assertIn(name, proc.stdout, name)

    def test_javascript_does_not_touch_the_dom_on_load(self):
        if not self.has_node:
            self.skipTest("node not installed")
        # Loading outside a browser must not throw: the parity check relies on it.
        proc = subprocess.run(
            ["node", "-e",
             "const fs=require('fs');"
             f"eval(fs.readFileSync({str(check_js_parity.APP_JS)!r},'utf8'));"
             "process.stdout.write('ok');"],
            capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout, "ok")

    def test_engines_agree_on_the_held_corpus(self):
        if not self.has_node:
            self.skipTest("node not installed")
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "check_js_parity.py"), "--limit", "8"],
            cwd=ROOT, capture_output=True, text=True)
        if "no fixtures available" in result.stdout:
            self.skipTest("corpus not present")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("engines agree", result.stdout)


if __name__ == "__main__":
    unittest.main()
