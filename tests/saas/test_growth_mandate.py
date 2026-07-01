"""Tests for saas.growth_mandate — Phase 8a."""

import pytest

from saas.growth_mandate import (
    acquisition_budget_gbp,
    ACQUISITION_WIN_RATE,
    COST_PER_ACQUISITION,
    FIXED_COST_MONTHLY,
    MANDATE,
    acquisition_budget_gbp,
    forecast_churns_next_year,
    roll_acquisition,
)


def test_mandate_constants_exist_with_correct_types():
    assert MANDATE in ("flat", "grow", "shrink")
    assert isinstance(COST_PER_ACQUISITION, dict)
    assert "resi" in COST_PER_ACQUISITION and "SME" in COST_PER_ACQUISITION
    assert isinstance(FIXED_COST_MONTHLY, float)
    assert FIXED_COST_MONTHLY > 0


def test_roll_acquisition_deterministic_by_seed():
    result_a = roll_acquisition("resi", "seed_abc")
    result_b = roll_acquisition("resi", "seed_abc")
    assert result_a == result_b


def test_roll_acquisition_returns_bool():
    assert isinstance(roll_acquisition("resi", "any"), bool)
    assert isinstance(roll_acquisition("SME", "any"), bool)


def test_roll_acquisition_respects_segment_rates():
    # With many seeds, win frequency should approach the configured rate.
    resi_wins = sum(roll_acquisition("resi", f"s{i}") for i in range(500))
    sme_wins = sum(roll_acquisition("SME", f"s{i}") for i in range(500))
    # Resi rate (0.20) should win more than SME rate (0.12)
    assert resi_wins > sme_wins


def test_forecast_churns_next_year_returns_accounts_in_window():
    churn_risk = {
        "C3": [{"event_date": "2020-06-01", "churn_probability": 0.45}],
        "C1": [{"event_date": "2021-01-01", "churn_probability": 0.30}],
    }
    result = forecast_churns_next_year(churn_risk, "2020-01-01")
    assert "C3" in result
    assert abs(result["C3"] - 0.45) < 1e-6


def test_forecast_churns_next_year_excludes_out_of_window():
    churn_risk = {
        "C3": [{"event_date": "2022-06-01", "churn_probability": 0.50}],
    }
    result = forecast_churns_next_year(churn_risk, "2020-01-01")
    assert "C3" not in result


def test_acquisition_budget_sums_probabilities():
    churn_forecast = {"C3": 0.50, "C5": 0.30}
    segment_by_account = {"C3": "resi", "C5": "SME"}
    budget = acquisition_budget_gbp(churn_forecast, segment_by_account)
    expected = 0.50 * COST_PER_ACQUISITION["resi"] + 0.30 * COST_PER_ACQUISITION["SME"]
    assert abs(budget - expected) < 0.01


def test_acquisition_budget_defaults_unknown_segment_to_resi():
    churn_forecast = {"C99": 1.0}
    segment_by_account = {}
    budget = acquisition_budget_gbp(churn_forecast, segment_by_account)
    assert abs(budget - COST_PER_ACQUISITION["resi"]) < 0.01


from saas.growth_mandate import (
    MANDATE,
    COST_PER_ACQUISITION,
    ACQUISITION_WIN_RATE,
    FIXED_COST_MONTHLY,
    should_attempt_acquisition,
)


def test_mandate_is_flat():
    assert MANDATE == "flat"


def test_resi_acquisition_cost():
    assert COST_PER_ACQUISITION["resi"] == pytest.approx(150.0)


def test_sme_acquisition_cost():
    assert COST_PER_ACQUISITION["SME"] == pytest.approx(400.0)


def test_resi_win_rate():
    assert ACQUISITION_WIN_RATE["resi"] == pytest.approx(0.20)


def test_sme_win_rate():
    assert ACQUISITION_WIN_RATE["SME"] == pytest.approx(0.12)


def test_fixed_cost_monthly():
    assert FIXED_COST_MONTHLY == pytest.approx(50.0)


def test_should_attempt_nonresi_always_proceeds():
    proceed, reason = should_attempt_acquisition("SME", "electricity", 999.0, "2022-01-01")
    assert proceed is True
    assert reason is None


def test_should_attempt_gas_always_proceeds():
    proceed, reason = should_attempt_acquisition("resi", "gas", 999.0, "2022-01-01")
    assert proceed is True
    assert reason is None


def test_acquisition_budget_empty():
    assert acquisition_budget_gbp({}, {}) == pytest.approx(0.0)


def test_acquisition_budget_single_resi():
    budget = acquisition_budget_gbp({"C1": 0.5}, {"C1": "resi"})
    assert budget == pytest.approx(0.5 * 150.0)
