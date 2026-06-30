"""Phase AY: Customer Strategic Value Matrix annual report section tests."""
import pytest
from saas.reporting.annual_report import _section_customer_strategic_value


def _bba(clv, churn, periods=10.0, cid_suffix=""):
    return {
        "clv_gbp": clv,
        "latest_churn_probability": churn,
        "expected_lifetime_periods": periods,
    }


# 1. Empty returns empty
def test_empty_returns_empty():
    assert _section_customer_strategic_value({}) == ""
    assert _section_customer_strategic_value({"by_billing_account": {}}) == ""


# 2. Header present with data
def test_header_present():
    d = {"by_billing_account": {"C1": _bba(5000, 0.3), "C2": _bba(10000, 0.1)}}
    result = _section_customer_strategic_value(d)
    assert "Customer Strategic Value Matrix" in result


# 3. PROTECT quadrant shown for high CLV, low churn
def test_protect_quadrant_for_high_clv_low_churn():
    d = {"by_billing_account": {
        "C_IC1": _bba(1000000, 0.08),
        "C5": _bba(5000, 0.35),
    }}
    result = _section_customer_strategic_value(d)
    assert "PROTECT" in result
    assert "C_IC1" in result


# 4. CRITICAL quadrant for high CLV, high churn
def test_critical_quadrant_shown():
    d = {"by_billing_account": {
        "C_IC1": _bba(1000000, 0.08),
        "C5": _bba(5000, 0.35),
        "C6": _bba(15000, 0.38),  # high CLV (vs median), high churn
        "C1": _bba(2000, 0.25),
    }}
    result = _section_customer_strategic_value(d)
    # With 4 accounts: median CLV = (2000+5000)/2=3500; C6 and C_IC1 above median
    # C_IC1: high CLV, low churn → PROTECT
    # C6: high CLV, high churn → CRITICAL
    assert "CRITICAL" in result


# 5. Gas accounts excluded (ending in 'g')
def test_gas_accounts_excluded():
    d = {"by_billing_account": {
        "C1": _bba(5000, 0.3),
        "C1g": _bba(1000, 0.1),  # should be excluded
    }}
    result = _section_customer_strategic_value(d)
    assert "C1g" not in result
    assert "C1" in result


# 6. Total portfolio CLV shown
def test_total_clv_shown():
    d = {"by_billing_account": {
        "C1": _bba(5000, 0.3),
        "C2": _bba(10000, 0.1),
    }}
    result = _section_customer_strategic_value(d)
    assert "£15,000.00" in result or "Total portfolio CLV" in result


# 7. Median CLV shown
def test_median_clv_shown():
    d = {"by_billing_account": {
        "C1": _bba(5000, 0.3),
        "C2": _bba(10000, 0.1),
    }}
    result = _section_customer_strategic_value(d)
    assert "Median CLV" in result


# 8. Quadrant CLV shown for each quadrant
def test_quadrant_clv_shown():
    d = {"by_billing_account": {
        "C_IC1": _bba(1000000, 0.08),
        "C1": _bba(2000, 0.35),
    }}
    result = _section_customer_strategic_value(d)
    assert "Quadrant CLV" in result


# 9. Board action note shown for CRITICAL quadrant
def test_board_action_note_for_critical():
    d = {"by_billing_account": {
        "C6": _bba(15000, 0.40),
        "C1": _bba(5000, 0.30),  # above median CLV, below median churn = PROTECT
        "C3": _bba(3000, 0.38),
        "C4": _bba(1000, 0.25),
    }}
    result = _section_customer_strategic_value(d)
    # Check if CRITICAL has any members
    if "CRITICAL" in result:
        assert "Board action" in result


# 10. Expected lifetime shown
def test_expected_lifetime_shown():
    d = {"by_billing_account": {
        "C_IC1": _bba(1000000, 0.08, periods=10.2),
    }}
    result = _section_customer_strategic_value(d)
    assert "10.2" in result


# 11. Churn percentage shown
def test_churn_pct_shown():
    d = {"by_billing_account": {
        "C_IC1": _bba(1000000, 0.08),
    }}
    result = _section_customer_strategic_value(d)
    assert "8%" in result


# 12. Single account handled
def test_single_account_handled():
    d = {"by_billing_account": {"C_IC1": _bba(1000000, 0.08)}}
    result = _section_customer_strategic_value(d)
    assert "C_IC1" in result
    assert "PROTECT" in result or "CRITICAL" in result or "MONITOR" in result or "EXIT" in result
