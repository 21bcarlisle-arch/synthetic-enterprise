"""The company's CREDIT-REFUND surface — the one place the world may report a closing
credit balance and learn what happened to the refund.

WHY THIS MODULE EXISTS (KNIFE pass 3, design B4_billing_mechanics_reached_directly)
-----------------------------------------------------------------------------------
`simulation/credit_refund_events.py` used to import `CreditRefundBook`,
`CreditRefundRecord` and `RefundTrigger` and RUN the company's SLC 14 compliance
process from inside the simulated world: it opened the company's book, classified the
trigger, raised the record, paid it, and then read the company's own breach verdict
back out. The world was operating the supplier's regulatory process and grading it.

WHAT THE WORLD LEGITIMATELY KNOWS, AND WHAT IT DOES NOT
--------------------------------------------------------
  * Known — **what happened to the household.** An account closed on a date carrying
    a credit balance of £X, and the money landed in the bank on a later date. Every
    one of those is something the customer experiences directly, so the world holds
    them and hands them over.
  * Not known — **the compliance apparatus.** The SLC 14 ten-working-day deadline,
    the working-day arithmetic, the refund taxonomy (`RefundTrigger` has four members
    and choosing between them is a supplier classification), the record's status
    lifecycle, the book that aggregates breaches for the regulator. A real customer
    knows their money was late; they do not hold their supplier's compliance register
    or its definition of late.

Importing the book handed the world all of it. This module takes the four facts and
returns the record the company made of them.

WHAT CROSSES, PRECISELY
-----------------------
In: account id, closure date, credit amount, and the date the money arrived.

Out: a plain JSON-serialisable dict — no `CreditRefundBook`, no `CreditRefundRecord`,
no `RefundTrigger`, no status enum, and deliberately no re-export of any of them.
`tests/company/interfaces/test_credit_refund_requests_seam.py` exists to keep that
true and is mutation-proven: a widened `__all__`, or handing back the record object
"for convenience", would restore the removed dependency WITHOUT creating a single wall
edge, because the import would still terminate on the exempt seam package and the
ratchet is blind to that by construction.

The trigger is CLASSIFIED here rather than passed in, which is the substance of the
cut rather than a detail of it: the world says "this account closed with money in
it", and it is the company that decides that means `ACCOUNT_CLOSURE` under SLC 14
rather than one of the other three triggers. Accepting a trigger argument would have
left the taxonomy in the world's hands and made this module a spelling change.

**This is a cut, not laundering.** `company/interfaces/` and `company/billing/` are
both WALKED by `tools/epistemic_wall.py` byte for byte. Nothing moved out of the
instrument's reach; the edge is exempt because it terminates on the sanctioned
crossing surface — the ratchet's own published `SEAM_PACKAGE` remedy — and not
because the measurement stopped looking.

TWO RESIDUALS, NAMED RATHER THAN IMPLIED
-----------------------------------------
1. **The refund LATENCY is still drawn world-side.** `credit_refund_events.py` keeps
   `ON_TIME_PROBABILITY` and the two working-day ranges, so how long the supplier
   takes to pay is currently modelled as a property of the world rather than of the
   company's operations. That is arguably backwards — a real supplier's payment speed
   is its own operational performance, and the 2022 enforcement notices this mechanic
   models were issued precisely because suppliers CHOSE to sit on credit balances.
   It is preserved rather than repaired here because moving an RNG draw across the
   wall in the same commit that moves an import would move published SLC 14 breach
   figures and make neither change reviewable. Owed to a later pass.
2. **This is a PULL, not the push B4 asks for.** Same structural blocker B5 measured:
   the bills are assembled by `simulation/run_phase4c_on_phase2b.py`, a SIM
   composition root, so there is no company-side emitter to carry a refund
   instruction. Owed to `A_composition_lift`.

What the pull buys now: the compliance book, the deadline, the record type and the
trigger taxonomy are unreachable from the SIM, and what comes back across the wall is
a dict of finished facts.
"""
from __future__ import annotations

import datetime as dt

__all__ = ["refund_on_account_closure"]


def refund_on_account_closure(
    account_id: str,
    closure_date: dt.date,
    credit_amount_gbp: float,
    paid_date: dt.date,
) -> dict:
    """Record, and answer for, one credit refund owed because an account closed in
    credit.

    The caller states what the household experienced — the account closed on
    ``closure_date`` holding ``credit_amount_gbp``, and the money arrived on
    ``paid_date``. The company classifies the trigger, runs it through its own SLC 14
    book and returns the resulting facts:

        trigger, request_date, credit_amount_gbp, paid_date,
        working_days_to_pay, breached_slc14_deadline

    all as plain JSON-serialisable values. The book itself does not leave this module.
    """
    # Imported INSIDE the function, for the reason the sibling DD-review door records:
    # at module level these names land in THIS module's namespace, so
    # `from company.interfaces.credit_refund_requests import RefundTrigger` would hand
    # the world the compliance taxonomy straight back — with the epistemic ratchet
    # still green, because that import terminates on the exempt seam package. The
    # walker descends into function bodies (`ast.walk`), so the measurement is
    # unchanged; only the door's namespace narrows to what it exports.
    from company.billing.credit_refund import (
        CreditRefundBook,
        CreditRefundRecord,
        RefundTrigger,
    )

    book = CreditRefundBook()
    book.raise_refund(CreditRefundRecord(
        account_id=account_id,
        request_date=closure_date,
        # The company's own reading of SLC 14: a balance left over at closure is the
        # account-closure trigger, not a customer request or an annual review.
        trigger=RefundTrigger.ACCOUNT_CLOSURE,
        credit_amount_gbp=credit_amount_gbp,
    ))
    record = book.pay(account_id, paid_date)
    return {
        "trigger": record.trigger.value,
        "request_date": record.request_date.isoformat(),
        "credit_amount_gbp": record.credit_amount_gbp,
        "paid_date": record.paid_date.isoformat(),
        "working_days_to_pay": record.working_days_to_pay(),
        "breached_slc14_deadline": record.breached_deadline(),
    }
