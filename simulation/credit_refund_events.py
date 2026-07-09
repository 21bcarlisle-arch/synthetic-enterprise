"""SLC 14 credit-balance refund activation (Phase 3 item 2, docs/design/
CORE_FIDELITY_PHASES.md: "wire credit_refund.py into the live run -- it
already has the SLA mechanic, this is activation, not a build").

company/billing/credit_refund.py has a real Ofgem SLC 14 mechanic
(CreditRefundBook, 10-working-day refund deadline) but grepping every file
in simulation/ for a caller returned nothing -- dead code (Phase 1 audit
finding #3). This module is the activation: it gives the mechanic something
real to fire on.

Real DD billing pays a flat monthly amount, reconciled periodically -- not
the exact bill each month. `saas/bill_generator.py` bills exact consumption
with no DD smoothing anywhere in the codebase before this. DD smoothing is
added here, scoped tightly to this module: a DD customer's flat monthly
amount at any point is the trailing mean of their own bills TO DATE (no
lookahead -- what a real supplier would already know when it set the DD
amount). A customer who churns mid-cycle carrying a positive smoothing
balance (paid more via flat DD than they were actually billed) is the most
common real-world SLC 14 trigger.

This is a narrow, closure-only mechanic -- NOT the full billed-vs-collected
customer statement docs/staging/done/BILLING_AND_PAYMENTS_LEDGER.md's item 3
still owns (that is a customer-facing reconciliation surface; this is an
internal SIM trigger for one company compliance process).

Deterministic dispatch: `random.Random(f"creditrefund_{customer_id}_{period_end}")`,
matching simulation/feedback_survey.py's convention.
"""
from __future__ import annotations

import datetime as dt
import random
import statistics

from company.billing.credit_refund import (
    CreditRefundBook,
    CreditRefundRecord,
    RefundTrigger,
)
from simulation.arrears_engine import payment_method

# Probability the refund is paid within the SLC 14 10-working-day deadline.
# A small tail breaches it -- the real pattern Ofgem issued multiple 2022
# enforcement notices for (suppliers holding credit balances during the
# crisis rather than refunding promptly).
ON_TIME_PROBABILITY = 0.90
ON_TIME_WORKING_DAYS = (2, 10)
LATE_WORKING_DAYS = (11, 25)


def dd_smoothing_balance_at_closure(bills_for_customer: list[dict]) -> float:
    """Cumulative (flat DD amount - actual bill) across a DD customer's full
    bill history, chronological. The flat DD amount charged in any given
    month is that customer's own trailing mean of prior bills (no
    lookahead) -- the first bill has no history yet, so DD == actual for it.
    """
    if not bills_for_customer:
        return 0.0
    seen_totals: list[float] = []
    balance = 0.0
    for bill in bills_for_customer:
        actual = bill["total_amount_gbp"]
        dd_amount = statistics.mean(seen_totals) if seen_totals else actual
        balance += dd_amount - actual
        seen_totals.append(actual)
    return balance


def _add_working_days(start: dt.date, n: int) -> dt.date:
    current = start
    added = 0
    while added < n:
        current += dt.timedelta(days=1)
        if current.weekday() < 5:
            added += 1
    return current


def generate_credit_refund_log(
    bills: list[dict],
    customer_segments: dict[str, str],
    churned_ids: set[str],
) -> list[dict]:
    """One SLC 14 refund event per churned DD customer closing with a
    positive DD-smoothing credit balance. Returns plain JSON-serialisable
    dicts. Non-DD customers (I&C/SME on bacs/chaps) and customers who never
    churn are not evaluated -- SLC 14's account-closure trigger only applies
    at closure.
    """
    by_customer: dict[str, list[dict]] = {}
    for bill in sorted(bills, key=lambda b: (b["customer_id"], b["period_end"])):
        by_customer.setdefault(bill["customer_id"], []).append(bill)

    book = CreditRefundBook()
    log: list[dict] = []
    for cid, customer_bills in by_customer.items():
        if cid not in churned_ids or not customer_bills:
            continue
        segment = customer_segments.get(cid, "resi")
        last_bill = customer_bills[-1]
        method = payment_method(segment, last_bill["total_amount_gbp"], cid,
                                 last_bill.get("commodity", "electricity"))
        if method != "direct_debit":
            continue
        balance = dd_smoothing_balance_at_closure(customer_bills)
        if balance <= 0:
            continue

        request_date = dt.date.fromisoformat(last_bill["period_end"])
        book.raise_refund(CreditRefundRecord(
            account_id=cid,
            request_date=request_date,
            trigger=RefundTrigger.ACCOUNT_CLOSURE,
            credit_amount_gbp=round(balance, 2),
        ))

        rng = random.Random(f"creditrefund_{cid}_{last_bill['period_end']}")
        on_time = rng.random() < ON_TIME_PROBABILITY
        lo, hi = ON_TIME_WORKING_DAYS if on_time else LATE_WORKING_DAYS
        working_days = rng.randint(lo, hi)
        paid_date = _add_working_days(request_date, working_days)

        record = book.pay(cid, paid_date)
        log.append({
            "customer_id": cid,
            "trigger": record.trigger.value,
            "request_date": record.request_date.isoformat(),
            "credit_amount_gbp": record.credit_amount_gbp,
            "paid_date": record.paid_date.isoformat(),
            "working_days_to_pay": record.working_days_to_pay(),
            "breached_slc14_deadline": record.breached_deadline(),
        })
    return log
