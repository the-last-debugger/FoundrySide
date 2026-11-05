"""Assessment journal — what was said, when, and how it turned out.

The product's honesty rules govern the moment of generation. This module covers the part that is
usually skipped: keeping the record so the advice can be checked later.

A journal entry stores the assessment **as it was made** — the recorded quote, the claim kinds and the
caveats — and never rewrites it after the result is known. Settling joins entries to the held results
and reports how the market-implied probabilities performed. It says nothing about profit: a hit rate
is not an edge, and the valuation needs prices a user could obtain.

Storage is a local JSONL file. No database, no server, no external calls.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PATH = ROOT / "var" / "assessments.jsonl"


def save(entry: dict, path: Path | None = None) -> dict:
    """Append one assessment. The stored record is immutable once written."""
    target = path or DEFAULT_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    record = dict(entry)
    record.setdefault("recorded_utc", datetime.now(timezone.utc).isoformat(timespec="seconds"))
    with open(target, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
    return record


def load(path: Path | None = None) -> list[dict]:
    target = path or DEFAULT_PATH
    if not target.exists():
        return []
    entries = []
    with open(target, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return entries


def _outcome(score: tuple[int, int]) -> str:
    home, away = score
    if home > away:
        return "H"
    if home < away:
        return "A"
    return "D"


def review(fixtures_by_key: dict, path: Path | None = None) -> dict:
    """Settle every journalled assessment that has a known result.

    Reports accuracy and Brier against the recorded market probability, and states what that does and
    does not establish.
    """
    entries = load(path)
    settled = []
    pending = 0
    unresolved = 0

    for entry in entries:
        fixture = fixtures_by_key.get(entry.get("fixture_key", ""))
        if fixture is None:
            unresolved += 1
            continue
        if not fixture.score:
            pending += 1
            continue
        actual = _outcome(fixture.score)
        outcome = entry.get("outcome")
        probability = entry.get("market_implied")
        if outcome not in ("H", "D", "A") or not isinstance(probability, (int, float)):
            unresolved += 1
            continue
        settled.append({
            "fixture": entry.get("fixture"),
            "outcome": outcome,
            "actual": actual,
            "hit": outcome == actual,
            "market_implied": probability,
            "brier": round((probability - (1 if outcome == actual else 0)) ** 2, 6),
        })

    n = len(settled)
    hits = sum(1 for s in settled if s["hit"])
    return {
        "entries": len(entries),
        "settled": n,
        "pending_result": pending,
        "unresolved": unresolved,
        "hits": hits,
        "accuracy": round(hits / n, 4) if n else None,
        "mean_brier": round(sum(s["brier"] for s in settled) / n, 6) if n else None,
        "detail": settled[-20:],
        "claims": {
            "accuracy": "observed — how often the assessed selection matched the result in the held "
                        "corpus",
            "mean_brier": "observed arithmetic — squared error of the recorded market probability",
        },
        "caveats": [
            "A hit rate is not an edge. These are selections a user chose to assess, so the sample is "
            "self-selected and not a strategy test.",
            "Probabilities are de-vigged market prices, not our forecasts; scoring them measures the "
            "market, not the product.",
            "Nothing here accounts for the price paid, stake sizing or whether the quote was "
            "obtainable when the assessment was made.",
        ],
    }
