"""A household's carbon carries its gas, and the gas factor has one home.

THE DEFECT (2026-10-05, docs/market_research/household_carbon_and_the_measures_that_save_it.md
§3). The only household carbon figure the company published was electricity only: about 15% of a
gas-heated home's carbon on the 2025 grid, and it would have shown a heat pump -- gas off,
electricity up -- as an INCREASE. Two gas factors disagreed in the tree, and one of them
(0.18253) was DESNZ's CO2-only column labelled as CO2e.

Each test is named for the defect it fails on.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from company.carbon.half_hourly_footprint import (
    BILLED,
    GAS_CLOSED,
    NO_GAS_SUPPLY_REASON,
    NO_SUPPLY,
    FootprintUnavailable,
    HouseholdFootprint,
    electricity_leg,
    gas_leg,
    household_change,
)
from company.regulatory.carbon_emissions import (
    DESNZ_NATURAL_GAS_KG_CO2E_PER_KWH_GROSS_CV,
    GAS_EMISSION_FACTOR_G_CO2E_PER_KWH,
    grid_intensity_g_co2e_per_kwh,
)
from company.sustainability.environmental_impact import EnvironmentalImpactRegister

REPO = Path(__file__).resolve().parents[3]

#: DESNZ 2023 natural gas, kWh gross CV: the CO2e column and the CO2-only column beside it.
#: Sourced in the knowledge doc above; the second is the value this file exists to refuse.
DESNZ_2023_CO2E = 0.18293
DESNZ_2023_CO2_ONLY = 0.18253


def _home(year, elec_kwh, gas_kwh, *, gas_closed_on=None):
    return HouseholdFootprint(
        "H", year,
        electricity_leg(year, elec_kwh, 12),
        gas_leg(year, gas_kwh, 0 if gas_closed_on else 12, gas_closed_on)
        if gas_kwh is not None else gas_leg(year, None, 0),
    )


def test_a_gas_heated_households_total_exceeds_its_electricity_by_its_gas_carbon():
    """The electricity-only figure was published as the household's carbon. Ofgem's TDCV-medium
    home (2,700 / 11,500 kWh) in 2024: the total must be electricity PLUS the gas burnt."""
    home = _home(2024, 2_700, 11_500)
    gas_kg = 11_500 * DESNZ_NATURAL_GAS_KG_CO2E_PER_KWH_GROSS_CV[2024]
    elec_kg = 2_700 * grid_intensity_g_co2e_per_kwh(2024) / 1000.0

    assert home.electricity.co2e_kg == pytest.approx(elec_kg, abs=0.01)
    assert home.gas.co2e_kg == pytest.approx(gas_kg, abs=0.01)
    assert home.total_co2e_kg == pytest.approx(elec_kg + gas_kg, abs=0.01)
    assert home.total_co2e_kg - home.electricity.co2e_kg == pytest.approx(gas_kg, abs=0.01)
    assert home.gas.co2e_kg > home.electricity.co2e_kg, (
        "a gas-heated home's gas is the larger leg on every year of the record")


def test_a_closed_gas_account_with_more_electricity_shows_a_net_fall_only_when_the_gas_outweighs_it():
    """The heat-pump case. Gas closed and electricity up is a FALL exactly when the gas no longer
    burnt outweighs the extra electricity's carbon -- and a RISE otherwise. Both branches are
    asserted reachable, so a change that always reports a fall cannot pass."""
    # 2023 -> 2024: two WHOLE published grid years (2025's level is a part year, so it has no
    # annual electricity figure and no change can be taken against it).
    before = _home(2023, 2_700, 11_500)
    after = _home(2024, 2_700 + 3_400, 0.0, gas_closed_on="2023-12-31")
    assert after.gas.status == GAS_CLOSED and "closed 2023-12-31" in after.gas.reason
    change = household_change(before, after)

    assert change["gas_closed"] is True
    assert change["electricity_change_kg"] > 0, "the heat pump's electricity must show as a rise"
    assert change["gas_change_kg"] == pytest.approx(-before.gas.co2e_kg)
    assert change["net_fall"] is True and change["total_change_kg"] < 0

    # The same closure with a tiny gas bill before it: the extra electricity now outweighs it.
    small_gas = _home(2023, 2_700, 500)
    worse = household_change(small_gas, after)
    assert worse["gas_closed"] is True and worse["net_fall"] is False


def test_a_household_with_no_gas_account_shows_gas_as_zero_with_its_reason():
    home = _home(2024, 2_700, None)
    assert home.gas.status == NO_SUPPLY
    assert home.gas.co2e_kg == 0.0 and home.gas.reason == NO_GAS_SUPPLY_REASON
    assert home.total_co2e_kg == home.electricity.co2e_kg


def test_a_year_with_no_established_gas_factor_has_no_gas_kg_and_no_total():
    """2022's DESNZ files were not parsed. A neighbouring year's factor would be read as 2022's."""
    home = _home(2022, 2_700, 11_500)
    assert home.gas.status == BILLED and home.gas.kwh == 11_500
    assert home.gas.co2e_kg is None and "2022" in home.gas.reason
    with pytest.raises(FootprintUnavailable, match="gas leg has no figure"):
        home.total_co2e_kg


def test_a_part_year_is_never_compared_with_a_whole_one():
    whole = _home(2024, 2_700, 11_500)
    part = HouseholdFootprint("H", 2025, electricity_leg(2025, 900, 4), gas_leg(2025, 4_000, 4))
    with pytest.raises(FootprintUnavailable, match="part year"):
        household_change(whole, part)


def _numeric_literals(path: Path) -> list[float]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return [node.value for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, float)]


def test_exactly_one_gas_factor_is_used_and_it_is_the_co2e_one():
    """MUTATION (must fire): put DESNZ's CO2-only 0.18253 back -- in the owner's 2023 entry, or as
    `_GAS_EMISSION_FACTOR` in company/sustainability/environmental_impact.py."""
    assert DESNZ_NATURAL_GAS_KG_CO2E_PER_KWH_GROSS_CV[2023] == DESNZ_2023_CO2E, (
        "the owner's 2023 gas factor is not DESNZ's CO2e figure")
    assert gas_leg(2023, 1_000, 12).co2e_kg == pytest.approx(1_000 * DESNZ_2023_CO2E)

    # The year-less published figure is DERIVED from the same table, not a second number.
    latest = DESNZ_NATURAL_GAS_KG_CO2E_PER_KWH_GROSS_CV[max(DESNZ_NATURAL_GAS_KG_CO2E_PER_KWH_GROSS_CV)]
    assert GAS_EMISSION_FACTOR_G_CO2E_PER_KWH == round(1000 * latest)

    # The SECR register's gas default is that one figure.
    record = EnvironmentalImpactRegister().record_gas_scope3(2023, 1_000)
    assert record.emission_factor_kgco2e_per_kwh == pytest.approx(GAS_EMISSION_FACTOR_G_CO2E_PER_KWH / 1000)

    # And the CO2-only value is not a number anywhere in the company's code (comments may name it).
    offenders = [
        str(p.relative_to(REPO))
        for package in ("company", "saas")
        for p in sorted((REPO / package).rglob("*.py"))
        if DESNZ_2023_CO2_ONLY in _numeric_literals(p)
    ]
    assert not offenders, f"DESNZ's CO2-only gas factor is a live number in: {offenders}"
