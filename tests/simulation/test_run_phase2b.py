from datetime import date, timedelta

from sim.weather_price_sensitivity import COLD_SPELL_PRICE_MULTIPLIER
from simulation.run_phase2b import (
    DEFAULT_PROPERTY,
    _build_gas_renewal_schedule,
    _weather_adjusted_shape_fn,
)


def _flat_base_shape(date_str):
    return [1.0] * 48


def test_weather_adjusted_shape_fn_falls_back_without_weather_data():
    shape_fn = _weather_adjusted_shape_fn(_flat_base_shape, {}, DEFAULT_PROPERTY)
    assert shape_fn("2016-01-01") == [1.0] * 48


def test_weather_adjusted_shape_fn_adds_heating_load_on_cold_day():
    weather_means = {"2016-01-01": -5.0}  # well below 15.5C heating base
    shape_fn = _weather_adjusted_shape_fn(_flat_base_shape, weather_means, DEFAULT_PROPERTY)

    cold_shape = shape_fn("2016-01-01")
    assert sum(cold_shape) > sum(_flat_base_shape("2016-01-01"))


def _flat_gas_price_records(start_date: str, end_date: str, price: float = 50.0) -> list[dict]:
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)
    records = []
    current = start
    while current <= end:
        records.append({"settlementDate": current.isoformat(), "systemSellPrice": price})
        current += timedelta(days=1)
    return records


def test_build_gas_renewal_schedule_cold_spell_raises_forward_price():
    records = _flat_gas_price_records("2015-10-01", "2017-06-30")
    customer = {"aq_kwh": 12000, "acquisition_date": "2016-01-01"}

    no_weather = _build_gas_renewal_schedule(
        {**customer, "acquisition_date": "2016-01-01"}, records
    )

    def cold_lookback(term_start):
        return [0.0] * 90

    with_cold_weather = _build_gas_renewal_schedule(
        {**customer, "acquisition_date": "2016-01-01"}, records, lookback_temps_fn=cold_lookback
    )

    ratio = (
        with_cold_weather[0]["forward_price_gbp_per_mwh"]
        / no_weather[0]["forward_price_gbp_per_mwh"]
    )
    assert ratio == COLD_SPELL_PRICE_MULTIPLIER
