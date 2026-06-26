"""Smart meter half-hourly consumption analytics: peak detection, seasonal profiling."""
from __future__ import annotations

import datetime as dt
import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


# Ofgem standard HH settlement periods
PERIODS_PER_DAY = 48
PERIOD_MINUTES = 30


class PeakPeriod(str):
    EVENING = 'evening'  # 16:00-20:00 (periods 33-40)
    MORNING = 'morning'  # 07:00-09:00 (periods 15-18)
    OVERNIGHT = 'overnight'  # 00:00-06:00 (periods 1-12)


@dataclass(frozen=True)
class HHReading:
    customer_id: str
    read_datetime: dt.datetime
    kwh: float

    @property
    def settlement_period(self) -> int:
        minutes = self.read_datetime.hour * 60 + self.read_datetime.minute
        return minutes // 30 + 1

    @property
    def is_evening_peak(self) -> bool:
        return 33 <= self.settlement_period <= 40

    @property
    def is_morning_peak(self) -> bool:
        return 15 <= self.settlement_period <= 18


@dataclass(frozen=True)
class ConsumptionProfile:
    customer_id: str
    period_start: dt.date
    period_end: dt.date
    total_kwh: float
    reading_count: int
    peak_kwh: float
    off_peak_kwh: float
    avg_daily_kwh: float
    max_demand_kw: float
    load_factor_pct: float

    @property
    def peak_share_pct(self) -> float:
        if self.total_kwh == 0:
            return 0.0
        return round(self.peak_kwh / self.total_kwh * 100, 1)

    @property
    def days_covered(self) -> int:
        return (self.period_end - self.period_start).days + 1


def build_consumption_profile(
    customer_id: str,
    readings: List[HHReading],
) -> Optional[ConsumptionProfile]:
    if not readings:
        return None

    customer_readings = [r for r in readings if r.customer_id == customer_id]
    if not customer_readings:
        return None

    dates = [r.read_datetime.date() for r in customer_readings]
    period_start = min(dates)
    period_end = max(dates)
    days = max(1, (period_end - period_start).days + 1)

    total_kwh = sum(r.kwh for r in customer_readings)
    peak_kwh = sum(r.kwh for r in customer_readings if r.is_evening_peak)
    off_peak_kwh = total_kwh - peak_kwh
    avg_daily_kwh = round(total_kwh / days, 3)

    # Max demand: peak half-hour in kW = kWh * 2 (30min -> hour)
    max_demand_kw = max(r.kwh * 2 for r in customer_readings) if customer_readings else 0.0

    # Load factor: avg demand / max demand
    avg_kw = total_kwh / (days * 24) if days > 0 else 0.0
    load_factor_pct = round(avg_kw / max_demand_kw * 100, 1) if max_demand_kw > 0 else 0.0

    return ConsumptionProfile(
        customer_id=customer_id,
        period_start=period_start,
        period_end=period_end,
        total_kwh=round(total_kwh, 3),
        reading_count=len(customer_readings),
        peak_kwh=round(peak_kwh, 3),
        off_peak_kwh=round(off_peak_kwh, 3),
        avg_daily_kwh=avg_daily_kwh,
        max_demand_kw=round(max_demand_kw, 3),
        load_factor_pct=load_factor_pct,
    )


class SmartMeterAnalytics:
    def __init__(self) -> None:
        self._readings: List[HHReading] = []

    def ingest(self, customer_id: str, read_datetime: dt.datetime, kwh: float) -> HHReading:
        r = HHReading(customer_id=customer_id, read_datetime=read_datetime, kwh=kwh)
        self._readings.append(r)
        return r

    def profile(self, customer_id: str) -> Optional[ConsumptionProfile]:
        return build_consumption_profile(customer_id, self._readings)

    def customers_with_data(self) -> List[str]:
        return list(set(r.customer_id for r in self._readings))

    def evening_peak_customers(self, threshold_pct: float = 35.0) -> List[str]:
        result = []
        for cid in self.customers_with_data():
            p = self.profile(cid)
            if p and p.peak_share_pct >= threshold_pct:
                result.append(cid)
        return result

    def high_demand_customers(self, threshold_kw: float) -> List[str]:
        result = []
        for cid in self.customers_with_data():
            p = self.profile(cid)
            if p and p.max_demand_kw >= threshold_kw:
                result.append(cid)
        return result
