# ARCHIVED LEGS of tests/company/regulatory/test_carbon_emissions_single_series.py (archive increment 3b). The tests here reach a module
# under archive/unhooked_supplier/; the live legs stay at tests/company/regulatory/test_carbon_emissions_single_series.py.
"""The company's ONE annual grid intensity is NESO's published level, read from the feed.

THE DEFECT (2026-10-05). `grid_intensity_g_co2e_per_kwh(year)` was `UK_GRID_FUEL_MIX` x lifecycle
factors -- an undated hand table -- and read 196.1 gCO2/kWh for 2024 against NESO's published
133.1, while the half-hourly SHAPE the company multiplies it by was already NESO's. Since then
`tools/generate_grid_intensity_feed.py` publishes each year's demand-weighted mean beside the
shape (`annual_level`), and the owner reads that.

The 2026-08-14 version of this file pinned the hand-table values as "unchanged by the
reconciliation". That pin was correct for a de-duplication that fetched no source, and it is
exactly the control that has to invert now a source exists: the mutation below puts the hand
table back and must red here.

MUTATION (must fire): in `carbon_emissions.grid_intensity_g_co2e_per_kwh`, return
`UK_GRID_FUEL_MIX[year].emission_intensity_g_per_kwh` (clamped to the table's window, as it was)
-> `test_the_companys_annual_level_is_the_feeds_published_mean` and
`test_a_year_the_feed_does_not_cover_returns_none_with_a_reason_not_a_clamp` red.
"""

from __future__ import annotations

import json

import pytest

from company.billing.carbon_footprint import electricity_intensity, estimate_carbon
from company.regulatory import carbon_emissions as ce
from company.regulatory.carbon_emissions import (
    GAS_EMISSION_FACTOR_G_CO2E_PER_KWH,
    GRID_INTENSITY_FEED,
    GRID_INTENSITY_PROVENANCE,
    UK_GRID_FUEL_MIX,
    grid_intensity_g_co2e_per_kwh,
    grid_intensity_level,
    grid_intensity_unavailable_reason,
)


def _published() -> dict:
    return json.loads(GRID_INTENSITY_FEED.read_text(encoding="utf-8"))["annual_level"]["by_year"]


def _write_feed(tmp_path, by_year: dict):
    path = tmp_path / "grid_intensity_feed.json"
    path.write_text(json.dumps({"annual_level": {"by_year": by_year}}))
    return path


# --------------------------------------------------------------------------- #
# The level is the published one                                               #
# --------------------------------------------------------------------------- #







# --------------------------------------------------------------------------- #
# Coverage: None with a reason, never a clamp                                  #
# --------------------------------------------------------------------------- #







# --------------------------------------------------------------------------- #
# The mix stays, for decomposition only                                        #
# --------------------------------------------------------------------------- #









# --------------------------------------------------------------------------- #
# The readers                                                                  #
# --------------------------------------------------------------------------- #

def test_the_two_deleted_series_are_gone_from_their_old_homes():
    import company.billing.carbon_footprint as footprint
    import company.sustainability.carbon_intensity_register as register

    assert not hasattr(footprint, "_ELECTRICITY_INTENSITY_G_CO2E_PER_KWH")
    assert not hasattr(register, "_GRID_AVERAGE_INTENSITY")






def _rendered():
    from saas.reporting.annual_report import _section_carbon_emissions

    accounts = {str(y): {"income_statement": {"revenue_gbp": 1_000_000.0}} for y in UK_GRID_FUEL_MIX}
    return _section_carbon_emissions({"management_accounts": accounts})






def test_the_register_compares_against_the_published_level_and_refuses_without_one():
    from company.sustainability.carbon_intensity_register import FuelMixSnapshot, FuelSource

    mix = {FuelSource.NATURAL_GAS: 1.0}
    whole = FuelMixSnapshot(year=2024, fuel_mix=mix, total_kwh_supplied=1.0)
    assert whole.vs_grid_average == pytest.approx(394.0 - grid_intensity_g_co2e_per_kwh(2024))
    assert FuelMixSnapshot(year=2030, fuel_mix=mix, total_kwh_supplied=1.0).vs_grid_average is None
