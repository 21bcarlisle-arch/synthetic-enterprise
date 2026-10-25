"""SLC 14 credit-balance refund activation (Phase 3 item 2, docs/design/
CORE_FIDELITY_PHASES.md: "wire credit_refund.py into the live run -- it
already has the SLA mechanic, this is activation, not a build").

company/billing/credit_refund.py has a real Ofgem SLC 14 mechanic
(CreditRefundBook, 10-working-day refund deadline) but grepping every file
in simulation/ for a caller returned nothing -- dead code (Phase 1 audit
finding #3). This module is the activation: it gives the mechanic something
real to fire on.

KNIFE pass 3 (B4, 2026-08-10) moved the mechanic itself back behind the wall.
This module no longer opens the company's compliance book: it reports the
closure, the credit left in the account and the date the money arrived to
``company/interfaces/credit_refund_requests.py``, and logs what comes back.
The SLC 14 deadline, the refund taxonomy and the breach verdict are the
supplier's, and are no longer readable from here.

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

Deterministic dispatch: `random.Random(f"creditrefund_{customer_id}_{period_end}")`,
matching simulation/feedback_survey.py's convention.
"""
from __future__ import annotations

import datetime as dt
import random

from company.interfaces.credit_refund_requests import refund_on_account_closure
from simulation.segment_vocabulary import RESIDENTIAL, normalise_segment

# Probability the refund is paid within the SLC 14 10-working-day deadline.
# A small tail breaches it -- the real pattern Ofgem issued multiple 2022
# enforcement notices for (suppliers holding credit balances during the
# crisis rather than refunding promptly).
ON_TIME_PROBABILITY = 0.90
ON_TIME_WORKING_DAYS = (2, 10)
LATE_WORKING_DAYS = (11, 25)


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
    closing_balances: dict[str, float],
) -> list[dict]:
    """One reg 6D refund event per closed domestic account the ledger closes in credit.

    ``closing_balances`` is the run's, account -> GBP owed (+) or held in credit (-) at the final
    bill, for leavers only. An account it does not hold is not evaluated: no balance is not a credit.
    The closure date is the account's last bill's period end. Returns plain JSON-serialisable dicts.
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
        closure_date = dt.date.fromisoformat(final["period_end"])

        # How long the money took to ARRIVE is what the household observes. The deadline it is
        # judged against, and the verdict, are the company's -- see the seam module's residual (1)
        # on why this draw is still world-side.
        rng = random.Random(f"creditrefund_{cid}_{final['period_end']}")
        on_time = rng.random() < ON_TIME_PROBABILITY
        lo, hi = ON_TIME_WORKING_DAYS if on_time else LATE_WORKING_DAYS
        working_days = rng.randint(lo, hi)
        paid_date = _add_working_days(closure_date, working_days)

        log.append({
            "customer_id": cid,
            **refund_on_account_closure(
                account_id=cid,
                closure_date=closure_date,
                credit_amount_gbp=round(-balance, 2),
                paid_date=paid_date,
            ),
        })
    return log
