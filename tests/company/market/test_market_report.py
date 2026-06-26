"""Phase 125: Ofgem market benchmark tests."""

from company.market.market_report import (
    get_market_elec_rate, get_market_gas_rate, get_switching_rate,
    market_benchmark, compare_to_market,
)


def test_elec_rate_2022_crisis():
    assert get_market_elec_rate(2022) == 34.0


def test_gas_rate_rises_then_falls():
    assert get_market_gas_rate(2022) > get_market_gas_rate(2021)
    assert get_market_gas_rate(2023) < get_market_gas_rate(2022)


def test_switching_rate_dropped_in_crisis():
    sr_2022 = get_switching_rate(2022)
    sr_2020 = get_switching_rate(2020)
    assert sr_2022 < sr_2020


def test_market_benchmark_structure():
    b = market_benchmark(2024)
    for k in ("elec_unit_rate_p_kwh", "gas_unit_rate_p_kwh", "switching_rate_pct",
              "elec_annual_gbp_typical", "gas_annual_gbp_typical"):
        assert k in b


def test_market_benchmark_elec_annual_reasonable():
    b = market_benchmark(2024)
    # 24.5p/kWh x 3100 kWh / 100 = £759.50
    assert 500 < b["elec_annual_gbp_typical"] < 1500


def test_compare_above_market():
    result = compare_to_market(30.0, 6.0, 2024)
    assert result["positioning"] == "ABOVE_MARKET"
    assert result["elec_delta_pct"] > 0


def test_compare_below_market():
    result = compare_to_market(20.0, 5.0, 2024)
    assert result["positioning"] == "BELOW_MARKET"


def test_compare_at_market():
    b = market_benchmark(2024)
    result = compare_to_market(b["elec_unit_rate_p_kwh"], b["gas_unit_rate_p_kwh"], 2024)
    assert result["positioning"] == "AT_MARKET"
    assert result["elec_delta_pct"] == 0.0


def test_unknown_year_falls_back_to_2025():
    rate = get_market_elec_rate(2030)
    assert rate == get_market_elec_rate(2025)
