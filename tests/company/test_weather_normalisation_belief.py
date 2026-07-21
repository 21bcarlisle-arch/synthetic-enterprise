"""COMPANY-side weather->demand (weather-normalisation) belief tests
(company/pricing/weather_normalisation_belief.py, C13).

The company's belief is a temperature-only HDD/CDD degree-day regression fit on
observables. These tests assert (a) it fits a real degree-day model from observed
history, (b) it is STRUCTURALLY unable to recover a WIND-COUPLED truth -- the form
inadequacy that IS the coupled-triad gap (it cannot see wind chill / the CWV term)
-- and (c) it FAILS LOUD on unusable input rather than returning a silent zero
model.
"""
from __future__ import annotations

import numpy as np
import pytest

from company.pricing.weather_normalisation_belief import (
    HEATING_BASE_TEMP_C,
    InsufficientHistoryError,
    WeatherNormalisationBelief,
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
