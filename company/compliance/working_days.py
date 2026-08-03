"""Canonical UK working-day arithmetic -- the ONE definition (R10 class fix).

WHY THIS EXISTS. 22 modules across `company/`, `sim/`, `simulation/` and `saas/` each
defined their own working-day arithmetic (`_add_working_days`, `_working_days_between`,
inline weekend-skipping loops). Every one was Mon-Fri only with ZERO bank-holiday
awareness, so every regulatory deadline the company computes -- SLC complaint acks, the
SLC 14 10-working-day refund deadline, EMIR T+1, BSC dispute windows, the Bacs cycle --
ran EARLY across a bank holiday. A real supplier is fined against the real calendar.
Fixing one instance would have been the second instance of the same defect, so per R10
the closure is the invariant, not the instance: one primitive, plus a guard
(`tools/working_day_guard.py`) that fails the build on a second definition.

Design: `docs/design/WORKING_DAY_CALCULATOR_DISCOVER.md` (DISCOVER half, 2026-07-28).

--------------------------------------------------------------------------------------
CALENDAR PROVENANCE -- every date below is government-published, none is derived,
inferred or typed from memory (R13: fabricating a calendar would be false precision).

Source of record:
  `ministryofjustice/govuk-bank-holidays`, `govuk_bank_holidays/bank-holidays.json`
  (fetched 2026-08-03 from raw.githubusercontent.com, @ branch `main`) -- a cache of
  the GDS `https://www.gov.uk/bank-holidays.json` feed. Chosen as the source of record
  because it is on this project's egress allowlist (`background/egress_allowlist.py`)
  and, unlike the live feed, covers years GDS has since dropped from its rolling window.

Corroboration -- THREE independent GDS-derived sources were reconciled before any date
was committed here, and all three agree EXACTLY on every overlapping year:
  * `alphagov/calendars` @ `master`, `lib/data/bank-holidays.json` (the GDS repository
    that SERVES the gov.uk endpoint; covers 2015-2021, DD/MM/YYYY)
        vs source of record, 2015-2021: 56 events each, identical set.
  * the live `https://www.gov.uk/bank-holidays.json` feed (covers 2019-2028)
        vs source of record, 2019-2028: 83 events each, identical set.
  * `alphagov/calendars` vs the live feed, 2019-2021: 24 events each, identical set.

DIVISION: England & Wales only. Scotland and Northern Ireland have additional holidays
(St Andrew's Day, Battle of the Boyne, 2 Jan) and are deliberately NOT modelled -- see
`Nation` below for the materiality judgement and why E&W is the safe default direction.

REFRESH: the table is static and committed on purpose (C-S4 / "no network in autonomous
runs" -- a sim run must never depend on a live HTTP call). To extend it, re-fetch the
source of record, re-run the three-way reconciliation above, and widen `_COVERAGE`.
--------------------------------------------------------------------------------------
"""

from __future__ import annotations

import datetime as dt
from enum import Enum

__all__ = [
    "Nation",
    "OutsideCalendarCoverage",
    "bank_holidays",
    "calendar_coverage",
    "is_working_day",
    "add_working_days",
    "working_days_between",
]


class Nation(Enum):
    """The calendar division a deadline is computed against.

    Currently single-valued. It exists as an enum rather than being absent because
    every caller is today a GB-wide regulatory deadline (Ofgem SLC, BSC, EMIR) or a
    company-wide operational one (Bacs, CRM), none segmented by customer nation, and
    the customer model carries no nation field. E&W is the correct default error
    direction: Scotland/NI diverge by ADDING holidays, so an E&W calculation
    UNDER-skips -- it can only ever compute a deadline early (conservative), never
    late (a breach). Widening is a new member plus a new table, not a rework.
    """

    ENGLAND_AND_WALES = "england-and-wales"


class OutsideCalendarCoverage(ValueError):
    """Raised when arithmetic would rely on a year the committed table does not cover.

    This is the deliberate FAIL-CLOSED choice (R15). The tempting alternative -- treat
    an uncovered year as simply having no bank holidays -- is the textbook fail-open:
    it returns a confident, silently wrong answer (weekend-only, i.e. the exact defect
    this module exists to fix) precisely when the data is missing. A missing calendar
    is a FAILED calculation, not a holiday-free one.
    """


# England & Wales bank holidays. Provenance and three-way reconciliation: module
# docstring above. Do not hand-edit -- regenerate from the source of record.
_ENGLAND_AND_WALES: tuple[str, ...] = (
    # 2012
    "2012-01-02",  # New Year's Day (Substitute day)
    "2012-04-06",  # Good Friday
    "2012-04-09",  # Easter Monday
    "2012-05-07",  # Early May bank holiday
    "2012-06-04",  # Spring bank holiday (Substitute day)
    "2012-06-05",  # Queen's Diamond Jubilee (Extra bank holiday)
    "2012-08-27",  # Summer bank holiday
    "2012-12-25",  # Christmas Day
    "2012-12-26",  # Boxing Day
    # 2013
    "2013-01-01",  # New Year's Day
    "2013-03-29",  # Good Friday
    "2013-04-01",  # Easter Monday
    "2013-05-06",  # Early May bank holiday
    "2013-05-27",  # Spring bank holiday
    "2013-08-26",  # Summer bank holiday
    "2013-12-25",  # Christmas Day
    "2013-12-26",  # Boxing Day
    # 2014
    "2014-01-01",  # New Year's Day
    "2014-04-18",  # Good Friday
    "2014-04-21",  # Easter Monday
    "2014-05-05",  # Early May bank holiday
    "2014-05-26",  # Spring bank holiday
    "2014-08-25",  # Summer bank holiday
    "2014-12-25",  # Christmas Day
    "2014-12-26",  # Boxing Day
    # 2015
    "2015-01-01",  # New Year's Day
    "2015-04-03",  # Good Friday
    "2015-04-06",  # Easter Monday
    "2015-05-04",  # Early May bank holiday
    "2015-05-25",  # Spring bank holiday
    "2015-08-31",  # Summer bank holiday
    "2015-12-25",  # Christmas Day
    "2015-12-28",  # Boxing Day (Substitute day)
    # 2016
    "2016-01-01",  # New Year's Day
    "2016-03-25",  # Good Friday
    "2016-03-28",  # Easter Monday
    "2016-05-02",  # Early May bank holiday
    "2016-05-30",  # Spring bank holiday
    "2016-08-29",  # Summer bank holiday
    "2016-12-26",  # Boxing Day
    "2016-12-27",  # Christmas Day (Substitute day)
    # 2017
    "2017-01-02",  # New Year's Day (Substitute day)
    "2017-04-14",  # Good Friday
    "2017-04-17",  # Easter Monday
    "2017-05-01",  # Early May bank holiday
    "2017-05-29",  # Spring bank holiday
    "2017-08-28",  # Summer bank holiday
    "2017-12-25",  # Christmas Day
    "2017-12-26",  # Boxing Day
    # 2018
    "2018-01-01",  # New Year's Day
    "2018-03-30",  # Good Friday
    "2018-04-02",  # Easter Monday
    "2018-05-07",  # Early May bank holiday
    "2018-05-28",  # Spring bank holiday
    "2018-08-27",  # Summer bank holiday
    "2018-12-25",  # Christmas Day
    "2018-12-26",  # Boxing Day
    # 2019
    "2019-01-01",  # New Year's Day
    "2019-04-19",  # Good Friday
    "2019-04-22",  # Easter Monday
    "2019-05-06",  # Early May bank holiday
    "2019-05-27",  # Spring bank holiday
    "2019-08-26",  # Summer bank holiday
    "2019-12-25",  # Christmas Day
    "2019-12-26",  # Boxing Day
    # 2020
    "2020-01-01",  # New Year's Day
    "2020-04-10",  # Good Friday
    "2020-04-13",  # Easter Monday
    "2020-05-08",  # Early May bank holiday (VE day)
    "2020-05-25",  # Spring bank holiday
    "2020-08-31",  # Summer bank holiday
    "2020-12-25",  # Christmas Day
    "2020-12-28",  # Boxing Day (Substitute day)
    # 2021
    "2021-01-01",  # New Year's Day
    "2021-04-02",  # Good Friday
    "2021-04-05",  # Easter Monday
    "2021-05-03",  # Early May bank holiday
    "2021-05-31",  # Spring bank holiday
    "2021-08-30",  # Summer bank holiday
    "2021-12-27",  # Christmas Day (Substitute day)
    "2021-12-28",  # Boxing Day (Substitute day)
    # 2022
    "2022-01-03",  # New Year's Day (Substitute day)
    "2022-04-15",  # Good Friday
    "2022-04-18",  # Easter Monday
    "2022-05-02",  # Early May bank holiday
    "2022-06-02",  # Spring bank holiday
    "2022-06-03",  # Platinum Jubilee bank holiday
    "2022-08-29",  # Summer bank holiday
    "2022-09-19",  # Bank Holiday for the State Funeral of Queen Elizabeth II
    "2022-12-26",  # Boxing Day
    "2022-12-27",  # Christmas Day (Substitute day)
    # 2023
    "2023-01-02",  # New Year's Day (Substitute day)
    "2023-04-07",  # Good Friday
    "2023-04-10",  # Easter Monday
    "2023-05-01",  # Early May bank holiday
    "2023-05-08",  # Bank holiday for the coronation of King Charles III
    "2023-05-29",  # Spring bank holiday
    "2023-08-28",  # Summer bank holiday
    "2023-12-25",  # Christmas Day
    "2023-12-26",  # Boxing Day
    # 2024
    "2024-01-01",  # New Year's Day
    "2024-03-29",  # Good Friday
    "2024-04-01",  # Easter Monday
    "2024-05-06",  # Early May bank holiday
    "2024-05-27",  # Spring bank holiday
    "2024-08-26",  # Summer bank holiday
    "2024-12-25",  # Christmas Day
    "2024-12-26",  # Boxing Day
    # 2025
    "2025-01-01",  # New Year's Day
    "2025-04-18",  # Good Friday
    "2025-04-21",  # Easter Monday
    "2025-05-05",  # Early May bank holiday
    "2025-05-26",  # Spring bank holiday
    "2025-08-25",  # Summer bank holiday
    "2025-12-25",  # Christmas Day
    "2025-12-26",  # Boxing Day
    # 2026
    "2026-01-01",  # New Year's Day
    "2026-04-03",  # Good Friday
    "2026-04-06",  # Easter Monday
    "2026-05-04",  # Early May bank holiday
    "2026-05-25",  # Spring bank holiday
    "2026-08-31",  # Summer bank holiday
    "2026-12-25",  # Christmas Day
    "2026-12-28",  # Boxing Day (Substitute day)
    # 2027
    "2027-01-01",  # New Year's Day
    "2027-03-26",  # Good Friday
    "2027-03-29",  # Easter Monday
    "2027-05-03",  # Early May bank holiday
    "2027-05-31",  # Spring bank holiday
    "2027-08-30",  # Summer bank holiday
    "2027-12-27",  # Christmas Day (Substitute day)
    "2027-12-28",  # Boxing Day (Substitute day)
    # 2028
    "2028-01-03",  # New Year's Day (Substitute day)
    "2028-04-14",  # Good Friday
    "2028-04-17",  # Easter Monday
    "2028-05-01",  # Early May bank holiday
    "2028-05-29",  # Spring bank holiday
    "2028-08-28",  # Summer bank holiday
    "2028-12-25",  # Christmas Day
    "2028-12-26",  # Boxing Day
)

_BANK_HOLIDAYS: dict[Nation, frozenset[dt.date]] = {
    Nation.ENGLAND_AND_WALES: frozenset(
        dt.date.fromisoformat(s) for s in _ENGLAND_AND_WALES
    ),
}

_COVERAGE: dict[Nation, tuple[int, int]] = {
    Nation.ENGLAND_AND_WALES: (2012, 2028),
}


def bank_holidays(nation: Nation = Nation.ENGLAND_AND_WALES) -> frozenset[dt.date]:
    """The committed bank-holiday set for `nation` (immutable)."""
    return _BANK_HOLIDAYS[nation]


def calendar_coverage(nation: Nation = Nation.ENGLAND_AND_WALES) -> tuple[int, int]:
    """Inclusive (first_year, last_year) the committed table covers for `nation`."""
    return _COVERAGE[nation]


def _check_covered(d: dt.date, nation: Nation) -> None:
    lo, hi = _COVERAGE[nation]
    if not lo <= d.year <= hi:
        raise OutsideCalendarCoverage(
            f"{d.isoformat()} is outside the committed {nation.value} bank-holiday "
            f"calendar ({lo}-{hi}). Extend the table from the source of record rather "
            f"than computing a weekend-only answer."
        )


def is_working_day(d: dt.date, *, nation: Nation = Nation.ENGLAND_AND_WALES) -> bool:
    """True iff `d` is Mon-Fri AND not a `nation` bank holiday.

    Raises OutsideCalendarCoverage if `d`'s year is not covered by the table.
    """
    if isinstance(d, dt.datetime):
        d = d.date()
    _check_covered(d, nation)
    return d.weekday() < 5 and d not in _BANK_HOLIDAYS[nation]


def add_working_days(
    start: dt.date, n: int, *, nation: Nation = Nation.ENGLAND_AND_WALES
) -> dt.date:
    """Advance `n` working days from `start`.

    Semantics are INCREMENT-THEN-TEST, matching all 15 pre-existing
    `_add_working_days` implementations byte-for-byte in behaviour (verified by
    differential test over 2016-2026 x n in {0,1,2,3,5,10,20,40} before this module
    was written -- all 15 agreed with each other, so one canonical semantics is safe):

      * `n == 0` returns `start` UNCHANGED, even when `start` is a weekend or a bank
        holiday. Several callers rely on this.
      * `n >= 1` always lands on a working day, and a weekend/holiday `start` is
        handled naturally -- the first increment walks forward to the next one.
      * `n < 0` raises ValueError. No caller subtracts working days; supporting it
        silently would be undiscovered scope, not a real need.

    The ONLY behavioural change vs the 15 implementations it replaces is the intended
    one: bank holidays are now skipped.
    """
    if isinstance(start, dt.datetime):
        start = start.date()
    if n < 0:
        raise ValueError(
            f"add_working_days does not subtract (got n={n}); no caller needs it and "
            f"a silent implementation would be undiscovered scope."
        )
    _check_covered(start, nation)
    d = start
    remaining = n
    while remaining > 0:
        d += dt.timedelta(days=1)
        _check_covered(d, nation)
        if is_working_day(d, nation=nation):
            remaining -= 1
    return d


def working_days_between(
    start: dt.date, end: dt.date, *, nation: Nation = Nation.ENGLAND_AND_WALES
) -> int:
    """Count working days in `(start, end]` -- i.e. days AFTER `start`, up to and
    INCLUDING `end`.

    NOTE THE INTERVAL. `docs/design/WORKING_DAY_CALCULATOR_DISCOVER.md` s4 specifies
    "half-open [start, end)". That is a mis-statement of the shipped behaviour: the 4
    pre-existing `_working_days_between` implementations (all AST-identical) increment
    BEFORE testing, giving `(start, end]`. The two readings agree whenever both
    endpoints are working days, which is why the slip survived review -- they diverge
    exactly when an endpoint is a weekend or holiday (Fri->Sat is 0 under the shipped
    reading, 1 under the doc's). Implementing the doc literally would have silently
    moved every deadline this primitive is supposed to leave alone, so the SHIPPED
    semantics is canonical here and the design doc is what needs correcting.

    `end <= start` returns 0 (the shipped loop never runs). Raises
    OutsideCalendarCoverage if either endpoint's year is not covered.
    """
    if isinstance(start, dt.datetime):
        start = start.date()
    if isinstance(end, dt.datetime):
        end = end.date()
    _check_covered(start, nation)
    _check_covered(end, nation)
    days = 0
    current = start
    while current < end:
        current += dt.timedelta(days=1)
        if is_working_day(current, nation=nation):
            days += 1
    return days
