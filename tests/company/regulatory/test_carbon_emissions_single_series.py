"""The reconciliation must not have revalued anything published (2026-08-14).

Discharging `WORKER_FINDING_THREE_LIVE_GRID_INTENSITY_SERIES_DISAGREE_BY_HALF_2026-08-14.md`
(BLOCKING, `F_risk_compliance`) meant deleting two of three grid-intensity series. The finding
explicitly made NO claim about which was correct — no network that tick, no external source
fetched — so the repair had to be a pure de-duplication, not a pick-the-winner.

That is the thing this file pins. The ten values below were MEASURED at the pre-repair HEAD by
executing the shipped code (the published column is a blend, not a table lookup) and are recorded
verbatim in the finding's own table. If a future change to the mix, the factors or the accessor
moves any of them, this goes red and whoever moved it owes a sourced reason — which is exactly
what the class control (`tools/grid_intensity_guard.py`) cannot say for itself: it enforces that
there is ONE series, never that the one is right.

The R11 counterpart lives in `docs/reports/ANNUAL_REPORT.md`, whose `Grid Intensity` column is
these same numbers rendered.
"""

from __future__ import annotations

import pytest

from company.billing.carbon_footprint import electricity_intensity
from company.regulatory.carbon_emissions import (
    GAS_EMISSION_FACTOR_G_CO2E_PER_KWH,
    GRID_INTENSITY_FIRST_YEAR,
    GRID_INTENSITY_LAST_YEAR,
    GRID_INTENSITY_PROVENANCE,
    UK_GRID_FUEL_MIX,
    grid_intensity_g_co2e_per_kwh,
    grid_intensity_is_extrapolated,
)

#: gCO2eq/kWh, as published in the Carbon Emissions Reporting Observatory before the repair.
PUBLISHED_SERIES = {
    2016: 315.4, 2017: 289.7, 2018: 273.8, 2019: 243.9, 2020: 225.3,
    2021: 242.7, 2022: 237.0, 2023: 219.3, 2024: 196.1, 2025: 175.2,
}


@pytest.mark.parametrize("year,expected", sorted(PUBLISHED_SERIES.items()))
def test_the_published_value_is_unchanged_by_the_reconciliation(year, expected):
    assert grid_intensity_g_co2e_per_kwh(year) == pytest.approx(expected, abs=0.05)


def test_the_published_gas_factor_is_unchanged():
    """0.18316 kg/kWh also existed in the tree; the PUBLISHED 183.0 g/kWh is what survived."""
    assert GAS_EMISSION_FACTOR_G_CO2E_PER_KWH == 183.0


def test_the_window_is_the_mix_it_actually_has():
    assert GRID_INTENSITY_FIRST_YEAR == min(UK_GRID_FUEL_MIX) == 2016
    assert GRID_INTENSITY_LAST_YEAR == max(UK_GRID_FUEL_MIX) == 2025
    assert sorted(UK_GRID_FUEL_MIX) == list(range(2016, 2026))


def test_every_mix_year_sums_to_one_hundred_percent():
    off = {y: r.total_pct for y, r in UK_GRID_FUEL_MIX.items() if abs(r.total_pct - 100.0) > 0.05}
    assert not off, f"mix years that do not sum to 100%: {off}"


def test_the_series_is_derived_not_a_literal():
    """Decomposability is the reason this construction survived and the two literals did not."""
    for year, expected in PUBLISHED_SERIES.items():
        assert UK_GRID_FUEL_MIX[year].emission_intensity_g_per_kwh == pytest.approx(expected, abs=0.05)


def test_out_of_window_clamps_and_admits_it():
    """A clamp that cannot be distinguished from a measurement is the fail-open shape E5 names."""
    assert grid_intensity_g_co2e_per_kwh(2010) == grid_intensity_g_co2e_per_kwh(2016)
    assert grid_intensity_g_co2e_per_kwh(2030) == grid_intensity_g_co2e_per_kwh(2025)
    assert grid_intensity_is_extrapolated(2010) is True
    assert grid_intensity_is_extrapolated(2030) is True
    assert grid_intensity_is_extrapolated(2020) is False


def test_the_provenance_says_it_is_unverified():
    """R9: the citation is `inferred`. A block that quietly claimed a source would be worse."""
    assert "PROVISIONAL" in GRID_INTENSITY_PROVENANCE["status"]
    assert GRID_INTENSITY_PROVENANCE["unit"] == "gCO2eq/kWh"
    assert "lifecycle" in GRID_INTENSITY_PROVENANCE["basis"]


def test_the_two_deleted_series_are_gone_from_their_old_homes():
    """Named directly, so a revert of the repair reds here as well as in the class guard."""
    import company.billing.carbon_footprint as footprint
    import company.sustainability.carbon_intensity_register as register

    assert not hasattr(footprint, "_ELECTRICITY_INTENSITY_G_CO2E_PER_KWH")
    assert not hasattr(register, "_GRID_AVERAGE_INTENSITY")


def test_the_surviving_consumers_all_read_the_owner():
    """The old tables disagreed with the published one by up to 55.6%. Now they cannot."""
    for year in PUBLISHED_SERIES:
        assert electricity_intensity(year) == grid_intensity_g_co2e_per_kwh(year)


def test_the_annual_report_section_uses_the_owned_mix():
    """The published section imported a LOCAL copy; that local is what made the split invisible."""
    import inspect

    from saas.reporting import annual_report

    source = inspect.getsource(annual_report._section_carbon_emissions)
    assert "UK_GRID_FUEL_MIX as _UK_FUEL_MIX" in source
    assert "FuelMixRecord(2016" not in source, "the local mix copy is back"


def test_the_sections_closing_sentence_agrees_with_its_own_table():
    """It used to say "2016 ~290g/kWh ... (40% reduction)" directly under a table reading 315
    and falling 44% — a third copy of the series, in prose, contradicting the rows above it."""
    from saas.reporting.annual_report import _section_carbon_emissions

    accounts = {str(y): {"income_statement": {"revenue_gbp": 1_000_000.0}} for y in PUBLISHED_SERIES}
    rendered = _section_carbon_emissions({"management_accounts": accounts})
    summary = rendered.splitlines()[-1]

    first, last = min(PUBLISHED_SERIES), max(PUBLISHED_SERIES)
    fall = round((1.0 - PUBLISHED_SERIES[last] / PUBLISHED_SERIES[first]) * 100.0)
    assert f"{first} {PUBLISHED_SERIES[first]:.0f}g/kWh" in summary, summary
    assert f"{last} {PUBLISHED_SERIES[last]:.0f}g/kWh" in summary, summary
    assert f"({fall}% reduction)" in summary, summary
    first_row = next(ln for ln in rendered.splitlines() if ln.startswith(f"| {first} |"))
    assert f"{PUBLISHED_SERIES[first]:.0f}g/kWh" in first_row, first_row
