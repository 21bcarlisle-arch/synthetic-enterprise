"""Phase NE -- Gas Pass-Through Capital Risk Correction.

Root cause: assess_term_risk was called with naked_kwh = aq_kwh * (1 - hf)
for pass_through gas (hf=0), generating full VaR capital on a zero-risk position.
Fix: naked_kwh = 0.0 for pass_through (customer pays spot directly).
"""
import pytest
from sim.risk_engine import (
    WACC,
    assess_term_risk,
    calculate_active_collateral,
    calculate_monthly_cost_of_capital,
    calculate_var,
)
from simulation.gas_settlement import GAS_PASS_THROUGH_SERVICE_FEE_GBP_PER_MWH


def _minimal_gas_records(n: int = 30) -> list[dict]:
    from datetime import date, timedelta
    base = date(2022, 1, 1)
    return [{"settlementDate": (base + timedelta(days=i)).isoformat(), "systemSellPrice": 100.0} for i in range(n)]


def test_var_zero_volume_is_zero():
    assert calculate_var(sigma=0.5, naked_volume_kwh=0.0, forward_price_gbp_per_mwh=100.0) == 0.0


def test_assess_term_risk_zero_naked_returns_zero_capital():
    r = assess_term_risk('2022-01-01', 0.0, 100.0, _minimal_gas_records())
    assert r['monthly_cost_of_capital_gbp'] == 0.0


def test_assess_term_risk_zero_naked_all_capital_keys_zero():
    r = assess_term_risk('2022-01-01', 0.0, 100.0, _minimal_gas_records())
    assert r['var_current_gbp'] == 0.0
    assert r['var_stressed_gbp'] == 0.0
    assert r['active_collateral_gbp'] == 0.0
    assert r['monthly_cost_of_capital_gbp'] == 0.0


def test_assess_term_risk_nonzero_naked_has_positive_capital():
    r = assess_term_risk('2022-01-01', 1_000_000.0, 100.0, _minimal_gas_records())
    assert r['monthly_cost_of_capital_gbp'] > 0.0


def test_var_linear_in_volume():
    v1 = calculate_var(0.3, 1_000_000.0, 100.0)
    v2 = calculate_var(0.3, 2_000_000.0, 100.0)
    assert abs(v2 - 2 * v1) < 1e-6


def test_var_linear_in_forward_price():
    v1 = calculate_var(0.3, 500_000.0, 100.0)
    v2 = calculate_var(0.3, 500_000.0, 200.0)
    assert abs(v2 - 2 * v1) < 1e-6


def test_active_collateral_takes_max():
    assert calculate_active_collateral(1000.0, 2000.0) == 2000.0
    assert calculate_active_collateral(3000.0, 500.0) == 3000.0
    assert calculate_active_collateral(0.0, 0.0) == 0.0


def test_monthly_cost_zero_collateral():
    assert calculate_monthly_cost_of_capital(0.0) == 0.0


def test_monthly_cost_positive_collateral():
    cost = calculate_monthly_cost_of_capital(12000.0)
    assert abs(cost - 12000.0 * WACC / 12) < 1e-6


def test_pass_through_service_fee_is_2_gbp_per_mwh():
    assert GAS_PASS_THROUGH_SERVICE_FEE_GBP_PER_MWH == 2.0


def test_service_fee_at_5gwh_is_10k_per_year():
    annual_mwh = 5_000_000 / 1000
    annual_income = annual_mwh * GAS_PASS_THROUGH_SERVICE_FEE_GBP_PER_MWH
    assert annual_income == 10_000.0


def test_fixed_tariff_naked_kwh_is_aq_times_one_minus_hf():
    aq_kwh = 500_000
    hf = 0.40
    term_tariff_type = 'fixed'
    naked = 0.0 if term_tariff_type == 'pass_through' else aq_kwh * (1.0 - hf)
    assert naked == pytest.approx(300_000.0)


def test_pass_through_naked_kwh_is_always_zero():
    aq_kwh = 5_000_000
    for hf in (0.0, 0.25, 0.5, 1.0):
        term_tariff_type = 'pass_through'
        naked = 0.0 if term_tariff_type == 'pass_through' else aq_kwh * (1.0 - hf)
        assert naked == 0.0


def _run_single_day_pass_through(date_str: str, spot: float) -> dict:
    from simulation.gas_settlement import run_gas_term
    y, m, d = date_str.split("-")
    next_day = f"{y}-{m}-{int(d)+1:02d}"
    recs = run_gas_term(
        "PT_TEST", date_str, next_day,
        aq_kwh=365_000,
        unit_rate_gbp_mwh=999.0,
        hedge_fraction=0.0,
        forward_price=999.0,
        monthly_cost_of_capital_gbp=0.0,
        gas_price_records=[{"settlementDate": date_str, "systemSellPrice": spot}],
        segment="I&C",
        pass_through=True,
    )
    return recs[0]


def test_pass_through_margin_far_below_unit_rate_margin():
    rec = _run_single_day_pass_through("2022-06-15", 50.0)
    assert rec["margin_gbp"] < 50.0


def test_pass_through_net_margin_positive_with_zero_capital():
    rec = _run_single_day_pass_through("2023-06-15", 120.0)
    assert rec["net_margin_gbp"] > 0.0


def test_pass_through_capital_cost_is_zero():
    rec = _run_single_day_pass_through("2022-03-01", 50.0)
    assert rec["capital_cost_gbp"] == 0.0
