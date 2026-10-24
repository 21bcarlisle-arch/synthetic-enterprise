"""A dual-fuel household that moves with us takes its gas leg too, on the same date (home_moves.md s.8.7).

One run of the real loop to 2017-12-31 with moves on, the company offering on every notice its rule
passes, and the world answering at k = 1. Before this build every follower's gas leg ended at the
move, so the household arrived electricity-only wherever it went (the 17 Oct ruling: households move
as households). Measured on 2026-10-24 to 2018-12-31: of 9 households supplied at a new home, 4 took
their gas and 2 arrived electricity-only at a home with no mains gas; the rest had no gas leg.
"""
from __future__ import annotations

import dataclasses

import pytest

import simulation.run_phase2b as run
from company.policy.decision_policy import CURRENT_POLICY, policy_scope
from sim import weather_hdd
from sim.weather_hdd import hdd_reading
from simulation.weather_inputs import cell_weather_for_customer

REPORT_END = "2017-12-31"


@pytest.fixture(scope="module")
def followed(tmp_path_factory):
    patch = pytest.MonkeyPatch()
    patch.setattr(run, "moves_active", lambda: True)
    patch.setattr(run, "move_with_us_active", lambda: True)
    patch.setattr(run, "take_up_scale", lambda: 1.0)
    policy = dataclasses.replace(CURRENT_POLICY, move_with_us_offers=True)
    # Each gas leg's sky as the run starts, from the same door the HDD leg resolves through.
    before_run = {c["customer_id"]: dict(cell_weather_for_customer(c).series)
                  for c in run.GAS_CUSTOMERS}
    try:
        with policy_scope(policy):
            result = run.main(report_end=REPORT_END, policy=policy,
                              gap_ledger_path=tmp_path_factory.mktemp("g") / "gap_ledger.json")
        # Read before tests/conftest.py puts the book back: the sky each followed leg ends on.
        result["_skies"] = {
            r["billing_account"] + "g": (r["move_out_date"], before_run[r["billing_account"] + "g"],
                                 dict(weather_hdd._premise_sky(r["billing_account"] + "g").series),
                                 hdd_reading(r["move_out_date"], r["billing_account"] + "g").basis)
            for r in result["move_with_us_log"] if r.get("gas_leg_follows")}
        yield result
    finally:
        patch.undo()


def _gas_rows(result, household):
    return [r for r in result["account_state_log"] if r["customer_id"] == household + "g"]


def test_both_answers_are_reachable(followed):
    """Defect: the gas leg never follows (the old rule), or follows into a home with no gas meter.
    Both branches must be taken in this window before either is asserted on."""
    supplied = [r for r in followed["move_with_us_log"] if r.get("supplied_at_new_home")]
    assert {r.get("gas_leg_follows") for r in supplied} >= {True, False}, supplied


def test_a_followed_gas_leg_is_supplied_past_the_move_and_a_refused_one_is_not(followed):
    """Defect: the follow recorded while the gas term is still cut at the move (or the reverse)."""
    for r in followed["move_with_us_log"]:
        if r.get("gas_leg_follows") is None:
            continue
        rows = _gas_rows(followed, r["billing_account"])
        past = [a for a in rows if a["term_end"][:10] > r["move_out_date"]]
        assert bool(past) is r["gas_leg_follows"], (r, rows)
        if not r["gas_leg_follows"]:
            assert r["destination_takes_gas"] is False, r


def test_a_followed_gas_leg_reads_the_new_cell_from_the_move_date(followed):
    """Defect: the gas leg moves on paper and goes on burning the old home's weather."""
    assert followed["_skies"]
    for moved_on, old, now, basis in followed["_skies"].values():
        assert {d: t for d, t in now.items() if d < moved_on} == {
            d: t for d, t in old.items() if d < moved_on}, "the past was re-read at the new home"
        after = [d for d in now if d >= moved_on]
        assert after and any(now[d] != old.get(d) for d in after), "the old sky kept after the move"
        assert "from it" in basis and "before " + moved_on in basis, basis
