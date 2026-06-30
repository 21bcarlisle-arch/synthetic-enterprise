"""Gas Safety Incident Register.

Gas Safety (Installation and Use) Regulations 1998 (SI 1998/2451) and RIDDOR
(Reporting of Injuries, Diseases and Dangerous Occurrences Regulations 2013).

When a gas supplier is notified of a gas safety incident, it must:
1. Make the supply safe immediately (isolate if required).
2. Investigate and arrange Gas Safe registered engineer response.
3. Report RIDDOR-reportable events (dangerous gas fittings, CO incidents,
   gas escapes leading to injury) to HSE within 15 days.
4. Maintain records for 3 years (GSIUR Reg 35).

Epistemic: company learns of incidents via customer contact, Gas Safe
notification, or emergency response; it does not have real-time gas
network sensor data.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class GasSafetyIncidentType(str, Enum):
    GAS_ESCAPE = "gas_escape"
    CO_SUSPECTED = "co_suspected"
    CO_CONFIRMED = "co_confirmed"
    DANGEROUS_FITTING = "dangerous_fitting"
    METER_DAMAGE = "meter_damage"
    EXPLOSION = "explosion"
    FIRE_GAS_RELATED = "fire_gas_related"


class IncidentSeverity(str, Enum):
    LOW = "low"          # no injury, minor escape
    MEDIUM = "medium"    # property damage or medical attention
    HIGH = "high"        # hospitalisation or significant escape
    FATAL = "fatal"      # fatality


class IncidentStatus(str, Enum):
    REPORTED = "reported"           # initial notification received
    ENGINEER_DISPATCHED = "engineer_dispatched"
    SUPPLY_ISOLATED = "supply_isolated"
    MADE_SAFE = "made_safe"
    RIDDOR_NOTIFIED = "riddor_notified"
    CLOSED = "closed"


# RIDDOR-reportable if type involves injury or dangerous gas fitting
_RIDDOR_TYPES = frozenset({
    GasSafetyIncidentType.CO_CONFIRMED,
    GasSafetyIncidentType.EXPLOSION,
    GasSafetyIncidentType.FIRE_GAS_RELATED,
    GasSafetyIncidentType.DANGEROUS_FITTING,
})

# RIDDOR: 15 calendar days from occurrence
_RIDDOR_DAYS = 15

_OPEN = frozenset({
    IncidentStatus.REPORTED,
    IncidentStatus.ENGINEER_DISPATCHED,
    IncidentStatus.SUPPLY_ISOLATED,
    IncidentStatus.MADE_SAFE,
})

_RESOLUTION_REQUIRED_BEFORE_CLOSE = frozenset({
    IncidentStatus.MADE_SAFE,
    IncidentStatus.RIDDOR_NOTIFIED,
})


@dataclass(frozen=True)
class GasSafetyIncidentRecord:
    incident_id: str
    account_id: str
    mprn: str
    incident_type: GasSafetyIncidentType
    severity: IncidentSeverity
    status: IncidentStatus
    reported_date: dt.date
    engineer_dispatched_date: Optional[dt.date] = None
    made_safe_date: Optional[dt.date] = None
    riddor_notified_date: Optional[dt.date] = None
    closed_date: Optional[dt.date] = None
    injuries_count: int = 0
    gas_safe_ref: Optional[str] = None

    @property
    def is_open(self) -> bool:
        return self.status in _OPEN

    @property
    def requires_riddor_notification(self) -> bool:
        return (
            self.incident_type in _RIDDOR_TYPES
            or self.severity in (IncidentSeverity.HIGH, IncidentSeverity.FATAL)
            or self.injuries_count > 0
        )

    @property
    def riddor_deadline(self) -> Optional[dt.date]:
        if not self.requires_riddor_notification:
            return None
        return self.reported_date + dt.timedelta(days=_RIDDOR_DAYS)

    def is_riddor_overdue(self, as_of: dt.date) -> bool:
        if not self.requires_riddor_notification:
            return False
        if self.riddor_notified_date is not None:
            return False
        deadline = self.riddor_deadline
        return deadline is not None and as_of > deadline

    def incident_summary(self) -> str:
        parts = [
            f"Gas Incident {self.incident_id}: {self.account_id} {self.mprn} "
            f"{self.incident_type.value} [{self.severity.value}] [{self.status.value}]"
        ]
        if self.injuries_count:
            parts.append(f"injuries={self.injuries_count}")
        if self.requires_riddor_notification and not self.riddor_notified_date:
            parts.append("RIDDOR_PENDING")
        return " | ".join(parts)


class GasSafetyIncidentRegister:
    """Register of gas safety incidents under GSIUR 1998 and RIDDOR 2013."""

    def __init__(self) -> None:
        self._records: List[GasSafetyIncidentRecord] = []
        self._counter: int = 0

    def _next_id(self) -> str:
        self._counter += 1
        return "GSI-" + str(self._counter).zfill(5)

    def _update(self, incident_id: str, **kwargs) -> GasSafetyIncidentRecord:
        for i, rec in enumerate(self._records):
            if rec.incident_id == incident_id:
                updated = GasSafetyIncidentRecord(**{**rec.__dict__, **kwargs})
                self._records[i] = updated
                return updated
        raise KeyError(f"Incident not found: {incident_id}")

    def report_incident(
        self,
        account_id: str,
        mprn: str,
        incident_type: GasSafetyIncidentType,
        severity: IncidentSeverity,
        reported_date: dt.date,
        injuries_count: int = 0,
        gas_safe_ref: Optional[str] = None,
    ) -> GasSafetyIncidentRecord:
        if injuries_count < 0:
            raise ValueError("injuries_count cannot be negative")
        rec = GasSafetyIncidentRecord(
            incident_id=self._next_id(),
            account_id=account_id,
            mprn=mprn,
            incident_type=incident_type,
            severity=severity,
            status=IncidentStatus.REPORTED,
            reported_date=reported_date,
            injuries_count=injuries_count,
            gas_safe_ref=gas_safe_ref,
        )
        self._records.append(rec)
        return rec

    def dispatch_engineer(
        self, incident_id: str, dispatch_date: dt.date, gas_safe_ref: Optional[str] = None
    ) -> GasSafetyIncidentRecord:
        rec = next((r for r in self._records if r.incident_id == incident_id), None)
        if rec is None:
            raise KeyError(f"Incident not found: {incident_id}")
        if rec.status != IncidentStatus.REPORTED:
            raise ValueError(f"Cannot dispatch engineer for {rec.status.value} incident")
        kwargs = {"status": IncidentStatus.ENGINEER_DISPATCHED, "engineer_dispatched_date": dispatch_date}
        if gas_safe_ref is not None:
            kwargs["gas_safe_ref"] = gas_safe_ref
        return self._update(incident_id, **kwargs)

    def isolate_supply(self, incident_id: str) -> GasSafetyIncidentRecord:
        rec = next((r for r in self._records if r.incident_id == incident_id), None)
        if rec is None:
            raise KeyError(f"Incident not found: {incident_id}")
        if rec.status not in (IncidentStatus.REPORTED, IncidentStatus.ENGINEER_DISPATCHED):
            raise ValueError(f"Cannot isolate supply for {rec.status.value} incident")
        return self._update(incident_id, status=IncidentStatus.SUPPLY_ISOLATED)

    def mark_made_safe(self, incident_id: str, made_safe_date: dt.date) -> GasSafetyIncidentRecord:
        rec = next((r for r in self._records if r.incident_id == incident_id), None)
        if rec is None:
            raise KeyError(f"Incident not found: {incident_id}")
        if rec.status not in _OPEN:
            raise ValueError(f"Cannot mark made safe: {rec.status.value}")
        return self._update(incident_id, status=IncidentStatus.MADE_SAFE, made_safe_date=made_safe_date)

    def notify_riddor(self, incident_id: str, notification_date: dt.date) -> GasSafetyIncidentRecord:
        rec = next((r for r in self._records if r.incident_id == incident_id), None)
        if rec is None:
            raise KeyError(f"Incident not found: {incident_id}")
        if not rec.requires_riddor_notification:
            raise ValueError("This incident does not require RIDDOR notification")
        if rec.status not in _OPEN:
            raise ValueError(f"Cannot notify RIDDOR for {rec.status.value} incident")
        return self._update(incident_id, status=IncidentStatus.RIDDOR_NOTIFIED,
                            riddor_notified_date=notification_date)

    def close_incident(self, incident_id: str, closed_date: dt.date) -> GasSafetyIncidentRecord:
        rec = next((r for r in self._records if r.incident_id == incident_id), None)
        if rec is None:
            raise KeyError(f"Incident not found: {incident_id}")
        if rec.status not in _RESOLUTION_REQUIRED_BEFORE_CLOSE:
            raise ValueError(
                f"Incident must be made safe (or RIDDOR notified if required) before closing. "
                f"Current status: {rec.status.value}"
            )
        return self._update(incident_id, status=IncidentStatus.CLOSED, closed_date=closed_date)

    # ── Queries ──────────────────────────────────────────────────────────────

    @property
    def all_records(self) -> List[GasSafetyIncidentRecord]:
        return list(self._records)

    @property
    def open_incidents(self) -> List[GasSafetyIncidentRecord]:
        return [r for r in self._records if r.is_open]

    def riddor_overdue(self, as_of: dt.date) -> List[GasSafetyIncidentRecord]:
        return [r for r in self._records if r.is_riddor_overdue(as_of)]

    def riddor_required_open(self) -> List[GasSafetyIncidentRecord]:
        return [r for r in self._records
                if r.is_open and r.requires_riddor_notification and r.riddor_notified_date is None]

    def incidents_for_account(self, account_id: str) -> List[GasSafetyIncidentRecord]:
        return [r for r in self._records if r.account_id == account_id]

    def incidents_by_type(self, incident_type: GasSafetyIncidentType) -> List[GasSafetyIncidentRecord]:
        return [r for r in self._records if r.incident_type == incident_type]

    def incidents_by_severity(self, severity: IncidentSeverity) -> List[GasSafetyIncidentRecord]:
        return [r for r in self._records if r.severity == severity]

    @property
    def total_injuries(self) -> int:
        return sum(r.injuries_count for r in self._records)

    @property
    def fatal_incidents(self) -> List[GasSafetyIncidentRecord]:
        return [r for r in self._records if r.severity == IncidentSeverity.FATAL]

    def gas_safety_register_summary(self, as_of: dt.date) -> str:
        total = len(self._records)
        open_count = len(self.open_incidents)
        overdue = len(self.riddor_overdue(as_of))
        pending_riddor = len(self.riddor_required_open())
        injuries = self.total_injuries
        fatals = len(self.fatal_incidents)
        return (
            f"Gas Safety Incidents: {total} total | {open_count} open "
            f"| {pending_riddor} RIDDOR pending | {overdue} RIDDOR overdue "
            f"| {injuries} injuries | {fatals} fatal"
        )
