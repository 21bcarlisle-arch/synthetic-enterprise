"""Customer Credit Assessment Register (Phase DU).

When a customer applies for energy supply, the supplier conducts a credit
assessment to determine:
1. Whether to supply them (credit acceptance/decline)
2. Whether to require a deposit (security deposit for high-risk customers)
3. What payment method to mandate (direct debit, PPM)
4. What credit limit to set on the account

UK credit assessment for energy:
- Suppliers cannot use credit scores to REFUSE domestic supply (SLC 12)
- But can require a prepayment meter or security deposit
- Can limit to PPM if credit score below threshold
- I&C: no restriction — suppliers can decline on credit grounds
- Use credit reference agencies (Experian/Equifax/TransUnion)

ICO guidance: credit scoring must be fair, explained, and disputable.
GDPR: legitimate interest basis for credit search (must be proportionate).
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class CreditDecision(str, Enum):
    APPROVED = "approved"                  # supply approved, no restrictions
    APPROVED_WITH_DEPOSIT = "approved_with_deposit"
    APPROVED_PPM_ONLY = "approved_ppm_only"
    DECLINED_IC = "declined_ic"            # I&C only: can decline
    THIN_FILE = "thin_file"                # insufficient credit history


class CreditReferenceAgency(str, Enum):
    EXPERIAN = "experian"
    EQUIFAX = "equifax"
    TRANSUNION = "transunion"


class CustomerSegmentType(str, Enum):
    DOMESTIC = "domestic"
    SME = "sme"
    I_AND_C = "i_and_c"


_DEPOSIT_REFUND_DAYS = 365              # Ofgem guidance: refund deposit after 12m good payment
_CREDIT_SEARCH_VALID_DAYS = 90         # credit search result valid for 90 days
_MIN_DEPOSIT_GBP = 50.0
_MAX_DOMESTIC_DEPOSIT_GBP = 300.0      # Ofgem guidance: domestic deposit cap


@dataclass(frozen=True)
class CreditAssessmentRecord:
    assessment_id: str
    customer_id: str
    segment: CustomerSegmentType
    assessed_at: dt.date
    agency: CreditReferenceAgency
    credit_score: Optional[int]          # None if thin file
    decision: CreditDecision
    deposit_gbp: float
    deposit_paid_at: Optional[dt.date]
    deposit_refunded_at: Optional[dt.date] = None

    @property
    def requires_deposit(self) -> bool:
        return self.decision == CreditDecision.APPROVED_WITH_DEPOSIT

    @property
    def deposit_paid(self) -> bool:
        return self.deposit_paid_at is not None

    @property
    def is_ppm_required(self) -> bool:
        return self.decision == CreditDecision.APPROVED_PPM_ONLY

    @property
    def is_valid(self) -> bool:
        return True  # once on supply, assessment is historic

    def deposit_refund_eligible(self, as_of: dt.date) -> bool:
        if self.deposit_paid_at is None or self.deposit_refunded_at is not None:
            return False
        return (as_of - self.deposit_paid_at).days >= _DEPOSIT_REFUND_DAYS


class CreditAssessmentRegister:
    """Tracks customer credit assessments and deposit management."""

    def __init__(self) -> None:
        self._records: Dict[str, CreditAssessmentRecord] = {}
        self._seq = 0

    def _next_id(self) -> str:
        self._seq += 1
        return f"CA-{self._seq:04d}"

    def assess(
        self,
        customer_id: str,
        segment: CustomerSegmentType,
        assessed_at: dt.date,
        agency: CreditReferenceAgency,
        credit_score: Optional[int],
        decision: CreditDecision,
        deposit_gbp: float = 0.0,
    ) -> CreditAssessmentRecord:
        aid = self._next_id()
        rec = CreditAssessmentRecord(
            assessment_id=aid,
            customer_id=customer_id,
            segment=segment,
            assessed_at=assessed_at,
            agency=agency,
            credit_score=credit_score,
            decision=decision,
            deposit_gbp=deposit_gbp,
            deposit_paid_at=None,
        )
        self._records[customer_id] = rec
        return rec

    def record_deposit_paid(
        self, customer_id: str, paid_at: dt.date
    ) -> CreditAssessmentRecord:
        rec = self._records[customer_id]
        updated = CreditAssessmentRecord(
            assessment_id=rec.assessment_id, customer_id=rec.customer_id,
            segment=rec.segment, assessed_at=rec.assessed_at,
            agency=rec.agency, credit_score=rec.credit_score,
            decision=rec.decision, deposit_gbp=rec.deposit_gbp,
            deposit_paid_at=paid_at,
        )
        self._records[customer_id] = updated
        return updated

    def record_deposit_refunded(
        self, customer_id: str, refunded_at: dt.date
    ) -> CreditAssessmentRecord:
        rec = self._records[customer_id]
        updated = CreditAssessmentRecord(
            assessment_id=rec.assessment_id, customer_id=rec.customer_id,
            segment=rec.segment, assessed_at=rec.assessed_at,
            agency=rec.agency, credit_score=rec.credit_score,
            decision=rec.decision, deposit_gbp=rec.deposit_gbp,
            deposit_paid_at=rec.deposit_paid_at,
            deposit_refunded_at=refunded_at,
        )
        self._records[customer_id] = updated
        return updated

    def get(self, customer_id: str) -> Optional[CreditAssessmentRecord]:
        return self._records.get(customer_id)

    def accounts_with_deposits(self) -> List[CreditAssessmentRecord]:
        return [r for r in self._records.values() if r.requires_deposit and r.deposit_paid]

    def ppm_required_accounts(self) -> List[CreditAssessmentRecord]:
        return [r for r in self._records.values() if r.is_ppm_required]

    def deposits_eligible_for_refund(self, as_of: dt.date) -> List[CreditAssessmentRecord]:
        return [r for r in self._records.values()
                if r.deposit_refund_eligible(as_of)]

    def total_deposits_held_gbp(self) -> float:
        return sum(
            r.deposit_gbp for r in self._records.values()
            if r.deposit_paid and r.deposit_refunded_at is None
        )

    def thin_file_accounts(self) -> List[CreditAssessmentRecord]:
        return [r for r in self._records.values()
                if r.decision == CreditDecision.THIN_FILE]

    def credit_assessment_summary(self) -> str:
        total = len(self._records)
        n_dep = len(self.accounts_with_deposits())
        n_ppm = len(self.ppm_required_accounts())
        held = self.total_deposits_held_gbp()
        return (
            f"Credit Assessment Register: {total} assessments. "
            f"Deposits held: {n_dep} (£{held:,.0f} total). "
            f"PPM required: {n_ppm}. "
            f"Deposit refund eligibility: 12m good payment (Ofgem)."
        )
