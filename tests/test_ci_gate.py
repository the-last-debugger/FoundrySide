"""Tests for the CI resource gate.

The point of these is that the policy is *enforced by tests*, not merely described: a pause switch
that does not pause, or a daily limit that does not limit, would be worse than none.
"""

from __future__ import annotations

import datetime as dt
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import ci_gate  # noqa: E402

TODAY = dt.date(2026, 11, 4)


def policy(**over) -> dict:
    base = {"paused": False, "max_minutes_per_run": 15, "max_runs_per_day": 5}
    base.update(over)
    return base


def entries(n: int, day: dt.date = TODAY) -> list[dict]:
    return [{"date": day.isoformat(), "at": f"{day}T00:0{i}:00Z", "note": "x", "minutes": 1}
            for i in range(n)]


class GateTest(unittest.TestCase):
    def test_proceeds_when_not_paused(self):
        code, message = ci_gate.decide(policy(), entries(2), TODAY)
        self.assertEqual(code, 0)
        self.assertIn("proceeding", message)

    def test_pause_is_reported_as_a_decision_code(self):
        # The policy reports a pause; whether it blocks is the caller's choice, and the workflow
        # calls with --advisory so essential checks still run.
        code, message = ci_gate.decide(policy(paused=True), entries(0), TODAY)
        self.assertEqual(code, 2)
        self.assertIn("paused", message)

    def test_daily_limit_is_advisory_not_enforced(self):
        # The ledger lives in a read-only checkout and cannot persist, so a limit counted from it
        # would be a claim the mechanism cannot support. It reports and proceeds.
        code, message = ci_gate.decide(policy(max_runs_per_day=3), entries(10), TODAY)
        self.assertEqual(code, 0)
        self.assertIn("advisory", message)

    def test_yesterdays_runs_do_not_count_towards_today(self):
        old = entries(10, TODAY - dt.timedelta(days=1))
        code, _ = ci_gate.decide(policy(max_runs_per_day=5), old, TODAY)
        self.assertEqual(code, 0)

    def test_a_minute_ceiling_above_the_job_timeout_is_a_configuration_error(self):
        code, message = ci_gate.decide(policy(max_minutes_per_run=60), entries(0), TODAY,
                                       job_timeout_minutes=15)
        self.assertEqual(code, 1)
        self.assertIn("job timeout", message)

    def test_policy_file_is_parseable_and_complete(self):
        p = ci_gate.load_policy()
        for key in ("paused", "max_minutes_per_run", "max_runs_per_day"):
            self.assertIn(key, p)

    def test_ledger_round_trips(self):
        import tempfile
        path = Path(tempfile.mkdtemp()) / "runs.jsonl"
        ci_gate.record("test run", 1.5, path=path)
        rows = ci_gate.read_ledger(path)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["note"], "test run")
        self.assertIn("date", rows[0])


class WorkflowPolicyTest(unittest.TestCase):
    def test_workflow_declares_concurrency(self):
        text = (ROOT / ".github" / "workflows" / "checks.yml").read_text(encoding="utf-8")
        self.assertIn("concurrency:", text)
        self.assertIn("cancel-in-progress: true", text)

    def test_workflow_runs_the_gate_in_advisory_mode(self):
        text = (ROOT / ".github" / "workflows" / "checks.yml").read_text(encoding="utf-8")
        self.assertIn("scripts/ci_gate.py --advisory", text)

    def test_pause_cannot_suppress_essential_checks(self):
        # Every substantive step must be unconditional: the pause switch has no discretionary work
        # to gate, and must not be able to skip the suite or the bridge check.
        text = (ROOT / ".github" / "workflows" / "checks.yml").read_text(encoding="utf-8")
        for step in ("Test suite", "Bridge consistency", "Verification transcript"):
            line = [l for l in text.splitlines() if step in l][0]
            index = text.splitlines().index(line)
            following = text.splitlines()[index + 1]
            self.assertFalse(following.strip().startswith("if:"),
                             f"{step} must run unconditionally, found: {following.strip()}")

    def test_ledger_is_not_committed_as_live_state(self):
        # A runner cannot write back to a read-only checkout, so the file must not be presented as
        # persistent state.
        ledger = ROOT / "docs" / "ci" / "runs.jsonl"
        self.assertFalse(ledger.exists(),
                         "runs.jsonl should not be committed: it is runner-local and ephemeral")

    def test_job_timeout_does_not_exceed_the_policy(self):
        text = (ROOT / ".github" / "workflows" / "checks.yml").read_text(encoding="utf-8")
        policy_doc = json.loads((ROOT / ".github" / "ci-policy.json").read_text(encoding="utf-8"))
        self.assertIn("timeout-minutes: %d" % policy_doc["max_minutes_per_run"], text)


if __name__ == "__main__":
    unittest.main()
