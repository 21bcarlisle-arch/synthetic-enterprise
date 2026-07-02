"""Phase NJ: Churn Model Calibration Report -- 16 tests."""
import pytest
from company.analytics.churn_accuracy_report import compute_churn_model_performance


def _ce(cid, estimate, event_type, year="2019", month="01"):
    return {
        "customer_id": cid,
        "event_date": f"{year}-{month}-01",
        "company_churn_estimate": estimate,
        "event_type": event_type,
    }


def _nol(cid, estimate=0.10, year="2019"):
    return {
        "customer_id": cid,
        "event_date": f"{year}-01-01",
        "company_churn_estimate": estimate,
    }


# ------------------------------------------------------------------
# 1. All TP: every predicted churn actually churned
# ------------------------------------------------------------------
def test_all_tp():
    events = [_ce("C1", 0.80, "churned")]
    result = compute_churn_model_performance(events, [], [])
    assert result["true_positives"] == 1
    assert result["false_positives"] == 0
    assert result["false_negatives"] == 0
    assert result["recall"] == 1.0
    assert result["precision"] == 1.0


# ------------------------------------------------------------------
# 2. All FN: no churns predicted, all churn
# ------------------------------------------------------------------
def test_all_fn():
    events = [_ce("C1", 0.10, "churned")]
    result = compute_churn_model_performance(events, [], [])
    assert result["true_positives"] == 0
    assert result["false_negatives"] == 1
    assert result["recall"] == 0.0
    assert result["precision"] == 0.0


# ------------------------------------------------------------------
# 3. All FP: all predicted churn, none churn
# ------------------------------------------------------------------
def test_all_fp():
    events = [_ce("C1", 0.50, "renewed")]
    result = compute_churn_model_performance(events, [], [])
    assert result["true_positives"] == 0
    assert result["false_positives"] == 1
    assert result["total_churn_events"] == 0
    assert result["recall"] == 0.0
    assert result["precision"] == 0.0


# ------------------------------------------------------------------
# 4. Mixed: 2 TP, 1 FP, 1 FN, 3 TN -> recall=2/3, precision=2/3
# ------------------------------------------------------------------
def test_mixed():
    events = [
        _ce("C1", 0.80, "churned", "2019", "01"),
        _ce("C2", 0.70, "churned", "2019", "06"),
        _ce("C3", 0.50, "renewed", "2019", "03"),
        _ce("C4", 0.10, "churned", "2020", "01"),
        _ce("C5", 0.05, "renewed", "2020", "02"),
        _ce("C6", 0.20, "renewed", "2020", "03"),
        _ce("C7", None, "renewed", "2020", "04"),
    ]
    result = compute_churn_model_performance(events, [], [])
    assert result["true_positives"] == 2
    assert result["false_positives"] == 1
    assert result["false_negatives"] == 1
    assert result["true_negatives"] == 3
    assert abs(result["recall"] - 2 / 3) < 0.001
    assert abs(result["precision"] - 2 / 3) < 0.001


# ------------------------------------------------------------------
# 5. Threshold boundary: estimate == threshold treated as not above (< not <=)
# ------------------------------------------------------------------
def test_threshold_boundary():
    events = [_ce("C1", 0.30, "churned")]
    result = compute_churn_model_performance(events, [], [], threshold=0.30)
    assert result["true_positives"] == 0
    assert result["false_negatives"] == 1
    assert result["recall"] == 0.0


# ------------------------------------------------------------------
# 6. F1 score matches 2*p*r/(p+r)
# ------------------------------------------------------------------
def test_f1_score():
    events = [
        _ce("C1", 0.80, "churned"),
        _ce("C2", 0.10, "churned"),
    ]
    result = compute_churn_model_performance(events, [], [])
    p = result["precision"]
    r = result["recall"]
    expected_f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0.0
    assert abs(result["f1_score"] - expected_f1) < 0.001


# ------------------------------------------------------------------
# 7. Per-year: two events in 2019, one in 2020 -> separate entries
# ------------------------------------------------------------------
def test_per_year():
    events = [
        _ce("C1", 0.80, "churned", "2019", "01"),
        _ce("C2", 0.50, "renewed", "2019", "06"),
        _ce("C3", 0.10, "churned", "2020", "01"),
    ]
    result = compute_churn_model_performance(events, [], [])
    assert "2019" in result["per_year"]
    assert "2020" in result["per_year"]
    y2019 = result["per_year"]["2019"]
    y2020 = result["per_year"]["2020"]
    assert y2019["tp"] == 1
    assert y2019["fp"] == 1
    assert y2020["fn"] == 1


# ------------------------------------------------------------------
# 8. Empty events: all zeros
# ------------------------------------------------------------------
def test_empty_events():
    result = compute_churn_model_performance([], [], [])
    assert result["total_churn_events"] == 0
    assert result["true_positives"] == 0
    assert result["false_positives"] == 0
    assert result["false_negatives"] == 0
    assert result["true_negatives"] == 0
    assert result["recall"] == 0.0
    assert result["precision"] == 0.0
    assert result["f1_score"] == 0.0


# ------------------------------------------------------------------
# 9. no_offer_churn_log entries count as FN (supplemental source)
# ------------------------------------------------------------------
def test_no_offer_churns_are_fn():
    no_offer = [_nol("C1", estimate=0.10, year="2019")]
    result = compute_churn_model_performance([], [], no_offer)
    assert result["false_negatives"] == 1
    assert result["total_churn_events"] == 1
    assert result["recall"] == 0.0


# ------------------------------------------------------------------
# 10. retention_log outcome=="retained" are NOT TP -- they are FP
# ------------------------------------------------------------------
def test_retained_despite_offer_are_not_tp():
    events = [_ce("C1", 0.50, "renewed")]
    retention = [{"customer_id": "C1", "event_date": "2019-01-01", "outcome": "retained"}]
    result = compute_churn_model_performance(events, retention, [])
    assert result["true_positives"] == 0
    assert result["false_positives"] == 1


# ------------------------------------------------------------------
# 11. retention_log outcome=="churned_despite_offer" correspond to TP
# ------------------------------------------------------------------
def test_churned_despite_offer_are_tp():
    events = [_ce("C1", 0.80, "churned")]
    retention = [
        {"customer_id": "C1", "event_date": "2019-01-01", "outcome": "churned_despite_offer"}
    ]
    result = compute_churn_model_performance(events, retention, [])
    assert result["true_positives"] == 1
    assert result["false_negatives"] == 0


# ------------------------------------------------------------------
# 12. above_threshold_renewed_are_fp: company over-estimated churn for renewals
# ------------------------------------------------------------------
def test_above_threshold_renewed_are_fp():
    events = [
        _ce("C1", 0.60, "renewed"),
        _ce("C2", 0.80, "renewed"),
    ]
    result = compute_churn_model_performance(events, [], [])
    assert result["false_positives"] == 2
    assert result["true_positives"] == 0
    assert result["total_churn_events"] == 0


# ------------------------------------------------------------------
# 13. total_churn_events == TP + FN (matches total actual churns)
# ------------------------------------------------------------------
def test_total_churn_events():
    events = [
        _ce("C1", 0.80, "churned"),
        _ce("C2", 0.10, "churned"),
        _ce("C3", 0.05, "renewed"),
    ]
    result = compute_churn_model_performance(events, [], [])
    actual_churns = sum(1 for e in events if e["event_type"] == "churned")
    assert result["total_churn_events"] == actual_churns
    assert result["total_churn_events"] == result["true_positives"] + result["false_negatives"]


# ------------------------------------------------------------------
# 14. recall_formula: TP / (TP + FN)
# ------------------------------------------------------------------
def test_recall_formula():
    events = [
        _ce("C1", 0.80, "churned"),
        _ce("C2", 0.75, "churned"),
        _ce("C3", 0.10, "churned"),
    ]
    result = compute_churn_model_performance(events, [], [])
    tp = result["true_positives"]
    fn = result["false_negatives"]
    expected = tp / (tp + fn)
    assert abs(result["recall"] - expected) < 0.0001


# ------------------------------------------------------------------
# 15. precision_formula: TP / (TP + FP), 0.0 if no predictions
# ------------------------------------------------------------------
def test_precision_formula():
    events = [
        _ce("C1", 0.80, "churned"),
        _ce("C2", 0.80, "renewed"),
    ]
    result = compute_churn_model_performance(events, [], [])
    tp = result["true_positives"]
    fp = result["false_positives"]
    expected = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    assert abs(result["precision"] - expected) < 0.0001

    # No predictions case
    events2 = [_ce("C3", 0.10, "churned")]
    result2 = compute_churn_model_performance(events2, [], [])
    assert result2["precision"] == 0.0


# ------------------------------------------------------------------
# 16. f1_zero_if_no_predictions: F1 = 0 when precision=0 and recall=0
# ------------------------------------------------------------------
def test_f1_zero_if_no_predictions():
    events = [_ce("C1", 0.10, "churned")]
    result = compute_churn_model_performance(events, [], [])
    assert result["precision"] == 0.0
    assert result["recall"] == 0.0
    assert result["f1_score"] == 0.0
