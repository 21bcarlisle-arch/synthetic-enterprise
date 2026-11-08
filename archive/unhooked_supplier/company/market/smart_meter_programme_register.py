"""Smart Meter Installation Programme Register (Phase GI).

Tracks the SMETS2 smart meter rollout programme at the supplier level.

Distinct from dcc_meter_registration.py (Phase GB), which tracks whether
a specific installed SMETS2 meter has been successfully registered with
the DCC. This module manages the installation appointments and outcomes
before and during the physical installation visit.

Ofgem mandated rollout obligations:
  - Original target: 100% coverage by end of 2020
  - Extended deadline: 2025 (meters of working class at each property)
  - Annual rollout plans must be submitted to Ofgem
  - Annual progress reports published; non-delivery may attract enforcement
  - Smart Meter Implementation Programme (SMIP) overseen by BEIS/DBT

Outcome categories based on real DNO/supplier experience:
  - COMPLETED: meter successfully installed and tested
  - CUSTOMER_REFUSED: customer declined at point of appointment (SLC 21B:
    suppliers cannot force installation on domestic customers)
  - PROPERTY_UNSUITABLE: physical constraints prevent installation (e.g. no
    phone signal for comms hub, meter in communal area requiring landlord)
  - ACCESS_FAILED: engineer arrived but couldn't gain entry
  - ABORTED_ENGINEER: engineer aborted during installation (unforeseen issue)
  - FAILED_TECHNICAL: installation attempted but meter failed commissioning

SLC 21B: no compulsion on domestic customers; cannot delay switching for
smart meter installation; DCC registration must be attempted within 10WD
of installation (tracked in dcc_meter_registration.py).

Access failure rate: typically 8-15% of all appointments in real suppliers.
Refusal rate: 3-8%; technical failure: <2%.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple


class SMETSGeneration(str, Enum):
    SMETS1 = "smets1"           # pre-DCC; not DCC-interoperable
    SMETS2 = "smets2"           # DCC-connected; full interoperability
    DCC_SMETS1 = "dcc_smets1"  # SMETS1 enrolled in DCC (SMETS1 upgrade programme)


class AppointmentSlot(str, Enum):
    MORNING = "morning"        # 08:00-13:00
    AFTERNOON = "afternoon"    # 13:00-18:00
    EVENING = "evening"        # 16:00-20:00 (premium/evening appointments)
    ALL_DAY = "all_day"        # flexible (sometimes offered to high-priority customers)


class InstallationOutcome(str, Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CUSTOMER_REFUSED = "customer_refused"
    PROPERTY_UNSUITABLE = "property_unsuitable"
    ACCESS_FAILED = "access_failed"
    ABORTED_ENGINEER = "aborted_engineer"
    FAILED_TECHNICAL = "failed_technical"


_SUCCESSFUL = frozenset({InstallationOutcome.COMPLETED})
_ACCESS_ISSUES = frozenset({
    InstallationOutcome.ACCESS_FAILED,
    InstallationOutcome.CUSTOMER_REFUSED,
})
_TECHNICAL_FAILURES = frozenset({
    InstallationOutcome.ABORTED_ENGINEER,
    InstallationOutcome.FAILED_TECHNICAL,
})


@dataclass(frozen=True)
class InstallationAppointmentRecord:
    appt_id: str                         # SMAPPT-NNNNN
    account_id: str
    mpan: str
    fuel: str                            # "electricity" or "gas" or "dual_fuel"
    appointment_date: dt.date
    slot: AppointmentSlot
    smets_generation: SMETSGeneration = SMETSGeneration.SMETS2
    outcome: InstallationOutcome = InstallationOutcome.SCHEDULED
    outcome_date: Optional[dt.date] = None
    engineer_ref: Optional[str] = None
    notes: str = ""

    @property
    def is_complete(self) -> bool:
        return self.outcome == InstallationOutcome.COMPLETED

    @property
    def is_access_issue(self) -> bool:
        return self.outcome in _ACCESS_ISSUES

    @property
    def is_technical_failure(self) -> bool:
        return self.outcome in _TECHNICAL_FAILURES

    @property
    def is_terminal(self) -> bool:
        return self.outcome != InstallationOutcome.SCHEDULED

    def appt_summary(self) -> str:
        return (
            f"SMAPPT {self.appt_id} acct={self.account_id} "
            f"mpan={self.mpan} {self.appointment_date} [{self.outcome.value}]"
        )


class SmartMeterProgrammeRegister:

    def __init__(self) -> None:
        self._records: List[InstallationAppointmentRecord] = []
        self._counter: int = 0

    def _next_id(self) -> str:
        self._counter += 1
        return f"SMAPPT-{self._counter:05d}"

    def schedule_appointment(
        self,
        account_id: str,
        mpan: str,
        fuel: str,
        appointment_date: dt.date,
        slot: AppointmentSlot = AppointmentSlot.MORNING,
        smets_generation: SMETSGeneration = SMETSGeneration.SMETS2,
        engineer_ref: Optional[str] = None,
    ) -> InstallationAppointmentRecord:
        if fuel not in ("electricity", "gas", "dual_fuel"):
            raise ValueError(f"Invalid fuel: {fuel}")
        record = InstallationAppointmentRecord(
            appt_id=self._next_id(),
            account_id=account_id,
            mpan=mpan,
            fuel=fuel,
            appointment_date=appointment_date,
            slot=slot,
            smets_generation=smets_generation,
            engineer_ref=engineer_ref,
        )
        self._records.append(record)
        return record

    def _update(self, appt_id: str, **kwargs) -> InstallationAppointmentRecord:
        for i, r in enumerate(self._records):
            if r.appt_id == appt_id:
                updated = InstallationAppointmentRecord(
                    appt_id=r.appt_id, account_id=r.account_id,
                    mpan=r.mpan, fuel=r.fuel,
                    appointment_date=r.appointment_date, slot=r.slot,
                    smets_generation=kwargs.get("smets_generation", r.smets_generation),
                    outcome=kwargs.get("outcome", r.outcome),
                    outcome_date=kwargs.get("outcome_date", r.outcome_date),
                    engineer_ref=kwargs.get("engineer_ref", r.engineer_ref),
                    notes=kwargs.get("notes", r.notes),
                )
                self._records[i] = updated
                return updated
        raise KeyError(f"Appointment {appt_id} not found")

    def record_outcome(
        self,
        appt_id: str,
        outcome: InstallationOutcome,
        outcome_date: dt.date,
        notes: str = "",
    ) -> InstallationAppointmentRecord:
        return self._update(appt_id, outcome=outcome, outcome_date=outcome_date, notes=notes)

    def completions(self) -> List[InstallationAppointmentRecord]:
        return [r for r in self._records if r.is_complete]

    def access_failures(self) -> List[InstallationAppointmentRecord]:
        return [r for r in self._records if r.is_access_issue]

    def technical_failures(self) -> List[InstallationAppointmentRecord]:
        return [r for r in self._records if r.is_technical_failure]

    def customer_refusals(self) -> List[InstallationAppointmentRecord]:
        return [r for r in self._records if r.outcome == InstallationOutcome.CUSTOMER_REFUSED]

    def pending_appointments(self, as_of: dt.date) -> List[InstallationAppointmentRecord]:
        return [r for r in self._records
                if not r.is_terminal and r.appointment_date >= as_of]

    def completion_rate_pct(self) -> Optional[float]:
        terminal = [r for r in self._records if r.is_terminal]
        if not terminal:
            return None
        return round(sum(1 for r in terminal if r.is_complete) / len(terminal) * 100, 1)

    def access_failure_rate_pct(self) -> Optional[float]:
        terminal = [r for r in self._records if r.is_terminal]
        if not terminal:
            return None
        return round(sum(1 for r in terminal if r.is_access_issue) / len(terminal) * 100, 1)

    def monthly_completions(self, year: int, month: int) -> int:
        return sum(1 for r in self._records
                   if r.is_complete and r.outcome_date is not None
                   and r.outcome_date.year == year and r.outcome_date.month == month)

    def by_fuel(self, fuel: str) -> List[InstallationAppointmentRecord]:
        return [r for r in self._records if r.fuel == fuel]

    def programme_summary(self, as_of: dt.date) -> str:
        n = len(self._records)
        n_done = len(self.completions())
        cr = self.completion_rate_pct()
        cr_str = f"{cr:.1f}%" if cr is not None else "n/a"
        n_pending = len(self.pending_appointments(as_of))
        return (
            f"Smart Meter Programme ({as_of}): {n} appointments "
            f"({n_done} completed, {n_pending} pending). "
            f"Completion rate: {cr_str}."
        )
