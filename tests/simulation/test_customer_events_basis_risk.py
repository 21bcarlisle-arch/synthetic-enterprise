"""Tests for Phase 11b: company churn estimate in roll_lifecycle_event output."""
import pytest
from datetime import date, timedelta
from simulation.settlement import CONTRACT_LENGTH_DAYS
from simulation.customer_events import roll_lifecycle_event


ACQ_DATE = "2016-01-01"
FIRST_RENEWAL = (
    date.fromisoformat(ACQ_DATE) + timedelta(days=CONTRACT_LENGTH_DAYS)
).isoformat()


def _make_customers(customer_id="C5", acquisition_date=ACQ_DATE):
    return [
        {
            "customer_id": customer_id,
            "commodity": "electricity",
            "segment": "resi",
            "epc_rating": "D",
            "acquisition_date": acquisition_date,
        }
    ]


def _build_one_year_records(customer_id="C5", start_year=2016):
    records = []
    for month in range(1, 13):
        for day in range(1, 29):
            records.append({
                "customer_id": customer_id,
                "settlement_date": f"{start_year}-{month:02d}-{day:02d}",
                "settlement_period": 1,
                "consumption_kwh": 50.0,
                "unit_rate_gbp_per_mwh": 150.0,
                "revenue_gbp": 7.5,
                "wholesale_cost_gbp": 5.0,
                "margin_gbp": 2.5,
                "capital_cost_gbp": 0.1,
                "net_margin_gbp": 2.4,
            })
    return records


def test_company_churn_estimate_absent_when_rates_not_passed():
    """When old/new rates are omitted, company_churn_estimate should be None."""
    customers = _make_customers()
    records = _build_one_year_records()
    result = roll_lifecycle_event("C5", FIRST_RENEWAL, "electricity", records, customers)
    assert result is not None
    assert result["company_churn_estimate"] is None
    assert result["churn_estimate_error_pct"] is None


def test_company_churn_estimate_present_when_rates_passed():
    """When old/new rates are provided, company_churn_estimate is a float in [0, 0.95]."""
    customers = _make_customers()
    records = _build_one_year_records()
    result = roll_lifecycle_event(
        "C5", FIRST_RENEWAL, "electricity", records, customers,
        old_rate_gbp_per_mwh=150.0,
        new_rate_gbp_per_mwh=165.0,
    )
    assert result is not None
    assert result["company_churn_estimate"] is not None
    assert 0.0 <= result["company_churn_estimate"] <= 0.95
    assert result["churn_estimate_error_pct"] is not None


def test_company_churn_estimate_differs_from_sim():
    """Company uses rate change %, SIM uses bill-shock count — they will differ."""
    customers = _make_customers()
    records = _build_one_year_records()
    # No bill shocks -> SIM says 5% churn. Company sees 10% rate rise -> higher estimate.
    result = roll_lifecycle_event(
        "C5", FIRST_RENEWAL, "electricity", records, customers,
        old_rate_gbp_per_mwh=100.0,
        new_rate_gbp_per_mwh=110.0,
    )
    assert result is not None
    sim_p = result["churn_probability"]
    co_p = result["company_churn_estimate"]
    # With 10% rate rise and 0 bill shocks (5% SIM), company estimates ~0.10+0.8*0.1 = 0.18
    assert co_p > sim_p


def test_churn_estimate_error_pct_correct():
    """churn_estimate_error_pct = (company_est - sim_est) / sim_est."""
    customers = _make_customers()
    records = _build_one_year_records()
    result = roll_lifecycle_event(
        "C5", FIRST_RENEWAL, "electricity", records, customers,
        old_rate_gbp_per_mwh=100.0,
        new_rate_gbp_per_mwh=100.0,  # no rate change
    )
    assert result is not None
    sim_p = result["churn_probability"]
    co_p = result["company_churn_estimate"]
    expected_error = (co_p - sim_p) / sim_p
    assert abs(result["churn_estimate_error_pct"] - round(expected_error, 4)) < 1e-9


def test_company_estimate_is_rounded_to_4dp():
    """company_churn_estimate and error are rounded to 4 decimal places."""
    customers = _make_customers()
    records = _build_one_year_records()
    result = roll_lifecycle_event(
        "C5", FIRST_RENEWAL, "electricity", records, customers,
        old_rate_gbp_per_mwh=123.456,
        new_rate_gbp_per_mwh=134.567,
    )
    assert result is not None
    if result["company_churn_estimate"] is not None:
        # Value should equal its own round(x, 4)
        assert result["company_churn_estimate"] == round(result["company_churn_estimate"], 4)


def test_none_returned_when_no_renewal_data():
    """No renewal data -> still returns None (rate params have no effect)."""
    customers = _make_customers()
    records = _build_one_year_records("C5")[:5]  # too few records
    result = roll_lifecycle_event(
        "C5", FIRST_RENEWAL, "electricity", records, customers,
        old_rate_gbp_per_mwh=100.0,
        new_rate_gbp_per_mwh=120.0,
    )
    assert result is None
