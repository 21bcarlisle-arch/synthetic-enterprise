"""Scope 2 emissions intensity from supplied electricity: fuel mix reporting.

SOLE OWNER OF THE ANNUAL UK GRID INTENSITY SERIES (2026-08-14, discharge of
`WORKER_FINDING_THREE_LIVE_GRID_INTENSITY_SERIES_DISAGREE_BY_HALF_2026-08-14.md`, BLOCKING,
lane `F_risk_compliance`).

Three series in this tree claimed to measure the same quantity from the same cited source and
disagreed by up to 55.6% (2024: 196.1 published / 126 / 181). At most one could be right and the
published one was not obviously it. This module is now the ONE place an annual grid intensity may
be declared; `tools/grid_intensity_guard.py` (proved both ways in `tests/tools/test_grid_intensity_guard.py`,
and run on every code commit via the gate's `CONTROL_TESTS`) fails if a second year-keyed
intensity table reappears anywhere under `company/` or `saas/` (R10 — the class, not the instance).

WHY THE PUBLISHED CONSTRUCTION SURVIVED, and not one of the two literal tables:

* It is the only one with a consumer. `docs/reports/ANNUAL_REPORT.md` publishes it as the
  `Grid Intensity` column of the Carbon Emissions Reporting Observatory. The other two had zero
  renderers between them, so keeping either would have silently revalued a published table.
* It is DERIVED and therefore decomposable — mix x factor, both visible — where the other two
  were opaque literals. `EP13_adapter_carbon_intensity` eventually replaces the mix side with a
  real feed; it cannot replace a bare number it cannot take apart.
* The finding made NO claim about which series is correct (no network that tick, no external
  source fetched). So this reconciliation deliberately CHANGES NO PUBLISHED VALUE: it removes
  duplicates, it does not pick a winner on the merits. Naming a true value is EP13's job against
  a named publication, and the basis question below is the director's under R13.

PROVENANCE, and what is NOT verified (R9 labelling):
* `inferred` — the per-fuel factors below are lifecycle (gCO2eq/kWh) medians; the values match
  those commonly published as IPCC AR5 WG3 Annex III. No external source was fetched to confirm
  the edition or vintage. Treat the citation as unverified until EP13 sources it.
* `observed-with-evidence` — the mix percentages are those the annual report has been publishing;
  header text cites "DESNZ/National Grid annual fuel mix data" without a vintage.
* The series is therefore a LIFECYCLE-basis, GENERATION-mix, national annual average. It is NOT
  the DESNZ consumption conversion factor and NOT the NESO operational-CO2 series; those are
  different quantities and would give different numbers legitimately. Anything joining this
  series must state that basis.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


#: Lifecycle emission factors, gCO2eq/kWh generated. See PROVENANCE in the module docstring —
#: `inferred` citation, unverified vintage.
_EMISSION_FACTORS_G_CO2_PER_KWH = {
    'coal': 820.0,
    'gas': 490.0,
    'nuclear': 12.0,
    'wind': 11.0,
    'solar': 41.0,
    'hydro': 24.0,
    'biomass': 230.0,
    'imports': 300.0,
}


@dataclass(frozen=True)
class FuelMixRecord:
    year: int
    coal_pct: float
    gas_pct: float
    nuclear_pct: float
    wind_pct: float
    solar_pct: float
    hydro_pct: float
    biomass_pct: float
    imports_pct: float

    @property
    def total_pct(self) -> float:
        return round(self.coal_pct + self.gas_pct + self.nuclear_pct +
                      self.wind_pct + self.solar_pct + self.hydro_pct +
                      self.biomass_pct + self.imports_pct, 1)

    @property
    def renewable_pct(self) -> float:
        return round(self.wind_pct + self.solar_pct + self.hydro_pct, 1)

    @property
    def low_carbon_pct(self) -> float:
        return round(self.renewable_pct + self.nuclear_pct + self.biomass_pct, 1)

    @property
    def emission_intensity_g_per_kwh(self) -> float:
        intensity = (
            self.coal_pct / 100 * _EMISSION_FACTORS_G_CO2_PER_KWH['coal'] +
            self.gas_pct / 100 * _EMISSION_FACTORS_G_CO2_PER_KWH['gas'] +
            self.nuclear_pct / 100 * _EMISSION_FACTORS_G_CO2_PER_KWH['nuclear'] +
            self.wind_pct / 100 * _EMISSION_FACTORS_G_CO2_PER_KWH['wind'] +
            self.solar_pct / 100 * _EMISSION_FACTORS_G_CO2_PER_KWH['solar'] +
            self.hydro_pct / 100 * _EMISSION_FACTORS_G_CO2_PER_KWH['hydro'] +
            self.biomass_pct / 100 * _EMISSION_FACTORS_G_CO2_PER_KWH['biomass'] +
            self.imports_pct / 100 * _EMISSION_FACTORS_G_CO2_PER_KWH['imports']
        )
        return round(intensity, 1)


#: The UK national generation fuel mix, percent by year. Moved here 2026-08-14 from a local
#: declared INSIDE the function body of `saas/reporting/annual_report.py::_section_carbon_emissions`
#: — values unchanged, so every published figure is byte-identical across the move. This is the
#: single owned mix; a second one under `company/` or `saas/` is a control failure, not a variant.
UK_GRID_FUEL_MIX: Dict[int, 'FuelMixRecord'] = {
    2016: FuelMixRecord(2016, coal_pct=9.0, gas_pct=42.0, nuclear_pct=21.0, wind_pct=11.0, solar_pct=3.0, hydro_pct=2.0, biomass_pct=8.0, imports_pct=4.0),
    2017: FuelMixRecord(2017, coal_pct=7.0, gas_pct=40.0, nuclear_pct=21.0, wind_pct=15.0, solar_pct=3.0, hydro_pct=2.0, biomass_pct=8.0, imports_pct=4.0),
    2018: FuelMixRecord(2018, coal_pct=5.0, gas_pct=39.0, nuclear_pct=20.0, wind_pct=17.0, solar_pct=3.0, hydro_pct=2.0, biomass_pct=9.0, imports_pct=5.0),
    2019: FuelMixRecord(2019, coal_pct=2.0, gas_pct=37.0, nuclear_pct=19.0, wind_pct=20.0, solar_pct=4.0, hydro_pct=2.0, biomass_pct=12.0, imports_pct=4.0),
    2020: FuelMixRecord(2020, coal_pct=1.0, gas_pct=33.0, nuclear_pct=17.0, wind_pct=24.0, solar_pct=4.0, hydro_pct=2.0, biomass_pct=12.0, imports_pct=7.0),
    2021: FuelMixRecord(2021, coal_pct=2.0, gas_pct=36.0, nuclear_pct=17.0, wind_pct=22.0, solar_pct=4.0, hydro_pct=2.0, biomass_pct=11.0, imports_pct=6.0),
    2022: FuelMixRecord(2022, coal_pct=2.0, gas_pct=38.0, nuclear_pct=17.0, wind_pct=26.0, solar_pct=4.0, hydro_pct=2.0, biomass_pct=8.0, imports_pct=3.0),
    2023: FuelMixRecord(2023, coal_pct=1.0, gas_pct=32.0, nuclear_pct=14.0, wind_pct=28.0, solar_pct=5.0, hydro_pct=2.0, biomass_pct=10.0, imports_pct=8.0),
    2024: FuelMixRecord(2024, coal_pct=0.0, gas_pct=29.0, nuclear_pct=14.0, wind_pct=32.0, solar_pct=5.0, hydro_pct=2.0, biomass_pct=11.0, imports_pct=7.0),
    2025: FuelMixRecord(2025, coal_pct=0.0, gas_pct=25.0, nuclear_pct=13.0, wind_pct=36.0, solar_pct=6.0, hydro_pct=3.0, biomass_pct=10.0, imports_pct=7.0),
}

#: The window the mix actually covers. Outside it the accessor CLAMPS to the nearest end and says
#: so via `grid_intensity_is_extrapolated`, rather than inventing a value or reading 0.0 — the
#: fail-open family E5's control C1 names by name.
GRID_INTENSITY_FIRST_YEAR = min(UK_GRID_FUEL_MIX)
GRID_INTENSITY_LAST_YEAR = max(UK_GRID_FUEL_MIX)

#: Scope 1 factor for supplied gas, gCO2e/kWh. Also the published value (the annual report's
#: `Gas CO2 (t)` column), kept identical for the same no-silent-revaluation reason.
GAS_EMISSION_FACTOR_G_CO2E_PER_KWH = 183.0

#: Machine-readable provenance for anything that republishes the series. See the module docstring.
GRID_INTENSITY_PROVENANCE = {
    'quantity': 'UK national annual average grid electricity intensity',
    'unit': 'gCO2eq/kWh',
    'basis': 'lifecycle factors x annual generation mix',
    'source': 'DESNZ/National Grid annual fuel mix data (vintage unstated in tree)',
    'factor_source': 'lifecycle medians matching IPCC AR5 WG3 Annex III (inferred, unverified)',
    'status': 'PROVISIONAL — no external source fetched; EP13_adapter_carbon_intensity owns sourcing',
}


def grid_intensity_g_co2e_per_kwh(year: int) -> float:
    """The ONE annual UK grid intensity in this codebase, gCO2eq/kWh.

    Derived from `UK_GRID_FUEL_MIX` x `_EMISSION_FACTORS_G_CO2_PER_KWH` — never a literal, so a
    caller can always decompose the number it was given. Years outside the covered window clamp
    to the nearest end; `grid_intensity_is_extrapolated(year)` reports that so a caller can refuse
    it rather than have a clamp look like a measurement.
    """
    if year < GRID_INTENSITY_FIRST_YEAR:
        year = GRID_INTENSITY_FIRST_YEAR
    elif year > GRID_INTENSITY_LAST_YEAR:
        year = GRID_INTENSITY_LAST_YEAR
    return UK_GRID_FUEL_MIX[year].emission_intensity_g_per_kwh


def grid_intensity_is_extrapolated(year: int) -> bool:
    """True when `grid_intensity_g_co2e_per_kwh(year)` clamped rather than looked up."""
    return not (GRID_INTENSITY_FIRST_YEAR <= year <= GRID_INTENSITY_LAST_YEAR)


@dataclass(frozen=True)
class CustomerCarbonFootprint:
    customer_id: str
    year: int
    electricity_kwh: float
    gas_kwh: float
    electricity_intensity_g_per_kwh: float

    _GAS_EMISSION_FACTOR_G_PER_KWH = GAS_EMISSION_FACTOR_G_CO2E_PER_KWH

    @property
    def electricity_co2_kg(self) -> float:
        return round(self.electricity_kwh * self.electricity_intensity_g_per_kwh / 1000, 1)

    @property
    def gas_co2_kg(self) -> float:
        return round(self.gas_kwh * self._GAS_EMISSION_FACTOR_G_PER_KWH / 1000, 1)

    @property
    def total_co2_kg(self) -> float:
        return round(self.electricity_co2_kg + self.gas_co2_kg, 1)

    @property
    def total_co2_tonnes(self) -> float:
        return round(self.total_co2_kg / 1000, 3)

    def summary(self) -> dict:
        return {
            'customer_id': self.customer_id,
            'year': self.year,
            'electricity_kwh': self.electricity_kwh,
            'gas_kwh': self.gas_kwh,
            'electricity_co2_kg': self.electricity_co2_kg,
            'gas_co2_kg': self.gas_co2_kg,
            'total_co2_kg': self.total_co2_kg,
            'total_co2_tonnes': self.total_co2_tonnes,
        }


def build_customer_footprint(
    customer_id: str, year: int,
    electricity_kwh: float, gas_kwh: float,
    fuel_mix: FuelMixRecord,
) -> CustomerCarbonFootprint:
    return CustomerCarbonFootprint(
        customer_id=customer_id, year=year,
        electricity_kwh=electricity_kwh, gas_kwh=gas_kwh,
        electricity_intensity_g_per_kwh=fuel_mix.emission_intensity_g_per_kwh,
    )
