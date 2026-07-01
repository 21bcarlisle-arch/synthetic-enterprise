import pytest

from saas.cost_to_serve import get_bad_debt_rate, BAD_DEBT_RATE, _BAD_DEBT_RATE_BY_YEAR


def test_baseline_years_match_bad_debt_rate():
    for segment in ("resi", "SME"):
        assert get_bad_debt_rate(2019, segment) == BAD_DEBT_RATE[segment]
        assert get_bad_debt_rate(2020, segment) == BAD_DEBT_RATE[segment]


def test_crisis_year_2022_higher_than_baseline():
    assert get_bad_debt_rate(2022, "resi") > get_bad_debt_rate(2020, "resi")
    assert get_bad_debt_rate(2022, "SME") > get_bad_debt_rate(2020, "SME")


def test_2022_resi_rate_is_four_times_baseline():
    assert get_bad_debt_rate(2022, "resi") == pytest.approx(0.080)


def test_2021_resi_is_double_baseline():
    assert get_bad_debt_rate(2021, "resi") == pytest.approx(0.040)


def test_ic_segment_stable_through_crisis():
    assert get_bad_debt_rate(2021, "I&C") == get_bad_debt_rate(2020, "I&C")
    assert get_bad_debt_rate(2022, "I&C") == pytest.approx(0.010)


def test_out_of_range_year_falls_back_to_baseline():
    assert get_bad_debt_rate(2030, "resi") == BAD_DEBT_RATE["resi"]
    assert get_bad_debt_rate(2010, "SME") == BAD_DEBT_RATE["SME"]


def test_unknown_segment_falls_back():
    result = get_bad_debt_rate(2022, "unknown_segment")
    assert result == pytest.approx(0.02)


def test_rates_peak_in_2022_for_resi():
    resi_rates = [get_bad_debt_rate(y, "resi") for y in range(2016, 2025)]
    assert max(resi_rates) == get_bad_debt_rate(2022, "resi")


def test_post_2022_recovery_partial():
    assert get_bad_debt_rate(2023, "resi") < get_bad_debt_rate(2022, "resi")
    assert get_bad_debt_rate(2023, "resi") > get_bad_debt_rate(2020, "resi")


from saas.cost_to_serve import (
    cost_to_serve_for_period,
    FIXED_OVERHEAD_GBP_PER_PERIOD,
    BAD_DEBT_RATE,
    SETTLEMENT_PERIODS_PER_YEAR,
    FIXED_OVERHEAD_GBP_PER_YEAR,
)


def test_cost_to_serve_resi_zero_revenue():
    cts = cost_to_serve_for_period("resi", 0.0)
    assert cts == pytest.approx(FIXED_OVERHEAD_GBP_PER_PERIOD["resi"])


def test_cost_to_serve_sme_zero_revenue():
    cts = cost_to_serve_for_period("SME", 0.0)
    assert cts == pytest.approx(FIXED_OVERHEAD_GBP_PER_PERIOD["SME"])


def test_cost_to_serve_increases_with_revenue():
    low = cost_to_serve_for_period("resi", 10.0)
    high = cost_to_serve_for_period("resi", 100.0)
    assert high > low


def test_cost_to_serve_formula():
    rev = 200.0
    cts = cost_to_serve_for_period("resi", rev)
    expected = FIXED_OVERHEAD_GBP_PER_PERIOD["resi"] + BAD_DEBT_RATE["resi"] * rev
    assert cts == pytest.approx(expected)


def test_fixed_overhead_per_year_to_period_ratio():
    resi_annual = FIXED_OVERHEAD_GBP_PER_YEAR["resi"]
    resi_period = FIXED_OVERHEAD_GBP_PER_PERIOD["resi"]
    assert abs(resi_annual / SETTLEMENT_PERIODS_PER_YEAR - resi_period) < 1e-6
