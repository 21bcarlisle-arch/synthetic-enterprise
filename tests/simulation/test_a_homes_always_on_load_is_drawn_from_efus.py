"""W1_29: every world home drew the same 25 W always-on load, so no world home had the large,
persistent base that makes the calmest tenth of real homes calm.

The defect this names: a constant shared by every home where EFUS 2011 measured a median of 90 W
and a mean of 136 W across 79 gas-heated homes, and Low Carbon London's base loads run from about
16 W to 224 W between its p10 and p90.
"""
from __future__ import annotations

import datetime as dt
import random
import statistics

import pytest

from simulation import fabric_physics as fp
from simulation import premise_trace as pt
from tests.simulation.test_premise_trace import make_household


def test_the_draw_reproduces_efus_median_and_mean():
    draws = [pt.always_on_kw(seed) for seed in range(20000)]
    assert statistics.median(draws) == pytest.approx(0.090, abs=0.003)
    assert statistics.mean(draws) == pytest.approx(0.136, abs=0.006)
    assert len({round(d, 6) for d in draws[:200]}) == 200, "homes must differ"


def test_the_ceiling_can_be_reached_and_holds(monkeypatch):
    # The ceiling is taken rarely: the fitted lognormal puts about 1.4 in 10,000 homes above it.
    capped = sum(pt.always_on_kw(seed) == pt._ALWAYS_ON_CEILING_KW for seed in range(20000))
    assert capped <= 10

    class _Top(random.Random):
        def random(self):
            return 1.0 - 1e-15

    monkeypatch.setattr(pt, "_substream", lambda *a, **k: _Top())
    assert pt.always_on_kw(1) == pt._ALWAYS_ON_CEILING_KW


def test_the_always_on_load_moves_the_meter_by_exactly_itself():
    """One variable: the held standby shifts every half-hour by the same energy and nothing else."""
    weather = pt.load_trace_weather("C1", start=dt.date(2022, 1, 1), end=dt.date(2022, 1, 14))

    def meter(standby_kw):
        trace = pt.generate_premise_trace(
            premise_id="P-base", household=make_household(), weather=weather, seed=3,
            latitude_deg=fp.latitude_for_weather_site("C1"), standby_kw=standby_kw,
        )
        return [v for day in trace.half_hourly("electricity") for v in day]

    low, high = meter(pt.UNIFORM_STANDBY_KW), meter(0.200)
    step = (0.200 - pt.UNIFORM_STANDBY_KW) * pt.PERIOD_HOURS
    assert all(h - lo == pytest.approx(step, abs=1e-9) for lo, h in zip(low, high))
    drawn = meter(None)
    own = pt.always_on_kw(pt._base_seed_for("P-base", 3))
    assert drawn[0] - low[0] == pytest.approx((own - pt.UNIFORM_STANDBY_KW) * pt.PERIOD_HOURS)
