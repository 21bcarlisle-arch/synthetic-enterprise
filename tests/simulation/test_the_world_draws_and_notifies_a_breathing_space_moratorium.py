"""The world draws a Breathing Space moratorium and the company's register holds it (W2_44).

Defect named: `BreathingSpaceRegister.register_entry` had no caller in company/, simulation/ or
background/, so no run ever held a moratorium, and every Breathing Space refusal (the dunning
selector, the debt objection, the Consent offer, C37's meter recovery) was unreachable live.

Knowledge: `docs/market_research/debt_and_collections.md`, "The entry rate (E9, 2026-11-15)".
"""
from __future__ import annotations

import dataclasses
import datetime as dt

import pytest

import background.live_payment_triad as triad_mod
import simulation.debt_respite_draw as drw
from background.live_payment_triad import LivePaymentTriad
from company.billing.payment_observation_consumer import PaymentObservationConsumer
from simulation.debt_respite_draw import MoratoriumDrawer, annual_rate, monthly_hazard

ON = dt.date(2023, 3, 15)


def _forced(monkeypatch):
    monkeypatch.setattr(drw, "monthly_hazard", lambda year, share=drw.ENERGY_SHARE: 1.0)


def test_every_branch_of_the_draw_can_be_taken(monkeypatch):
    """One control over the partition: a guard that refuses everything passes every refusal test."""
    _forced(monkeypatch)
    d = MoratoriumDrawer()
    plan = {
        "fires": d.draw("H1", "H1", 1, ON, in_arrears=True) is not None,
        "not_in_arrears": d.draw("H2", "H2", 1, ON, in_arrears=False) is None,
        "before_the_scheme": d.draw("H3", "H3", 1, dt.date(2021, 5, 3), in_arrears=True) is None,
        "same_household_month": d.draw("H1", "H1", 1, ON, in_arrears=True) is None,
        "inside_the_12_month_bar": d.draw(
            "H1", "H1", 2, ON + dt.timedelta(days=300), in_arrears=True) is None,
        "after_the_bar": d.draw(
            "H1", "H1", 3, ON + dt.timedelta(days=400), in_arrears=True) is not None,
    }
    assert all(plan.values()), plan
    assert d.notices_sent == 2


def test_the_rate_is_the_derived_one_at_real_inputs():
    """Zero before 4 May 2021; about 1.3-1.9% a year per indebted account at the 0.37 share."""
    assert annual_rate(2020) == 0.0
    rates = {y: annual_rate(y) for y in range(2021, 2027)}
    assert all(0.010 < r < 0.020 for r in rates.values()), rates
    assert annual_rate(2023, 1.0) == pytest.approx(86_926 / 1_759_237)
    # The unforced draw fires at about the hazard over many indebted household-months.
    d = MoratoriumDrawer()
    n = 40_000
    fired = sum(d.draw(f"H{i}", f"H{i}", 7, ON, in_arrears=True) is not None for i in range(n))
    expect = n * monthly_hazard(2023)
    assert abs(fired - expect) < 4 * expect ** 0.5, (fired, expect)


def test_a_notice_puts_the_account_in_a_60_day_moratorium(monkeypatch):
    _forced(monkeypatch)
    notice = MoratoriumDrawer().draw("ACC1", "ACC1", 1, ON, in_arrears=True)
    consumer = PaymentObservationConsumer()
    assert not consumer.breathing_space.moratorium_active("ACC1", ON + dt.timedelta(days=1))
    entered = consumer.observe_moratorium_start_wire(notice)
    assert len(entered) == 1
    start = ON + dt.timedelta(days=1)
    reg = consumer.breathing_space
    assert not reg.moratorium_active("ACC1", ON)
    assert reg.moratorium_active("ACC1", start)
    assert reg.moratorium_active("ACC1", start + dt.timedelta(days=59))
    assert not reg.moratorium_active("ACC1", start + dt.timedelta(days=60))
    # A redelivered notice enters nothing (C-S2, at-least-once).
    assert consumer.observe_moratorium_start_wire(notice) == ()
    assert len(reg.records_for_account("ACC1")) == 1


def test_a_notice_carrying_world_truth_is_refused(monkeypatch):
    """The seam's second belt, consumer side."""
    _forced(monkeypatch)
    notice = MoratoriumDrawer().draw("ACC1", "ACC1", 1, ON, in_arrears=True)
    notice["envelope"]["payload"]["income_stress"] = "HIGH"
    with pytest.raises(Exception, match="world truth"):
        PaymentObservationConsumer().observe_moratorium_start_wire(notice)


def test_a_notice_from_another_sender_is_refused(monkeypatch):
    """The frame is authenticated: a notice presenting a credential the registry does not hold
    opens nothing."""
    _forced(monkeypatch)
    notice = MoratoriumDrawer().draw("ACC1", "ACC1", 1, ON, in_arrears=True)
    notice["credential"] = "not-the-register"
    consumer = PaymentObservationConsumer()
    with pytest.raises(Exception):
        consumer.observe_moratorium_start_wire(notice)
    assert not consumer.breathing_space.records_for_account("ACC1")


def test_the_run_triad_carries_the_moratorium_to_the_receivable(monkeypatch):
    """End to end: an unpaid bill in the world, a drawn notice, both books told, and the
    receivable the debt objection reads says moratorium_active."""
    _forced(monkeypatch)
    real = triad_mod.generate_payment_event

    def unpaid(*a, **k):
        e = real(*a, **k)
        return dataclasses.replace(e, result="failed", days_late=0, payment_date=None)

    monkeypatch.setattr(triad_mod, "generate_payment_event", unpaid)
    triad = LivePaymentTriad()
    triad.record_period(customer_id="BSX1", due_date=dt.date(2023, 2, 14), amount_gbp=180.0,
                        income_stress_value="HIGH", bill_month="2023-01")
    assert triad.moratoria_notified == 1
    account = triad_mod.account_of("BSX1")
    records = triad._consumer.breathing_space.records_for_account(account)
    assert [r.start_date for r in records] == [dt.date(2023, 2, 15)]
    assert triad.receivable("BSX1", dt.date(2023, 2, 20))["moratorium_active"] is True
    # Both books are told, for the reason both are billed.
    assert triad._cf_consumer.breathing_space.moratorium_active(account, dt.date(2023, 2, 20))
