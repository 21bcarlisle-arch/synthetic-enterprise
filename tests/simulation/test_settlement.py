"""Tests for simulation/settlement.py -- Phase 0b settlement orchestration."""

import pytest

from simulation.settlement import CONTRACT_LENGTH_DAYS, run_settlement


def _flat_shape(kwh_per_period: float = 1.0):
    def shape_fn(date_str: str) -> list[float]:
        return [kwh_per_period] * 48
    return shape_fn


def _price_records(date_str: str, periods: range = range(1, 49), price: float = 60.0):
    return [
        {"settlementDate": date_str, "settlementPeriod": p, "systemSellPrice": price}
        for p in periods
    ]


def test_contract_length_is_365():
    assert CONTRACT_LENGTH_DAYS == 365


def test_empty_customers_returns_empty():
    result = run_settlement(
        customers=[],
        start_date="2022-01-01",
        end_date="2022-01-01",
        consumption_shape=_flat_shape(),
        system_price_records=_price_records("2022-01-01"),
    )
    assert result == []


def test_single_customer_single_day_record_count():
    result = run_settlement(
        customers=[{"customer_id": "C1", "acquisition_date": "2022-01-01", "unit_rate_gbp_per_mwh": 100.0}],
        start_date="2022-01-01",
        end_date="2022-01-01",
        consumption_shape=_flat_shape(1.0),
        system_price_records=_price_records("2022-01-01"),
    )
    assert len(result) == 48


def test_revenue_formula():
    # 2 kWh at 100 GBP/MWh -> 2/1000 * 100 = 0.2 GBP
    result = run_settlement(
        customers=[{"customer_id": "C1", "acquisition_date": "2022-01-01", "unit_rate_gbp_per_mwh": 100.0}],
        start_date="2022-01-01",
        end_date="2022-01-01",
        consumption_shape=_flat_shape(2.0),
        system_price_records=_price_records("2022-01-01", price=60.0),
    )
    assert result[0]["revenue_gbp"] == pytest.approx(2.0 / 1000.0 * 100.0)


def test_wholesale_cost_formula():
    # 2 kWh at spot 60 GBP/MWh -> 0.12 GBP
    result = run_settlement(
        customers=[{"customer_id": "C1", "acquisition_date": "2022-01-01", "unit_rate_gbp_per_mwh": 100.0}],
        start_date="2022-01-01",
        end_date="2022-01-01",
        consumption_shape=_flat_shape(2.0),
        system_price_records=_price_records("2022-01-01", price=60.0),
    )
    assert result[0]["wholesale_cost_gbp"] == pytest.approx(2.0 / 1000.0 * 60.0)


def test_margin_equals_revenue_minus_cost():
    result = run_settlement(
        customers=[{"customer_id": "C1", "acquisition_date": "2022-01-01", "unit_rate_gbp_per_mwh": 100.0}],
        start_date="2022-01-01",
        end_date="2022-01-01",
        consumption_shape=_flat_shape(1.0),
        system_price_records=_price_records("2022-01-01"),
    )
    r = result[0]
    assert r["margin_gbp"] == pytest.approx(r["revenue_gbp"] - r["wholesale_cost_gbp"])


def test_customer_outside_contract_window_not_settled():
    # Acquisition 2022-01-01, contract ends 2022-12-31 (exclusive)
    # Query date 2023-01-02 should produce no records
    result = run_settlement(
        customers=[{"customer_id": "C1", "acquisition_date": "2022-01-01", "unit_rate_gbp_per_mwh": 100.0}],
        start_date="2023-01-02",
        end_date="2023-01-02",
        consumption_shape=_flat_shape(),
        system_price_records=_price_records("2023-01-02"),
    )
    assert len(result) == 0


def test_periods_without_price_data_skipped():
    # Only provide price for SP1 — should get exactly 1 record
    result = run_settlement(
        customers=[{"customer_id": "C1", "acquisition_date": "2022-01-01", "unit_rate_gbp_per_mwh": 100.0}],
        start_date="2022-01-01",
        end_date="2022-01-01",
        consumption_shape=_flat_shape(),
        system_price_records=[{"settlementDate": "2022-01-01", "settlementPeriod": 1, "systemSellPrice": 60.0}],
    )
    assert len(result) == 1
    assert result[0]["settlement_period"] == 1


def test_all_record_keys_present():
    result = run_settlement(
        customers=[{"customer_id": "C1", "acquisition_date": "2022-01-01", "unit_rate_gbp_per_mwh": 100.0}],
        start_date="2022-01-01",
        end_date="2022-01-01",
        consumption_shape=_flat_shape(),
        system_price_records=_price_records("2022-01-01"),
    )
    expected_keys = {
        "customer_id", "settlement_date", "settlement_period",
        "consumption_kwh", "unit_rate_gbp_per_mwh",
        "revenue_gbp", "wholesale_cost_gbp", "margin_gbp",
    }
    assert set(result[0].keys()) == expected_keys


def test_two_customers_independent_records():
    customers = [
        {"customer_id": "C1", "acquisition_date": "2022-01-01", "unit_rate_gbp_per_mwh": 100.0},
        {"customer_id": "C2", "acquisition_date": "2022-01-01", "unit_rate_gbp_per_mwh": 80.0},
    ]
    result = run_settlement(
        customers=customers,
        start_date="2022-01-01",
        end_date="2022-01-01",
        consumption_shape=_flat_shape(),
        system_price_records=_price_records("2022-01-01"),
    )
    c1_records = [r for r in result if r["customer_id"] == "C1"]
    c2_records = [r for r in result if r["customer_id"] == "C2"]
    assert len(c1_records) == 48
    assert len(c2_records) == 48
    assert c1_records[0]["unit_rate_gbp_per_mwh"] == 100.0
    assert c2_records[0]["unit_rate_gbp_per_mwh"] == 80.0


def test_contract_boundary_exclusive_right():
    # Customer acquired 2022-01-01, contract window [2022-01-01, 2023-01-01)
    # 2023-01-01 exactly should NOT be settled
    result = run_settlement(
        customers=[{"customer_id": "C1", "acquisition_date": "2022-01-01", "unit_rate_gbp_per_mwh": 100.0}],
        start_date="2023-01-01",
        end_date="2023-01-01",
        consumption_shape=_flat_shape(),
        system_price_records=_price_records("2023-01-01"),
    )
    assert len(result) == 0


def test_run_settlement_returns_list():
    result = run_settlement(
        customers=[],
        start_date="2022-01-01",
        end_date="2022-01-01",
        consumption_shape=_flat_shape(),
        system_price_records=_price_records("2022-01-01"),
    )
    assert isinstance(result, list)


def test_settlement_date_in_record():
    result = run_settlement(
        customers=[{"customer_id": "C1", "acquisition_date": "2022-01-01", "unit_rate_gbp_per_mwh": 100.0}],
        start_date="2022-01-01",
        end_date="2022-01-01",
        consumption_shape=_flat_shape(),
        system_price_records=_price_records("2022-01-01"),
    )
    assert all(r["settlement_date"] == "2022-01-01" for r in result)


def test_higher_unit_rate_higher_revenue():
    def _make_result(rate):
        return run_settlement(
            customers=[{"customer_id": "C1", "acquisition_date": "2022-01-01", "unit_rate_gbp_per_mwh": rate}],
            start_date="2022-01-01",
            end_date="2022-01-01",
            consumption_shape=_flat_shape(1.0),
            system_price_records=_price_records("2022-01-01", price=60.0),
        )
    low = sum(r["revenue_gbp"] for r in _make_result(80.0))
    high = sum(r["revenue_gbp"] for r in _make_result(200.0))
    assert high > low
