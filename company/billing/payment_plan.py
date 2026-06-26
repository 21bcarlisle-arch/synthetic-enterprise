from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum
from typing import List, Optional
import math


class PaymentPlanStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    DEFAULTED = "defaulted"
    CANCELLED = "cancelled"


_DEFAULT_THRESHOLD = 2   # missed payments before plan defaults


@dataclass
class PaymentPlan:
    plan_id: int
    customer_id: str
    original_debt_gbp: float
    installment_gbp: float       # monthly agreed amount
    start_date: date
    status: PaymentPlanStatus = PaymentPlanStatus.ACTIVE
    payments_made: int = 0
    total_paid_gbp: float = 0.0
    missed_payments: int = 0

    @property
    def expected_months(self) -> int:
        return math.ceil(self.original_debt_gbp / self.installment_gbp)

    @property
    def remaining_debt_gbp(self) -> float:
        return max(0.0, round(self.original_debt_gbp - self.total_paid_gbp, 2))

    @property
    def is_complete(self) -> bool:
        return self.remaining_debt_gbp == 0.0


@dataclass
class PaymentPlanBook:
    """Manages structured repayment plans for customers in arrears (Ofgem SLC 27A)."""

    _plans: List[PaymentPlan] = field(default_factory=list)
    _next_id: int = field(default=1)

    def create_plan(
        self,
        customer_id: str,
        original_debt_gbp: float,
        installment_gbp: float,
        start_date: date,
    ) -> PaymentPlan:
        plan = PaymentPlan(
            plan_id=self._next_id,
            customer_id=customer_id,
            original_debt_gbp=original_debt_gbp,
            installment_gbp=installment_gbp,
            start_date=start_date,
        )
        self._plans.append(plan)
        self._next_id += 1
        return plan

    def record_payment(self, plan_id: int, payment_date: date) -> bool:
        """Record a successful installment. Returns False if plan not found."""
        for plan in self._plans:
            if plan.plan_id == plan_id and plan.status == PaymentPlanStatus.ACTIVE:
                amount = min(plan.installment_gbp, plan.remaining_debt_gbp)
                plan.payments_made += 1
                plan.total_paid_gbp = round(plan.total_paid_gbp + amount, 2)
                if plan.is_complete:
                    plan.status = PaymentPlanStatus.COMPLETED
                return True
        return False

    def record_missed(self, plan_id: int, threshold: int = _DEFAULT_THRESHOLD) -> Optional[PaymentPlan]:
        """Record a missed payment; returns plan after update (None if not found)."""
        for plan in self._plans:
            if plan.plan_id == plan_id and plan.status == PaymentPlanStatus.ACTIVE:
                plan.missed_payments += 1
                if plan.missed_payments >= threshold:
                    plan.status = PaymentPlanStatus.DEFAULTED
                return plan
        return None

    def cancel_plan(self, plan_id: int) -> bool:
        for plan in self._plans:
            if plan.plan_id == plan_id:
                plan.status = PaymentPlanStatus.CANCELLED
                return True
        return False

    def active_plans(self) -> List[PaymentPlan]:
        return [p for p in self._plans if p.status == PaymentPlanStatus.ACTIVE]

    def defaulted_plans(self) -> List[PaymentPlan]:
        return [p for p in self._plans if p.status == PaymentPlanStatus.DEFAULTED]

    def plans_for_customer(self, customer_id: str) -> List[PaymentPlan]:
        return [p for p in self._plans if p.customer_id == customer_id]

    def portfolio_summary(self) -> dict:
        n = len(self._plans)
        if n == 0:
            return {
                "total_plans": 0, "active": 0, "completed": 0,
                "defaulted": 0, "cancelled": 0, "avg_original_debt_gbp": 0.0
            }
        return {
            "total_plans": n,
            "active": sum(1 for p in self._plans if p.status == PaymentPlanStatus.ACTIVE),
            "completed": sum(1 for p in self._plans if p.status == PaymentPlanStatus.COMPLETED),
            "defaulted": sum(1 for p in self._plans if p.status == PaymentPlanStatus.DEFAULTED),
            "cancelled": sum(1 for p in self._plans if p.status == PaymentPlanStatus.CANCELLED),
            "avg_original_debt_gbp": round(
                sum(p.original_debt_gbp for p in self._plans) / n, 2
            ),
        }
