"""COMPANY-side weather->price belief tests
(company/pricing/weather_price_belief.py).

The company's belief is a naive LINEAR price ~ gas + temp + wind fit on
observables. These tests assert (a) it fits a real model from observed history,
(b) it is STRUCTURALLY unable to recover a convex truth -- the form inadequacy
that IS the coupled-triad gap -- and (c) it FAILS LOUD on unusable input rather
than returning a silent zero model.
"""
from __future__ import annotations

import numpy as np
import pytest

from company.pricing.weather_price_belief import (
    InsufficientHistoryError,
    WeatherPriceBelief,
    fit_weather_price_belief,
)


def _synthetic_observed(n=400, seed=0):
    rng = np.random.default_rng(seed)
    gas = rng.uniform(20, 80, n)
    temp = rng.uniform(-3, 25, n)
    wind = rng.uniform(1, 11, n)
    # A LINEAR truth the belief CAN recover (used only for the recovery test).
    price = 5.0 + 1.4 * gas - 1.2 * temp - 2.0 * wind + rng.normal(0, 3, n)
    return gas, temp, wind, price


def test_fit_recovers_a_linear_truth():
    gas, temp, wind, price = _synthetic_observed()
    b = fit_weather_price_belief(gas, temp, wind, price)
    assert isinstance(b, WeatherPriceBelief)
    assert b.b_gas == pytest.approx(1.4, abs=0.1)     # positive gas pass-through
    assert b.b_temp < 0                                # colder -> dearer
    assert b.b_wind < 0                                # stiller -> dearer
    assert b.r2 > 0.9                                  # a linear truth is recovered
    pred = b.predict(gas, temp, wind)
    assert np.mean(np.abs(pred - price)) < 5


def test_belief_cannot_recover_a_convex_truth():
    # The epistemic point: a linear belief CANNOT reproduce a convex merit-order
    # spike. Build a convex truth (price jumps once it is cold enough) and show
    # the belief systematically UNDER-predicts the cold tail.
    rng = np.random.default_rng(1)
    n = 800
    gas = rng.uniform(20, 80, n)
    temp = rng.uniform(-3, 25, n)
    wind = rng.uniform(1, 11, n)
    convex = np.clip(2.0 - temp, 0, None) ** 2        # convex heating kink
    price = 5.0 + 1.3 * gas + 4.0 * convex + rng.normal(0, 3, n)
    b = fit_weather_price_belief(gas, temp, wind, price)
    pred = b.predict(gas, temp, wind)
    cold = temp < np.percentile(temp, 10)
    # On the cold tail the linear belief under-predicts the convex spike (negative
    # bias) -- the form inadequacy that is the gap.
    assert np.mean(pred[cold] - price[cold]) < -20


def test_fail_loud_on_unusable_history():
    with pytest.raises(InsufficientHistoryError):
        fit_weather_price_belief([], [], [], [])
    with pytest.raises(InsufficientHistoryError):
        fit_weather_price_belief([1, 2], [1, 2], [1, 2], [1, 2])   # too short
    with pytest.raises(InsufficientHistoryError):
        fit_weather_price_belief([1] * 20, [1] * 20, [1] * 20, [1] * 19)  # mismatch


def test_predict_scalar_and_vector():
    gas, temp, wind, price = _synthetic_observed(n=200)
    b = fit_weather_price_belief(gas, temp, wind, price)
    scalar = b.predict(50.0, 5.0, 6.0)
    assert isinstance(scalar, float)
    vec = b.predict(np.array([50.0, 60.0]), np.array([5.0, 0.0]), np.array([6.0, 3.0]))
    assert vec.shape == (2,)
