"""The company instructs a read on the 11th estimate in a row, once in each year of a run, and the
visit's answer decides the next bill.

Defect this guards (2026-10-17, direction item `the-company-instructs-a-read-before-the-21b4-year`,
docs/market_research/read_access_and_theft_duties.md s.2.8): the 21B.4 register (c5963a5c0) let the
company see the year pass, and it still took no step to get a read.

The bills come from the company's own `build_monthly_bills` with a scripted feed. Every account is
read in January 2023 and its ordinary reads then fail, except C1's, which arrives after 10
estimates, and C5's, which arrives in the very period an instruction's visit falls in. The visit
reads for C2, finds no access for C3 and C5, and C4 pays by prepayment.

Mutations, each run and reverted: `READ_INSTRUCTION_AT_ESTIMATES` at 10 (one bill early) or at 12
(one bill late), `%` dropped (one instruction per run), the prepayment exclusion dropped, and the
visit asked when the ordinary read already arrived. Each reds the single assertion of the partition.
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass

import pytest

from company.billing.monthly_bill_assembly import build_monthly_bills
from company.billing.read_duty_register import (
    read_duty_register,
    read_duty_summary,
    read_instruction_register,
    read_visit_cost_schedule,
)
from company.finance.accounting_close import close_the_books
from company.finance.double_entry import build_journal

MONTHS = [(yr, mo) for yr in (2023, 2024) for mo in range(1, 13)] + [(2025, m) for m in (1, 2, 3)]
ACCOUNTS = ("C1", "C2", "C3", "C4", "C5")
VISIT_READS = {"C1": True, "C2": True, "C3": False, "C4": True, "C4g": False, "C5": False}


def _records():
    out = []
    for cid in ACCOUNTS:
        for yr, mo in MONTHS:
            days = calendar.monthrange(yr, mo)[1]
            out.extend({
                "customer_id": cid,
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


@dataclass
class _Read:
    status: str
    estimated_consumption_kwh: float | None
    consecutive_estimated_count: int


class _Feed:
    def __init__(self):
        self.visits = []

    def meter_type_for(self, customer):
        return "traditional"

    def read_for(self, customer_id, period_end, meter_type, true_kwh, consecutive):
        index = MONTHS.index((int(period_end[:4]), int(period_end[5:7])))
        if index == 0 or (customer_id, index) in {("C1", 11), ("C5", 12)}:
            return _Read("actual", None, 0)
        return _Read("estimated", None, consecutive + 1)

    def final_read_for(self, customer_id, period_end, meter_type, true_kwh, consecutive):
        return self.read_for(customer_id, period_end, meter_type, true_kwh, consecutive)

    def instructed_read_for(self, customer_id, period_end, meter_type, true_kwh, consecutive):
        self.visits.append((customer_id, period_end))
        if VISIT_READS[customer_id]:
            return _Read("actual", None, 0)
        return _Read("estimated", None, consecutive + 1)


def _channel(customer):
    return "prepayment" if customer["customer_id"] == "C4" else "direct_debit"


def _bills(feed, **kw):
    return build_monthly_bills(_records(), feed, payment_channel_feed=_channel, **kw)


def test_the_instruction_falls_on_the_eleventh_estimate_once_a_year_and_the_visit_decides_the_year():
    feed = _Feed()
    bills = _bills(feed, instruct_reads=True)
    rows = read_instruction_register(bills)
    year = [(r["account_id"], r["date"]) for r in read_duty_register(bills)]
    assert (
        [(r["account_id"], r["raised"], r["visit_period_end"], r["outcome"]) for r in rows],
        feed.visits, year,
    ) == (
        [
            # C1: its own read after 10 estimates needs no visit; its next run's 11th does.
            ("C1", "2024-11-30", "2024-12-31", "actual"),
            # C2: read at the visit, so a fresh run starts and the next falls 12 bills on.
            ("C2", "2023-12-31", "2024-01-31", "actual"),
            ("C2", "2024-12-31", "2025-01-31", "actual"),
            # C3: no access, so the run goes on and the next year's instruction is its 23rd.
            ("C3", "2023-12-31", "2024-01-31", "no_read"),
            ("C3", "2024-12-31", "2025-01-31", "no_read"),
            # C5: its own read arrived in the visit's period, so no visit was asked for.
            ("C5", "2023-12-31", "2024-01-31", "actual"),
            ("C5", "2024-12-31", "2025-01-31", "no_read"),
        ],
        [("C1", "2024-12-31"), ("C2", "2024-01-31"), ("C2", "2025-01-31"), ("C3", "2024-01-31"), ("C3", "2025-01-31"),
         ("C5", "2025-01-31")],
        # The 21B.4 year: C3's run still reaches it, C2's never does; C4 is prepayment.
        [("C3", "2024-01-31"), ("C4", "2024-01-31"), ("C5", "2025-01-31")],
    )


def test_gas_prepayment_is_instructed_under_m5_9_14_and_electricity_prepayment_is_not():
    """Defect (2026-10-22, unbilled_energy_and_revenue_assurance.md K2): the exemption covered
    prepayment on both fuels, so the 26 gas PPM runs of 12+ estimates on the 76a29bd92 run got no
    step. 21B.3 excludes electricity prepayment; UNC TPD M5.9.14 applies the gas annual read to it.
    C4 (electricity) and C4g (gas) both pay by prepayment and are never read after January 2023.
    The 21B.4 register, the licence's test, still marks both rows outside the duty.

    Mutations, each run and reverted: the fuel test dropped (gas PPM exempt again), the exemption
    dropped (electricity PPM instructed). Each reds the one assertion."""
    feed = _Feed()
    records = [dict(r, customer_id=cid) for cid in ("C4", "C4g")
               for r in _records() if r["customer_id"] == "C1"]
    bills = build_monthly_bills(records, feed, payment_channel_feed=lambda c: "prepayment",
                                instruct_reads=True)
    assert (
        sorted({b["customer_id"]: b["commodity"] for b in bills}.items()),
        [(r["account_id"], r["visit_period_end"], r["outcome"]) for r in read_instruction_register(bills)],
        [(r["account_id"], r["duty_applies"]) for r in read_duty_register(bills)],
    ) == (
        [("C4", "electricity"), ("C4g", "gas")],
        [("C4g", "2024-01-31", "no_read"), ("C4g", "2025-01-31", "no_read")],
        [("C4", False), ("C4g", False)],
    )


def test_off_by_default_the_run_bills_byte_for_byte_as_before_and_asks_for_no_visit():
    class _NoVisitFeed(_Feed):
        instructed_read_for = None  # a feed without the method must still bill with the switch off

    default = _bills(_NoVisitFeed())
    assert default == _bills(_Feed(), instruct_reads=False)
    assert not any(k.startswith("read_instruction") for b in default for k in b)
    assert read_instruction_register(default) == []


def test_a_visit_is_charged_in_its_month_only_where_one_went_out():
    """Defect (2026-10-21, s.2.9): the instruction performs the 21B.4 step for nothing (an invented
    zero, K2), or charges an instruction whose ordinary read came in first and so sent no visit
    (C5's January 2024). The partition: off charges nothing; on charges each visit the feed was
    asked for, at £3, whether it read (C1, C2) or found no access (C3, C5), with £17.50 the bound.

    Mutations, each run and reverted: the `visit_sent` skip dropped (C5's January is charged), the
    schedule dated by `raised` not the visit period, and the price set to the bound. Each reds this."""
    feed = _Feed()
    bills = _bills(feed, instruct_reads=True)
    schedule = read_visit_cost_schedule(bills)
    cost = read_duty_summary(bills)["visit_cost"]
    assert (
        read_visit_cost_schedule(_bills(_Feed(), instruct_reads=False)),
        schedule, sum(e["amount_gbp"] for e in schedule) == 3.0 * len(feed.visits),
        (cost["instructions"], cost["visits"], cost["charged_gbp"], cost["upper_bound_gbp"]),
    ) == (
        [],
        [{"month": "2024-01", "amount_gbp": 6.0}, {"month": "2024-12", "amount_gbp": 3.0},
         {"month": "2025-01", "amount_gbp": 9.0}],
        True,
        (7, 6, 18.0, 105.0),
    )


def test_bills_that_predate_the_visit_flag_publish_no_visit_count_rather_than_one_per_instruction():
    """Defect: a pre-2026-10-21 run output, which never said whether a visit went out, is published
    as if every instruction sent one (582 where 469 went out on the 8927e9345 register arm)."""
    bills = _bills(_Feed(), instruct_reads=True)
    for bill in bills:
        bill.pop("read_instruction_visit_sent", None)
    cost = read_duty_summary(bills)["visit_cost"]
    assert (cost["instructions"], cost["visits"], "charged_gbp" in cost) == (7, None, False)


def test_the_close_posts_the_visits_to_account_6100_and_off_the_operating_margin():
    """Defect: the schedule is computed and never booked, so the published P&L shows the duty done
    for free. The close of the same bills with and without the instruction differs by the visits."""
    records = _records()
    on = close_the_books(records, _bills(_Feed(), instruct_reads=True))
    off = close_the_books(records, _bills(_Feed(), instruct_reads=False))
    posted = [e for e in on.events if e["event_type"] == "read_visit_cost_event"]
    assert (
        [e for e in off.events if e["event_type"] == "read_visit_cost_event"],
        sorted((e["month"], e["amount_gbp"]) for e in posted),
        on.pnl.get("read_visit_cost_gbp"),
    ) == (
        [], [("2024-01", -6.0), ("2024-12", -3.0), ("2025-01", -9.0)], 18.0,
    )
    journal = [(j["debit_account"], j["credit_account"], j["amount_gbp"])
               for j in build_journal(posted)]
    assert journal == [("6100", "1001", 6.0), ("6100", "1001", 3.0), ("6100", "1001", 9.0)]
    assert on.pnl["operating_net_margin_gbp"] == pytest.approx(
        on.pnl["net_margin_gbp"] - 18.0 - on.pnl.get("acquisition_spend_gbp", 0.0)
        - on.pnl.get("fixed_cost_gbp", 0.0) - on.pnl.get("cost_to_serve_gbp", 0.0))


def test_a_year_on_estimates_with_no_step_is_counted_and_one_with_a_failed_visit_is_not():
    """Defect this guards (2026-10-26, SEAT_FINDING_A_THIRD_OF_HOUSEHOLDS_GO_MORE_THAN_A_YEAR_ON_
    ESTIMATES_WITHOUT_THE_READ_DUTY_FIRING): 250 households a year on estimates read as the duty
    not firing, and nothing published could say whether the step was taken. Each 21B.4 row now
    says so. With instructions on, C3 and C5 reach the year after a visit that found no access:
    step taken, none counted. With them off, C1, C2, C3 and C5 all reach a year with no step, and every
    duty-applying row is counted; C4 (electricity prepayment) is outside the duty either way.

    Mutations, each run and reverted: `step_taken` hard-wired True (the off arm counts 0) or
    False (the on arm counts 2), and the count taken over prepayment rows too (the off arm counts
    5). Each reds the one assertion, whose two arms are the partition: both branches occur."""
    def without_step(bills):
        return read_duty_summary(bills)["by_fuel"]["electricity"]["rows_without_step"]

    on, off = _bills(_Feed(), instruct_reads=True), _bills(_Feed(), instruct_reads=False)
    assert (
        [(r["account_id"], r["step_taken"]) for r in read_duty_register(on) if r["duty_applies"]],
        without_step(on), without_step(off),
    ) == ([("C3", True), ("C5", True)], 0, 4)
