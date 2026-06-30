"""Service quality monitor — tracks bill clarity, complaint probability, and bill shock.

A real energy supplier tracks these metrics through its own customer service systems:
- Bill clarity scores (from customer feedback / smart meter accuracy checks)
- Complaint probability (from CRM complaint log / Ofgem complaint league tables)
- Bill shock events (bills > prior period + threshold pct, flagged by billing system)

Ofgem benchmarks: complaints < 2.5% of bills; clarity > 0.80; bill shock < 0.30%.
Consumer Duty (FCA 2023): good outcomes for customers — clarity and bill predictability
are direct indicators of compliance.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ServiceQualityRAG(str, Enum):
    GREEN = "GREEN"
    AMBER = "AMBER"
    RED = "RED"


_CLARITY_AMBER = 0.82
_CLARITY_RED = 0.80
_COMPLAINT_AMBER = 0.05
_COMPLAINT_RED = 0.06
_BILL_SHOCK_AMBER = 0.20   # pct
_BILL_SHOCK_RED = 0.30


@dataclass(frozen=True)
class ServiceQualitySnapshot:
    year: int
    avg_clarity: float
    avg_complaint_probability: float
    avg_bill_shock_pct: float
    bills_count: int
    shock_event_count: int

    @property
    def clarity_rag(self) -> ServiceQualityRAG:
        if self.avg_clarity >= _CLARITY_AMBER:
            return ServiceQualityRAG.GREEN
        if self.avg_clarity >= _CLARITY_RED:
            return ServiceQualityRAG.AMBER
        return ServiceQualityRAG.RED

    @property
    def complaint_rag(self) -> ServiceQualityRAG:
        if self.avg_complaint_probability < _COMPLAINT_AMBER:
            return ServiceQualityRAG.GREEN
        if self.avg_complaint_probability < _COMPLAINT_RED:
            return ServiceQualityRAG.AMBER
        return ServiceQualityRAG.RED

    @property
    def bill_shock_rag(self) -> ServiceQualityRAG:
        if self.avg_bill_shock_pct is None or self.avg_bill_shock_pct < _BILL_SHOCK_AMBER:
            return ServiceQualityRAG.GREEN
        if self.avg_bill_shock_pct < _BILL_SHOCK_RED:
            return ServiceQualityRAG.AMBER
        return ServiceQualityRAG.RED

    @property
    def overall_rag(self) -> ServiceQualityRAG:
        rags = [self.clarity_rag, self.complaint_rag, self.bill_shock_rag]
        if ServiceQualityRAG.RED in rags:
            return ServiceQualityRAG.RED
        if ServiceQualityRAG.AMBER in rags:
            return ServiceQualityRAG.AMBER
        return ServiceQualityRAG.GREEN

    @property
    def shock_rate_pct(self) -> float:
        """Bill shock events as % of total bills."""
        if self.bills_count == 0:
            return 0.0
        return self.shock_event_count / self.bills_count * 100


class ServiceQualityMonitor:
    """Accumulates annual service quality snapshots and surfaces trends."""

    def __init__(self) -> None:
        self._snapshots: dict[int, ServiceQualitySnapshot] = {}

    def record(
        self,
        year: int,
        avg_clarity: float,
        avg_complaint_probability: float,
        avg_bill_shock_pct: float,
        bills_count: int,
        shock_event_count: int,
    ) -> ServiceQualitySnapshot:
        snap = ServiceQualitySnapshot(
            year=year,
            avg_clarity=avg_clarity,
            avg_complaint_probability=avg_complaint_probability,
            avg_bill_shock_pct=avg_bill_shock_pct,
            bills_count=bills_count,
            shock_event_count=shock_event_count,
        )
        self._snapshots[year] = snap
        return snap

    def get(self, year: int) -> Optional[ServiceQualitySnapshot]:
        return self._snapshots.get(year)

    @property
    def all_snapshots(self) -> list[ServiceQualitySnapshot]:
        return sorted(self._snapshots.values(), key=lambda s: s.year)

    @property
    def red_years(self) -> list[ServiceQualitySnapshot]:
        return [s for s in self.all_snapshots if s.overall_rag == ServiceQualityRAG.RED]

    @property
    def amber_years(self) -> list[ServiceQualitySnapshot]:
        return [s for s in self.all_snapshots if s.overall_rag == ServiceQualityRAG.AMBER]

    @property
    def worst_clarity_year(self) -> Optional[ServiceQualitySnapshot]:
        if not self._snapshots:
            return None
        return min(self.all_snapshots, key=lambda s: s.avg_clarity)

    @property
    def worst_complaint_year(self) -> Optional[ServiceQualitySnapshot]:
        if not self._snapshots:
            return None
        return max(self.all_snapshots, key=lambda s: s.avg_complaint_probability)

    @property
    def worst_bill_shock_year(self) -> Optional[ServiceQualitySnapshot]:
        if not self._snapshots:
            return None
        return max(self.all_snapshots, key=lambda s: s.avg_bill_shock_pct)

    def is_improving(self) -> bool:
        """True if the last 2 recorded years show improving clarity."""
        snaps = self.all_snapshots
        if len(snaps) < 2:
            return False
        return snaps[-1].avg_clarity > snaps[-2].avg_clarity

    def quality_summary(self) -> str:
        snaps = self.all_snapshots
        if not snaps:
            return "No service quality data recorded."
        lines = [
            "Service Quality Summary",
            "Years recorded: {}".format(len(snaps)),
            "RED years: {}".format(len(self.red_years)),
            "AMBER years: {}".format(len(self.amber_years)),
        ]
        worst_c = self.worst_clarity_year
        if worst_c:
            lines.append("Worst clarity: {} ({:.3f})".format(worst_c.year, worst_c.avg_clarity))
        worst_s = self.worst_bill_shock_year
        if worst_s:
            lines.append("Worst bill shock: {} ({:.2f}%)".format(worst_s.year, worst_s.avg_bill_shock_pct))
        lines.append("Improving: {}".format(self.is_improving()))
        return chr(10).join(lines)
