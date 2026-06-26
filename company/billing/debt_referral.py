from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Dict, List, Optional


class DebtAdviceOrg(str, Enum):
    STEP_CHANGE = "step_change"
    CITIZENS_ADVICE = "citizens_advice"
    NATIONAL_DEBTLINE = "national_debtline"
    MONEY_ADVICE_SERVICE = "money_advice_service"


class ReferralStatus(str, Enum):
    REFERRED = "referred"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    COMPLETED = "completed"
    NO_RESPONSE = "no_response"


# Debt threshold above which referral becomes mandatory under SLC 27A (Ability to Pay)
REFERRAL_THRESHOLD_GBP = 200.0


@dataclass
class DebtReferral:
    referral_id: int
    customer_id: str
    total_debt_gbp: float
    referral_date: date
    org: DebtAdviceOrg
    status: ReferralStatus = ReferralStatus.REFERRED
    response_date: Optional[date] = None
    outcome_notes: Optional[str] = None

    @property
    def is_resolved(self) -> bool:
        return self.status in (
            ReferralStatus.ACCEPTED,
            ReferralStatus.DECLINED,
            ReferralStatus.COMPLETED,
            ReferralStatus.NO_RESPONSE,
        )


@dataclass
class DebtReferralBook:
    """Tracks mandatory debt advice referrals under Ofgem SLC 27A (Ability to Pay)."""

    _referrals: List[DebtReferral] = field(default_factory=list)
    _next_id: int = field(default=1)

    def refer(
        self,
        customer_id: str,
        total_debt_gbp: float,
        referral_date: date,
        org: DebtAdviceOrg = DebtAdviceOrg.STEP_CHANGE,
    ) -> DebtReferral:
        ref = DebtReferral(
            referral_id=self._next_id,
            customer_id=customer_id,
            total_debt_gbp=total_debt_gbp,
            referral_date=referral_date,
            org=org,
        )
        self._referrals.append(ref)
        self._next_id += 1
        return ref

    def update_status(
        self,
        referral_id: int,
        status: ReferralStatus,
        response_date: Optional[date] = None,
        notes: Optional[str] = None,
    ) -> bool:
        for r in self._referrals:
            if r.referral_id == referral_id:
                r.status = status
                r.response_date = response_date
                r.outcome_notes = notes
                return True
        return False

    def outstanding_referrals(self) -> List[DebtReferral]:
        return [r for r in self._referrals if r.status == ReferralStatus.REFERRED]

    @staticmethod
    def eligible_for_referral(total_debt_gbp: float, threshold: float = REFERRAL_THRESHOLD_GBP) -> bool:
        return total_debt_gbp >= threshold

    def referrals_for_customer(self, customer_id: str) -> List[DebtReferral]:
        return [r for r in self._referrals if r.customer_id == customer_id]

    def annual_summary(self, year: int) -> dict:
        year_refs = [r for r in self._referrals if r.referral_date.year == year]
        if not year_refs:
            return {
                "year": year,
                "total_referred": 0,
                "accepted": 0,
                "declined": 0,
                "completed": 0,
                "no_response": 0,
                "outstanding": 0,
            }
        return {
            "year": year,
            "total_referred": len(year_refs),
            "accepted": sum(1 for r in year_refs if r.status == ReferralStatus.ACCEPTED),
            "declined": sum(1 for r in year_refs if r.status == ReferralStatus.DECLINED),
            "completed": sum(1 for r in year_refs if r.status == ReferralStatus.COMPLETED),
            "no_response": sum(1 for r in year_refs if r.status == ReferralStatus.NO_RESPONSE),
            "outstanding": sum(1 for r in year_refs if r.status == ReferralStatus.REFERRED),
        }
