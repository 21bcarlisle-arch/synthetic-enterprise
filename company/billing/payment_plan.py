from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import List, Optional


class PaymentPlanStatus(str, Enum):
    # Offered by the company and not (yet) agreed. An offer is a fact the company holds; agreement
    # is the household's act, and until something tells the company the household agreed, an
    # offered plan is never ACTIVE (atom EP4: the arrangement exit is a world answer).
    OFFERED = "offered"
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
    # Monthly agreed amount. None on an OFFERED plan: SLC 27.8 sets it from the household's ability
    # to pay, which the company learns only in the affordability conversation an offer opens.
    installment_gbp: Optional[float]
    start_date: date
    status: PaymentPlanStatus = PaymentPlanStatus.ACTIVE
    payments_made: int = 0
    total_paid_gbp: float = 0.0
    missed_payments: int = 0

    @property
    def expected_months(self) -> Optional[int]:
        if self.installment_gbp is None:
            return None
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

    def offer_plan(self, customer_id: str, debt_gbp: float, offered_on: date) -> PaymentPlan:
        """Record that the company OFFERED an arrangement against `debt_gbp` on `offered_on`.

        The instalment is left None and the status OFFERED: what the household can afford, and
        whether it agrees, are its answers, not the company's (SLC 27.8). Nothing here may promote
        an offer to ACTIVE; an agreement must arrive as a fact from outside the company."""
        plan = PaymentPlan(
            plan_id=self._next_id,
            customer_id=customer_id,
            original_debt_gbp=debt_gbp,
            installment_gbp=None,
            start_date=offered_on,
            status=PaymentPlanStatus.OFFERED,
        )
        self._plans.append(plan)
        self._next_id += 1
        return plan

    def accept_offer(self, plan_id: int, installment_gbp: float) -> PaymentPlan:
        """The household AGREED offer `plan_id` at `installment_gbp` -- a fact the caller received
        from outside the company (the world's answer through the seam), never one it inferred.
        Refuses anything but an OFFERED plan, and an instalment that is not a positive amount."""
        if not installment_gbp or installment_gbp <= 0:
            raise ValueError(f"plan {plan_id}: an agreed instalment must be positive, "
                             f"got {installment_gbp!r}")
        for plan in self._plans:
            if plan.plan_id == plan_id:
                if plan.status != PaymentPlanStatus.OFFERED:
                    raise ValueError(f"plan {plan_id} is {plan.status.value}, not offered")
                plan.installment_gbp = installment_gbp
                plan.status = PaymentPlanStatus.ACTIVE
                return plan
        raise KeyError(plan_id)

    def offered_plans(self) -> List[PaymentPlan]:
        return [p for p in self._plans if p.status == PaymentPlanStatus.OFFERED]

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
                "total_plans": 0, "offered": 0, "active": 0, "completed": 0,
                "defaulted": 0, "cancelled": 0, "avg_original_debt_gbp": 0.0
            }
        return {
            "total_plans": n,
            "offered": sum(1 for p in self._plans if p.status == PaymentPlanStatus.OFFERED),
            "active": sum(1 for p in self._plans if p.status == PaymentPlanStatus.ACTIVE),
            "completed": sum(1 for p in self._plans if p.status == PaymentPlanStatus.COMPLETED),
            "defaulted": sum(1 for p in self._plans if p.status == PaymentPlanStatus.DEFAULTED),
            "cancelled": sum(1 for p in self._plans if p.status == PaymentPlanStatus.CANCELLED),
            "avg_original_debt_gbp": round(
                sum(p.original_debt_gbp for p in self._plans) / n, 2
            ),
        }
