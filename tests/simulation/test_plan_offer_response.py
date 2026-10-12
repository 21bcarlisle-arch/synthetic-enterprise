"""EP4 -- the world's answer to a repayment-plan offer.

What each control names as its own defect:

  * `test_the_published_basis_answers_none_and_names_why` -- the world invents an answer no
    published rate supports, or answers None without a reason.
  * `test_a_sourced_basis_reaches_both_answers_and_both_instalment_outcomes` -- the draw can only
    go one way (always agree, always pay), or an instalment dated after `through` is returned.
  * `test_the_live_seam_carries_the_worlds_answer` -- the seam drops or rewrites the answer.
"""
from __future__ import annotations

import dataclasses
import datetime as dt

import pytest

import simulation.plan_offer_response as por
from background.live_payment_triad import LivePaymentTriad
from company.interfaces.sim_interface import LiveSimInterface
from simulation.plan_offer_response import (
    LOWER_PAYMENT,
    PAUSE,
    PUBLISHED_BASIS,
    TOKEN_CUT_SHARE,
    HouseholdPlanBook,
    answer_plan_offer,
    basis_at,
    lower_payment_failure_multiplier,
    pause_resume_fails,
    plan_instalments,
    plan_outcomes,
)

OFFERED = dt.date(2017, 3, 1)


def test_the_published_basis_answers_none_and_names_why():
    answer = answer_plan_offer("C1", OFFERED, 40.0)
    assert answer.accepted is None and answer.instalment is None
    assert answer.reason == PUBLISHED_BASIS.take_up_gap and "take-up" in answer.reason
    assert plan_instalments("C1", OFFERED, dt.date(2020, 1, 1)) == []


def test_a_sourced_basis_reaches_both_answers_and_both_instalment_outcomes():
    basis = dataclasses.replace(PUBLISHED_BASIS, take_up_rate=0.5, instalment_keep_rate=0.5,
                                monthly_instalment_gbp=25.0)
    answers = [answer_plan_offer(f"C{i}", OFFERED, 40.0 if i % 2 else 10.0, basis=basis)
               for i in range(200)]
    assert {a.accepted for a in answers} == {True, False}
    assert {a.instalment for a in answers if a.accepted} == {25.0, 10.0}, (
        "an instalment is capped at the debt offered against")
    assert answers[7] == answer_plan_offer("C7", OFFERED, 40.0, basis=basis), "not deterministic"
    through = dt.date(2018, 3, 15)
    paid = [i for n in range(20) for i in plan_instalments(f"C{n}", OFFERED, through, basis=basis)]
    assert {i["paid"] for i in paid} == {True, False}
    assert all(i["due"] <= through.isoformat() for i in paid)
    one = plan_instalments("C0", OFFERED, through, basis=basis)
    assert [i["due"] for i in one][:2] == ["2017-04-01", "2017-05-01"] and len(one) == 12
    jan31 = plan_instalments("C0", dt.date(2017, 1, 31), dt.date(2017, 3, 31), basis=basis)
    assert [i["due"] for i in jan31] == ["2017-02-28", "2017-03-31"]


def test_the_live_seam_carries_the_worlds_answer():
    seam = LiveSimInterface()
    world = answer_plan_offer("C1", OFFERED, 40.0)
    assert seam.answer_plan_offer("C1", OFFERED, 40.0) == {
        "accepted": world.accepted, "instalment": world.instalment,
        "reason": world.reason}
    assert seam.get_plan_instalments("C1", OFFERED, dt.date(2020, 1, 1)) == []


# --- The household's answer from its own state (2026-10-12, the world lane) -----------------------
#
# What each control below names as its own defect:
#
#   * `test_the_shipped_world_still_answers_none` -- switching the module on by default, so the
#     shipped book moves before anyone chose a setting.
#   * `test_every_outcome_of_an_offer_is_reachable_at_a_register_setting` -- the control over the
#     whole partition, asserted BEFORE any shape: declined, agreed-and-completed, broken by the
#     household's own reasons, broken by an income shock. A world that only ever does one of these
#     passes every shape test below.
#   * `test_the_households_own_instalment_spreads_the_debt_over_the_weeks_to_recover` -- the
#     instalment is invented rather than derived from the published range.
#   * `test_a_supplier_named_instalment_above_the_households_own_breaks_more` -- affordability does
#     not reach keeping, so an unaffordable offer looks as good as an affordable one.
#   * `test_an_income_shock_breaks_a_plan_and_a_household_already_in_high_stress_is_not_shocked` --
#     the plan does not read the household's money, or reads it without a change.
#   * `test_a_token_cut_changes_nothing_and_a_material_cut_lowers_failures` -- MMI's null or HAMP's
#     elasticity lost.
#   * `test_a_pause_ends_in_a_failure_only_for_a_household_still_in_difficulty` -- the resume draw
#     ignores the household's state.
#   * `test_the_triad_applies_an_agreed_pause_to_the_collection_after_it` -- the effect is computed
#     and never reaches the run's payment draw.

HIGH = basis_at("high")
THROUGH = dt.date(2021, 12, 31)


def _book_with(accounts, stress_by_month):
    book = HouseholdPlanBook()
    for a in accounts:
        for m, s in stress_by_month:
            book.note_stress(a, m, s)
    return book


def test_the_shipped_world_still_answers_none():
    assert basis_at("default") is PUBLISHED_BASIS and por.BASIS is PUBLISHED_BASIS
    assert answer_plan_offer("C1", OFFERED, 40.0).accepted is None


def test_every_outcome_of_an_offer_is_reachable_at_a_register_setting():
    accounts = [f"ACC-{i}" for i in range(400)]
    # Half the households lose income in 2017-09 (LOW -> HIGH); half never do.
    book = _book_with(accounts[:200],
                      [(dt.date(2017, 2, 28), "low"), (dt.date(2017, 9, 28), "high")])
    for a in accounts[200:]:
        book.note_stress(a, dt.date(2017, 2, 28), "moderate")
    answers = [answer_plan_offer(a, OFFERED, 300.0, basis=HIGH, agreements=book) for a in accounts]
    out = plan_outcomes(book, THROUGH, basis=HIGH)
    assert {x.accepted for x in answers} == {True, False}
    assert out["completed"] and out["broken_own"] and out["broken_income_shock"], out
    assert out["agreed"] == sum(1 for x in answers if x.accepted)
    assert book.summary()["accepted"] == out["agreed"]
    share = out["agreed"] / len(accounts)
    assert abs(share - HIGH.take_up_rate) < 0.08, share


def test_the_households_own_instalment_spreads_the_debt_over_the_weeks_to_recover():
    low = basis_at("low")
    agreed = next(answer_plan_offer(f"A{i}", OFFERED, 520.0, basis=low) for i in range(50)
                  if answer_plan_offer(f"A{i}", OFFERED, 520.0, basis=low).accepted)
    assert agreed.instalment == round(520.0 / (low.weeks_to_recover * 12 / 52), 2)


def _broken_share(named_gbp):
    book = HouseholdPlanBook()
    n = broken = 0
    for i in range(1500):
        a = f"B{i}"
        x = answer_plan_offer(a, OFFERED, 300.0, basis=HIGH, agreements=book,
                              offer=None if named_gbp is None else {"kind": "repayment_plan",
                                                                     "monthly_gbp": named_gbp})
        if x.accepted:
            n += 1
            broken += not all(r["paid"] for r in plan_instalments(
                a, OFFERED, THROUGH, basis=HIGH, agreements=book)[:6])
    return broken / n


def test_a_supplier_named_instalment_above_the_households_own_breaks_more():
    own = 300.0 / (HIGH.weeks_to_recover * 12 / 52)
    base, dear = _broken_share(None), _broken_share(round(own * 1.4, 2))
    assert 0 < base < dear <= 1.0, (base, dear)
    assert abs(base - HIGH.plan_break_share) < 0.06, base


def test_an_income_shock_breaks_a_plan_and_a_household_already_in_high_stress_is_not_shocked():
    kept = dataclasses.replace(HIGH, take_up_rate=1.0, plan_break_share=0.0)
    for start, expect_break in (("low", True), ("high", False)):
        book = _book_with(["S"], [(dt.date(2017, 2, 28), start), (dt.date(2017, 9, 28), "high")])
        assert answer_plan_offer("S", OFFERED, 300.0, basis=kept, agreements=book).accepted
        rows = plan_instalments("S", OFFERED, dt.date(2018, 1, 31), basis=kept, agreements=book)
        paid = [r["paid"] for r in rows]
        if expect_break:
            assert paid[:6] == [True] * 6 and not any(paid[6:]), paid
        else:
            assert all(paid), paid


def test_a_token_cut_changes_nothing_and_a_material_cut_lowers_failures():
    assert lower_payment_failure_multiplier(TOKEN_CUT_SHARE * 0.99, HIGH) == 1.0
    assert lower_payment_failure_multiplier(0.30, HIGH) == pytest.approx(
        1 - HIGH.lower_payment_elasticity * 0.30)
    assert lower_payment_failure_multiplier(0.30, PUBLISHED_BASIS) == 1.0, "off means no effect"
    book = _book_with(["L"], [(dt.date(2017, 2, 28), "high")])
    lower = dataclasses.replace(HIGH, take_up_rate=1.0)
    answer_plan_offer("L", OFFERED, 0.0, basis=lower, agreements=book,
                      offer={"kind": LOWER_PAYMENT, "monthly_gbp": 70.0,
                             "usual_monthly_gbp": 100.0, "months": 3})
    assert book.collection_effect("L", dt.date(2017, 5, 28), lower)[0] == pytest.approx(0.7)
    assert book.collection_effect("L", dt.date(2017, 7, 28), lower) == (1.0, False)
    assert not book.repays_through_plan("L", dt.date(2017, 2, 1), dt.date(2017, 9, 1))


def test_a_pause_ends_in_a_failure_only_for_a_household_still_in_difficulty():
    certain = dataclasses.replace(HIGH, pause_resume_failure_share=1.0)
    assert pause_resume_fails("P", OFFERED, "high", certain)
    assert not pause_resume_fails("P", OFFERED, "low", certain)
    some = [pause_resume_fails(f"P{i}", OFFERED, "moderate", HIGH) for i in range(300)]
    assert True in some and False in some


@pytest.fixture
def pause_world(monkeypatch):
    world = dataclasses.replace(HIGH, take_up_rate=1.0, pause_resume_failure_share=1.0)
    monkeypatch.setattr(por, "BASIS", world)
    return world


def test_the_triad_applies_an_agreed_pause_to_the_collection_after_it(pause_world):
    triad = LivePaymentTriad()
    results = {}
    for i in range(30):
        cid = f"RESI{i:05d}"
        if i == 0:
            triad._household_plans.note_stress(f"ACC-{cid}", dt.date(2020, 1, 28), "high")
            answer_plan_offer(f"ACC-{cid}", dt.date(2020, 2, 1), 0.0, basis=pause_world,
                              agreements=triad._household_plans,
                              offer={"kind": PAUSE, "months": 2})
        rec = triad.record_period(customer_id=cid, due_date=dt.date(2020, 4, 28), amount_gbp=90.0,
                                  income_stress_value="high", segment="resi")
        results[cid] = rec["result"]
    assert set(results.values()) - {"DD_FAILED"}, "no ordinary household paid: nothing is tested"
    assert results["RESI00000"] == "DD_FAILED"
