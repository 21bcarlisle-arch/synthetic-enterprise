"""Phase BV: Retention Decision Economics section tests."""
import pytest
from saas.reporting.annual_report import _section_retention_decision_economics


def _entry(cid, date, cost, margin, disc=0.08, outcome="retained"):
    return {
        "customer_id": cid,
        "event_date": date,
        "retention_cost_gbp": cost,
        "expected_term_margin_gbp": margin,
        "discount_pct": disc,
        "outcome": outcome,
    }


# 1. Empty returns empty
def test_empty_returns_empty():
    assert _section_retention_decision_economics({}) == ""
    assert _section_retention_decision_economics({"retention_log": []}) == ""


# 2. Header present
def test_header_present():
    d = {"retention_log": [_entry("C_IC1", "2018-01-31", 24333, 164194)]}
    assert "Retention Decision Economics" in _section_retention_decision_economics(d)


# 3. Customer ID in row
def test_customer_id():
    d = {"retention_log": [_entry("C_IC1", "2018-01-31", 24333, 164194)]}
    assert "C_IC1" in _section_retention_decision_economics(d)


# 4. ROI computed (164194/24333 ≈ 6.7×)
def test_roi_computed():
    d = {"retention_log": [_entry("C_IC1", "2018-01-31", 24333, 164194)]}
    result = _section_retention_decision_economics(d)
    assert "6.7×" in result


# 5. Total spend correct
def test_total_spend():
    d = {"retention_log": [
        _entry("C1", "2018-01-31", 10000, 50000),
        _entry("C2", "2019-01-31", 5000, 30000),
    ]}
    result = _section_retention_decision_economics(d)
    assert "£15,000" in result  # total cost


# 6. Total margin protected correct
def test_total_margin():
    d = {"retention_log": [
        _entry("C1", "2018-01-31", 10000, 50000),
        _entry("C2", "2019-01-31", 5000, 30000),
    ]}
    result = _section_retention_decision_economics(d)
    assert "£80,000" in result  # total margin


# 7. Portfolio ROI shown
def test_portfolio_roi():
    d = {"retention_log": [_entry("C1", "2018-01-31", 10000, 50000)]}
    result = _section_retention_decision_economics(d)
    assert "Portfolio retention ROI: 5.0×" in result


# 8. Best ROI flagged
def test_best_roi_flagged():
    d = {"retention_log": [
        _entry("C1", "2018-01-31", 10000, 50000),  # ROI 5×
        _entry("C2", "2019-01-31", 5000, 100000),  # ROI 20×
    ]}
    result = _section_retention_decision_economics(d)
    assert "Best ROI intervention: C2" in result


# 9. Retained count correct
def test_retained_count():
    d = {"retention_log": [
        _entry("C1", "2018-01-31", 10000, 50000, outcome="retained"),
        _entry("C2", "2019-01-31", 5000, 30000, outcome="churned"),
    ]}
    result = _section_retention_decision_economics(d)
    assert "Retained: 1/2" in result


# 10. Discount % shown
def test_discount_pct_shown():
    d = {"retention_log": [_entry("C1", "2018-01-31", 10000, 50000, disc=0.08)]}
    result = _section_retention_decision_economics(d)
    assert "8%" in result


# 11. ROI note present
def test_roi_note():
    d = {"retention_log": [_entry("C1", "2018-01-31", 10000, 50000)]}
    result = _section_retention_decision_economics(d)
    assert "ROI = expected" in result or "retention cost" in result


# 12. Period shown (YYYY-MM format)
def test_period_shown():
    d = {"retention_log": [_entry("C1", "2018-01-31", 10000, 50000)]}
    result = _section_retention_decision_economics(d)
    assert "2018-01" in result


# 13. Portfolio ROI shown
def test_portfolio_roi_shown():
    rl = [{"customer_id": "C1", "event_date": "2022-03-01", "retention_cost_gbp": 500.0,
            "expected_term_margin_gbp": 2000.0, "discount_pct": 0.05, "outcome": "retained"}]
    d = {"retention_log": rl}
    result = _section_retention_decision_economics(d)
    assert "Portfolio retention ROI" in result


# 14. Total cost and margin shown
def test_total_cost_margin_shown():
    rl = [{"customer_id": "C1", "event_date": "2022-01-01", "retention_cost_gbp": 300.0,
            "expected_term_margin_gbp": 1500.0, "discount_pct": 0.05, "outcome": "retained"},
           {"customer_id": "C2", "event_date": "2022-06-01", "retention_cost_gbp": 200.0,
            "expected_term_margin_gbp": 800.0, "discount_pct": 0.05, "outcome": "churned"}]
    d = {"retention_log": rl}
    result = _section_retention_decision_economics(d)
    assert "Total retention spend" in result
    assert "500" in result


# 15. Churned outcome shown in table
def test_churned_outcome_shown():
    rl = [{"customer_id": "C1", "event_date": "2022-01-01", "retention_cost_gbp": 200.0,
            "expected_term_margin_gbp": 800.0, "discount_pct": 0.05, "outcome": "churned"}]
    d = {"retention_log": rl}
    result = _section_retention_decision_economics(d)
    assert "churned" in result
