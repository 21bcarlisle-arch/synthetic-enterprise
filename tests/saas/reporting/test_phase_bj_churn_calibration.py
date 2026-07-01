"""Phase BJ: Churn Prediction Calibration section tests."""
import pytest
from saas.reporting.annual_report import _section_churn_prediction_calibration


def _churn(cid, date, sim_p, co_p):
    return {
        "event_type": "churn",
        "customer_id": cid,
        "event_date": date,
        "sim_churn_probability": sim_p,
        "company_churn_estimate": co_p,
    }


def _acq(cid, date):
    return {"event_type": "acquisition", "customer_id": cid, "event_date": date}


# 1. Empty returns empty
def test_empty_returns_empty():
    assert _section_churn_prediction_calibration({}) == ""
    assert _section_churn_prediction_calibration({"company_event_log": []}) == ""
    # Acquisition-only events also return empty
    assert _section_churn_prediction_calibration({"company_event_log": [_acq("C1", "2022-01-01")]}) == ""


# 2. Header present
def test_header_present():
    d = {"company_event_log": [_churn("C3", "2020-06-30", 0.32, 0.0)]}
    assert "Churn Prediction Calibration" in _section_churn_prediction_calibration(d)


# 3. UNDERESTIMATED when company < sim by > 10pp
def test_underestimated_verdict():
    d = {"company_event_log": [_churn("C3", "2020-06-30", 0.32, 0.0)]}
    assert "UNDERESTIMATED" in _section_churn_prediction_calibration(d)


# 4. OVERESTIMATED when company > sim by > 10pp
def test_overestimated_verdict():
    d = {"company_event_log": [_churn("C5", "2021-12-30", 0.35, 0.83)]}
    assert "OVERESTIMATED" in _section_churn_prediction_calibration(d)


# 5. ACCURATE when delta < 10pp
def test_accurate_verdict():
    d = {"company_event_log": [_churn("C1", "2022-01-01", 0.50, 0.55)]}
    assert "ACCURATE" in _section_churn_prediction_calibration(d)


# 6. Systematic bias UNDER shown when underest > overest
def test_systematic_under_bias():
    d = {"company_event_log": [
        _churn("C1", "2020-01-01", 0.30, 0.0),  # under
        _churn("C2", "2021-01-01", 0.30, 0.0),  # under
        _churn("C3", "2022-01-01", 0.50, 0.80),  # over
    ]}
    assert "UNDER-predicted" in _section_churn_prediction_calibration(d)


# 7. Systematic bias OVER shown when overest > underest
def test_systematic_over_bias():
    d = {"company_event_log": [
        _churn("C1", "2022-01-01", 0.30, 0.80),  # over
        _churn("C2", "2023-01-01", 0.20, 0.75),  # over
        _churn("C3", "2024-01-01", 0.30, 0.0),   # under
    ]}
    assert "OVER-predicted" in _section_churn_prediction_calibration(d)


# 8. MAE computed
def test_mae_computed():
    d = {"company_event_log": [
        _churn("C1", "2022-01-01", 0.50, 0.0),  # delta = -50pp
    ]}
    result = _section_churn_prediction_calibration(d)
    assert "50.0pp" in result  # MAE


# 9. Delta sign shown in table
def test_delta_sign_positive():
    d = {"company_event_log": [_churn("C5", "2021-12-30", 0.35, 0.83)]}
    result = _section_churn_prediction_calibration(d)
    assert "+48" in result or "+48.0pp" in result or "+48.0" in result


# 10. Acquisition events filtered out
def test_acquisition_filtered():
    d = {"company_event_log": [
        _acq("C2_2", "2022-03-31"),
        _churn("C1", "2021-12-30", 0.32, 0.04),
    ]}
    result = _section_churn_prediction_calibration(d)
    assert "Churn Prediction Calibration" in result
    # Only 1 churn event, not 2
    assert "1 underestimated" in result or "| C1 |" in result


# 11. Epistemic note present
def test_epistemic_note():
    d = {"company_event_log": [_churn("C3", "2020-06-30", 0.32, 0.0)]}
    result = _section_churn_prediction_calibration(d)
    assert "epistemic" in result.lower() or "simulation" in result.lower()


# 12. Summary line with counts
def test_summary_counts():
    d = {"company_event_log": [
        _churn("C1", "2020-01-01", 0.30, 0.0),   # underestimated
        _churn("C2", "2021-01-01", 0.50, 0.56),  # accurate (delta 6pp)
        _churn("C3", "2022-01-01", 0.30, 0.80),  # overestimated
    ]}
    result = _section_churn_prediction_calibration(d)
    assert "1 underestimated" in result
    assert "1 accurate" in result
    assert "1 overestimated" in result


def test_verdict_accurate_shown():
    d = {"company_event_log": [_churn("C1", "2020-03-01", 0.50, 0.55)]}
    result = _section_churn_prediction_calibration(d)
    assert "ACCURATE" in result


def test_mean_absolute_error_shown():
    d = {"company_event_log": [
        _churn("C1", "2020-03-01", 0.50, 0.20),
    ]}
    result = _section_churn_prediction_calibration(d)
    assert "Mean absolute error" in result


def test_only_churn_events_counted():
    d = {"company_event_log": [
        _acq("C1", "2020-01-01"),
    ]}
    result = _section_churn_prediction_calibration(d)
    assert result == ""
