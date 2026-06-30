"""ICO Data Breach Notification Register.

UK GDPR / Data Protection Act 2018 requirements for energy suppliers:
- Personal data breaches likely to harm rights/freedoms must be notified to ICO within 72 hours
- High-risk breaches must also be notified directly to affected individuals without undue delay
- Smart meter data is sensitive personal data (consumption patterns = behavioural fingerprint)
- Energy suppliers hold: billing data, bank details, usage history, vulnerability flags, property info
- Maximum fine: £17.5M or 4% of global turnover (UK GDPR Art.83(5)); lesser breaches £8.75M / 2%
- ICO breach ID format: ref DP-[year]-[seq]

Epistemic: company knows its own data systems and what breaches occur.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class BreachType(str, Enum):
    CONFIDENTIALITY = "confidentiality"
    INTEGRITY = "integrity"
    AVAILABILITY = "availability"


class DataCategory(str, Enum):
    BILLING = "billing"
    BANK_DETAILS = "bank_details"
    SMART_METER = "smart_meter"
    VULNERABILITY_FLAGS = "vulnerability_flags"
    CONTACT_DETAILS = "contact_details"
    USAGE_HISTORY = "usage_history"
    CREDIT_SCORES = "credit_scores"


class BreachSeverity(str, Enum):
    MINOR = "minor"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class ICONotificationStatus(str, Enum):
    NONE_REQUIRED = "none_required"
    PENDING = "pending"
    NOTIFIED = "notified"
    LATE_NOTIFICATION = "late_notification"
    INVESTIGATION_OPEN = "investigation_open"
    CLOSED = "closed"


class IndividualNotificationStatus(str, Enum):
    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    COMPLETED = "completed"
    DELAYED = "delayed"


_ICO_NOTIFICATION_HOURS = 72
_MAX_FINE_ARTICLE_83_5 = 17_500_000.0
_MAX_FINE_ARTICLE_83_4 = 8_750_000.0


@dataclass(frozen=True)
class DataBreachRecord:
    breach_id: str
    breach_type: BreachType
    data_categories: tuple
    detected_at: dt.datetime
    occurred_at: dt.datetime
    accounts_affected: int
    description: str
    severity: BreachSeverity
    ico_status: ICONotificationStatus
    individual_status: IndividualNotificationStatus
    ico_reference: Optional[str] = None
    ico_notified_at: Optional[dt.datetime] = None
    closed_at: Optional[dt.datetime] = None
    estimated_fine_gbp: float = 0.0

    @property
    def hours_to_ico_notification(self) -> Optional[float]:
        if self.ico_notified_at is None:
            return None
        return (self.ico_notified_at - self.detected_at).total_seconds() / 3600

    @property
    def is_within_72h(self) -> bool:
        h = self.hours_to_ico_notification
        return h is not None and h <= _ICO_NOTIFICATION_HOURS

    @property
    def notification_overdue(self) -> bool:
        if self.severity == BreachSeverity.MINOR:
            return False
        if self.ico_status in (ICONotificationStatus.NOTIFIED, ICONotificationStatus.NONE_REQUIRED,
                                ICONotificationStatus.CLOSED):
            return False
        elapsed = (dt.datetime.now(dt.timezone.utc) - self.detected_at).total_seconds() / 3600
        return elapsed > _ICO_NOTIFICATION_HOURS

    @property
    def contains_sensitive_data(self) -> bool:
        sensitive = {DataCategory.BANK_DETAILS, DataCategory.VULNERABILITY_FLAGS,
                     DataCategory.SMART_METER}
        return bool(sensitive & set(self.data_categories))

    @property
    def maximum_fine_exposure_gbp(self) -> float:
        if self.severity in (BreachSeverity.HIGH, BreachSeverity.CRITICAL):
            return _MAX_FINE_ARTICLE_83_5
        return _MAX_FINE_ARTICLE_83_4

    @property
    def is_active(self) -> bool:
        return self.ico_status not in (ICONotificationStatus.CLOSED, ICONotificationStatus.NONE_REQUIRED)

def _assess_severity(data_categories: tuple, accounts_affected: int) -> BreachSeverity:
    sensitive = {DataCategory.BANK_DETAILS, DataCategory.VULNERABILITY_FLAGS,
                 DataCategory.SMART_METER}
    has_sensitive = bool(sensitive & set(data_categories))
    if accounts_affected == 0:
        return BreachSeverity.MINOR
    if has_sensitive and accounts_affected >= 100:
        return BreachSeverity.CRITICAL
    if has_sensitive or accounts_affected >= 1000:
        return BreachSeverity.HIGH
    if accounts_affected >= 10:
        return BreachSeverity.MODERATE
    return BreachSeverity.MINOR


class ICOBreachRegister:
    """Central register for personal data breach tracking (UK GDPR / DPA 2018)."""

    def __init__(self) -> None:
        self._breaches: Dict[str, DataBreachRecord] = {}
        self._seq = 0

    def _next_id(self) -> str:
        self._seq += 1
        return f"IDB-{self._seq:04d}"

    def record_breach(
        self,
        breach_type: BreachType,
        data_categories: tuple,
        detected_at: dt.datetime,
        occurred_at: dt.datetime,
        accounts_affected: int,
        description: str,
        severity: Optional[BreachSeverity] = None,
    ) -> DataBreachRecord:
        bid = self._next_id()
        if severity is None:
            severity = _assess_severity(data_categories, accounts_affected)
        ico_status = (ICONotificationStatus.NONE_REQUIRED
                      if severity == BreachSeverity.MINOR
                      else ICONotificationStatus.PENDING)
        ind_status = (IndividualNotificationStatus.NOT_REQUIRED
                      if severity in (BreachSeverity.MINOR, BreachSeverity.MODERATE)
                      else IndividualNotificationStatus.PENDING)
        rec = DataBreachRecord(
            breach_id=bid, breach_type=breach_type,
            data_categories=data_categories, detected_at=detected_at,
            occurred_at=occurred_at, accounts_affected=accounts_affected,
            description=description, severity=severity,
            ico_status=ico_status, individual_status=ind_status,
        )
        self._breaches[bid] = rec
        return rec

    def _replace(self, rec: DataBreachRecord, **kwargs) -> DataBreachRecord:
        fields = {
            "breach_id": rec.breach_id, "breach_type": rec.breach_type,
            "data_categories": rec.data_categories, "detected_at": rec.detected_at,
            "occurred_at": rec.occurred_at, "accounts_affected": rec.accounts_affected,
            "description": rec.description, "severity": rec.severity,
            "ico_status": rec.ico_status, "individual_status": rec.individual_status,
            "ico_reference": rec.ico_reference, "ico_notified_at": rec.ico_notified_at,
            "closed_at": rec.closed_at, "estimated_fine_gbp": rec.estimated_fine_gbp,
        }
        fields.update(kwargs)
        return DataBreachRecord(**fields)

    def notify_ico(
        self, breach_id: str, notified_at: dt.datetime,
        ico_reference: Optional[str] = None,
    ) -> DataBreachRecord:
        rec = self._breaches[breach_id]
        hours = (notified_at - rec.detected_at).total_seconds() / 3600
        status = (ICONotificationStatus.NOTIFIED
                  if hours <= _ICO_NOTIFICATION_HOURS
                  else ICONotificationStatus.LATE_NOTIFICATION)
        updated = self._replace(rec, ico_status=status, ico_notified_at=notified_at,
                                 ico_reference=ico_reference)
        self._breaches[breach_id] = updated
        return updated

    def complete_individual_notification(self, breach_id: str) -> DataBreachRecord:
        rec = self._breaches[breach_id]
        updated = self._replace(rec, individual_status=IndividualNotificationStatus.COMPLETED)
        self._breaches[breach_id] = updated
        return updated

    def open_investigation(self, breach_id: str) -> DataBreachRecord:
        rec = self._breaches[breach_id]
        updated = self._replace(rec, ico_status=ICONotificationStatus.INVESTIGATION_OPEN)
        self._breaches[breach_id] = updated
        return updated

    def close(self, breach_id: str, closed_at: dt.datetime,
              estimated_fine_gbp: float = 0.0) -> DataBreachRecord:
        rec = self._breaches[breach_id]
        updated = self._replace(rec, ico_status=ICONotificationStatus.CLOSED,
                                 closed_at=closed_at, estimated_fine_gbp=estimated_fine_gbp)
        self._breaches[breach_id] = updated
        return updated

    @property
    def all_breaches(self) -> List[DataBreachRecord]:
        return list(self._breaches.values())

    @property
    def active_breaches(self) -> List[DataBreachRecord]:
        return [b for b in self._breaches.values() if b.is_active]

    @property
    def overdue_ico_notifications(self) -> List[DataBreachRecord]:
        return [b for b in self._breaches.values() if b.notification_overdue]

    @property
    def late_notifications(self) -> List[DataBreachRecord]:
        return [b for b in self._breaches.values()
                if b.ico_status == ICONotificationStatus.LATE_NOTIFICATION]

    @property
    def pending_individual_notifications(self) -> List[DataBreachRecord]:
        return [b for b in self._breaches.values()
                if b.individual_status == IndividualNotificationStatus.PENDING]

    @property
    def sensitive_data_breaches(self) -> List[DataBreachRecord]:
        return [b for b in self._breaches.values() if b.contains_sensitive_data]

    @property
    def total_fine_exposure_gbp(self) -> float:
        return sum(b.maximum_fine_exposure_gbp for b in self.active_breaches)

    @property
    def total_accounts_affected(self) -> int:
        return sum(b.accounts_affected for b in self._breaches.values())

    def breaches_by_severity(self) -> Dict[str, int]:
        out: Dict[str, int] = {}
        for b in self._breaches.values():
            out[b.severity.value] = out.get(b.severity.value, 0) + 1
        return out

    def ico_breach_summary(self) -> str:
        total = len(self._breaches)
        active = len(self.active_breaches)
        overdue = len(self.overdue_ico_notifications)
        late = len(self.late_notifications)
        sensitive = len(self.sensitive_data_breaches)
        pending_ind = len(self.pending_individual_notifications)
        accts = self.total_accounts_affected
        fine_exposure = self.total_fine_exposure_gbp
        by_sev = self.breaches_by_severity()
        return (
            f"ICO Breach Register: {total} breaches recorded, {active} active, "
            f"{overdue} overdue ICO notification. "
            f"Severity: {by_sev}. "
            f"Late notifications: {late}. Sensitive data breaches: {sensitive}. "
            f"Pending individual notifications: {pending_ind}. "
            f"Total accounts affected: {accts:,}. "
            f"Max fine exposure: £{fine_exposure:,.0f} (UK GDPR Art.83)."
        )
