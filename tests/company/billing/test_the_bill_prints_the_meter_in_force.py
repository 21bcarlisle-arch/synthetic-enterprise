"""A bill prints the meter on the wall at its read date, not the meter the account opened on.

Defect this guards (2026-11-15, D48 P0,
docs/staging/records/SEAT_PREREG_THE_SMART_METER_EXCHANGE_SWITCH_FOR_D48_2026-11-15.md):
`build_monthly_bills` asked `read_feed.meter_type_for` once per account and stamped that type on
every bill. With `meter_reads.SMART_METER_EXCHANGE` on, the world reads an exchanged meter as smart
while the bill, the raw export, the read-duty register and K2's meter split all kept it in the
traditional cell, where a falling estimated share would be read as better reading of dumb meters.

The supplier learns of the exchange from its own metering record, which the feed carries as
`meter_in_force`; nothing here reads the world's exchange draw. Premise X5 at base seed 42,
acquired 2022-01-15, is exchanged on 2023-05-08 (`life_events.smart_meter_installed_event`).

Mutation, run and reverted 2026-11-15: stamping `meter_type` once per account again
(`bill["meter_type"] = meter_type`) reds the first test.
"""

from __future__ import annotations

import calendar
import json

import pytest

import company.billing.monthly_bill_assembly as assembly
from company.billing.monthly_bill_assembly import build_monthly_bills
from company.billing.read_duty_register import read_duty_register
from simulation.meter_reads import SimulatedReadFeed

CID = "X5"
EXCHANGED_ON = "2023-05-08"
MONTHS = [(2023, m) for m in range(1, 13)]


def _records():
    out = []
    for yr, mo in MONTHS:
        days = calendar.monthrange(yr, mo)[1]
        out.extend({
            "customer_id": CID,
            "settlement_date": f"{yr}-{mo:02d}-{d:02d}",
            "settlement_period": 1,
            "consumption_kwh": 10.0,
            "unit_rate_gbp_per_mwh": 200.0,
            "revenue_gbp": 0.01 * 200.0 + 0.5,
            "standing_charge_gbp": 0.5,
            "wholesale_cost_gbp": 0.0,
            "margin_gbp": 0.0,
        } for d in range(1, days + 1))
    return out


@pytest.fixture
def traditional_account(monkeypatch):
    monkeypatch.setattr(assembly, "get_customer", lambda cid: {
        "customer_id": cid, "commodity": "electricity", "acquisition_date": "2022-01-15",
        "smart_meter": False, "contract_type": "fixed_1yr", "segment": "resi"})


def _bills(feed):
    events: list = []
    bills = build_monthly_bills(_records(), feed, read_events_out=events)
    return bills, events


def test_an_account_exchanged_mid_life_bills_traditional_before_its_exchange_and_smart_after(
        traditional_account):
    bills, events = _bills(SimulatedReadFeed(smart_meter_exchange=True, base_seed=42))
    printed = {b["period_end"]: b["meter_type"] for b in bills}
    # The partition can be taken both ways: a stamp that never changes fails here, not silently.
    assert set(printed.values()) == {"traditional", "smart"}, printed
    assert printed == {pe: ("smart" if pe >= EXCHANGED_ON else "traditional") for pe in printed}
    # The bill agrees with the meter the read came from, period by period.
    assert printed == {e.period_end: e.meter_type for e in events}


def test_the_read_duty_register_carries_the_meter_the_bill_printed():
    bills = [{"customer_id": "A", "commodity": "gas", "period_end": "2024-01-31",
              "billing_basis": "estimated", "consecutive_estimated_count": 12,
              "payment_channel": "direct_debit", "meter_type": "smart"}]
    assert [r["meter_type"] for r in read_duty_register(bills)] == ["smart"]


class _OneTypePerAccount:
    """The feed as it was before P0: no `meter_in_force`, so the account's one type is stamped."""

    def __init__(self, feed):
        self._feed = feed
        self.meter_type_for = feed.meter_type_for
        self.read_for = feed.read_for
        self.final_read_for = feed.final_read_for
        self.instructed_read_for = feed.instructed_read_for


def test_with_the_switch_off_the_bill_run_is_byte_identical_to_one_type_per_account(
        traditional_account):
    now, _ = _bills(SimulatedReadFeed(smart_meter_exchange=False, base_seed=42))
    before, _ = _bills(_OneTypePerAccount(SimulatedReadFeed(smart_meter_exchange=False, base_seed=42)))
    assert json.dumps(now, sort_keys=True, default=str) == json.dumps(before, sort_keys=True, default=str)
    assert {b["meter_type"] for b in now} == {"traditional"}
