"""Wires simulation/bacs_rails.py's timing physics into the live DD flow --
M2's next build step (director in-console approval, 2026-07-11): "wire rails
timing into the live DD flow."

Real finding before building (R4 diagnosis discipline): grepped the whole
codebase for company/billing/direct_debit.py's DirectDebitBook/
record_attempt/DDPaymentAttempt and found ZERO callers anywhere -- that
class was entirely unwired, the exact "paper compliance" class the M2
payments-maturity audit already named for 18 other billing/collections
modules. The genuinely LIVE DD-relevant flow is
simulation/arrears_engine.py::payment_outcome(), called from
compute_emergent_bad_debt()/compute_debt_recovery() -- but those functions
compute REAL ground-truth bad-debt/recovery figures that flow into every
downstream financial number (net_margin_gbp, treasury_cash_balance_gbp),
exactly the class of code M1's own precedent (docs/design/
M1_EVENT_DRAIN_MATERIALITY_FRAME.md) already established extreme caution
around -- a same-day change to arrears TIMING there would shift which
calendar year a write-off lands in, silently changing historical financial
figures. Deliberately NOT touched.

This module instead does the SAFE, additive thing: populates the
previously-unwired DirectDebitBook with REAL Bacs-timed collection records,
using the SAME unchanged payment_outcome() decision (identical RNG seed and
call sequence as compute_emergent_bad_debt(), so this book's success/failure
pattern matches what's already baked into the real ground truth -- never
contradicts it) layered with bacs_rails.py's realistic submission/collection/
notification timing and ARUDD reason codes. No existing number changes;
this is a new, real, company-observable artefact where none existed before.

Scope: only bills paid by `method == "direct_debit"` (the genuine consumer
DD case) -- payment_method()'s "bacs"/"chaps" branch is B2B/corporate
direct-transfer, a different real-world rails entirely, out of scope here.
"""
from __future__ import annotations

import random
from datetime import date, timedelta

from company.billing.direct_debit import DirectDebitBook, DDPaymentAttempt
from simulation.arrears_engine import (
    PAYMENT_TERMS_DAYS, payment_method, payment_outcome, stress_for_year,
    _fuel_poor_for_bill, _tone_for_bill,
)
from simulation.bacs_rails import (
    ARUDD_REASON_CODES, resolve_submission, submit_collection,
)


def build_dd_collection_book(
    bills: list[dict], behavioral: dict, monthly_amount_by_customer: dict[str, float] | None = None,
    seed: int = 42,
) -> DirectDebitBook:
    """Build a DirectDebitBook populated with real, Bacs-rails-timed
    collection attempts for every direct_debit-method bill. Same sorted
    order and RNG seed as compute_emergent_bad_debt() -- the resulting
    success/failure pattern matches the real ground truth exactly, this
    just adds the missing rails-timing/reason-code layer around it."""
    rng = random.Random(seed)
    # Separate, independently-seeded RNG for bacs_rails' own lag-day
    # randomization (resolve_submission()'s `rng` arg) -- deliberately NOT
    # the same `rng` instance payment_outcome() draws from. Sharing one
    # stream would advance `rng`'s state by extra draws compute_emergent_
    # bad_debt() never makes, desyncing every outcome AFTER the first
    # resolved DD bill from the real ground truth this function is
    # supposed to mirror exactly.
    rails_rng = random.Random(seed + 1)
    book = DirectDebitBook()
    monthly_amount_by_customer = monthly_amount_by_customer or {}

    for bill in sorted(bills, key=lambda b: (b["customer_id"], b["period_end"])):
        cid = bill["customer_id"]
        segment = bill.get("segment", "resi")
        amount = bill["total_amount_gbp"]
        period_end = bill["period_end"]
        year = int(period_end[:4])

        method = payment_method(segment, amount, cid, bill.get("commodity", "electricity"))
        # Advance the SAME rng the SAME number of times regardless of
        # method, so every later bill's payment_outcome() draw stays
        # identical to compute_emergent_bad_debt()'s own sequence -- only
        # direct_debit bills get a DD collection record, but every bill
        # must still consume the RNG in lockstep.
        stress = stress_for_year(behavioral.get(cid) or {}, year)
        outcome, _days_late = payment_outcome(
            method, stress, rng, segment, _fuel_poor_for_bill(method, cid),
            _tone_for_bill(method, cid, period_end), cid,
        )
        if method != "direct_debit":
            continue

        issue_date = date.fromisoformat(period_end)
        due_date = issue_date + timedelta(days=PAYMENT_TERMS_DAYS)

        mandate = book.get_mandate(cid)
        if mandate is None:
            monthly_amount = monthly_amount_by_customer.get(cid, amount)
            mandate = book.create_mandate(
                customer_id=cid,
                sort_code="00-00-**",  # masked, matches DirectDebitMandate's own convention -- no real bank data exists to carry
                account_last4="0000",
                monthly_amount_gbp=monthly_amount,
                setup_date=due_date.isoformat(),
            )

        reference = f"{mandate.mandate_reference}-{period_end}"
        submission = submit_collection(reference, cid, amount, due_date)
        decided = "success" if outcome == "success" else "failed"
        resolved = resolve_submission(submission, decided, rng=rails_rng)

        failure_reason = ""
        if resolved.status == "failed" and resolved.reason_code is not None:
            failure_reason = ARUDD_REASON_CODES.get(resolved.reason_code, "")

        attempt = DDPaymentAttempt(
            mandate_reference=mandate.mandate_reference,
            customer_id=cid,
            attempt_date=resolved.expected_outcome_date.isoformat(),
            amount_gbp=amount,
            outcome="collected" if resolved.status == "success" else "failed",
            failure_reason=failure_reason,
        )
        book.record_attempt(attempt)

    return book
