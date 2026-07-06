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
        "episode_analysis": _compute_episode_analysis(
            customer_events, retention_log, no_offer_churn_log, threshold
        ),
    }


def _compute_episode_analysis(
    customer_events: list[dict],
    retention_log: list[dict],
    no_offer_churn_log: list[dict],
    threshold: float,
) -> dict:
    """Credit the model for catching a customer's risk at ANY renewal before
    departure, not only the terminal one.

    The per-event TP/FP/FN/TN counts above score every renewal in isolation,
    so a customer correctly flagged and saved by a retention offer (estimate
    above threshold, outcome "retained") at renewal N, whose satisfaction
    signal then decays back down before they eventually churn at renewal
    N+k, is scored as a false positive at N AND a false negative at N+k --
    the same real, correctly-detected risk penalised twice. This computes an
    episode-level view instead: group each customer's renewals in order,
    and ask "did the model ever flag this customer before they left?"
    """
    by_customer: dict[str, list[dict]] = {}
    for e in customer_events:
        cid = e.get("customer_id")
        if cid is None:
            continue
        by_customer.setdefault(cid, []).append(e)
    for evs in by_customer.values():
        evs.sort(key=lambda e: e.get("event_date") or "")

    retained_dates: dict[str, set] = {}
    offered_dates: dict[str, set] = {}
    prevented_churn_saves = 0
    for r in retention_log:
        cid = r.get("customer_id")
        if cid is None:
            continue
        offered_dates.setdefault(cid, set()).add(r.get("event_date"))
        if r.get("outcome") == "retained":
            retained_dates.setdefault(cid, set()).add(r.get("event_date"))
            prevented_churn_saves += 1

    churners: dict[str, str] = {}
    for e in customer_events:
        if e.get("event_type") == "churned":
            churners[e["customer_id"]] = e.get("event_date")
    for e in no_offer_churn_log:
        cid = e.get("customer_id")
        if cid is not None and cid not in churners:
            churners[cid] = e.get("event_date")

    caught_before_departure = 0
    never_flagged = 0
    decayed_after_prior_save = 0

    for cid, churn_date in churners.items():
        history = by_customer.get(cid, [])
        was_flagged = any(
            e.get("company_churn_estimate") is not None
            and e["company_churn_estimate"] > threshold
            for e in history
        )
        was_offered = cid in offered_dates
        flagged = was_flagged or was_offered
        if flagged:
            caught_before_departure += 1
            had_prior_save = any(
                d is not None and d < (churn_date or "") for d in retained_dates.get(cid, set())
            )
            if had_prior_save:
                decayed_after_prior_save += 1
        else:
            never_flagged += 1

    total_churners = len(churners)
    episode_recall = (
        round(caught_before_departure / total_churners, 4) if total_churners > 0 else 0.0
    )

    return {
        "total_churners": total_churners,
        "caught_before_departure": caught_before_departure,
        "never_flagged": never_flagged,
        "episode_recall": episode_recall,
        "decayed_after_prior_save": decayed_after_prior_save,
        "prevented_churn_saves": prevented_churn_saves,
    }
