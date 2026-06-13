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
        make_record("C1", "2023-01-01", 10.0),  # 10kWh @ 200/MWh = £2
        make_record("C1", "2023-02-01", 100.0),  # £20 -- big jump
    ]
    bills = build_monthly_bills(records)

    assert bills[0]["bill_shock_pct"] is None  # first bill, no prior total
    assert bills[1]["bill_shock_pct"] == pytest.approx((20.0 - 2.0) / 2.0)
    assert bills[1]["clarity_score"] < bills[0]["clarity_score"]


def test_build_monthly_bills_uses_customer_contract_type():
    records = [make_record("C1", "2023-01-01", 10.0)]
    bills = build_monthly_bills(records)
    # C1 is fixed_1yr -> base clarity 1.0, single steady day -> clarity 1.0
    assert bills[0]["clarity_score"] == pytest.approx(1.0)
