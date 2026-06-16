"""Tests for simulation/customer_events.py — Phase 6b lifecycle event rolling."""
import random as _random

from simulation.customer_events import PRICE_DIFFERENTIAL_PCT, roll_lifecycle_event


def _make_customers(customer_id="C5", segment="SME", epc="D", acquisition_date="2016-01-01"):
    return [
        {
            "customer_id": customer_id,
            "commodity": "electricity",
            "segment": segment,
            "epc_rating": epc,
            "acquisition_date": acquisition_date,
        }
    ]


def _make_settlement_records(customer_id="C5", year_month="2016-01", count=30):
    """Generate flat settlement records for bill-shock baseline (no shocks — flat bill)."""
    records = []
    for day in range(1, count + 1):
        date_str = f"{year_month}-{day:02d}"
        records.append({
            "customer_id": customer_id,
            "settlement_date": date_str,
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


def _build_one_year_records(customer_id="C5", start_year=2016):
    """One full year of flat settlement records (no bill shocks)."""
    records = []
    for month in range(1, 13):
        for day in range(1, 29):
            date_str = f"{start_year}-{month:02d}-{day:02d}"
            records.append({
                "customer_id": customer_id,
                "settlement_date": date_str,
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


def _first_renewal_date(acquisition_date: str) -> str:
    """Compute the first renewal date (acquisition + 365 days) as an ISO string.
    Note: 2016-01-01 + 365 = 2016-12-31 because 2016 is a leap year (366 days).
    """
    from datetime import date, timedelta
    from simulation.settlement import CONTRACT_LENGTH_DAYS
    return (date.fromisoformat(acquisition_date) + timedelta(days=CONTRACT_LENGTH_DAYS)).isoformat()


ACQ_DATE = "2016-01-01"
FIRST_RENEWAL = _first_renewal_date(ACQ_DATE)  # "2016-12-31"


def test_roll_returns_none_when_no_renewal_data_in_window():
    # Only a few days of records — churn model has no renewal point yet
    customers = _make_customers("C5", acquisition_date=ACQ_DATE)
    records = _make_settlement_records("C5", "2016-01", 10)  # only 10 days
    result = roll_lifecycle_event("C5", FIRST_RENEWAL, "electricity", records, customers)
    assert result is None


def test_roll_returns_event_dict_when_renewal_data_present():
    customers = _make_customers("C5", acquisition_date=ACQ_DATE)
    records = _build_one_year_records("C5", 2016)
    result = roll_lifecycle_event("C5", FIRST_RENEWAL, "electricity", records, customers)
    assert result is not None
    assert result["customer_id"] == "C5"
    assert result["event_date"] == FIRST_RENEWAL
    assert result["commodity"] == "electricity"
    assert result["event_type"] in ("renewed", "churned")
    assert 0.0 < result["churn_probability"] <= 1.0
    assert 0.0 < result["win_probability"] <= 1.0
    assert 0.0 < result["effective_retention_probability"] <= 1.0
    assert 0.0 <= result["random_roll"] <= 1.0


def test_roll_is_deterministic():
    """Same input always produces the same random roll and outcome."""
    customers = _make_customers("C5", acquisition_date=ACQ_DATE)
    records = _build_one_year_records("C5", 2016)
    result1 = roll_lifecycle_event("C5", FIRST_RENEWAL, "electricity", records, customers)
    result2 = roll_lifecycle_event("C5", FIRST_RENEWAL, "electricity", records, customers)
    assert result1 == result2


def test_different_customers_get_independent_rolls():
    """Different customer_ids produce different random rolls (seeded by id+date)."""
    customers_c5 = _make_customers("C5", acquisition_date=ACQ_DATE)
    customers_c6 = _make_customers("C6", acquisition_date=ACQ_DATE)
    records_c5 = _build_one_year_records("C5", 2016)
    records_c6 = _build_one_year_records("C6", 2016)
    result_c5 = roll_lifecycle_event("C5", FIRST_RENEWAL, "electricity", records_c5, customers_c5)
    result_c6 = roll_lifecycle_event("C6", FIRST_RENEWAL, "electricity", records_c6, customers_c6)
    assert result_c5 is not None and result_c6 is not None
    # Same date, different customer — rolls should differ (astronomically unlikely to collide)
    assert result_c5["random_roll"] != result_c6["random_roll"]


def test_retained_when_roll_below_retention_probability():
    """Roll outcome is consistent with the rolled probability."""
    customers = _make_customers("C5", acquisition_date=ACQ_DATE)
    records = _build_one_year_records("C5", 2016)

    result = roll_lifecycle_event("C5", FIRST_RENEWAL, "electricity", records, customers)
    assert result is not None
    p_retain = result["effective_retention_probability"]
    roll = result["random_roll"]
    expected = "renewed" if roll <= p_retain else "churned"
    assert result["event_type"] == expected


def test_no_bill_shocks_gives_base_churn_probability():
    """With no bill shocks, churn_probability == BASE_ANNUAL_CHURN_PROBABILITY (5%)."""
    from saas.churn_model import BASE_ANNUAL_CHURN_PROBABILITY

    customers = _make_customers("C5", acquisition_date=ACQ_DATE)
    records = _build_one_year_records("C5", 2016)
    result = roll_lifecycle_event("C5", FIRST_RENEWAL, "electricity", records, customers)
    assert result is not None
    assert abs(result["churn_probability"] - BASE_ANNUAL_CHURN_PROBABILITY) < 1e-9


def test_gas_leg_maps_to_billing_account():
    """Gas leg C1g rolls churn for billing account C1 (same seed as electricity leg)."""
    customers_elec = _make_customers("C1", segment="resi", epc="C", acquisition_date=ACQ_DATE)
    customers_gas = [
        {**customers_elec[0], "customer_id": "C1g", "commodity": "gas"}
    ]
    all_customers = customers_elec + customers_gas

    records = _build_one_year_records("C1", 2016)

    result_elec = roll_lifecycle_event("C1", FIRST_RENEWAL, "electricity", records, all_customers)
    result_gas = roll_lifecycle_event("C1g", FIRST_RENEWAL, "gas", records, all_customers)

    assert result_elec is not None and result_gas is not None
    # Both map to billing account C1 — same seed → same roll and outcome
    assert result_elec["random_roll"] == result_gas["random_roll"]
    assert result_elec["event_type"] == result_gas["event_type"]
    assert result_elec["customer_id"] == "C1"
    assert result_gas["customer_id"] == "C1"
