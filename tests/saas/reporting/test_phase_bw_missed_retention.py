"""Phase BW: Missed Retention Opportunity Analysis section tests."""
import pytest
from saas.reporting.annual_report import _section_missed_retention_analysis


def _no_offer(cid, date, churn_est, margin, reason="below_threshold"):
    return {
        "customer_id": cid,
        "event_date": date,
        "company_churn_estimate": churn_est,
        "expected_term_margin_gbp": margin,
        "no_offer_reason": reason,
    }


def _gas_churn(cid, term_start, old_r, new_r, churn_est):
    return {
        "customer_id": cid,
        "term_start": term_start,
        "old_gas_rate": old_r,
        "new_gas_rate": new_r,
        "company_gas_churn_estimate": churn_est,
    }


# 1. Empty returns empty
def test_empty_returns_empty():
    assert _section_missed_retention_analysis({}) == ""
    assert _section_missed_retention_analysis({"no_offer_churn_log": [], "company_gas_churn_log": []}) == ""


# 2. Header present with no-offer data
def test_header_present():
    d = {"no_offer_churn_log": [_no_offer("C6", "2024-03-30", 0.25, 2852)], "company_gas_churn_log": []}
    assert "Missed Retention" in _section_missed_retention_analysis(d)


# 3. Customer in no-offer table
def test_customer_in_table():
    d = {"no_offer_churn_log": [_no_offer("C6", "2024-03-30", 0.25, 2852)], "company_gas_churn_log": []}
    assert "C6" in _section_missed_retention_analysis(d)


# 4. High-risk count (churn_est >= 10%) flagged
def test_high_risk_count():
    d = {"no_offer_churn_log": [
        _no_offer("C6", "2024-03-30", 0.25, 2852),
        _no_offer("C3", "2020-06-30", 0.00, 585),
    ], "company_gas_churn_log": []}
    result = _section_missed_retention_analysis(d)
    assert "High-risk no-offer events (≥10% churn): 1" in result


# 5. Margin at risk summed
def test_margin_at_risk():
    d = {"no_offer_churn_log": [
        _no_offer("C6", "2024-03-30", 0.15, 1000),
        _no_offer("C5", "2023-01-01", 0.20, 2000),
    ], "company_gas_churn_log": []}
    result = _section_missed_retention_analysis(d)
    assert "£3,000" in result


# 6. Gas churn section present when gas data exists
def test_gas_churn_section():
    d = {"no_offer_churn_log": [], "company_gas_churn_log": [_gas_churn("C1g", "2017-01-01", 24.34, 26.25, 0.20)]}
    result = _section_missed_retention_analysis(d)
    assert "Gas Renewal" in result


# 7. High-risk gas reprices flagged (>= 15%)
def test_high_risk_gas():
    d = {"no_offer_churn_log": [], "company_gas_churn_log": [
        _gas_churn("C1g", "2017-01-01", 24.34, 26.25, 0.20),  # high
        _gas_churn("C2g", "2017-04-01", 26.92, 32.81, 0.05),  # low
    ]}
    result = _section_missed_retention_analysis(d)
    assert "High-risk gas reprices: 1" in result


# 8. Low-risk gas reprices not shown in table
def test_low_risk_gas_note():
    d = {"no_offer_churn_log": [], "company_gas_churn_log": [
        _gas_churn("C1g", "2017-01-01", 24.34, 26.25, 0.05),  # all below 15%
    ]}
    result = _section_missed_retention_analysis(d)
    assert "No high-risk gas reprices" in result


# 9. Churn estimate shown as percentage
def test_churn_pct_format():
    d = {"no_offer_churn_log": [_no_offer("C6", "2024-03-30", 0.2472, 2852)], "company_gas_churn_log": []}
    result = _section_missed_retention_analysis(d)
    assert "24.7%" in result


# 10. Reason shown in table
def test_reason_shown():
    d = {"no_offer_churn_log": [_no_offer("C6", "2024-03-30", 0.25, 2852, "below_threshold")],
         "company_gas_churn_log": []}
    result = _section_missed_retention_analysis(d)
    assert "below threshold" in result


# 11. Footnote present
def test_footnote():
    d = {"no_offer_churn_log": [_no_offer("C6", "2024-03-30", 0.25, 2852)], "company_gas_churn_log": []}
    result = _section_missed_retention_analysis(d)
    assert "15%" in result or "⚑" in result


# 12. Only gas data, no no-offer data
def test_gas_only():
    d = {"no_offer_churn_log": [], "company_gas_churn_log": [
        _gas_churn("C1g", "2017-01-01", 24.34, 26.25, 0.20),
    ]}
    result = _section_missed_retention_analysis(d)
    assert "Gas Renewal" in result
    assert len(result) > 50
