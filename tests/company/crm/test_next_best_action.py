"""C34 — one decision per customer, judged by its effect on forward value, against the flat rule.

The planted arm is a book in which the right action genuinely differs between accounts, so the
per-customer rule must beat one-action-for-all. The null arm is a book in which one action is
right for every account, so the per-customer rule must NOT beat it. The misled arm is a book whose
estimates point the wrong way, so the grade must be able to rule AGAINST the per-customer rule —
a grade that can only say "per-customer better" grades nothing.

The effect sizes below are planted test inputs, not estimates of the real world: no published
source gives a supplier's own uplift (research §7 gap 1).
"""
from __future__ import annotations

import pytest

from company.crm.next_best_action import (
    SLC_27_5B_CONSECUTIVE_MISSED_MONTHLY_PAYMENTS,
    AccountState,
    Action,
    ActionEstimate,
    decide,
    flat_action,
    forward_value,
    grade,
    hazard_estimate_from_holdout,
)

H = 36
T, C, D, N = Action.TARIFF_ADVICE, Action.CARBON_ADVICE, Action.DEBT_SUPPORT, Action.NOTHING


def est(action, benefit=50.0, dm=0.0, dh=0.0, why=""):
    return ActionEstimate(action, benefit, dm, dh, why)


def account(i, estimates, margin=20.0, hazard=0.02, missed=0):
    return AccountState(f"a{i}", margin, hazard, missed, tuple(estimates))


# Tariff advice keeps kind-A accounts (lower hazard, no margin given up); carbon advice costs them
# margin. Kind B is the mirror. Both leave the customer better off.
def kind_a():
    return [est(T, dh=-0.005), est(C, dm=-1.0)]


def kind_b():
    return [est(T, dm=-1.0), est(C, dh=-0.005)]


def truth_of(book):
    return {s.account_id: {e.action: e for e in s.estimates} for s in book}


def test_forward_value_is_b11s_shape():
    # B11 earns a month's margin when the account starts it supplied: the first month in full.
    assert forward_value(10.0, 0.5, 1) == 10.0
    assert forward_value(10.0, 0.5, 3) == pytest.approx(10.0 + 5.0 + 2.5)
    with pytest.raises(ValueError):
        forward_value(10.0, 1.2, 3)


def test_every_branch_of_the_decision_can_be_taken():
    book = [
        account(0, kind_a()),
        account(1, kind_b()),
        account(2, [est(D, dh=-0.01), est(T, dm=-1.0)]),
        account(3, [est(T, dm=-1.0), est(C, dm=-1.0)]),
    ]
    taken = {decide(s, H).action for s in book}
    assert taken == {T, C, D, N}


def test_the_planted_arm_per_customer_beats_the_flat_rule():
    book = [account(i, kind_a()) for i in range(60)] + [account(i, kind_b()) for i in range(60, 100)]
    g = grade(book, truth_of(book), H)
    assert g.flat_action is T
    assert g.chosen == {T: 60, C: 40}
    assert g.forgone_value.verdict == "per-customer better"
    assert g.forgone_value.interval_95[1] < 0


def test_the_null_arm_one_action_right_for_everyone_is_not_beaten():
    # Varied accounts, but tariff advice is the right action for every one of them.
    book = [account(i, kind_a(), margin=10.0 + i % 20, hazard=0.01 + (i % 5) / 200) for i in range(100)]
    g = grade(book, truth_of(book), H)
    assert g.flat_action is T and g.chosen == {T: 100}
    assert g.forgone_value.mean_difference == 0.0
    assert g.forgone_value.verdict.startswith("cannot tell")


def test_the_misled_arm_the_grade_can_rule_against_the_per_customer_rule():
    book = [account(i, kind_a()) for i in range(60)] + [account(i, kind_b()) for i in range(60, 100)]
    truth = {s.account_id: {T: est(T, dh=-0.005), C: est(C)} for s in book}
    g = grade(book, truth, H)
    assert g.forgone_value.verdict == "flat better"


def test_the_licence_trigger_pre_empts_a_better_scoring_action():
    ests = [est(D, dm=-2.0), est(T, dh=-0.01)]
    below = account(0, ests, missed=SLC_27_5B_CONSECUTIVE_MISSED_MONTHLY_PAYMENTS - 1)
    at = account(1, ests, missed=SLC_27_5B_CONSECUTIVE_MISSED_MONTHLY_PAYMENTS)
    assert decide(below, H).action is T
    d = decide(at, H)
    assert d.action is D and "SLC 27.5B" in d.reason


def test_the_customers_benefit_comes_first():
    s = account(0, [est(T, benefit=-30.0, dm=2.0), est(C, benefit=40.0, dh=-0.002)])
    d = decide(s, H)
    assert d.action is C and d.customer_benefit_gbp_per_year == 40.0


def test_an_unknown_effect_is_never_chosen_and_says_why():
    s = account(0, [ActionEstimate(T, 60.0, -1.0, None, "no holdout: atom B8")])
    d = decide(s, H)
    assert d.action is N
    assert d.unscored == ((T, "hazard_change_per_month unknown: no holdout: atom B8"),)
    with pytest.raises(ValueError):
        ActionEstimate(C, None, 0.0, 0.0)


def test_the_flat_rule_does_nothing_when_nothing_pays_on_average():
    book = [account(i, [est(T, dm=-1.0)]) for i in range(5)]
    assert flat_action(book, H) is N


def test_c7_ranks_on_joint_value_and_holds_a_no_loss_floor_on_both_sides():
    """Canon v4 C7 (2026-10-12). Fires on the old key (our forward value alone would take T, which
    gives us 1 more month of margin but the household nothing) and on a missing floor (C gives the
    household GBP 400 a year but costs us margin, so it is refused however large the sum)."""
    s = account(0, [est(T, benefit=0.0, dm=0.05), est(Action.CARBON_ADVICE, benefit=60.0, dm=0.0),
                    est(D, benefit=400.0, dm=-2.0)])
    d = decide(s, H)
    assert d.action is Action.CARBON_ADVICE, d
    # The rare branch exists: with the household's gain removed, our side alone decides.
    s2 = account(0, [est(T, benefit=0.0, dm=0.05), est(Action.CARBON_ADVICE, benefit=0.0, dm=0.0)])
    assert decide(s2, H).action is T


def holdout(n, stayed_contacted, stayed_held_out):
    return ([{"arm": "treated", "stayed": i < round(stayed_contacted * n)} for i in range(n)]
            + [{"arm": "holdout", "stayed": i < round(stayed_held_out * n)} for i in range(n)])


def test_a_holdout_sets_the_hazard_only_when_its_interval_decides_and_can_decide_against_us():
    """Research §6.2. Over one partition: a holdout that raises staying, one that lowers it, and one
    that cannot tell all occur. Fires on ranking the point when the interval spans zero (the
    undecided arm would be scored) and on a sign flip (the sleeping dog would be taken)."""
    raises = hazard_estimate_from_holdout(T, holdout(3000, 0.86, 0.84), 12, 50.0, 0.0)
    lowers = hazard_estimate_from_holdout(T, holdout(3000, 0.80, 0.84), 12, 50.0, 0.0)
    unsure = hazard_estimate_from_holdout(T, holdout(200, 0.86, 0.84), 12, 50.0, 0.0)
    assert raises.hazard_change_per_month < 0 < lowers.hazard_change_per_month
    assert unsure.hazard_change_per_month is None and "spans zero" in unsure.unknown_because
    # 1 - 0.86^(1/12) minus 1 - 0.84^(1/12): the constant-hazard reading of the window.
    assert raises.hazard_change_per_month == pytest.approx(0.84 ** (1 / 12) - 0.86 ** (1 / 12))
    taken = {e: decide(account(0, [e]), H).action for e in (raises, lowers, unsure)}
    assert taken == {raises: T, lowers: N, unsure: N}
    assert "unknown" in decide(account(0, [unsure]), H).unscored[0][1]
    one_arm = hazard_estimate_from_holdout(T, holdout(10, 1.0, 1.0)[:10], 12, 50.0, 0.0)
    assert one_arm.hazard_change_per_month is None and "holds no decision" in one_arm.unknown_because
    with pytest.raises(ValueError):
        hazard_estimate_from_holdout(T, holdout(10, 1.0, 1.0), 0, 50.0, 0.0)
