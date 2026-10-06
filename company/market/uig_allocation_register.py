"""Unidentified Gas (UIG) Allocation Register (Phase GN).

UIG = gas entering the LDZs minus the gas allocated to metered consumers; undetected theft is one
component. It is allocated daily to shippers by AUGE weighting factors by matrix position, not in
simple proportion to throughput share.

Corrected 2026-10-06 against `docs/market_research/read_access_and_theft_duties.md` §3.3 (AUG
Statement 2024-25 p.27, read in the primary): actual final UIG was 3.81%, 2.19%, 2.69%, 2.90% and
2.50% of throughput for GY17/18-GY21/22, "around 2.5% ... since Nexus go-live" -- toggle
`q6_uig_share_of_ldz_throughput`, default 0.025, range 0.0219-0.0381. This said "UIG adds
~0.5-2%", below every observed year, and that "high UIG (>=2%) triggers Xoserve investigation",
for which no source was found.
Distinct from gas_imbalance_ledger.py (nominated vs actual flow balance)
and gas_network_ledger.py (transportation charges).
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import List, Optional

#: UNSOURCED, so None. No published UIG level that "triggers investigation" was found; the 2.0
#: this held sat below every observed final UIG (2.19-3.81%), so it flagged every real month.
#: A caller with a sourced or graded threshold passes it to `exceeds` / `high_uig_periods`.
_HIGH_UIG_PCT: Optional[float] = None


@dataclass(frozen=True)
class UIGMonthlyRecord:
    record_id: str
    settlement_month: dt.date
    total_throughput_mwh: float
    uig_allocated_mwh: float
    xoserve_ref: Optional[str] = None
    notes: str = ""

    @property
    def uig_rate_pct(self) -> float:
        if self.total_throughput_mwh == 0:
            return 0.0
        return round(self.uig_allocated_mwh / self.total_throughput_mwh * 100, 4)

    def exceeds(self, threshold_pct: float) -> bool:
        return self.uig_rate_pct >= threshold_pct

    @property
    def is_high_uig(self) -> Optional[bool]:
        """None: no sourced threshold, so "high" cannot be told."""
        if _HIGH_UIG_PCT is None:
            return None
        return self.exceeds(_HIGH_UIG_PCT)

    def uig_summary(self) -> str:
        flag = " [HIGH]" if self.is_high_uig is True else ""
        return (
            "UIG " + self.record_id
            + " month=" + str(self.settlement_month)
            + " tp=" + str(round(self.total_throughput_mwh, 1)) + "MWh"
            + " uig=" + str(round(self.uig_allocated_mwh, 1)) + "MWh"
            + " (" + str(self.uig_rate_pct) + "%)"
            + flag
        )


class UIGAllocationRegister:

    def __init__(self) -> None:
        self._records: List[UIGMonthlyRecord] = []
        self._counter: int = 0

    def _next_id(self) -> str:
        self._counter += 1
        return "UIG-" + str(self._counter).zfill(5)

    def record_allocation(
        self, settlement_month: dt.date, total_throughput_mwh: float,
        uig_allocated_mwh: float, xoserve_ref: Optional[str] = None,
        notes: str = "",
    ) -> UIGMonthlyRecord:
        if total_throughput_mwh < 0:
            raise ValueError("total_throughput_mwh must be non-negative")
        record = UIGMonthlyRecord(
            record_id=self._next_id(),
            settlement_month=dt.date(settlement_month.year, settlement_month.month, 1),
            total_throughput_mwh=total_throughput_mwh,
            uig_allocated_mwh=uig_allocated_mwh,
            xoserve_ref=xoserve_ref,
            notes=notes,
        )
        self._records.append(record)
        return record

    def for_month(self, year: int, month: int) -> Optional[UIGMonthlyRecord]:
        target = dt.date(year, month, 1)
        for r in self._records:
            if r.settlement_month == target:
                return r
        return None

    def high_uig_periods(
        self, threshold_pct: Optional[float] = None,
    ) -> Optional[List[UIGMonthlyRecord]]:
        """None when no threshold is supplied and the module's own is unsourced."""
        threshold = threshold_pct if threshold_pct is not None else _HIGH_UIG_PCT
        if threshold is None:
            return None
        return [r for r in self._records if r.exceeds(threshold)]

    def total_uig_allocated_mwh(self) -> float:
        return sum(r.uig_allocated_mwh for r in self._records)

    def total_throughput_mwh(self) -> float:
        return sum(r.total_throughput_mwh for r in self._records)

    def average_uig_rate_pct(self) -> Optional[float]:
        tp = self.total_throughput_mwh()
        if tp == 0:
            return None
        return round(self.total_uig_allocated_mwh() / tp * 100, 4)

    def rolling_3m_avg_rate_pct(self, year: int, month: int) -> Optional[float]:
        months = []
        for delta in range(3):
            m = month - delta
            y = year
            while m <= 0:
                m += 12
                y -= 1
            r = self.for_month(y, m)
            if r is not None:
                months.append(r)
        if not months:
            return None
        tp = sum(r.total_throughput_mwh for r in months)
        uig = sum(r.uig_allocated_mwh for r in months)
        return round(uig / tp * 100, 4) if tp > 0 else None

    def most_recent(self) -> Optional[UIGMonthlyRecord]:
        if not self._records:
            return None
        return max(self._records, key=lambda r: r.settlement_month)

    def uig_register_summary(self) -> str:
        n = len(self._records)
        high = self.high_uig_periods()
        n_high = "n/a" if high is None else str(len(high))
        avg = self.average_uig_rate_pct()
        avg_str = (str(avg) + "%") if avg is not None else "n/a"
        total_mwh = round(self.total_uig_allocated_mwh(), 1)
        return (
            "UIG Allocation Register: " + str(n) + " months, "
            + n_high + " high-UIG periods. "
            + "Total UIG: " + str(total_mwh) + " MWh. "
            + "Avg rate: " + avg_str + "."
        )
