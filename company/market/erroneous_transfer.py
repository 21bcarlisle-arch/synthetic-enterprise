from __future__ import annotations

import dataclasses
import datetime
from enum import Enum
from typing import Dict, List, Optional


class ETStatus(str, Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED_CORRECTED = "resolved_corrected"
    RESOLVED_ACCEPTED = "resolved_accepted"
    COMPENSATION_DUE = "compensation_due"
    CLOSED = "closed"


class ETResolutionType(str, Enum):
    RETURNED_TO_ORIGINAL = "returned_to_original"
    CUSTOMER_ACCEPTED_GAIN = "customer_accepted_gain"
    WITHDRAWN = "withdrawn"


_OPEN_STATUSES = {ETStatus.OPEN, ETStatus.INVESTIGATING, ETStatus.COMPENSATION_DUE}
_RESOLVED_STATUSES = {ETStatus.RESOLVED_CORRECTED, ETStatus.RESOLVED_ACCEPTED, ETStatus.CLOSED}


@dataclasses.dataclass(frozen=True)
class ETClaim:
    claim_id: str
    mpan: str
    affected_account_id: str
    claim_date: datetime.date
    original_supplier: str
    gaining_supplier: str
    status: ETStatus
    resolution_date: Optional[datetime.date] = None
    resolution_type: Optional[ETResolutionType] = None

    def working_days_open(self, as_of: datetime.date) -> int:
        current = self.claim_date
        count = 0
        while current < as_of:
            if current.weekday() < 5:
                count += 1
            current += datetime.timedelta(days=1)
        return count

    def is_overdue(self, as_of: datetime.date) -> bool:
        return self.working_days_open(as_of) > 20

    def compensation_gbp(self, as_of: datetime.date) -> float:
        if self.is_overdue(as_of) and self.status not in _RESOLVED_STATUSES:
            return 30.0
        return 0.0


class ErroneousTransferRegister:
    def __init__(self) -> None:
        self._claims: List[ETClaim] = []

    def raise_claim(self, claim: ETClaim) -> None:
        self._claims.append(claim)

    def update_status(self, claim_id: str, new_status: ETStatus) -> None:
        for i, c in enumerate(self._claims):
            if c.claim_id == claim_id:
                self._claims[i] = dataclasses.replace(c, status=new_status)
                return

    def resolve_claim(
        self,
        claim_id: str,
        resolution_date: datetime.date,
        resolution_type: ETResolutionType,
    ) -> None:
        for i, c in enumerate(self._claims):
            if c.claim_id == claim_id:
                new_status = (
                    ETStatus.RESOLVED_CORRECTED
                    if resolution_type == ETResolutionType.RETURNED_TO_ORIGINAL
                    else ETStatus.RESOLVED_ACCEPTED
                )
                self._claims[i] = dataclasses.replace(
                    c,
                    status=new_status,
                    resolution_date=resolution_date,
                    resolution_type=resolution_type,
                )
                return

    def open_claims(self) -> List[ETClaim]:
        return [c for c in self._claims if c.status in _OPEN_STATUSES]

    def overdue_claims(self, as_of: datetime.date) -> List[ETClaim]:
        return [c for c in self.open_claims() if c.is_overdue(as_of)]

    def et_rate_pct(self, total_switches: int) -> float:
        if total_switches <= 0:
            return 0.0
        return round(len(self._claims) / total_switches * 100, 4)

    def compensation_outstanding_gbp(self, as_of: datetime.date) -> float:
        return round(sum(c.compensation_gbp(as_of) for c in self._claims), 2)

    def claims_by_status(self) -> Dict[str, int]:
        counts: Dict[str, int] = {s.value: 0 for s in ETStatus}
        for c in self._claims:
            counts[c.status.value] += 1
        return counts

    def et_summary(self, as_of: datetime.date, total_switches: int) -> dict:
        rate = self.et_rate_pct(total_switches)
        return {
            "total_claims": len(self._claims),
            "open_claims": len(self.open_claims()),
            "overdue_claims": len(self.overdue_claims(as_of)),
            "resolved_corrected": sum(1 for c in self._claims if c.status == ETStatus.RESOLVED_CORRECTED),
            "resolved_accepted": sum(1 for c in self._claims if c.status == ETStatus.RESOLVED_ACCEPTED),
            "et_rate_pct": rate,
            "compensation_outstanding_gbp": self.compensation_outstanding_gbp(as_of),
            "above_threshold": rate > 0.1,
        }
