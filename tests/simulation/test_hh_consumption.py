from saas.customers import get_customer
from simulation.hh_consumption import (
    estimate_annual_kwh,
    hh_shape_fn,
    is_hh_customer,
    load_hh_consumption,
)


def test_is_hh_customer_true_for_c7_c8_c9():
    for cid in ("C7", "C8", "C9"):
        assert is_hh_customer(get_customer(cid))


def test_is_hh_customer_false_for_profile_class_customers():
    for cid in ("C1", "C2", "C3", "C4", "C5", "C6"):
        assert not is_hh_customer(get_customer(cid))


def test_load_hh_consumption_reads_existing_csv():
    consumption = load_hh_consumption("C7")
    assert "2016-01-01" in consumption
    assert len(consumption["2016-01-01"]) == 48
    assert all(isinstance(v, float) for v in consumption["2016-01-01"])


def test_load_hh_consumption_missing_file_returns_empty():
    assert load_hh_consumption("DOES_NOT_EXIST") == {}


def test_hh_shape_fn_returns_consumption_for_known_date():
    consumption = load_hh_consumption("C7")
    shape_fn = hh_shape_fn(consumption)
    assert shape_fn("2016-01-01") == consumption["2016-01-01"]


def test_hh_shape_fn_falls_back_to_zeros_for_unknown_date():
    shape_fn = hh_shape_fn({"2016-01-01": [1.0] * 48})
    assert shape_fn("2099-01-01") == [0.0] * 48


def test_estimate_annual_kwh_extrapolates_daily_mean_to_365_days():
    consumption = {"2016-01-01": [1.0] * 48, "2016-01-02": [1.0] * 48}
    # Daily total = 48 kWh, mean = 48 kWh/day -> * 365
    assert estimate_annual_kwh(consumption) == 48.0 * 365.0


def test_estimate_annual_kwh_empty_returns_zero():
    assert estimate_annual_kwh({}) == 0.0


from simulation.hh_consumption import is_hh_customer, estimate_annual_kwh, hh_shape_fn, PERIODS_PER_DAY


def test_is_hh_customer_requires_metering_hh():
    assert is_hh_customer({"metering": "HH", "customer_id": "C7"}) is True
    assert is_hh_customer({"metering": "smart", "customer_id": "C1"}) is False


def test_is_hh_customer_missing_metering():
    assert is_hh_customer({}) is False


def test_estimate_annual_kwh_single_day():
    consumption = {"2022-01-01": [1.0] * 48}
    # total_kwh = 48.0, n=1, annual = 48 * 365 = 17,520
    result = estimate_annual_kwh(consumption)
    assert abs(result - 48.0 * 365.0) < 1e-6


def test_hh_shape_fn_returns_zeros_for_unknown_date():
    fn = hh_shape_fn({})
    result = fn("2022-01-01")
    assert len(result) == PERIODS_PER_DAY
    assert all(v == 0.0 for v in result)


def test_hh_shape_fn_returns_data_for_known_date():
    data = {"2022-01-01": [2.5] * 48}
    fn = hh_shape_fn(data)
    result = fn("2022-01-01")
    assert result[0] == 2.5


def test_periods_per_day_constant():
    assert PERIODS_PER_DAY == 48
