"""Environmental Impact Register — Scope 3 downstream gas emissions.

UK suppliers with >250 employees or >£36M turnover must report under
SECR (Streamlined Energy and Carbon Reporting) Regulations 2018.

A gas supplier's Scope 3 (Category 11 — Use of Sold Products) emissions
arise from customers burning the gas they supply. For an electricity
supplier, Scope 2 market-based emissions depend on the fuel mix
(tracked via FuelMixDisclosureBook, Phase CL).

DEFRA emission factors (kgCO₂e per kWh):
- Natural gas (domestic/SME consumption): 0.18253 kgCO₂e/kWh (2023)
- Note: this is lower than combustion-only (0.2037) because it includes
  GHG intensity adjustments post-2021 under the UK ETS reporting method

For electricity: market-based emissions use REGO-backed fuel mix
(zero for REGO-matched volume); location-based uses national grid average.

This module tracks the annual Scope 3 gas emissions from customer
consumption and estimates electricity Scope 2 (market-based and
location-based) for the company's own operations.

Epistemic: the company knows what gas/electricity it bills customers
for. It does NOT see the simulation's actual dispatch or generation data.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


# DEFRA 2023 emission factors (kgCO₂e/kWh)
_GAS_EMISSION_FACTOR = 0.18253    # natural gas
_GRID_ELECTRICITY_FACTOR = 0.2104  # UK national grid 2023 location-based
_REGO_ELECTRICITY_FACTOR = 0.0    # REGO-matched = zero market-based emissions


class EmissionScope(str, Enum):
    SCOPE_1 = "scope_1"    # Direct (e.g. company vehicles, boilers)
    SCOPE_2_LOCATION = "scope_2_location"  # Purchased electricity (grid avg)
    SCOPE_2_MARKET = "scope_2_market"    # Purchased electricity (REGO-based)
    SCOPE_3_DOWNSTREAM = "scope_3_downstream"  # Customer use of sold gas/electricity


@dataclass(frozen=True)
class EmissionRecord:
    year: int
    scope: EmissionScope
    commodity: str           # "gas" or "electricity"
    consumption_kwh: float
    emission_factor_kgco2e_per_kwh: float

    @property
    def emissions_kgco2e(self) -> float:
        return self.consumption_kwh * self.emission_factor_kgco2e_per_kwh

    @property
    def emissions_tco2e(self) -> float:
        return self.emissions_kgco2e / 1000

    @property
    def emissions_mtco2e(self) -> float:
        """Megatonnes CO₂e."""
        return self.emissions_tco2e / 1_000_000


class EnvironmentalImpactRegister:
    """Tracks annual scope emissions for SECR compliance and TCFD disclosure."""

    def __init__(self) -> None:
        self._records: list[EmissionRecord] = []

    def record_gas_scope3(
        self,
        year: int,
        customer_gas_kwh: float,
        factor: float = _GAS_EMISSION_FACTOR,
    ) -> EmissionRecord:
        record = EmissionRecord(
            year=year,
            scope=EmissionScope.SCOPE_3_DOWNSTREAM,
            commodity="gas",
            consumption_kwh=customer_gas_kwh,
            emission_factor_kgco2e_per_kwh=factor,
        )
        self._records.append(record)
        return record

    def record_electricity_scope3(
        self,
        year: int,
        customer_elec_kwh: float,
        rego_coverage_fraction: float = 0.0,
    ) -> tuple[EmissionRecord, EmissionRecord]:
        """Record electricity Scope 3 emissions (market-based and location-based)."""
        # Market-based: zero for REGO-matched, grid factor for unmatched
        unmatched_fraction = max(0.0, 1.0 - rego_coverage_fraction)
        market_factor = _REGO_ELECTRICITY_FACTOR * rego_coverage_fraction + _GRID_ELECTRICITY_FACTOR * unmatched_fraction

        location_rec = EmissionRecord(
            year=year,
            scope=EmissionScope.SCOPE_3_DOWNSTREAM,
            commodity="electricity_location",
            consumption_kwh=customer_elec_kwh,
            emission_factor_kgco2e_per_kwh=_GRID_ELECTRICITY_FACTOR,
        )
        market_rec = EmissionRecord(
            year=year,
            scope=EmissionScope.SCOPE_3_DOWNSTREAM,
            commodity="electricity_market",
            consumption_kwh=customer_elec_kwh,
            emission_factor_kgco2e_per_kwh=market_factor,
        )
        self._records.extend([location_rec, market_rec])
        return location_rec, market_rec

    @property
    def all_records(self) -> list[EmissionRecord]:
        return list(self._records)

    def records_for_year(self, year: int) -> list[EmissionRecord]:
        return [r for r in self._records if r.year == year]

    def total_scope3_tco2e(self, year: int) -> float:
        """Total Scope 3 (market-based) tCO₂e for a given year."""
        scope3 = [r for r in self.records_for_year(year)
                  if r.scope == EmissionScope.SCOPE_3_DOWNSTREAM
                  and r.commodity not in ("electricity_location",)]  # exclude location-based
        return sum(r.emissions_tco2e for r in scope3)

    def emissions_by_year(self) -> dict[int, float]:
        """Total market-based Scope 3 tCO₂e by year."""
        result: dict[int, float] = {}
        for r in self._records:
            if r.commodity == "electricity_location":
                continue
            result[r.year] = result.get(r.year, 0.0) + r.emissions_tco2e
        return result

    def peak_emission_year(self) -> int | None:
        eb = self.emissions_by_year()
        if not eb:
            return None
        return max(eb, key=lambda y: eb[y])

    def environmental_summary(self) -> str:
        eb = self.emissions_by_year()
        if not eb:
            return "Environmental Impact Register — no data"
        total = sum(eb.values())
        peak_yr = self.peak_emission_year()
        lines = [
            "Environmental Impact Register (SECR / TCFD)",
            "Years on record: {} | Total Scope 3: {:.1f} tCO₂e".format(len(eb), total),
            "Peak year: {} at {:.1f} tCO₂e".format(peak_yr, eb.get(peak_yr, 0)),
        ]
        return chr(10).join(lines)
