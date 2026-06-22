import pytest

from sim.scenario.gas_scenario_generator import (
    GAS_SCENARIOS,
    GasScenarioParams,
    generate_gas_scenario_prices,
)


def test_returns_one_record_per_day():
    records = generate_gas_scenario_prices(2027, 2027, "central_2027", seed="g1")
    assert len(records) == 365


def test_records_sorted_by_date():
    records = generate_gas_scenario_prices(2027, 2027, "central_2027", seed="g2")
    dates = [r["settlementDate"] for r in records]
    assert dates == sorted(dates)


def test_first_and_last_dates():
    records = generate_gas_scenario_prices(2026, 2028, "central_2027", seed="g3")
    assert records[0]["settlementDate"] == "2026-01-01"
    assert records[-1]["settlementDate"] == "2028-12-31"


def test_prices_non_negative_above_floor():
    params = GasScenarioParams(price_floor=5.0)
    records = generate_gas_scenario_prices(2027, 2028, params, seed="floor")
    assert all(r["systemSellPrice"] >= 5.0 for r in records)


def test_stress_scenario_higher_mean_than_baseline():
    baseline = generate_gas_scenario_prices(2027, 2027, "baseline_2025", seed="cmp")
    stress = generate_gas_scenario_prices(2027, 2027, "stress_dunkelflaute_2027", seed="cmp")
    baseline_mean = sum(r["systemSellPrice"] for r in baseline) / len(baseline)
    stress_mean = sum(r["systemSellPrice"] for r in stress) / len(stress)
    assert stress_mean > baseline_mean


def test_deterministic_same_seed():
    a = generate_gas_scenario_prices(2027, 2027, "central_2027", seed="det")
    b = generate_gas_scenario_prices(2027, 2027, "central_2027", seed="det")
    assert a == b


def test_all_named_scenarios_work():
    for name in GAS_SCENARIOS:
        records = generate_gas_scenario_prices(2027, 2027, name, seed="all")
        assert len(records) == 365


def test_unknown_scenario_raises():
    with pytest.raises(ValueError, match="Unknown gas scenario"):
        generate_gas_scenario_prices(2027, 2027, "bad_scenario")


def test_custom_params():
    params = GasScenarioParams(
        upper_regime_mean=100.0, upper_regime_std=2.0,
        lower_regime_mean=100.0, lower_regime_std=2.0,
        price_floor=90.0,
        dunkelflaute_events_per_year=0.0,  # no dunkelflaute so no spike above ~120
    )
    records = generate_gas_scenario_prices(2027, 2027, params, seed="custom")
    prices = [r["systemSellPrice"] for r in records]
    assert all(90 <= p < 130 for p in prices)
