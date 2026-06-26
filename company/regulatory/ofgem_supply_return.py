from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class OfgemSupplyReturn:
    year: int
    submitted_date: Optional[dt.date]
    total_customers_residential: int
    total_customers_sme: int
    total_customers_ic: int
    elec_supplied_gwh: float
    gas_supplied_gwh: float
    residential_complaints: int
    average_debt_per_customer_gbp: float
    whd_customers_supported: int
    gsop_payments_gbp: float
    solr_events: int = 0
    bad_debt_written_off_gbp: float = 0.0

    @property
    def total_customers(self) -> int:
        return self.total_customers_residential + self.total_customers_sme + self.total_customers_ic

    @property
    def complaints_per_100_customers(self) -> Optional[float]:
        if self.total_customers_residential == 0:
            return None
        return round(self.residential_complaints / self.total_customers_residential * 100, 2)

    @property
    def is_submitted(self) -> bool:
        return self.submitted_date is not None

    @property
    def whd_penetration_pct(self) -> Optional[float]:
        if self.total_customers_residential == 0:
            return None
        return round(self.whd_customers_supported / self.total_customers_residential * 100, 2)

    def summary(self) -> dict:
        return {
            'year': self.year,
            'submitted': self.is_submitted,
            'submitted_date': str(self.submitted_date) if self.submitted_date else None,
            'total_customers': self.total_customers,
            'elec_supplied_gwh': self.elec_supplied_gwh,
            'gas_supplied_gwh': self.gas_supplied_gwh,
            'complaints_per_100_customers': self.complaints_per_100_customers,
            'average_debt_per_customer_gbp': self.average_debt_per_customer_gbp,
            'whd_penetration_pct': self.whd_penetration_pct,
            'gsop_payments_gbp': self.gsop_payments_gbp,
            'bad_debt_written_off_gbp': self.bad_debt_written_off_gbp,
        }


class OfgemReturnBook:
    def __init__(self) -> None:
        self._returns: dict[int, OfgemSupplyReturn] = {}

    def file_return(
        self,
        year: int,
        submitted_date: dt.date,
        total_customers_residential: int,
        total_customers_sme: int,
        total_customers_ic: int,
        elec_supplied_gwh: float,
        gas_supplied_gwh: float,
        residential_complaints: int,
        average_debt_per_customer_gbp: float,
        whd_customers_supported: int,
        gsop_payments_gbp: float,
        solr_events: int = 0,
        bad_debt_written_off_gbp: float = 0.0,
    ) -> OfgemSupplyReturn:
        r = OfgemSupplyReturn(
            year=year, submitted_date=submitted_date,
            total_customers_residential=total_customers_residential,
            total_customers_sme=total_customers_sme,
            total_customers_ic=total_customers_ic,
            elec_supplied_gwh=elec_supplied_gwh,
            gas_supplied_gwh=gas_supplied_gwh,
            residential_complaints=residential_complaints,
            average_debt_per_customer_gbp=average_debt_per_customer_gbp,
            whd_customers_supported=whd_customers_supported,
            gsop_payments_gbp=gsop_payments_gbp,
            solr_events=solr_events,
            bad_debt_written_off_gbp=bad_debt_written_off_gbp,
        )
        self._returns[year] = r
        return r

    def get(self, year: int) -> Optional[OfgemSupplyReturn]:
        return self._returns.get(year)

    def missing_years(self, from_year: int, to_year: int) -> list[int]:
        submitted = {r.year for r in self._returns.values() if r.is_submitted}
        return [y for y in range(from_year, to_year + 1) if y not in submitted]

    def all_returns(self) -> list[OfgemSupplyReturn]:
        return sorted(self._returns.values(), key=lambda r: r.year)
