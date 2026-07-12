"""E3_accrual_restatement: Unbilled Revenue Accrual section tests."""
import pytest
from saas.reporting.annual_report import _section_unbilled_revenue_accrual


def _bill(customer_id="C1", period_start="2016-01-01", period_end="2016-01-31",
          total_amount_gbp=100.0, billing_basis="actual", **extra):
    bill = {
        "customer_id": customer_id,
        "period_start": period_start,
        "period_end": period_end,
        "total_amount_gbp": total_amount_gbp,
        "billing_basis": billing_basis,
    }
    bill.update(extra)
    return bill


def test_empty_bills_returns_empty():
    assert _section_unbilled_revenue_accrual({}) == ""
    assert _section_unbilled_revenue_accrual({"bills": []}) == ""


def test_header_present_with_bills():
    data = {"bills": [_bill()]}
    result = _section_unbilled_revenue_accrual(data)
    assert "Unbilled Revenue Accrual" in result


def test_outstanding_estimated_bill_shown():
    data = {"bills": [_bill(billing_basis="estimated", total_amount_gbp=150.0)]}
    result = _section_unbilled_revenue_accrual(data)
    assert "£150.00" in result
    assert "1 bill(s)" in result


def test_resolved_estimated_bill_not_outstanding():
    est = _bill(period_start="2016-01-01", period_end="2016-01-31",
                billing_basis="estimated", total_amount_gbp=150.0)
    resolving = _bill(period_start="2016-02-01", period_end="2016-02-29",
                       billing_basis="actual", catchup_applied=True,
                       catchup_period_start="2016-01-01", catchup_period_end="2016-01-31",
                       catchup_raw_delta_gbp=10.0)
    data = {"bills": [est, resolving]}
    result = _section_unbilled_revenue_accrual(data)
    assert "£0.00" in result


def test_restated_total_shown():
    resolving = _bill(catchup_applied=True, catchup_raw_delta_gbp=42.5)
    data = {"bills": [resolving]}
    result = _section_unbilled_revenue_accrual(data)
    assert "£42.50" in result
    assert "1 catch-up correction(s)" in result


def test_no_restatements_shows_zero():
    data = {"bills": [_bill()]}
    result = _section_unbilled_revenue_accrual(data)
    assert "£0.00" in result
    assert "0 catch-up correction(s)" in result


def test_per_customer_table_shown_when_outstanding():
    data = {"bills": [_bill(customer_id="C1", billing_basis="estimated", total_amount_gbp=99.0)]}
    result = _section_unbilled_revenue_accrual(data)
    assert "| C1 |" in result
    assert "£99.00" in result


def test_no_per_customer_table_when_nothing_outstanding():
    data = {"bills": [_bill()]}
    result = _section_unbilled_revenue_accrual(data)
    assert "| Customer |" not in result
