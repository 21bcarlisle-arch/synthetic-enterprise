"""The day a Bacs direct debit actually lands -- the world's reading of the published calendar.

A collection the supplier schedules for a weekend or a bank holiday does not move money that day.
Bacs settles only on English bank working days, and a due date on a non-processing day is collected
on the next working day, never the one before (Bacs via CIPP, Pay.UK, GoCardless; the knowledge page
is `docs/market_research/payments_and_direct_debit_2026-10-25.md`, "The day a collection lands").
This is the rails' physics, not a choice the supplier makes, so the world holds it.

Until 2026-11-08 every DD date in the run was its scheduled date: 11,067 of 36,098 collections on
the af31e73fa7 ledger fell on a weekend or bank holiday (N22).

The calendar is the regulation commons' data
(`docs/domain_artefact_library/regulatory/england_and_wales_bank_holidays.json`), not
`company.compliance.working_days`. The world may not import the company's reading, and the company's
table is the same source of record. Outside the artefact's coverage this raises, as the company's
does, rather than give a weekend-only answer.
"""
from __future__ import annotations

import json
from datetime import date, timedelta
from functools import lru_cache
from pathlib import Path

_CALENDAR = (Path(__file__).resolve().parent.parent / "docs" / "domain_artefact_library"
             / "regulatory" / "england_and_wales_bank_holidays.json")


@lru_cache(maxsize=1)
def _calendar() -> tuple[frozenset[date], int, int]:
    art = json.loads(_CALENDAR.read_text())
    days = frozenset(date.fromisoformat(h["date"]) for h in art["holidays"])
    return days, art["coverage"]["first_year"], art["coverage"]["last_year"]


def is_bacs_processing_day(d: date) -> bool:
    """Mon-Fri and not an England and Wales bank holiday (substitute days included)."""
    holidays, lo, hi = _calendar()
    if not lo <= d.year <= hi:
        raise ValueError(f"{d.isoformat()} is outside the committed bank-holiday calendar "
                         f"({lo}-{hi}); extend the commons artefact from its source of record")
    return d.weekday() < 5 and d not in holidays


def collected_on(scheduled: date) -> date:
    """The first Bacs processing day on or after `scheduled`: the day a DD due then is collected.

    A processing day is returned unchanged. The longest run of non-processing days 2016-2025 is
    four (Good Friday to Easter Monday, or Christmas with substitute days), so this moves a date by
    at most four calendar days."""
    d = scheduled
    while not is_bacs_processing_day(d):
        d += timedelta(days=1)
    return d
