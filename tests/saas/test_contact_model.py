import pytest

from saas.contact_model import (
    BASE_CONTACT_PROBABILITY,
    BILL_SHOCK_CONTACT_PENALTY,
    LOW_CLARITY_CONTACT_PENALTY,
    UNRESOLVED_AFTER_14_DAYS_RATE,
    build_contact_model,
    complaint_probability,
    contact_probability,
    service_quality_score,
)


def test_contact_probability_clear_bill_no_shock_is_base():
    assert contact_probability(1.0, None) == pytest.approx(BASE_CONTACT_PROBABILITY)


def test_contact_probability_low_clarity_raises_probability():
    clear = contact_probability(1.0)
    confusing = contact_probability(0.0)
    assert confusing == pytest.approx(BASE_CONTACT_PROBABILITY + LOW_CLARITY_CONTACT_PENALTY)
    assert confusing > clear


def test_contact_probability_bill_shock_raises_probability():
    no_shock = contact_probability(1.0, 0.0)
    shocked = contact_probability(1.0, 0.5)
    assert shocked == pytest.approx(BASE_CONTACT_PROBABILITY + 0.5 * BILL_SHOCK_CONTACT_PENALTY)
    assert shocked > no_shock


def test_contact_probability_bill_shock_capped_at_one():
    capped = contact_probability(1.0, 1.0)
    over = contact_probability(1.0, 3.0)
    assert over == pytest.approx(capped)


def test_contact_probability_never_exceeds_one():
    worst_case = BASE_CONTACT_PROBABILITY + LOW_CLARITY_CONTACT_PENALTY + BILL_SHOCK_CONTACT_PENALTY
    assert worst_case <= 1.0
    assert contact_probability(0.0, 5.0) == pytest.approx(worst_case)


def test_complaint_probability_scales_contact_probability():
    cp = 0.4
    assert complaint_probability(cp) == pytest.approx(cp * UNRESOLVED_AFTER_14_DAYS_RATE)


def test_service_quality_score_no_complaints_is_perfect():
    assert service_quality_score(0.0) == pytest.approx(1.0)


def test_service_quality_score_decreases_with_complaint_rate():
    low = service_quality_score(0.05)
    high = service_quality_score(0.2)
    assert high < low < 1.0


def test_service_quality_score_floored_at_zero():
    assert service_quality_score(1.0) == pytest.approx(0.0)


def test_build_contact_model_per_customer_records():
    bills = [
        {"customer_id": "C1", "period_end": "2023-01-31", "clarity_score": 1.0, "bill_shock_pct": None},
        {"customer_id": "C1", "period_end": "2023-02-28", "clarity_score": 0.5, "bill_shock_pct": 0.2},
    ]
    result = build_contact_model(bills)

    records = result["by_customer"]["C1"]
    assert [r["period_end"] for r in records] == ["2023-01-31", "2023-02-28"]
    assert records[0]["contact_probability"] == pytest.approx(contact_probability(1.0, None))
    assert records[1]["contact_probability"] == pytest.approx(contact_probability(0.5, 0.2))
    assert records[0]["complaint_probability"] == pytest.approx(
        complaint_probability(records[0]["contact_probability"])
    )


def test_build_contact_model_portfolio_summary():
    bills = [
        {"customer_id": "C1", "period_end": "2023-01-31", "clarity_score": 1.0, "bill_shock_pct": None},
        {"customer_id": "C2", "period_end": "2023-01-31", "clarity_score": 0.2, "bill_shock_pct": 0.8},
    ]
    result = build_contact_model(bills)

    expected_avg = (
        complaint_probability(contact_probability(1.0, None))
        + complaint_probability(contact_probability(0.2, 0.8))
    ) / 2
    assert result["portfolio"]["avg_complaint_probability"] == pytest.approx(expected_avg)
    assert result["portfolio"]["service_quality_score"] == pytest.approx(service_quality_score(expected_avg))


def test_build_contact_model_empty_bills():
    result = build_contact_model([])
    assert result["by_customer"] == {}
    assert result["portfolio"]["avg_complaint_probability"] == pytest.approx(0.0)
    assert result["portfolio"]["service_quality_score"] == pytest.approx(1.0)


from saas.contact_model import (
    BASE_CONTACT_PROBABILITY,
    LOW_CLARITY_CONTACT_PENALTY,
    BILL_SHOCK_CONTACT_PENALTY,
    COMPLAINT_ESCALATION_DAYS,
    MIN_SERVICE_QUALITY_SCORE,
    MAX_SERVICE_QUALITY_SCORE,
    complaint_probability,
    service_quality_score,
)


def test_base_contact_probability():
    assert BASE_CONTACT_PROBABILITY == pytest.approx(0.05)


def test_low_clarity_penalty():
    assert LOW_CLARITY_CONTACT_PENALTY == pytest.approx(0.3)


def test_bill_shock_penalty():
    assert BILL_SHOCK_CONTACT_PENALTY == pytest.approx(0.5)


def test_complaint_escalation_days():
    assert COMPLAINT_ESCALATION_DAYS == 14


def test_min_service_quality_zero():
    assert MIN_SERVICE_QUALITY_SCORE == pytest.approx(0.0)


def test_max_service_quality_one():
    assert MAX_SERVICE_QUALITY_SCORE == pytest.approx(1.0)


def test_complaint_probability_zero_contact():
    assert complaint_probability(0.0) == pytest.approx(0.0)


def test_service_quality_no_complaints_is_perfect():
    assert service_quality_score(0.0) == pytest.approx(1.0)


def test_service_quality_all_complaints_floored():
    result = service_quality_score(1.0)
    assert result >= MIN_SERVICE_QUALITY_SCORE


def test_contact_prob_clear_bill_no_shock_is_base():
    assert contact_probability(1.0, None) == pytest.approx(BASE_CONTACT_PROBABILITY)
