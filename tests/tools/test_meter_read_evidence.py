"""Tests for the meter-read evidence surface (Phase 3, CORE_FIDELITY_PHASES.md
item 1, rule 0b): meter_read_log must reach dashboard.json's customers
section so the Sim tab can render the delay/estimation histogram."""
from tools.generate_dashboard_data import extract_customers


def _base_data(**overrides):
    data = {"customer_events": [], "retention_log": [], "per_customer_lifetime": {}}
    data.update(overrides)
    return data


def test_extract_customers_carries_meter_read_log():
    data = _base_data(meter_read_log=[
        {"customer_id": "C1", "period_end": "2020-01-31", "meter_type": "smart",
         "delay_days": 1, "status": "actual", "estimated_consumption_kwh": None,
         "true_consumption_kwh": 300.0, "consecutive_estimated_count": 0,
         "forced_catch_up": False},
    ])
    out = extract_customers(data)
    assert out["meter_read_log"] == [
        {"customer_id": "C1", "period_end": "2020-01-31", "meter_type": "smart",
         "delay_days": 1, "status": "actual"},
    ]


def test_extract_customers_meter_read_log_empty_when_absent():
    out = extract_customers(_base_data())
    assert out["meter_read_log"] == []
