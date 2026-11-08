from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List, Optional


_SEG_MIN_RATE_PPM = 1.0   # Ofgem: must be >0; convention is 1p minimum

_SEG_RATES_PPM: dict[int, float] = {
    2020: 5.5,
    2021: 7.0,
    2022: 15.0,  # crisis era: exported energy highly valuable
    2023: 12.0,
    2024: 8.5,
    2025: 7.0,
}


def seg_rate_ppm(year: int) -> float:
    return _SEG_RATES_PPM.get(year, _SEG_RATES_PPM[2020])


def seg_valid_rate(rate_ppm: float) -> bool:
    return rate_ppm >= _SEG_MIN_RATE_PPM


@dataclass
class SEGAccount:
    customer_id: str
    meter_point_id: str
    tariff_name: str
    rate_ppm: float
    registered_date: date
    export_readings: Dict[str, float] = field(default_factory=dict)  # YYYY-MM -> kWh

    def record_export(self, year_month: str, kwh: float) -> None:
        self.export_readings[year_month] = self.export_readings.get(year_month, 0.0) + kwh

    def payment_for_period(self, year_month: str) -> float:
        kwh = self.export_readings.get(year_month, 0.0)
        return round(kwh * self.rate_ppm / 100 / 100, 2)

    def total_export_kwh(self) -> float:
        return sum(self.export_readings.values())

    def total_payments_gbp(self) -> float:
        return round(sum(
            kwh * self.rate_ppm / 100 / 100
            for kwh in self.export_readings.values()
        ), 2)

    def annual_summary(self, year: int) -> dict:
        year_str = str(year)
        year_months = {k: v for k, v in self.export_readings.items() if k.startswith(year_str)}
        export_kwh = sum(year_months.values())
        payment_gbp = round(export_kwh * self.rate_ppm / 100 / 100, 2)
        result = dict(
            customer_id=self.customer_id,
            year=year,
            export_kwh=round(export_kwh, 2),
            rate_ppm=self.rate_ppm,
            payment_gbp=payment_gbp,
        )
        return result


@dataclass
class SEGBook:
    _accounts: List[SEGAccount] = field(default_factory=list)

    def register(
        self,
        customer_id: str,
        meter_point_id: str,
        tariff_name: str,
        rate_ppm: float,
        registered_date: date,
    ) -> SEGAccount:
        if not seg_valid_rate(rate_ppm):
            raise ValueError(f"SEG rate must be >= {_SEG_MIN_RATE_PPM}p/kWh, got {rate_ppm}")
        acc = SEGAccount(
            customer_id=customer_id,
            meter_point_id=meter_point_id,
            tariff_name=tariff_name,
            rate_ppm=rate_ppm,
            registered_date=registered_date,
        )
        self._accounts.append(acc)
        return acc

    def get_account(self, customer_id: str) -> Optional[SEGAccount]:
        for a in self._accounts:
            if a.customer_id == customer_id:
                return a
        return None

    def record_export(self, customer_id: str, year_month: str, kwh: float) -> bool:
        acc = self.get_account(customer_id)
        if acc is None:
            return False
        acc.record_export(year_month, kwh)
        return True

    def portfolio_summary(self, year: int) -> dict:
        accounts = self._accounts
        if not accounts:
            result = dict(year=year, total_accounts=0, total_export_kwh=0.0, total_payments_gbp=0.0)
            return result
        summaries = [a.annual_summary(year) for a in accounts]
        total_kwh = sum(s["export_kwh"] for s in summaries)
        total_gbp = sum(s["payment_gbp"] for s in summaries)
        result = dict(
            year=year,
            total_accounts=len(accounts),
            total_export_kwh=round(total_kwh, 2),
            total_payments_gbp=round(total_gbp, 2),
        )
        return result
