"""GSoP reg 6D credit-balance refund activation (labelled "SLC 14" until 2026-10-25, the wrong
locus: home_moves.md s.8.8) (Phase 3 item 2, docs/design/
CORE_FIDELITY_PHASES.md: "wire credit_refund.py into the live run -- it
already has the SLA mechanic, this is activation, not a build").

company/billing/credit_refund.py has a real refund-deadline mechanic
(CreditRefundBook, 10-working-day refund deadline) but grepping every file
in simulation/ for a caller returned nothing -- dead code (Phase 1 audit
finding #3). This module is the activation: it gives the mechanic something
real to fire on.

KNIFE pass 3 (B4, 2026-08-10) moved the mechanic itself back behind the wall.
This module no longer opens the company's compliance book: it reports the
closure, the final bill's issue date and the credit left in the account to
``company/interfaces/credit_refund_requests.py``, and logs what comes back.
The reg 6D deadline, the refund taxonomy and the breach verdict are the
supplier's, and are no longer readable from here. So, since 2026-10-25, is the day
the refund is paid: this module used to draw it, 90% within 10 working days and the
rest 11 to 25, a supplier's operating speed held as a property of the world and a
probability nobody had sourced. Those draws were every late refund in the run at
b2bc3d8da5 (10 of 100).

The credit is the run's own ledger balance at the final bill (`closing_balances`, from
``arrears_engine.balance_settlement_from_outcomes``: owed positive, credit negative, per fuel), not a
balance this module keeps. Until 2026-10-25 it fired from a level-DD smoothing balance of its own (the
trailing mean of a DD payer's bills less each bill). No household in the run ever paid a level DD:
the world has one payment truth and a paid bill is paid exactly. So that balance was money nobody had
collected, and the two books disagreed both ways. At 60 founders to 2020-12-31 the log refunded
SYN-2016-052, which the ledger says owes GBP 27.64, and refunded none of the 7 move-outs the ledger
closes in credit (home_moves.md s.8.8a). A level DD's over-collection belongs in that same ledger
(DD3, ``simulation/dd_balance_book.py``), and reaches the refund once it is posted there.

Reg 6D binds a domestic credit however it was paid, so every domestic leaver in credit is evaluated,
not only DD payers. Non-domestic accounts are not: the Standards of Performance are domestic.

The final bill's issue date is its period end: `company/billing/invoice.py` issues a bill at its
period end and the bill record carries no other date (home_moves.md s.8.8, choice 2). A corrected
final bill does not occur in this world.
"""
from __future__ import annotations

import datetime as dt

from company.interfaces.credit_refund_requests import refund_on_account_closure
from company.interfaces.dd_review_outcome import billing_account_of
from simulation.arrears_engine import bill_issue_date
from simulation.segment_vocabulary import RESIDENTIAL, normalise_segment


def generate_credit_refund_log(
    bills: list[dict],
    customer_segments: dict[str, str],
    closing_balances: dict[str, float],
    last_collection: dict[str, dt.date] | None = None,
    money_in: dict[str, dt.date] | None = None,
    later_cash: dict[str, list[tuple[dt.date, dt.date, float]]] | None = None,
) -> list[dict]:
    """One reg 6D refund event per closed domestic account the ledger closes in credit.

    ``closing_balances`` is the run's, account -> GBP owed (+) or held in credit (-) at the final
    bill, for leavers only. An account it does not hold is not evaluated: no balance is not a credit.
    The final bill is the account's last bill. Reg 6D's clock starts on the day it is issued,
    `bill_issue_date`, the day the ledger prints (s.8.8 choice 2, corrected 2026-11-12): from the
    period end, 134 of 176 clocks on the N29 replay started before the bill existed. Returns plain
    JSON-serialisable dicts.

    ``last_collection`` is a level-DD leaver's last level collection. One taken after the final
    bill is part of the credit, so the refund clock runs from the later of the two
    (home_moves.md s.8.8b choice 2).

    ``money_in`` is the day the last money a leaver's closing credit counts reached the account
    (`balance_settlement_from_outcomes`). A credit exists once its money does (SLC 27.16), so the
    clock runs from that day too when it is later (s.8.8d choice 18).

    A dual-fuel household whose other fuel closes owing hands that debt to the company with the
    credit. The company sets the credit against it first and refunds the rest (s.8.8e). Each event
    then carries ``set_off_gbp`` and ``set_off_against``, the debt leg. ``credit_amount_gbp`` is what
    is refunded, and it is 0.0 where the debt took the whole credit. Two credit legs on one
    household draw on its debt in leg order, so the debt is never set off twice.

    The debt is the other leg's on the refund day (s.8.8e choice 30): its closing balance plus the
    cash of every bill issued by that day and collected after it (``later_cash``, the walk's
    `later_cash_out`). The closing balance alone counts a final bill the direct debit collects a
    few days after the refund as paid, so the set-off missed it: 23 refunds, GBP 483.51, on
    run_output_8a300fa561.
    """
    legs: dict[str, list[str]] = {}
    for cid, owed in closing_balances.items():
        if owed > -0.005:
            legs.setdefault(billing_account_of(cid), []).append(cid)
    set_off_so_far: dict[str, float] = {}

    def _owed_on(leg: str, day: dt.date) -> float:
        later = sum(cash for issued, paid, cash in (later_cash or {}).get(leg, ())
                    if issued <= day < paid)
        return round(closing_balances[leg] + later - set_off_so_far.get(leg, 0.0), 2)
    last_bill: dict[str, dict] = {}
    for bill in bills:
        held = last_bill.get(bill["customer_id"])
        if held is None or bill["period_end"] > held["period_end"]:
            last_bill[bill["customer_id"]] = bill

    log: list[dict] = []
    for cid in sorted(closing_balances):
        balance = closing_balances[cid]
        if balance >= 0 or cid not in last_bill:
            continue
        if normalise_segment(customer_segments.get(cid, RESIDENTIAL)) != RESIDENTIAL:
            continue
        final = bill_issue_date(cid, last_bill[cid]["period_end"])
        later = [d for d in ((last_collection or {}).get(cid), (money_in or {}).get(cid)) if d]
        collected = max(later) if later else None
        issued = max(final, collected) if collected else final
        others: dict[str, float] = {}
        if any(leg != cid for leg in legs.get(billing_account_of(cid), ())):
            # The company pays on its own schedule, and the debt is the other leg's on that day,
            # so the day is asked first. The answer's date does not depend on the debt stated.
            refund_day = dt.date.fromisoformat(refund_on_account_closure(
                account_id=cid, final_bill_issued=issued,
                credit_amount_gbp=round(-balance, 2))["paid_date"])
            others = {leg: owed for leg in legs[billing_account_of(cid)] if leg != cid
                      and (owed := _owed_on(leg, refund_day)) > 0.005}
        against = max(others, key=lambda leg: (others[leg], leg)) if others else None
        event = {
            "customer_id": cid,
            **refund_on_account_closure(
                account_id=cid,
                final_bill_issued=issued,
                credit_amount_gbp=round(-balance, 2),
                other_fuel_closing_debt=round(others[against], 2) if against else 0.0,
            ),
        }
        # The run's logs label money in pounds; the seam names its currency once.
        event["set_off_gbp"] = event.pop("set_off")
        if event["set_off_gbp"] > 0:
            event["set_off_against"] = against
            set_off_so_far[against] = round(
                set_off_so_far.get(against, 0.0) + event["set_off_gbp"], 2)
        log.append(event)
    return log


def set_offs_from_refund_log(refund_log: list[dict]) -> dict[str, list[dict]]:
    """Each set-off the close refund made (home_moves.md s.8.8e), keyed by the leg it paid, in the
    shape `balance_settlement_from_outcomes(set_offs=)` nets against that leg's outstanding bills:
    ``{debt_leg: [{"date", "amount_gbp", "other_leg"}]}``, dated the refund's paid day.

    The run and the page both read the debt leg's write-off from that walk, so a set-off fed to it
    lowers the case, the page's write-off and the P&L together. Posted beside the case, as the first
    build did, the case still wrote off its whole amount and the page closed below zero."""
    out: dict[str, list[dict]] = {}
    for event in refund_log:
        amount, debt_leg = event.get("set_off_gbp") or 0.0, event.get("set_off_against")
        if amount > 0 and debt_leg:
            out.setdefault(debt_leg, []).append({
                "date": dt.date.fromisoformat(event["paid_date"]), "amount_gbp": round(amount, 2),
                "other_leg": event["customer_id"]})
    return out
