"""Fixture clock handling: local civil time to UTC, and the T-90 cutoff rule.

The data files give a date and a kickoff time with **no timezone**. Computing a cutoff
by subtracting ninety minutes from a wall clock is reproducible arithmetic on an
ambiguous clock, which is why the protocol could not call the cutoff auditable. This
module makes the assumption explicit and testable:

  each division's date and time are local civil time in that country, converted to UTC
  with the IANA zone for that country, and all arithmetic happens in UTC.

That matters twice a year. Across a daylight-saving boundary the offset between two
apparently adjacent fixtures can differ by an hour, so a cutoff computed from a wall
clock and a cutoff computed from UTC disagree by exactly the amount that decides
whether an earlier match counts as available.

A timestamp that falls in a DST gap (spring forward) or is ambiguous (autumn) is flagged
rather than silently resolved.

    python research/fixture_time.py --audit
"""

from __future__ import annotations

import csv
import glob
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]

# The files carry no timezone field, so this map is an assumption about the source, not
# a fact read from it. It is checked by --audit: every parsed time must be a plausible
# local kickoff, and nothing may land in a DST gap.
LEAGUE_TZ = {
    "E0": "Europe/London",
    "E1": "Europe/London",
    "SP1": "Europe/Madrid",
    "D1": "Europe/Berlin",
    "I1": "Europe/Rome",
    "F1": "Europe/Paris",
    "N1": "Europe/Oslo",
    "P1": "Europe/Lisbon",
}

CUTOFF = timedelta(minutes=90)
INPUT_BUFFER = timedelta(hours=3)   # full time, stoppage, publication margin


class ClockError(ValueError):
    """Raised when a fixture's clock cannot be interpreted unambiguously."""


def _local(naive: datetime, league: str) -> tuple[ZoneInfo, datetime]:
    zone_name = LEAGUE_TZ.get(league)
    if zone_name is None:
        raise ClockError(f"no timezone mapping for league {league!r}")
    return ZoneInfo(zone_name), naive.replace(tzinfo=ZoneInfo(zone_name), fold=0)


def clock_status(naive: datetime, league: str) -> str:
    """'ok', 'ambiguous' (autumn fold) or 'gap' (spring forward)."""
    zone_name = LEAGUE_TZ.get(league)
    if zone_name is None:
        raise ClockError(f"no timezone mapping for league {league!r}")
    zone = ZoneInfo(zone_name)
    first = naive.replace(tzinfo=zone, fold=0)
    second = naive.replace(tzinfo=zone, fold=1)
    if first.utcoffset() != second.utcoffset():
        # Either the wall time occurs twice (ambiguous) or not at all (gap). Round-trip
        # decides which: a gap cannot be reproduced from its own UTC instant.
        if first.astimezone(timezone.utc).astimezone(zone).replace(tzinfo=None) != naive:
            return "gap"
        return "ambiguous"
    return "ok"


def kickoff_utc(date: str, clock: str, league: str) -> datetime:
    """Parse `dd/mm/yyyy` + `HH:MM` as the league's local civil time, return aware UTC."""
    try:
        naive = datetime.strptime(f"{date.strip()} {clock.strip()}", "%d/%m/%Y %H:%M")
    except ValueError as exc:
        raise ClockError(f"unparseable date/time {date!r} {clock!r}") from exc
    status = clock_status(naive, league)
    if status != "ok":
        raise ClockError(f"{league} {date} {clock} is {status} in local time")
    _, local = _local(naive, league)
    return local.astimezone(timezone.utc)


def cutoff_utc(date: str, clock: str, league: str) -> datetime:
    """The model's information cutoff: kickoff minus ninety minutes, in UTC."""
    return kickoff_utc(date, clock, league) - CUTOFF


def available_at_cutoff(input_date: str, input_clock: str, input_league: str,
                        fixture_date: str, fixture_clock: str, fixture_league: str) -> bool:
    """True when a prior match's result is final before the fixture's cutoff."""
    prior = kickoff_utc(input_date, input_clock, input_league) + INPUT_BUFFER
    return prior <= cutoff_utc(fixture_date, fixture_clock, fixture_league)


def audit(data_dir: Path | None = None, expected: int | None = None) -> int:
    """Every fixture row must be accounted for, parsed, mapped and unambiguous.

    An audit that silently skips a row with a missing clock is not an audit: it reports
    "clean" over whatever subset happened to be parseable. Total rows, parsed rows and
    failures are therefore counted separately, and any missing or unparseable clock is a
    failure rather than a skip.

    A clean parse is evidence about *our* arithmetic and the corpus's completeness. It is
    **not** evidence that the source used these local zones — the zone map is an
    assumption, and no amount of successful conversion tests it.
    """
    problems: list[str] = []
    rows_total = 0
    parsed = 0
    missing_clock = 0
    leagues: dict[str, int] = {}
    for path in sorted(glob.glob(str((data_dir or ROOT / "research" / "data") / "*.csv"))):
        league = Path(path).stem.split("_")[0]
        with open(path, encoding="latin-1", newline="") as fh:
            for row in csv.DictReader(fh):
                rows_total += 1
                date, clock = row.get("Date", "").strip(), row.get("Time", "").strip()
                if not date or not clock:
                    missing_clock += 1
                    if missing_clock <= 10:
                        problems.append(f"{Path(path).name}: row {rows_total} has no clock "
                                        f"(Date={date!r}, Time={clock!r})")
                    continue
                leagues[league] = leagues.get(league, 0) + 1
                try:
                    kickoff_utc(date, clock, league)
                except ClockError as exc:
                    problems.append(str(exc))
                    continue
                parsed += 1

    unaccounted = rows_total - parsed - missing_clock
    print(f"fixture rows:            {rows_total}")
    print(f"parsed to a UTC instant: {parsed}")
    print(f"missing clock fields:    {missing_clock}")
    print(f"failed conversion:       {unaccounted}")
    for league in sorted(leagues):
        zone = LEAGUE_TZ.get(league, "UNMAPPED")
        print(f"  {league:4} {leagues[league]:5}  {zone}")

    if missing_clock:
        problems.append(f"{missing_clock} row(s) have no Date or Time")
    if unaccounted:
        problems.append(f"{unaccounted} row(s) parsed but not counted as converted")
    if expected is not None and rows_total != expected:
        problems.append(f"expected {expected} fixture rows, found {rows_total}")

    if problems:
        print(f"PROBLEMS: {len(problems)}")
        for p in problems[:10]:
            print("  " + p)
        return 1
    print(f"all {rows_total} fixture rows accounted for, no ambiguous or unmapped clocks")
    print("note: this validates our arithmetic and completeness, not the source's "
          "timezone convention")
    return 0


if __name__ == "__main__":
    import sys

    want_audit = "--audit" in sys.argv
    expect = None
    if "--expect" in sys.argv:
        expect = int(sys.argv[sys.argv.index("--expect") + 1])
    data = None
    if "--data" in sys.argv:
        data = Path(sys.argv[sys.argv.index("--data") + 1])
    # Keyword, not positional: `audit(expect)` silently became `data_dir=expect` when the
    # signature gained a first parameter, and the documented command failed.
    sys.exit(audit(data_dir=data, expected=expect) if want_audit else 0)
