"""A prepayment leg is sent a statement of what its meter charged, never an estimated credit bill.

Defect this guards (2026-10-26, SEAT_FINDING_A_PREPAYMENT_HOUSEHOLD_IS_SENT_ESTIMATED_CREDIT_BILLS):
the company was told a leg paid by prepayment and billed it on the monthly credit cycle anyway, so
136 of 164 prepayment legs on the 4ae8da9b0f book were sent bills on an estimated read. A meter is
paid before use, so there is nothing to estimate and nothing to true up
(docs/market_research/what_a_prepayment_customer_is_sent_2026-10-26.md).

The bills come from the company's own `build_monthly_bills` with a feed on which no read arrives
after January 2023. C1 (P) pays by prepayment and C2 (D) by direct debit, on identical use.

Mutations, each run and reverted: the prepayment branch in `build_monthly_bills` dropped (P is
estimated again), `document_for_channel` returning a bill for every channel, and the read duty
register's meter-charged clause dropped (P's unread year leaves the register). Each reds the single
assertion.
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass

from company.billing.monthly_bill_assembly import build_monthly_bills
from company.billing.read_duty_register import read_duty_register
from saas.bill_generator import CHARGED_AT_THE_METER, CREDIT_BILL, PREPAYMENT_STATEMENT

MONTHS = [(yr, mo) for yr in (2023, 2024) for mo in range(1, 13)]


def _records():
    out = []
    for cid in ("C1", "C2"):
        for yr, mo in MONTHS:
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
            } for d in range(1, calendar.monthrange(yr, mo)[1] + 1))
    return out


@dataclass
class _Read:
    status: str
    estimated_consumption_kwh: float | None
    consecutive_estimated_count: int


class _Feed:
    def meter_type_for(self, customer):
        return "traditional"

    def read_for(self, customer_id, period_end, meter_type, true_kwh, consecutive):
        if period_end.startswith("2023-01"):
            return _Read("actual", None, 0)
        return _Read("estimated", None, consecutive + 1)

    final_read_for = read_for


def test_a_prepayment_leg_is_charged_at_the_meter_and_a_credit_leg_on_the_same_feed_is_estimated():
    bills = build_monthly_bills(
        _records(), _Feed(),
        payment_channel_feed=lambda c: "prepayment" if c["customer_id"] == "C1" else "direct_debit")
    by = {k: [b for b in bills if b["customer_id"] == cid] for k, cid in (("P", "C1"), ("D", "C2"))}
    assert (
        len(by["P"]), len(by["D"]),
        # The partition: the estimate branch is taken on the credit leg and never on the meter.
        sum(b["billing_basis"] == "estimated" for b in by["D"]),
        sum(b["billing_basis"] == "estimated" for b in by["P"]),
        {b["billing_basis"] for b in by["P"]},
        {b["document"] for b in by["P"]}, {b["document"] for b in by["D"]},
        # Charged on what was used: no estimate, no catch-up.
        any(b.get("catchup_applied") or b.get("estimated_consumption_kwh") for b in by["P"]),
        # The settlement read still goes a year unread, and the register still says so.
        [(r["account_id"], r["duty_applies"]) for r in read_duty_register(bills)],
    ) == (
        24, 24, 23, 0, {CHARGED_AT_THE_METER}, {PREPAYMENT_STATEMENT}, {CREDIT_BILL}, False,
        [("C1", False), ("C2", True)],
    )
