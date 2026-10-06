"""Cooking and laundry carry HES's season; every other appliance, and a year's total, do not move.

THE DEFECTS EACH TEST NAMES:

  * `test_the_partition_is_reachable_and_each_year_averages_to_one` -- a factor that returns 1.0
    for everything passes every test asking "is the annual mean kept". Both seasonal groups are
    asserted to be above 1 in winter and below 1 in summer FIRST. A factor not normalised to the
    HES annual mean of 1 silently moves annual kWh and the TDCV judgement.
  * `test_only_the_hes_curves_are_seasonal` -- the curve laid on an appliance HES did not curve
    (dishwasher, vacuum/iron), when HES §13.1 measured audiovisual use flat.
  * `test_the_draw_obeys_the_factor` -- a factor computed but never multiplied into the rate.
  * `test_the_trace_hands_the_draw_its_own_month` -- a caller passing a fixed month makes the whole
    season a constant.

Sources: docs/market_research/the_seasonal_swing_of_a_gas_heated_homes_electricity.md.
"""
from __future__ import annotations

import calendar
import datetime as dt

import pytest

import simulation.premise_trace as pt
from tests.simulation.test_premise_trace import make_household

SEASONAL = {"kettle", "toaster", "microwave", "oven", "hob", "washing_machine", "tumble_dryer"}


def _year_mean(name: str, year: int) -> float:
    days = [calendar.monthrange(year, m)[1] for m in range(1, 13)]
    return sum(pt.appliance_season_factor(name, m) * d for m, d in zip(range(1, 13), days)) / sum(days)


def test_the_partition_is_reachable_and_each_year_averages_to_one():
    for name in SEASONAL:
        assert pt.appliance_season_factor(name, 1) > 1.0 > pt.appliance_season_factor(name, 7), name
    for spec in pt.APPLIANCE_CATALOGUE:
        # A leap year's extra February day moves the mean by under 0.1%.
        assert _year_mean(spec.name, 2022) == pytest.approx(1.0, abs=1e-9), spec.name
        assert _year_mean(spec.name, 2024) == pytest.approx(1.0, abs=1e-3), spec.name


def test_only_the_hes_curves_are_seasonal():
    flat = {spec.name for spec in pt.APPLIANCE_CATALOGUE} - SEASONAL
    assert flat == {"dishwasher", "vacuum_iron"}
    for name in flat:
        assert {pt.appliance_season_factor(name, m) for m in range(1, 13)} == {1.0}


def test_the_draw_obeys_the_factor():
    profile = pt.behaviour_profile_for("P-season", make_household(), seed=3)

    def count(month: int, names: set[str]) -> int:
        return sum(
            1
            for day in range(4000)
            for e in pt.draw_appliance_events(11, day, profile, month=month, is_weekend=False, is_away=False)
            if e.name in names
        )

    for names, (winter, summer) in (
        ({"kettle", "toaster", "microwave", "oven", "hob"}, pt._HES_SEASON_DJF_JJA["cooking"]),
        ({"washing_machine", "tumble_dryer"}, pt._HES_SEASON_DJF_JJA["laundry"]),
    ):
        assert count(1, names) / count(7, names) == pytest.approx(winter / summer, rel=0.06), names
    assert count(1, {"dishwasher"}) / count(7, {"dishwasher"}) == pytest.approx(1.0, rel=0.06)


def test_the_trace_hands_the_draw_its_own_month(monkeypatch):
    seen: list[int] = []
    real = pt.appliance_season_factor

    def spy(name: str, month: int) -> float:
        seen.append(month)
        return real(name, month)

    monkeypatch.setattr(pt, "appliance_season_factor", spy)
    weather = pt.load_trace_weather("C1", start=dt.date(2022, 7, 1), end=dt.date(2022, 7, 3))
    pt.generate_premise_trace(
        premise_id="P-month", household=make_household(), weather=weather, seed=1,
        latitude_deg=pt.DEFAULT_LATITUDE_DEG,
    )
    assert seen and set(seen) == {7}
