# ARCHIVED LEGS of tests/company/carbon/test_household_carbon_has_a_gas_leg.py (archive increment 3b). The tests here reach a module
# under archive/unhooked_supplier/; the live legs stay at tests/company/carbon/test_household_carbon_has_a_gas_leg.py.
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
    ACCOUNT_CLOSED,
    BILLED,
    CLOSURE_CAUSES,
    GAS_CLOSED,
    GAS_ELSEWHERE_REASON,
    NO_GAS_SUPPLY_REASON,
    NO_SUPPLY,
    REMOVED,
    SWITCHED_AWAY,
    UNKNOWN,
    FootprintUnavailable,
    HouseholdFootprint,
    electricity_leg,
    gas_closure_cause,
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


def _home(year, elec_kwh, gas_kwh, *, gas_closed_on=None, cause=UNKNOWN):
    return HouseholdFootprint(
        "H", year,
        electricity_leg(year, elec_kwh, 12),
        gas_leg(year, gas_kwh, 0 if gas_closed_on else 12, gas_closed_on, cause)
        if gas_kwh is not None else gas_leg(year, None, 0),
    )






# The Q5 harness household (docs/market_research/practitioner_questions_as_assumption_toggles.md):
# 3,000 kWh of electricity and 11,500 kWh of gas, electricity unchanged after the gas leaves us.
def _moved_gas_elsewhere(cause):
    before = _home(2023, 3_000, 11_500)
    after = _home(2024, 3_000, 0.0, gas_closed_on="2023-12-31", cause=cause)
    return before, after
















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


