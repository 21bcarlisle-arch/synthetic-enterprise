"""W3_1b — sub-annual Ofgem cap granularity.

The atom: the deemed/SVT and resi-fixed clamps used to key the cap on
``current_date.year``, so every day of 2022 got one full-year blend
(elec 305 / gas 95 £/MWh). The real cap moved on 1 Apr 2022, not 1 Jan — the
Oct-2021 level (elec 208 / gas 40.7) ran through 31 Mar 2022 and then stepped
+54%. An annual blend erases the step, which is the defining feature of the
crisis this simulation exists to reproduce.

R15 obligation for this file: every control here must be provable by mutation.
The mutations that must FIRE are named on each test.
"""
from datetime import date

import pytest

from company.pricing.ofgem_price_cap import (
    _CAP_WINDOWS,
    get_cap_unit_rate_for_date,
    get_cap_unit_rate_gbp_per_mwh,
)


# --- The named defect: the Apr-2022 step must not be smoothed away ---


def test_jan_mar_2022_clamps_against_the_pre_april_cap_not_the_annual_blend():
    """MUTATION (must fire): revert the lookup to
    ``get_cap_unit_rate_gbp_per_mwh(fuel, on_date.year)`` — this sees 305.0.

    The asserted 208.0 comes from Ofgem's published Oct-2021 cap (20.8p/kWh),
    independently corroborated by House of Commons Library CBP-9714. It is NOT
    derived from the lookup under test, so this is not a tautology.
    """
    cap = get_cap_unit_rate_for_date("electricity", date(2022, 2, 15))
    assert cap == pytest.approx(208.0)
    assert cap != pytest.approx(get_cap_unit_rate_gbp_per_mwh("electricity", 2022))


def test_may_2022_clamps_against_the_post_step_cap():
    """MUTATION (must fire): extend the Oct-2021 window past 31 Mar 2022 (the
    calendar-quarter defect ``company/regulatory/price_cap.py`` still carries) —
    this sees 208.0 instead of 283.4, so the window BOUNDARY, not merely the
    year, is proven load-bearing."""
    assert get_cap_unit_rate_for_date("electricity", date(2022, 5, 15)) == pytest.approx(283.4)


def test_the_april_2022_step_is_a_step_not_a_ramp():
    """The +54% cap move happened between two consecutive days. If the schedule
    ever regresses to an averaged/interpolated form this fails.

    MUTATION (must fire): replace both 2022 windows with the annual blend —
    the ratio collapses to 1.0.
    """
    before = get_cap_unit_rate_for_date("electricity", date(2022, 3, 31))
    after = get_cap_unit_rate_for_date("electricity", date(2022, 4, 1))
    assert before == pytest.approx(208.0)
    assert after == pytest.approx(283.4)
    assert after / before > 1.3


def test_gas_steps_at_the_same_boundary_and_is_read_from_the_gas_column():
    """MUTATION (must fire): point the gas branch at the elec column — gas reads
    208.0/283.4 and both assertions fail."""
    assert get_cap_unit_rate_for_date("gas", date(2022, 2, 15)) == pytest.approx(40.7)
    assert get_cap_unit_rate_for_date("gas", date(2022, 5, 15)) == pytest.approx(73.7)


# --- Fail-open / fail-silent guards (R15's three killer patterns) ---


def test_no_cap_before_the_cap_existed():
    assert get_cap_unit_rate_for_date("electricity", date(2018, 12, 31)) is None
    assert get_cap_unit_rate_for_date("gas", date(2016, 6, 1)) is None


def test_first_day_of_the_cap_is_capped():
    """Off-by-one at the very first boundary: 1 Jan 2019 IS capped."""
    assert get_cap_unit_rate_for_date("electricity", date(2019, 1, 1)) is not None


def test_every_day_from_2019_to_2030_returns_a_cap_no_silent_gap():
    """FAIL-OPEN guard. A missing/misordered window would return None for some
    date, which un-caps a resi customer silently.

    MUTATION (must fire): delete any single window from ``_CAP_WINDOWS`` — the
    dates it covered return None (or, past the end, this test's sibling below
    catches the carry-forward) and this fails naming the date.
    """
    d = date(2019, 1, 1)
    while d <= date(2030, 12, 31):
        for fuel in ("electricity", "gas"):
            assert get_cap_unit_rate_for_date(fuel, d) is not None, f"uncapped {fuel} on {d}"
        d = date(d.year + (d.month == 12), (d.month % 12) + 1, 1)


def test_beyond_the_schedule_carries_forward_rather_than_uncapping():
    """The cap is a standing statutory instrument: 'no published level yet' must
    never mean 'no ceiling'.

    MUTATION (must fire): return None past the last window — this fails.
    """
    last = _CAP_WINDOWS[-1]
    assert get_cap_unit_rate_for_date("electricity", date(2031, 6, 1)) == pytest.approx(last["elec"])
    assert get_cap_unit_rate_for_date("gas", date(2031, 6, 1)) == pytest.approx(last["gas"])


def test_unknown_fuel_returns_none():
    assert get_cap_unit_rate_for_date("oil", date(2022, 2, 15)) is None


# --- Schedule integrity (independent of the lookup that reads it) ---


def test_windows_are_contiguous_with_no_gaps_and_no_overlaps():
    """MUTATION (must fire): shift any window's ``to`` by one day — the
    contiguity assertion fails naming that pair."""
    for earlier, later in zip(_CAP_WINDOWS, _CAP_WINDOWS[1:]):
        assert earlier["to"] < later["from"], f"overlap: {earlier['to']} >= {later['from']}"
        assert (later["from"] - earlier["to"]).days == 1, (
            f"gap between {earlier['to']} and {later['from']}"
        )


def test_every_window_carries_both_fuels_and_positive_rates():
    for w in _CAP_WINDOWS:
        assert w["elec"] > 0 and w["gas"] > 0, f"non-positive rate in window from {w['from']}"
        assert w["elec"] > w["gas"], f"elec must exceed gas in £/MWh, window {w['from']}"


def test_the_real_cap_cadence_is_six_monthly_then_quarterly():
    """The schedule must reproduce Ofgem's own cadence change: six-monthly
    (Apr/Oct) to 30 Sep 2022, quarterly from 1 Oct 2022. Keying on calendar
    quarters throughout — the defect in the sibling quarterly table — would make
    every pre-Oct-2022 window ~3 months long and fail this.
    """
    pre = [w for w in _CAP_WINDOWS if w["to"] <= date(2022, 9, 30)]
    post = [w for w in _CAP_WINDOWS if w["from"] >= date(2022, 10, 1)]
    # First window (Jan-Mar 2019) is a short launch window; the rest are 6-monthly.
    for w in pre[1:]:
        assert 150 <= (w["to"] - w["from"]).days <= 200, f"not six-monthly: {w['from']}"
    for w in post:
        assert 80 <= (w["to"] - w["from"]).days <= 100, f"not quarterly: {w['from']}"


def test_epg_binds_below_the_ofgem_cap_where_it_applied():
    """Oct-2022 → Jun-2023: the Energy Price Guarantee, not the Ofgem cap, was
    the ceiling people actually paid (£2,500 typical vs a £4,279 Jan-2023 cap).

    MUTATION (must fire): drop the ``min(ofgem, epg)`` and return the raw Ofgem
    rate — Jan-2023 reads 674.7 instead of 340.0.
    """
    jan_2023 = get_cap_unit_rate_for_date("electricity", date(2023, 2, 1))
    assert jan_2023 == pytest.approx(340.0)
    raw = next(w for w in _CAP_WINDOWS if w["from"] == date(2023, 1, 1))
    assert raw["elec"] == pytest.approx(674.7)
    assert jan_2023 < raw["elec"]


def test_epg_does_not_leak_outside_its_window():
    """The EPG ended 30 Jun 2023. Jul-2023 must read the raw Ofgem cap."""
    assert get_cap_unit_rate_for_date("electricity", date(2023, 8, 1)) == pytest.approx(301.1)


# --- R10 CLASS CLOSURE: no settlement/term clamp may go back to a year key ---


def test_no_settlement_clamp_uses_the_annual_lookup():
    """The defect class is 'a per-period ceiling keyed on a calendar year'. Fixing
    the two known instances is not closure — this fails the whole class.

    Sites that legitimately keep the annual lookup (annual compliance anchors,
    growth mandates, switching advice) are not listed here; their own grain IS a
    year. Sites that clamp a settlement period or a term are.

    MUTATION (must fire): restore ``get_cap_unit_rate_gbp_per_mwh`` at either
    binding site — this fails naming that file.
    """
    from pathlib import Path

    repo = Path(__file__).resolve().parents[3]
    clamp_sites = [
        repo / "simulation" / "hedged_settlement.py",
        repo / "simulation" / "run_phase2b.py",
    ]
    for path in clamp_sites:
        assert path.exists(), f"clamp site moved or renamed: {path}"
        src = path.read_text()
        assert "get_cap_unit_rate_gbp_per_mwh" not in src, (
            f"{path.name} clamps a settlement period/term with the ANNUAL cap "
            f"lookup — use get_cap_unit_rate_for_date (W3_1b)"
        )
        assert "get_cap_unit_rate_for_date" in src, (
            f"{path.name} no longer applies any cap lookup — the clamp was removed, "
            f"not re-keyed"
        )
