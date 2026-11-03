"""Build the pilot's analysis frame: one row per fixture, with its cutoff and cluster.

This is pilot preparation, not scoring. It puts the pieces together that the protocol
requires to exist before any engine is fitted, and — after review — it **fails closed**:
a frame that cannot account for every source row, or that contains an unassigned fixture
or a mis-computed cutoff, is an error rather than a printed count.

    python research/pilot.py
    python research/pilot.py --expect-total 14735 --expect-pilot 8941 --expect-confirmatory 5794

Writes research/PILOT_FRAME.md and exits non-zero if any check fails.
"""

from __future__ import annotations

import statistics
import sys
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research"))

import analyse          # noqa: E402
import fixture_time     # noqa: E402

OUT = ROOT / "research" / "PILOT_FRAME.md"

PILOT_SEASONS = ("2021", "2122", "2223")
CONFIRMATORY_SEASONS = ("2324", "2425")

CATEGORIES = ("missing_ou_price", "invalid_ou_price", "clock", "result", "other")


def frame(rows: list[dict]) -> tuple[list[dict], dict[str, list[str]]]:
    """Join clock, cutoff, cluster and market probability; classify every reject."""
    out: list[dict] = []
    rejects: dict[str, list[str]] = {c: [] for c in CATEGORIES}
    for r in rows:
        league, season = r["_league"], r["_season"]
        where = f"{league} {season} {r.get('Date')} {r.get('Time')}"
        try:
            kick = fixture_time.kickoff_utc(r["Date"], r["Time"], league)
            cutoff = fixture_time.cutoff_utc(r["Date"], r["Time"], league)
        except fixture_time.ClockError as exc:
            rejects["clock"].append(f"{where}: {exc}")
            continue
        except (KeyError, ValueError, TypeError) as exc:
            rejects["other"].append(f"{where}: {exc}")
            continue
        try:
            hg, ag = int(r["FTHG"]), int(r["FTAG"])
        except (KeyError, TypeError, ValueError):
            rejects["result"].append(f"{where}: no usable full-time score")
            continue
        try:
            o_over, o_under = float(r["PC>2.5"]), float(r["PC<2.5"])
        except (KeyError, TypeError, ValueError):
            rejects["missing_ou_price"].append(f"{where}: no complete O/U 2.5 price")
            continue
        # Present but unusable is a different thing from absent, and only the first is
        # expected at this stage. Grouping them would let a corrupt price hide inside an
        # "expected exclusion" count.
        if o_over <= 1.0 or o_under <= 1.0:
            rejects["invalid_ou_price"].append(
                f"{where}: price <= 1.0 ({o_over}, {o_under})")
            continue
        raw_over, raw_under = 1 / o_over, 1 / o_under
        out.append({
            "league": league,
            "season": season,
            "cluster": f"{league}_{season}",
            "kickoff_utc": kick,
            "cutoff_utc": cutoff,
            "p_market": raw_over / (raw_over + raw_under),
            "y": 1 if hg + ag >= 3 else 0,
            "phase": ("pilot" if season in PILOT_SEASONS else
                      "confirmatory" if season in CONFIRMATORY_SEASONS else "unassigned"),
        })
    return out, rejects


def summarise(framed: list[dict]) -> str:
    lines = ["| Phase | Fixtures | Clusters | Median per cluster | Min | Max | Window |",
             "| --- | --- | --- | --- | --- | --- | --- |"]
    for phase in ("pilot", "confirmatory"):
        subset = [f for f in framed if f["phase"] == phase]
        if not subset:
            lines.append(f"| {phase} | 0 | 0 | – | – | – | – |")
            continue
        sizes: dict[str, int] = {}
        for f in subset:
            sizes[f["cluster"]] = sizes.get(f["cluster"], 0) + 1
        counts = sorted(sizes.values())
        first = min(f["kickoff_utc"] for f in subset)
        last = max(f["kickoff_utc"] for f in subset)
        lines.append(f"| {phase} | {len(subset):,} | {len(sizes)} | "
                     f"{statistics.median(counts):.0f} | {counts[0]} | {counts[-1]} | "
                     f"{first:%Y-%m-%d} – {last:%Y-%m-%d} |")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]

    def flag(name: str) -> int | None:
        return int(args[args.index(name) + 1]) if name in args else None

    expect_total, expect_pilot = flag("--expect-total"), flag("--expect-pilot")
    expect_confirm = flag("--expect-confirmatory")
    exclude_invalid = "--exclude-invalid" in args

    rows = analyse.load()
    framed, rejects = frame(rows)
    rejected = sum(len(v) for v in rejects.values())

    bad_cutoff = [f for f in framed
                  if not (f["cutoff_utc"] < f["kickoff_utc"] ==
                          f["cutoff_utc"] + timedelta(minutes=90))]
    unassigned = [f for f in framed if f["phase"] == "unassigned"]
    pilot_n = sum(1 for f in framed if f["phase"] == "pilot")
    confirm_n = sum(1 for f in framed if f["phase"] == "confirmatory")

    failures: list[str] = []
    if len(framed) + rejected != len(rows):
        failures.append(f"accounting does not reconcile: {len(framed)} framed + "
                        f"{rejected} rejected != {len(rows)} source rows")
    for cat in ("clock", "result", "other"):
        if rejects[cat]:
            failures.append(f"{cat}: {len(rejects[cat])} row(s) — a frame cannot be built "
                            f"over broken inputs")
    if rejects["invalid_ou_price"] and not exclude_invalid:
        failures.append(f"invalid_ou_price: {len(rejects['invalid_ou_price'])} row(s) with a "
                        f"present but unusable price — rerun with --exclude-invalid to drop "
                        f"them explicitly, or investigate")
    if bad_cutoff:
        failures.append(f"{len(bad_cutoff)} cutoff(s) are not exactly T-90")
    if unassigned:
        failures.append(f"{len(unassigned)} fixture(s) in an unassigned season")
    if expect_total is not None and len(rows) != expect_total:
        failures.append(f"expected {expect_total} source rows, found {len(rows)}")
    if expect_pilot is not None and pilot_n != expect_pilot:
        failures.append(f"expected {expect_pilot} pilot fixtures, found {pilot_n}")
    if expect_confirm is not None and confirm_n != expect_confirm:
        failures.append(f"expected {expect_confirm} confirmatory fixtures, found {confirm_n}")

    checks = [
        ("every source row accounted for", len(framed) + rejected == len(rows)),
        ("no clock or result defects", not any(rejects[c] for c in ("clock", "result", "other"))),
        ("invalid prices absent or explicitly waived",
         not rejects["invalid_ou_price"] or exclude_invalid),
        ("every cutoff is exactly T-90", not bad_cutoff),
        ("every fixture in an assigned phase", not unassigned),
    ]

    doc = f"""# Pilot frame

Generated by `python research/pilot.py`. This builds the frame the pilot needs; it fits
no model and scores nothing.

{summarise(framed)}

| Check | Result |
| --- | --- |
""" + "\n".join(f"| {name} | {'PASS' if ok else '**FAIL**'} |" for name, ok in checks) + f"""

## Exclusions, by category

| Category | Count |
| --- | --- |
""" + "\n".join(f"| {c} | {len(rejects[c])} |" for c in CATEGORIES) + f"""
| **total** | **{rejected}** |

The expected exclusion is `missing_ou_price`: fixtures that exist but have no complete
over/under 2.5 closing price. `invalid_ou_price` is a different thing — a price is
**present** and unusable — and it is fatal unless `--exclude-invalid` is passed, in which
case the decision is recorded here rather than made silently. Clock, result and other
failures are always fatal, so no count above can hide a broken row in an expected bucket.
""" + (f"""
`--exclude-invalid` was passed: **{len(rejects['invalid_ou_price'])} row(s)** with present
but unusable prices were dropped by explicit decision, not by rule.
""" if exclude_invalid and rejects["invalid_ou_price"] else "") + f"""

## What this establishes

The clock, cutoff and cluster columns exist for every scored row, the cutoff is exactly
T−90 by construction, and the accounting closes. That is the mechanical part of the
point-in-time rule; the substantive part — that no *input* to a prediction is later than
the cutoff — is enforced when an engine is fitted, by recording the maximum input
timestamp per prediction.

## What it does not establish

- No engine has been fitted, so there is no Δ distribution and no measured power.
- `σ²_w` and `σ²_b` remain unmeasured; `research/cluster_power.py` shows how they become
  a power figure once the pilot produces them.
- The market probability is de-vigged proportionally; no timestamp for it exists, as the
  protocol records.
"""
    OUT.write_text(doc, encoding="utf-8")

    print(f"source rows={len(rows)} framed={len(framed):,} rejected={rejected}")
    for c in CATEGORIES:
        print(f"  {c:16} {len(rejects[c])}")
    for name, ok in checks:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    for f in failures:
        print(f"FAILURE: {f}")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0 if not failures else 1


if __name__ == "__main__":
    import sys as _sys
    raise SystemExit(main(_sys.argv[1:]))
