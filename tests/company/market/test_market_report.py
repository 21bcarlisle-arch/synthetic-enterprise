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


def test_elec_rate_pre_crisis_lower_than_2022():
    assert get_market_elec_rate(2020) < get_market_elec_rate(2022)


def test_gas_rate_2016_lowest():
    assert get_market_gas_rate(2016) < get_market_gas_rate(2021)


def test_switching_rate_2016_higher_than_2022():
    assert get_switching_rate(2016) > get_switching_rate(2022)


def test_benchmark_domestic_accounts_crisis_drop():
    # Supplier failures 2021-22 reduced active accounts
    assert _make_benchmark(2022)['domestic_accounts_millions'] < _make_benchmark(2019)['domestic_accounts_millions']


def _make_benchmark(year):
    from company.market.market_report import market_benchmark
    return market_benchmark(year)


def test_compare_gas_delta_above():
    result = compare_to_market(24.5, 10.0, 2024)
    assert result['gas_delta_pct'] > 0


def test_compare_result_keys():
    result = compare_to_market(24.5, 5.8, 2024)
    for k in ('year', 'own_elec_p_kwh', 'market_elec_p_kwh', 'elec_delta_pct',
              'own_gas_p_kwh', 'market_gas_p_kwh', 'gas_delta_pct', 'positioning'):
        assert k in result


def test_benchmark_gas_annual_reasonable():
    b = market_benchmark(2022)
    # 10.3p/kWh x 11500 kWh / 100 = £1184.50
    assert 500 < b['gas_annual_gbp_typical'] < 3000


def test_elec_rate_2022_peak_of_series():
    rates = [get_market_elec_rate(y) for y in range(2016, 2026)]
    assert get_market_elec_rate(2022) == max(rates)


def test_switching_rate_2021_very_low():
    # Crisis onset: suppliers exiting, fewer good deals available
    assert get_switching_rate(2021) < 10.0


def test_compare_just_above_three_pct_threshold():
    # elec_delta > 3 → ABOVE_MARKET
    market_2024 = get_market_elec_rate(2024)  # 24.5
    own_rate = market_2024 * 1.031  # +3.1%
    result = compare_to_market(own_rate, 5.8, 2024)
    assert result['positioning'] == 'ABOVE_MARKET'
