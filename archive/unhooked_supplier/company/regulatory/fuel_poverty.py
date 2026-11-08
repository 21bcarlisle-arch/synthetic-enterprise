"""Fuel Poverty Indicator: customer fuel poverty risk assessment."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class FuelPovertyDefinition(str, Enum):
    CLASSIC = "classic"          # >10% income spent on energy (pre-2013)
    LOW_INCOME_HIGH_COST = "lihc"  # LIHC: below poverty after energy costs (post-2013)
    AFFORDABLE_WARMTH = "affordable_warmth"  # Scotland definition


class FuelPovertyRisk(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    FUEL_POOR = "fuel_poor"


_CLASSIC_THRESHOLD_PCT = 10.0      # >10% of income = fuel poor
_LIHC_INCOME_THRESHOLD_PCT = 60.0  # below 60% median income after energy = fuel poor


@dataclass(frozen=True)
class FuelPovertyAssessment:
    account_id: str
    assessment_date: dt.date
    annual_energy_cost_gbp: float
    estimated_annual_income_gbp: float
    definition: FuelPovertyDefinition = FuelPovertyDefinition.CLASSIC
    median_income_gbp: float = 35_000.0  # UK median ~£35k

    @property
    def energy_as_pct_income(self) -> Optional[float]:
        if self.estimated_annual_income_gbp <= 0:
            return None
        return round(self.annual_energy_cost_gbp / self.estimated_annual_income_gbp * 100, 1)

    @property
    def income_after_energy_gbp(self) -> float:
        return self.estimated_annual_income_gbp - self.annual_energy_cost_gbp

    @property
    def risk(self) -> FuelPovertyRisk:
        pct = self.energy_as_pct_income
        if pct is None:
            return FuelPovertyRisk.HIGH
        if self.definition == FuelPovertyDefinition.CLASSIC:
            if pct >= _CLASSIC_THRESHOLD_PCT:
                return FuelPovertyRisk.FUEL_POOR
            if pct >= 7.0:
                return FuelPovertyRisk.HIGH
            if pct >= 5.0:
                return FuelPovertyRisk.MODERATE
            return FuelPovertyRisk.LOW
        else:
            after = self.income_after_energy_gbp
            if after < self.median_income_gbp * 0.60 and pct >= _CLASSIC_THRESHOLD_PCT:
                return FuelPovertyRisk.FUEL_POOR
            if after < self.median_income_gbp * 0.60:
                return FuelPovertyRisk.HIGH
            if pct >= 7.0:
                return FuelPovertyRisk.MODERATE
            return FuelPovertyRisk.LOW

    @property
    def is_fuel_poor(self) -> bool:
        return self.risk == FuelPovertyRisk.FUEL_POOR


class FuelPovertyBook:
    """Tracks customer-level fuel poverty assessments.

    Real calibration:
    - UK fuel poverty definitions changed 2013: England moved from Classic (>10% income)
      to Low Income High Cost (LIHC). Scotland, Wales, NI retain older definitions.
    - National Energy Action: ~6.5M UK households fuel poor 2023 (energy crisis peak).
    - Ofgem Consumer Duty: suppliers must identify and act on fuel poverty indicators.
    - WHD Core Group: automatically identified via DWP matching; WHD helps fuel poor.
    - Connexus / StepChange referral: common pathway for fuel-poor customers to support.
    """

    def __init__(self) -> None:
        self._assessments: List[FuelPovertyAssessment] = []

    def record_assessment(self, assessment: FuelPovertyAssessment) -> FuelPovertyAssessment:
        self._assessments.append(assessment)
        return assessment

    def latest_for(self, account_id: str) -> Optional[FuelPovertyAssessment]:
        account_assessments = [a for a in self._assessments if a.account_id == account_id]
        if not account_assessments:
            return None
        return sorted(account_assessments, key=lambda a: a.assessment_date)[-1]

    def fuel_poor_accounts(self) -> List[FuelPovertyAssessment]:
        latest: dict = {}
        for a in self._assessments:
            if (a.account_id not in latest
                    or a.assessment_date > latest[a.account_id].assessment_date):
                latest[a.account_id] = a
        return [a for a in latest.values() if a.is_fuel_poor]

    def high_risk_accounts(self) -> List[FuelPovertyAssessment]:
        latest: dict = {}
        for a in self._assessments:
            if (a.account_id not in latest
                    or a.assessment_date > latest[a.account_id].assessment_date):
                latest[a.account_id] = a
        return [a for a in latest.values()
                if a.risk in (FuelPovertyRisk.HIGH, FuelPovertyRisk.FUEL_POOR)]

    def fuel_poverty_rate_pct(self) -> float:
        fp = self.fuel_poor_accounts()
        total = len({a.account_id for a in self._assessments})
        if total == 0:
            return 0.0
        return round(len(fp) / total * 100, 1)

    def fuel_poverty_summary(self) -> dict:
        return {
            "total_assessments": len(self._assessments),
            "fuel_poor_count": len(self.fuel_poor_accounts()),
            "high_risk_count": len(self.high_risk_accounts()),
            "fuel_poverty_rate_pct": self.fuel_poverty_rate_pct(),
        }
