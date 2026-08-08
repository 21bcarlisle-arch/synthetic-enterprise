"""CHARACTERIZATION: freezes current behaviour, including behaviour that may be
defective. Characterized, not endorsed.

Target: company/pricing/ofgem_price_cap.py — the Ofgem Default Tariff Cap ceiling
applied to domestic unit rates. Two deliberately separate lookups: an ANNUAL blend
and a CAP-WINDOW lookup keyed on the window that actually contained a date.

Values here are real published regulatory history (R13 baseline). These tests
record what the module returns; they are not a judgement on the published levels.
All dates are literals.
"""
from __future__ import annotations

import datetime as dt
from datetime import date

import pytest

from company.pricing.ofgem_price_cap import (
    get_cap_unit_rate_for_date,
    get_cap_unit_rate_gbp_per_mwh,
)

# ---------------------------------------------------------------------------
# Annual lookup
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("year", [2015, 2018])
def test_no_annual_cap_before_2019(year):
    assert get_cap_unit_rate_gbp_per_mwh("electricity", year) is None
    assert get_cap_unit_rate_gbp_per_mwh("gas", year) is None


@pytest.mark.parametrize(
    "year,elec,gas",
    [(2019, 165.0, 26.0), (2020, 157.0, 25.0), (2021, 183.0, 35.0),
     (2022, 305.0, 95.0), (2023, 265.0, 70.0), (2024, 210.0, 55.0),
     (2025, 190.0, 52.0)],
)
def test_annual_cap_table(year, elec, gas):
    assert get_cap_unit_rate_gbp_per_mwh("electricity", year) == elec
    assert get_cap_unit_rate_gbp_per_mwh("gas", year) == gas


def test_annual_lookup_beyond_the_table_returns_a_flat_fallback():
    assert get_cap_unit_rate_gbp_per_mwh("electricity", 2030) == 190.0
    assert get_cap_unit_rate_gbp_per_mwh("gas", 2030) == 52.0


# ---------------------------------------------------------------------------
# Cap-window lookup
# ---------------------------------------------------------------------------


def test_no_window_cap_before_the_first_published_day():
    assert get_cap_unit_rate_for_date("electricity", date(2018, 12, 31)) is None
    assert get_cap_unit_rate_for_date("electricity", date(2019, 1, 1)) == 165.2


@pytest.mark.parametrize(
    "on_date,elec",
    [
        ("2021-09-30", 189.5),   # last day of the Apr-2021 window
        ("2021-10-01", 208.0),   # Oct-2021 window opens
        ("2022-03-31", 208.0),   # ...and runs through 31 Mar 2022
        ("2022-04-01", 283.4),   # the +54% step the annual blend erases
        ("2022-09-30", 283.4),
    ],
)
def test_window_boundaries_are_inclusive_on_both_ends(on_date, elec):
    assert get_cap_unit_rate_for_date("electricity", date.fromisoformat(on_date)) == elec


@pytest.mark.parametrize(
    "on_date,elec,gas",
    [("2022-11-15", 340.0, 103.2), ("2023-02-15", 340.0, 103.2),
     ("2023-05-15", 340.0, 103.2)],
)
def test_epg_overlay_binds_where_it_was_below_the_ofgem_cap(on_date, elec, gas):
    """Oct-2022 to Jun-2023 the binding ceiling is min(Ofgem cap, EPG) — the
    Jan-2023 Ofgem level was 674.7 but the EPG held it at 340.0."""
    d = date.fromisoformat(on_date)
    assert get_cap_unit_rate_for_date("electricity", d) == elec
    assert get_cap_unit_rate_for_date("gas", d) == gas


def test_epg_expiry_lets_the_ofgem_level_bind_again():
    assert get_cap_unit_rate_for_date("electricity", date(2023, 6, 30)) == 340.0
    assert get_cap_unit_rate_for_date("electricity", date(2023, 7, 1)) == 301.1


def test_dates_past_the_schedule_carry_the_last_window_forward_never_uncapped():
    """Deliberately NOT None: returning None past the schedule would silently
    un-cap every domestic customer (the FAIL-OPEN pattern)."""
    assert get_cap_unit_rate_for_date("electricity", date(2030, 6, 1)) == 263.5
    assert get_cap_unit_rate_for_date("gas", date(2030, 6, 1)) == 62.9


# ---------------------------------------------------------------------------
# Cross-checks between the two lookups
# ---------------------------------------------------------------------------


def test_the_annual_table_is_not_the_day_weighted_blend_of_the_windows():
    """SURPRISE (unit class, money-relevant): the annual lookup is documented as
    "the ANNUAL blend", but for 2022 it returns 305.0 £/MWh while the day-weighted
    mean of that year's actual cap windows is 279.1 — a £25.9/MWh LOOSER ceiling.
    Which of the two accessors a caller happens to use changes the ceiling applied
    to the same customer in the same year."""
    day = date(2022, 1, 1)
    total, days = 0.0, 0
    while day <= date(2022, 12, 31):
        total += get_cap_unit_rate_for_date("electricity", day)
        days += 1
        day += dt.timedelta(days=1)
    assert round(total / days, 1) == 279.1
    assert get_cap_unit_rate_gbp_per_mwh("electricity", 2022) == 305.0


def test_the_two_lookups_diverge_sharply_past_the_published_schedule():
    """SURPRISE (unit class): past 2025 the window lookup carries the last real
    window forward (263.5) while the annual lookup drops to a hardcoded fallback
    (190.0) — a £73.5/MWh disagreement about the same ceiling in the same year."""
    assert get_cap_unit_rate_for_date("electricity", date(2026, 6, 1)) == 263.5
    assert get_cap_unit_rate_gbp_per_mwh("electricity", 2026) == 190.0


# ---------------------------------------------------------------------------
# Fuel argument handling
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("fuel", ["elec", "Electricity", "ELECTRICITY", "Gas", "", "dual"])
def test_an_unrecognised_fuel_string_returns_none_which_reads_as_no_cap(fuel):
    """SURPRISE (R15 FAIL-OPEN class, money-relevant): the fuel name is matched
    exactly and case-sensitively, and anything else returns None. Callers are
    documented to apply `min(unit_rate, cap) when cap is not None`, so None means
    NO CEILING. A caller passing "elec" or "Electricity" — neither obviously wrong
    — silently un-caps the customer rather than raising."""
    assert get_cap_unit_rate_for_date(fuel, date(2023, 1, 15)) is None
    assert get_cap_unit_rate_gbp_per_mwh(fuel, 2023) is None


def test_the_two_recognised_fuel_names_are_exactly_these():
    assert get_cap_unit_rate_for_date("electricity", date(2023, 1, 15)) is not None
    assert get_cap_unit_rate_for_date("gas", date(2023, 1, 15)) is not None


# ---------------------------------------------------------------------------
# Shape properties of the schedule
# ---------------------------------------------------------------------------


def test_every_day_from_2019_to_2025_resolves_to_a_cap_with_no_gaps():
    """The windows must tile the whole period — a gap would fall through to the
    carry-forward branch and silently apply the 2025 level to, say, 2020."""
    day = date(2019, 1, 1)
    while day <= date(2025, 12, 31):
        assert get_cap_unit_rate_for_date("electricity", day) is not None
        assert get_cap_unit_rate_for_date("gas", day) is not None
        day += dt.timedelta(days=1)


def test_electricity_ceiling_always_exceeds_gas_across_the_schedule():
    day = date(2019, 1, 1)
    while day <= date(2025, 12, 31):
        assert get_cap_unit_rate_for_date("electricity", day) > get_cap_unit_rate_for_date(
            "gas", day
        )
        day += dt.timedelta(days=90)


def test_the_april_2022_step_is_the_crisis_jump_the_annual_blend_hides():
    before = get_cap_unit_rate_for_date("electricity", date(2022, 3, 31))
    after = get_cap_unit_rate_for_date("electricity", date(2022, 4, 1))
    assert before == 208.0 and after == 283.4
    assert round((after - before) / before, 2) == 0.36
