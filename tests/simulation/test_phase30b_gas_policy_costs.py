"""Phase 30b: Gas-side policy costs — CCL, GGL, and gas network charges."""

import pytest
from simulation.policy_costs import (
    get_gas_ccl_per_mwh,
    get_gas_network_cost_per_mwh,
    get_ggl_per_mwh,
    _GAS_CCL_RATE_BY_YEAR,
    _GAS_NETWORK_COST_BY_YEAR,
    _GGL_RATE_GBP_PER_METER_YEAR,
)


# --- Gas CCL ---

def test_gas_ccl_2016():
    """2016/17: 0.195 p/kWh = £1.95/MWh — HMRC Table 1."""
    assert get_gas_ccl_per_mwh("2016-06-01", "SME") == pytest.approx(1.95)


def test_gas_ccl_2019_jump():
    """2019/20: £3.39/MWh — Budget 2016 rebalancing policy started."""
    assert get_gas_ccl_per_mwh("2019-06-01", "SME") == pytest.approx(3.39)


def test_gas_ccl_2022():
    """2022/23: £5.68/MWh — HMRC 0.568 p/kWh."""
    assert get_gas_ccl_per_mwh("2022-06-01", "I&C") == pytest.approx(5.68)


def test_gas_ccl_2024_parity():
    """2024/25: £7.75/MWh — parity with electricity CCL (0.775 p/kWh)."""
    assert get_gas_ccl_per_mwh("2024-06-01", "SME") == pytest.approx(7.75)


def test_gas_ccl_resi_exempt():
    """Domestic gas is exempt from CCL — returns 0 for all years."""
    assert get_gas_ccl_per_mwh("2016-01-01", "resi") == 0.0
    assert get_gas_ccl_per_mwh("2022-06-01", "resi") == 0.0
    assert get_gas_ccl_per_mwh("2024-06-01", "resi") == 0.0


def test_gas_ccl_sme_pays():
    """SME pays gas CCL — non-zero for all years."""
    for year_str in ["2016-06-01", "2020-06-01", "2023-06-01"]:
        assert get_gas_ccl_per_mwh(year_str, "SME") > 0.0


def test_gas_ccl_oy_boundary_jan():
    """Jan 2022 → OY 2021/22 → £4.65/MWh (before Apr rebalancing step)."""
    assert get_gas_ccl_per_mwh("2022-01-15", "SME") == pytest.approx(4.65)


def test_gas_ccl_oy_boundary_apr():
    """Apr 2022 → OY 2022/23 → £5.68/MWh."""
    assert get_gas_ccl_per_mwh("2022-04-01", "SME") == pytest.approx(5.68)


def test_gas_ccl_all_years_defined():
    """All OY start years 2016-2024 have gas CCL rates."""
    for year in range(2016, 2025):
        assert year in _GAS_CCL_RATE_BY_YEAR


def test_gas_ccl_clamps_pre_2016():
    """Pre-2016 dates clamp to the 2016 rate."""
    assert get_gas_ccl_per_mwh("2010-01-01", "SME") == pytest.approx(_GAS_CCL_RATE_BY_YEAR[2016])


def test_gas_ccl_clamps_post_2024():
    """Post-2024 dates clamp to the 2024 rate."""
    assert get_gas_ccl_per_mwh("2030-01-01", "SME") == pytest.approx(_GAS_CCL_RATE_BY_YEAR[2024])


def test_gas_ccl_rising_trend():
    """Gas CCL rose from 2019 onward (rebalancing policy)."""
    assert get_gas_ccl_per_mwh("2019-06-01", "SME") > get_gas_ccl_per_mwh("2018-06-01", "SME")
    assert get_gas_ccl_per_mwh("2024-06-01", "SME") > get_gas_ccl_per_mwh("2019-06-01", "SME")


# --- Gas Network Charges ---

def test_gas_network_2016():
    """2016 gas network: ~£9.9/MWh (26% of ~3.8 p/kWh market rate)."""
    assert get_gas_network_cost_per_mwh("2016-06-01") == pytest.approx(9.9)


def test_gas_network_2023_step_up():
    """2023 shows RIIO-GD2 + SOLR cost step-up: £17.6/MWh."""
    assert get_gas_network_cost_per_mwh("2023-06-01") == pytest.approx(17.6)


def test_gas_network_all_years_defined():
    """All OY start years 2016-2024 have gas network cost rates."""
    for year in range(2016, 2025):
        assert year in _GAS_NETWORK_COST_BY_YEAR


def test_gas_network_all_positive():
    """All gas network costs are positive."""
    for year, rate in _GAS_NETWORK_COST_BY_YEAR.items():
        assert rate > 0, f"Year {year} gas network rate {rate} should be positive"


def test_gas_network_clamps_pre_2016():
    assert get_gas_network_cost_per_mwh("2010-01-01") == pytest.approx(_GAS_NETWORK_COST_BY_YEAR[2016])


def test_gas_network_clamps_post_2024():
    assert get_gas_network_cost_per_mwh("2030-01-01") == pytest.approx(_GAS_NETWORK_COST_BY_YEAR[2024])


def test_gas_network_no_segment_exemption():
    """Gas network charge is same for resi and SME — no exemption."""
    assert get_gas_network_cost_per_mwh("2022-06-01") > 0.0


# --- Green Gas Levy ---

def test_ggl_zero_before_nov_2021():
    """GGL did not exist before 30 Nov 2021."""
    aq = 11500
    assert get_ggl_per_mwh("2021-11-29", aq) == 0.0
    assert get_ggl_per_mwh("2020-06-01", aq) == 0.0
    assert get_ggl_per_mwh("2016-01-01", aq) == 0.0


def test_ggl_nov_2021_start():
    """GGL applies from 30 Nov 2021."""
    aq = 11500
    assert get_ggl_per_mwh("2021-11-30", aq) > 0.0


def test_ggl_2022_rate():
    """2022/23: £2.10/year ÷ 11.5 MWh = £0.183/MWh (at AQ 11,500 kWh)."""
    rate = get_ggl_per_mwh("2022-06-01", 11500)
    assert rate == pytest.approx(2.10 / 11.5, rel=0.01)


def test_ggl_2023_drop():
    """2023/24: 0.122 p/day × 365 / 100 = £0.4453/year ÷ 11.5 MWh — fell as fewer projects signed up."""
    rate = get_ggl_per_mwh("2023-06-01", 11500)
    expected = (0.122 * 365 / 100) / 11.5
    assert rate == pytest.approx(expected, rel=0.001)


def test_ggl_lower_in_2023_than_2022():
    """GGL fell sharply from 2022/23 to 2023/24."""
    aq = 11500
    assert get_ggl_per_mwh("2023-06-01", aq) < get_ggl_per_mwh("2022-06-01", aq)


def test_ggl_normalises_correctly_to_daily():
    """ggl_per_mwh × daily_mwh = annual_rate / 365 (invariant regardless of AQ)."""
    aq_kwh = 11500
    daily_mwh = aq_kwh / 365 / 1000
    ggl_per_mwh = get_ggl_per_mwh("2022-06-01", aq_kwh)
    daily_ggl = ggl_per_mwh * daily_mwh
    expected_daily = 2.10 / 365  # annual £2.10 ÷ 365 days
    assert daily_ggl == pytest.approx(expected_daily, rel=0.01)


def test_ggl_zero_for_zero_aq():
    """Zero AQ → zero GGL (avoids division by zero)."""
    assert get_ggl_per_mwh("2022-06-01", 0) == 0.0


# --- Gas settlement integration ---

def test_gas_settlement_records_have_policy_fields():
    """run_gas_term records include gas_ccl_gbp, ggl_gbp, gas_policy_cost_gbp, gas_network_cost_gbp."""
    from simulation.gas_settlement import run_gas_term

    gas_prices = [
        {"settlementDate": "2022-06-01", "systemSellPrice": 100.0},
    ]
    records = run_gas_term(
        customer_id="C1g",
        term_start="2022-06-01",
        term_end="2022-06-02",
        aq_kwh=11500,
        unit_rate_gbp_mwh=120.0,
        hedge_fraction=0.85,
        forward_price=100.0,
        monthly_cost_of_capital_gbp=0.0,
        gas_price_records=gas_prices,
        segment="resi",
    )
    assert len(records) == 1
    rec = records[0]
    assert "gas_ccl_gbp" in rec
    assert "ggl_gbp" in rec
    assert "gas_policy_cost_gbp" in rec
    assert "gas_network_cost_gbp" in rec


def test_resi_gas_ccl_exempt_in_settlement():
    """Resi gas settlement: gas_ccl_gbp == 0 (domestic exempt)."""
    from simulation.gas_settlement import run_gas_term

    gas_prices = [{"settlementDate": "2022-06-01", "systemSellPrice": 100.0}]
    records = run_gas_term(
        "C1g", "2022-06-01", "2022-06-02", 11500, 120.0, 0.85, 100.0, 0.0, gas_prices,
        segment="resi",
    )
    assert records[0]["gas_ccl_gbp"] == pytest.approx(0.0)


def test_gas_network_cost_in_settlement_2022():
    """2022 gas network: £11/MWh × daily_mwh for resi customer (June).

    Phase W: resi gas uses daily HDD shape; compute expected from actual daily_kwh
    in the record rather than the old static monthly profile factor.
    """
    from simulation.gas_settlement import run_gas_term

    aq_kwh = 11500
    gas_prices = [{"settlementDate": "2022-06-01", "systemSellPrice": 100.0}]
    records = run_gas_term(
        "NO_WEATHER_FILE_CID", "2022-06-01", "2022-06-02", aq_kwh, 120.0, 0.85, 100.0, 0.0,
        gas_prices, segment="resi",
    )
    assert records, "Expected at least one settlement record"
    daily_mwh = records[0]["daily_kwh"] / 1000.0
    expected_network = 11.0 * daily_mwh
    assert records[0]["gas_network_cost_gbp"] == pytest.approx(expected_network, rel=0.01)


def test_gas_policy_cost_equals_ccl_plus_ggl():
    """gas_policy_cost_gbp = gas_ccl_gbp + ggl_gbp for each record."""
    from simulation.gas_settlement import run_gas_term

    gas_prices = [{"settlementDate": "2022-06-01", "systemSellPrice": 100.0}]
    records = run_gas_term(
        "C1g", "2022-06-01", "2022-06-02", 11500, 120.0, 0.85, 100.0, 0.0, gas_prices,
        segment="resi",
    )
    rec = records[0]
    assert rec["gas_policy_cost_gbp"] == pytest.approx(rec["gas_ccl_gbp"] + rec["ggl_gbp"])


def test_gas_net_margin_deducts_policy_and_network():
    """net_margin_gbp deducts gas_policy_cost + gas_network_cost from margin."""
    from simulation.gas_settlement import run_gas_term

    gas_prices = [{"settlementDate": "2022-06-01", "systemSellPrice": 100.0}]
    records = run_gas_term(
        "C1g", "2022-06-01", "2022-06-02", 11500, 120.0, 0.85, 100.0, 0.0, gas_prices,
        segment="resi",
    )
    rec = records[0]
    expected_net = rec["margin_gbp"] - rec["gas_policy_cost_gbp"] - rec["gas_network_cost_gbp"]
    assert rec["net_margin_gbp"] == pytest.approx(expected_net, rel=1e-6)


def test_ggl_present_from_nov_2021():
    """GGL appears in settlement records from Nov 2021 onward."""
    from simulation.gas_settlement import run_gas_term

    gas_prices = [{"settlementDate": "2021-11-30", "systemSellPrice": 60.0}]
    records = run_gas_term(
        "C1g", "2021-11-30", "2021-12-01", 11500, 80.0, 0.85, 60.0, 0.0, gas_prices,
        segment="resi",
    )
    assert records[0]["ggl_gbp"] > 0.0


def test_ggl_zero_before_nov_2021_in_settlement():
    """GGL is zero in settlement records before Nov 2021."""
    from simulation.gas_settlement import run_gas_term

    gas_prices = [{"settlementDate": "2021-06-01", "systemSellPrice": 50.0}]
    records = run_gas_term(
        "C1g", "2021-06-01", "2021-06-02", 11500, 70.0, 0.85, 50.0, 0.0, gas_prices,
        segment="resi",
    )
    assert records[0]["ggl_gbp"] == pytest.approx(0.0)
