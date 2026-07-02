from __future__ import annotations


def compute_churn_model_performance(
    customer_events: list[dict],
    retention_log: list[dict],
    no_offer_churn_log: list[dict],
    threshold: float = 0.30,
) -> dict:
    """Compare company churn estimates against observed outcomes.

    Uses company_churn_estimate vs threshold from customer_events for primary
    classification, with no_offer_churn_log as supplemental FN source for
    churns that have no corresponding customer_events entry.

    Returns TP/FP/FN/TN counts, recall, precision, F1, and a per-year breakdown.
    """
    tp = fp = fn = tn = 0
    per_year: dict[str, dict] = {}

    def _add(bucket: str, year: str) -> None:
        if year:
            d = per_year.setdefault(year, {"tp": 0, "fp": 0, "fn": 0, "tn": 0})
            d[bucket] += 1

    counted_churns: set[tuple] = set()

    for e in customer_events:
        estimate = e.get("company_churn_estimate")
        event_type = e.get("event_type")
        yr = (e.get("event_date") or "")[:4]
        key = (e.get("customer_id"), e.get("event_date"))

        if event_type == "churned":
            counted_churns.add(key)

        predicted = estimate is not None and estimate > threshold

        if predicted and event_type == "churned":
            tp += 1
            _add("tp", yr)
        elif predicted and event_type == "renewed":
            fp += 1
            _add("fp", yr)
        elif not predicted and event_type == "churned":
            fn += 1
            _add("fn", yr)
        elif not predicted and event_type == "renewed":
            tn += 1
            _add("tn", yr)

    # Supplemental FN: no_offer_churn_log entries absent from customer_events
    for e in no_offer_churn_log:
        key = (e.get("customer_id"), e.get("event_date"))
        if key not in counted_churns:
            fn += 1
            yr = (e.get("event_date") or "")[:4]
            _add("fn", yr)
            counted_churns.add(key)

    total_churn_events = tp + fn
    recall = tp / total_churn_events if total_churn_events > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    for d in per_year.values():
        y_tp = d["tp"]
        y_fn = d["fn"]
        y_fp = d["fp"]
        y_total = y_tp + y_fn
        d["recall"] = round(y_tp / y_total, 4) if y_total > 0 else 0.0
        d["precision"] = round(y_tp / (y_tp + y_fp), 4) if (y_tp + y_fp) > 0 else 0.0

    return {
        "total_churn_events": total_churn_events,
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "true_negatives": tn,
        "recall": round(recall, 4),
        "precision": round(precision, 4),
        "f1_score": round(f1, 4),
        "per_year": per_year,
    }
