"""DD Indemnity Claim Register: BACS Direct Debit Guarantee claim management."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class DDIndemnityStatus(str, Enum):
    RECEIVED = "received"           # bank has recalled funds
    INVESTIGATING = "investigating"
    UPHELD = "upheld"               # customer keeps refund; debt on account
    REJECTED = "rejected"           # supplier contested; bank returned funds
    WRITTEN_OFF = "written_off"     # accepted as irrecoverable


class DDIndemnityReason(str, Enum):
    NOT_AUTHORISED = "not_authorised"
    AMOUNT_INCORRECT = "amount_incorrect"
    TIMING_INCORRECT = "timing_incorrect"
    DUPLICATE_PAYMENT = "duplicate_payment"
    FRAUDULENT = "fraudulent"


_INVESTIGATION_DEADLINE_WORKING_DAYS = 10


def _working_days_between(start: dt.date, end: dt.date) -> int:
    days = 0
    current = start
    while current < end:
        current += dt.timedelta(days=1)
        if current.weekday() < 5:
            days += 1
    return days


@dataclass(frozen=True)
class DDIndemnityClaim:
    claim_id: str
    account_id: str
    receipt_date: dt.date
    payment_date: dt.date             # original DD payment date
    claimed_amount_gbp: float
    reason: DDIndemnityReason
    status: DDIndemnityStatus = DDIndemnityStatus.RECEIVED
    resolution_date: Optional[dt.date] = None
    resolution_notes: str = ""

    def is_investigation_overdue(self, as_of: dt.date) -> bool:
        if self.status in (DDIndemnityStatus.UPHELD, DDIndemnityStatus.REJECTED,
                           DDIndemnityStatus.WRITTEN_OFF):
            return False
        return _working_days_between(self.receipt_date, as_of) > _INVESTIGATION_DEADLINE_WORKING_DAYS

    def is_active(self) -> bool:
        return self.status in (
            DDIndemnityStatus.RECEIVED, DDIndemnityStatus.INVESTIGATING
        )

    def creates_debt(self) -> bool:
        return self.status == DDIndemnityStatus.UPHELD


class DDIndemnityRegister:
    """Tracks BACS Direct Debit Guarantee indemnity claims.

    Real calibration:
    - BACS DD Guarantee (UK): customer may request refund from their bank at any time
      for a DD payment made in error; bank refunds immediately (no questions asked).
      Supplier has right to contest via BACS Indemnity process.
    - When upheld: the claimed amount becomes a debt on the customer account.
    - When rejected: BACS returns funds to supplier; DD must be re-instructed.
    - Energy sector: ~2-3% of all DD customers raise an indemnity each year.
    - Risk: large coordinated indemnity campaigns (e.g. against price rises) can
      create significant short-term cash flow risk for suppliers.
    """

    def __init__(self) -> None:
        self._claims: List[DDIndemnityClaim] = []

    def receive_claim(self, claim: DDIndemnityClaim) -> DDIndemnityClaim:
        self._claims.append(claim)
        return claim

    def _update(self, claim_id: str, **kwargs) -> DDIndemnityClaim:
        import dataclasses
        for i, c in enumerate(self._claims):
            if c.claim_id == claim_id:
                updated = dataclasses.replace(c, **kwargs)
                self._claims[i] = updated
                return updated
        raise ValueError(f"Claim not found: {claim_id}")

    def start_investigation(self, claim_id: str) -> DDIndemnityClaim:
        return self._update(claim_id, status=DDIndemnityStatus.INVESTIGATING)

    def uphold(self, claim_id: str, resolution_date: dt.date,
              notes: str = "") -> DDIndemnityClaim:
        return self._update(claim_id, status=DDIndemnityStatus.UPHELD,
                            resolution_date=resolution_date, resolution_notes=notes)

    def reject(self, claim_id: str, resolution_date: dt.date,
              notes: str = "") -> DDIndemnityClaim:
        return self._update(claim_id, status=DDIndemnityStatus.REJECTED,
                            resolution_date=resolution_date, resolution_notes=notes)

    def write_off(self, claim_id: str, resolution_date: dt.date) -> DDIndemnityClaim:
        return self._update(claim_id, status=DDIndemnityStatus.WRITTEN_OFF,
                            resolution_date=resolution_date)

    def active_claims(self) -> List[DDIndemnityClaim]:
        return [c for c in self._claims if c.is_active()]

    def overdue_investigations(self, as_of: dt.date) -> List[DDIndemnityClaim]:
        return [c for c in self._claims if c.is_investigation_overdue(as_of)]

    def total_exposure_gbp(self) -> float:
        return round(sum(c.claimed_amount_gbp for c in self.active_claims()), 2)

    def total_upheld_gbp(self) -> float:
        return round(sum(c.claimed_amount_gbp for c in self._claims
                         if c.status == DDIndemnityStatus.UPHELD), 2)

    def claims_by_reason(self, reason: DDIndemnityReason) -> List[DDIndemnityClaim]:
        return [c for c in self._claims if c.reason == reason]

    def dd_indemnity_summary(self) -> dict:
        return {
            "total_claims": len(self._claims),
            "active": len(self.active_claims()),
            "upheld": sum(1 for c in self._claims if c.status == DDIndemnityStatus.UPHELD),
            "rejected": sum(1 for c in self._claims if c.status == DDIndemnityStatus.REJECTED),
            "total_exposure_gbp": self.total_exposure_gbp(),
            "total_upheld_gbp": self.total_upheld_gbp(),
        }
