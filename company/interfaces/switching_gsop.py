"""The company's SWITCHING-GSOP surface: the one place the world reports a won switch's
registration facts and learns what the gaining supplier owes on them under regs 6ZA and 6ZB.

Knowledge: `docs/market_research/switching_mechanics_2026-10-25.md` s.6. The regulations are
applied by `company/regulatory/gsop.py`; this door only feeds it the supplier's own records.

WHAT CROSSES
------------
In, per won switch (`simulation/gain_registration.py`): the day the supplier held enough
information to confirm the customer, the contract day, the day the registration service confirmed
the transfer, and the day the two suppliers agreed the transfer had no valid contract (or None).
Every one is a record a real gaining supplier holds: its own sales system, the registration
service's confirmation, and the inter-supplier erroneous-transfer agreement (s.6, "What the
supplier can observe"). Nothing about whether the household really contracted crosses; only the
agreement both suppliers hold.

Out: plain dicts, one per payment owed: the standard, its regulation, the day it was failed, the
amount, the day it is due and the day the company pays, and the account credit that payment is.
No `GSOPBook`, no `GSOPType` and no `GSOPPayment` leave this module (imported inside the function,
as `credit_refund_requests` does, so the door's namespace stays what it exports).

THE COMPANY'S OWN CHOICE: it pays every switching standard payment by credit to the customer's
account on the last day reg 8(2) allows, 10 working days after the failure. That is compliant and
it is the latest compliant day; an earlier payment run is a supplier choice nothing here measures.
"""
from __future__ import annotations

import datetime as dt

__all__ = ["switching_payments_on_gains"]


def _day(value) -> dt.date | None:
    if value is None or isinstance(value, dt.date):
        return value
    return dt.date.fromisoformat(value)


def switching_payments_on_gains(gains: list[dict]) -> list[dict]:
    """Every reg 6ZA and 6ZB standard payment owed on ``gains``, in the order the gains came.

    Each gain is ``customer_id``, ``information_received_on``, ``contract_on``,
    ``registration_confirmed_on`` and ``erroneous_transfer_agreed_on`` (ISO strings or dates; the
    last may be None). A gain whose standard was not in force on the day owes nothing and returns
    nothing. Each answer: ``customer_id``, ``standard``, ``regulation``, ``failed_on``,
    ``amount_gbp``, ``due_on``, ``paid_on`` and ``posted_as`` ("account_credit").
    """
    from company.regulatory.gsop import (
        SWITCHING_STANDARDS,
        GSOPBook,
        GSOPType,
        switch_speed_deadline,
        switch_speed_failed_on,
    )

    book = GSOPBook()
    answers: list[dict] = []

    def _owe(customer_id: str, gsop_type: GSOPType, failed_on: dt.date) -> None:
        payment = book.record_trigger(customer_id, gsop_type, failed_on)
        # The company pays on the last day the payment is due: `payment_due_date` is reg 8(2)'s
        # 10 working days, computed by the book.
        paid_on = payment.payment_due_date
        book.pay(payment.payment_id, paid_on)
        answers.append({
            "customer_id": customer_id,
            "standard": gsop_type.value,
            "regulation": SWITCHING_STANDARDS[gsop_type].regulation,
            "failed_on": failed_on.isoformat(),
            "amount_gbp": payment.amount_gbp,
            "due_on": payment.payment_due_date.isoformat(),
            "paid_on": paid_on.isoformat(),
            "posted_as": "account_credit",
        })

    for gain in gains:
        cid = gain["customer_id"]
        deadline = switch_speed_deadline(_day(gain["information_received_on"]),
                                         _day(gain["contract_on"]))
        failed = switch_speed_failed_on(deadline, _day(gain["registration_confirmed_on"]))
        if failed is not None:
            _owe(cid, GSOPType.SWITCH_SPEED, failed)
        agreed = _day(gain.get("erroneous_transfer_agreed_on"))
        # Reg 6ZB is failed on the day the suppliers agree; before 1 May 2020 it did not exist.
        if agreed is not None and agreed >= SWITCHING_STANDARDS[GSOPType.ERRONEOUS_TRANSFER].in_force_from:
            _owe(cid, GSOPType.ERRONEOUS_TRANSFER, agreed)
    return answers
