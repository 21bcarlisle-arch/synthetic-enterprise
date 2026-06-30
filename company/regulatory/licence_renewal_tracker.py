"""Supplier Licence Renewal Tracker (Phase EP).

Gas and electricity suppliers in GB must hold licences issued by Ofgem under:
- Electricity Act 1989 s.6 (electricity supply licence)
- Gas Act 1986 s.7A (gas supply licence)

Licence conditions include:
- Standard Licence Conditions (SLCs): mandatory obligations
- Special Conditions: supplier-specific commitments made at application
- Financial Resilience Assessment (FRA): Ofgem reviews annually post-2022 crisis

Key compliance milestones:
- Annual FRA submission (September annually)
- SLC compliance self-report (quarterly)
- Material change notification (within 10 working days)
- Customer Transfer Process compliance (monthly)

The licence is not 'renewed' annually in the traditional sense — it is revoked
if conditions are breached. This tracker models the ongoing compliance posture
that keeps the licence active, not a periodic renewal event.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class LicenceType(str, Enum):
    ELECTRICITY_SUPPLY = "electricity_supply"
    GAS_SUPPLY = "gas_supply"
    ELECTRICITY_DISTRIBUTION = "electricity_distribution"  # not held by pure suppliers


class ComplianceMilestoneType(str, Enum):
    ANNUAL_FRA_SUBMISSION = "annual_fra_submission"
    SLC_SELF_REPORT = "slc_self_report"
    MATERIAL_CHANGE_NOTIFICATION = "material_change_notification"
    CUSTOMER_TRANSFER_REPORT = "customer_transfer_report"
    SMART_METER_REPORT = "smart_meter_report"
    ODGEN_COMPLIANCE_RETURN = "ofgem_compliance_return"  # Ofgem compliance monitoring


_MILESTONE_WINDOW_DAYS = {
    ComplianceMilestoneType.ANNUAL_FRA_SUBMISSION: 14,          # 14 days grace
    ComplianceMilestoneType.SLC_SELF_REPORT: 10,
    ComplianceMilestoneType.MATERIAL_CHANGE_NOTIFICATION: 10,   # SLC 10-WD rule
    ComplianceMilestoneType.CUSTOMER_TRANSFER_REPORT: 5,
    ComplianceMilestoneType.SMART_METER_REPORT: 20,
    ComplianceMilestoneType.ODGEN_COMPLIANCE_RETURN: 14,
}


@dataclass(frozen=True)
class ComplianceMilestone:
    milestone_type: ComplianceMilestoneType
    due_date: dt.date
    submitted_date: Optional[dt.date] = None
    notes: str = ""

    @property
    def is_submitted(self) -> bool:
        return self.submitted_date is not None

    def is_overdue(self, as_of: dt.date) -> bool:
        if self.is_submitted:
            return False
        return as_of > self.due_date

    def days_overdue(self, as_of: dt.date) -> int:
        if not self.is_overdue(as_of):
            return 0
        return (as_of - self.due_date).days

    def is_late_submission(self) -> bool:
        if not self.is_submitted or self.submitted_date is None:
            return False
        return self.submitted_date > self.due_date


@dataclass(frozen=True)
class LicenceRecord:
    licence_type: LicenceType
    licence_number: str
    granted_date: dt.date
    fra_due_month: int = 9   # September default


class SupplierLicenceRenewalTracker:

    def __init__(self) -> None:
        self._licences: List[LicenceRecord] = []
        self._milestones: List[ComplianceMilestone] = []

    def register_licence(self, licence: LicenceRecord) -> LicenceRecord:
        self._licences.append(licence)
        return licence

    def add_milestone(self, milestone: ComplianceMilestone) -> ComplianceMilestone:
        self._milestones.append(milestone)
        return milestone

    def submit_milestone(
        self, milestone_type: ComplianceMilestoneType,
        due_date: dt.date, submitted_date: dt.date
    ) -> Optional[ComplianceMilestone]:
        for i, m in enumerate(self._milestones):
            if m.milestone_type == milestone_type and m.due_date == due_date:
                updated = ComplianceMilestone(
                    milestone_type=m.milestone_type,
                    due_date=m.due_date,
                    submitted_date=submitted_date,
                    notes=m.notes,
                )
                self._milestones[i] = updated
                return updated
        return None

    def overdue_milestones(self, as_of: dt.date) -> List[ComplianceMilestone]:
        return [m for m in self._milestones if m.is_overdue(as_of)]

    def upcoming_milestones(self, as_of: dt.date, within_days: int = 30) -> List[ComplianceMilestone]:
        window = as_of + dt.timedelta(days=within_days)
        return [m for m in self._milestones
                if not m.is_submitted and as_of <= m.due_date <= window]

    def late_submissions(self) -> List[ComplianceMilestone]:
        return [m for m in self._milestones if m.is_late_submission()]

    def total_licences(self) -> int:
        return len(self._licences)

    def licence_compliance_summary(self, as_of: dt.date) -> str:
        n_overdue = len(self.overdue_milestones(as_of))
        n_upcoming = len(self.upcoming_milestones(as_of))
        n_late = len(self.late_submissions())
        return (
            "Licence Compliance (" + str(as_of) + "): "
            + str(self.total_licences()) + " licences. "
            "Overdue: " + str(n_overdue) + ". "
            "Upcoming (30d): " + str(n_upcoming) + ". "
            "Late submissions: " + str(n_late) + "."
        )
