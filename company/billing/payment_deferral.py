from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class DeferralStatus(str, Enum):
    ACTIVE = 'active'
    COMPLETED = 'completed'
    DEFAULTED = 'defaulted'
    CANCELLED = 'cancelled'


class DeferralReason(str, Enum):
    FINANCIAL_HARDSHIP = 'financial_hardship'
    COVID_19 = 'covid_19'
    JOB_LOSS = 'job_loss'
    ILLNESS = 'illness'
    BEREAVEMENT = 'bereavement'
    BENEFIT_DELAY = 'benefit_delay'


@dataclass
class PaymentDeferral:
    deferral_id: str
    customer_id: str
    reason: DeferralReason
    deferred_amount_gbp: float
    deferral_start: dt.date
    deferral_end: dt.date
    repayment_plan_monthly_gbp: float
    status: DeferralStatus = DeferralStatus.ACTIVE
    amount_repaid_gbp: float = 0.0

    @property
    def outstanding_gbp(self) -> float:
        return max(0.0, round(self.deferred_amount_gbp - self.amount_repaid_gbp, 2))

    @property
    def is_active(self) -> bool:
        return self.status == DeferralStatus.ACTIVE

    @property
    def deferral_days(self) -> int:
        return (self.deferral_end - self.deferral_start).days


class PaymentDeferralBook:
    def __init__(self) -> None:
        self._deferrals: Dict[str, PaymentDeferral] = {}
        self._next_id = 1

    def create(self, customer_id: str, reason: DeferralReason,
               deferred_amount_gbp: float, deferral_start: dt.date,
               deferral_end: dt.date, repayment_plan_monthly_gbp: float
               ) -> PaymentDeferral:
        deferral_id = f'DEF-{self._next_id:04d}'
        self._next_id += 1
        d = PaymentDeferral(
            deferral_id=deferral_id,
            customer_id=customer_id,
            reason=reason,
            deferred_amount_gbp=deferred_amount_gbp,
            deferral_start=deferral_start,
            deferral_end=deferral_end,
            repayment_plan_monthly_gbp=repayment_plan_monthly_gbp,
        )
        self._deferrals[deferral_id] = d
        return d

    def record_repayment(self, deferral_id: str, amount_gbp: float) -> PaymentDeferral:
        d = self._deferrals[deferral_id]
        d.amount_repaid_gbp = round(d.amount_repaid_gbp + amount_gbp, 2)
        if d.outstanding_gbp == 0.0:
            d.status = DeferralStatus.COMPLETED
        return d

    def mark_defaulted(self, deferral_id: str) -> PaymentDeferral:
        self._deferrals[deferral_id].status = DeferralStatus.DEFAULTED
        return self._deferrals[deferral_id]

    def cancel(self, deferral_id: str) -> PaymentDeferral:
        self._deferrals[deferral_id].status = DeferralStatus.CANCELLED
        return self._deferrals[deferral_id]

    def active_deferrals(self) -> List[PaymentDeferral]:
        return [d for d in self._deferrals.values() if d.is_active]

    def overdue_deferrals(self, as_of: dt.date) -> List[PaymentDeferral]:
        return [d for d in self._deferrals.values()
                if d.is_active and d.deferral_end < as_of]

    def deferrals_for_customer(self, customer_id: str) -> List[PaymentDeferral]:
        return [d for d in self._deferrals.values() if d.customer_id == customer_id]

    def total_deferred_outstanding_gbp(self) -> float:
        return round(sum(d.outstanding_gbp for d in self._deferrals.values() if d.is_active), 2)

    def annual_summary(self) -> dict:
        all_d = list(self._deferrals.values())
        by_reason: dict = {}
        for d in all_d:
            by_reason[d.reason.value] = by_reason.get(d.reason.value, 0) + 1
        return {
            'total_deferrals': len(all_d),
            'active': len([d for d in all_d if d.status == DeferralStatus.ACTIVE]),
            'completed': len([d for d in all_d if d.status == DeferralStatus.COMPLETED]),
            'defaulted': len([d for d in all_d if d.status == DeferralStatus.DEFAULTED]),
            'total_deferred_outstanding_gbp': self.total_deferred_outstanding_gbp(),
            'by_reason': by_reason,
        }
