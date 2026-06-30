"""Imbalance Charge Register (Phase EN).

Under BSC (Balancing and Settlement Code), electricity suppliers are charged
for the difference between their nominated energy (contracted/hedged) and
actual consumption by customers.

Imbalance charges are levied at the System Buy Price (SBP) when short
(consumed more than nominated) or credited at System Sell Price (SSP) when
long (consumed less than nominated). SBP > SSP always (bid-offer spread).

This module models:
- Per-settlement-period imbalance position (MWh)
- Charge calculation using SBP/SSP rates
- Aggregated exposure by month/year
- Crisis periods (2021-22 when SBP exceeded £4,000/MWh in some periods)

The company observes its own imbalance via BSC data services
(Elexon API, REMIT notifications). It cannot see competitor imbalances.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class ImbalanceType(str, Enum):
    SHORT = "short"   # consumed more than nominated -> buy at SBP
    LONG = "long"     # consumed less than nominated -> sell at SSP
    FLAT = "flat"     # within tolerance


_IMBALANCE_FLAT_TOLERANCE_MWH = 0.5  # ±0.5 MWh considered flat


@dataclass(frozen=True)
class ImbalanceRecord:
    settlement_period: int    # 1-48 (HH)
    settlement_date: dt.date
    nominated_mwh: float
    actual_mwh: float
    sbp_gbp_per_mwh: float    # System Buy Price
    ssp_gbp_per_mwh: float    # System Sell Price

    @property
    def imbalance_mwh(self) -> float:
        return self.actual_mwh - self.nominated_mwh

    @property
    def imbalance_type(self) -> ImbalanceType:
        if abs(self.imbalance_mwh) <= _IMBALANCE_FLAT_TOLERANCE_MWH:
            return ImbalanceType.FLAT
        return ImbalanceType.SHORT if self.imbalance_mwh > 0 else ImbalanceType.LONG

    @property
    def charge_gbp(self) -> float:
        imb = self.imbalance_mwh
        if self.imbalance_type == ImbalanceType.FLAT:
            return 0.0
        if imb > 0:
            return imb * self.sbp_gbp_per_mwh
        return imb * self.ssp_gbp_per_mwh  # negative * negative = positive credit (negative charge)

    @property
    def is_crisis_period(self) -> bool:
        return self.sbp_gbp_per_mwh > 1000.0

    def record_summary(self) -> str:
        return (
            str(self.settlement_date) + " SP" + str(self.settlement_period) + ": "
            "nom=" + str(round(self.nominated_mwh, 2)) + "MWh "
            "act=" + str(round(self.actual_mwh, 2)) + "MWh "
            "imb=" + self.imbalance_type.value + " "
            "charge=GBP" + str(round(self.charge_gbp, 2))
        )


class ImbalanceChargeRegister:

    def __init__(self) -> None:
        self._records: List[ImbalanceRecord] = []

    def record(self, rec: ImbalanceRecord) -> ImbalanceRecord:
        self._records.append(rec)
        return rec

    def records_for_date(self, date: dt.date) -> List[ImbalanceRecord]:
        return [r for r in self._records if r.settlement_date == date]

    def records_for_month(self, year: int, month: int) -> List[ImbalanceRecord]:
        return [r for r in self._records
                if r.settlement_date.year == year and r.settlement_date.month == month]

    def short_periods(self) -> List[ImbalanceRecord]:
        return [r for r in self._records if r.imbalance_type == ImbalanceType.SHORT]

    def long_periods(self) -> List[ImbalanceRecord]:
        return [r for r in self._records if r.imbalance_type == ImbalanceType.LONG]

    def crisis_exposures(self) -> List[ImbalanceRecord]:
        return [r for r in self._records if r.is_crisis_period]

    def total_charge_gbp(self, year: Optional[int] = None) -> float:
        recs = self._records
        if year is not None:
            recs = [r for r in recs if r.settlement_date.year == year]
        return sum(r.charge_gbp for r in recs)

    def net_imbalance_mwh(self, year: Optional[int] = None) -> float:
        recs = self._records
        if year is not None:
            recs = [r for r in recs if r.settlement_date.year == year]
        return sum(r.imbalance_mwh for r in recs)

    def average_sbp(self, year: Optional[int] = None) -> float:
        recs = self._records
        if year is not None:
            recs = [r for r in recs if r.settlement_date.year == year]
        if not recs:
            return 0.0
        return sum(r.sbp_gbp_per_mwh for r in recs) / len(recs)

    def imbalance_summary(self, year: Optional[int] = None) -> str:
        total = self.total_charge_gbp(year)
        net = self.net_imbalance_mwh(year)
        n_crisis = len(self.crisis_exposures())
        return (
            "Imbalance Register" + (" " + str(year) if year else "") + ": "
            "net_imb=" + str(round(net, 1)) + "MWh "
            "total_charge=GBP" + str(round(total)) + " "
            "crisis_periods=" + str(n_crisis) + "."
        )
