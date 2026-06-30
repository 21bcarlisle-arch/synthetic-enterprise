"""Revenue Protection Visit Register — GS(SS)5 site investigation obligation.

When theft risk scoring flags a site, a Revenue Protection (RP) visit is
scheduled. The outcome determines whether the case progresses to the
energy theft book (confirmed tamper) or is cleared.

Sits between theft_risk_scoring_register (risk score) and
energy_theft_book (confirmed theft / DNO notification).
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class Fuel(str, Enum):
    ELECTRICITY = "electricity"
    GAS = "gas"


class RPVTrigger(str, Enum):
    THEFT_RISK_SCORE = "theft_risk_score"
    CONSUMPTION_ANOMALY = "consumption_anomaly"
    ANONYMOUS_TIP = "anonymous_tip"
    ROUTINE_INSPECTION = "routine_inspection"
    POLICE_REQUEST = "police_request"


class RPVStatus(str, Enum):
    SCHEDULED = "scheduled"
    VISITED_CLEAR = "visited_clear"
    VISITED_TAMPER_FOUND = "visited_tamper_found"
    VISITED_VACANT = "visited_vacant"
    ABORTED_ACCESS_DENIED = "aborted_access_denied"
    CANCELLED = "cancelled"


class AccessOutcome(str, Enum):
    CLEAR = "clear"
    TAMPER_FOUND = "tamper_found"
    METER_ABSENT = "meter_absent"
    PROPERTY_VACANT = "property_vacant"
    ACCESS_DENIED = "access_denied"


# Status sets
_TERMINAL = frozenset({
    RPVStatus.VISITED_CLEAR,
    RPVStatus.VISITED_TAMPER_FOUND,
    RPVStatus.VISITED_VACANT,
    RPVStatus.ABORTED_ACCESS_DENIED,
    RPVStatus.CANCELLED,
})

_COMPLETED = frozenset({
    RPVStatus.VISITED_CLEAR,
    RPVStatus.VISITED_TAMPER_FOUND,
    RPVStatus.VISITED_VACANT,
})

_OUTCOME_TO_STATUS = {
    AccessOutcome.CLEAR: RPVStatus.VISITED_CLEAR,
    AccessOutcome.TAMPER_FOUND: RPVStatus.VISITED_TAMPER_FOUND,
    AccessOutcome.METER_ABSENT: RPVStatus.VISITED_TAMPER_FOUND,
    AccessOutcome.PROPERTY_VACANT: RPVStatus.VISITED_VACANT,
    AccessOutcome.ACCESS_DENIED: RPVStatus.ABORTED_ACCESS_DENIED,
}


@dataclass(frozen=True)
class RevenueProtectionVisitRecord:
    visit_id: str
    account_id: str
    mpan_or_mprn: str
    fuel: Fuel
    trigger: RPVTrigger
    status: RPVStatus
    scheduled_date: dt.date
    completed_date: Optional[dt.date] = None
    access_outcome: Optional[AccessOutcome] = None
    investigator_id: Optional[str] = None
    # Estimated revenue loss if tamper found (GBP)
    estimated_loss_gbp: Optional[float] = None

    @property
    def is_terminal(self) -> bool:
        return self.status in _TERMINAL

    @property
    def is_completed(self) -> bool:
        return self.status in _COMPLETED

    def is_overdue(self, as_of: dt.date) -> bool:
        """Scheduled but past the scheduled date without an outcome."""
        return self.status == RPVStatus.SCHEDULED and as_of > self.scheduled_date

    @property
    def requires_theft_investigation(self) -> bool:
        return self.access_outcome in (
            AccessOutcome.TAMPER_FOUND,
            AccessOutcome.METER_ABSENT,
        )

    def visit_summary(self) -> str:
        parts = [
            f"RPV {self.visit_id}: {self.account_id} {self.fuel.value} "
            f"[{self.trigger.value}] [{self.status.value}]"
        ]
        if self.access_outcome:
            parts.append(f"outcome={self.access_outcome.value}")
        if self.estimated_loss_gbp is not None:
            parts.append(f"loss=£{self.estimated_loss_gbp:,.0f}")
        return " | ".join(parts)


class RevenueProtectionVisitRegister:
    """Register of revenue protection site visits."""

    def __init__(self) -> None:
        self._records: List[RevenueProtectionVisitRecord] = []
        self._counter: int = 0

    def _next_id(self) -> str:
        self._counter += 1
        return "RPV-" + str(self._counter).zfill(5)

    def _update(self, visit_id: str, **kwargs) -> RevenueProtectionVisitRecord:
        for i, rec in enumerate(self._records):
            if rec.visit_id == visit_id:
                updated = RevenueProtectionVisitRecord(**{**rec.__dict__, **kwargs})
                self._records[i] = updated
                return updated
        raise KeyError(f"Visit not found: {visit_id}")

    def schedule_visit(
        self,
        account_id: str,
        mpan_or_mprn: str,
        fuel: Fuel,
        trigger: RPVTrigger,
        scheduled_date: dt.date,
        investigator_id: Optional[str] = None,
    ) -> RevenueProtectionVisitRecord:
        rec = RevenueProtectionVisitRecord(
            visit_id=self._next_id(),
            account_id=account_id,
            mpan_or_mprn=mpan_or_mprn,
            fuel=fuel,
            trigger=trigger,
            status=RPVStatus.SCHEDULED,
            scheduled_date=scheduled_date,
            investigator_id=investigator_id,
        )
        self._records.append(rec)
        return rec

    def record_outcome(
        self,
        visit_id: str,
        access_outcome: AccessOutcome,
        completed_date: dt.date,
        estimated_loss_gbp: Optional[float] = None,
    ) -> RevenueProtectionVisitRecord:
        rec = next((r for r in self._records if r.visit_id == visit_id), None)
        if rec is None:
            raise KeyError(f"Visit not found: {visit_id}")
        if rec.status != RPVStatus.SCHEDULED:
            raise ValueError(f"Cannot record outcome for {rec.status.value} visit")
        new_status = _OUTCOME_TO_STATUS[access_outcome]
        return self._update(
            visit_id,
            status=new_status,
            access_outcome=access_outcome,
            completed_date=completed_date,
            estimated_loss_gbp=estimated_loss_gbp,
        )

    def cancel(self, visit_id: str) -> RevenueProtectionVisitRecord:
        rec = next((r for r in self._records if r.visit_id == visit_id), None)
        if rec is None:
            raise KeyError(f"Visit not found: {visit_id}")
        if rec.status != RPVStatus.SCHEDULED:
            raise ValueError(f"Cannot cancel {rec.status.value} visit")
        return self._update(visit_id, status=RPVStatus.CANCELLED)

    # ── Queries ──────────────────────────────────────────────────────────────

    @property
    def all_records(self) -> List[RevenueProtectionVisitRecord]:
        return list(self._records)

    @property
    def scheduled_visits(self) -> List[RevenueProtectionVisitRecord]:
        return [r for r in self._records if r.status == RPVStatus.SCHEDULED]

    def overdue_visits(self, as_of: dt.date) -> List[RevenueProtectionVisitRecord]:
        return [r for r in self._records if r.is_overdue(as_of)]

    @property
    def visits_requiring_investigation(self) -> List[RevenueProtectionVisitRecord]:
        return [r for r in self._records if r.requires_theft_investigation]

    def visits_for_account(self, account_id: str) -> List[RevenueProtectionVisitRecord]:
        return [r for r in self._records if r.account_id == account_id]

    def visits_for_mpan(self, mpan_or_mprn: str) -> List[RevenueProtectionVisitRecord]:
        return [r for r in self._records if r.mpan_or_mprn == mpan_or_mprn]

    def by_trigger(self, trigger: RPVTrigger) -> List[RevenueProtectionVisitRecord]:
        return [r for r in self._records if r.trigger == trigger]

    def by_fuel(self, fuel: Fuel) -> List[RevenueProtectionVisitRecord]:
        return [r for r in self._records if r.fuel == fuel]

    @property
    def total_estimated_loss_gbp(self) -> float:
        return sum(
            r.estimated_loss_gbp
            for r in self._records
            if r.requires_theft_investigation and r.estimated_loss_gbp is not None
        )

    def tamper_detection_rate_pct(self) -> Optional[float]:
        """Percentage of completed visits where tamper/meter-absent was found."""
        completed = [r for r in self._records if r.is_completed]
        if not completed:
            return None
        tamper = sum(1 for r in completed if r.requires_theft_investigation)
        return round(tamper / len(completed) * 100, 2)

    def access_denial_rate_pct(self) -> Optional[float]:
        """Percentage of terminal visits where access was denied."""
        terminal = [r for r in self._records if r.is_terminal]
        if not terminal:
            return None
        denied = sum(1 for r in terminal if r.status == RPVStatus.ABORTED_ACCESS_DENIED)
        return round(denied / len(terminal) * 100, 2)

    def rp_visit_summary(self, as_of: dt.date) -> str:
        total = len(self._records)
        scheduled = len(self.scheduled_visits)
        overdue = len(self.overdue_visits(as_of))
        requiring = len(self.visits_requiring_investigation)
        loss = self.total_estimated_loss_gbp
        rate = self.tamper_detection_rate_pct()
        rate_str = f"{rate:.1f}%" if rate is not None else "N/A"
        return (
            f"RP Visits: {total} total | {scheduled} scheduled "
            f"| {overdue} overdue | {requiring} require investigation "
            f"| tamper rate {rate_str} | est. loss £{loss:,.0f}"
        )
