import pytest

from simulation.run_phase3b_regression import _fit_ols


def test_fit_ols_recovers_exact_linear_relationship():
    # ssp = 10 + 2*gas_price, independent of demand/wind (zero coefficients).
    # demand and wind vary independently so the design matrix is full rank.
    rows = [
        {"ssp": 10.0 + 2.0 * gas, "gas_price": gas, "demand_mw": demand, "wind_mw": wind}
        for gas, demand, wind in (
            (5.0, 1000.0, 500.0),
            (10.0, 1100.0, 480.0),
            (15.0, 950.0, 510.0),
            (20.0, 1050.0, 490.0),
            (25.0, 1000.0, 505.0),
        )
    ]
    fit = _fit_ols(rows)
    assert fit["intercept"] == pytest.approx(10.0, abs=1e-6)
    assert fit["coef_gas_price"] == pytest.approx(2.0, abs=1e-6)
    assert fit["mae"] == pytest.approx(0.0, abs=1e-6)
    assert fit["r2"] == pytest.approx(1.0, abs=1e-6)


def test_fit_ols_reports_mae_and_r2_for_imperfect_fit():
    rows = [
        {"ssp": 10.0, "gas_price": 5.0, "demand_mw": 1000.0, "wind_mw": 500.0},
        {"ssp": 20.0, "gas_price": 5.0, "demand_mw": 1000.0, "wind_mw": 500.0},
        {"ssp": 12.0, "gas_price": 10.0, "demand_mw": 1100.0, "wind_mw": 400.0},
        {"ssp": 25.0, "gas_price": 10.0, "demand_mw": 1100.0, "wind_mw": 400.0},
    ]
    fit = _fit_ols(rows)
    assert fit["n"] == 4
    assert fit["mae"] >= 0.0
    assert fit["r2"] <= 1.0
