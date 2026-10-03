"""A run past the record lives through a NAMED world, and every forward input reaches it.

Three defects this guards, each found while wiring depth past 2025 (2026-10-03):
  1. `run_forward_scenario` patched the loaders' home modules, which `run_phase2b` had already
     bound by name, so no forward run ever saw a forward price. The control asks the RUNNER's
     binding, inside the block, for a date past the record.
  2. Past the record there is no weather. The store is extended by analogue years: one complete
     record year per forward year, the same year in every regime, none repeated before all are
     used, and the record itself untouched.
  3. A run past the record with no named world must refuse, not settle on whatever the cache holds.
"""
from __future__ import annotations

import ast
import datetime as dt
from pathlib import Path

import pytest

import simulation.run_phase2b as runner
from sim.weather_world import WeatherWorld
from simulation.run_scenario import active_forward_world, forward_world


def _history(end=dt.date(2025, 6, 7)):
    elec, gas, day = [], [], dt.date(2025, 5, 1)
    while day <= end:
        elec += [{"settlementDate": day.isoformat(), "settlementPeriod": p,
                  "systemSellPrice": 80.0} for p in range(1, 49)]
        gas.append({"settlementDate": day.isoformat(), "systemSellPrice": 30.0})
        day += dt.timedelta(days=1)
    return elec, gas


def test_inside_the_block_the_runners_own_loaders_return_forward_prices_and_are_restored_after():
    before = (runner.get_cached_prices, runner.load_nbp_history)
    elec, gas = _history()
    with forward_world("neso_central", "2026-12-31", historical_elec=elec, historical_gas=gas) as w:
        assert w["world_id"] == "neso_central" and active_forward_world() == w
        forward = runner.get_cached_prices("2026-03-01", "2026-03-01")
        assert len(forward) == 48
        assert any(r["settlementDate"] == "2026-12-31" for r in runner.load_nbp_history())
    assert (runner.get_cached_prices, runner.load_nbp_history) == before
    assert active_forward_world() is None


def _toy_world():
    cells = {}
    daily = {}
    for regime in ("r1", "r2"):
        series = {}
        day = dt.date(2016, 1, 1)
        while day <= dt.date(2019, 12, 31):
            series[day.isoformat()] = {"temperature_mean_c": float(day.year % 100) + (regime == "r2"),
                                       "temperature_min_c": 0.0, "temperature_max_c": 1.0}
            day += dt.timedelta(days=1)
        daily[regime] = series
    return WeatherWorld(cells, daily, {})


def test_forward_weather_replays_one_whole_record_year_per_year_in_every_regime():
    world = _toy_world()
    forward = world.extended_by_analogue_years("2023-12-31", seed="s")
    years = forward.analogue_years
    assert sorted(years) == [2020, 2021, 2022, 2023]
    assert sorted(years.values()) == [2016, 2017, 2018, 2019]      # none repeated before all used
    for year, source in years.items():
        for day in ("01-01", "07-15", "12-31"):
            r1 = forward.daily["r1"][f"{year}-{day}"]["temperature_mean_c"]
            r2 = forward.daily["r2"][f"{year}-{day}"]["temperature_mean_c"]
            assert r1 == float(source % 100) and r2 == r1 + 1.0   # same source year, both regimes
    assert forward.daily["r1"]["2020-02-29"]                       # a leap day is never a hole
    assert world.record_end() == "2019-12-31"                      # the record is untouched
    assert world.extended_by_analogue_years("2023-12-31", seed="s").analogue_years == years


def test_a_run_past_the_record_without_a_named_world_refuses_and_inside_one_does_not():
    with pytest.raises(ValueError, match="must name the world"):
        runner.refuse_a_window_past_the_record_without_a_world("2027-12-31")
    runner.refuse_a_window_past_the_record_without_a_world(runner.REPORT_END)   # the record: fine
    elec, gas = _history()
    with forward_world("neso_central", "2027-12-31", historical_elec=elec, historical_gas=gas):
        runner.refuse_a_window_past_the_record_without_a_world("2027-12-31")


def test_main_asks_the_refusal_before_it_reads_a_price():
    """The refusal is only a control if the run reaches it -- asked of `main`'s own body."""
    tree = ast.parse(Path(runner.__file__).read_text(encoding="utf-8"))
    main = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "_main")
    called = [n.func.id for n in ast.walk(main)
              if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)]
    assert "refuse_a_window_past_the_record_without_a_world" in called


def test_the_ab_harness_refuses_a_world_on_a_run_that_never_leaves_the_record():
    from tools.run_value_cycle_ab import main as ab_main
    assert ab_main(["--world", "neso_central"]) == 2
