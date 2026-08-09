"""Undischarged credit-balance control (SLC 14 / Ofgem DD Market Compliance Review).

WHY THIS EXISTS. The existing money control on this path,
`domain_invariants.check_billed_clock_reconciles`, is a FOOTING check: it asserts that
recognised billed revenue equals the sum of `total_amount_gbp` over issued bills. Both
sides sum the SAME SIGNED totals, so a credit note reduces both by exactly the same
amount and the check passes with the credit invisible. It cannot distinguish "billed
£31,447 and credited £202" from "billed £31,245" -- and it was never meant to. Footing
is not lifecycle: a control that proves the books add up says nothing about whether
money the supplier owes a customer was ever GIVEN BACK.

That gap is not academic. Unreturned domestic credit balances were central to the 2021
GB supplier failures: balances built up on Direct Debit, were neither refunded nor
offset, and became unsecured customer losses at administration, which is why Ofgem's
Direct Debit Market Compliance Review and the SLC 14 refund obligations exist in the
form they do.

THE FOUR DISCHARGE PATHS a credit balance is supposed to have (any ONE of which
discharges it; this control fires only when NONE has occurred):
  1. refunded on customer request                      (SLC 14)
  2. offset against future bills                       (the ordinary path)
  3. cut/returned at the annual DD review              (SLC 22A / DD review)
  4. settled on account closure                        (SLC 21B final bill)
`company/billing/credit_refund.py` models path 4 and enumerates 1 and 3 as
`RefundTrigger` members -- but only `ACCOUNT_CLOSURE` is ever CONSTRUCTED anywhere in
non-test code, so 1, 2 and 3 are enumerated-but-dead. This control is what makes their
absence VISIBLE rather than merely true.

WHAT "UNDISCHARGED" MEANS, precisely. A live account's balance legitimately oscillates:
a bill is issued (balance rises, customer owes), then paid (balance falls). Testing
"is the balance negative right now" would therefore be both noisy and wrong. The signal
that actually means "the supplier is sitting on the customer's money" is the SETTLED
balance -- the balance immediately after each successful payment. On a healthy account
that returns to ~zero. On an account holding an undischarged credit it returns to the
same negative FLOOR every time, because each new bill is paid in full and the credit is
never applied to any of them. A floor that persists across a full annual review cycle
has, by construction, survived every one of the four discharge paths.

R15 -- THIS CONTROL CAN FAIL, and is built so its failure modes are the safe ones:
  * INDEPENDENCE (anti-TAUTOLOGY): the balance is rebuilt from the RAW signed invoice
    and payment streams. It deliberately does NOT read the ledger's own `balance_gbp`
    or `total_billed_gbp` -- those are the netted aggregates whose netting is the very
    blindness being fixed, so trusting them would reproduce it.
  * FAIL-CLOSED: missing, empty, malformed or non-numeric input FIRES rather than
    passes. An unavailable check is a FAILED check, never a silent green.
  * MATERIALITY: a sub-threshold credit (rounding dust -- e.g. the real -£0.22 credit
    note on C7 invoice 900) is not a compliance defect and must not fire, or the
    control becomes noise and gets muted, which is how controls die.
"""
from __future__ import annotations

from datetime import date, datetime

#: A credit below this is rounding dust, not a refundable balance. A real supplier does
#: not raise a refund for pennies, and a control that fires on them gets switched off.
CREDIT_MATERIALITY_GBP = 1.00

#: How long a material credit may sit before its persistence is itself the defect.
#: Anchored to the ANNUAL review cycle (SLC 22A / the DD review): a credit that has
#: survived a full year has necessarily survived the review that exists to catch it,
#: so this is the tightest defensible bound that cannot be argued away as "it was
#: about to be offset against the next bill".
MAX_UNDISCHARGED_DAYS = 365


def _as_date(value) -> date | None:
    """Parse an ISO date. Returns None on anything unparseable -- callers treat None as
    a FAIL-CLOSED signal, never as 'skip this row'."""
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        try:
            return date.fromisoformat(value[:10])
        except ValueError:
            return None
    return None


def settled_balance_series(invoices, payments) -> list[tuple[date, float]] | None:
    """Rebuild the account balance from RAW signed streams and return the balance as at
    each successful payment, chronologically: [(payment_date, balance_after), ...].

    Sign convention: positive = the customer owes the supplier; negative = the supplier
    holds the customer's money. A credit note is simply an invoice with a negative
    `total_amount_gbp`, which is exactly how the billing ledger already represents it.

    Returns None if the inputs are missing or malformed (FAIL-CLOSED -- the caller
    fires). Failed/pending payments are excluded: money that never moved cannot settle
    a balance.
    """
    if invoices is None or payments is None:
        return None
    events: list[tuple[date, int, float]] = []
    try:
        for inv in invoices:
            d = _as_date(inv.get("issue_date"))
            amt = inv.get("total_amount_gbp")
            if d is None or not isinstance(amt, (int, float)) or isinstance(amt, bool):
                return None
            events.append((d, 0, float(amt)))
        for pay in payments:
            if pay.get("outcome") != "success":
                continue
            d = _as_date(pay.get("payment_date"))
            amt = pay.get("amount_gbp")
            if d is None or not isinstance(amt, (int, float)) or isinstance(amt, bool):
                return None
            events.append((d, 1, -float(amt)))
    except (AttributeError, TypeError):
        return None
    if not events:
        return None

    # Order by date, and within a date settle bills before payments so a same-day
    # bill-and-pay lands on the post-payment balance rather than straddling it.
    events.sort(key=lambda e: (e[0], e[1]))
    balance = 0.0
    series: list[tuple[date, float]] = []
    for d, kind, amt in events:
        balance = round(balance + amt, 2)
        if kind == 1:
            series.append((d, balance))
    return series or None


def longest_undischarged_credit(invoices, payments,
                                materiality_gbp: float = CREDIT_MATERIALITY_GBP):
    """The longest continuous run during which the SETTLED balance never returned to
    within `materiality_gbp` of zero (i.e. the supplier held the customer's money
    across every payment in the run).

    Returns {"days", "floor_gbp", "start", "end"} for the worst such run, or None if
    there is no material undischarged credit. Returns the sentinel {"days": -1} when
    the balance series cannot be built at all -- FAIL-CLOSED, distinguishable by the
    caller from a genuine clean result.
    """
    series = settled_balance_series(invoices, payments)
    if series is None:
        return {"days": -1, "floor_gbp": None, "start": None, "end": None}

    worst = None
    run_start: date | None = None
    run_floor = 0.0
    for d, bal in series:
        if bal <= -materiality_gbp:
            if run_start is None:
                run_start, run_floor = d, bal
            else:
                run_floor = min(run_floor, bal)
            span = (d - run_start).days
            if worst is None or span > worst["days"]:
                worst = {"days": span, "floor_gbp": round(run_floor, 2),
                         "start": run_start.isoformat(), "end": d.isoformat()}
        else:
            # The settled balance came back to ~zero: the credit was discharged
            # (offset or refunded). Reset -- a later credit is a separate episode.
            run_start = None
    return worst


def check_credit_balance_discharged(invoices, payments, discharge_events=None,
                                    max_days: int = MAX_UNDISCHARGED_DAYS,
                                    materiality_gbp: float = CREDIT_MATERIALITY_GBP) -> bool:
    """Tier-1 control. Returns False (FIRES) when a material credit balance was held
    for longer than `max_days` with no discharge event recorded against it.

    `discharge_events` is any iterable of recorded refunds/offsets for this account
    (e.g. `CreditRefundBook` records). An explicit discharge inside the window clears
    the finding -- the credit was returned, which is the whole point. Passing None
    means "no refund data available", which FAILS CLOSED: a control that cannot see
    the refund book must not report the account as compliant.
    """
    worst = longest_undischarged_credit(invoices, payments, materiality_gbp)
    if worst is None:
        return True                      # no material credit ever held -- nothing to discharge
    if worst["days"] == -1:
        return False                     # unreadable input -- FAIL CLOSED
    if worst["days"] <= max_days:
        return True                      # held, but within the annual review cycle
    return bool(discharge_events)        # held too long: only a real discharge saves it
