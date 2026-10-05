"""Controls for `sim/grid_carbon_future.py`: the weather-fitted intensity model for generated futures."""
from __future__ import annotations

from dataclasses import replace

import numpy as np
import pytest

from sim import grid_carbon_future as g


def _record(dates, wind, solar, demand, actual):
    return {k: np.asarray(v) for k, v in (("date", dates), ("wind_mw", wind), ("solar_mw", solar),
                                           ("demand_mw", demand), ("actual", actual))}


def _synthetic(era, n, coef=(60.0, -7.0, -4.0, 5.0), noise=0.0, seed=1):
    lo, _ = g.FIT_WINDOWS[era]
    rng = np.random.default_rng(seed)
    wind = rng.uniform(1_000, 18_000, n)
    solar = rng.uniform(0, 10_000, n)
    demand = rng.uniform(16_000, 40_000, n)
    actual = (coef[0] + coef[1] * wind / 1e3 + coef[2] * solar / 1e3 + coef[3] * demand / 1e3
              + rng.normal(0, noise, n))
    dates = np.array([lo] * n)
    return _record(dates, wind, solar, demand, actual)


def test_the_fit_recovers_known_coefficients():
    model = g.fit(g.POST_COAL, _synthetic(g.POST_COAL, g.MIN_FIT_HALF_HOURS))
    assert (model.intercept, model.per_gw_wind, model.per_gw_solar, model.per_gw_demand) == \
        pytest.approx((60.0, -7.0, -4.0, 5.0), abs=1e-6)
    assert model.r_squared == pytest.approx(1.0)


def test_an_era_shorter_than_ninety_days_is_refused_and_says_why():
    with pytest.raises(g.FutureCarbonUnavailable, match="season, not an era"):
        g.fit(g.POST_COAL, _synthetic(g.POST_COAL, g.MIN_FIT_HALF_HOURS - 1))


def test_the_fit_reads_only_its_own_eras_window():
    coal = _synthetic(g.COAL, g.MIN_FIT_HALF_HOURS, coef=(200.0, -10.0, -5.0, 4.0))
    post = _synthetic(g.POST_COAL, g.MIN_FIT_HALF_HOURS, coef=(50.0, -6.0, -3.0, 5.0), seed=2)
    both = {k: np.concatenate([coal[k], post[k]]) for k in coal}
    assert g.fit(g.POST_COAL, both).intercept == pytest.approx(50.0)
    assert g.fit(g.COAL, both).intercept == pytest.approx(200.0)


def test_era_of_splits_at_the_day_after_the_last_coal_station_closed():
    assert g.era_of("2024-09-30") == g.COAL
    assert g.era_of("2024-10-01") == g.POST_COAL
    assert g.era_of("2031-01-15") == g.POST_COAL


def test_the_daily_mean_of_the_model_is_the_model_at_the_daily_means():
    # The reason the form is linear: the world's daily chain and a half-hourly caller agree.
    rng = np.random.default_rng(3)
    w, s, d = rng.uniform(3_000, 12_000, 48), rng.uniform(0, 6_000, 48), rng.uniform(20_000, 35_000, 48)
    assert np.all(g.intensity(w, s, d) > 0), "the fixture must stay off the floor"
    assert g.intensity(w, s, d).mean() == pytest.approx(g.intensity(w.mean(), s.mean(), d.mean()))


def test_the_floor_can_bind_and_is_reported_never_silent():
    # Rare branch first: an input that reaches the floor exists.
    value = g.intensity(25_000, 10_000, 18_000)
    assert value == 0.0
    reasons = g.outside_fitted_range(25_000, 10_000, 18_000)
    assert any("floored at 0" in r for r in reasons)
    assert any(r.startswith("wind ") for r in reasons)


def test_an_input_inside_the_fit_reports_no_extrapolation():
    m = g.FROZEN[g.POST_COAL]
    mid = [1e3 * (lo + hi) / 2 for lo, hi in (m.wind_gw_range, m.solar_gw_range, m.demand_gw_range)]
    assert g.outside_fitted_range(*mid) == []
    assert g.intensity(*mid) > 0


def test_more_wind_or_solar_never_raises_intensity_and_more_demand_never_lowers_it():
    # The physical property, keyed to sign rather than to today's coefficients.
    for era in g.ERAS:
        m = g.FROZEN[era]
        assert m.per_gw_wind < 0 and m.per_gw_solar < 0 and m.per_gw_demand > 0, era


def test_residuals_by_year_grade_against_the_record_not_the_model():
    rec = _synthetic(g.POST_COAL, 200)
    rec["date"] = np.array(["2025-01-01"] * 100 + ["2026-01-01"] * 100)
    rec["actual"] = rec["actual"].copy()
    rec["actual"][100:] += 30.0
    model = replace(g.FROZEN[g.POST_COAL], intercept=60.0, per_gw_wind=-7.0, per_gw_solar=-4.0,
                    per_gw_demand=5.0)
    rows = g.residuals_by_year(model, rec)
    assert rows[2025]["bias"] == pytest.approx(0.0, abs=1e-6)
    assert rows[2026]["bias"] == pytest.approx(30.0)


def test_the_frozen_coefficients_are_what_the_record_refits_to():
    try:
        record = g.load_record()
    except g.FutureCarbonUnavailable as exc:
        pytest.skip(f"real caches absent on this machine: {exc}")
    for era in g.ERAS:
        assert g.fit(era, record) == g.FROZEN[era], (
            f"{era}: the record refits to different coefficients; rerun "
            "`python3 -m sim.grid_carbon_future`, update FROZEN and the docstring's year table")
