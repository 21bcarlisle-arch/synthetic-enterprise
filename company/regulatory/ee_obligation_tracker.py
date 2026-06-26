"""Energy efficiency obligation referral tracker: ECO4, GBIS, WHD, BUS."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class EEScheme(str, Enum):
    ECO4 = 'eco4'
    GBIS = 'gbis'
    WHD = 'whd'
    BUS = 'bus'
    HUG2 = 'hug2'


class MeasureType(str, Enum):
    LOFT_INSULATION = 'loft_insulation'
    CAVITY_WALL = 'cavity_wall'
    SOLID_WALL = 'solid_wall'
    HEAT_PUMP = 'heat_pump'
    BOILER_UPGRADE = 'boiler_upgrade'
    SOLAR_PV = 'solar_pv'
    SMART_HEATING = 'smart_heating'
    GLAZING = 'glazing'


class ReferralStatus(str, Enum):
    REFERRED = 'referred'
    INSTALLER_ASSIGNED = 'installer_assigned'
    SURVEY_BOOKED = 'survey_booked'
    MEASURE_INSTALLED = 'measure_installed'
    DECLINED = 'declined'
    INELIGIBLE = 'ineligible'


_TYPICAL_SAVINGS_KWH_PER_YEAR: Dict[MeasureType, float] = {
    MeasureType.LOFT_INSULATION: 600.0,
    MeasureType.CAVITY_WALL: 800.0,
    MeasureType.SOLID_WALL: 1200.0,
    MeasureType.HEAT_PUMP: 3000.0,
    MeasureType.BOILER_UPGRADE: 400.0,
    MeasureType.SOLAR_PV: 1800.0,
    MeasureType.SMART_HEATING: 200.0,
    MeasureType.GLAZING: 300.0,
}


@dataclass
class EEReferral:
    referral_id: str
    customer_id: str
    scheme: EEScheme
    measure_type: MeasureType
    referral_date: dt.date
    status: ReferralStatus = ReferralStatus.REFERRED
    installation_date: Optional[dt.date] = None
    installer_name: Optional[str] = None
    cost_gbp: float = 0.0
    is_vulnerable: bool = False

    @property
    def typical_annual_saving_kwh(self) -> float:
        return _TYPICAL_SAVINGS_KWH_PER_YEAR.get(self.measure_type, 0.0)

    @property
    def is_completed(self) -> bool:
        return self.status == ReferralStatus.MEASURE_INSTALLED

    def install(self, installation_date: dt.date,
                  installer_name: str, cost_gbp: float = 0.0) -> None:
        self.status = ReferralStatus.MEASURE_INSTALLED
        self.installation_date = installation_date
        self.installer_name = installer_name
        self.cost_gbp = cost_gbp


class EEObligationTracker:
    def __init__(self) -> None:
        self._referrals: List[EEReferral] = []

    def refer(self, referral_id: str, customer_id: str, scheme: EEScheme,
               measure_type: MeasureType, referral_date: dt.date,
               is_vulnerable: bool = False) -> EEReferral:
        ref = EEReferral(
            referral_id=referral_id, customer_id=customer_id,
            scheme=scheme, measure_type=measure_type,
            referral_date=referral_date, is_vulnerable=is_vulnerable,
        )
        self._referrals.append(ref)
        return ref

    def get(self, referral_id: str) -> Optional[EEReferral]:
        return next((r for r in self._referrals if r.referral_id == referral_id), None)

    def completed_measures(self, year: Optional[int] = None) -> List[EEReferral]:
        result = [r for r in self._referrals if r.is_completed]
        if year is not None:
            result = [r for r in result
                       if r.installation_date and r.installation_date.year == year]
        return result

    def total_savings_kwh(self, year: Optional[int] = None) -> float:
        return sum(r.typical_annual_saving_kwh
                   for r in self.completed_measures(year))

    def obligation_mwh_delivered(self, scheme: EEScheme, year: int) -> float:
        return round(sum(
            r.typical_annual_saving_kwh
            for r in self._referrals
            if r.scheme == scheme and r.is_completed
            and r.installation_date and r.installation_date.year == year
        ) / 1000, 3)

    def vulnerable_customer_count(self, scheme: EEScheme) -> int:
        return sum(1 for r in self._referrals
                   if r.scheme == scheme and r.is_vulnerable)

    def portfolio_summary(self, year: int) -> dict:
        by_scheme: Dict[str, int] = {}
        for r in self._referrals:
            if r.referral_date.year == year:
                k = r.scheme.value
                by_scheme[k] = by_scheme.get(k, 0) + 1
        return {
            'year': year,
            'total_referrals': len([r for r in self._referrals
                                     if r.referral_date.year == year]),
            'completed': len(self.completed_measures(year)),
            'total_savings_kwh': self.total_savings_kwh(year),
            'by_scheme': by_scheme,
        }
