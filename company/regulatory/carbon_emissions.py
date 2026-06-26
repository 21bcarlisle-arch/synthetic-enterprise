"""Scope 2 emissions intensity from supplied electricity: fuel mix reporting."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


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


@dataclass(frozen=True)
class CustomerCarbonFootprint:
    customer_id: str
    year: int
    electricity_kwh: float
    gas_kwh: float
    electricity_intensity_g_per_kwh: float

    _GAS_EMISSION_FACTOR_G_PER_KWH = 183.0

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
