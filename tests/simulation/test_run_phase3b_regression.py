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


from simulation.run_phase3b_regression import _fit_ols_by_year


def _make_exact_rows(n=5):
    return [
        {
            "ssp": 10.0 + 2.0 * i,
            "gas_price": float(i),
            "demand_mw": 1000.0 + i,
            "wind_mw": 500.0 - i,
        }
        for i in range(1, n + 1)
    ]


def test_fit_ols_n_matches_len():
    rows = _make_exact_rows(5)
    fit = _fit_ols(rows)
    assert fit["n"] == 5


def test_fit_ols_all_keys_present():
    rows = _make_exact_rows(5)
    fit = _fit_ols(rows)
    for key in ("n", "intercept", "coef_gas_price", "coef_demand_mw", "coef_wind_mw", "mae", "rmse", "r2"):
        assert key in fit, f"missing key: {key}"


def test_fit_ols_rmse_nonnegative():
    rows = _make_exact_rows(5)
    fit = _fit_ols(rows)
    assert fit["rmse"] >= 0.0


def test_fit_ols_rmse_geq_mae():
    rows = [
        {"ssp": float(s), "gas_price": float(g), "demand_mw": 1000.0, "wind_mw": 500.0}
        for s, g in [(10, 1), (20, 2), (25, 3), (35, 4), (30, 5)]
    ]
    fit = _fit_ols(rows)
    assert fit["rmse"] >= fit["mae"] - 1e-9


def test_fit_ols_perfect_gives_rmse_zero():
    rows = [
        {"ssp": 5.0 * gas, "gas_price": gas, "demand_mw": 1000.0 + gas, "wind_mw": 500.0 - gas}
        for gas in [1.0, 2.0, 3.0, 4.0, 5.0]
    ]
    fit = _fit_ols(rows)
    assert fit["rmse"] == pytest.approx(0.0, abs=1e-6)


def test_fit_ols_r2_at_most_one():
    rows = _make_exact_rows(5)
    fit = _fit_ols(rows)
    assert fit["r2"] <= 1.0 + 1e-9


def test_fit_ols_by_year_empty():
    result = _fit_ols_by_year([])
    assert result == {}


def test_fit_ols_by_year_two_years():
    rows_2022 = [
        {"settlementDate": "2022-01-01", "ssp": 10.0 + g, "gas_price": g, "demand_mw": 1000.0, "wind_mw": 500.0}
        for g in [5.0, 10.0, 15.0, 20.0, 25.0]
    ]
    rows_2023 = [
        {"settlementDate": "2023-01-01", "ssp": 5.0 + g, "gas_price": g, "demand_mw": 1100.0, "wind_mw": 400.0}
        for g in [5.0, 10.0, 15.0, 20.0, 25.0]
    ]
    result = _fit_ols_by_year(rows_2022 + rows_2023)
    assert set(result.keys()) == {"2022", "2023"}
    assert result["2022"]["n"] == 5
    assert result["2023"]["n"] == 5


def test_fit_ols_returns_dict():
    rows = _make_exact_rows(5)
    fit = _fit_ols(rows)
    assert isinstance(fit, dict)


def test_fit_ols_by_year_returns_dict():
    result = _fit_ols_by_year([])
    assert isinstance(result, dict)


def test_fit_ols_by_year_single_year():
    rows = [
        {"settlementDate": "2020-06-01", "ssp": 10.0 + g, "gas_price": g, "demand_mw": 1000.0, "wind_mw": 500.0}
        for g in [5.0, 10.0, 15.0, 20.0, 25.0]
    ]
    result = _fit_ols_by_year(rows)
    assert "2020" in result
    assert result["2020"]["n"] == 5
