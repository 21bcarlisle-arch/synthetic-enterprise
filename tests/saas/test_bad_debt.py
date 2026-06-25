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
