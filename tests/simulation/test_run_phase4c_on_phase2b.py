import pytest

from simulation.run_phase4c_on_phase2b import build_monthly_bills


def make_record(customer_id, settlement_date, kwh, unit_rate=200.0):
    return {
        "customer_id": customer_id,
        "settlement_date": settlement_date,
        "settlement_period": 1,
        "consumption_kwh": kwh,
        "unit_rate_gbp_per_mwh": unit_rate,
        "revenue_gbp": (kwh / 1000) * unit_rate,
        "wholesale_cost_gbp": 0.0,
        "margin_gbp": 0.0,
    }


def test_build_monthly_bills_groups_by_customer_and_month():
    records = [
        make_record("C1", "2023-01-15", 10.0),
        make_record("C1", "2023-01-16", 10.0),
        make_record("C1", "2023-02-01", 10.0),
        make_record("C2", "2023-01-10", 5.0),
    ]
    bills = build_monthly_bills(records)

    c1_bills = [b for b in bills if b["customer_id"] == "C1"]
    c2_bills = [b for b in bills if b["customer_id"] == "C2"]
    assert [b["period_start"] for b in c1_bills] == ["2023-01-15", "2023-02-01"]
    assert len(c2_bills) == 1


def test_build_monthly_bills_carries_previous_bill_total_for_shock():
    records = [
        make_record("C1", "2023-01-01", 10.0),   # small bill
        make_record("C1", "2023-02-01", 100.0),  # 10× jump — big shock
    ]
    bills = build_monthly_bills(records)

    assert bills[0]["bill_shock_pct"] is None  # first bill, no prior total
    # bill_shock_pct = |feb_total - jan_total| / jan_total (both totals include non-commodity + VAT)
    jan_total = bills[0]["total_amount_gbp"]
    feb_total = bills[1]["total_amount_gbp"]
    assert bills[1]["bill_shock_pct"] == pytest.approx((feb_total - jan_total) / jan_total)
    assert bills[1]["clarity_score"] < bills[0]["clarity_score"]


def test_build_monthly_bills_uses_customer_contract_type():
    records = [make_record("C1", "2023-01-01", 10.0)]
    bills = build_monthly_bills(records)
    # C1 is fixed_1yr -> base clarity 1.0, single steady day -> clarity 1.0
    assert bills[0]["clarity_score"] == pytest.approx(1.0)


from simulation.run_phase4c_on_phase2b import _billing_month


def test_billing_month_standard():
    assert _billing_month("2022-01-15") == "2022-01"


def test_billing_month_december():
    assert _billing_month("2022-12-31") == "2022-12"


def test_build_monthly_bills_empty():
    assert build_monthly_bills([]) == []


def test_build_monthly_bills_bill_keys_present():
    records = [make_record("C1", "2023-01-01", 10.0)]
    bills = build_monthly_bills(records)
    bill = bills[0]
    for key in ("customer_id", "period_start", "total_amount_gbp", "clarity_score", "bill_shock_pct"):
        assert key in bill, f"missing key: {key}"


def test_build_monthly_bills_chronological_order():
    records = [
        make_record("C1", "2023-02-15", 10.0),
        make_record("C1", "2023-01-01", 10.0),
    ]
    bills = build_monthly_bills(records)
    c1_bills = [b for b in bills if b["customer_id"] == "C1"]
    starts = [b["period_start"] for b in c1_bills]
    assert starts == sorted(starts)


def test_build_monthly_bills_total_is_positive():
    records = [make_record("C1", "2023-01-01", 50.0, unit_rate=200.0)]
    bills = build_monthly_bills(records)
    assert bills[0]["total_amount_gbp"] > 0.0


def test_billing_month_february_leap():
    assert _billing_month("2020-02-29") == "2020-02"


def test_build_monthly_bills_clarity_score_in_range():
    records = [make_record("C1", "2023-06-01", 50.0)]
    bills = build_monthly_bills(records)
    score = bills[0]["clarity_score"]
    assert 0.0 <= score <= 1.0


def test_build_monthly_bills_multi_customer_total_revenue():
    records = [
        make_record("C1", "2023-01-01", 10.0, unit_rate=100.0),
        make_record("C2", "2023-01-01", 20.0, unit_rate=100.0),
        make_record("C1", "2023-01-02", 5.0, unit_rate=100.0),
    ]
    bills = build_monthly_bills(records)
    total = sum(b["total_amount_gbp"] for b in bills)
    # Revenue: (10+5)/1000*100 + 20/1000*100 = 1.5 + 2.0 = 3.5 (before VAT/SC)
    assert total > 0.0
    c1_bills = [b for b in bills if b["customer_id"] == "C1"]
    c2_bills = [b for b in bills if b["customer_id"] == "C2"]
    assert len(c1_bills) == 1  # both C1 dates same month
    assert len(c2_bills) == 1


def test_billing_month_new_year():
    assert _billing_month("2022-01-01") == "2022-01"


def test_build_monthly_bills_total_exceeds_raw_revenue():
    records = [make_record("C1", "2023-01-01", 10.0, unit_rate=200.0)]
    bills = build_monthly_bills(records)
    raw_revenue = (10.0 / 1000) * 200.0
    assert bills[0]["total_amount_gbp"] > raw_revenue


def test_build_monthly_bills_clarity_score_not_none():
    records = [make_record("C1", "2023-03-01", 25.0)]
    bills = build_monthly_bills(records)
    assert bills[0]["clarity_score"] is not None
    assert isinstance(bills[0]["clarity_score"], float)
