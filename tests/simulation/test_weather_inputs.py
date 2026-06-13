from saas.customers import get_customer
from simulation.weather_inputs import (
    load_weather_means,
    lookback_mean_temps,
    weather_means_for_customer,
)


def test_load_weather_means_reads_existing_csv():
    means = load_weather_means("C1")
    assert means["2016-01-01"] == 4.6
    assert means["2016-01-02"] == 9.2


def test_load_weather_means_missing_file_returns_empty():
    assert load_weather_means("DOES_NOT_EXIST") == {}


def test_weather_means_for_customer_resolves_shared_location_to_c1():
    # C5 (SME, London) shares C1's exact location dict — no weather file of
    # its own, so it should resolve to C1's.
    c5_means = weather_means_for_customer(get_customer("C5"))
    c1_means = weather_means_for_customer(get_customer("C1"))
    assert c5_means == c1_means
    assert c5_means["2016-01-01"] == 4.6


def test_weather_means_for_customer_resolves_gas_leg_to_electricity_counterpart():
    c2g_means = weather_means_for_customer(get_customer("C2g"))
    c2_means = weather_means_for_customer(get_customer("C2"))
    assert c2g_means == c2_means


def test_lookback_mean_temps_returns_window_before_term_start():
    weather_means = {"2016-01-01": 1.0, "2016-01-02": 2.0, "2016-01-03": 3.0}
    temps = lookback_mean_temps(weather_means, "2016-01-03", lookback_days=2)
    assert sorted(temps) == [1.0, 2.0]


def test_lookback_mean_temps_returns_none_when_window_has_no_data():
    weather_means = {"2020-01-01": 5.0}
    assert lookback_mean_temps(weather_means, "2016-01-03", lookback_days=2) is None
