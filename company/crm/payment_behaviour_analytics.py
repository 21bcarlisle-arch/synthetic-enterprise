"""Company-side payment behaviour analytics.

Scores customers based on observable payment records (ON_TIME / LATE / DD_FAILED).
Does not read income_stress or any SIM internal -- only observed payment outcomes.
Consistent with the SIM/company epistemic barrier.

A deteriorating score is a leading indicator for churn risk and debt exposure,
informing the company's CRM and retention response without revealing SIM ground truth.
"""
from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional


class BehaviourScore(str, Enum):
    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    FAIR = "FAIR"
    POOR = "POOR"
    CRITICAL = "CRITICAL"


_SCORE_ORDER: dict[str, int] = {
    BehaviourScore.EXCELLENT: 0,
    BehaviourScore.GOOD: 1,
    BehaviourScore.FAIR: 2,
    BehaviourScore.POOR: 3,
    BehaviourScore.CRITICAL: 4,
}


def compute_payment_metrics(records: list[dict]) -> dict:
    if not records:
        return {"on_time_rate": 0.0, "late_rate": 0.0, "dd_fail_rate": 0.0, "avg_days_late": 0.0}
    n = len(records)
    on_time = sum(1 for r in records if r.get("result") == "ON_TIME")
    late = sum(1 for r in records if r.get("result") == "LATE")
    dd_fail = sum(1 for r in records if r.get("result") == "DD_FAILED")
    days_late_vals = [r.get("days_late", 0) or 0 for r in records if r.get("result") in ("LATE", "DD_FAILED")]
    avg_days_late = sum(days_late_vals) / len(days_late_vals) if days_late_vals else 0.0
    return {
        "on_time_rate": on_time / n,
        "late_rate": late / n,
        "dd_fail_rate": dd_fail / n,
        "avg_days_late": avg_days_late,
    }


def score_payment_history(records: list[dict]) -> BehaviourScore:
    if not records:
        return BehaviourScore.EXCELLENT
    m = compute_payment_metrics(records)
    otr = m["on_time_rate"]
    ddf = m["dd_fail_rate"]
    if otr >= 0.95 and ddf == 0.0:
        return BehaviourScore.EXCELLENT
    if otr >= 0.80 and ddf < 0.05:
        return BehaviourScore.GOOD
    if otr >= 0.60 and ddf < 0.15:
        return BehaviourScore.FAIR
    if otr >= 0.40 and ddf < 0.35:
        return BehaviourScore.POOR
    return BehaviourScore.CRITICAL


class PaymentBehaviourAnalytics:
    def __init__(self) -> None:
        self._records: Dict[str, List[dict]] = {}

    def record_payment(self, customer_id: str, record: dict) -> None:
        if customer_id not in self._records:
            self._records[customer_id] = []
        self._records[customer_id].append(record)

    def get_score(self, customer_id: str) -> Optional[BehaviourScore]:
        if customer_id not in self._records:
            return None
        return score_payment_history(self._records[customer_id])

    def get_metrics(self, customer_id: str) -> Optional[dict]:
        if customer_id not in self._records:
            return None
        return compute_payment_metrics(self._records[customer_id])

    def is_at_risk(self, customer_id: str) -> bool:
        score = self.get_score(customer_id)
        if score is None:
            return False
        return score in (BehaviourScore.POOR, BehaviourScore.CRITICAL)

    def at_risk_customers(self) -> List[str]:
        return [cid for cid in self._records if self.is_at_risk(cid)]

    def get_miss_trajectory(self, customer_id: str) -> List[dict]:
        """Return [{"year": int, "late": int, "dd_failed": int, "total": int}, ...].

        Unlike get_score/get_metrics (rolling scalars over all-time history),
        this buckets the already-retained per-event record list (each carries
        a due_date) by calendar year -- no separate snapshot bookkeeping is
        needed since the full history is never discarded.
        """
        recs = self._records.get(customer_id, [])
        by_year: Dict[int, dict] = {}
        for r in recs:
            due = r.get("due_date")
            if due is None:
                continue
            year = due.year if hasattr(due, "year") else int(str(due)[:4])
            bucket = by_year.setdefault(year, {"late": 0, "dd_failed": 0, "total": 0})
            bucket["total"] += 1
            if r.get("result") == "LATE":
                bucket["late"] += 1
            elif r.get("result") == "DD_FAILED":
                bucket["dd_failed"] += 1
        return [{"year": yr, **by_year[yr]} for yr in sorted(by_year)]

    def score_trend(self, customer_id: str, window: int = 6) -> str:
        recs = self._records.get(customer_id, [])
        recent = recs[-window:] if len(recs) >= window else recs
        if len(recent) < 4:
            return "STABLE"
        mid = len(recent) // 2
        first_score = score_payment_history(recent[:mid])
        second_score = score_payment_history(recent[mid:])
        first_ord = _SCORE_ORDER[first_score]
        second_ord = _SCORE_ORDER[second_score]
        if second_ord < first_ord:
            return "IMPROVING"
        if second_ord > first_ord:
            return "DETERIORATING"
        return "STABLE"
