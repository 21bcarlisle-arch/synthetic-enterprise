"""The S&RP conversation crosses as the household's answers, and the company's finding is made on them.

Defect each leg names: a world that never conceals (every PSR-type household honest, so the gate
can never be fooled); a discloser whose answers read as a clear "no"; a question the world answers
that the company does not ask (or the reverse); the company re-asking inside the year, or never
re-asking after it (SLC 28.3); a seam that cannot answer recorded as a conversation.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import fields

from company.billing.payment_observation_consumer import PaymentObservationConsumer
from company.billing.prepayment_suitability import FINDING_LAPSE_DAYS, SuitabilityAnswers
from company.interfaces.sim_interface import StubSimInterface
from simulation.household import household_of
from simulation.payment_method_dynamics import (
    SUITABILITY_ALL_NO,
    SUITABILITY_DISCLOSED,
    SUITABILITY_OFF,
    SUITABILITY_QUESTIONS,
    answer_suitability_questions,
)
from simulation.vulnerability_state import vulnerability_state

SEED, ON = 20240101, dt.date(2024, 3, 1)


class _World:
    """The live door's body at a fixed seed, counting how often it is asked."""

    def __init__(self, active=True):
        self.asked = []
        self.active = active

    def ask_prepayment_suitability(self, account_id, asked_on):
        self.asked.append((account_id, asked_on))
        return answer_suitability_questions(account_id, dt.date.fromisoformat(asked_on), SEED,
                                            active=self.active)


def test_the_world_answers_the_questions_the_company_asks():
    asked = tuple(f.name for f in fields(SuitabilityAnswers) if f.name != "asked_on")
    assert SUITABILITY_QUESTIONS == asked


def test_every_kind_of_answer_is_reached_and_a_concealer_says_no():
    # Partition control: each outcome must be reachable, or the gate is never tested by the world.
    seen = {"clear": 0, "concealed": 0, "disclosed": 0}
    for n in range(4000):
        point = f"C{n}"
        state = vulnerability_state(household_of(point), SEED)
        said = answer_suitability_questions(point, ON, SEED, active=True)
        if state.discloses_psr:
            assert said["reason"] == SUITABILITY_DISCLOSED
            assert set(said["answers"].values()) == {None}
            seen["disclosed"] += 1
        else:
            assert said["reason"] == SUITABILITY_ALL_NO
            assert set(said["answers"].values()) == {False}
            seen["concealed" if state.psr_type_vulnerable else "clear"] += 1
    assert all(seen.values()), seen
    off = answer_suitability_questions("C1", ON, SEED, active=False)
    assert off == {"answers": None, "reason": SUITABILITY_OFF}


def _point(kind):
    for n in range(4000):
        state = vulnerability_state(household_of(f"C{n}"), SEED)
        if kind == "disclosed" and state.discloses_psr:
            return f"C{n}"
        if kind == "concealed" and state.psr_type_vulnerable and not state.discloses_psr:
            return f"C{n}"
    raise AssertionError(kind)


def test_the_company_finds_on_what_it_was_told_and_asks_once_a_year():
    world = _World()
    consumer = PaymentObservationConsumer(plan_offers=world)
    # A concealer is found S&RP: the world pressing back, a harm the gate cannot see.
    concealer = _point("concealed")
    finding = consumer._prepayment_suitability(concealer, ON)
    assert finding is not None and finding.met and finding.unusable_on(ON) is None
    # A discloser is not: every question unanswered, and that is the bar.
    discloser = _point("disclosed")
    refused = consumer._prepayment_suitability(discloser, ON)
    assert refused is not None and not refused.met
    assert any(e.startswith("unanswered") for e in refused.evidence)

    # Asked once inside the year, again on the day the answers lapse (28.3).
    consumer._prepayment_suitability(concealer, ON + dt.timedelta(days=FINDING_LAPSE_DAYS - 1))
    assert [a for a, _ in world.asked].count(concealer) == 1
    later = ON + dt.timedelta(days=FINDING_LAPSE_DAYS)
    again = consumer._prepayment_suitability(concealer, later)
    assert [a for a, _ in world.asked].count(concealer) == 2
    assert again.learned_on == later


def test_a_seam_that_cannot_answer_records_no_conversation():
    for seam in (StubSimInterface(), _World(active=False)):
        consumer = PaymentObservationConsumer(plan_offers=seam)
        assert consumer._prepayment_suitability("C1", ON) is None
        assert consumer.suitability_answers == {}
