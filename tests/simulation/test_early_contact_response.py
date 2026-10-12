"""A household contacted early in difficulty -- the world's answer (2026-10-12, the world lane).

What each control names as its own defect:

  * `test_the_shipped_world_answers_no_contact` -- the response switched on by default.
  * `test_every_answer_is_reachable_and_money_decides_which` -- the partition, asserted first:
    not woken, woken and pays, woken and cannot pay. A world where every contact pays (or none
    does), or where a HIGH-stress household pays, passes every shape test.
  * `test_a_later_contact_wakes_fewer_and_one_past_the_window_wakes_none` -- the published decay
    with delay lost, or the window open at its far end.
  * `test_the_store_finds_only_a_difficulty_contact_inside_the_window` -- an SVT letter, or a
    contact before the miss, read as a contact about it.
  * `test_the_triad_pays_a_contacted_miss_at_the_window_end_and_drops_its_later_lump` -- the
    response is drawn and never reaches the company's cash, or the bill is paid twice.
"""
from __future__ import annotations

from datetime import date, timedelta

import pytest

import simulation.contact_response as cr
from background.live_payment_triad import LivePaymentTriad
from simulation.contact_response import (
    EARLY_CONTACT_INSTRUMENT,
    EARLY_WINDOW_DAYS,
    ContactsReceived,
    early_contact_response,
    early_contact_share_at,
)

DUE = date(2020, 1, 28)


def test_the_shipped_world_answers_no_contact():
    assert cr.EARLY_CONTACT_SHARE == 0.0 == early_contact_share_at("default")
    assert not any(early_contact_response(f"A{i}", DUE, DUE + timedelta(days=2), "low")["woken"]
                   for i in range(200))


def test_every_answer_is_reachable_and_money_decides_which():
    high = early_contact_share_at("high")
    rows = [early_contact_response(f"A{i}", DUE, DUE + timedelta(days=2), s, high)
            for i in range(600) for s in ("low", "high")]
    assert {(r["woken"], r["pays"]) for r in rows} == {(False, False), (True, True), (True, False)}
    assert not any(r["pays"] for r in rows if r["stress"] == "HIGH")
    assert all(r["pays"] for r in rows if r["woken"] and r["stress"] != "HIGH")
    woken = sum(r["woken"] for r in rows) / len(rows)
    assert abs(woken - high) < 0.05, woken


def test_a_later_contact_wakes_fewer_and_one_past_the_window_wakes_none():
    def share(days):
        return sum(early_contact_response(f"A{i}", DUE, DUE + timedelta(days=days), "low", 0.9)
                   ["woken"] for i in range(2000)) / 2000
    assert share(3) > share(8) > share(20) > 0
    assert share(EARLY_WINDOW_DAYS + 1) == 0 == share(0)


def test_the_store_finds_only_a_difficulty_contact_inside_the_window():
    store = ContactsReceived()
    store.receive("A", DUE - timedelta(days=1), EARLY_CONTACT_INSTRUMENT)
    store.receive("A", DUE + timedelta(days=4), "cmoc_letter")
    assert store.first_contact_on("A", DUE, DUE + timedelta(days=30),
                                  EARLY_CONTACT_INSTRUMENT) is None
    store.receive("A", DUE + timedelta(days=9), EARLY_CONTACT_INSTRUMENT)
    store.receive("A", DUE + timedelta(days=6), EARLY_CONTACT_INSTRUMENT)
    assert store.first_contact_on("A", DUE, DUE + timedelta(days=30),
                                  EARLY_CONTACT_INSTRUMENT) == DUE + timedelta(days=6)
    with pytest.raises(ValueError):
        store.receive("A", DUE, "a letter nobody sourced")


def _contacted_book(monkeypatch, share, contact):
    monkeypatch.setattr(cr, "EARLY_CONTACT_SHARE", share)
    triad = LivePaymentTriad()
    triad.contacts_received = ContactsReceived()
    failed = []
    for i in range(300):
        cid = f"RESI{i:05d}"
        rec = triad.record_period(customer_id=cid, due_date=DUE, amount_gbp=80.0,
                                  income_stress_value="moderate", segment="resi")
        if rec["result"] == "DD_FAILED":
            failed.append(cid)
            if contact:
                assert triad._plan_seam.send_contact(f"ACC-{cid}", DUE + timedelta(days=2),
                                                     EARLY_CONTACT_INSTRUMENT)["sent"]
    for i in range(300):
        for m in (2, 3, 4, 5, 6, 7, 8):
            triad.record_period(customer_id=f"RESI{i:05d}", due_date=date(2020, m, 28),
                                amount_gbp=80.0, income_stress_value="low", segment="resi")
    triad.collections_journeys(date(2021, 6, 30))
    return triad, failed


def test_the_triad_pays_a_contacted_miss_at_the_window_end_and_drops_its_later_lump(monkeypatch):
    on, failed = _contacted_book(monkeypatch, 1.0, contact=True)
    summary = on.early_contact_summary()
    assert failed and summary["contacted"] == summary["paid"] > 0, summary
    off, _ = _contacted_book(monkeypatch, 1.0, contact=False)
    assert off.early_contact_summary()["contacted"] == 0
    # A contacted January miss crosses at the window's end, once: no later lump for it crosses too.
    # Misses the bank's re-presentation already settled inside the window are never checked.
    early = DUE + timedelta(days=EARLY_WINDOW_DAYS)
    crossed_jan = [c for c in on._crossed_settlements if c[1] == DUE]
    assert all(c[2] <= early for c in crossed_jan), "a contacted miss was also paid later"
    assert sum(c[2] == early for c in crossed_jan) == summary["paid"]
    assert len({c[0] for c in crossed_jan}) == len(crossed_jan), "a bill crossed twice"
    late_off = [c for c in off._crossed_settlements if c[1] == DUE and c[2] > early]
    assert late_off and summary["later_lumps_replaced"] == len(late_off), (
        "without the contact those misses are repaid later, and only those lumps are replaced")
