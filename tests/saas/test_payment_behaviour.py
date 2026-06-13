import pytest

from saas.payment_behaviour import (
    CREDIT_RISK_BY_CUSTOMER,
    DEFAULT_PROBABILITY_BY_CREDIT_RISK,
    PAYMENT_TIMING_DAYS_BY_CREDIT_RISK,
    bad_debt_provision_gbp,
    build_payment_behaviour,
    expected_payment_date,
)


def test_bad_debt_provision_scales_with_credit_risk():
    low = bad_debt_provision_gbp("low", 100.0)
    vulnerable = bad_debt_provision_gbp("vulnerable", 100.0)
    assert low == pytest.approx(100.0 * DEFAULT_PROBABILITY_BY_CREDIT_RISK["low"])
    assert vulnerable == pytest.approx(100.0 * DEFAULT_PROBABILITY_BY_CREDIT_RISK["vulnerable"])
    assert vulnerable > low


def test_bad_debt_provision_unknown_segment_falls_back_to_medium():
    assert bad_debt_provision_gbp("unknown", 100.0) == pytest.approx(
        bad_debt_provision_gbp("medium", 100.0)
    )


def test_expected_payment_date_adds_segment_days():
    result = expected_payment_date("2023-01-31", "low")
    assert result == "2023-02-05"  # +5 days


def test_expected_payment_date_vulnerable_is_later_than_low():
    low_date = expected_payment_date("2023-01-31", "low")
    vulnerable_date = expected_payment_date("2023-01-31", "vulnerable")
    assert vulnerable_date > low_date


def test_build_payment_behaviour_attaches_credit_risk_per_customer():
    bills = [
        {"customer_id": "C1", "period_end": "2023-01-31", "total_amount_gbp": 50.0},
        {"customer_id": "C3", "period_end": "2023-01-31", "total_amount_gbp": 60.0},
    ]
    result = build_payment_behaviour(bills)

    assert result["C1"][0]["credit_risk"] == CREDIT_RISK_BY_CUSTOMER["C1"]
    assert result["C3"][0]["credit_risk"] == CREDIT_RISK_BY_CUSTOMER["C3"]
    assert result["C3"][0]["is_vulnerable"] is True
    assert result["C1"][0]["is_vulnerable"] is False


def test_build_payment_behaviour_unknown_customer_defaults_to_medium():
    bills = [{"customer_id": "CX", "period_end": "2023-01-31", "total_amount_gbp": 50.0}]
    result = build_payment_behaviour(bills)
    assert result["CX"][0]["credit_risk"] == "medium"


def test_build_payment_behaviour_preserves_bill_order_per_customer():
    bills = [
        {"customer_id": "C1", "period_end": "2023-01-31", "total_amount_gbp": 50.0},
        {"customer_id": "C1", "period_end": "2023-02-28", "total_amount_gbp": 60.0},
    ]
    result = build_payment_behaviour(bills)
    assert [r["period_end"] for r in result["C1"]] == ["2023-01-31", "2023-02-28"]


def test_build_payment_behaviour_includes_bad_debt_and_payment_date():
    bills = [{"customer_id": "C2", "period_end": "2023-01-31", "total_amount_gbp": 100.0}]
    result = build_payment_behaviour(bills)
    record = result["C2"][0]
    credit_risk = CREDIT_RISK_BY_CUSTOMER["C2"]
    assert record["bad_debt_provision_gbp"] == pytest.approx(
        100.0 * DEFAULT_PROBABILITY_BY_CREDIT_RISK[credit_risk]
    )
    assert record["expected_payment_date"] == expected_payment_date("2023-01-31", credit_risk)


def test_all_credit_risk_segments_have_probability_and_timing():
    for segment in CREDIT_RISK_BY_CUSTOMER.values():
        assert segment in DEFAULT_PROBABILITY_BY_CREDIT_RISK
        assert segment in PAYMENT_TIMING_DAYS_BY_CREDIT_RISK
