"""L2.4: a home's active use was drawn independently of its always-on load, so the world's
between-home size was the always-on draw alone and its p90/p10 sat at 2.97 against LCL's 5.38.

The defect this names: a home that leaves 300 W on all night using its lights, screens and
washing machine exactly as a home leaving 30 W on does. In Low Carbon London the slope of
ln(mean - base) on ln(base) is 0.46; this world's was 0.11 at the same estimator.
"""
from __future__ import annotations

import datetime as dt

import pytest

from simulation import fabric_physics as fp
from simulation import premise_trace as pt
from tests.simulation.test_premise_trace import make_household


def test_the_multiplier_is_one_at_the_median_and_rises_with_the_always_on_load():
    assert pt.active_use_multiplier(pt._ALWAYS_ON_MEDIAN_KW) == pytest.approx(1.0)
    low, high = pt.active_use_multiplier(0.030), pt.active_use_multiplier(0.300)
    assert low < 1.0 < high
    assert high / low == pytest.approx(10.0 ** pt._ACTIVE_USE_BETA)


def test_drawn_homes_land_on_both_sides_of_the_median():
    """The coupling must be able to shrink a home as well as grow it: a multiplier that only
    ever exceeded 1 would pass every test below and inflate the whole world."""
    multipliers = [
        pt.active_use_multiplier(pt.always_on_kw(pt._base_seed_for(f"P{i:04d}", 7)))
        for i in range(200)
    ]
    assert min(multipliers) < 0.7 and max(multipliers) > 1.4


def _meter(**kw):
    weather = pt.load_trace_weather("C1", start=dt.date(2022, 1, 1), end=dt.date(2022, 1, 14))
    trace = pt.generate_premise_trace(
        premise_id="P-active", household=make_household(), weather=weather, seed=3,
        latitude_deg=fp.latitude_for_weather_site("C1"), **kw,
    )
    return sum(v for day in trace.half_hourly("electricity") for v in day)


def test_active_use_moves_the_meter_at_a_held_always_on_load():
    """One variable: same home, same standby, active use doubled. The meter must rise."""
    held = pt.UNIFORM_STANDBY_KW
    assert _meter(standby_kw=held, active_use=2.0) > _meter(standby_kw=held, active_use=1.0) * 1.2


def test_by_default_the_active_use_is_the_multiplier_of_the_standby_in_force():
    """Absent `active_use`, the trace couples to the standby: a held 300 W home is the same
    as a 300 W home told its multiplier, and differs from one held at 1.0."""
    coupled = _meter(standby_kw=0.300)
    assert coupled == pytest.approx(_meter(standby_kw=0.300, active_use=pt.active_use_multiplier(0.300)))
    assert coupled > _meter(standby_kw=0.300, active_use=1.0)
