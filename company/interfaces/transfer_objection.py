"""The door the world asks through when a domestic household asks to switch away: does the company
object for debt?

WHO DECIDES. The company, from its own ledger (EP12, 2026-10-25). Until this door the world drew
the objection itself, blocking an indebted credit household's departure at Ofgem's 2013-15 blocked
share of 0.283 off its own payment truth, so the supplier never made the decision the licence
gives it. Knowledge: `docs/market_research/switching_mechanics_2026-10-25.md` section 2.

WHAT CROSSES. In: the supply point, the day the company learns of the switch request, the
company's own unpaid bills by age, whether its own method register holds the account on
prepayment, and how many fuels the account carries. Out: a plain dict -- objected or not, the
reason, the objectionable debt, the objection id -- and no register object, ground enum or record.
The world reads `objected` and nothing else to cancel or complete the switch.
"""
from __future__ import annotations

import datetime as dt

from company.market.transfer_objection_register import (
    DebtObjectionPolicy,
    TransferObjectionRegister,
    decide_debt_objection,
)

__all__ = ["open_transfer_objection_register", "request_debt_objection"]


def open_transfer_objection_register() -> TransferObjectionRegister:
    """The company's objection register for one run, held by the run like its CoS register."""
    return TransferObjectionRegister()


def request_debt_objection(register: TransferObjectionRegister, supply_point_id: str,
                           request_day: str, unpaid_bills_by_age, *, prepayment: bool,
                           fuels: int) -> dict:
    """The company's answer to one domestic switch request on the debt ground, as plain values."""
    day = dt.date.fromisoformat(request_day)
    decision = decide_debt_objection(
        register, supply_point_id, f"SW-{supply_point_id}-{request_day}", day,
        unpaid_bills_by_age, prepayment=prepayment, fuels=fuels, policy=DebtObjectionPolicy())
    return {
        "objected": decision.objected,
        "reason": decision.reason,
        "objectionable_debt": decision.objectionable_debt,
        "objection_id": None if decision.record is None else decision.record.objection_id,
    }
