"""The oven and hob start on HES's hours, not uniformly from 16:00 to 21:00.

HES (Intertek R66141, 2012) Figs 432-433 and 440-441: the oven peaks at 17:00 and puts 0.358 of its
day in 18:00-24:00; the hob peaks at 18:00 at 0.410. Until 2026-10-09 the world started both
uniformly in 16:00-21:30, which put 0.6-0.7 of their energy after 18:00 and none before 16:00.
docs/staging/SEAT_FINDING_THE_EVENING_COOKING_HOUR_AGAINST_HES_2026-10-09.md.
"""

import datetime as dt

import pytest

import simulation.premise_trace as pt
from simulation.premise_population import draw_premise_from_joint

_ALL = frozenset(s.name for s in pt.APPLIANCE_CATALOGUE)


def _spec(name: str) -> pt.ApplianceSpec:
    return next(s for s in pt.APPLIANCE_CATALOGUE if s.name == name)


def _curve_share(curve, lo_hour: int, hi_hour: int) -> float:
    return sum(curve[lo_hour:hi_hour]) / sum(curve)


def _world_hourly(name: str, homes: int = 40, days: int = 120) -> list[float]:
    """The appliance's energy by hour of day, summed over drawn homes' days, from its own events."""
    load = [0.0] * pt.PERIODS_PER_DAY
    for i in range(homes):
        pid = f"SYN-S{i:04d}"
        hh = draw_premise_from_joint(pid, base_seed=17, as_of=dt.date(2022, 1, 1)).household
        if not hh.is_residential:
            continue
        profile = pt.behaviour_profile_for(pid, hh, seed=17)
        for d in range(days):
            for e in pt.draw_appliance_events(
                17 + i, d, profile, month=1 + d % 12, is_weekend=d % 7 >= 5, is_away=False, owned=_ALL,
            ):
                if e.name == name:
                    pt._spread_event(e, load)
    return [load[2 * h] + load[2 * h + 1] for h in range(24)]


@pytest.mark.parametrize("name", ["oven", "hob"])
def test_the_appliance_carries_hes_load_curve(name):
    # Defect it catches: the oven or hob drawn uniformly in an evening window again.
    assert _spec(name).load_by_hour is not None


@pytest.mark.parametrize("name", ["oven", "hob", "dishwasher"])
def test_the_worlds_evening_share_is_within_the_rule_of_hes(name):
    # Defect it catches: a curve that is carried but not reached (a window that still clips it, or
    # a start drawn uniformly). The pre-registered rule: share 18:00-24:00 within 0.10 of HES's.
    curve = _spec(name).load_by_hour
    world = _world_hourly(name)
    assert sum(world) > 0, f"{name}: no energy drawn, so the share below would test nothing"
    assert _curve_share(world, 18, 24) == pytest.approx(_curve_share(curve, 18, 24), abs=0.10)


@pytest.mark.parametrize("name", ["oven", "hob"])
def test_a_meal_can_be_cooked_before_four(name):
    # The rare branch the old window made unreachable: HES puts 0.38 of each before 16:00.
    world = _world_hourly(name)
    assert _curve_share(world, 0, 16) > 0.20
