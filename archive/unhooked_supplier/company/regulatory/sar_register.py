"""Data Subject Access Request (SAR) Register.

UK GDPR Article 15 / DPA 2018: individuals can request a copy of all personal
data held about them. Energy suppliers hold: billing records, meter reads
(including HH smart meter consumption), vulnerability flags, payment history,
call recordings, communications, credit assessments, and debt history.

Key rules:
- Response deadline: 1 calendar month from receipt (extendable to 3 months for complex)
- No fee unless request is manifestly unfounded or excessive
- Must provide: data held, purpose, recipients, retention period, source
- SAR cannot be refused simply because the requester is disputing a debt
- If denied: must provide reasons and right to complain to ICO
- ICO enforcement: commissioner investigation, enforcement notice, fine up to GBP 17.5M

Common triggers in energy supply:
- Customer disputing a bill (wants to see meter reads and billing calculations)
- Debt dispute (wants to see all communications and payment records)
- Complaint about vulnerability handling
- Litigation preparation (subject access as pre-action disclosure)

Epistemic: company knows what personal data it holds and how it processes SARs.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class SARStatus(str, Enum):
    RECEIVED = "received"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    RESPONDED = "responded"
    EXTENDED = "extended"       # 1-month extension invoked
    REFUSED = "refused"         # manifestly unfounded / excessive
    COMPLAINT_RAISED = "complaint_raised"  # customer escalated to ICO


class SARTrigger(str, Enum):
    BILLING_DISPUTE = "billing_dispute"
    DEBT_DISPUTE = "debt_dispute"
    VULNERABILITY_CONCERN = "vulnerability_concern"
    GENERAL_ENQUIRY = "general_enquiry"
    PRE_LITIGATION = "pre_litigation"
    OMBUDSMAN_REFERRAL = "ombudsman_referral"
    UNKNOWN = "unknown"


class SARRefusalReason(str, Enum):
    MANIFESTLY_UNFOUNDED = "manifestly_unfounded"
    MANIFESTLY_EXCESSIVE = "manifestly_excessive"    # repeat requests
    THIRD_PARTY_RIGHTS = "third_party_rights"        # would expose another person
    LEGAL_EXEMPTION = "legal_exemption"              # crime prevention etc.


_STANDARD_DEADLINE_DAYS = 30    # 1 calendar month (GDPR Art.12(3))
_EXTENDED_DEADLINE_DAYS = 90    # 3 calendar months for complex
_MAX_FINE_GBP = 17_500_000.0


@dataclass(frozen=True)
class SARRecord:
    sar_id: str
    customer_id: str
    received_at: dt.date
    trigger: SARTrigger
    status: SARStatus
    is_extended: bool
    responded_at: Optional[dt.date] = None
    refused_reason: Optional[SARRefusalReason] = None
    ico_complaint_ref: Optional[str] = None
    fee_charged_gbp: float = 0.0

    @property
    def deadline(self) -> dt.date:
        days = _EXTENDED_DEADLINE_DAYS if self.is_extended else _STANDARD_DEADLINE_DAYS
        return self.received_at + dt.timedelta(days=days)

    def is_overdue(self, as_of: dt.date) -> bool:
        if self.status in (SARStatus.RESPONDED, SARStatus.REFUSED):
            return False
        return as_of > self.deadline

    def days_to_deadline(self, as_of: dt.date) -> int:
        return (self.deadline - as_of).days

    @property
    def days_to_respond(self) -> Optional[int]:
        if self.responded_at is None:
            return None
        return (self.responded_at - self.received_at).days

    @property
    def responded_within_deadline(self) -> Optional[bool]:
        if self.responded_at is None:
            return None
        return self.responded_at <= self.deadline

    @property
    def is_active(self) -> bool:
        return self.status not in (SARStatus.RESPONDED, SARStatus.REFUSED)


class SARRegister:
    """Tracks Data Subject Access Requests under UK GDPR Art.15."""

    def __init__(self) -> None:
        self._requests: Dict[str, SARRecord] = {}
        self._seq = 0

    def _next_id(self) -> str:
        self._seq += 1
        return f"SAR-{self._seq:04d}"

    def receive(
        self,
        customer_id: str,
        received_at: dt.date,
        trigger: SARTrigger = SARTrigger.UNKNOWN,
    ) -> SARRecord:
        sid = self._next_id()
        rec = SARRecord(
            sar_id=sid, customer_id=customer_id, received_at=received_at,
            trigger=trigger, status=SARStatus.RECEIVED, is_extended=False,
        )
        self._requests[sid] = rec
        return rec

    def _replace(self, rec: SARRecord, **kwargs) -> SARRecord:
        fields = {
            "sar_id": rec.sar_id, "customer_id": rec.customer_id,
            "received_at": rec.received_at, "trigger": rec.trigger,
            "status": rec.status, "is_extended": rec.is_extended,
            "responded_at": rec.responded_at, "refused_reason": rec.refused_reason,
            "ico_complaint_ref": rec.ico_complaint_ref, "fee_charged_gbp": rec.fee_charged_gbp,
        }
        fields.update(kwargs)
        return SARRecord(**fields)

    def acknowledge(self, sar_id: str) -> SARRecord:
        rec = self._requests[sar_id]
        updated = self._replace(rec, status=SARStatus.ACKNOWLEDGED)
        self._requests[sar_id] = updated
        return updated

    def extend(self, sar_id: str) -> SARRecord:
        """Invoke 3-month extension for complex/multiple requests."""
        rec = self._requests[sar_id]
        updated = self._replace(rec, status=SARStatus.EXTENDED, is_extended=True)
        self._requests[sar_id] = updated
        return updated

    def respond(self, sar_id: str, responded_at: dt.date) -> SARRecord:
        rec = self._requests[sar_id]
        updated = self._replace(rec, status=SARStatus.RESPONDED, responded_at=responded_at)
        self._requests[sar_id] = updated
        return updated

    def refuse(self, sar_id: str, reason: SARRefusalReason,
               fee_charged_gbp: float = 0.0) -> SARRecord:
        rec = self._requests[sar_id]
        updated = self._replace(rec, status=SARStatus.REFUSED,
                                 refused_reason=reason, fee_charged_gbp=fee_charged_gbp)
        self._requests[sar_id] = updated
        return updated

    def mark_ico_complaint(self, sar_id: str, ico_ref: str) -> SARRecord:
        rec = self._requests[sar_id]
        updated = self._replace(rec, status=SARStatus.COMPLAINT_RAISED,
                                 ico_complaint_ref=ico_ref)
        self._requests[sar_id] = updated
        return updated

    def overdue(self, as_of: dt.date) -> List[SARRecord]:
        return [r for r in self._requests.values() if r.is_overdue(as_of)]

    def active(self) -> List[SARRecord]:
        return [r for r in self._requests.values() if r.is_active]

    def late_responses(self) -> List[SARRecord]:
        return [r for r in self._requests.values()
                if r.responded_within_deadline is False]

    def by_trigger(self) -> Dict[str, int]:
        out: Dict[str, int] = {}
        for r in self._requests.values():
            out[r.trigger.value] = out.get(r.trigger.value, 0) + 1
        return out

    def compliance_rate(self) -> float:
        completed = [r for r in self._requests.values()
                     if r.responded_within_deadline is not None]
        if not completed:
            return 1.0
        on_time = [r for r in completed if r.responded_within_deadline]
        return len(on_time) / len(completed)

    def sar_summary(self) -> str:
        total = len(self._requests)
        active = len(self.active())
        late = len(self.late_responses())
        by_trig = self.by_trigger()
        rate = self.compliance_rate()
        return (
            f"SAR Register (UK GDPR Art.15): {total} requests, {active} active, {late} late. "
            f"Compliance rate: {rate:.1%}. Triggers: {by_trig}. "
            f"Deadline: 30 days standard, 90 days extended. Max fine: GBP{_MAX_FINE_GBP:,.0f}."
        )
