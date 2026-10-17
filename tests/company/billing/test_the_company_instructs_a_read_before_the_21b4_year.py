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

from company.billing.monthly_bill_assembly import build_monthly_bills
from company.billing.read_duty_register import read_duty_register, read_instruction_register

MONTHS = [(yr, mo) for yr in (2023, 2024) for mo in range(1, 13)] + [(2025, m) for m in (1, 2, 3)]
ACCOUNTS = ("C1", "C2", "C3", "C4", "C5")
VISIT_READS = {"C1": True, "C2": True, "C3": False, "C4": True, "C5": False}


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


def test_off_by_default_the_run_bills_byte_for_byte_as_before_and_asks_for_no_visit():
    class _NoVisitFeed(_Feed):
        instructed_read_for = None  # a feed without the method must still bill with the switch off

    default = _bills(_NoVisitFeed())
    assert default == _bills(_Feed(), instruct_reads=False)
    assert not any(k.startswith("read_instruction") for b in default for k in b)
    assert read_instruction_register(default) == []
