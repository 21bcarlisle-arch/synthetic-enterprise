"""Customer payment behaviour analytics: timing, DD failure rates, lateness scoring."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class PaymentResult(str, Enum):
    ON_TIME = 'on_time'
    LATE = 'late'
    DD_FAILED = 'dd_failed'
    PARTIAL = 'partial'
    MISSED = 'missed'


class PaymentBehaviour(str, Enum):
    EXCELLENT = 'excellent'
    GOOD = 'good'
    FAIR = 'fair'
    POOR = 'poor'
    CRITICAL = 'critical'


@dataclass(frozen=True)
class PaymentRecord:
    customer_id: str
    due_date: dt.date
    amount_due_gbp: float
    amount_paid_gbp: float
    payment_date: Optional[dt.date]
    result: PaymentResult

    @property
    def days_late(self) -> Optional[int]:
        if self.payment_date is None or self.result in {PaymentResult.MISSED, PaymentResult.DD_FAILED}:
            return None
        return max(0, (self.payment_date - self.due_date).days)

    @property
    def shortfall_gbp(self) -> float:
        return round(max(0.0, self.amount_due_gbp - self.amount_paid_gbp), 2)


class PaymentBehaviourAnalytics:
    def __init__(self) -> None:
        self._records: List[PaymentRecord] = []

    def record(self, customer_id: str, due_date: dt.date, amount_due_gbp: float,
                amount_paid_gbp: float, payment_date: Optional[dt.date],
                result: PaymentResult) -> PaymentRecord:
        rec = PaymentRecord(
            customer_id=customer_id, due_date=due_date,
            amount_due_gbp=amount_due_gbp, amount_paid_gbp=amount_paid_gbp,
            payment_date=payment_date, result=result,
        )
        self._records.append(rec)
        return rec

    def records_for_customer(self, customer_id: str) -> List[PaymentRecord]:
        return [r for r in self._records if r.customer_id == customer_id]

    def on_time_rate(self, customer_id: str) -> Optional[float]:
        recs = self.records_for_customer(customer_id)
        if not recs:
            return None
        on_time = sum(1 for r in recs if r.result == PaymentResult.ON_TIME)
        return round(on_time / len(recs) * 100, 1)

    def dd_failure_rate(self, customer_id: str) -> Optional[float]:
        recs = self.records_for_customer(customer_id)
        if not recs:
            return None
        failed = sum(1 for r in recs if r.result == PaymentResult.DD_FAILED)
        return round(failed / len(recs) * 100, 1)

    def avg_days_late(self, customer_id: str) -> Optional[float]:
        recs = [r for r in self.records_for_customer(customer_id)
                if r.days_late is not None and r.days_late > 0]
        if not recs:
            return None
        return round(sum(r.days_late for r in recs) / len(recs), 1)

    def behaviour_score(self, customer_id: str) -> Optional[PaymentBehaviour]:
        recs = self.records_for_customer(customer_id)
        if not recs:
            return None
        missed_or_failed = sum(1 for r in recs
                                if r.result in {PaymentResult.MISSED, PaymentResult.DD_FAILED})
        rate = missed_or_failed / len(recs)
        if rate == 0:
            return PaymentBehaviour.EXCELLENT
        if rate < 0.10:
            return PaymentBehaviour.GOOD
        if rate < 0.25:
            return PaymentBehaviour.FAIR
        if rate < 0.50:
            return PaymentBehaviour.POOR
        return PaymentBehaviour.CRITICAL

    def total_shortfall_gbp(self, customer_id: str) -> float:
        return round(sum(r.shortfall_gbp for r in self.records_for_customer(customer_id)), 2)

    def portfolio_summary(self) -> dict:
        customers = set(r.customer_id for r in self._records)
        scores: Dict[str, int] = {}
        for cid in customers:
            s = self.behaviour_score(cid)
            if s:
                scores[s.value] = scores.get(s.value, 0) + 1
        return {
            'total_customers': len(customers),
            'total_records': len(self._records),
            'by_behaviour': scores,
        }
