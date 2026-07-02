"""Phase ND: SIM-side bill shock tracker -> enriched company churn estimate.

Tests simulation/bill_shock_tracker.count_rate_shocks() which computes
cumulative unit-rate shock count from all_records for a given customer.
This feeds bill_shock_count into enriched_churn_estimate in run_phase2b.py.

All data used is observable: the company set the rates and issued the bills.
"""
import pytest
from simulation.bill_shock_tracker import BILL_SHOCK_THRESHOLD, count_rate_shocks


def _rec(cid, commodity, term_start, rate):
    return {
        "customer_id": cid,
        "commodity": commodity,
        "term_start": term_start,
        "unit_rate_gbp_per_mwh": rate,
    }


def test_empty_records_returns_zero():
    assert count_rate_shocks("C1", "electricity", []) == 0


def test_single_record_returns_zero():
    records = [_rec("C1", "electricity", "2020-01-01", 80.0)]
    assert count_rate_shocks("C1", "electricity", records) == 0


def test_small_increase_no_shock():
    records = [
        _rec("C1", "electricity", "2020-01-01", 80.0),
        _rec("C1", "electricity", "2021-01-01", 90.0),
    ]
    assert count_rate_shocks("C1", "electricity", records) == 0


def test_large_increase_counts_one():
    records = [
        _rec("C1", "electricity", "2020-01-01", 80.0),
        _rec("C1", "electricity", "2021-01-01", 120.0),
    ]
    assert count_rate_shocks("C1", "electricity", records) == 1


def test_exact_threshold_not_counted():
    records = [
        _rec("C1", "electricity", "2020-01-01", 100.0),
        _rec("C1", "electricity", "2021-01-01", 120.0),
    ]
    assert count_rate_shocks("C1", "electricity", records) == 0


def test_just_above_threshold_counted():
    records = [
        _rec("C1", "electricity", "2020-01-01", 100.0),
        _rec("C1", "electricity", "2021-01-01", 120.01),
    ]
    assert count_rate_shocks("C1", "electricity", records) == 1


def test_multiple_shocks_cumulate():
    records = [
        _rec("C1", "electricity", "2019-01-01", 50.0),
        _rec("C1", "electricity", "2020-01-01", 65.0),
        _rec("C1", "electricity", "2021-01-01", 100.0),
        _rec("C1", "electricity", "2022-01-01", 130.0),
    ]
    assert count_rate_shocks("C1", "electricity", records) == 3


def test_rate_decrease_no_shock():
    records = [
        _rec("C1", "electricity", "2020-01-01", 120.0),
        _rec("C1", "electricity", "2021-01-01", 80.0),
    ]
    assert count_rate_shocks("C1", "electricity", records) == 0


def test_different_customers_isolated():
    records = [
        _rec("C1", "electricity", "2020-01-01", 80.0),
        _rec("C1", "electricity", "2021-01-01", 120.0),
        _rec("C2", "electricity", "2020-01-01", 80.0),
        _rec("C2", "electricity", "2021-01-01", 85.0),
    ]
    assert count_rate_shocks("C1", "electricity", records) == 1
    assert count_rate_shocks("C2", "electricity", records) == 0


def test_commodity_filter():
    records = [
        _rec("C1", "electricity", "2020-01-01", 80.0),
        _rec("C1", "electricity", "2021-01-01", 120.0),
        _rec("C1", "gas", "2020-01-01", 30.0),
        _rec("C1", "gas", "2021-01-01", 35.0),
    ]
    assert count_rate_shocks("C1", "electricity", records) == 1
    assert count_rate_shocks("C1", "gas", records) == 0


def test_none_unit_rate_records_ignored():
    records = [
        {"customer_id": "C1", "commodity": "electricity", "term_start": "2020-01-01",
         "unit_rate_gbp_per_mwh": None},
        _rec("C1", "electricity", "2021-01-01", 120.0),
    ]
    assert count_rate_shocks("C1", "electricity", records) == 0


def test_unsorted_records_sorted_by_term_start():
    records = [
        _rec("C1", "electricity", "2021-01-01", 120.0),
        _rec("C1", "electricity", "2020-01-01", 80.0),
    ]
    assert count_rate_shocks("C1", "electricity", records) == 1


def test_custom_threshold():
    records = [
        _rec("C1", "electricity", "2020-01-01", 100.0),
        _rec("C1", "electricity", "2021-01-01", 115.0),
    ]
    assert count_rate_shocks("C1", "electricity", records, shock_threshold=0.10) == 1
    assert count_rate_shocks("C1", "electricity", records, shock_threshold=0.20) == 0


def test_zero_prev_rate_does_not_crash():
    records = [
        _rec("C1", "electricity", "2020-01-01", 0.0),
        _rec("C1", "electricity", "2021-01-01", 80.0),
    ]
    assert count_rate_shocks("C1", "electricity", records) == 0


def test_bill_shock_threshold_constant_is_020():
    assert BILL_SHOCK_THRESHOLD == 0.20


def test_crisis_years_generate_multiple_shocks():
    records = [
        _rec("C1", "electricity", "2019-01-01", 80.0),
        _rec("C1", "electricity", "2020-01-01", 82.0),
        _rec("C1", "electricity", "2021-01-01", 120.0),
        _rec("C1", "electricity", "2022-01-01", 200.0),
        _rec("C1", "electricity", "2023-01-01", 150.0),
    ]
    assert count_rate_shocks("C1", "electricity", records) == 2
