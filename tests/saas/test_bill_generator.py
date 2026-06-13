import pytest

from saas.bill_generator import (
    BILL_SHOCK_PENALTY_FACTOR,
    CONSUMPTION_CV_PENALTY_FACTOR,
    consumption_coefficient_of_variation,
    generate_bill,
)


def make_records(daily_kwh: dict[str, float], unit_rate_gbp_per_mwh: float = 200.0):
    records = []
    for settlement_date, kwh in daily_kwh.items():
        records.append({
            "customer_id": "C1",
            "settlement_date": settlement_date,
            "settlement_period": 1,
            "consumption_kwh": kwh,
            "unit_rate_gbp_per_mwh": unit_rate_gbp_per_mwh,
            "revenue_gbp": (kwh / 1000) * unit_rate_gbp_per_mwh,
            "wholesale_cost_gbp": 0.0,
            "margin_gbp": 0.0,
        })
    return records


def test_generate_bill_empty_raises():
    with pytest.raises(ValueError):
        generate_bill("C1", [], "fixed_1yr")


def test_generate_bill_totals_and_period():
    records = make_records({"2023-01-01": 10.0, "2023-01-02": 20.0})
    bill = generate_bill("C1", records, "fixed_1yr")

    assert bill["customer_id"] == "C1"
    assert bill["period_start"] == "2023-01-01"
    assert bill["period_end"] == "2023-01-02"
    assert bill["total_consumption_kwh"] == pytest.approx(30.0)
    assert bill["total_amount_gbp"] == pytest.approx((30.0 / 1000) * 200.0)
    assert bill["average_unit_rate_gbp_per_mwh"] == pytest.approx(200.0)


def test_steady_consumption_fixed_tariff_is_maximally_clear():
    records = make_records({"2023-01-01": 10.0, "2023-01-02": 10.0, "2023-01-03": 10.0})
    bill = generate_bill("C1", records, "fixed_1yr")
    assert bill["clarity_score"] == pytest.approx(1.0)
    assert bill["bill_shock_pct"] is None


def test_volatile_consumption_reduces_clarity():
    steady = make_records({"2023-01-01": 10.0, "2023-01-02": 10.0})
    volatile = make_records({"2023-01-01": 1.0, "2023-01-02": 19.0})

    bill_steady = generate_bill("C1", steady, "fixed_1yr")
    bill_volatile = generate_bill("C1", volatile, "fixed_1yr")

    assert bill_volatile["clarity_score"] < bill_steady["clarity_score"]


def test_unknown_contract_type_uses_default_base_clarity():
    records = make_records({"2023-01-01": 10.0, "2023-01-02": 10.0})
    bill = generate_bill("C1", records, "tou_smart")
    assert bill["clarity_score"] == pytest.approx(0.7)


def test_bill_shock_reduces_clarity_and_reports_pct():
    records = make_records({"2023-02-01": 10.0, "2023-02-02": 10.0})
    bill_no_shock = generate_bill("C1", records, "fixed_1yr", previous_bill_total_gbp=4.0)
    bill_with_shock = generate_bill("C1", records, "fixed_1yr", previous_bill_total_gbp=1.0)

    assert bill_no_shock["bill_shock_pct"] == pytest.approx(0.0)
    assert bill_with_shock["bill_shock_pct"] == pytest.approx(3.0)  # (4 - 1) / 1
    assert bill_with_shock["clarity_score"] < bill_no_shock["clarity_score"]
    # bill_shock_pct of 3.0 is capped at 1.0 for the penalty
    assert bill_with_shock["clarity_score"] == pytest.approx(
        bill_no_shock["clarity_score"] - 1.0 * BILL_SHOCK_PENALTY_FACTOR
    )


def test_clarity_score_floored_at_zero():
    volatile = make_records({"2023-01-01": 0.1, "2023-01-02": 100.0})
    bill = generate_bill("C1", volatile, "tou_smart", previous_bill_total_gbp=0.01)
    assert bill["clarity_score"] == pytest.approx(0.0)


def test_consumption_cv_single_day_is_zero():
    records = make_records({"2023-01-01": 10.0})
    assert consumption_coefficient_of_variation(records) == 0.0


def test_consumption_cv_matches_manual_calc():
    records = make_records({"2023-01-01": 5.0, "2023-01-02": 15.0})
    # mean=10, pstdev=5 -> cv=0.5
    assert consumption_coefficient_of_variation(records) == pytest.approx(0.5)
    bill = generate_bill("C1", records, "fixed_1yr")
    assert bill["clarity_score"] == pytest.approx(1.0 - 0.5 * CONSUMPTION_CV_PENALTY_FACTOR)
