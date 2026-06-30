"""Meter Operator (MOP) Appointment Register.

UK energy suppliers must ensure each supply point (MPAN) has an appointed
Meter Operator (MOP). The MOP installs, maintains, and decommissions the
physical meter asset, and holds a BSC qualification.

The MOP is distinct from:
  - MAP (Meter Asset Provider): owns the physical meter hardware (Phase GJ)
  - DA (Data Aggregator): aggregates HH reads from DCs for BSC settlement
  - DC (Data Collector): collects reads from the meter

When a supplier wins a new customer, they either inherit the existing MOP
or initiate a MOP change (via D0147/D0148 BSC data flows). The outgoing MOP
has a notice period of up to 5 working days.

MOP fees vary by service tier (basic/enhanced/premium) and are charged monthly
per MPAN as a non-commodity cost recovered through standing charges.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


def _add_working_days(date: dt.date, days: int) -> dt.date:
    current = date
    added = 0
    while added < days:
        current += dt.timedelta(days=1)
        if current.weekday() < 5:
            added += 1
    return current


_MOP_CHANGE_NOTICE_WD = 5  # D0147: 5 working days notice required


class MOPServiceTier(str, Enum):
    BASIC = "basic"           # read-on-request, annual visit
    ENHANCED = "enhanced"     # quarterly inspection, 24h fault response
    PREMIUM = "premium"       # proactive monitoring, 4h fault response


class MOPAppointmentStatus(str, Enum):
    ACTIVE = "active"
    PENDING_CHANGE = "pending_change"
    TERMINATED = "terminated"


class MOPChangeReason(str, Enum):
    SUPPLIER_CHOICE = "supplier_choice"
    METER_EXCHANGE = "meter_exchange"
    SMART_ROLLOUT = "smart_rollout"
    NON_PERFORMANCE = "non_performance"
    CUSTOMER_REQUEST = "customer_request"


_LIVE = frozenset({MOPAppointmentStatus.ACTIVE, MOPAppointmentStatus.PENDING_CHANGE})


@dataclass(frozen=True)
class MOPAppointmentRecord:
    appointment_id: str
    mpan: str
    mop_id: str
    tier: MOPServiceTier
    monthly_fee_gbp: float
    start_date: dt.date
    status: MOPAppointmentStatus
    end_date: Optional[dt.date] = None
    change_reason: Optional[MOPChangeReason] = None

    def is_active_as_of(self, as_of: dt.date) -> bool:
        if self.status not in (MOPAppointmentStatus.ACTIVE, MOPAppointmentStatus.PENDING_CHANGE):
            return False
        if as_of < self.start_date:
            return False
        if self.end_date is not None and as_of > self.end_date:
            return False
        return True

    def months_of_service(self, as_of: dt.date) -> int:
        end = self.end_date if self.end_date and self.end_date < as_of else as_of
        if end < self.start_date:
            return 0
        delta = (end.year - self.start_date.year) * 12 + (end.month - self.start_date.month)
        return max(0, delta)

    def total_cost_to_date_gbp(self, as_of: dt.date) -> float:
        return self.months_of_service(as_of) * self.monthly_fee_gbp

    def appointment_summary(self) -> str:
        return (
            f"MOP {self.appointment_id}: MPAN={self.mpan} "
            f"mop={self.mop_id} tier={self.tier.value} "
            f"GBP{self.monthly_fee_gbp:.2f}/mo [{self.status.value}]"
        )


class MOPAppointmentRegister:
    """Register of MOP appointments across all MPANs held by the supplier.

    Tracks current and historical MOP appointments, change notices, and
    cumulative service costs. Enforces the 5WD change notice period per
    BSC D0147 data flow requirements.
    """

    def __init__(self) -> None:
        self._records: List[MOPAppointmentRecord] = []
        self._counter: int = 0

    def _next_id(self) -> str:
        self._counter += 1
        return "MOP-" + str(self._counter).zfill(5)

    def _update(self, appointment_id: str, **kwargs) -> MOPAppointmentRecord:
        for i, rec in enumerate(self._records):
            if rec.appointment_id == appointment_id:
                updated = MOPAppointmentRecord(**{**rec.__dict__, **kwargs})
                self._records[i] = updated
                return updated
        raise KeyError(f"Appointment not found: {appointment_id}")

    def _get(self, appointment_id: str) -> MOPAppointmentRecord:
        rec = next((r for r in self._records if r.appointment_id == appointment_id), None)
        if rec is None:
            raise KeyError(f"Appointment not found: {appointment_id}")
        return rec

    def appoint_mop(
        self,
        mpan: str,
        mop_id: str,
        tier: MOPServiceTier,
        monthly_fee_gbp: float,
        start_date: dt.date,
        reason: Optional[MOPChangeReason] = None,
    ) -> MOPAppointmentRecord:
        """Record a new MOP appointment for an MPAN."""
        if monthly_fee_gbp < 0:
            raise ValueError("monthly_fee_gbp cannot be negative")
        rec = MOPAppointmentRecord(
            appointment_id=self._next_id(),
            mpan=mpan,
            mop_id=mop_id,
            tier=tier,
            monthly_fee_gbp=monthly_fee_gbp,
            start_date=start_date,
            status=MOPAppointmentStatus.ACTIVE,
            change_reason=reason,
        )
        self._records.append(rec)
        return rec

    def initiate_change(
        self,
        appointment_id: str,
        notice_date: dt.date,
    ) -> tuple:
        """Mark existing appointment as PENDING_CHANGE and compute effective change date.

        Returns (updated_record, change_effective_date) where change_effective_date
        is 5WD after notice_date per D0147 requirement.
        """
        rec = self._get(appointment_id)
        if rec.status != MOPAppointmentStatus.ACTIVE:
            raise ValueError(
                f"Can only initiate change on ACTIVE appointment, not {rec.status.value}"
            )
        change_effective = _add_working_days(notice_date, _MOP_CHANGE_NOTICE_WD)
        updated = self._update(appointment_id, status=MOPAppointmentStatus.PENDING_CHANGE)
        return updated, change_effective

    def complete_change(
        self,
        old_appointment_id: str,
        new_mop_id: str,
        new_tier: MOPServiceTier,
        new_fee_gbp: float,
        effective_date: dt.date,
        reason: MOPChangeReason,
    ) -> tuple:
        """Terminate old appointment and create new one on the same MPAN.

        Returns (terminated_record, new_record).
        """
        old = self._get(old_appointment_id)
        if old.status != MOPAppointmentStatus.PENDING_CHANGE:
            raise ValueError(
                f"Can only complete change on PENDING_CHANGE appointment, not {old.status.value}"
            )
        terminated = self._update(
            old_appointment_id,
            status=MOPAppointmentStatus.TERMINATED,
            end_date=effective_date,
        )
        new_rec = self.appoint_mop(
            mpan=terminated.mpan,
            mop_id=new_mop_id,
            tier=new_tier,
            monthly_fee_gbp=new_fee_gbp,
            start_date=effective_date,
            reason=reason,
        )
        return terminated, new_rec

    def terminate(
        self, appointment_id: str, end_date: dt.date
    ) -> MOPAppointmentRecord:
        """Terminate an appointment (e.g. loss of supply point)."""
        rec = self._get(appointment_id)
        if rec.status == MOPAppointmentStatus.TERMINATED:
            raise ValueError("Appointment is already terminated")
        return self._update(appointment_id, status=MOPAppointmentStatus.TERMINATED, end_date=end_date)

    def appointments_for_mpan(self, mpan: str) -> List[MOPAppointmentRecord]:
        return [r for r in self._records if r.mpan == mpan]

    def current_mop_for_mpan(
        self, mpan: str, as_of: dt.date
    ) -> Optional[MOPAppointmentRecord]:
        """Return the active appointment for the given MPAN as of a date, or None."""
        live = [r for r in self._records if r.mpan == mpan and r.is_active_as_of(as_of)]
        return live[-1] if live else None

    def active_appointments(self, as_of: dt.date) -> List[MOPAppointmentRecord]:
        return [r for r in self._records if r.is_active_as_of(as_of)]

    def pending_changes(self, as_of: dt.date) -> List[MOPAppointmentRecord]:
        return [
            r for r in self._records
            if r.status == MOPAppointmentStatus.PENDING_CHANGE and r.is_active_as_of(as_of)
        ]

    def mpans_without_mop(self, all_mpans: List[str], as_of: dt.date) -> List[str]:
        """Return MPANs from the given list that have no live appointment as of a date.

        A gap in MOP coverage is an SLC breach and creates settlement risk.
        """
        covered = {r.mpan for r in self._records if r.is_active_as_of(as_of)}
        return [m for m in all_mpans if m not in covered]

    def appointments_by_tier(self, tier: MOPServiceTier) -> List[MOPAppointmentRecord]:
        return [r for r in self._records if r.tier == tier]

    def total_monthly_fees_gbp(self, as_of: dt.date) -> float:
        """Sum of monthly fees across all currently active appointments."""
        return sum(r.monthly_fee_gbp for r in self._records if r.is_active_as_of(as_of))

    def total_fees_to_date_gbp(self, as_of: dt.date) -> float:
        """Cumulative fees paid across all appointments (active and terminated)."""
        return sum(r.total_cost_to_date_gbp(as_of) for r in self._records)

    def mop_provider_breakdown(self, as_of: dt.date) -> dict:
        """Count of active appointments per MOP provider ID."""
        result = {}
        for r in self.active_appointments(as_of):
            result[r.mop_id] = result.get(r.mop_id, 0) + 1
        return result

    def mop_summary(self, as_of: dt.date) -> str:
        active = self.active_appointments(as_of)
        pending = self.pending_changes(as_of)
        total_fees = self.total_monthly_fees_gbp(as_of)
        return (
            f"MOPRegister: {len(active)} active appointments "
            f"({len(pending)} pending change) "
            f"GBP{total_fees:.2f}/mo total fees"
        )
