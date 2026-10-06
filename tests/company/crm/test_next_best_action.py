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
