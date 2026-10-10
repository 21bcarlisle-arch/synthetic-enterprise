"""At a term the world does not roll, a retention offer is made only where the discount wins the fix.

The defect each leg names: a household converting off our default tariff carries no exit at that
term, so an offer there buys only a conversion the household would otherwise decline. On run
224e4af02, 95 of 105 such offers (GBP 3,252) bought nothing: 84 converted at the full rate anyway,
and 11 declined even at the discount (`SEAT_FINDING_C29_THE_BOOK_ARM_SURVIVES_THE_REFIT_AT_HALF_ITS_
LIFT_2026-10-05`, addenda 2026-10-09 and 2026-10-10).
"""
from __future__ import annotations

import ast
from pathlib import Path

from company.interfaces.growth_desk import retention_offer_can_buy_anything
from company.policy.decision_policy import CURRENT_POLICY, NAIVE_POLICY, VALUE_ARM_POLICY

REPO = Path(__file__).resolve().parents[2]
FLAG = "retention_offers_at_default_anniversary_only_where_the_discount_wins"

#: (full-rate position vs default, offered position, offer?) at an unrolled term. The positions are
#: the run's own at 2018-04-01 electricity: a fix 3% over the default with a 5% tier sits at -2.15%.
UNROLLED = [
    (-0.05, -0.0975, False),   # converts at the full rate: the discount is a transfer
    (0.0, -0.05, False),       # AT the default converts too: the world declines only above it
    (0.03, -0.0215, True),     # declines at full, converts at the offer: the one thing it buys
    (0.03, -0.0009, True),
    (0.06, 0.007, False),      # declines even at the offer
    (0.10, 0.045, False),
]


def _offers(full, offered, *, on_default=True):
    return retention_offer_can_buy_anything(
        previous_term_on_our_default=on_default,
        full_position_vs_default=full, offered_position_vs_default=offered)


def test_both_branches_are_reached_at_an_unrolled_term():
    decisions = {_offers(f, o) for f, o, _ in UNROLLED}
    assert decisions == {True, False}, "the rule never offers, or always offers, at an unrolled term"


def test_an_offer_is_made_only_where_it_converts_a_decline():
    for full, offered, want in UNROLLED:
        assert _offers(full, offered) is want, (full, offered)


def test_no_offer_where_the_full_rate_fix_is_already_at_or_below_the_default():
    for full in (-0.20, -0.0001, 0.0):
        assert not _offers(full, full - 0.05), (
            f"offered at an unrolled term whose full-rate fix is {full:+.4f} against the default: "
            "the household converts without it")


def test_an_unknown_position_makes_no_offer_and_a_rolled_term_is_untouched():
    assert not _offers(None, None)
    assert not _offers(0.03, None)
    for full, offered, _ in UNROLLED + [(None, None, None)]:
        assert _offers(full, offered, on_default=False), "a rolled term was gated by the rule"


def test_the_rule_stands_on_current_and_its_arms_and_not_on_naive():
    assert getattr(CURRENT_POLICY, FLAG) and getattr(VALUE_ARM_POLICY, FLAG)
    assert not getattr(NAIVE_POLICY, FLAG)


def test_the_run_gates_the_offer_on_the_rule_from_its_own_book():
    """The rule is inert unless the runner asks it before the economic guard, with the previous
    term's tariff type and the fix's position at both rates."""
    tree = ast.parse((REPO / "simulation" / "run_phase2b.py").read_text(encoding="utf-8"))
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
             and getattr(n.func, "id", None) == "retention_offer_can_buy_anything"]
    assert len(calls) == 1
    kw = {k.arg: ast.unparse(k.value) for k in calls[0].keywords}
    assert "_previous_tariff_type == SVT_TARIFF_TYPE" in kw["previous_term_on_our_default"]
    assert kw["full_position_vs_default"] == "_offer_vs_default"
    assert "offered_rate(unit_rate, discount_pct)" in kw["offered_position_vs_default"]
    gates = [n for n in ast.walk(tree) if isinstance(n, ast.If)
             and ast.unparse(n.test) == "not _offer_can_buy"]
    assert len(gates) == 1
    branch = gates[0].orelse[0]
    assert isinstance(branch, ast.If) and "retention_value_protected" in ast.unparse(branch.test), (
        "the economic guard is not the else-branch of the rule: an offer can be made around it")
    assert any(isinstance(n, ast.Attribute) and n.attr == FLAG for n in ast.walk(tree)), (
        "the runner never reads the policy field, so no arm can switch the rule off")
