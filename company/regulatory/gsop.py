from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum
from typing import Dict, List, Optional


class GSOPType(str, Enum):
    MISSED_APPOINTMENT = "missed_appointment"
    ERRONEOUS_TRANSFER = "erroneous_transfer"
    WRONGFUL_DISCONNECT = "wrongful_disconnect"
    FINAL_BILL_DELAY = "final_bill_delay"
    REFUND_DELAY = "refund_delay"


# Statutory payment amounts (pence-equivalent in GBP) — Ofgem-set, approximate calendar year
_GSOP_AMOUNT_GBP: Dict[GSOPType, float] = {
    GSOPType.MISSED_APPOINTMENT: 30.0,
    GSOPType.ERRONEOUS_TRANSFER: 30.0,
    GSOPType.WRONGFUL_DISCONNECT: 30.0,   # per day, capped at 10 days
    GSOPType.FINAL_BILL_DELAY: 30.0,
    GSOPType.REFUND_DELAY: 30.0,
}

# Working days allowed before payment is due (from trigger date)
_GSOP_PAYMENT_DAYS: Dict[GSOPType, int] = {
    GSOPType.MISSED_APPOINTMENT: 10,
    GSOPType.ERRONEOUS_TRANSFER: 20,
    GSOPType.WRONGFUL_DISCONNECT: 2,
    GSOPType.FINAL_BILL_DELAY: 10,
    GSOPType.REFUND_DELAY: 10,
}


def _add_working_days(start: date, n: int) -> date:
    """Advance n working days (Mon-Fri) from start."""
    current = start
    added = 0
    while added < n:
        current += timedelta(days=1)
        if current.weekday() < 5:   # Mon-Fri
            added += 1
    return current


@dataclass
class GSOPPayment:
    payment_id: int
    customer_id: str
    gsop_type: GSOPType
    trigger_date: date
    payment_due_date: date
    amount_gbp: float
    paid_date: Optional[date] = None

    @property
    def is_paid(self) -> bool:
        return self.paid_date is not None

    def is_overdue(self, as_of: date) -> bool:
        return not self.is_paid and as_of > self.payment_due_date


@dataclass
class GSOPBook:
    """Tracks GSOP triggers and auto-payments for Ofgem compliance."""

    _payments: List[GSOPPayment] = field(default_factory=list)
    _next_id: int = field(default=1)

    def record_trigger(
        self,
        customer_id: str,
        gsop_type: GSOPType,
        trigger_date: date,
    ) -> GSOPPayment:
        due_date = _add_working_days(trigger_date, _GSOP_PAYMENT_DAYS[gsop_type])
        payment = GSOPPayment(
            payment_id=self._next_id,
            customer_id=customer_id,
            gsop_type=gsop_type,
            trigger_date=trigger_date,
            payment_due_date=due_date,
            amount_gbp=_GSOP_AMOUNT_GBP[gsop_type],
        )
        self._payments.append(payment)
        self._next_id += 1
        return payment

    def pay(self, payment_id: int, paid_date: date) -> bool:
        for p in self._payments:
            if p.payment_id == payment_id:
                p.paid_date = paid_date
                return True
        return False

    def overdue(self, as_of: date) -> List[GSOPPayment]:
        return [p for p in self._payments if p.is_overdue(as_of)]

    def total_liability_gbp(self, year: Optional[int] = None) -> float:
        payments = self._payments
        if year is not None:
            payments = [p for p in payments if p.trigger_date.year == year]
        return sum(p.amount_gbp for p in payments)

    def annual_report(self, year: int) -> dict:
        year_payments = [p for p in self._payments if p.trigger_date.year == year]
        if not year_payments:
            return {
                "year": year,
                "total_triggers": 0,
                "total_paid": 0,
                "total_liability_gbp": 0.0,
                "auto_pay_rate_pct": 100.0,
                "overdue_count": 0,
                "by_type": {},
            }
        cutoff = date(year, 12, 31)
        paid = [p for p in year_payments if p.is_paid]
        overdue = [p for p in year_payments if p.is_overdue(cutoff)]
        by_type: Dict[str, int] = {}
        for p in year_payments:
            by_type[p.gsop_type.value] = by_type.get(p.gsop_type.value, 0) + 1
        auto_pay_rate = len(paid) / len(year_payments) * 100.0
        return {
            "year": year,
            "total_triggers": len(year_payments),
            "total_paid": len(paid),
            "total_liability_gbp": round(sum(p.amount_gbp for p in year_payments), 2),
            "auto_pay_rate_pct": round(auto_pay_rate, 1),
            "overdue_count": len(overdue),
            "by_type": by_type,
        }
