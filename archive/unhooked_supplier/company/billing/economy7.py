from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Optional, Tuple


class TariffRegister(str, Enum):
    DAY = "day"
    NIGHT = "night"


_E7_NIGHT_HOURS_START = 0   # midnight
_E7_NIGHT_HOURS_END = 7     # 07:00 local time


_E7_DAY_RATE_PPM: dict[int, float] = {
    2016: 12.0, 2017: 12.5, 2018: 13.5, 2019: 14.5,
    2020: 14.0, 2021: 16.0, 2022: 34.0, 2023: 28.0, 2024: 22.0, 2025: 18.0,
}
_E7_NIGHT_RATE_PPM: dict[int, float] = {
    2016: 6.5,  2017: 7.0,  2018: 7.5,  2019: 8.0,
    2020: 7.5,  2021: 9.0,  2022: 19.0, 2023: 15.0, 2024: 12.0, 2025: 10.0,
}


def e7_unit_rate_ppm(year: int, register: TariffRegister) -> float:
    if register == TariffRegister.DAY:
        return _E7_DAY_RATE_PPM.get(year, _E7_DAY_RATE_PPM[2019])
    return _E7_NIGHT_RATE_PPM.get(year, _E7_NIGHT_RATE_PPM[2019])


@dataclass(frozen=True)
class E7MeterRead:
    customer_id: str
    read_date: date
    day_kwh: float
    night_kwh: float

    @property
    def total_kwh(self) -> float:
        return self.day_kwh + self.night_kwh

    @property
    def night_pct(self) -> float:
        if self.total_kwh == 0:
            return 0.0
        return self.night_kwh / self.total_kwh * 100.0


@dataclass(frozen=True)
class E7Bill:
    customer_id: str
    period_start: date
    period_end: date
    day_kwh: float
    night_kwh: float
    day_rate_ppm: float
    night_rate_ppm: float

    @property
    def day_charge_gbp(self) -> float:
        return round(self.day_kwh * self.day_rate_ppm / 100 / 100, 2)

    @property
    def night_charge_gbp(self) -> float:
        return round(self.night_kwh * self.night_rate_ppm / 100 / 100, 2)

    @property
    def total_gbp(self) -> float:
        return round(self.day_charge_gbp + self.night_charge_gbp, 2)

    @property
    def blended_rate_ppm(self) -> float:
        total = self.day_kwh + self.night_kwh
        if total == 0:
            return 0.0
        return round(
            (self.day_kwh * self.day_rate_ppm + self.night_kwh * self.night_rate_ppm)
            / total,
            2,
        )


def generate_e7_bill(
    customer_id: str,
    period_start: date,
    period_end: date,
    day_kwh: float,
    night_kwh: float,
) -> E7Bill:
    year = period_start.year
    return E7Bill(
        customer_id=customer_id,
        period_start=period_start,
        period_end=period_end,
        day_kwh=day_kwh,
        night_kwh=night_kwh,
        day_rate_ppm=e7_unit_rate_ppm(year, TariffRegister.DAY),
        night_rate_ppm=e7_unit_rate_ppm(year, TariffRegister.NIGHT),
    )
