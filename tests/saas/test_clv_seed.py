"""Tests for saas/clv_seed.py -- CLV seed accumulation from settlement records."""

from saas.clv_seed import build_clv_seed


def _record(cid, date, period, revenue, wholesale):
    return {
        "customer_id": cid,
        "settlement_date": date,
        "settlement_period": period,
        "revenue_gbp": revenue,
        "wholesale_cost_gbp": wholesale,
    }


def test_empty_input_returns_empty_dict():
    assert build_clv_seed([]) == {}


def test_single_record_creates_customer_entry():
    records = [_record("C1", "2024-01-01", 1, 50.0, 30.0)]
    result = build_clv_seed(records)
    assert "C1" in result


def test_single_record_running_total():
    records = [_record("C1", "2024-01-01", 1, 50.0, 30.0)]
    result = build_clv_seed(records)
    assert result["C1"]["running_total_gbp"] == 20.0


def test_single_record_periods_counted():
    records = [_record("C1", "2024-01-01", 1, 50.0, 30.0)]
    result = build_clv_seed(records)
    assert result["C1"]["periods_counted"] == 1


def test_multiple_records_same_customer_accumulates():
    records = [
        _record("C1", "2024-01-01", 1, 50.0, 30.0),
        _record("C1", "2024-01-01", 2, 60.0, 35.0),
    ]
    result = build_clv_seed(records)
    assert result["C1"]["running_total_gbp"] == 45.0
    assert result["C1"]["periods_counted"] == 2


def test_two_customers_independent():
    records = [
        _record("C1", "2024-01-01", 1, 50.0, 30.0),
        _record("C2", "2024-01-01", 1, 80.0, 50.0),
    ]
    result = build_clv_seed(records)
    assert result["C1"]["running_total_gbp"] == 20.0
    assert result["C2"]["running_total_gbp"] == 30.0


def test_history_appended_per_period():
    records = [
        _record("C1", "2024-01-01", 1, 50.0, 30.0),
        _record("C1", "2024-01-01", 2, 60.0, 35.0),
    ]
    result = build_clv_seed(records)
    assert len(result["C1"]["history"]) == 2


def test_history_running_total_in_last_entry():
    records = [
        _record("C1", "2024-01-01", 1, 50.0, 30.0),
        _record("C1", "2024-01-01", 2, 60.0, 35.0),
    ]
    result = build_clv_seed(records)
    last = result["C1"]["history"][-1]
    assert last["running_total_gbp"] == 45.0


def test_records_sorted_by_date_and_period():
    records = [
        _record("C1", "2024-01-01", 2, 60.0, 35.0),
        _record("C1", "2024-01-01", 1, 50.0, 30.0),
    ]
    result = build_clv_seed(records)
    dates = [h["settlement_period"] for h in result["C1"]["history"]]
    assert dates == sorted(dates)


def test_negative_margin_subtracts():
    records = [
        _record("C1", "2024-01-01", 1, 50.0, 30.0),
        _record("C1", "2024-01-01", 2, 20.0, 40.0),
    ]
    result = build_clv_seed(records)
    assert result["C1"]["running_total_gbp"] == 0.0
