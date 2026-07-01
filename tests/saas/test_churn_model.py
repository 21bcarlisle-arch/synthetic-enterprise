import pytest

from saas.churn_model import (
    BASE_ANNUAL_CHURN_PROBABILITY,
    CHURN_UPLIFT_PER_BILL_SHOCK,
    MAX_CHURN_PROBABILITY,
    build_churn_risk,
    churn_probability,
    _shift_month,
    _renewal_periods,
)

CUSTOMERS = [
    {"customer_id": "C1", "acquisition_date": "2016-01-01"},
]


def _record(customer_id, settlement_date, revenue_gbp, wholesale_cost_gbp=80.0):
    return {
        "customer_id": customer_id,
        "settlement_date": settlement_date,
        "settlement_period": 1,
        "revenue_gbp": revenue_gbp,
        "wholesale_cost_gbp": wholesale_cost_gbp,
    }


def test_churn_probability_base_rate_with_no_shocks():
    assert churn_probability(0) == BASE_ANNUAL_CHURN_PROBABILITY


def test_churn_probability_increases_per_shock():
    assert churn_probability(1) == BASE_ANNUAL_CHURN_PROBABILITY + CHURN_UPLIFT_PER_BILL_SHOCK
    assert churn_probability(2) == BASE_ANNUAL_CHURN_PROBABILITY + 2 * CHURN_UPLIFT_PER_BILL_SHOCK


def test_churn_probability_capped():
    assert churn_probability(100) == MAX_CHURN_PROBABILITY


def test_empty_input_returns_empty_dict():
    assert build_churn_risk([], CUSTOMERS) == {}


def test_account_with_less_than_a_year_has_no_renewal_points():
    records = [_record("C1", f"2016-{month:02d}-15", 100.0) for month in range(1, 7)]
    result = build_churn_risk(records, CUSTOMERS)
    assert result["C1"] == []


def test_renewal_point_counts_bill_shocks_in_preceding_year():
    # Jan-Jun: flat £100/month, no prior history to compare against -> no shocks.
    # Jul: £200 spikes vs the £100 rolling avg -> bill_shock_triggered.
    # Aug-Dec: back to £100; rolling avg (last 6 incl. the £200) softens the
    # gap below the 0.15 threshold -> not triggered.
    revenues = {1: 100, 2: 100, 3: 100, 4: 100, 5: 100, 6: 100, 7: 200, 8: 100, 9: 100, 10: 100, 11: 100, 12: 100}
    records = [_record("C1", f"2016-{month:02d}-15", revenue) for month, revenue in revenues.items()]

    result = build_churn_risk(records, CUSTOMERS)

    assert len(result["C1"]) == 1
    renewal = result["C1"][0]
    assert renewal["renewal_period"] == "2016-12"
    assert renewal["bill_shock_count"] == 1
    assert renewal["churn_probability"] == BASE_ANNUAL_CHURN_PROBABILITY + CHURN_UPLIFT_PER_BILL_SHOCK


def test_unknown_account_raises_key_error():
    records = [_record("C99", "2016-01-15", 100.0)]
    try:
        build_churn_risk(records, CUSTOMERS)
        assert False, "expected KeyError"
    except KeyError:
        pass


def test_constants_values():
    assert BASE_ANNUAL_CHURN_PROBABILITY == pytest.approx(0.05)
    assert CHURN_UPLIFT_PER_BILL_SHOCK == pytest.approx(0.03)
    assert MAX_CHURN_PROBABILITY == pytest.approx(0.95)


def test_shift_month_forward():
    assert _shift_month("2022-06", 6) == "2022-12"


def test_shift_month_crosses_year():
    assert _shift_month("2022-12", 1) == "2023-01"


def test_shift_month_backward():
    assert _shift_month("2023-01", -1) == "2022-12"


def test_shift_month_twelve_months():
    assert _shift_month("2022-01", 12) == "2023-01"


def test_renewal_periods_one_year():
    periods = _renewal_periods("2022-01-01", "2023-01")
    assert periods == ["2023-01"]


def test_renewal_periods_too_short():
    periods = _renewal_periods("2022-01-01", "2022-11")
    assert periods == []


def test_renewal_periods_three_points():
    periods = _renewal_periods("2022-01-01", "2024-12")
    assert periods == ["2023-01", "2024-01", "2024-12"]


def test_churn_probability_specific_value():
    assert churn_probability(3) == pytest.approx(0.05 + 3 * 0.03)
