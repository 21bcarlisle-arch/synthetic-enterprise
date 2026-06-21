from datetime import date, timedelta

from sim.weather_price_sensitivity import COLD_SPELL_PRICE_MULTIPLIER
from simulation.run_phase2b import (
    DEFAULT_PROPERTY,
    REPORT_END,
    _build_gas_renewal_schedule,
    _clamp_term_end,
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


def test_clamp_term_end_uses_default_report_end():
    # With no end_date kwarg the default REPORT_END is used — verify it returns a date string
    result = _clamp_term_end("2016-01-01")
    assert isinstance(result, str) and len(result) == 10


def test_clamp_term_end_truncates_to_custom_end_date():
    short_end = "2018-06-30"
    result = _clamp_term_end("2018-01-01", end_date=short_end)
    # Contract is 365 days; term end = 2019-01-01, which is beyond 2018-06-30 — should clamp
    assert result == "2018-07-01"  # end_date + 1 day (exclusive upper bound convention)


def test_clamp_term_end_does_not_truncate_when_natural_end_is_within_window():
    long_end = "2025-12-31"
    result = _clamp_term_end("2016-01-01", end_date=long_end)
    # Natural end ~2017-01-01 is well inside the window — no truncation
    assert result < long_end


def test_build_gas_renewal_schedule_truncates_on_report_end():
    records = _flat_gas_price_records("2015-01-01", "2022-12-31")
    customer = {"aq_kwh": 12000, "acquisition_date": "2016-01-01"}

    short_end = "2017-06-30"
    schedule = _build_gas_renewal_schedule(customer, records, report_end=short_end)

    # All terms must start on or before short_end
    for term in schedule:
        assert term["acquisition_date"] <= short_end

    # Full-window schedule should have more terms
    full_schedule = _build_gas_renewal_schedule(customer, records)
    assert len(full_schedule) > len(schedule)


# Phase 12e: _compute_company_divergence tests

def test_compute_company_divergence_groups_by_year():
    from simulation.run_phase2b import _compute_company_divergence
    basis_risk = [
        {"term_start": "2021-01-01", "tariff_error_pct": 0.20},
        {"term_start": "2021-07-01", "tariff_error_pct": -0.30},
        {"term_start": "2022-01-01", "tariff_error_pct": 0.50},
    ]
    churn_risk = [
        {"term_start": "2021-01-01", "churn_estimate_error_pct": 0.10},
        {"term_start": "2022-01-01", "churn_estimate_error_pct": -0.40},
    ]
    result = _compute_company_divergence(basis_risk, churn_risk)
    tariff = result["tariff_error_by_year"]
    churn = result["churn_error_by_year"]

    assert "2021" in tariff
    assert "2022" in tariff
    assert tariff["2021"]["n"] == 2
    # mean abs error for 2021: (0.20 + 0.30) / 2 = 0.25
    assert abs(tariff["2021"]["mean_abs_error_pct"] - 0.25) < 0.001
    assert tariff["2021"]["max_abs_error_pct"] == 0.30
    assert tariff["2022"]["n"] == 1
    assert tariff["2022"]["mean_abs_error_pct"] == 0.50

    assert "2021" in churn
    assert "2022" in churn
    assert churn["2021"]["n"] == 1
    assert abs(churn["2021"]["mean_abs_error_pct"] - 0.10) < 0.001


def test_compute_company_divergence_skips_none_churn_errors():
    from simulation.run_phase2b import _compute_company_divergence
    churn_risk = [
        {"term_start": "2020-01-01", "churn_estimate_error_pct": None},
        {"term_start": "2020-07-01", "churn_estimate_error_pct": 0.15},
    ]
    result = _compute_company_divergence([], churn_risk)
    churn = result["churn_error_by_year"]
    assert "2020" in churn
    assert churn["2020"]["n"] == 1  # None entry skipped


def test_compute_company_divergence_empty_inputs():
    from simulation.run_phase2b import _compute_company_divergence
    result = _compute_company_divergence([], [])
    assert result["tariff_error_by_year"] == {}
    assert result["churn_error_by_year"] == {}
