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

    def test_binned_brier_differs_from_raw_when_forecasts_vary_within_a_bin(self):
        # All forecasts land in the same bin but differ from each other: the binned
        # identity reconstructs the coarsened forecast, not the raw one.
        data = []
        for i in range(100):
            p_i = 0.31 + 0.07 * (i % 5) / 4      # 0.31 … 0.38, all in bin 3
            y = 1 if i % 3 == 0 else 0
            data.append({"division": "E0", "cluster": "E0_1", "p_model": p_i,
                         "p_market": 0.5, "y": y, "delta": 0.0})
        parts = gap_diagnosis.decompose(data, "p_model")
        self.assertAlmostEqual(parts["brier"], parts["reliability"] - parts["resolution"]
                               + parts["uncertainty"], places=12)
        self.assertGreater(parts["within_bin"], 0.0)
        self.assertAlmostEqual(parts["brier_raw"], parts["brier"] + parts["within_bin"],
                               places=12)

    def test_perfect_forecasts_have_no_reliability_cost(self):
        data = [{"division": "E0", "cluster": "E0_1", "p_model": float(y),
                 "p_market": 0.5, "y": y, "delta": 0.0} for y in (0, 1) * 50]
        parts = gap_diagnosis.decompose(data, "p_model")
        self.assertAlmostEqual(parts["reliability"], 0.0, places=12)


if __name__ == "__main__":
    unittest.main()
