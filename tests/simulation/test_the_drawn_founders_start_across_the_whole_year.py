"""Drawn founders start across the whole of 2016, not its first seven months.

The founder draw reads a DATE-ORDERED stream and asks for headroom above the director's number.
Until 2026-10-03 it kept the first `wanted` eligible candidates, which kept the first ~1/headroom
of the year: every drawn founder began between 1 January and 14 August, and their renewals bunched
in the same months for a decade. Real switching runs through every month and peaks in October
(DESNZ QEP Table 2.7.1, `docs/market_research/gb_domestic_switching_by_calendar_month.md`).

THE PROPERTY, NOT TODAY'S COUNTS. Thinning a uniform year evenly leaves the last founder in the
stream's final 1/wanted, in December. Truncating at 1/1.6 of the year left it near August. A 1
October line sits between the two whatever the headroom or the founder number becomes, so it
fails on a return to truncation and not on an ordinary change of either dial.
"""
from __future__ import annotations

import datetime as dt

import pytest

from simulation.live_population import _founder_roster_size, founder_accounts, founder_book

SEEDS = (42, 61001, 61002, 61003)


@pytest.mark.parametrize("seed", SEEDS)
def test_the_last_drawn_founder_starts_in_the_last_quarter_of_the_year(seed):
    drawn = founder_book(seed)[_founder_roster_size():]
    assert drawn, "no founder was drawn, so the property below would hold of nothing"
    latest = max(dt.date.fromisoformat(r["acquisition_date"]) for r in drawn)
    assert latest >= dt.date(2016, 10, 1), (
        f"seed {seed}: the last drawn founder starts {latest}, so the draw kept only the start of "
        "a date-ordered year")


@pytest.mark.parametrize("seed", SEEDS)
def test_thinning_still_delivers_the_directors_number(seed):
    assert len(founder_book(seed)) == founder_accounts()
