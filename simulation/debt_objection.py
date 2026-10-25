"""The domestic debt objection, world side: the world completes or cancels a switch the losing
supplier objected to, and keeps only what the household does next.

THE LAW. Under SLC 14 a supplier may object to the transfer of a domestic customer who owes it
money outstanding for more than 28 days since the customer was told of it in writing, and an
objection stops the transfer. Source: `docs/market_research/domestic_debt_objection_rates_gb.md`.

WHO DECIDES. The losing supplier, from its own ledger, at the switch request
(`company/interfaces/transfer_objection.py`, EP12). Until 2026-10-25 this module drew the block
itself: P(blocked | indebted credit household) = 170k / (170k + 430k) = 0.283, Ofgem's 2013-15
counts, read off the world's own payment truth. That made the outcome of a supplier decision a
property of the world, so no company could earn or lose anything by how it objected. Those
published counts are now what the company's OUTPUT is graded against, never an input.

THE WORLD'S PART. The switch request reaches the loser on `objection_request_day`; an objection
cancels the switch (`apply_objection`), so the household stays on its renewal.

NAMED GAPS, each moving the effect in a stated direction:

1. THE REQUEST DAY. A CSS request is read at the latest submission day the rules allow
   (`registration_loss_feed.switch_request_day`). Before CSS a loser had about a week's
   window inside a switch of about three weeks, so it learned of the request earlier; reading its
   ledger on the same late floor lets more bills pass the 28-day clock and can only overstate
   pre-CSS objections.
2. A BLOCK IS FINAL FOR THIS DECISION. A blocked household stays this renewal and is asked again
   at the next one. Ofgem's IA (rows 22-23) has about half of blocked customers repaying, and
   27-39% of repayers switching within a year; no repay-and-leave-between-renewals route is
   modelled, so the world holds a blocked household at least as long as the record does.
3. RENEWAL DEPARTURES ONLY. The C1b inertia exit (an SVT household leaving between renewals) is not
   offered to the company's objection.
4. THE LEVEL ANCHOR ALREADY CONTAINS IT. `departure_level_anchor` is fitted to published realised
   switching, which already nets out blocked switches; with objections on, the world departs below
   that record until the anchor is re-fitted. Re-fitting is a separate decision.

THE SWITCH. `SE_DEBT_OBJECTION=0` stops the switch request reaching the company's objection, so a
run can be re-taken without it. Default ON: it is the published law (R13).
"""
from __future__ import annotations

import os
from datetime import date

from simulation.registration_loss_feed import switch_request_day

#: SLC 14: a supplier may not object for a debt outstanding fewer than 28 days since written notice.
#: Source: docs/market_research/domestic_debt_objection_rates_gb.md row 17. The bill is the written
#: notice and the clock runs from its due date.
DEBT_OBJECTION_MIN_DAYS_OUTSTANDING = 28

#: The world switch. Unset or anything but "0" = ON.
DEBT_OBJECTION_ENV = "SE_DEBT_OBJECTION"


def debt_objection_active() -> bool:
    """True unless `SE_DEBT_OBJECTION=0`. Read per call so a test or a re-take can flip it."""
    return os.environ.get(DEBT_OBJECTION_ENV, "").strip() != "0"


def objection_request_day(supply_effective_from_date: date) -> date:
    """The day the losing supplier is asked: the latest submission day for this effective date
    (gap 1)."""
    return switch_request_day(supply_effective_from_date)


def apply_objection(event: dict, objected: bool) -> dict:
    """The world's answer to the company's decision: an objection cancels the switch, so a
    departure becomes a stay on the same renewal. The household's own roll is kept, and the event
    records that it was the objection, not the household, that kept it."""
    blocked = bool(objected) and event["event_type"] == "churned"
    out = dict(event, departure_blocked_by_debt_objection=blocked)
    if blocked:
        out.update(event_type="renewed", departure_cause=None)
    return out
