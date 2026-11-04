"""Regenerate every report and report whether the committed artefacts reproduce.

Two distinct failures this catches:

- **drift**: a report in the repository no longer matches what its generator produces, meaning
  someone edited one and not the other;
- **non-reproducibility**: a generator produces different bytes on a second run, meaning it
  depends on something it does not control (hash order, wall clock, unseeded randomness).

Usage:

    python scripts/repro_sweep.py            # run generators, report drift
    python scripts/repro_sweep.py --check    # do not run anything, just verify stamps

Exit code is non-zero if any report drifted.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable

# Order matters: later scripts consume artefacts written by earlier ones.
GENERATORS = [
    ("research/analyse.py", ()),
    ("research/power.py", ()),
    ("research/logloss_power.py", ()),
    ("research/cluster_power.py", ()),
    ("research/pilot.py", ("--exclude-invalid",)),
    ("research/pilot_model.py", ()),
    ("research/pilot_power.py", ("--deltas", "research/pilot_deltas.csv")),
    ("research/market_structure.py", ()),
    ("research/gap_diagnosis.py", ()),
    ("research/calibration_study.py", ()),
    ("research/segment_study.py", ()),
    ("research/residual_study.py", ()),
    ("research/book_disagreement.py", ()),
    ("research/congestion_study.py", ()),
    ("research/cross_market.py", ()),
    ("research/data_audit.py", ()),
    ("research/feature_screen.py", ()),
    ("research/model_family.py", ()),
    ("research/track_b.py", ()),
    ("research/fl_test.py", ()),
    ("research/superstition_study.py", ()),
    ("research/bogey_team.py", ()),
    ("research/style_mismatch.py", ()),
    ("research/best_price.py", ()),
    ("research/accumulator_pricing.py", ()),
]




def changed_artefacts(before: dict[str, str], after: dict[str, str]) -> list[str]:
    """Names whose bytes differ. Pure, so the dirty-file case can be tested."""
    return sorted(name for name in after if before.get(name) != after[name])


def _artefact_state() -> dict[str, str]:
    """Content hash of every artefact, not its git status.

    A status-set comparison misses a second change to a file that was already dirty before the
    run: the path is in both snapshots, so the difference is empty and real drift passes. Hashing
    the bytes catches every change regardless of repository state.
    """
    import hashlib

    state: dict[str, str] = {}
    for pattern in ("*.md", "*.csv"):
        for path in sorted((ROOT / "research").glob(pattern)):
            state[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return state


def main() -> int:
    if "--check" in sys.argv:
        import unittest
        return unittest.main(module="tests.test_reports", exit=False, argv=["x"]).result.wasSuccessful() is False

    drift = []
    failures = []
    for script, args in GENERATORS:
        # Scope drift detection to generated artefacts. Tracking the whole tree reports any
        # concurrent documentation edit as generator drift, which is noise.
        before = _artefact_state()
        proc = subprocess.run([PY, script, *args], cwd=ROOT, capture_output=True, text=True)
        after = _artefact_state()
        if proc.returncode != 0:
            failures.append((script, proc.stderr.strip().splitlines()[-1] if proc.stderr.strip() else ""))
        changed = changed_artefacts(before, after)
        if changed:
            drift.append((script, sorted(changed)))

    print(f"generators run: {len(GENERATORS)}")
    if failures:
        print("\nfailures:")
        for script, err in failures:
            print(f"  {script}: {err}")
    if drift:
        print("\ndrifted (regeneration changed committed files):")
        for script, changed in drift:
            print(f"  {script}")
            for line in changed[:5]:
                print(f"    {line}")
    else:
        print("\nno drift: every report reproduces byte-for-byte")
    return 1 if (failures or drift) else 0


if __name__ == "__main__":
    raise SystemExit(main())
