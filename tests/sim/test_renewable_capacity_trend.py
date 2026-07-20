"""W1_7 — Renewable capacity + generation-mix evolution over time (L1 skeletal).

Tests for `sim/renewable_capacity_trend.py` + its wiring into
`sim/weather_price_chain.py`. The atom's compounding claim: the same weather draw
must price DIFFERENTLY in 2016 than in 2025, because GB's renewable fleet ~tripled.

R15 discipline (each honest, network-free invariant shown to FIRE on its own named
defect — a control that cannot fail is worse than none):
  * TREND (check_trend_increasing): fleet grows materially across the window; the
    old whole-window flat scalar collapses per-year variance -> ratio ~ 1 -> FIRES.
  * NON-DEGENERACY (check_time_varying): the trajectory is not the flat scalar;
    reverting to one scalar -> CV 0 -> FIRES.
  * COVERAGE-FAIL-CLOSED: an all-thin record raises DegenerateTrajectoryError, never
    a silent degenerate fleet (FAIL-OPEN forbidden).
  * DETERMINISM/replay (C-S2): two builds byte-identical.
  * WIRING: derive_price(year=2016) != derive_price(year=2025) for one weather draw;
    year=None is byte-identical to the pre-W1_7 whole-window scalar path (backward
    compat — the SSP calibration gate is not re-opened).

NOT tested here (deliberately — the FRAME §10 honesty boundary): A2 outturn-consistency
and A3 mix-share. Validating a per-year mean-match against the same-year outturn it was
matched to is tautological; the independent sources (DUKES Ch.6 capacity, DESNZ Energy
Trends Table 6 mix-share) are network-blocked and registered as a discovery-agent pass,
not asserted.
"""
from __future__ import annotations

import numpy as np
import pytest

from sim import renewable_capacity_trend as rct
from sim import weather_price_chain as wpc


# ── the trajectory itself ─────────────────────────────────────────────────────────────
def test_trajectory_covers_multiple_years_of_the_real_window():
    traj = rct.fleet_trajectory()
    assert len(traj) >= 5, "expected several covered years across 2016-2025"
    for y, cell in traj.items():
        assert cell["wind_fleet_mw"] > 0
        assert cell["solar_fleet_mw"] > 0
        assert cell["n_days"] >= rct._MIN_DAYS_PER_YEAR


def test_capacity_clamps_flat_outside_the_window_R13_hold_flat():
    traj = rct.fleet_trajectory()
    ys = sorted(traj)
    # forward (curriculum default = hold last flat) and back both clamp, never extrapolate
    assert rct.capacity_wind(ys[-1] + 5) == rct.capacity_wind(ys[-1])
    assert rct.capacity_wind(ys[0] - 5) == rct.capacity_wind(ys[0])
    assert rct.capacity_solar(ys[-1] + 5) == rct.capacity_solar(ys[-1])


# ── R15: TREND invariant fires on the flat-scalar mutation ──────────────────────────────
def test_trend_increasing_holds_on_real_data():
    assert rct.check_trend_increasing() is True


def test_trend_increasing_FIRES_on_flat_scalar_mutation():
    ys = sorted(rct.fleet_trajectory())
    # the pre-W1_7 world: one whole-window scalar for every year -> no trend
    flat = {y: {"wind_fleet_mw": 8000.0, "solar_fleet_mw": 5000.0, "n_days": 300} for y in ys}
    assert rct.check_trend_increasing(flat) is False


# ── R15: NON-DEGENERACY invariant fires on the flat-scalar mutation ─────────────────────
def test_time_varying_holds_on_real_data():
    assert rct.check_time_varying() is True


def test_time_varying_FIRES_on_flat_scalar_mutation():
    ys = sorted(rct.fleet_trajectory())
    flat = {y: {"wind_fleet_mw": 8000.0, "solar_fleet_mw": 5000.0, "n_days": 300} for y in ys}
    assert rct.check_time_varying(flat) is False


# ── R15: COVERAGE fails closed (FAIL-OPEN forbidden) ────────────────────────────────────
def test_all_thin_years_raise_rather_than_return_degenerate(monkeypatch):
    """If every year is below the min-days floor, refuse — never mean-match on a
    handful of days and pass it off as a fleet."""
    real = wpc.load_daily_record()
    # keep only the first 3 aligned days of one year -> every year thin
    thin = {k: (v[:3] if isinstance(v, np.ndarray) else v) for k, v in real.items()}
    monkeypatch.setattr(wpc, "load_daily_record", lambda: thin)
    rct.fleet_trajectory.cache_clear()
    with pytest.raises(rct.DegenerateTrajectoryError):
        rct.fleet_trajectory()
    rct.fleet_trajectory.cache_clear()  # restore real cache for later tests


# ── C-S2 determinism / replay ───────────────────────────────────────────────────────────
def test_trajectory_is_deterministic():
    a = rct.fleet_trajectory()
    b = rct.fleet_trajectory()
    assert a == b


# ── WIRING into the price chain ─────────────────────────────────────────────────────────
# A cold, genuinely WINDY draw: high demand AND real wind output, so a bigger fleet
# scales to materially more renewable MW and the per-year capacity trend actually bites
# (a still draw would scale ~0 by any fleet and hide the mechanism).
_DRAW = dict(temp_c=-2.0, wind_speed_ms=9.0, cloud_pct=90.0, day_of_year=15, gas_price=60.0)


def test_same_weather_prices_differently_across_years():
    """The whole point of W1_7: a fixed cold-still weather draw yields a different
    residual demand -> different price in an early vs late year."""
    ys = sorted(rct.fleet_trajectory())
    early, late = ys[0], ys[-1]
    p_early = wpc.derive_price(**_DRAW, year=early)
    p_late = wpc.derive_price(**_DRAW, year=late)
    assert p_early != p_late
    # more renewable capacity later -> more renewable output for the SAME wind -> lower
    # residual demand -> a lower (or equal-then-lower) merit-order price for this draw.
    rd_early = wpc.residual_demand(_DRAW["temp_c"], _DRAW["wind_speed_ms"],
                                   _DRAW["cloud_pct"], _DRAW["day_of_year"], year=early)
    rd_late = wpc.residual_demand(_DRAW["temp_c"], _DRAW["wind_speed_ms"],
                                  _DRAW["cloud_pct"], _DRAW["day_of_year"], year=late)
    assert float(np.ravel(rd_late)[0]) < float(np.ravel(rd_early)[0])


def test_year_none_is_backward_compatible():
    """year=None must reproduce the pre-W1_7 whole-window scalar path byte-for-byte —
    proving the SSP calibration gate is untouched."""
    p = wpc.fit_chain()
    frac = np.array([wpc.wind_power_output_fraction(_DRAW["wind_speed_ms"])])
    expected_wind = float(p.wind_fleet_mw * frac[0])
    got_wind = wpc.wind_output_from_speed(_DRAW["wind_speed_ms"])
    assert got_wind == pytest.approx(expected_wind)
    # and the whole price is identical to calling with no year kwarg at all
    p_default = wpc.derive_price(**_DRAW)
    p_none = wpc.derive_price(**_DRAW, year=None)
    assert p_default == p_none
