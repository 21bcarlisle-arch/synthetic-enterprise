"""COMPANY-side weather->demand (weather-normalisation) belief tests
(company/pricing/weather_normalisation_belief.py, C13).

The company's belief is a temperature-only HDD/CDD degree-day regression fit on
observables (L1). These tests assert (a) it fits a real degree-day model from
observed history, (b) it is STRUCTURALLY unable to recover a WIND-COUPLED truth --
the form inadequacy that IS the coupled-triad gap (it cannot see wind chill / the
CWV term) -- and (c) it FAILS LOUD on unusable input rather than returning a
silent zero model.

L2 additions (below): the WIND-CHILL (CWV) term genuinely recovers wind-coupled
structure the L1 temperature-only fit cannot (R15 independence: same synthetic
truth generator, different fit machinery -- if the L2 fit could NOT beat L1 here,
the wind term would be theatre); FAIL-LOUD on a wind-fitted belief predicted
without wind (no silent FAIL-OPEN degrade); and `book_weighted_temperature`, the
regional-dispersion input transform, tested for both its guard rails and its
synthetic-truth discrimination effect.
"""
from __future__ import annotations

import numpy as np
import pytest

from company.pricing.weather_normalisation_belief import (
    HEATING_BASE_TEMP_C,
    InsufficientHistoryError,
    InvalidRegionWeightsError,
    MissingWindObservableError,
    WeatherNormalisationBelief,
    book_weighted_temperature,
    fit_weather_normalisation_belief,
)


def _hdd(t):
    return np.clip(HEATING_BASE_TEMP_C - t, 0.0, None)


def _synthetic_degree_day(n=600, seed=0):
    rng = np.random.default_rng(seed)
    temp = rng.uniform(-3, 25, n)
    hdd = _hdd(temp)
    cdd = np.clip(temp - 18.0, 0.0, None)
    # A degree-day truth the belief CAN recover (used only for the recovery test).
    demand = 24000.0 + 750.0 * hdd + 500.0 * cdd + rng.normal(0, 300, n)
    return temp, demand


def test_fit_recovers_a_degree_day_truth():
    temp, demand = _synthetic_degree_day()
    b = fit_weather_normalisation_belief(temp, demand)
    assert isinstance(b, WeatherNormalisationBelief)
    assert b.b_hdd == pytest.approx(750.0, abs=60)     # heating sensitivity recovered
    assert b.b_cdd == pytest.approx(500.0, abs=120)    # cooling sensitivity recovered
    assert b.b_hdd > 0                                  # colder -> more demand
    assert b.r2 > 0.9                                   # a degree-day truth is recovered
    pred = b.predict(temp)
    assert np.mean(np.abs(pred - demand)) < 500


def test_belief_cannot_recover_a_wind_coupled_truth():
    # The epistemic point: a temperature-only degree-day belief CANNOT reproduce a
    # WIND-COUPLED truth (real heat loss rises with wind on cold days -- the CWV
    # term). Build a truth with a wind-chill term and show the belief systematically
    # UNDER-predicts the cold-AND-windy days -- the form inadequacy that is the gap.
    rng = np.random.default_rng(1)
    n = 1200
    temp = rng.uniform(-3, 25, n)
    wind = rng.uniform(1, 12, n)
    hdd = _hdd(temp)
    # Wind chill: extra heat loss proportional to HDD * (wind above a light breeze).
    windchill = hdd * np.clip(wind - 4.0, 0.0, None) * 45.0
    demand = 24000.0 + 750.0 * hdd + windchill + rng.normal(0, 300, n)
    b = fit_weather_normalisation_belief(temp, demand)
    pred = b.predict(temp)
    cold = temp < np.percentile(temp, 25)
    windy = wind > np.median(wind)
    mask = cold & windy
    # On the cold-and-windy subset the temperature-only belief under-predicts the
    # wind-chill spike (negative bias) -- it cannot see wind, by the wall.
    assert np.mean(pred[mask] - demand[mask]) < -200
    # And it over-predicts the cold-and-CALM subset (the missed wind term is
    # smeared into the average HDD coefficient) -- the mirror of the same blindness.
    calm = wind <= np.median(wind)
    assert np.mean(pred[cold & calm] - demand[cold & calm]) > 0


def test_fail_loud_on_unusable_history():
    with pytest.raises(InsufficientHistoryError):
        fit_weather_normalisation_belief([], [])
    with pytest.raises(InsufficientHistoryError):
        fit_weather_normalisation_belief([1, 2], [1, 2])           # too short
    with pytest.raises(InsufficientHistoryError):
        fit_weather_normalisation_belief([1] * 20, [1] * 19)       # mismatch


def test_predict_scalar_and_vector():
    temp, demand = _synthetic_degree_day(n=200)
    b = fit_weather_normalisation_belief(temp, demand)
    scalar = b.predict(5.0)
    assert isinstance(scalar, float)
    vec = b.predict(np.array([5.0, 20.0]))
    assert vec.shape == (2,)
    # Colder day -> higher predicted demand (heating).
    assert b.predict(0.0) > b.predict(15.0)


# ---------------------------------------------------------------------------
# L2: wind-chill (CWV) term
# ---------------------------------------------------------------------------

def _synthetic_wind_coupled(n=1200, seed=1):
    rng = np.random.default_rng(seed)
    temp = rng.uniform(-3, 25, n)
    wind = rng.uniform(1, 12, n)
    hdd = _hdd(temp)
    windchill = hdd * np.clip(wind - 4.0, 0.0, None) * 45.0
    demand = 24000.0 + 750.0 * hdd + windchill + rng.normal(0, 300, n)
    return temp, wind, demand


def test_wind_aware_fit_recovers_a_wind_coupled_truth():
    # R15 independence: SAME synthetic truth as
    # test_belief_cannot_recover_a_wind_coupled_truth (the L1 fit structurally
    # fails it) -- the L2 wind-aware fit is DIFFERENT machinery (a 4th OLS
    # regressor) and must genuinely recover it, not by construction of the test.
    temp, wind, demand = _synthetic_wind_coupled()
    b = fit_weather_normalisation_belief(temp, demand, wind_speed_ms=wind)
    assert b.has_wind_term is True
    assert b.b_hdd == pytest.approx(750.0, abs=100)
    assert b.b_windchill == pytest.approx(45.0, abs=10)   # the CWV coefficient recovered
    assert b.r2 > 0.9

    pred = b.predict(temp, wind_speed_ms=wind)
    cold = temp < np.percentile(temp, 25)
    windy = wind > np.median(wind)
    mask = cold & windy
    # Unlike the L1 temp-only belief (systematic negative bias on this cell,
    # asserted in test_belief_cannot_recover_a_wind_coupled_truth), the
    # wind-aware belief is UNBIASED here -- it can see the wind-chill load.
    assert abs(np.mean(pred[mask] - demand[mask])) < 200


def test_wind_none_reproduces_l1_exactly():
    # Regression safety by construction: fitting WITHOUT wind_speed_ms must be
    # byte-for-byte the L1 3-parameter fit -- same coefficients as calling the
    # (unchanged) 2-arg form.
    temp, demand = _synthetic_degree_day(n=300)
    b_default = fit_weather_normalisation_belief(temp, demand)
    b_explicit_none = fit_weather_normalisation_belief(temp, demand, wind_speed_ms=None)
    assert b_default.has_wind_term is False
    assert b_default.b_windchill == 0.0
    assert b_default.base == b_explicit_none.base
    assert b_default.b_hdd == b_explicit_none.b_hdd
    assert b_default.b_cdd == b_explicit_none.b_cdd
    # predict() ignores a wind arg entirely when the belief has no wind term --
    # passing one changes nothing (further regression safety).
    assert b_default.predict(5.0) == b_default.predict(5.0, wind_speed_ms=999.0)


def test_predict_fails_loud_without_wind_when_fitted_with_wind():
    # R15 mutation-provable: if the has_wind_term guard in predict() were
    # removed/neutered, this test fails (silently returns a wrong prediction
    # instead of raising) -- proving the FAIL-LOUD control actually fires.
    temp, wind, demand = _synthetic_wind_coupled(n=300, seed=2)
    b = fit_weather_normalisation_belief(temp, demand, wind_speed_ms=wind)
    with pytest.raises(MissingWindObservableError):
        b.predict(5.0)
    with pytest.raises(MissingWindObservableError):
        b.predict(np.array([5.0, 10.0]))
    # A belief WITHOUT a wind term never raises (no false positive -- the
    # control targets the real defect only).
    b_no_wind = fit_weather_normalisation_belief(temp, demand)
    b_no_wind.predict(5.0)   # no raise


def test_wind_fit_requires_more_history_than_temp_only():
    temp, wind, demand = _synthetic_wind_coupled(n=15, seed=3)
    # n=15 is enough for the 3-parameter temp-only fit (min 10)...
    fit_weather_normalisation_belief(temp, demand)
    # ...but not enough for the 4-parameter wind-aware fit (min 20).
    with pytest.raises(InsufficientHistoryError):
        fit_weather_normalisation_belief(temp, demand, wind_speed_ms=wind)


def test_wind_length_mismatch_fails_loud():
    temp, wind, demand = _synthetic_wind_coupled(n=100, seed=4)
    with pytest.raises(InsufficientHistoryError):
        fit_weather_normalisation_belief(temp, demand, wind_speed_ms=wind[:-5])


# ---------------------------------------------------------------------------
# L2: book-weighted (regional-dispersion) temperature
# ---------------------------------------------------------------------------

def test_book_weighted_temperature_is_the_weighted_average():
    region_a = np.array([0.0, 10.0, 20.0])
    region_b = np.array([10.0, 20.0, 30.0])
    out = book_weighted_temperature(
        {"A": region_a, "B": region_b}, {"A": 0.75, "B": 0.25})
    expected = 0.75 * region_a + 0.25 * region_b
    np.testing.assert_allclose(out, expected)


def test_book_weighted_temperature_rejects_mismatched_keys():
    with pytest.raises(InvalidRegionWeightsError):
        book_weighted_temperature({"A": [1.0]}, {"B": 1.0})


def test_book_weighted_temperature_rejects_weights_not_summing_to_one():
    with pytest.raises(InvalidRegionWeightsError):
        book_weighted_temperature({"A": [1.0], "B": [2.0]}, {"A": 0.5, "B": 0.6})


def test_book_weighted_temperature_rejects_negative_weight():
    with pytest.raises(InvalidRegionWeightsError):
        book_weighted_temperature({"A": [1.0], "B": [2.0]}, {"A": 1.5, "B": -0.5})


def test_book_weighted_temperature_rejects_mismatched_lengths():
    with pytest.raises(InvalidRegionWeightsError):
        book_weighted_temperature(
            {"A": [1.0, 2.0], "B": [1.0, 2.0, 3.0]}, {"A": 0.5, "B": 0.5})


def test_regional_dispersion_belief_beats_national_only_on_a_skewed_book():
    # The regional-dispersion story, built honestly on SYNTHETIC truth (real
    # per-book demand truth is not available inside this atom's file_scope --
    # a registered R10 limit, see module docstring). National temperature and
    # two PUBLISHED regional series (offsets from national, standing in for two
    # real published regional feeds); the company's book is 90% concentrated in
    # the colder region A.
    rng = np.random.default_rng(7)
    n = 800
    national_temp = rng.uniform(-3, 25, n)
    region_a = national_temp - 4.0     # colder region
    region_b = national_temp + 2.0     # warmer region
    book_weights = {"A": 0.9, "B": 0.1}
    book_true_temp = book_weighted_temperature(
        {"A": region_a, "B": region_b}, book_weights)

    hdd_book = _hdd(book_true_temp)
    cdd_book = np.clip(book_true_temp - 18.0, 0.0, None)
    demand = 24000.0 + 750.0 * hdd_book + 500.0 * cdd_book + rng.normal(0, 200, n)

    # A "nationally-normalised" belief: fit blind to the book's regional skew,
    # against the national mean temperature.
    b_national = fit_weather_normalisation_belief(national_temp, demand)
    pred_national = b_national.predict(national_temp)
    mae_national = float(np.mean(np.abs(pred_national - demand)))

    # A book-weighted belief: fit against the SAME public regional feeds
    # combined with the company's OWN book weights.
    book_input_temp = book_weighted_temperature(
        {"A": region_a, "B": region_b}, book_weights)
    b_book = fit_weather_normalisation_belief(book_input_temp, demand)
    pred_book = b_book.predict(book_input_temp)
    mae_book = float(np.mean(np.abs(pred_book - demand)))

    # The book-weighted belief discriminates the regional skew the
    # nationally-normalised belief cannot see -- materially lower error.
    assert mae_book < mae_national * 0.5
    assert b_book.b_hdd == pytest.approx(750.0, abs=80)
