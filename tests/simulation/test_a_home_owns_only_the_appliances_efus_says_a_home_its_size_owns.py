"""W1_29: every world home owned the whole stock, so homes differed only in headcount and clock.

The defect this names: a dishwasher, tumble dryer and separate freezer in every home, where EFUS
puts them in 44%, 58% and 38% of homes, and far fewer of the one-person ones.
"""
from __future__ import annotations

import datetime as dt

import pytest

from simulation import fabric_physics as fp
from simulation import premise_trace as pt
from tests.simulation.test_premise_trace import make_household

N = 4000


def _share(name: str, people: int) -> float:
    return sum(name in pt.owned_stock(seed, people) for seed in range(N)) / N


@pytest.mark.parametrize("people, dishwasher, tumble_dryer", [(1, 0.19, 0.49), (4, 0.60, 0.70), (7, 0.48, 0.65)])
def test_ownership_follows_efus_by_household_size(people, dishwasher, tumble_dryer):
    assert _share("dishwasher", people) == pytest.approx(dishwasher, abs=0.025)
    assert _share("tumble_dryer", people) == pytest.approx(tumble_dryer, abs=0.025)
    assert _share("freezer", people) == pytest.approx(0.382, abs=0.025)


def test_both_sides_of_every_draw_are_reachable_and_nothing_else_is_drawn():
    stocks = [pt.owned_stock(seed, 2) for seed in range(400)]
    for name in ("dishwasher", "tumble_dryer", "freezer"):
        assert any(name in s for s in stocks) and any(name not in s for s in stocks), name
    drawn = {"dishwasher", "tumble_dryer", "freezer"}
    assert all(s >= pt.FULL_STOCK - drawn for s in stocks)


def test_an_unowned_appliance_never_runs_and_the_owned_ones_replay_exactly():
    profile = pt.behaviour_profile_for("P-stock", make_household(), seed=3)
    without = pt.FULL_STOCK - {"dishwasher", "tumble_dryer"}
    for day in range(200):
        kwargs = dict(month=1 + day % 12, is_weekend=day % 7 >= 5, is_away=False)
        full = pt.draw_appliance_events(5, day, profile, owned=pt.FULL_STOCK, **kwargs)
        some = pt.draw_appliance_events(5, day, profile, owned=without, **kwargs)
        assert some == [e for e in full if e.name in without]


def test_a_home_without_a_separate_freezer_hums_less_and_owns_a_fridge_freezer_still():
    weather = pt.load_trace_weather("C1", start=dt.date(2022, 1, 1), end=dt.date(2022, 1, 14))

    def cold(owned):
        trace = pt.generate_premise_trace(
            premise_id="P-cold", household=make_household(), weather=weather, seed=3,
            latitude_deg=fp.latitude_for_weather_site("C1"), owned=owned,
        )
        return sum(sum(d.cold_appliance_kwh) for d in trace.days)

    full, no_freezer = cold(pt.FULL_STOCK), cold(pt.FULL_STOCK - {"freezer"})
    assert 0.0 < no_freezer < full
