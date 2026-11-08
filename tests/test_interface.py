"""Structural checks on the interface, as a substitute for a screenshot.

There is no browser in this environment, so the page cannot be rendered and compared. What can be
checked is the class of defect that actually breaks it: duplicate element ids, a tab with no view, a
view with no tab, a script or stylesheet that does not exist, and a handler that targets an element the
markup never defines.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UI = ROOT / "app" / "ui" / "index.html"
ASSETS = ROOT / "app" / "ui"


class InterfaceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = UI.read_text(encoding="utf-8")

    def ids(self) -> list[str]:
        return re.findall(r'\bid="([^"]+)"', self.page)

    def test_no_duplicate_element_ids(self):
        ids = self.ids()
        duplicates = {i for i in ids if ids.count(i) > 1}
        self.assertFalse(duplicates, f"duplicate ids break the handlers: {duplicates}")

    def test_every_tab_has_a_view(self):
        tabs = re.findall(r'data-view="([^"]+)"', self.page)
        self.assertTrue(tabs, "no tabs found")
        for tab in tabs:
            self.assertIn(f'id="view-{tab}"', self.page, f"tab {tab} has no panel")

    def test_every_view_has_a_tab(self):
        views = set(re.findall(r'id="view-([^"]+)"', self.page))
        tabs = set(re.findall(r'data-view="([^"]+)"', self.page))
        self.assertEqual(views, tabs, "a panel exists that no tab can reach")

    def test_referenced_local_assets_exist(self):
        for src in re.findall(r'(?:src|href)="(/static/[^"]+)"', self.page):
            path = ASSETS / src.replace("/static/", "")
            self.assertTrue(path.exists(), f"missing asset {src}")

    def test_handlers_target_elements_that_exist(self):
        ids = set(self.ids())
        # $("x").onclick / addEventListener patterns in the inline script.
        for target in set(re.findall(r'\$\("([a-zA-Z0-9_-]+)"\)\.onclick', self.page)):
            self.assertIn(target, ids, f"handler bound to missing id {target}")

    def test_the_page_states_its_limits(self):
        lowered = " ".join(self.page.lower().split())
        self.assertIn("no timestamps", lowered)
        self.assertIn("not a forecast", lowered)

    def test_every_plan_path_is_reachable_from_the_interface(self):
        # The planner and the typed card are the user-facing answer to "stake X, make Y".
        self.assertIn("/api/plan", self.page)
        self.assertIn("Target multiplier", self.page)
        # The typed-card path is the only prospective one; the page must at least point at it.
        self.assertIn("plan_card.py", self.page)
        # And the browser must be able to plan a card itself, not only point at the CLI.
        self.assertIn("card-input", self.page)
        self.assertIn("card-go", self.page)


    def test_card_editor_plans_a_card_in_a_stubbed_dom(self):
        # Structural checks cannot tell whether the editor works; this runs it under Node.
        import shutil, subprocess
        if not shutil.which("node"):
            self.skipTest("node not installed")
        script = ROOT / "tests" / "fixtures" / "card_editor_check.js"
        result = subprocess.run(["node", str(script)], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("plans correctly", result.stdout)


if __name__ == "__main__":
    unittest.main()
