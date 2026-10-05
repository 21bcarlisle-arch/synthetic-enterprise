"""B7 slice 2: with home moves on, the run stops supplying a mover at the move date.

One short run (2016 only, about a minute and a half) with the curriculum switch forced on. The
unit tests in `tests/sim/test_customer_state_layer.py` cannot see whether the run asks the layer at
all; this is the control that goes red if the call site is removed and every unit test stays green.
"""
from __future__ import annotations

import datetime as dt

import pytest

import simulation.run_phase2b as run


@pytest.fixture(scope="module")
def moved_run():
    patch = pytest.MonkeyPatch()
    patch.setattr(run, "moves_active", lambda: True)
    try:
        yield run.main(report_end="2016-12-31")
    finally:
        patch.undo()


def test_the_run_draws_moves_when_the_layer_is_on(moved_run):
    """Defect: the layer switched on and never asked -- the CoT stack's state for months."""
    assert moved_run["home_move_outs"]


def test_a_movers_supply_ends_on_the_move_date_and_never_resumes(moved_run):
    """Defect: the move recorded while the account goes on being billed past it, or a term lost."""
    rows = moved_run["account_state_log"]
    for move in moved_run["home_move_outs"]:
        moved = dt.date.fromisoformat(move["move_date"])
        own = [r for r in rows if r["customer_id"] == move["customer_id"]]
        assert [r for r in own if r["term_end"][:10] == move["move_date"]], move
        assert not [r for r in own if dt.date.fromisoformat(r["term_start"][:10]) >= moved], move


def test_a_move_is_the_one_churn_the_journey_calls_uncatchable(moved_run):
    """Defect: the move leaves the journey on a funnel state, so churn recall is scored on it."""
    assert {(m["journey_state"], m["catchable"]) for m in moved_run["home_move_outs"]} == {
        ("home_move_churned", False)}


def test_a_business_account_never_moves_home(moved_run):
    """Defect: the domestic hazard applied to an I&C or SME site."""
    segment = {c["customer_id"]: c.get("segment", "resi") for c in run._ALL_KNOWN_CUSTOMERS}
    assert {segment.get(m["household"], "resi") for m in moved_run["home_move_outs"]} == {"resi"}
