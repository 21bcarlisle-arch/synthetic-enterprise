"""The one canonical UK working-day calculator.

WHY THIS EXISTS (not tidiness). UK regulatory deadline arithmetic -- GSOP, SLC
obligations, complaint acknowledgement clocks, BSC/Elexon windows, Bacs
processing cycles -- is specified in WORKING DAYS. Until this module landed,
22 modules each implemented their own ``weekday() < 5`` loop and not one of
them knew what a bank holiday was. A deadline that a real supplier would
breach (because the intervening week contained Christmas) simply could not be
breached here: the whole class of that regulatory outcome was structurally
unreachable. Closing that is a correctness gain, not a refactor.

WHAT LIVES HERE AND WHAT DOES NOT. This module publishes a FACT (which dates
are bank holidays) and the ARITHMETIC over it. It holds no opinion about what
any deadline *is*. "SLC 18.7 allows 3 working days to acknowledge a complaint"
is a belief about the law and stays in the lane that holds it -- see
``regulation_commons/__init__.py`` for why that separation is the epistemic
wall and not bookkeeping.

THE CALENDAR IS DATED AND TIME-INDEXED. Bank holidays are not an algorithm.
They move (Easter), they gain substitute days when they fall on a weekend, and
one-offs exist that no rule generates -- the 2022 Platinum Jubilee, the 2022
State Funeral of Queen Elizabeth II, the 2023 Coronation. A holiday that did
not exist in a given year is not applied to that year, because the table is a
list of real dates rather than a set of recurrence rules.

PROVENANCE. ``data/bank_holidays_england_wales.json`` is generated, never
hand-typed, by ``regulation_commons/refresh_bank_holidays.py`` from two
independent Government Digital Service channels (the live
``gov.uk/bank-holidays.json`` feed and the ``alphagov/calendars`` source repo
that serves it). The generator REFUSES to write unless the two channels agree
on every date in their overlap. No date in that file came from anybody's
memory.

COVERAGE IS FINITE AND FAILS CLOSED. The sources cover 2015-2028. A date
outside that window raises ``CalendarCoverageError`` -- it never falls back to
weekends-only. A silently-wrong holiday answer is far worse than a refusal:
the caller would get a deadline that is confidently wrong, which is precisely
the defect this module was built to end. Extending coverage means re-running
the refresh script against the sources, not editing the table.

NATION. England & Wales only, behind a ``nation`` enum so widening is an added
member rather than a signature change. Scotland and NI diverge by *adding*
holidays, so E&W under-skips rather than over-skips -- the conservative error
direction for a deadline (a deadline computed slightly early is not a breach).
No customer record in this codebase carries a nation today; when one does,
this is the seam that takes it.
"""

from __future__ import annotations

import datetime as dt
import json
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Dict, FrozenSet, Tuple

_DATA_DIR = Path(__file__).parent / "data"


class Nation(Enum):
    """The bank-holiday division a date is judged against."""

    ENGLAND_AND_WALES = "england-and-wales"


_DATA_FILES: Dict[Nation, str] = {
    Nation.ENGLAND_AND_WALES: "bank_holidays_england_wales.json",
}


class CalendarCoverageError(Exception):
    """A date was asked about that the sourced calendar does not cover.

    Deliberately NOT a subclass of ``ValueError``/``LookupError``: a caller's
    broad ``except ValueError`` must not be able to swallow this into a
    weekends-only answer. An unavailable calendar is a FAILED check, never a
    skipped one (R15, fail-silent).
    """


class CalendarDataError(Exception):
    """The committed calendar file is missing, empty or unparseable.

    Raised rather than degrading to weekends-only, for the same reason as
    ``CalendarCoverageError`` (R15, fail-open).
    """


@lru_cache(maxsize=None)
def _load(nation: Nation) -> Tuple[FrozenSet[dt.date], int, int]:
    """Return (bank holiday dates, first covered year, last covered year)."""
    path = _DATA_DIR / _DATA_FILES[nation]
    try:
        raw = path.read_text()
    except OSError as exc:  # missing/unreadable -> FAIL, never fall back
        raise CalendarDataError(f"bank-holiday table unreadable at {path}: {exc}") from exc
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise CalendarDataError(f"bank-holiday table at {path} is not valid JSON: {exc}") from exc

    events = payload.get("events")
    if not events:
        raise CalendarDataError(f"bank-holiday table at {path} contains no events")

    try:
        dates = frozenset(dt.date.fromisoformat(event["date"]) for event in events)
        first = int(payload["coverage"]["first_year"])
        last = int(payload["coverage"]["last_year"])
    except (KeyError, TypeError, ValueError) as exc:
        raise CalendarDataError(f"bank-holiday table at {path} is malformed: {exc}") from exc

    if first > last:
        raise CalendarDataError(
            f"bank-holiday table at {path} declares an empty coverage window {first}-{last}"
        )
    declared = set(range(first, last + 1))
    actual = {d.year for d in dates}
    missing = sorted(declared - actual)
    if missing:
        raise CalendarDataError(
            f"bank-holiday table at {path} claims coverage {first}-{last} but has no "
            f"events for {missing} -- a year with zero holidays would silently answer "
            f"'not a holiday' for every date in it"
        )
    return dates, first, last


def coverage(nation: Nation = Nation.ENGLAND_AND_WALES) -> Tuple[int, int]:
    """Inclusive (first_year, last_year) the sourced calendar covers."""
    _dates, first, last = _load(nation)
    return first, last


def bank_holidays(nation: Nation = Nation.ENGLAND_AND_WALES) -> FrozenSet[dt.date]:
    """Every sourced bank-holiday date for ``nation``."""
    dates, _first, _last = _load(nation)
    return dates


def _check(d: dt.date, nation: Nation) -> dt.date:
    """Reject a datetime, and refuse any date the calendar cannot answer for."""
    if isinstance(d, dt.datetime):
        raise TypeError(
            "working-day arithmetic takes a date, not a datetime -- a working day has no "
            "sub-day resolution. Pass `.date()` and reattach any time-of-day deadline in "
            "your own module, where that judgement belongs."
        )
    if not isinstance(d, dt.date):
        raise TypeError(f"expected datetime.date, got {type(d).__name__}")
    _dates, first, last = _load(nation)
    if not first <= d.year <= last:
        raise CalendarCoverageError(
            f"{d.isoformat()} is outside the sourced {nation.value} bank-holiday calendar "
            f"({first}-{last}). Refusing to answer rather than silently treating it as "
            f"weekends-only. Re-run regulation_commons/refresh_bank_holidays.py to extend "
            f"coverage from the GDS sources."
        )
    return d


def is_bank_holiday(d: dt.date, *, nation: Nation = Nation.ENGLAND_AND_WALES) -> bool:
    """True iff ``d`` is a sourced bank holiday for ``nation``."""
    _check(d, nation)
    return d in bank_holidays(nation)


def is_working_day(d: dt.date, *, nation: Nation = Nation.ENGLAND_AND_WALES) -> bool:
    """True iff ``d`` is Mon-Fri AND not a bank holiday for ``nation``."""
    _check(d, nation)
    return d.weekday() < 5 and d not in bank_holidays(nation)


def add_working_days(
    start: dt.date, n: int, *, nation: Nation = Nation.ENGLAND_AND_WALES
) -> dt.date:
    """Advance ``n`` working days from ``start``.

    ``n == 0`` returns ``start`` unchanged, including when ``start`` is itself
    a weekend or bank holiday -- every migrated caller relied on that. The
    first increment from a non-working ``start`` lands on the next working
    day, so a Saturday start still yields a working-day answer for ``n >= 1``.

    ``n < 0`` raises: no caller subtracts working days, and adding the
    behaviour silently would be undiscovered scope rather than a real need.
    """
    _check(start, nation)
    if n < 0:
        raise ValueError(f"add_working_days does not subtract (got n={n})")
    current = start
    remaining = n
    while remaining > 0:
        current += dt.timedelta(days=1)
        if is_working_day(current, nation=nation):
            remaining -= 1
    return current


def working_days_between(
    start: dt.date, end: dt.date, *, nation: Nation = Nation.ENGLAND_AND_WALES
) -> int:
    """Working days in the half-open interval ``[start, end)``.

    Counts ``start`` itself if it is a working day; never counts ``end``.
    Returns 0 when ``end <= start``. This is the "how long has this been open"
    convention -- the shape the ``working_days_open`` callers used.
    """
    _check(start, nation)
    _check(end, nation)
    count = 0
    current = start
    while current < end:
        if is_working_day(current, nation=nation):
            count += 1
        current += dt.timedelta(days=1)
    return count


def working_days_elapsed(
    start: dt.date, end: dt.date, *, nation: Nation = Nation.ENGLAND_AND_WALES
) -> int:
    """Working days in the half-open interval ``(start, end]``.

    Counts ``end`` itself if it is a working day; never counts ``start``.
    Returns 0 when ``end <= start``. This is the "how many working days have
    passed since the clock started" convention -- the shape the
    ``_working_days_between`` callers used, and NOT the same function as
    :func:`working_days_between` (they diverge whenever an endpoint is a
    non-working day, which is exactly when a deadline argument happens).

    Walks the same :func:`is_working_day` predicate as
    :func:`working_days_between` -- there is exactly one definition of a
    working day, so the two conventions cannot drift apart. It does not simply
    call that function on a shifted interval, because shifting past ``end``
    would raise at the last covered date for no real reason.
    """
    _check(start, nation)
    _check(end, nation)
    count = 0
    current = start + dt.timedelta(days=1)
    while current <= end:
        if is_working_day(current, nation=nation):
            count += 1
        current += dt.timedelta(days=1)
    return count
