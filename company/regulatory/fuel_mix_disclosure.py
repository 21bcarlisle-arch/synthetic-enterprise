"""Fuel Mix Disclosure Book — SLC 21C / REGO annual disclosure.

All UK electricity supply licence holders must publish an annual Fuel Mix
Disclosure (FMD) statement showing the percentage of electricity supplied
from each generation technology.

Regulatory basis:
- SLC 21C: Annual fuel mix disclosure to customers
- Renewables Obligation (RO): REGO certificates prove renewable origin
- DESNZ (previously BEIS) defines the residual fuel mix — the 'default' mix
  for suppliers who don't hold REGOs, based on UK generation not matched
  to certificates. Typically contains ~70% gas, ~15% nuclear, ~10% renewable.

UK residual fuel mix (approx 2022): gas 56%, nuclear 24%, renewables 13%,
imports 4%, coal 3%.

A "green" tariff supplier needs to hold 1 REGO certificate per MWh supplied.
Without REGOs, the default residual mix applies (high carbon content).

This module tracks REGO certificate holdings, customer-facing disclosure,
and the carbon intensity implied by the fuel mix (gCO₂e/kWh).

Epistemic constraint: the company knows its REGO certificate holdings
(purchased or received), not the actual generation mix of the national grid.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class FuelSource(str, Enum):
    WIND_ONSHORE = "wind_onshore"
    WIND_OFFSHORE = "wind_offshore"
    SOLAR = "solar"
    HYDRO = "hydro"
    BIOMASS = "biomass"
    NUCLEAR = "nuclear"
    GAS_CCGT = "gas_ccgt"
    GAS_OCGT = "gas_ocgt"
    COAL = "coal"
    OTHER = "other"
    RESIDUAL = "residual"   # Default UK mix for unmatched volume


# Carbon intensity in gCO₂e/kWh (UK DESNZ values, ~2022 basis)
_CARBON_INTENSITY: dict[FuelSource, float] = {
    FuelSource.WIND_ONSHORE: 7.0,
    FuelSource.WIND_OFFSHORE: 9.0,
    FuelSource.SOLAR: 33.0,
    FuelSource.HYDRO: 4.0,
    FuelSource.BIOMASS: 120.0,
    FuelSource.NUCLEAR: 12.0,
    FuelSource.GAS_CCGT: 394.0,
    FuelSource.GAS_OCGT: 610.0,
    FuelSource.COAL: 820.0,
    FuelSource.OTHER: 350.0,
    FuelSource.RESIDUAL: 280.0,  # UK residual mix average (DESNZ 2022)
}

# Whether the source qualifies as "renewable" for REGO purposes
_IS_RENEWABLE: dict[FuelSource, bool] = {
    FuelSource.WIND_ONSHORE: True,
    FuelSource.WIND_OFFSHORE: True,
    FuelSource.SOLAR: True,
    FuelSource.HYDRO: True,
    FuelSource.BIOMASS: True,
    FuelSource.NUCLEAR: False,
    FuelSource.GAS_CCGT: False,
    FuelSource.GAS_OCGT: False,
    FuelSource.COAL: False,
    FuelSource.OTHER: False,
    FuelSource.RESIDUAL: False,
}


@dataclass(frozen=True)
class FuelMixComponent:
    source: FuelSource
    fraction: float   # 0.0-1.0

    @property
    def carbon_intensity_gco2_per_kwh(self) -> float:
        return _CARBON_INTENSITY[self.source]

    @property
    def is_renewable(self) -> bool:
        return _IS_RENEWABLE[self.source]

    @property
    def weighted_carbon(self) -> float:
        return self.fraction * self.carbon_intensity_gco2_per_kwh


@dataclass(frozen=True)
class FuelMixDisclosure:
    disclosure_year: int
    total_supply_mwh: float
    components: tuple[FuelMixComponent, ...]
    rego_certificates_held: int   # Each REGO = 1 MWh renewable

    @property
    def renewable_fraction(self) -> float:
        return sum(c.fraction for c in self.components if c.is_renewable)

    @property
    def carbon_intensity_gco2_per_kwh(self) -> float:
        """Weighted average carbon intensity of the disclosed fuel mix."""
        return sum(c.weighted_carbon for c in self.components)

    @property
    def rego_coverage_fraction(self) -> float:
        """REGO certificates as fraction of total supply (1.0 = fully matched)."""
        if self.total_supply_mwh <= 0:
            return 0.0
        return self.rego_certificates_held / self.total_supply_mwh

    @property
    def is_fully_rego_matched(self) -> bool:
        """True if supplier holds ≥1 REGO per MWh supplied (green tariff eligible)."""
        return self.rego_coverage_fraction >= 1.0

    @property
    def unmatched_volume_mwh(self) -> float:
        """Supply volume not backed by REGOs — defaults to residual fuel mix."""
        backed = min(self.rego_certificates_held, self.total_supply_mwh)
        return max(0.0, self.total_supply_mwh - backed)


class FuelMixDisclosureBook:
    """Tracks annual fuel mix disclosures and REGO certificate holdings."""

    # UK residual mix (DESNZ 2022 benchmark)
    RESIDUAL_MIX: tuple[FuelMixComponent, ...] = (
        FuelMixComponent(FuelSource.GAS_CCGT, 0.56),
        FuelMixComponent(FuelSource.NUCLEAR, 0.24),
        FuelMixComponent(FuelSource.WIND_ONSHORE, 0.10),
        FuelMixComponent(FuelSource.OTHER, 0.06),
        FuelMixComponent(FuelSource.COAL, 0.04),
    )

    def __init__(self) -> None:
        self._disclosures: list[FuelMixDisclosure] = []

    def record_disclosure(
        self,
        year: int,
        total_supply_mwh: float,
        components: list[tuple[FuelSource, float]],  # (source, fraction) list
        rego_certificates_held: int,
    ) -> FuelMixDisclosure:
        disclosure = FuelMixDisclosure(
            disclosure_year=year,
            total_supply_mwh=total_supply_mwh,
            components=tuple(FuelMixComponent(src, frac) for src, frac in components),
            rego_certificates_held=rego_certificates_held,
        )
        self._disclosures.append(disclosure)
        return disclosure

    def disclosure_for_year(self, year: int) -> FuelMixDisclosure | None:
        return next((d for d in self._disclosures if d.disclosure_year == year), None)

    @property
    def latest_disclosure(self) -> FuelMixDisclosure | None:
        if not self._disclosures:
            return None
        return max(self._disclosures, key=lambda d: d.disclosure_year)

    @property
    def fully_matched_years(self) -> list[int]:
        return [d.disclosure_year for d in self._disclosures if d.is_fully_rego_matched]

    def carbon_trend(self) -> dict[int, float]:
        """Carbon intensity by year."""
        return {d.disclosure_year: d.carbon_intensity_gco2_per_kwh for d in sorted(self._disclosures, key=lambda x: x.disclosure_year)}

    def fmd_summary(self) -> str:
        if not self._disclosures:
            return "Fuel Mix Disclosure Book — no disclosures recorded"
        latest = self.latest_disclosure
        lines = [
            "Fuel Mix Disclosure Book (SLC 21C)",
            "Years on record: {} | Latest: {}".format(len(self._disclosures), latest.disclosure_year),
            "Latest renewable: {:.1f}% | Carbon: {:.0f} gCO₂e/kWh".format(
                latest.renewable_fraction * 100,
                latest.carbon_intensity_gco2_per_kwh,
            ),
            "REGO coverage: {:.1f}% | Fully matched: {}".format(
                latest.rego_coverage_fraction * 100,
                latest.is_fully_rego_matched,
            ),
        ]
        return chr(10).join(lines)
