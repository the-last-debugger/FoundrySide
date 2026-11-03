"""The Brier decomposition must be an identity, not an approximation."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research import gap_diagnosis  # noqa: E402


def rows() -> list[dict]:
    out = []
    for i in range(200):
        p = 0.3 + 0.4 * (i % 5) / 4
        y = 1 if (i % 7) < (p * 7) else 0
        out.append({"division": "E0", "cluster": f"E0_{i % 3}", "p_model": p,
                    "p_market": 0.5, "y": y, "delta": 0.0})
    return out


class DecompositionTest(unittest.TestCase):
    def test_components_reconstruct_the_brier_score(self):
        data = rows()
        parts = gap_diagnosis.decompose(data, "p_model")
        actual = gap_diagnosis.brier(data, "p_model")
        self.assertAlmostEqual(parts["brier"], actual, places=10)

    def test_uncertainty_depends_only_on_the_outcome(self):
        data = rows()
        a = gap_diagnosis.decompose(data, "p_model")["uncertainty"]
        b = gap_diagnosis.decompose(data, "p_market")["uncertainty"]
        self.assertAlmostEqual(a, b, places=12)

    def test_perfect_forecasts_have_no_reliability_cost(self):
        data = [{"division": "E0", "cluster": "E0_1", "p_model": float(y),
                 "p_market": 0.5, "y": y, "delta": 0.0} for y in (0, 1) * 50]
        parts = gap_diagnosis.decompose(data, "p_model")
        self.assertAlmostEqual(parts["reliability"], 0.0, places=12)


if __name__ == "__main__":
    unittest.main()
