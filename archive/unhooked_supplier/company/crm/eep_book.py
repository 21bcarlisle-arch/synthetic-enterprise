from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class EEPMeasure(str, Enum):
    CAVITY_WALL = 'cavity_wall_insulation'
    SOLID_WALL = 'solid_wall_insulation'
    LOFT_INSULATION = 'loft_insulation'
    HEAT_PUMP = 'heat_pump'
    SOLAR_PV = 'solar_pv'
    SMART_CONTROLS = 'smart_controls'
    DOUBLE_GLAZING = 'double_glazing'
    BOILER_UPGRADE = 'boiler_upgrade'


class EEPScheme(str, Enum):
    ECO4 = 'eco4'
    BUS = 'bus'
    SEG = 'seg'
    SELF_FUNDED = 'self_funded'


@dataclass(frozen=True)
class EEPInstallation:
    installation_id: str
    customer_id: str
    mpan: str
    measure: EEPMeasure
    scheme: EEPScheme
    install_date: dt.date
    estimated_annual_saving_gbp: float
    cost_gbp: float
    subsidy_gbp: float

    @property
    def customer_cost_gbp(self) -> float:
        return round(self.cost_gbp - self.subsidy_gbp, 2)

    @property
    def simple_payback_years(self) -> Optional[float]:
        if self.estimated_annual_saving_gbp <= 0:
            return None
        return round(self.customer_cost_gbp / self.estimated_annual_saving_gbp, 1)


class EEPBook:
    def __init__(self) -> None:
        self._installs: list[EEPInstallation] = []
        self._next_id = 1

    def record(self, customer_id: str, mpan: str, measure: EEPMeasure,
               scheme: EEPScheme, install_date: dt.date,
               estimated_annual_saving_gbp: float, cost_gbp: float,
               subsidy_gbp: float) -> EEPInstallation:
        inst = EEPInstallation(
            installation_id=f'EEP-{self._next_id:05d}',
            customer_id=customer_id, mpan=mpan,
            measure=measure, scheme=scheme, install_date=install_date,
            estimated_annual_saving_gbp=estimated_annual_saving_gbp,
            cost_gbp=cost_gbp, subsidy_gbp=subsidy_gbp,
        )
        self._next_id += 1
        self._installs.append(inst)
        return inst

    def installs_for_customer(self, customer_id: str) -> List[EEPInstallation]:
        return [i for i in self._installs if i.customer_id == customer_id]

    def total_subsidy_gbp(self, scheme: Optional[EEPScheme] = None,
                          year: Optional[int] = None) -> float:
        recs = self._installs
        if scheme:
            recs = [r for r in recs if r.scheme == scheme]
        if year:
            recs = [r for r in recs if r.install_date.year == year]
        return round(sum(r.subsidy_gbp for r in recs), 2)

    def estimated_savings_portfolio_gbp(self, year: Optional[int] = None) -> float:
        recs = self._installs if year is None else [r for r in self._installs if r.install_date.year == year]
        return round(sum(r.estimated_annual_saving_gbp for r in recs), 2)

    def annual_summary(self, year: int) -> dict:
        year_recs = [r for r in self._installs if r.install_date.year == year]
        by_measure: dict[str, int] = {}
        for r in year_recs:
            by_measure[r.measure.value] = by_measure.get(r.measure.value, 0) + 1
        return {
            'year': year,
            'installations': len(year_recs),
            'total_subsidy_gbp': round(sum(r.subsidy_gbp for r in year_recs), 2),
            'estimated_savings_gbp': round(sum(r.estimated_annual_saving_gbp for r in year_recs), 2),
            'by_measure': by_measure,
        }
