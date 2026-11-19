"""Every stock prepayment household has a meter that can go off supply, and some go off for over
3 hours (energy_vulnerability_observables_prepayment_and_self_disconnection_2026-11-19.md
s.7a).

Defect each leg names: a world where only a debt-fitted meter reports, so the ~14% who already
prepay assert zero harm (K2); a meter reported for every household, prepayer or not; a feed
that reports weeks before the supplier supplied the household; an over-3h flag that is always
or never set; adding the flag moving a debt meter's interruptions.
"""
from __future__ import annotations

import datetime as dt

from background.live_payment_triad import LivePaymentTriad
from company.interfaces.sim_interface import LiveSimInterface
from simulation.household_segments import PaymentChannel, payment_channel_for_customer
from simulation.payment_method_dynamics import (
    meter_supply_events,
    summarise_supply_events,
)
from simulation.plan_offer_response import HouseholdPlanBook

SEED = 20240101
START = dt.date(2024, 1, 1)


def test_the_triad_gives_a_reporting_meter_to_every_prepayer_and_to_no_one_else():
    triad = LivePaymentTriad()
    book = triad._household_plans
    channel = {}
    for i in range(120):
        cid = f"RESI{i:05d}"
        channel[cid] = payment_channel_for_customer(cid)
        triad.record_period(customer_id=cid, due_date=dt.date(2024, 2, 28), amount_gbp=90.0,
                            income_stress_value="low", segment="resi", bill_month="2024-01")
    prepayers = {c for c, ch in channel.items() if ch is PaymentChannel.PREPAYMENT}
    # The partition must hold both sides, or the leg below cannot fail.
    assert prepayers and set(channel) - prepayers
    for cid in channel:
        since = book.reporting_meter_from(f"ACC-{cid}")
        assert (since == START) == (cid in prepayers), (cid, channel[cid], since)


def test_a_stock_meter_goes_off_supply_at_the_weekly_share_and_most_spells_are_severe():
    through = START + dt.timedelta(days=7 * 52)
    feeds = {f"A{n}": meter_supply_events(f"A{n}", START, through, base_seed=SEED)
             for n in range(800)}
    s = summarise_supply_events(feeds)
    rate = s["interruptions"] / (800 * 52)
    assert 0.014 < rate < 0.024, rate               # the toggle's 0.019
    severe = s["interruptions_over_3h"] / s["interruptions"]
    assert 0.53 < severe < 0.72, severe             # the toggle's 0.627
    assert 0 < s["prepayers_over_3h"] < s["prepayers_interrupted"] < s["prepayers_on_meter"]


def test_the_flag_leaves_a_debt_meters_interruptions_where_they_were():
    feed = meter_supply_events("C1", START, START + dt.timedelta(days=700), base_seed=SEED,
                               weekly_share=0.3)
    for over_3h in (0.0, 1.0):
        other = meter_supply_events("C1", START, START + dt.timedelta(days=700), base_seed=SEED,
                                    weekly_share=0.3, over_3h_share=over_3h)
        assert [e["on"] for e in other["interruptions"]] == [e["on"] for e in feed["interruptions"]]
        assert {e["over_3h"] for e in other["interruptions"]} == {bool(over_3h)}


def test_the_seam_reports_a_stock_meter_from_supply_and_a_debt_meter_from_its_fitting():
    book = HouseholdPlanBook()
    live = LiveSimInterface(household_plans=book)
    book.note_prepaying("S1", START)
    book.note_prepaying("S1", START + dt.timedelta(days=60))       # a later bill: start stands
    assert not live.get_meter_supply_events("S1", "2023-12-31")["on_meter"]
    feed = live.get_meter_supply_events("S1", "2025-01-01")
    assert feed["on_meter"] and all(e["on"] > START.isoformat() for e in feed["interruptions"])
    book.record_meter("D1", START + dt.timedelta(days=30), 250.0)
    book.note_prepaying("D1", START)
    assert book.reporting_meter_from("D1") == START + dt.timedelta(days=30)
    assert sorted(book.prepaying_accounts()) == ["D1", "S1"]
