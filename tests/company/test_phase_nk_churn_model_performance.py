"""Phase NK: Churn Model Performance Report -- 14 tests."""
import pytest


def _make_perf(tp, fp, fn, tn, recall, precision, f1, per_year=None):
    """Build a minimal churn_model_performance dict."""
    return {
        "total_churn_events": tp + fn,
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "true_negatives": tn,
        "recall": recall,
        "precision": precision,
        "f1_score": f1,
        "per_year": per_year or {},
    }


# ------------------------------------------------------------------
# 1. section is empty string when churn_model_performance not in data
# ------------------------------------------------------------------
def test_section_silent_missing_key():
    from saas.reporting.annual_report import _section_churn_model_performance
    assert _section_churn_model_performance({}) == ""


# ------------------------------------------------------------------
# 2. section is empty when churn_model_performance is empty dict
# ------------------------------------------------------------------
def test_section_silent_empty_dict():
    from saas.reporting.annual_report import _section_churn_model_performance
    result = _section_churn_model_performance({"churn_model_performance": {}})
    assert result == ""


# ------------------------------------------------------------------
# 3. section is empty when total_churn_events == 0 (no churns to evaluate)
# ------------------------------------------------------------------
def test_section_silent_no_churn_events():
    from saas.reporting.annual_report import _section_churn_model_performance
    perf = _make_perf(0, 0, 0, 10, 0.0, 0.0, 0.0)
    result = _section_churn_model_performance({"churn_model_performance": perf})
    assert result == ""


# ------------------------------------------------------------------
# 4. section renders heading when data present
# ------------------------------------------------------------------
def test_section_renders_heading():
    from saas.reporting.annual_report import _section_churn_model_performance
    perf = _make_perf(1, 0, 1, 8, 0.5, 1.0, 0.667)
    result = _section_churn_model_performance({"churn_model_performance": perf})
    assert "Churn Model Quality" in result


# ------------------------------------------------------------------
# 5. section shows recall label
# ------------------------------------------------------------------
def test_section_shows_recall():
    from saas.reporting.annual_report import _section_churn_model_performance
    perf = _make_perf(2, 1, 0, 8, 1.0, 0.667, 0.8)
    result = _section_churn_model_performance({"churn_model_performance": perf})
    assert "Recall" in result


# ------------------------------------------------------------------
# 6. section shows precision label
# ------------------------------------------------------------------
def test_section_shows_precision():
    from saas.reporting.annual_report import _section_churn_model_performance
    perf = _make_perf(2, 1, 0, 8, 1.0, 0.667, 0.8)
    result = _section_churn_model_performance({"churn_model_performance": perf})
    assert "Precision" in result


# ------------------------------------------------------------------
# 7. section shows F1 label
# ------------------------------------------------------------------
def test_section_shows_f1():
    from saas.reporting.annual_report import _section_churn_model_performance
    perf = _make_perf(2, 1, 0, 8, 1.0, 0.667, 0.8)
    result = _section_churn_model_performance({"churn_model_performance": perf})
    assert "F1" in result


# ------------------------------------------------------------------
# 8. RED rating when f1 < 0.3
# ------------------------------------------------------------------
def test_section_rag_red():
    from saas.reporting.annual_report import _section_churn_model_performance
    perf = _make_perf(0, 0, 6, 45, 0.0, 0.0, 0.0)
    result = _section_churn_model_performance({"churn_model_performance": perf})
    assert "RED" in result


# ------------------------------------------------------------------
# 9. GREEN rating when f1 >= 0.5
# ------------------------------------------------------------------
def test_section_rag_green():
    from saas.reporting.annual_report import _section_churn_model_performance
    perf = _make_perf(4, 0, 0, 47, 1.0, 1.0, 1.0)
    result = _section_churn_model_performance({"churn_model_performance": perf})
    assert "GREEN" in result


# ------------------------------------------------------------------
# 10. AMBER rating when 0.3 <= f1 < 0.5
# ------------------------------------------------------------------
def test_section_rag_amber():
    from saas.reporting.annual_report import _section_churn_model_performance
    perf = _make_perf(2, 3, 4, 42, 0.333, 0.4, 0.364)
    result = _section_churn_model_performance({"churn_model_performance": perf})
    assert "AMBER" in result


# ------------------------------------------------------------------
# 11. TP/FP/FN/TN counts appear in section
# ------------------------------------------------------------------
def test_section_shows_tp_fp_fn_tn():
    from saas.reporting.annual_report import _section_churn_model_performance
    perf = _make_perf(3, 2, 1, 44, 0.75, 0.6, 0.667)
    result = _section_churn_model_performance({"churn_model_performance": perf})
    assert "True Positives" in result
    assert "False Negatives" in result


# ------------------------------------------------------------------
# 12. per_year section renders when per_year data present
# ------------------------------------------------------------------
def test_section_per_year_table():
    from saas.reporting.annual_report import _section_churn_model_performance
    per_year = {
        "2020": {"tp": 1, "fp": 0, "fn": 1, "tn": 5, "recall": 0.5, "precision": 1.0},
        "2021": {"tp": 2, "fp": 1, "fn": 0, "tn": 7, "recall": 1.0, "precision": 0.667},
    }
    perf = _make_perf(3, 1, 1, 12, 0.75, 0.75, 0.75, per_year=per_year)
    result = _section_churn_model_performance({"churn_model_performance": perf})
    assert "Per-Year" in result
    assert "2020" in result
    assert "2021" in result


# ------------------------------------------------------------------
# 13. section mentions passive limitation note
# ------------------------------------------------------------------
def test_section_passive_note():
    from saas.reporting.annual_report import _section_churn_model_performance
    perf = _make_perf(1, 0, 1, 8, 0.5, 1.0, 0.667)
    result = _section_churn_model_performance({"churn_model_performance": perf})
    assert "passive" in result.lower()


# ------------------------------------------------------------------
# 14. extract_report_data includes churn_model_performance key
#     (verifies the Phase NK extraction fix in annual_report.py)
# ------------------------------------------------------------------
def test_extract_report_data_key_present():
    """Verify churn_model_performance is in extract_report_data return dict."""
    import inspect
    from saas.reporting import annual_report
    src = inspect.getsource(annual_report.extract_report_data)
    assert "churn_model_performance" in src, (
        "extract_report_data must include churn_model_performance key "
        "(Phase NK fix for silent Phase NJ regression)"
    )
