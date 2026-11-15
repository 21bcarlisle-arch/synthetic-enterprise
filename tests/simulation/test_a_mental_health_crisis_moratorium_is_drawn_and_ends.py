"""The world draws a mental health crisis moratorium, and the register's end notice ends it (W2_45).

Defect named: W2_44 drew only standard moratoria. An MHCM has no fixed end (reg 32(2)), and the
company's register had no end-notice route, so a drawn one would have held collections for ever.
It was therefore left out: about 1 in 60 moratoria were never drawn.

Knowledge: `docs/market_research/debt_and_collections.md`, "The mental health crisis moratorium's
length (W2_45)".
"""
from __future__ import annotations

import datetime as dt

import pytest

import simulation.debt_respite_draw as drw
from company.billing.payment_observation_consumer import PaymentObservationConsumer
from simulation.debt_respite_draw import (
    MHCM_TREATMENT_DAYS_RANGE,
    MoratoriumDrawer,
    annual_rate,
    mhcm_annual_rate,
    mhcm_end_date,
    mhcm_end_notice_day,
)
from simulation.rng_substream import substream

ON = dt.date(2023, 3, 15)


def _only_mhcm(monkeypatch):
    monkeypatch.setattr(drw, "monthly_hazard", lambda year, share=drw.ENERGY_SHARE: 0.0)
    monkeypatch.setattr(drw, "mhcm_monthly_hazard", lambda year, share=drw.ENERGY_SHARE: 1.0)


def _type(notice):
    return notice["envelope"]["payload"]["moratorium_type"]


def test_every_branch_of_the_type_draw_can_be_taken(monkeypatch):
    """One control over the partition: standard, MHCM, nothing, and held-while-in-force."""
    monkeypatch.setattr(drw, "monthly_hazard", lambda year, share=drw.ENERGY_SHARE: 0.3)
    monkeypatch.setattr(drw, "mhcm_monthly_hazard", lambda year, share=drw.ENERGY_SHARE: 0.3)
    d = MoratoriumDrawer()
    kinds = [None if (n := d.draw(f"H{i}", f"H{i}", 1, ON, in_arrears=True)) is None else _type(n)
             for i in range(200)]
    held = MoratoriumDrawer()
    _only_mhcm(monkeypatch)
    first = held.draw("H", "H", 1, ON, in_arrears=True)
    again = held.draw("H", "H", 2, ON + dt.timedelta(days=30), in_arrears=True)
    plan = {"standard": "standard" in kinds, "mhcm": "mental_health_crisis" in kinds,
            "none": None in kinds, "held": first is not None and again is None}
    assert all(plan.values()), plan


def test_no_standard_draw_moved():
    """The standard band is the bottom of the same uniform, so W2_44's realisations stand."""
    d = MoratoriumDrawer()
    h = drw.monthly_hazard(ON.year)
    fired = {i for i in range(20_000)
             if (n := d.draw(f"H{i}", f"H{i}", 3, ON, in_arrears=True)) is not None
             and _type(n) == "standard"}
    expected = {i for i in range(20_000)
                if substream(drw.STREAM_NAMESPACE, f"H{i}::3", 0).random() < h}
    assert fired == expected


def test_the_mhcm_rate_is_its_published_share_of_the_standard_rate():
    for year, mh, std in ((2022, 1_216, 69_571), (2025, 1_317, 87_813)):
        assert mhcm_annual_rate(year) / annual_rate(year) == pytest.approx(mh / std)
    assert mhcm_annual_rate(2020) == 0.0


def test_the_end_is_treatment_plus_thirty_days():
    """Reg 32(2)(a): 30 days beginning with the day treatment stops."""
    start = dt.date(2023, 3, 16)
    lo, hi = MHCM_TREATMENT_DAYS_RANGE
    # Treatment's last day is start + lo - 1; it stops on start + lo; day 30 is 29 days later.
    assert mhcm_end_date(start, lo) == start + dt.timedelta(days=lo + 29)
    assert (mhcm_end_date(start, lo) - start).days + 1 == lo + 30
    assert (mhcm_end_date(start, hi) - start).days + 1 == hi + 30


def test_the_register_holds_an_mhcm_until_its_end_notice_and_then_releases_it(monkeypatch):
    _only_mhcm(monkeypatch)
    d = MoratoriumDrawer()
    start_wire = d.draw("ACC1", "ACC1", 1, ON, in_arrears=True)
    assert _type(start_wire) == "mental_health_crisis"
    consumer = PaymentObservationConsumer()
    consumer.observe_moratorium_start_wire(start_wire)
    reg = consumer.breathing_space
    start = ON + dt.timedelta(days=1)
    # No fixed end: still held well past a standard moratorium's 60 days.
    assert reg.moratorium_active("ACC1", start + dt.timedelta(days=200))
    end = d._in_force_until["ACC1"]
    lo, hi = MHCM_TREATMENT_DAYS_RANGE
    assert lo + 30 <= (end - start).days + 1 <= hi + 30
    # The notice is sent BEFORE the end it names (regs 32(4), 32(6), 33), and handed over once.
    sent_on = d._pending_ends[0][0]
    assert sent_on < end
    assert d.end_notices_due(sent_on - dt.timedelta(days=1)) == []
    (end_wire,) = d.end_notices_due(sent_on)
    assert d.end_notices_due(end + dt.timedelta(days=5)) == []
    assert end_wire["envelope"]["payload"]["end_date"] == end.isoformat()
    assert end_wire["envelope"]["observed_at"].startswith(sent_on.isoformat())
    closed = consumer.observe_moratorium_end_wire(end_wire)
    assert len(closed) == 1
    # Completed early, held through the end it names, released the day after.
    assert reg.moratorium_active("ACC1", sent_on)
    assert reg.moratorium_active("ACC1", end)
    assert not reg.moratorium_active("ACC1", end + dt.timedelta(days=1))
    assert reg.records_for_account("ACC1")[0].end_date == end
    # A redelivered end notice completes nothing.
    assert consumer.observe_moratorium_end_wire(end_wire) == ()
    # Counting: one start notice sent, one MHCM started and ended.
    assert (d.notices_sent, d.mhcm_started, d.mhcm_ended) == (1, 1, 1)


def test_an_end_notice_for_an_entry_never_opened_is_refused_by_name(monkeypatch):
    _only_mhcm(monkeypatch)
    d = MoratoriumDrawer()
    d.draw("ACC9", "ACC9", 1, ON, in_arrears=True)
    (end_wire,) = d.end_notices_due(ON + dt.timedelta(days=200))
    with pytest.raises(ValueError, match="MHCM-ACC9"):
        PaymentObservationConsumer().observe_moratorium_end_wire(end_wire)


def test_an_end_notice_carrying_world_truth_is_refused(monkeypatch):
    _only_mhcm(monkeypatch)
    d = MoratoriumDrawer()
    consumer = PaymentObservationConsumer()
    consumer.observe_moratorium_start_wire(d.draw("ACC2", "ACC2", 1, ON, in_arrears=True))
    (end_wire,) = d.end_notices_due(ON + dt.timedelta(days=200))
    end_wire["envelope"]["payload"]["true_debt"] = 12.0
    with pytest.raises(ValueError, match="world truth"):
        consumer.observe_moratorium_end_wire(end_wire)


def test_the_end_notice_comes_after_the_treatment_stops_and_before_the_end_it_names():
    """Regs 32(2)(a), 32(4), 32(6) and 33, at every treatment length the belief can draw and well
    past it: the adviser cannot know before the treatment stops, and the 25-day check plus two
    business days always lands inside the 30 post-treatment days."""
    start = dt.date(2023, 1, 1)
    for t in range(0, 400):
        stopped = start + dt.timedelta(days=t)
        sent = mhcm_end_notice_day(start, t)
        assert stopped <= sent < mhcm_end_date(start, t), (t, sent)
