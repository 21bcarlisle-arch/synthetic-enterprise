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

from company.interfaces.sim_interface import LiveSimInterface
from simulation.plan_offer_response import (
    PUBLISHED_BASIS,
    answer_plan_offer,
    plan_instalments,
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
