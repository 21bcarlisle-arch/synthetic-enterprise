"""Tests for simulation/triad.py -- Phase 27d / MT."""

import pytest

from simulation.triad import (
    _TRIAD_ALERT_SSP_THRESHOLD,
    _IC_TRIAD_RESPONSE_REDUCTION,
    _triad_year,
    build_triad_alert_set,
    compute_triad_exposure,
    get_tnuos_tariff,
    identify_triad_candidates,
    make_triad_aware_shape_fn,
)


# --- _triad_year ---

def test_triad_year_november():
    assert _triad_year("2021-11-15") == 2021


def test_triad_year_december():
    assert _triad_year("2021-12-01") == 2021


def test_triad_year_january():
    # Jan 2022 belongs to winter 2021-22
    assert _triad_year("2022-01-20") == 2021


def test_triad_year_february():
    assert _triad_year("2022-02-28") == 2021


# --- get_tnuos_tariff ---

def test_get_tnuos_tariff_2022():
    assert get_tnuos_tariff(2022) == pytest.approx(58.93)


def test_get_tnuos_tariff_future_falls_back_to_max():
    assert get_tnuos_tariff(2030) == pytest.approx(get_tnuos_tariff(2024))


def test_get_tnuos_tariff_past_falls_back_to_min():
    assert get_tnuos_tariff(2010) == pytest.approx(get_tnuos_tariff(2016))


# --- build_triad_alert_set ---

def test_build_triad_alert_set_fires_in_season_high_ssp():
    records = [{"settlementDate": "2021-11-15", "settlementPeriod": 35, "systemSellPrice": 90.0}]
    alerts = build_triad_alert_set(records)
    assert ("2021-11-15", 35) in alerts


def test_build_triad_alert_set_no_alert_low_ssp():
    records = [{"settlementDate": "2021-11-15", "settlementPeriod": 35, "systemSellPrice": 70.0}]
    alerts = build_triad_alert_set(records)
    assert len(alerts) == 0


def test_build_triad_alert_set_no_alert_summer():
    records = [{"settlementDate": "2022-06-15", "settlementPeriod": 35, "systemSellPrice": 150.0}]
    alerts = build_triad_alert_set(records)
    assert len(alerts) == 0


def test_build_triad_alert_set_no_alert_wrong_period():
    # SP 20 is not a risk period (risk = SP 33-39)
    records = [{"settlementDate": "2021-11-15", "settlementPeriod": 20, "systemSellPrice": 150.0}]
    alerts = build_triad_alert_set(records)
    assert len(alerts) == 0


# --- make_triad_aware_shape_fn ---

def test_make_triad_aware_shape_reduces_alerted_period():
    alert_set = frozenset([("2021-12-01", 35)])
    base_fn = lambda d: [1.0] * 48
    shaped_fn = make_triad_aware_shape_fn(base_fn, alert_set)
    shape = shaped_fn("2021-12-01")
    # SP35 is index 34 (0-indexed), should be reduced by 25%
    assert shape[34] == pytest.approx(1.0 * (1.0 - _IC_TRIAD_RESPONSE_REDUCTION))


def test_make_triad_aware_shape_no_effect_on_non_alerted():
    alert_set = frozenset([("2021-12-01", 35)])
    base_fn = lambda d: [2.0] * 48
    shaped_fn = make_triad_aware_shape_fn(base_fn, alert_set)
    shape = shaped_fn("2021-12-01")
    # All other periods should be unchanged
    assert shape[0] == pytest.approx(2.0)
    assert shape[47] == pytest.approx(2.0)


def test_make_triad_aware_shape_other_dates_unaffected():
    alert_set = frozenset([("2021-12-01", 35)])
    base_fn = lambda d: [3.0] * 48
    shaped_fn = make_triad_aware_shape_fn(base_fn, alert_set)
    shape = shaped_fn("2021-12-02")
    assert all(v == pytest.approx(3.0) for v in shape)
