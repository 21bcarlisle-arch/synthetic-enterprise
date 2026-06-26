"""GDPR data privacy consent register and data subject request tracker."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class ConsentPurpose(str, Enum):
    BILLING = 'billing'
    MARKETING_EMAIL = 'marketing_email'
    MARKETING_SMS = 'marketing_sms'
    THIRD_PARTY_SHARING = 'third_party_sharing'
    ANALYTICS = 'analytics'
    SMART_METER_DATA = 'smart_meter_data'


class DSRType(str, Enum):  # Data Subject Request
    ACCESS = 'access'           # DSAR — subject access request
    ERASURE = 'erasure'         # right to be forgotten
    PORTABILITY = 'portability' # data export
    RECTIFICATION = 'rectification'
    RESTRICTION = 'restriction'


class DSRStatus(str, Enum):
    RECEIVED = 'received'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    EXTENDED = 'extended'
    REFUSED = 'refused'


_DSR_DEADLINE_DAYS = 30
_DSR_EXTENSION_DAYS = 60  # up to 3 months total for complex requests


@dataclass(frozen=True)
class ConsentRecord:
    customer_id: str
    purpose: ConsentPurpose
    granted: bool
    consent_date: dt.date
    withdrawal_date: Optional[dt.date] = None

    @property
    def is_active(self) -> bool:
        return self.granted and self.withdrawal_date is None


@dataclass
class DataSubjectRequest:
    request_id: str
    customer_id: str
    dsr_type: DSRType
    received_date: dt.date
    status: DSRStatus = DSRStatus.RECEIVED
    completed_date: Optional[dt.date] = None
    is_extended: bool = False

    def deadline(self) -> dt.date:
        extra = _DSR_EXTENSION_DAYS if self.is_extended else _DSR_DEADLINE_DAYS
        return self.received_date + dt.timedelta(days=extra)

    def is_overdue(self, as_of: dt.date) -> bool:
        if self.status in (DSRStatus.COMPLETED, DSRStatus.REFUSED):
            return False
        return as_of > self.deadline()

    def complete(self, completion_date: dt.date) -> None:
        self.completed_date = completion_date
        self.status = DSRStatus.COMPLETED

    def extend(self) -> None:
        self.is_extended = True
        self.status = DSRStatus.EXTENDED


class PrivacyConsentRegister:
    def __init__(self) -> None:
        self._consents: List[ConsentRecord] = []
        self._requests: List[DataSubjectRequest] = []
        self._request_counter = 0

    def record_consent(self, customer_id: str, purpose: ConsentPurpose,
                         granted: bool, consent_date: dt.date,
                         withdrawal_date: Optional[dt.date] = None) -> ConsentRecord:
        r = ConsentRecord(
            customer_id=customer_id, purpose=purpose, granted=granted,
            consent_date=consent_date, withdrawal_date=withdrawal_date,
        )
        self._consents.append(r)
        return r

    def has_active_consent(self, customer_id: str,
                             purpose: ConsentPurpose) -> bool:
        latest = None
        for c in self._consents:
            if c.customer_id == customer_id and c.purpose == purpose:
                if latest is None or c.consent_date > latest.consent_date:
                    latest = c
        return latest is not None and latest.is_active

    def raise_dsr(self, customer_id: str, dsr_type: DSRType,
                    received_date: dt.date) -> DataSubjectRequest:
        self._request_counter += 1
        dsr = DataSubjectRequest(
            request_id=f'DSR-{self._request_counter:04d}',
            customer_id=customer_id, dsr_type=dsr_type,
            received_date=received_date,
        )
        self._requests.append(dsr)
        return dsr

    def get_dsr(self, request_id: str) -> Optional[DataSubjectRequest]:
        return next((r for r in self._requests if r.request_id == request_id), None)

    def overdue_requests(self, as_of: dt.date) -> List[DataSubjectRequest]:
        return [r for r in self._requests if r.is_overdue(as_of)]

    def customers_without_consent(self, purpose: ConsentPurpose,
                                     customer_ids: List[str]) -> List[str]:
        return [cid for cid in customer_ids
                 if not self.has_active_consent(cid, purpose)]

    def privacy_summary(self, as_of: dt.date) -> dict:
        marketing_opt_in = sum(
            1 for c in self._consents
            if c.purpose == ConsentPurpose.MARKETING_EMAIL and c.is_active
        )
        return {
            'total_consent_records': len(self._consents),
            'total_dsr': len(self._requests),
            'overdue_dsr': len(self.overdue_requests(as_of)),
            'marketing_email_opt_ins': marketing_opt_in,
        }
