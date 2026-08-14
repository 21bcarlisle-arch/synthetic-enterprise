"""Carbon Intensity Register (Phase FD).

Energy suppliers must report the fuel mix and carbon intensity of electricity
supplied to customers (Electricity (Disclosure) Regulations 1999; amended).

Key disclosures:
- Annual Fuel Mix Disclosure (FMD): % from each source (gas/coal/nuclear/wind/etc.)
- Carbon Intensity: gCO2eq/kWh (blended from grid mix purchased)
- Renewables percentage for green tariff customers
- Companies with Science Based Targets (SBTi) track Scope 2 emissions

Data sources (publicly observable):
- NESO Annual Fuel Mix report
- Elexon BSC: supplier licence conditions require FMD
- Grid average intensity: NOT declared here. Single owner
  `company.regulatory.carbon_emissions.grid_intensity_g_co2e_per_kwh`, lifecycle basis. This
  docstring previously cited "DESNZ (formerly BEIS) ~196 gCO2/kWh 2023 (down from 350g 2016)",
  which described the local table deleted 2026-08-14; no external source was ever fetched for it.
- Renewable Energy Guarantees of Origin (REGO) for green tariff claims

Carbon intensity has fallen ~44% from 2016 to 2023 due to:
- Coal phase-out (last coal plant 2024)
- Wind capacity growth (offshore doubled)
- Solar + BESS growth
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

from company.regulatory.carbon_emissions import grid_intensity_g_co2e_per_kwh


class FuelSource(str, Enum):
    NATURAL_GAS = "natural_gas"
    COAL = "coal"
    NUCLEAR = "nuclear"
    WIND_ONSHORE = "wind_onshore"
    WIND_OFFSHORE = "wind_offshore"
    SOLAR = "solar"
    HYDRO = "hydro"
    BIOMASS = "biomass"
    IMPORTS = "imports"
    OTHER = "other"


_CARBON_INTENSITY_G_CO2_PER_KWH: Dict[FuelSource, float] = {
    FuelSource.NATURAL_GAS: 394.0,
    FuelSource.COAL: 820.0,
    FuelSource.NUCLEAR: 12.0,
    FuelSource.WIND_ONSHORE: 11.0,
    FuelSource.WIND_OFFSHORE: 12.0,
    FuelSource.SOLAR: 41.0,
    FuelSource.HYDRO: 24.0,
    FuelSource.BIOMASS: 230.0,
    FuelSource.IMPORTS: 300.0,     # EU average (conservative)
    FuelSource.OTHER: 200.0,
}

# The grid average this register compares a supplier mix AGAINST is not declared here. It used to
# be `_GRID_AVERAGE_INTENSITY` (350.0 in 2016 falling to 165.0 in 2025) — the highest of three
# mutually inconsistent series in the tree, with zero non-test importers. Deleted 2026-08-14
# discharging WORKER_FINDING_THREE_LIVE_GRID_INTENSITY_SERIES_DISAGREE_BY_HALF_2026-08-14.md.
# Single owner: company.regulatory.carbon_emissions. See the docstring caveat below.


@dataclass(frozen=True)
class FuelMixSnapshot:
    year: int
    fuel_mix: Dict[FuelSource, float]     # FuelSource -> fraction (sums to 1.0)
    total_kwh_supplied: float
    has_rego_backing: bool = False        # green tariff REGO certificates

    @property
    def carbon_intensity_g_co2_per_kwh(self) -> float:
        return sum(
            fraction * _CARBON_INTENSITY_G_CO2_PER_KWH[source]
            for source, fraction in self.fuel_mix.items()
        )

    @property
    def total_co2_tonnes(self) -> float:
        return self.total_kwh_supplied * self.carbon_intensity_g_co2_per_kwh / 1e6

    @property
    def renewables_fraction(self) -> float:
        renewable_sources = {
            FuelSource.WIND_ONSHORE, FuelSource.WIND_OFFSHORE,
            FuelSource.SOLAR, FuelSource.HYDRO,
        }
        return sum(
            v for k, v in self.fuel_mix.items() if k in renewable_sources
        )

    @property
    def vs_grid_average(self) -> float:
        """This supplier mix minus the national grid average, gCO2/kWh.

        NOTE the basis mismatch, recorded not hidden: the grid side is the owner's lifecycle
        series, while this snapshot's own side blends `_CARBON_INTENSITY_G_CO2_PER_KWH`, a second
        per-fuel table whose gas figure (394.0) is a direct-combustion number sitting beside
        lifecycle values for nuclear and wind. Reconciling the PER-FUEL tables is a separate,
        larger class than the annual series this discharge closed, and is filed as its own finding.
        """
        return self.carbon_intensity_g_co2_per_kwh - grid_intensity_g_co2e_per_kwh(self.year)

    def fuel_mix_summary(self) -> str:
        return (
            "FuelMix " + str(self.year) + ": "
            + str(round(self.carbon_intensity_g_co2_per_kwh, 1)) + " gCO2/kWh "
            + "renewables=" + str(round(self.renewables_fraction * 100, 1)) + "% "
            + "CO2=" + str(round(self.total_co2_tonnes / 1000, 1)) + "ktCO2."
        )


class CarbonIntensityRegister:

    def __init__(self) -> None:
        self._snapshots: List[FuelMixSnapshot] = []

    def record(self, snapshot: FuelMixSnapshot) -> FuelMixSnapshot:
        self._snapshots.append(snapshot)
        return snapshot

    def snapshot_for_year(self, year: int) -> Optional[FuelMixSnapshot]:
        matching = [s for s in self._snapshots if s.year == year]
        return matching[0] if matching else None

    def intensity_trend(self) -> str:
        sorted_snaps = sorted(self._snapshots, key=lambda s: s.year)
        if len(sorted_snaps) < 2:
            return "insufficient_data"
        first = sorted_snaps[0].carbon_intensity_g_co2_per_kwh
        last = sorted_snaps[-1].carbon_intensity_g_co2_per_kwh
        delta = last - first
        if delta < -10:
            return "improving"
        if delta > 10:
            return "worsening"
        return "stable"

    def total_co2_tonnes_all_years(self) -> float:
        return sum(s.total_co2_tonnes for s in self._snapshots)

    def avg_renewables_fraction(self) -> float:
        if not self._snapshots:
            return 0.0
        return sum(s.renewables_fraction for s in self._snapshots) / len(self._snapshots)

    def carbon_register_summary(self) -> str:
        n = len(self._snapshots)
        if n == 0:
            return "CarbonIntensityRegister: no data."
        trend = self.intensity_trend()
        total_co2 = self.total_co2_tonnes_all_years()
        avg_ren = self.avg_renewables_fraction()
        return (
            "Carbon Intensity Register: " + str(n) + " years. "
            "Trend: " + trend + ". "
            "Total CO2: " + str(round(total_co2 / 1000, 1)) + "ktCO2. "
            "Avg renewables: " + str(round(avg_ren * 100, 1)) + "%."
        )
