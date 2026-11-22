"""B8: the blind retention holdout is drawn before any treatment, can assign both arms, and is off.

The defect each test names. The holdouts B8 already had were drawn AFTER the guard's own verdict
(the save-rate coin draws only among renewals the guard would offer on), so the desk's decision chose
who could be held out. This one is drawn over every renewal the desk considers, ahead of the cut and
the guard, at the power-derived share (`competitive_pressure.SAVE_HOLDOUT_SHARE`, not a share picked
from practice: `docs/market_research/retention_slope_per_pound_of_renewal_cut.md` §3.5). It stays off
on every standing policy, so no standing book carries a second variable.
"""

from __future__ import annotations

import ast
import dataclasses
import inspect
import json
import math

from company.crm.competitive_pressure import SAVE_HOLDOUT_SHARE, save_holdout_draws
from company.interfaces.growth_desk import retention_blind_holdout_draws, retention_holdout_by_desk
from company.policy import decision_policy
from company.policy.decision_policy import DecisionPolicy

SWITCH = "retention_holdout_drawn_blind_before_treatment"


def _renewals(n: int = 600):
    return [(f"acct-{i}", f"{2019 + i % 4}-0{1 + i % 9}-01") for i in range(n)]


def test_the_switch_can_assign_both_arms_at_the_derived_share():
    """Defect: the coin holds out nobody (or everybody), so every guard test passes vacuously."""
    draws = [retention_blind_holdout_draws(a, d) for a, d in _renewals()]
    held, treated = sum(draws), len(draws) - sum(draws)
    assert held and treated, "the blind coin must be able to put a renewal in either arm"
    sd = math.sqrt(SAVE_HOLDOUT_SHARE * (1 - SAVE_HOLDOUT_SHARE) / len(draws))
    assert abs(held / len(draws) - SAVE_HOLDOUT_SHARE) < 4 * sd, (
        f"held {held / len(draws):.3f} of renewals, against the derived {SAVE_HOLDOUT_SHARE:.3f}")


def test_the_book_publishes_both_arms_of_the_blind_coin_per_year():
    """Defect: the assignment happens but the book's table drops an arm or the blind desk."""
    rows = [{"event_date": d, "arm": "holdout" if retention_blind_holdout_draws(a, d) else "treated",
             "stayed_at_decision": i % 4 != 0} for i, (a, d) in enumerate(_renewals())]
    table = retention_holdout_by_desk(renewal_offer_holdout=False, save_rate_holdout_on=False,
                                      blind_approach_rows=rows)["blind_approach"]
    assert table["assigned"] is True
    assert sum(r["treated"] + r["held_out"] for r in table["by_year"].values()) == len(rows)
    assert all(r["treated"] and r["held_out"] for r in table["by_year"].values())


def test_the_blind_coin_is_not_the_save_rate_coin():
    """Defect: the blind coin reuses the save-rate salt, so where both run they hold out the same
    households and neither arm is a twin of the other's."""
    pairs = [(retention_blind_holdout_draws(a, d), save_holdout_draws(a, d)) for a, d in _renewals()]
    assert any(b != s for b, s in pairs)
    assert list(inspect.signature(retention_blind_holdout_draws).parameters) == [
        "account_id", "event_date"]


def test_off_on_every_standing_policy_and_the_book_is_unchanged_when_off():
    """Defect: the switch defaults on, or the book gains a key with it off, so a standing book is
    no longer byte-identical to the one before the switch existed."""
    assert {f.name: f.default for f in dataclasses.fields(DecisionPolicy)}[SWITCH] is False
    policies = {name: p for name, p in vars(decision_policy).items()
                if isinstance(p, DecisionPolicy)}
    assert {"CURRENT_POLICY", "NAIVE_POLICY", "FLAT_SUPPLIER_POLICY"} <= set(policies)
    assert not [name for name, p in policies.items() if getattr(p, SWITCH)]
    before = retention_holdout_by_desk(renewal_offer_holdout=False, save_rate_holdout_on=False)
    off = retention_holdout_by_desk(renewal_offer_holdout=False, save_rate_holdout_on=False,
                                    blind_approach_rows=None)
    assert json.dumps(off, sort_keys=True) == json.dumps(before, sort_keys=True)
    assert "blind_approach" not in off


def _run_loop_tree():
    from simulation import run_phase2b

    return ast.parse(inspect.getsource(run_phase2b))


def _call_lines(tree, name):
    return sorted(n.lineno for n in ast.walk(tree) if isinstance(n, ast.Call)
                  and (getattr(n.func, "id", None) == name or getattr(n.func, "attr", None) == name))


def test_the_run_draws_the_coin_before_the_cut_the_guard_and_the_other_coins():
    """Defect: the draw moves after a treatment decision, and the desk again picks its holdout."""
    tree = _run_loop_tree()
    (draw,) = _call_lines(tree, "retention_blind_holdout_draws")
    later = {name: _call_lines(tree, name) for name in (
        "retention_cut_share_at_price_match", "retention_cut_share_at_risk_tiers", "decide",
        "retention_value_protected", "retention_save_holdout_draws", "book_retention_cost")}
    for name, lines in later.items():
        assert lines and all(draw < line for line in lines), f"{name} is asked before the blind coin"
    # The draw sits under the switch, so a run with it off never flips the coin.
    guarded = [n for n in ast.walk(tree) if isinstance(n, ast.If)
               and isinstance(n.test, ast.Attribute) and n.test.attr == SWITCH
               and any(isinstance(c, ast.Call) and getattr(c.func, "id", None)
                       == "retention_blind_holdout_draws" for c in ast.walk(n))]
    assert len(guarded) == 1


def test_a_held_renewal_withholds_the_approach_and_never_the_tariff():
    """Defect: the held branch is not the first in the offer chain (so a held renewal can still be
    offered), or it touches the re-fix rate the household is billed."""
    tree = _run_loop_tree()
    held = [n for n in ast.walk(tree) if isinstance(n, ast.If)
            and isinstance(n.test, ast.Name) and n.test.id == "_blind_held"]
    assert len(held) == 1
    branch = held[0]
    assert isinstance(branch.orelse[0], ast.If), "the held branch must head the offer chain"
    assigned = {t.id for n in ast.walk(ast.Module(body=branch.body, type_ignores=[]))
                if isinstance(n, ast.Assign) for t in n.targets if isinstance(t, ast.Name)}
    assert assigned == {"_no_offer_reason"}, f"the held branch writes {assigned}"


#: One year of renewals is the smallest window that has any: through 2016 the run holds one.
#: Measured 22 Nov (switch on, CURRENT_POLICY, to 2017-12-31): 72 considered, 16 held, 9 of them
#: stayed on the re-fix with no approach, none in the retention log. About 9 minutes.
RUN_WINDOW_END = "2017-12-31"


def test_a_run_with_the_switch_on_holds_households_out_and_they_keep_the_re_fix():
    """Defect: the switch is on and the run never takes the held branch (the coin sits on a path no
    renewal reaches), or a held renewal is still approached, or the held arm cannot stay on the
    re-fix. The director's 22 Nov ruling: a test shows the switch can be taken. The partition
    first: both arms must be populated before either is checked."""
    from company.policy.decision_policy import CURRENT_POLICY, policy_scope
    from simulation.run_phase2b import main as run_phase2b

    policy = dataclasses.replace(CURRENT_POLICY, **{SWITCH: True})
    with policy_scope(policy):
        run = run_phase2b(report_end=RUN_WINDOW_END, policy=policy)
    log = run["retention_blind_holdout_log"]
    held = {(r["customer_id"], r["event_date"]) for r in log if r["arm"] == "holdout"}
    treated = {(r["customer_id"], r["event_date"]) for r in log if r["arm"] == "treated"}
    assert held and treated, f"{len(held)} held, {len(treated)} treated: the switch was not taken"
    approached = {(e["customer_id"], e["event_date"]) for e in run["retention_log"]}
    assert not held & approached, "a renewal the blind coin held out was still approached"
    reasons = {(e["customer_id"], e["event_date"]): e.get("no_offer_reason")
               for e in run["no_offer_churn_log"]}
    assert {reasons[k] for k in held if k in reasons} <= {"held_out_blind_before_treatment"}
    assert any(r["stayed_at_decision"] for r in log if r["arm"] == "holdout"), (
        "no held household stayed, so the run cannot show the re-fix is still theirs")
    assert "blind_approach" in run["retention_holdout_by_desk_year"]


def test_a_held_household_that_asks_to_leave_can_still_be_saved():
    """Defect: the blind coin reaches the reactive save on the loss notice, so a held household
    that asks (by leaving) is refused the retention tariff. Only the proactive approach is held."""
    tree = _run_loop_tree()
    saves = [n for n in ast.walk(tree) if isinstance(n, ast.If)
             and "_save_offers_on" in {getattr(x, "id", None) for x in ast.walk(n.test)}]
    assert saves, "the reactive save's branch is not where this test looks for it"
    for n in saves:
        names = {getattr(x, "id", None) or getattr(x, "attr", None) for x in ast.walk(n.test)}
        assert not names & {"_blind_held", "_blind_drawn", SWITCH}, names
