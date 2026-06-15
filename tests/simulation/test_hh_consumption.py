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
