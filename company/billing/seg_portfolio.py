"""Smart Export Guarantee (SEG) and domestic battery storage analytics."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class SEGTariffTier(str, Enum):
    FIXED = 'fixed'
    FLEXIBLE = 'flexible'


_SEG_RATE_HISTORY_PENCE_PER_KWH: Dict[int, float] = {
    2020: 5.5,  # SEG launched Jan 2020
    2021: 6.0,
    2022: 12.0,  # Rose with wholesale prices
    2023: 15.0,
    2024: 12.0,
    2025: 10.0,
}


def get_seg_rate(year: int) -> float:
    if year in _SEG_RATE_HISTORY_PENCE_PER_KWH:
        return _SEG_RATE_HISTORY_PENCE_PER_KWH[year]
    return _SEG_RATE_HISTORY_PENCE_PER_KWH.get(
        max(k for k in _SEG_RATE_HISTORY_PENCE_PER_KWH if k <= year), 10.0
    )


@dataclass(frozen=True)
class SEGCustomer:
    customer_id: str
    mpan: str
    solar_capacity_kwp: float
    registration_date: dt.date
    tariff_tier: SEGTariffTier = SEGTariffTier.FIXED
    battery_capacity_kwh: float = 0.0

    @property
    def has_battery(self) -> bool:
        return self.battery_capacity_kwh > 0

    def estimated_annual_export_kwh(self, year: int) -> float:
        base_generation_kwh_per_kwp = 900.0
        self_consumption_pct = 0.70 if self.has_battery else 0.50
        gross_kwh = self.solar_capacity_kwp * base_generation_kwh_per_kwp
        return round(gross_kwh * (1 - self_consumption_pct), 1)

    def annual_seg_income_gbp(self, year: int) -> float:
        rate = get_seg_rate(year)
        export_kwh = self.estimated_annual_export_kwh(year)
        return round(export_kwh * rate / 100, 2)


class SEGPortfolio:
    def __init__(self) -> None:
        self._customers: List[SEGCustomer] = []
        self._export_records: List[tuple] = []

    def register(self, customer_id: str, mpan: str,
                   solar_kwp: float, registration_date: dt.date,
                   tier: SEGTariffTier = SEGTariffTier.FIXED,
                   battery_kwh: float = 0.0) -> SEGCustomer:
        c = SEGCustomer(
            customer_id=customer_id, mpan=mpan,
            solar_capacity_kwp=solar_kwp,
            registration_date=registration_date,
            tariff_tier=tier, battery_capacity_kwh=battery_kwh,
        )
        self._customers.append(c)
        return c

    def record_export(self, customer_id: str, period: dt.date,
                        kwh: float) -> None:
        self._export_records.append((customer_id, period, kwh))

    def total_export_kwh(self, year: int) -> float:
        return round(sum(
            kwh for _, period, kwh in self._export_records
            if period.year == year
        ), 1)

    def total_seg_payments_gbp(self, year: int) -> float:
        rate = get_seg_rate(year)
        return round(self.total_export_kwh(year) * rate / 100, 2)

    def customers_with_battery(self) -> List[SEGCustomer]:
        return [c for c in self._customers if c.has_battery]

    def total_solar_capacity_kwp(self) -> float:
        return round(sum(c.solar_capacity_kwp for c in self._customers), 1)

    def seg_summary(self, year: int) -> dict:
        return {
            'year': year,
            'seg_rate_pence': get_seg_rate(year),
            'registered_customers': len(self._customers),
            'battery_customers': len(self.customers_with_battery()),
            'total_solar_kwp': self.total_solar_capacity_kwp(),
            'total_export_kwh': self.total_export_kwh(year),
            'total_seg_payments_gbp': self.total_seg_payments_gbp(year),
        }
