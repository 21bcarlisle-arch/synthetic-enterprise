"""The retention cutoff can read the desk belief calibrated on the company's own closed renewals.

Defect named: a fixed 0.30 cutoff compares against a belief whose LEVEL a policy switch moved
(candidate A's ending-term conditioning), so the population the cutoff admits moves with the belief's
level and not with anything the cut was set for (`THE_VALUE_TEST_REDESIGN.md` §12c, §12e). Candidate 2
puts the cutoff on the book's own scale: observed over expected on the cutoff's belief, closed years.
Knowledge: `docs/market_research/a_save_offer_against_the_switching_rules_and_the_seam.md` §11g.
"""
from __future__ import annotations

import ast
import dataclasses
import inspect

import simulation.run_phase2b as run_phase2b
from company.crm.competitive_pressure import CompetitivePressureLedger, pressure_ledger_scope
from company.interfaces.growth_desk import RETENTION_THRESHOLD, retention_cutoff_belief
from company.policy.decision_policy import CURRENT_POLICY, DecisionPolicy


def _ledger_with_2017_closed(losses: int, n: int = 200, belief: float = 0.30):
    ledger = CompetitivePressureLedger()
    ledger.arm_loss_reporting()
    for i in range(n):
        retention_cutoff_belief_booked(ledger, 2017, f"A-{i}", belief)
        if i < losses:
            ledger.observe_competitive_loss(2017, account_id=f"A-{i}")
    return ledger


def retention_cutoff_belief_booked(ledger, year, acct, belief):
    with pressure_ledger_scope(ledger):
        retention_cutoff_belief(belief, calibrate=True, account_id=acct, renewal_year=year)


def _read(ledger, belief, *, calibrate, year=2018, acct="Z-1"):
    with pressure_ledger_scope(ledger):
        return retention_cutoff_belief(belief, calibrate=calibrate, account_id=acct, renewal_year=year)


def test_every_branch_of_the_calibration_can_be_taken():
    """One control over the whole partition. Reds if the switch is ignored (the belief never moves on
    a learned ledger), if it leaks when off (a belief moves, or a renewal is booked, with it off), or
    if calibration moves the level the wrong way: the book's losses under the belief must pull it down
    and losses over it must push it up, the §12e read being the first and the twin-scale cut the
    second."""
    low, high = _ledger_with_2017_closed(losses=24), _ledger_with_2017_closed(losses=120)
    off_before = dict(low.cutoff_belief_sums)
    off = _read(low, 0.12, calibrate=False)
    assert off == (0.12, "the cutoff reads the belief as given")
    assert low.cutoff_belief_sums == off_before and "Z-1" not in low.pending_cutoff_by_account

    down, why_down = _read(low, 0.12, calibrate=True)
    up, _ = _read(high, 0.12, calibrate=True)
    assert down < 0.12 < up
    assert "24 losses against 60.00 predicted on 200 closed renewals" in why_down

    unclosed, why = _read(low, 0.12, calibrate=True, year=2017, acct="Z-2")
    assert (unclosed, why) == (0.12, "no closed renewals booked against the cutoff's belief")
    assert retention_cutoff_belief(0.12, calibrate=True, account_id="Z-3", renewal_year=2018) == (
        0.12, "no pressure ledger in scope")


def test_a_loss_is_attributed_to_the_renewal_that_booked_the_account():
    ledger = CompetitivePressureLedger()
    ledger.arm_loss_reporting()
    retention_cutoff_belief_booked(ledger, 2017, "A-1", 0.2)
    ledger.observe_competitive_loss(2017, account_id="A-1")
    ledger.observe_competitive_loss(2017, account_id="A-1")  # a second report finds nothing pending
    assert ledger.cutoff_belief_sums[2017] == {"n": 1, "sp": 0.2, "losses": 1}


def test_the_switch_is_off_on_the_standing_policy_and_the_run_loop_reads_it():
    field = "retention_cutoff_reads_the_calibrated_belief"
    assert {f.name: f.default for f in dataclasses.fields(DecisionPolicy)}[field] is False
    assert getattr(CURRENT_POLICY, field) is False
    tree = ast.parse(inspect.getsource(run_phase2b))
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
             and getattr(n.func, "id", None) == "retention_cutoff_belief"]
    assert len(calls) == 1
    assert getattr({k.arg: k.value for k in calls[0].keywords}["calibrate"], "attr", None) == field
    considers = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
                 and getattr(n.func, "id", None) == "retention_considers_the_renewal"]
    assert getattr(considers[0].args[0], "id", None) == "_cutoff_belief"


def test_the_cut_has_one_home_with_its_origin():
    assert run_phase2b.RETENTION_THRESHOLD is RETENTION_THRESHOLD == 0.30
    from tools.domain_constant_origins import scan  # noqa: PLC0415
    rows = [r for r in scan() if r["name"] == "RETENTION_THRESHOLD"]
    assert rows and all(r["origin"] == "simplification" for r in rows), rows
