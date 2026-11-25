"""Every `epg_support_gbp` a bill carries is booked as a receipt, held bills included.

The defect this names: the close booked the Treasury's EPG receipt off ISSUED bills only, so a bill
the Tier-1 gate held took its month's receipt out of the books. The scheme paid on settled volume,
never on the bill (`docs/market_research/default_tariff_cap_and_epg_on_the_bill.md`). On
f2c6979d01's book that was GBP 1,338.06, two held bills of SYN-2016-175_3, and the publisher refused
the run (`tools/grade_svt_invoices_over_ceiling.epg_receipt`).

The held bill's CHARGE must still stay out of the books: that is the issuance gate's own control
(`tests/company/interfaces/test_accounting_close_seam.py`), asserted again here so the fix cannot
be "post the held bill".
"""

from __future__ import annotations

import pytest

from company.finance import accounting_close as impl
from tools.grade_svt_invoices_over_ceiling import epg_receipt


def _bill(customer_id: str, start: str, end: str, net: float, epg: float) -> dict:
    commodity = round(net * 0.70, 2)
    non_commodity = round(net * 0.20, 2)
    standing = round(net - commodity - non_commodity, 2)
    vat = round((commodity + non_commodity + standing) * 0.05, 2)
    return {
        "customer_id": customer_id,
        "segment": "resi",
        "commodity": "electricity",
        "period_start": start,
        "period_end": end,
        "total_consumption_kwh": 300.0,
        "commodity_amount_gbp": commodity,
        "non_commodity_amount_gbp": non_commodity,
        "standing_charge_gbp": standing,
        "vat_gbp": vat,
        "total_amount_gbp": round(commodity + non_commodity + standing + vat, 2),
        "hmt_epg_receipt_gbp": epg,
        "epg_support_gbp": epg + 1.25,  # settled share differs from the billed one
    }


class _NoProvisionModel:
    CREDIT_RISK_BY_CUSTOMER: dict[str, str] = {}
    DEFAULT_CREDIT_RISK = "low"

    @staticmethod
    def bad_debt_provision_gbp(credit_risk, amount_gbp):  # noqa: ARG004
        return 0.0

    @staticmethod
    def expected_payment_date(period_end, credit_risk):  # noqa: ARG004
        return period_end


def _close():
    issued = _bill("C1", "2022-12-01", "2022-12-31", 120.0, 40.0)
    held = _bill("C_HELD", "2023-03-01", "2023-03-31", 500.0, 740.20)
    held["total_amount_gbp"] = 9_999.00  # does not foot: the gate HOLDS it
    bills = [issued, held]
    closed = impl.close_the_books([], bills, payment_model=_NoProvisionModel)
    return bills, closed


def test_every_bills_epg_support_is_booked_as_a_receipt_held_ones_included():
    bills, closed = _close()
    assert [h.customer_id for h in closed.held_bills] == ["C_HELD"], "fixture no longer holds"
    paid = sum(b["epg_support_gbp"] for b in bills)
    assert closed.pnl["epg_receipt_gbp"] == pytest.approx(paid)
    # ...and the grader that refused f2c6979d01 agrees, on these books.
    grade = epg_receipt({"bills": bills, "ledger_pnl": closed.pnl})
    assert grade["paid_gbp"] == grade["booked_gbp"]


def test_the_held_bills_charge_still_never_reaches_the_books():
    _, closed = _close()
    billed = [e for e in closed.events if e["event_type"] == "billing_event"]
    assert {e["customer_id"] for e in billed} == {"C1"}
    assert closed.meta["billed_clock_reconciles_with_issued_bills"] is True


def test_mutation_booking_from_issued_bills_only_is_caught(monkeypatch):
    """Perform the defect: the close as it stood at f2c6979d01, receipts off issued bills only."""
    monkeypatch.setattr(impl, "held_bill_epg_receipts", lambda bills, held: [])
    bills, closed = _close()
    grade = epg_receipt({"bills": bills, "ledger_pnl": closed.pnl})
    assert grade["paid_gbp"] - grade["booked_gbp"] == pytest.approx(741.45)
