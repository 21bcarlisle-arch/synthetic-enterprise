"""Tests for simulation/hedged_settlement.py -- Phase 1e hedge-aware settlement."""

import pytest

from simulation.hedged_settlement import run_hedged_term


def _shape_fn(kwh_per_period=1.0):
    return lambda date_str: [kwh_per_period] * 48


def _prices(dates, periods=range(1, 49), price=60.0):
    return [
        {"settlementDate": d, "settlementPeriod": p, "systemSellPrice": price}
        for d in dates for p in periods
    ]


def test_single_day_48_periods():
    result = run_hedged_term(
        customer_id="C1",
        term_start_date="2022-01-01",
        term_end_date="2022-01-02",
        fixed_tariff_rate_gbp_per_mwh=100.0,
        hedge_price_gbp_per_mwh=80.0,
        hedge_fraction=0.5,
        monthly_cost_of_capital_gbp=10.0,
        consumption_shape=_shape_fn(1.0),
        system_price_records=_prices(["2022-01-01"]),
    )
    assert len(result) == 48


def test_end_date_exclusive():
    # term_end_date is exclusive: 2022-01-02 should not produce records for that date
    result = run_hedged_term(
        customer_id="C1",
        term_start_date="2022-01-01",
        term_end_date="2022-01-01",
        fixed_tariff_rate_gbp_per_mwh=100.0,
        hedge_price_gbp_per_mwh=80.0,
        hedge_fraction=0.5,
        monthly_cost_of_capital_gbp=10.0,
        consumption_shape=_shape_fn(),
        system_price_records=_prices(["2022-01-01"]),
    )
    assert len(result) == 0


def test_missing_price_periods_skipped():
    # Only provide SP1
    result = run_hedged_term(
        customer_id="C1",
        term_start_date="2022-01-01",
        term_end_date="2022-01-02",
        fixed_tariff_rate_gbp_per_mwh=100.0,
        hedge_price_gbp_per_mwh=80.0,
        hedge_fraction=0.5,
        monthly_cost_of_capital_gbp=10.0,
        consumption_shape=_shape_fn(),
        system_price_records=[
            {"settlementDate": "2022-01-01", "settlementPeriod": 1, "systemSellPrice": 60.0}
        ],
    )
    assert len(result) == 1


def test_all_keys_present():
    result = run_hedged_term(
        customer_id="C1",
        term_start_date="2022-01-01",
        term_end_date="2022-01-02",
        fixed_tariff_rate_gbp_per_mwh=100.0,
        hedge_price_gbp_per_mwh=80.0,
        hedge_fraction=0.5,
        monthly_cost_of_capital_gbp=10.0,
        consumption_shape=_shape_fn(),
        system_price_records=_prices(["2022-01-01"]),
    )
    expected_keys = {
        "customer_id", "settlement_date", "settlement_period",
        "consumption_kwh", "unit_rate_gbp_per_mwh", "hedge_price_gbp_per_mwh",
        "hedge_fraction", "hedged_volume_kwh", "unhedged_volume_kwh",
        "revenue_gbp", "wholesale_cost_gbp", "margin_gbp",
        "ro_levy_gbp", "cfd_levy_gbp", "policy_cost_gbp",
        "capital_cost_gbp", "net_margin_gbp",
    }
    assert expected_keys.issubset(set(result[0].keys()))


def test_fully_hedged_spot_irrelevant():
    # hedge_fraction=1.0 → wholesale cost = hedge_price × volume
    # Two runs with different spot prices should have same wholesale_cost_gbp
    r1 = run_hedged_term(
        customer_id="C1",
        term_start_date="2022-01-01",
        term_end_date="2022-01-02",
        fixed_tariff_rate_gbp_per_mwh=100.0,
        hedge_price_gbp_per_mwh=80.0,
        hedge_fraction=1.0,
        monthly_cost_of_capital_gbp=0.0,
        consumption_shape=_shape_fn(2.0),
        system_price_records=_prices(["2022-01-01"], price=50.0),
    )
    r2 = run_hedged_term(
        customer_id="C1",
        term_start_date="2022-01-01",
        term_end_date="2022-01-02",
        fixed_tariff_rate_gbp_per_mwh=100.0,
        hedge_price_gbp_per_mwh=80.0,
        hedge_fraction=1.0,
        monthly_cost_of_capital_gbp=0.0,
        consumption_shape=_shape_fn(2.0),
        system_price_records=_prices(["2022-01-01"], price=500.0),
    )
    assert r1[0]["wholesale_cost_gbp"] == pytest.approx(r2[0]["wholesale_cost_gbp"])


def test_capital_cost_allocated_per_period():
    # 48 periods in one day; capital/period = 10/48
    result = run_hedged_term(
        customer_id="C1",
        term_start_date="2022-01-01",
        term_end_date="2022-01-02",
        fixed_tariff_rate_gbp_per_mwh=100.0,
        hedge_price_gbp_per_mwh=80.0,
        hedge_fraction=0.5,
        monthly_cost_of_capital_gbp=48.0,
        consumption_shape=_shape_fn(),
        system_price_records=_prices(["2022-01-01"]),
    )
    # 48 periods settled in January; 48 GBP/month / 48 = 1 GBP per period
    assert result[0]["capital_cost_gbp"] == pytest.approx(1.0)


def test_net_margin_deducts_policy_and_capital():
    result = run_hedged_term(
        customer_id="C1",
        term_start_date="2022-01-01",
        term_end_date="2022-01-02",
        fixed_tariff_rate_gbp_per_mwh=100.0,
        hedge_price_gbp_per_mwh=80.0,
        hedge_fraction=0.5,
        monthly_cost_of_capital_gbp=0.0,
        consumption_shape=_shape_fn(),
        system_price_records=_prices(["2022-01-01"]),
    )
    r = result[0]
    # net_margin < margin_gbp because policy costs + network are deducted
    assert r["net_margin_gbp"] < r["margin_gbp"]


from simulation.hedged_settlement import run_deemed_term


def test_deemed_single_day_48_periods():
    result = run_deemed_term(
        customer_id="C1",
        term_start_date="2022-01-01",
        term_end_date="2022-01-02",
        deemed_premium=0.10,
        consumption_shape=_shape_fn(1.0),
        system_price_records=_prices(["2022-01-01"]),
    )
    assert len(result) == 48


def test_deemed_keys_present():
    result = run_deemed_term(
        customer_id="C1",
        term_start_date="2022-01-01",
        term_end_date="2022-01-02",
        deemed_premium=0.10,
        consumption_shape=_shape_fn(1.0),
        system_price_records=_prices(["2022-01-01"]),
    )
    r = result[0]
    for key in ("customer_id", "settlement_date", "settlement_period",
                "consumption_kwh", "revenue_gbp", "wholesale_cost_gbp",
                "margin_gbp", "capital_cost_gbp", "net_margin_gbp",
                "hedge_fraction", "tariff_type"):
        assert key in r


def test_deemed_zero_premium_gives_zero_margin():
    result = run_deemed_term(
        customer_id="C1",
        term_start_date="2022-01-01",
        term_end_date="2022-01-02",
        deemed_premium=0.0,
        consumption_shape=_shape_fn(1.0),
        system_price_records=_prices(["2022-01-01"], price=100.0),
    )
    for r in result:
        assert r["margin_gbp"] == pytest.approx(0.0)


def test_deemed_hedge_fraction_is_zero():
    result = run_deemed_term(
        customer_id="C1",
        term_start_date="2022-01-01",
        term_end_date="2022-01-02",
        deemed_premium=0.10,
        consumption_shape=_shape_fn(1.0),
        system_price_records=_prices(["2022-01-01"]),
    )
    for r in result:
        assert r["hedge_fraction"] == 0.0
        assert r["capital_cost_gbp"] == pytest.approx(0.0)


def test_deemed_revenue_equals_spot_times_premium():
    spot = 100.0
    premium = 0.20
    consumption_kwh = 2.0
    result = run_deemed_term(
        customer_id="C1",
        term_start_date="2022-01-01",
        term_end_date="2022-01-02",
        deemed_premium=premium,
        consumption_shape=_shape_fn(consumption_kwh),
        system_price_records=_prices(["2022-01-01"], price=spot),
    )
    r = result[0]
    expected_revenue = spot * (1.0 + premium) * (consumption_kwh / 1000.0)
    assert r["revenue_gbp"] == pytest.approx(expected_revenue)


def test_deemed_tariff_type_field():
    result = run_deemed_term(
        customer_id="C1",
        term_start_date="2022-01-01",
        term_end_date="2022-01-02",
        deemed_premium=0.10,
        consumption_shape=_shape_fn(1.0),
        system_price_records=_prices(["2022-01-01"]),
    )
    assert all(r["tariff_type"] == "deemed" for r in result)


# --- MARGIN_REALISM Step 5 (W3_1_price_cap_binding): the Ofgem cap as a
# BINDING constraint on deemed/SVT pricing, not just a lookup ---

def test_deemed_cap_binds_when_spot_plus_premium_exceeds_cap_post_2019():
    """2022 electricity cap is 305.0 GBP/MWh (company/pricing/ofgem_price_cap.py).
    A spot price high enough that spot*(1+premium) exceeds it must be clamped --
    real UK deemed/SVT customers cannot legally be charged above the cap."""
    result = run_deemed_term(
        customer_id="C1",
        term_start_date="2022-01-01",
        term_end_date="2022-01-02",
        deemed_premium=0.10,
        consumption_shape=_shape_fn(2.0),
        system_price_records=_prices(["2022-01-01"], price=1000.0),
        segment="resi",
        commodity="electricity",
    )
    r = result[0]
    assert r["unit_rate_gbp_per_mwh"] == pytest.approx(305.0)
    assert r["cap_bound"] is True
    # Wholesale cost is unaffected by the cap -- the company still buys at spot.
    assert r["wholesale_cost_gbp"] == pytest.approx(1000.0 * (2.0 / 1000.0))


def test_deemed_margin_can_go_negative_once_capped():
    """Real crisis economics: buying at spot, capped on the sell side -- gross
    margin on this settlement period must be able to go negative, exactly the
    mechanism that squeezed real suppliers through 2021-22."""
    result = run_deemed_term(
        customer_id="C1",
        term_start_date="2022-01-01",
        term_end_date="2022-01-02",
        deemed_premium=0.10,
        consumption_shape=_shape_fn(2.0),
        system_price_records=_prices(["2022-01-01"], price=1000.0),
        segment="resi",
        commodity="electricity",
    )
    r = result[0]
    assert r["margin_gbp"] < 0


def test_deemed_uncapped_pre_2019():
    """No Ofgem Default Tariff Cap existed before Q4 2019 -- the same high
    spot price must NOT be clamped for a pre-cap date."""
    result = run_deemed_term(
        customer_id="C1",
        term_start_date="2018-01-01",
        term_end_date="2018-01-02",
        deemed_premium=0.10,
        consumption_shape=_shape_fn(2.0),
        system_price_records=_prices(["2018-01-01"], price=1000.0),
        segment="resi",
        commodity="electricity",
    )
    r = result[0]
    assert r["unit_rate_gbp_per_mwh"] == pytest.approx(1000.0 * 1.10)
    assert r["cap_bound"] is False


def test_deemed_cap_not_applied_to_non_resi_segment():
    """The Ofgem Default Tariff Cap is domestic-only -- an I&C/SME deemed
    period must not be clamped even post-2019."""
    result = run_deemed_term(
        customer_id="C_IC1",
        term_start_date="2022-01-01",
        term_end_date="2022-01-02",
        deemed_premium=0.10,
        consumption_shape=_shape_fn(2.0),
        system_price_records=_prices(["2022-01-01"], price=1000.0),
        segment="I&C",
        commodity="electricity",
    )
    r = result[0]
    assert r["unit_rate_gbp_per_mwh"] == pytest.approx(1000.0 * 1.10)
    assert r["cap_bound"] is False


def test_deemed_gas_commodity_uses_gas_cap_not_electricity_cap():
    """2022 gas cap (95.0 GBP/MWh) is materially different from the 2022
    electricity cap (305.0 GBP/MWh) -- a gas deemed period must clamp against
    the gas table, proving commodity is actually threaded through, not
    defaulted to electricity regardless of the real fuel."""
    result = run_deemed_term(
        customer_id="C1g",
        term_start_date="2022-01-01",
        term_end_date="2022-01-02",
        deemed_premium=0.0,
        consumption_shape=_shape_fn(2.0),
        system_price_records=_prices(["2022-01-01"], price=800.0),
        segment="resi",
        commodity="gas",
    )
    r = result[0]
    assert r["unit_rate_gbp_per_mwh"] == pytest.approx(95.0)
    assert r["cap_bound"] is True


def test_deemed_default_commodity_is_electricity_backward_compatible():
    """commodity defaults to 'electricity' -- every pre-existing caller/test
    that never passed it keeps its exact prior behaviour."""
    result = run_deemed_term(
        customer_id="C1",
        term_start_date="2022-01-01",
        term_end_date="2022-01-02",
        deemed_premium=0.10,
        consumption_shape=_shape_fn(1.0),
        system_price_records=_prices(["2022-01-01"], price=60.0),
    )
    r = result[0]
    assert r["unit_rate_gbp_per_mwh"] == pytest.approx(60.0 * 1.10)
    assert r["cap_bound"] is False
