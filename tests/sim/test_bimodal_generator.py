from datetime import date

import pytest

from sim.scenario.bimodal_generator import (
    SCENARIOS,
    ScenarioParams,
    _markov_transition_probs,
    generate_scenario_prices,
)


def test_generate_returns_one_record_per_day():
    records = generate_scenario_prices(2027, 2027, "central_2027", seed="t1")
    assert len(records) == 365


def test_generate_multi_year_count():
    records = generate_scenario_prices(2027, 2029, "central_2027", seed="t2")
    expected = sum(
        366 if year % 4 == 0 else 365 for year in range(2027, 2030)
    )
    assert len(records) == expected


def test_records_are_sorted_by_date():
    records = generate_scenario_prices(2027, 2027, "central_2027", seed="t3")
    dates = [r["settlementDate"] for r in records]
    assert dates == sorted(dates)


def test_first_and_last_dates_correct():
    records = generate_scenario_prices(2027, 2028, "central_2027", seed="t4")
    assert records[0]["settlementDate"] == "2027-01-01"
    assert records[-1]["settlementDate"] == "2028-12-31"


def test_all_records_have_required_keys():
    records = generate_scenario_prices(2027, 2027, "central_2027", seed="t5")
    for r in records:
        assert "settlementDate" in r
        assert "systemSellPrice" in r


def test_prices_are_floats():
    records = generate_scenario_prices(2027, 2027, "central_2027", seed="t6")
    for r in records:
        assert isinstance(r["systemSellPrice"], float)


def test_negative_price_floor_respected():
    params = ScenarioParams(
        negative_days_per_year=50.0,
        negative_price_floor=-75.0,
        negative_price_mean=-40.0,
        negative_price_std=20.0,
    )
    records = generate_scenario_prices(2027, 2028, params, seed="t7")
    prices = [r["systemSellPrice"] for r in records]
    assert all(p >= -75.0 for p in prices), f"Found prices below floor: {min(prices)}"


def test_stress_scenario_has_more_negative_days_than_baseline():
    baseline = generate_scenario_prices(2027, 2027, "baseline_2025", seed="neg")
    stress = generate_scenario_prices(2027, 2027, "stress_dunkelflaute_2027", seed="neg")
    baseline_neg = sum(1 for r in baseline if r["systemSellPrice"] < 0)
    stress_neg = sum(1 for r in stress if r["systemSellPrice"] < 0)
    assert stress_neg > baseline_neg


def test_central_2027_mean_price_lower_than_baseline():
    """Central 2027 has more renewable hours — lower average price."""
    baseline = generate_scenario_prices(2027, 2027, "baseline_2025", seed="mean")
    central = generate_scenario_prices(2027, 2027, "central_2027", seed="mean")
    baseline_mean = sum(r["systemSellPrice"] for r in baseline) / len(baseline)
    central_mean = sum(r["systemSellPrice"] for r in central) / len(central)
    assert central_mean < baseline_mean


def test_deterministic_same_seed():
    a = generate_scenario_prices(2027, 2027, "central_2027", seed="det")
    b = generate_scenario_prices(2027, 2027, "central_2027", seed="det")
    assert a == b


def test_different_seeds_produce_different_output():
    a = generate_scenario_prices(2027, 2027, "central_2027", seed="seedA")
    b = generate_scenario_prices(2027, 2027, "central_2027", seed="seedB")
    prices_a = [r["systemSellPrice"] for r in a]
    prices_b = [r["systemSellPrice"] for r in b]
    assert prices_a != prices_b


def test_custom_scenario_params():
    params = ScenarioParams(
        upper_mode_mean=200.0,
        upper_mode_std=5.0,
        lower_mode_mean=10.0,
        lower_mode_std=2.0,
        lower_mode_fraction=0.0,  # always in upper mode
        negative_days_per_year=0.0,
        dunkelflaute_events_per_year=0.0,
    )
    records = generate_scenario_prices(2027, 2027, params, seed="custom")
    prices = [r["systemSellPrice"] for r in records]
    # With lower_fraction=0 and no specials, all prices should be near upper mode
    assert all(150 < p < 260 for p in prices), f"Unexpected prices: min={min(prices)}, max={max(prices)}"


def test_all_named_scenarios_are_generatable():
    for name in SCENARIOS:
        records = generate_scenario_prices(2027, 2027, name, seed="all")
        assert len(records) == 365, f"Scenario {name!r} returned wrong count"


def test_unknown_scenario_raises_value_error():
    with pytest.raises(ValueError, match="Unknown scenario"):
        generate_scenario_prices(2027, 2027, "nonexistent_scenario")


def test_markov_transition_probs_stationary_distribution():
    """Stationary distribution of the Markov chain should equal lower_mode_fraction."""
    pi_L = 0.55
    p_stay_lower, p_stay_upper = _markov_transition_probs(pi_L, persistence=0.85)
    # Stationary: pi_L × (1-p_LL) = pi_U × (1-p_UU)
    pi_U = 1.0 - pi_L
    lhs = pi_L * (1.0 - p_stay_lower)
    rhs = pi_U * (1.0 - p_stay_upper)
    assert abs(lhs - rhs) < 1e-10


def test_markov_long_run_fraction_matches_target():
    """Simulate the Markov chain; long-run fraction should approximate lower_mode_fraction."""
    import random as _rnd
    pi_L = 0.55
    p_stay_lower, p_stay_upper = _markov_transition_probs(pi_L, persistence=0.85)
    rng = _rnd.Random("markov_test")
    state = rng.random() < pi_L
    lower_count = 0
    n = 100_000
    for _ in range(n):
        if state:
            state = rng.random() < p_stay_lower
        else:
            state = rng.random() >= p_stay_upper
        lower_count += state
    observed = lower_count / n
    assert abs(observed - pi_L) < 0.02, f"Observed {observed:.3f}, expected {pi_L}"
