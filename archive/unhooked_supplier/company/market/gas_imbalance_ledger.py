from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional

_LINEPACK_TOLERANCE_PCT = 0.01

_NBP_ANNUAL_GBP_PER_MWH = {
    2016: 12.0, 2017: 16.0, 2018: 22.0, 2019: 15.0, 2020:  9.0,
    2021: 45.0, 2022: 180.0, 2023: 65.0, 2024: 35.0, 2025: 30.0,
}

_SEASONAL_FACTOR = {
    1: 1.18, 2: 1.15, 3: 1.08, 4: 0.95, 5: 0.90,
    6: 0.88, 7: 0.88, 8: 0.90, 9: 0.95, 10: 1.00,
    11: 1.10, 12: 1.20,
}

_SBP_PREMIUM = 0.05
_SSP_DISCOUNT = 0.05
_CRISIS_SBP_THRESHOLD_GBP_PER_MWH = 100.0


class GasImbalanceDirection(str, Enum):
    LONG  = "long"
    SHORT = "short"
    FLAT  = "flat"


@dataclass(frozen=True)
class GasImbalanceRecord:
    mprn: str
    trade_date: str
    nominated_mwh: float
    metered_mwh: float
    sbp_gbp_per_mwh: float
    ssp_gbp_per_mwh: float

    @property
    def imbalance_mwh(self) -> float:
        return round(self.metered_mwh - self.nominated_mwh, 4)

    @property
    def direction(self) -> GasImbalanceDirection:
        tol = self.nominated_mwh * _LINEPACK_TOLERANCE_PCT
        if abs(self.imbalance_mwh) <= max(tol, 0.001):
            return GasImbalanceDirection.FLAT
        return GasImbalanceDirection.SHORT if self.imbalance_mwh > 0 else GasImbalanceDirection.LONG

    @property
    def imbalance_charge_gbp(self) -> float:
        if self.direction == GasImbalanceDirection.FLAT:
            return 0.0
        if self.direction == GasImbalanceDirection.SHORT:
            return round(-self.imbalance_mwh * self.sbp_gbp_per_mwh, 2)
        return round(-self.imbalance_mwh * self.ssp_gbp_per_mwh, 2)

    @property
    def is_crisis_price(self) -> bool:
        return self.sbp_gbp_per_mwh > _CRISIS_SBP_THRESHOLD_GBP_PER_MWH

    @property
    def cashout_spread(self) -> float:
        return round(self.sbp_gbp_per_mwh - self.ssp_gbp_per_mwh, 4)


class GasImbalanceLedger:
    def __init__(self) -> None:
        self._records = []

    def nbp_annual_rate(self, year: int) -> float:
        return _NBP_ANNUAL_GBP_PER_MWH.get(year, 30.0)

    def nbp_sbp_for_month(self, year: int, month: int) -> float:
        base = _NBP_ANNUAL_GBP_PER_MWH.get(year, 30.0) * _SEASONAL_FACTOR.get(month, 1.0)
        return round(base * (1 + _SBP_PREMIUM), 2)

    def nbp_ssp_for_month(self, year: int, month: int) -> float:
        base = _NBP_ANNUAL_GBP_PER_MWH.get(year, 30.0) * _SEASONAL_FACTOR.get(month, 1.0)
        return round(base * (1 - _SSP_DISCOUNT), 2)

    def record(self, rec: GasImbalanceRecord) -> GasImbalanceRecord:
        self._records.append(rec)
        return rec

    def records_for_date(self, date: str):
        return [r for r in self._records if r.trade_date == date]

    def records_for_mprn(self, mprn: str):
        return [r for r in self._records if r.mprn == mprn]

    def _records_for_year(self, year: int):
        return [r for r in self._records if r.trade_date.startswith(str(year))]

    def net_imbalance_cost_gbp(self, year=None) -> float:
        records = self._records_for_year(year) if year else self._records
        return round(sum(r.imbalance_charge_gbp for r in records), 2)

    def crisis_periods(self):
        return [r for r in self._records if r.is_crisis_price]

    def short_periods(self):
        return [r for r in self._records if r.direction == GasImbalanceDirection.SHORT]

    def mean_cashout_spread(self, year=None) -> float:
        records = self._records_for_year(year) if year else self._records
        if not records:
            return 0.0
        return round(sum(r.cashout_spread for r in records) / len(records), 4)

    def gas_imbalance_summary(self, year=None) -> dict:
        records = self._records_for_year(year) if year else self._records
        return {
            "total_records": len(records),
            "net_imbalance_cost_gbp": self.net_imbalance_cost_gbp(year),
            "short_periods": len([r for r in records if r.direction == GasImbalanceDirection.SHORT]),
            "long_periods": len([r for r in records if r.direction == GasImbalanceDirection.LONG]),
            "crisis_periods": len([r for r in records if r.is_crisis_price]),
            "mean_cashout_spread_gbp_per_mwh": self.mean_cashout_spread(year),
        }
