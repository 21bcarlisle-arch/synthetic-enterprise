"""CSS Performance Register (Phase GA).

The Central Switching Service (CSS) launched 22 June 2023, replacing the legacy
MPAS/MPRN switching process. It guarantees:

  - 5 Working Day (5WD) switching guarantee for all domestic customers
  - 48-hour objection window (previously 5 working days)
  - Gain/Loss notification within 1 working day of switch completion
  - Supplier must complete switch within 5WD or face Ofgem enforcement

CSS is operated by Xoserve (gas) and Elexon (electricity) under Ofgem licence.
Monthly performance data is published on the NESO/Elexon CSS portal.

The company must:
  1. Monitor its own 5WD compliance rate (breaches attract regulatory attention)
  2. Report breaches of the 5WD guarantee to the CSS operator
  3. Track ET (Erroneous Transfer) rates per 1,000 switches
  4. Submit quarterly CSS performance data to Ofgem

Distinct from switch_governance.py (objections, cooling-off, erroneous
transfer resolution) — this register tracks aggregate CSS KPI performance.

CSS went live 2023-06-22. Records for earlier dates are rejected.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

_CSS_GO_LIVE = dt.date(2023, 6, 22)
_CSS_SLA_WORKING_DAYS = 5

_WORKING_DAY_OFFSETS = (0, 1, 2, 3, 4)  # Mon-Fri pattern used in add-working-days


def _add_working_days(start: dt.date, n: int) -> dt.date:
    """Return the date n working days after start (skips weekends only)."""
    current = start
    remaining = n
    while remaining > 0:
        current += dt.timedelta(days=1)
        if current.weekday() < 5:  # Mon-Fri
            remaining -= 1
    return current


class SwitchOutcome(str, Enum):
    PENDING = "pending"
    COMPLETED_ON_TIME = "completed_on_time"   # within 5WD
    COMPLETED_LATE = "completed_late"          # after 5WD
    CANCELLED_COOLING_OFF = "cancelled_cooling_off"
    CANCELLED_OBJECTION = "cancelled_objection"
    ERRONEOUS_TRANSFER = "erroneous_transfer"


@dataclass(frozen=True)
class CSSPerformanceRecord:
    switch_id: str                     # SW-NNNNN
    request_date: dt.date              # date switch was requested
    fuel: str                          # "electricity" or "gas"
    outcome: SwitchOutcome = SwitchOutcome.PENDING
    completion_date: Optional[dt.date] = None

    @property
    def sla_deadline(self) -> dt.date:
        return _add_working_days(self.request_date, _CSS_SLA_WORKING_DAYS)

    @property
    def is_completed(self) -> bool:
        return self.outcome in (
            SwitchOutcome.COMPLETED_ON_TIME,
            SwitchOutcome.COMPLETED_LATE,
        )

    @property
    def is_cancelled(self) -> bool:
        return self.outcome in (
            SwitchOutcome.CANCELLED_COOLING_OFF,
            SwitchOutcome.CANCELLED_OBJECTION,
        )

    @property
    def is_compliant(self) -> bool:
        return self.outcome == SwitchOutcome.COMPLETED_ON_TIME

    @property
    def is_late(self) -> bool:
        return self.outcome == SwitchOutcome.COMPLETED_LATE

    @property
    def is_et(self) -> bool:
        return self.outcome == SwitchOutcome.ERRONEOUS_TRANSFER

    def days_to_complete(self) -> Optional[int]:
        if self.completion_date is None:
            return None
        return (self.completion_date - self.request_date).days

    def record_summary(self) -> str:
        status = self.outcome.value
        if self.completion_date:
            return (
                f"CSS {self.switch_id} ({self.fuel}): {status} "
                f"on {self.completion_date} (SLA={self.sla_deadline})"
            )
        return f"CSS {self.switch_id} ({self.fuel}): {status} (SLA={self.sla_deadline})"


class CSSPerformanceRegister:

    def __init__(self) -> None:
        self._records: List[CSSPerformanceRecord] = []
        self._counter: int = 0

    def _next_id(self) -> str:
        self._counter += 1
        return f"SW-{self._counter:05d}"

    def record_switch(
        self,
        request_date: dt.date,
        fuel: str,
    ) -> CSSPerformanceRecord:
        if request_date < _CSS_GO_LIVE:
            raise ValueError(
                f"CSS did not go live until {_CSS_GO_LIVE}; "
                f"request_date={request_date} is invalid"
            )
        if fuel not in ("electricity", "gas"):
            raise ValueError(f"fuel must be 'electricity' or 'gas'; got '{fuel}'")
        record = CSSPerformanceRecord(
            switch_id=self._next_id(),
            request_date=request_date,
            fuel=fuel,
        )
        self._records.append(record)
        return record

    def _update(self, switch_id: str, **kwargs) -> CSSPerformanceRecord:
        for i, r in enumerate(self._records):
            if r.switch_id == switch_id:
                updated = CSSPerformanceRecord(
                    switch_id=r.switch_id,
                    request_date=r.request_date,
                    fuel=r.fuel,
                    outcome=kwargs.get("outcome", r.outcome),
                    completion_date=kwargs.get("completion_date", r.completion_date),
                )
                self._records[i] = updated
                return updated
        raise KeyError(f"Switch record {switch_id} not found")

    def complete_switch(
        self, switch_id: str, completion_date: dt.date
    ) -> CSSPerformanceRecord:
        for r in self._records:
            if r.switch_id == switch_id:
                outcome = (
                    SwitchOutcome.COMPLETED_ON_TIME
                    if completion_date <= r.sla_deadline
                    else SwitchOutcome.COMPLETED_LATE
                )
                return self._update(
                    switch_id, outcome=outcome, completion_date=completion_date
                )
        raise KeyError(f"Switch record {switch_id} not found")

    def cancel_cooling_off(self, switch_id: str) -> CSSPerformanceRecord:
        return self._update(switch_id, outcome=SwitchOutcome.CANCELLED_COOLING_OFF)

    def cancel_objection(self, switch_id: str) -> CSSPerformanceRecord:
        return self._update(switch_id, outcome=SwitchOutcome.CANCELLED_OBJECTION)

    def mark_erroneous_transfer(self, switch_id: str) -> CSSPerformanceRecord:
        return self._update(switch_id, outcome=SwitchOutcome.ERRONEOUS_TRANSFER)

    def _completed(self) -> List[CSSPerformanceRecord]:
        return [r for r in self._records if r.is_completed]

    def on_time_completions(self) -> List[CSSPerformanceRecord]:
        return [r for r in self._records if r.is_compliant]

    def late_completions(self) -> List[CSSPerformanceRecord]:
        return [r for r in self._records if r.is_late]

    def pending_switches(self) -> List[CSSPerformanceRecord]:
        return [r for r in self._records if r.outcome == SwitchOutcome.PENDING]

    def erroneous_transfers(self) -> List[CSSPerformanceRecord]:
        return [r for r in self._records if r.is_et]

    def compliance_rate_pct(self) -> Optional[float]:
        completed = self._completed()
        if not completed:
            return None
        on_time = sum(1 for r in completed if r.is_compliant)
        return round(100.0 * on_time / len(completed), 2)

    def et_rate_per_1000(self) -> Optional[float]:
        completed = self._completed()
        if not completed:
            return None
        n_et = len(self.erroneous_transfers())
        return round(1000.0 * n_et / len(completed), 2)

    def switches_for_fuel(self, fuel: str) -> List[CSSPerformanceRecord]:
        return [r for r in self._records if r.fuel == fuel]

    def css_performance_summary(self) -> str:
        n = len(self._records)
        n_pending = len(self.pending_switches())
        rate = self.compliance_rate_pct()
        rate_str = f"{rate:.1f}%" if rate is not None else "n/a"
        n_et = len(self.erroneous_transfers())
        return (
            f"CSS Performance Register: {n} switches "
            f"({n_pending} pending, {rate_str} 5WD compliance, {n_et} ETs)."
        )
