"""B8 / director ruling 2: the funnel-sourced decision set. One control per way it can mislead:

  1. it cannot see option 1 -- the defect the draw-sourced set had: switch off and on built
     byte-identical sets, so P4's control was the same run as arm I;
  2. a winner is re-id'd on the way in, so the elasticity the funnel selected on is redrawn;
  3. the walk never takes its rare branches (onto the default, back off it, out from it), so
     `days_on_default` and `ever_actively_renewed` are constants that read like observables;
  4. the three positions do not cross to the company, or cross with world truth beside them.
"""
from __future__ import annotations

import json

import pytest

from company.interfaces.sim_interface import (
    HOLDOUT_OBSERVABLE_FIELDS,
    holdout_decision_observations,
)
from simulation import coin_drawn_decision_set as cds

SEED = 101


def _switch(monkeypatch, tmp_path, on: bool, level: str = "independent"):
    import simulation.population_draw as pd

    src = json.loads(pd.ACQUISITION_RESPONSIVENESS_PATH.read_text(encoding="utf-8"))
    src["activated"]["value"], src["sensitivity_level_draw"]["value"] = on, level
    path = tmp_path / f"switch_{on}_{level}.json"
    path.write_text(json.dumps(src), encoding="utf-8")
    monkeypatch.setattr(pd, "ACQUISITION_RESPONSIVENESS_PATH", path)


def _accounts(monkeypatch, tmp_path, on: bool) -> list[str]:
    _switch(monkeypatch, tmp_path, on)
    return sorted(c.customer_id for c, route in cds.campaign_households(SEED)
                  if route == cds.ROUTE_CAMPAIGN_WIN)


def test_option_one_changes_which_households_the_set_holds(monkeypatch, tmp_path):
    """Defect 1. Off and on must give different won books; were they equal, the grade's control
    and its treated arm would be one run."""
    off = _accounts(monkeypatch, tmp_path, False)
    on = _accounts(monkeypatch, tmp_path, True)
    assert off and on
    assert off != on, "option 1 reaches no household of the funnel-sourced set"


@pytest.fixture(scope="module")
def funnel_set():
    return cds.build_funnel_decision_set(SEED, cut_gbp_per_mwh=7.5)


def test_a_winner_keeps_the_id_its_traits_are_keyed_on(funnel_set):
    """Defect 2. A re-prefixed winner carries a fresh elasticity draw, erasing the selection."""
    won = {r["account"] for r in funnel_set.rows if r["acquisition_route"] == cds.ROUTE_CAMPAIGN_WIN}
    assert won and all(a.startswith("PROS-") for a in won)


def test_the_walk_reaches_every_position_it_reports(funnel_set):
    """Defect 3, asserted as one partition: a household that has rolled onto the default and come
    back off it, one that has renewed actively and one that never has must all reach a decision."""
    rows = funnel_set.rows
    # A campaign win opens on a fix, so only the roll-off can put it on the default; a move-in's
    # days there would satisfy a leg asked of the whole set without the roll-off ever running.
    assert any(r["days_on_default"] > 0 for r in rows
               if r["acquisition_route"] == cds.ROUTE_CAMPAIGN_WIN)
    assert {r["ever_actively_renewed"] for r in rows} == {True, False}
    assert {r["active_renewal"] for r in rows} == {True, False}
    assert all(r["days_on_default"] % 365 == 0 for r in rows)


def test_a_household_on_the_default_can_leave_on_the_inertia_hazard():
    """Defect 3, the exit that has no row: a year on the default must be able to end the walk."""
    c, _route = next((c, r) for c, r in cds.campaign_households(SEED))
    import datetime as dt

    with cds.world_seed(SEED), cds.registered([c]):
        start = dt.date(2019, 1, 1)
        p, _departs = cds.default_year_departs(c, start, start)
    assert 0.0 < p < 1.0


def test_the_company_sees_the_three_positions_and_no_truth(funnel_set):
    """Defect 4."""
    seen = holdout_decision_observations(funnel_set.rows)
    for k in ("acquisition_route", "days_on_default", "ever_actively_renewed"):
        assert k in HOLDOUT_OBSERVABLE_FIELDS
    assert all(set(r) == set(HOLDOUT_OBSERVABLE_FIELDS) for r in seen)
    assert not {"p_stay_holdout", "p_stay_treated", "roll", "active_renewal"} & set(HOLDOUT_OBSERVABLE_FIELDS)
