"""The supplier's own accounting close — issue, post, derive, reconcile.

WHY THIS LIVES COMPANY-SIDE (KNIFE pass 3, `A_composition_lift`, step 14,
2026-08-11). Five steps sat inlined in `simulation/run_phase4c_on_phase2b.py`'s
`main()`, and not one of them is world physics:

  1. `pre_bill_validation.validate_bills` — the supplier's Tier-1 issuance gate.
     A HELD bill has not been issued to the customer.
  2. `saas.ledger.make_cost_to_serve_event` over the cost-to-serve schedule, and
     the merge of that with the acquisition-spend and fixed-cost events — the
     supplier deciding what else posts to its own chart of accounts this run.
  3. `saas.ledger.build_ledger` — double-entry posting.
  4. `saas.ledger.derive_pnl` / `ledger_summary` — the supplier's own P&L.
  5. `company.compliance.domain_invariants.check_billed_clock_reconciles` — the
     supplier's own reconciliation of its recognised revenue against the bills
     it actually issued (BILL_TO_LEDGER_LINKAGE.md's Tier-1 invariant).

A real supplier is free to change every one of those — its issuance gate, its
chart of accounts, its revenue-recognition policy, its month-end reconciliation
— without telling the world anything. The world's only contribution is the
SETTLED RECORDS: what physically flowed, half-hour by half-hour. That, and the
bills the company itself already assembled, is what crosses.

POINT-IN-TIME NOTE, because this module takes a whole run's `all_records` and
that is the exact shape of the 2026-07-10 hedge-volatility foresight bug. There
is deliberately NO `as_of` bound here and its absence is not an oversight: a
month-end close is an after-the-fact aggregation of records that have ALREADY
SETTLED, not a decision taken at a point in time. Nothing computed below feeds a
forward-looking choice — no price, no hedge, no forecast — so there is no future
for the company to see. The blindfold binds decisions; posting the books is the
one place a supplier is supposed to look at the whole period at once, and it is
the same argument under which `saas.ledger.build_ledger` has always taken the
full record set. If a future caller ever routes a DECISION through this output,
that caller needs the bound — this module does not.

WHAT THE WORLD KEEPS, AND WHY THAT IS THE TEST OF THE CUT. The world still owns
the settled records and still owns the *inputs* to the extra events —
acquisition spend and fixed cost are emitted by `run_phase2b` as records of what
the company spent, and the cost-to-serve schedule is computed by the
customer-value layer. Those arrive as DATA. What moved is the DECISION about
what to do with them: how they are shaped into ledger events, in what order they
merge, and whether the resulting revenue figure is allowed to stand. The world
hands over records and takes back a closed set of books.

BEHAVIOUR IS UNCHANGED BY CONSTRUCTION, which is the stronger claim §3f made for
bill assembly and is available here for the same reason: nothing is
reimplemented. The same five functions are called with the same arguments in the
same order, including the `extra_events or None` collapse (an empty list and
`None` are the same input to `build_ledger`, but preserving the exact call
argument means there is no behaviour question to argue about at all). The
`payment_model` seam below is injection, not reimplementation — its default IS
the module the inlined code passed.

WHY `payment_model` IS A PARAMETER. `saas.payment_behaviour` is the supplier's
own credit-risk and bad-debt-provision model, so the close imports it directly
rather than being handed it by the world — the world has no business supplying a
supplier's provisioning policy. It stays injectable because `build_ledger`
writes a `CREDIT_COLLECTIONS_POLICY` decision-log entry per provisioned bill,
and a test that could not substitute the model would either write to the real
decision log or be unable to exercise the provisioning path at all.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import saas.payment_behaviour as _default_payment_model
from company.billing.pre_bill_validation import validate_bills
from company.compliance.domain_invariants import check_billed_clock_reconciles
from saas.ledger import (
    build_ledger,
    derive_pnl,
    ledger_summary,
    make_broker_commission_event,
    make_cost_to_serve_event,
)

__all__ = ["AccountingClose", "close_the_books"]


@dataclass(frozen=True)
class AccountingClose:
    """One run's closed books.

    `issued_bills` / `held_bills` are `validate_bills`'s two halves, returned
    rather than discarded: the caller needs to know that a bill was withheld,
    and the held half is the exception queue a real billing operation works.

    `meta` carries `billed_clock_reconciles_with_issued_bills` — the invariant's
    verdict travels WITH the books it is about, so a consumer cannot render the
    P&L without the flag that says whether it reconciles.
    """

    issued_bills: list[dict[str, Any]]
    held_bills: list[Any]
    events: list[dict[str, Any]]
    pnl: dict[str, float]
    meta: dict[str, Any]


def close_the_books(
    settled_records: list[dict[str, Any]],
    bills: list[dict[str, Any]],
    *,
    acquisition_spend_events: list[dict[str, Any]] | None = None,
    fixed_cost_events: list[dict[str, Any]] | None = None,
    cost_to_serve_ledger_events: list[dict[str, Any]] | None = None,
    broker_commission_events: list[dict[str, Any]] | None = None,
    payment_model: Any = None,
) -> AccountingClose:
    """Close this run's books over the settled records and assembled bills.

    `settled_records` — the world's settled half-hourly records (what flowed).
        The whole run's worth, deliberately; see the point-in-time note above.
    `bills` — the FULL, unfiltered bill list from the company's own assembly.
        Filtering to the issued half happens here, deliberately: revenue
        recognition against an un-issued bill is a real accounting error, and
        the gate that prevents it belongs next to the posting it guards.
    `acquisition_spend_events` / `fixed_cost_events` — pre-built events the run
        emitted (Phase 8a growth mandate).
    `cost_to_serve_ledger_events` — the customer-value layer's monthly
        per-account cost-to-serve schedule (`{month, amount_gbp}`), shaped into
        account-6100 events here so account 6100 stops netting to zero.
    `broker_commission_events` — the ONGOING half of business acquisition cost, a monthly
        `{month, amount_gbp}` schedule of broker trail commission accrued on billed volume
        (`saas.opex_ledger.build_broker_commission_ledger_events`). Shaped into account-6300
        events here, the same account the one-off acquisition spend it replaced booked to.
    `payment_model` — the supplier's credit-risk/bad-debt model; defaults to
        `saas.payment_behaviour`.
    """
    model = _default_payment_model if payment_model is None else payment_model

    issued_bills, held_bills = validate_bills(bills)

    extra_events = (
        list(acquisition_spend_events or [])
        + list(fixed_cost_events or [])
        + [
            make_cost_to_serve_event(event["month"], event["amount_gbp"])
            for event in (cost_to_serve_ledger_events or [])
        ]
        + [
            make_broker_commission_event(event["month"], event["amount_gbp"])
            for event in (broker_commission_events or [])
        ]
    )

    events = build_ledger(
        settled_records,
        issued_bills,
        model,
        extra_events=extra_events or None,
    )
    pnl = derive_pnl(events)
    meta = ledger_summary(events)

    reconciles = check_billed_clock_reconciles(
        pnl.get("total_billed_gbp", 0.0), issued_bills
    )
    if not reconciles:
        # Logged loudly rather than raised: a full pipeline run takes ~100
        # minutes, and a divergence here is a real defect worth a visible flag,
        # not a reason to discard a completed run. It is also surfaced on the
        # report itself via `meta`, so it lands on a business surface and not
        # only in a log line.
        print(
            "WARNING: billed-clock invariant VIOLATED -- ledger_pnl.total_billed_gbp "
            "does not reconcile with the sum of issued bills. See "
            "BILLED_CLOCK_RECONCILES_WITH_ISSUED_BILLS "
            "(company/compliance/domain_invariants.py)."
        )
    meta["billed_clock_reconciles_with_issued_bills"] = reconciles

    return AccountingClose(
        issued_bills=issued_bills,
        held_bills=held_bills,
        events=events,
        pnl=pnl,
        meta=meta,
    )
