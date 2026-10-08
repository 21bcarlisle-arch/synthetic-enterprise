"""A save on the Invitation to Intervene must never be paid for by raising a stayer's price
(director, 2026-10-08). Controls, one per way it can mislead:

  1. the save's thinner margin reaches the portfolio premium every later renewal is priced on, so
     the stayers pay for it -- measured on 2026-10-08 before the guard existed;
  2. the household's answer to a save is a coin of ours, not the world's own roll at the save price;
  3. the comparison of stayers' prices cannot see a move;
  4. a household the company knows to be vulnerable (its own disclosure register) is offered less
     than a household in the same position that is not -- a higher save price, or no offer at all.

THE PAIR. Two runs of the real loop to 2018-09-30 that save the same households, decided by the
world at the save's price. `on` bills them the save; `placebo` bills them the renewal. So the book
holds the same households and only the save's price differs: any stayer whose price differs between
the two is paying for the save. CSS did not exist in 2017, so the Invitation's go-live gate is
opened for this test; the response is scaled up so saves happen in a short window, which changes
who is saved and not how a saved term is priced.

WHY 2018-09-30 AND NOT EARLIER (measured 2026-10-08, the guard deleted): to 2018-03-31 the only saved
term that ended was a gas term, released into a gas premium already at its floor, so it moved
nothing and the control could not fail; the first saved ELECTRICITY term ends 2018-06-20, and from
the next day the deleted guard moved 131 stayer account-terms by year end.
"""
from __future__ import annotations

import dataclasses

import pytest

import simulation.registration_loss_feed as feed
import simulation.run_phase2b as run
from company.policy.decision_policy import CURRENT_POLICY, policy_scope
from simulation.coin_drawn_decision_set import saved_on_loss_notice
from simulation.save_on_loss_notice import household_takes_save
from tools.save_on_loss_notice_arms import (
    stayer_price_moves,
    vulnerable_leavers_not_offered,
    vulnerable_twin_shortfalls,
)

REPORT_END = "2018-09-30"
SHARE = 0.15


def _arm(placebo: bool, tmp_path) -> dict:
    patch = pytest.MonkeyPatch()
    patch.setattr(feed, "emits_pending_notice", lambda day: True)
    patch.setattr(run, "save_offers_active", lambda: True)
    patch.setattr(run, "world_save_response_scale", lambda: 50.0)
    if placebo:
        patch.setattr(run, "billed_rate_when_saved", lambda renewal, save: renewal)
    policy = dataclasses.replace(CURRENT_POLICY, save_offer_cut_share=SHARE)
    try:
        with policy_scope(policy):
            return run.main(report_end=REPORT_END, policy=policy,
                            gap_ledger_path=tmp_path / "gap_ledger.json")
    finally:
        patch.undo()


@pytest.fixture(scope="module")
def pair(tmp_path_factory):
    return (_arm(False, tmp_path_factory.mktemp("on")),
            _arm(True, tmp_path_factory.mktemp("placebo")))


def _saved(result) -> list[dict]:
    return [r for r in result["save_on_loss_notice_log"] if r["saved"]]


def test_a_saved_term_ends_and_stayers_renew_after_it(pair):
    """The precondition, so the control below cannot pass vacuously: the arms save the same
    households, at least one saved term ENDS inside the window (only an ended term reaches the
    premium), and stayers renew after that end."""
    on, placebo = pair
    assert [(r["customer_id"], r["term_start"]) for r in _saved(on)] == [
        (r["customer_id"], r["term_start"]) for r in _saved(placebo)]
    saved_terms = {(r["customer_id"], r["term_start"]) for r in _saved(on)}
    saved_accounts = {r["billing_account"] for r in _saved(on)}
    ends = [s["term_end"] for s in on["account_state_log"]
            if (s["customer_id"], s["term_start"]) in saved_terms and s["term_end"] < REPORT_END]
    assert ends, "no saved term ended inside the window"
    assert any(s["term_start"] > min(ends) and s["billing_account"] not in saved_accounts
               for s in on["account_state_log"])
    assert any(s["unit_rate_gbp_per_mwh"] != p["unit_rate_gbp_per_mwh"]
               for s, p in zip(on["account_state_log"], placebo["account_state_log"])
               if s["billing_account"] in saved_accounts), "the save price was never billed"


def test_no_stayer_price_moves_with_the_save_price(pair):
    """Defect 1. Account by account, every term priced in both arms outside a saved household
    carries the same unit rate."""
    on, placebo = pair
    saved = {r["billing_account"] for r in _saved(on)}
    assert stayer_price_moves(placebo["account_state_log"], on["account_state_log"], saved) == []


def test_the_household_answers_the_save_on_its_own_roll():
    """Defect 2. At the world's own response the answer is the world's rule unchanged; scaling to 0
    saves nobody; a stayer is never 'saved'; and both branches are reachable."""
    for roll, p0, pc in ((0.65, 0.6, 0.7), (0.75, 0.6, 0.7), (0.3, 0.6, 0.9)):
        assert household_takes_save(roll, p0, pc, 1.0) == saved_on_loss_notice(roll, p0, pc)
        assert not household_takes_save(roll, p0, pc, 0.0)
    assert household_takes_save(0.65, 0.6, 0.7) and not household_takes_save(0.75, 0.6, 0.7)
    assert not household_takes_save(0.3, 0.6, 0.9), "a roll below P(stay) was never leaving"


def test_the_comparison_sees_a_raised_stayer_and_skips_a_saved_one():
    """Defect 3. A stayer whose price differs is listed and marked raised; the saved household's
    own different price is not a stayer's; a term only one arm priced is not compared."""
    def row(cid, rate, start="2018-01-01"):
        return {"customer_id": cid, "billing_account": cid, "commodity": "electricity",
                "term_start": start, "unit_rate_gbp_per_mwh": rate}
    off = [row("A", 100.0), row("S", 100.0), row("B", 100.0), row("C", 100.0, "2018-02-01")]
    on = [row("A", 101.0), row("S", 90.0), row("B", 100.0)]
    moves = stayer_price_moves(off, on, {"S"})
    assert [(m["customer_id"], m["raised"]) for m in moves] == [("A", True)]


def test_no_vulnerable_household_in_the_run_is_offered_less(pair):
    """Defect 4, over the run. Every save the loop offered, a known-vulnerable household priced at
    what it was actually offered: none above its plain twin, and none left unoffered while a plain
    leaver was offered. The log must carry the company's knowledge, never the world's state."""
    on, _ = pair
    log = on["save_on_loss_notice_log"]
    assert log and all("known_vulnerable" in r for r in log)
    assert not any(k.startswith("world_") or "psr_type" in k for r in log for k in r)
    assert vulnerable_twin_shortfalls(log, SHARE) == []
    assert vulnerable_leavers_not_offered(log) == []


def test_the_vulnerability_check_sees_a_shortfall_and_an_unoffered_leaver():
    """Defect 4's instrument can fire on both legs: a known-vulnerable row offered above its plain
    twin is listed; a known-vulnerable leaver holding an Invitation and offered nothing is listed
    while a plain leaver was offered; a vulnerable row offered the twin's price is not."""
    def row(vuln, save, held=True, rate=200.0):
        return {"known_vulnerable": vuln, "invitation_held": held,
                "renewal_unit_rate_gbp_per_mwh": rate, "save_unit_rate_gbp_per_mwh": save}
    fair = row(True, 200.0 * (1 - SHARE))
    dear = row(True, 199.0)
    assert vulnerable_twin_shortfalls([fair, dear], SHARE) == [
        {**dear, "vulnerable_rate": 199.0, "plain_rate": 200.0 * (1 - SHARE)}]
    snubbed = row(True, None)
    assert vulnerable_leavers_not_offered([row(False, 170.0), snubbed]) == [snubbed]
    assert vulnerable_leavers_not_offered([row(False, None), snubbed]) == []
