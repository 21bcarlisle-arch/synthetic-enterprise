"""R15 tests for the W1_3 'show the tail' Dunkelflaute demonstration
(`sim/weather_tail_demonstration.py`).

Covered:
  * ENVELOPE GATE (both directions) -- the healthy calibrated engine reaches the
    real worst winter week; a SMOOTHED engine (no stressed regime, no
    autocorrelation) collapses below it and `assert_tail_not_smoothed` FIRES.
  * JOINT not MARGINAL -- a cold-but-windy or still-but-mild week scores ~0; only
    co-occurring cold AND still scores > 0 (the product metric is the point).
  * WINTER-ONLY -- a non-winter cold-and-still window does not count.
  * THRESHOLDS -- the low winter percentile of the REAL series, applied to both.
  * DETERMINISM (C-S2) -- same seed -> identical demonstration.
  * FAIL-LOUD -- a series with no winter windows raises rather than scoring 0.
"""
from __future__ import annotations

import copy
from datetime import datetime, timedelta

import numpy as np
import pytest

from sim.weather_engine import fit_national_macro_model
from sim.weather_tail_demonstration import (
    TailAnchorMissingError,
    TailDemonstration,
    TailSmoothedError,
    WorstWeek,
    assert_tail_not_smoothed,
    demonstrate_tail,
    derive_thresholds,
    joint_severity,
    load_national_daily,
    worst_winter_week,
)


@pytest.fixture(scope="module")
def real_data():
    return load_national_daily()


# --------------------------------------------------------------------------
# ENVELOPE GATE -- both directions (R15)
# --------------------------------------------------------------------------

def test_healthy_engine_reaches_the_real_worst_week(real_data):
    nat, doy, dates = real_data
    demo = demonstrate_tail(nat, doy, dates, n_sims=25, seed=42)
    # The engine is capable of a winter week at least as severe as the real one.
    assert demo.envelope_reaches_real is True
    assert demo.synthetic_worst_max >= demo.real_worst.severity
    assert demo.real_worst.severity > 0.0  # the real GB tail exists
    assert_tail_not_smoothed(demo)  # does not raise


def test_smoothed_engine_fires_the_gate(real_data):
    nat, doy, dates = real_data
    params = fit_national_macro_model(nat, doy)
    smoothed = copy.deepcopy(params)
    # MUTATION: never enter the stressed regime + kill autocorrelation -> no
    # persistent cold/still spells -> the joint tail is smoothed away.
    smoothed["regime_transition"] = np.array([[1.0, 0.0], [1.0, 0.0]])
    smoothed["cov"]["stressed"] = smoothed["cov"]["standard"]
    for v in smoothed["phi"]:
        smoothed["phi"][v] = 0.0
    demo = demonstrate_tail(nat, doy, dates, n_sims=25, seed=42, macro_params=smoothed)
    assert demo.envelope_reaches_real is False
    with pytest.raises(TailSmoothedError):
        assert_tail_not_smoothed(demo)


def test_autocorrelation_alone_is_load_bearing(real_data):
    """W1_3 headline invariant, ISOLATED (R15 independence): the atom's DoD is
    'temporal autocorrelation is physics not noise -- cold spells and still spells
    LAST'. `test_smoothed_engine_fires_the_gate` mutes phi COMPOUNDED with the
    stressed covariance and the regime transition, so it cannot prove the AR1
    persistence control fires on its OWN named defect (a compound mutation can pass
    on any one lever collapsing -- the killer pattern R15 exists to forbid).

    Here ONLY the autocorrelation is killed (phi -> 0 for every macro var) while
    the stressed season covariance AND regime are left fully intact. A joint
    cold-and-still WEEK requires the residuals to persist across the window; strip
    the persistence and the worst synthetic winter week collapses to ~0 even with
    the coupling untouched -- the envelope can no longer reach the real tail and
    the gate FIRES. This isolates persistence from cross-sectional coupling: both
    are independently necessary, neither is decorative."""
    nat, doy, dates = real_data
    params = fit_national_macro_model(nat, doy)

    # Sanity: the healthy engine (all controls live) reaches the real tail.
    healthy = demonstrate_tail(nat, doy, dates, n_sims=25, seed=42, macro_params=params)
    assert healthy.envelope_reaches_real is True

    no_persistence = copy.deepcopy(params)
    for v in no_persistence["phi"]:
        no_persistence["phi"][v] = 0.0  # ISOLATED: kill autocorrelation ONLY
    # covariance + regime deliberately untouched -- the coupling is still there.
    assert np.array_equal(
        no_persistence["cov"]["stressed"], params["cov"]["stressed"]
    )

    demo = demonstrate_tail(nat, doy, dates, n_sims=25, seed=42, macro_params=no_persistence)
    assert demo.envelope_reaches_real is False
    with pytest.raises(TailSmoothedError):
        assert_tail_not_smoothed(demo)


# --------------------------------------------------------------------------
# JOINT, not two marginals -- the product metric
# --------------------------------------------------------------------------

def _winter_dates(n: int):
    # A run of consecutive January days (all winter).
    start = datetime(2020, 1, 1)
    return [start + timedelta(days=i) for i in range(n)]


def test_cold_but_windy_scores_zero():
    dates = _winter_dates(14)
    temp = np.full(14, -5.0)   # very cold
    wind = np.full(14, 12.0)   # very windy (well above any still threshold)
    sev = joint_severity(temp, wind, dates, temp_thr=0.0, wind_thr=3.0)
    assert np.nanmax(sev) == 0.0  # still_intensity == 0 -> product 0


def test_still_but_mild_scores_zero():
    dates = _winter_dates(14)
    temp = np.full(14, 12.0)    # mild
    wind = np.full(14, 0.5)     # very still
    sev = joint_severity(temp, wind, dates, temp_thr=0.0, wind_thr=3.0)
    assert np.nanmax(sev) == 0.0  # cold_intensity == 0 -> product 0


def test_cold_and_still_scores_positive():
    dates = _winter_dates(14)
    temp = np.full(14, -3.0)    # cold (3 below the 0.0 threshold)
    wind = np.full(14, 1.0)     # still (2 below the 3.0 threshold)
    sev = joint_severity(temp, wind, dates, temp_thr=0.0, wind_thr=3.0)
    assert np.nanmax(sev) == pytest.approx(3.0 * 2.0)  # cold_int * still_int


def test_non_winter_window_does_not_count():
    # A cold-and-still run in July must NOT register (winter-only tail).
    start = datetime(2020, 7, 1)
    dates = [start + timedelta(days=i) for i in range(14)]
    temp = np.full(14, -3.0)
    wind = np.full(14, 1.0)
    sev = joint_severity(temp, wind, dates, temp_thr=0.0, wind_thr=3.0)
    assert np.all(np.isnan(sev))  # every window is non-winter


# --------------------------------------------------------------------------
# Thresholds + determinism + fail-loud
# --------------------------------------------------------------------------

def test_thresholds_are_real_winter_low_percentile(real_data):
    nat, _doy, dates = real_data
    temp_thr, wind_thr = derive_thresholds(nat, dates, percentile=15.0)
    winter = np.array([d.month in (12, 1, 2) for d in dates])
    assert temp_thr == pytest.approx(
        float(np.percentile(nat["temperature_mean_c"][winter], 15.0))
    )
    assert wind_thr == pytest.approx(
        float(np.percentile(nat["wind_speed_mean_ms"][winter], 15.0))
    )


def test_deterministic_same_seed(real_data):
    nat, doy, dates = real_data
    a = demonstrate_tail(nat, doy, dates, n_sims=10, seed=7)
    b = demonstrate_tail(nat, doy, dates, n_sims=10, seed=7)
    assert a.synthetic_worst_severities == b.synthetic_worst_severities
    assert a.real_worst == b.real_worst


def test_real_worst_week_is_a_cold_still_winter_week(real_data):
    nat, _doy, dates = real_data
    temp_thr, wind_thr = derive_thresholds(nat, dates)
    w = worst_winter_week(
        nat["temperature_mean_c"], nat["wind_speed_mean_ms"], dates, temp_thr, wind_thr
    )
    # It is a real winter week that is genuinely both cold and still.
    assert datetime.strptime(w.end_date, "%Y-%m-%d").month in (12, 1, 2)
    assert w.mean_temperature_c <= temp_thr
    assert w.mean_wind_ms <= wind_thr
    assert w.severity > 0.0


def test_zero_real_anchor_fails_loud_not_open():
    # R15 FAIL-OPEN guard: a degenerate demonstration where the REAL series has no
    # cold-and-still tail (severity 0) and a fully-smoothed synthetic tail (also 0)
    # would satisfy `envelope_max >= real_worst.severity` trivially. The gate must
    # REFUSE to certify it, not pass silently.
    zero_anchor = TailDemonstration(
        temp_threshold_c=2.0, wind_threshold_ms=2.5, tail_percentile=15.0,
        real_worst=WorstWeek("2020-01-01", "2020-01-07", 0.0, 5.0, 6.0),
        synthetic_worst_severities=(0.0, 0.0, 0.0), synthetic_worst_median=0.0,
        synthetic_worst_max=0.0, reach_fraction=1.0,
        envelope_reaches_real=True, passes=True, n_sims=3, seed=1,
        simplification_id="x",
    )
    with pytest.raises(TailAnchorMissingError):
        assert_tail_not_smoothed(zero_anchor)


def test_no_winter_windows_raises():
    start = datetime(2020, 7, 1)
    dates = [start + timedelta(days=i) for i in range(30)]
    temp = np.full(30, -3.0)
    wind = np.full(30, 1.0)
    with pytest.raises(ValueError):
        worst_winter_week(temp, wind, dates, temp_thr=0.0, wind_thr=3.0)
