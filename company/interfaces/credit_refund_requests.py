"""The company's CREDIT-REFUND surface — the one place the world may report a closing
credit balance and learn what happened to the refund.

WHY THIS MODULE EXISTS (KNIFE pass 3, design B4_billing_mechanics_reached_directly)
-----------------------------------------------------------------------------------
`simulation/credit_refund_events.py` used to import `CreditRefundBook`,
`CreditRefundRecord` and `RefundTrigger` and RUN the company's reg 6D compliance
process from inside the simulated world: it opened the company's book, classified the
trigger, raised the record, paid it, and then read the company's own breach verdict
back out. The world was operating the supplier's regulatory process and grading it.

WHAT THE WORLD LEGITIMATELY KNOWS, AND WHAT IT DOES NOT
--------------------------------------------------------
  * Known — **what happened to the household.** An account's final bill was issued on
    a date closing in a credit of £X. Both are on the bill the customer holds, so the
    world hands them over. When the money lands is the supplier's doing, and comes back.
  * Not known — **the compliance apparatus.** The reg 6D ten-working-day deadline,
    the working-day arithmetic, the refund taxonomy (`RefundTrigger` has four members
    and choosing between them is a supplier classification), the record's status
    lifecycle, the book that aggregates breaches for the regulator. A real customer
    knows their money was late; they do not hold their supplier's compliance register
    or its definition of late.

Importing the book handed the world all of it. This module takes the four facts and
returns the record the company made of them.

WHAT CROSSES, PRECISELY
-----------------------
In: account id, the final bill's issue date, and the credit amount. Out: the date the company
pays, and its reg 6D verdict and any guaranteed-standard payment owed on it.

Out: a plain JSON-serialisable dict — no `CreditRefundBook`, no `CreditRefundRecord`,
no `RefundTrigger`, no status enum, and deliberately no re-export of any of them.
`tests/company/interfaces/test_credit_refund_requests_seam.py` exists to keep that
true and is mutation-proven: a widened `__all__`, or handing back the record object
"for convenience", would restore the removed dependency WITHOUT creating a single wall
edge, because the import would still terminate on the exempt seam package and the
ratchet is blind to that by construction.

The trigger is CLASSIFIED here rather than passed in, which is the substance of the
cut rather than a detail of it: the world says "this account closed with money in
it", and it is the company that decides that means `ACCOUNT_CLOSURE` under reg 6D
rather than one of the other three triggers. Accepting a trigger argument would have
left the taxonomy in the world's hands and made this module a spelling change.

**This is a cut, not laundering.** `company/interfaces/` and `company/billing/` are
both WALKED by `tools/epistemic_wall.py` byte for byte. Nothing moved out of the
instrument's reach; the edge is exempt because it terminates on the sanctioned
crossing surface — the ratchet's own published `SEAM_PACKAGE` remedy — and not
because the measurement stopped looking.

TWO RESIDUALS, NAMED RATHER THAN IMPLIED
-----------------------------------------
1. **The refund LATENCY was drawn world-side until 2026-10-25.** `credit_refund_events.py`
   kept a 90% on-time draw and two working-day ranges, so how long the supplier took to pay
   was a property of the world. The run at b2bc3d8da5 paid 10 of 100 closure refunds 13 to
   24 working days after the final bill, every one of them that draw's late arm. The day
   is now the company's (`credit_refund.scheduled_refund_date`) and `paid_date` no longer
   crosses in.
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
    final_bill_issued: dt.date,
    credit_amount_gbp: float,
) -> dict:
    """Record, and answer for, one credit refund owed because an account closed in
    credit.

    The caller states what the household experienced — its final bill was issued on
    ``final_bill_issued`` closing ``credit_amount_gbp`` in credit. The company classifies
    the trigger, pays on its own schedule, grades it against GSoP reg 6D and returns:

        trigger, request_date, credit_amount_gbp, paid_date,
        working_days_to_pay, breached_reg_6d_deadline, reg_6d_payment_owed (in £)

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
        scheduled_refund_date,
    )

    book = CreditRefundBook()
    book.raise_refund(CreditRefundRecord(
        account_id=account_id,
        request_date=final_bill_issued,
        # The company's own reading of reg 6D: a balance left over at closure is the
        # account-closure trigger, not a customer request or an annual review.
        trigger=RefundTrigger.ACCOUNT_CLOSURE,
        credit_amount_gbp=credit_amount_gbp,
    ))
    record = book.pay(account_id, scheduled_refund_date(final_bill_issued))
    return {
        "trigger": record.trigger.value,
        "request_date": record.request_date.isoformat(),
        "credit_amount_gbp": record.credit_amount_gbp,
        "paid_date": record.paid_date.isoformat(),
        "working_days_to_pay": record.working_days_to_pay(),
        "breached_reg_6d_deadline": record.breached_deadline(),
        "reg_6d_payment_owed": record.reg_6d_payment(),
    }
