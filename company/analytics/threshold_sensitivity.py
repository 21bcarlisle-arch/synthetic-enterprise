from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ThresholdPoint:
    threshold: float
    tp: int
    fp: int
    fn: int
    tn: int
    recall: float
    precision: float
    f1: float


@dataclass
class ThresholdSensitivityResult:
    curve: list[ThresholdPoint]
    optimal_threshold: float
    optimal_f1: float
    current_threshold: float
    current_f1: float


def compute_threshold_sensitivity(
    customer_events: list[dict[str, Any]],
    no_offer_churn_log: list[dict[str, Any]],
    current_threshold: float = 0.30,
    steps: list[float] | None = None,
) -> ThresholdSensitivityResult:
    """Compute recall/precision/F1 at each threshold from 0% to 50% in 5% steps.

    Treats churned customers as positives.
    - TP: company_churn_estimate >= threshold AND customer churned
    - FP: company_churn_estimate >= threshold AND customer renewed
    - FN: company_churn_estimate < threshold AND customer churned
    - TN: company_churn_estimate < threshold AND customer renewed
    """
    if steps is None:
        steps = [t / 100 for t in range(0, 55, 5)]

    churned_at_renewal = {
        (e["customer_id"], e.get("event_date", ""))
        for e in customer_events
        if e.get("event_type") == "churned"
    }
    no_offer_churned = {
        (m["customer_id"], m["event_date"])
        for m in no_offer_churn_log
    }
    all_churned = churned_at_renewal | no_offer_churned

    all_renewals = [
        e for e in customer_events
        if e.get("event_type") in ("churned", "renewed")
    ]
    for m in no_offer_churn_log:
        key = (m["customer_id"], m["event_date"])
        if not any(
            (e["customer_id"], e.get("event_date", "")) == key
            for e in all_renewals
        ):
            all_renewals.append({
                "customer_id": m["customer_id"],
                "event_date": m["event_date"],
                "event_type": "churned",
                "company_churn_estimate": m["company_churn_estimate"],
            })

    curve: list[ThresholdPoint] = []
    for thresh in steps:
        tp = fp = fn = tn = 0
        for e in all_renewals:
            key = (e["customer_id"], e.get("event_date", ""))
            est = e.get("company_churn_estimate") or 0.0
            predicted_churn = est >= thresh
            actually_churned = key in all_churned
            if predicted_churn and actually_churned:
                tp += 1
            elif predicted_churn and not actually_churned:
                fp += 1
            elif not predicted_churn and actually_churned:
                fn += 1
            else:
                tn += 1
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
        curve.append(ThresholdPoint(thresh, tp, fp, fn, tn, recall, precision, f1))

    best = max(curve, key=lambda p: p.f1)
    current_pt = next((p for p in curve if abs(p.threshold - current_threshold) < 1e-9), curve[0])

    return ThresholdSensitivityResult(
        curve=curve,
        optimal_threshold=best.threshold,
        optimal_f1=best.f1,
        current_threshold=current_threshold,
        current_f1=current_pt.f1,
    )
