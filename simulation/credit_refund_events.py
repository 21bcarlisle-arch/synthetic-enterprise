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
from simulation.segment_vocabulary import RESIDENTIAL, normalise_segment


def generate_credit_refund_log(
    bills: list[dict],
    customer_segments: dict[str, str],
    closing_balances: dict[str, float],
) -> list[dict]:
    """One reg 6D refund event per closed domestic account the ledger closes in credit.

    ``closing_balances`` is the run's, account -> GBP owed (+) or held in credit (-) at the final
    bill, for leavers only. An account it does not hold is not evaluated: no balance is not a credit.
    The final bill is the account's last bill, issued at its period end. Returns plain
    JSON-serialisable dicts.
    """
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
        final = last_bill[cid]
        log.append({
            "customer_id": cid,
            **refund_on_account_closure(
                account_id=cid,
                final_bill_issued=dt.date.fromisoformat(final["period_end"]),
                credit_amount_gbp=round(-balance, 2),
            ),
        })
    return log
