from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class FuelPovertyBand(str, Enum):
    NOT_FUEL_POOR = 'not_fuel_poor'
    BORDERLINE = 'borderline'          # 8-10% of income on energy
    FUEL_POOR = 'fuel_poor'             # >10% of income (old UK definition)
    SEVERELY_FUEL_POOR = 'severely_fuel_poor'  # >20% of income


class LIHCStatus(str, Enum):
    NOT_LIHC = 'not_lihc'
    LIHC = 'lihc'   # Low Income High Cost (post-2012 UK definition)
    LIHC_SEVERE = 'lihc_severe'


_UK_MEDIAN_HOUSEHOLD_INCOME_GBP = 34_963
_UK_MEDIAN_ENERGY_COST_GBP = 2_074


@dataclass(frozen=True)
class FuelPovertyAssessment:
    customer_id: str
    gross_annual_income_gbp: float
    estimated_annual_energy_cost_gbp: float

    @property
    def energy_spend_pct(self) -> float:
        if self.gross_annual_income_gbp <= 0:
            return 100.0
        return round(self.estimated_annual_energy_cost_gbp / self.gross_annual_income_gbp * 100, 2)

    @property
    def fuel_poverty_band(self) -> FuelPovertyBand:
        pct = self.energy_spend_pct
        if pct >= 20.0:
            return FuelPovertyBand.SEVERELY_FUEL_POOR
        if pct >= 10.0:
            return FuelPovertyBand.FUEL_POOR
        if pct >= 8.0:
            return FuelPovertyBand.BORDERLINE
        return FuelPovertyBand.NOT_FUEL_POOR

    @property
    def lihc_status(self) -> LIHCStatus:
        low_income = self.gross_annual_income_gbp < _UK_MEDIAN_HOUSEHOLD_INCOME_GBP * 0.60
        high_cost = self.estimated_annual_energy_cost_gbp > _UK_MEDIAN_ENERGY_COST_GBP
        if not (low_income and high_cost):
            return LIHCStatus.NOT_LIHC
        if self.energy_spend_pct >= 20.0:
            return LIHCStatus.LIHC_SEVERE
        return LIHCStatus.LIHC

    @property
    def is_fuel_poor(self) -> bool:
        return self.fuel_poverty_band in (
            FuelPovertyBand.FUEL_POOR, FuelPovertyBand.SEVERELY_FUEL_POOR
        )

    @property
    def whd_eligible(self) -> bool:
        return self.lihc_status != LIHCStatus.NOT_LIHC

    @property
    def eco4_priority(self) -> bool:
        return self.is_fuel_poor or self.lihc_status != LIHCStatus.NOT_LIHC


def assess_fuel_poverty(
    customer_id: str,
    gross_annual_income_gbp: float,
    estimated_annual_energy_cost_gbp: float,
) -> FuelPovertyAssessment:
    return FuelPovertyAssessment(
        customer_id=customer_id,
        gross_annual_income_gbp=gross_annual_income_gbp,
        estimated_annual_energy_cost_gbp=estimated_annual_energy_cost_gbp,
    )
