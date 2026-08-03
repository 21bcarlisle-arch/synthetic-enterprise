"""DD2 (atom ``DD_seasonal_cashflow_physics``) -- the per-customer rolling
credit/debit balance carried tick-by-tick under a LEVEL (fixed) direct debit.

The physics this instruments, which nothing in the codebase did before: under a
level DD a household pays the SAME fixed amount every month while consuming
seasonally (little in summer, a lot in winter). So a credit BUILDS through the
warm months and DRAWS DOWN through the cold ones. The positive balance the
supplier is holding at any moment is money it owes back -- a LIABILITY, not
profit -- and its seasonal PEAK (autumn, after the summer build) is exactly the
"cash-rich but balance-sheet-insolvent" tell the atom exists to make visible: a
supplier can sit on a pile of cash that is entirely other people's overpayments.

Until now the only instrumented "held credit" was the DD5 SITE *floor* in
``tools/generate_shadow_html.py::_held_credit_floor`` -- the sum of today's
Variable-DD overpayment balances in a drawn sample, whose own docstring says it
is "NOT the full level-DD seasonal cycle (DD1-DD4, designed not instrumented)".
This module is that missing instrumentation: the actual level-DD seasonal
balance trajectory across the whole portfolio and over time.

Safe-by-construction, mirroring ``simulation/dd_collection_book.py`` and
``company/billing/dd_review_runner.py`` EXACTLY -- a new company-observable
artefact where none existed before, with NO existing number changed:

* It reads ONLY company-observable bill fields (``customer_id``, ``segment``,
  ``commodity``, ``total_amount_gbp``, ``period_end`` -- all things a real
  supplier issued itself and can see) and produces a balance book. It mutates
  nothing, touches no ledger / treasury / cash-timing figure, and changes no
  published number.
* It draws NO RNG and is a pure, deterministic, idempotent function of the bill
  list (C-S2: replaying the same bills reproduces an identical book). It is
  time-scale invariant (C-S5): it operates on bill *periods* in issue order,
  not on any wall clock or fixed cadence -- monthly, quarterly, or accelerated
  billing all carry the same way.
* The DD-customer population and the standing level-DD chain are IDENTICAL to
  the two sibling artefacts so the three stay mutually consistent: the DD
  population is ``payment_method(...) == "direct_debit"`` (same gate as
  ``dd_collection_book``); the standing monthly DD is the first issued bill's
  amount in the first year, then each subsequent year is the prior year's
  ``dd_review._recommended_monthly(actual)`` -- the very same year-on-year
  re-estimation chain ``dd_review_runner`` walks.

Deferred / NOT built here (registered, not silently dropped):

* DD3 -- booking this held-credit balance as a LIABILITY in the double-entry
  chart of accounts -- is the registered next step. This module EMITS the
  liability figure DD3 will book (``portfolio_final_held_credit_gbp``); it does
  not itself post to any ledger.
* DD-H -- the belief-vs-truth solvency gap organ -- consumes this module's
  held-credit series (the TRUTH of what is owed back) against the company's
  believed cash-on-hand. Not built here; this is its input.
* The non-zero OPENING balance a customer inherits from a prior tenancy's debt
  belongs to ``W2_12_change_of_tenancy_debt_physics``. This module opens every
  customer at ZERO and must NOT duplicate that physics. W2_12 has since BUILT
  its physics (``company/crm/change_of_tenancy_register.py::TenancyChangeCoupler``
  + ``simulation/final_bill_outcome.py``, commit f2fe0bde1) but has NO live
  pipeline caller yet -- grep-verified 2026-08-03: every reference outside its
  own module is a test -- so no run emits a tenancy-change stream this module
  could join to. Inventing an opening here would fabricate that physics, so the
  opening stays ZERO and the residual is honestly W2_12's live wiring, not DD2's.

2026-08-03 -- THE COLLECTION-OUTCOME OVERLAY (DD2 residual, this pass)
---------------------------------------------------------------------
The original build carried ``balance += standing_dd - bill`` for every billed
month, i.e. it assumed EVERY level DD was actually collected. On the real
2016-2025 run that is false in 26 of 751 cases: ``dd_collection_book`` resolves
each DD bill's collection through the real Bacs rails and 26 come back
``failed`` (ARUDD). Counting money that never left the customer's bank as held
credit OVERSTATES the liability and, worse, understates the arrears -- it is a
FAIL-OPEN in exactly this module's own named physics, and it made the
cash-rich-but-insolvent tell read from money the supplier never had.

So the balance now carries the money that was actually BANKED, while the
*instructed* standing amount (``collected_gbp``) is unchanged -- a real DD is
two separate events in time (C-S3): the supplier instructs a fixed amount, and
the bank either honours it or does not. DD1's level-fixed invariant reads the
INSTRUCTED amount and is therefore untouched by this change (a failed collection
does not make a level DD stop being level).

C-S1 (event-arrival tolerance) is explicit: outcomes are an OVERLAY keyed by
``(customer_id, 'YYYY-MM')``. A month with no outcome yet keeps the instructed
treatment and is labelled ``assumed`` -- an un-arrived outcome is not silently
recoded as a failure, and outcomes may arrive singly, late or out of order
without changing the result (C-S2: rebuilding from the same inputs reproduces
the book exactly).
"""
from __future__ import annotations

import dataclasses
import math
from dataclasses import dataclass, field
from datetime import date
from typing import Mapping, Optional

from company.billing.dd_review import _recommended_monthly
from simulation.arrears_engine import payment_method

# How many per-customer trajectories to carry on the serialised surface so a
# business page can render a REAL customer's seasonal saw-tooth (not a synthetic
# illustration). Deterministic pick: the first N direct-debit customers by id.
_SAMPLE_TRAJECTORY_CUSTOMERS = 6

# Collection-outcome vocabulary. Mirrors dd_collection_book's own attempt
# outcomes by VALUE (typed message, not a shared object) plus the C-S1 state
# that book has no word for: "we have not been told yet".
OUTCOME_COLLECTED = "collected"
OUTCOME_FAILED = "failed"
OUTCOME_ASSUMED = "assumed"     # no outcome has arrived; instructed amount stands


def _months_between(anchor: date, d: date) -> int:
    """Whole calendar months from ``anchor`` to ``d`` (>=0 for d>=anchor)."""
    return (d.year - anchor.year) * 12 + (d.month - anchor.month)


def _finite(x, name: str) -> float:
    """Reject non-finite money, FAIL-CLOSED (R15).

    A NaN bill amount propagates silently through ``balance += ...`` and then
    disappears from the held-credit aggregate, because ``nan > 0`` is False --
    the liability would read plausible and be wrong. Comparison guards are
    NaN-blind, so finiteness is checked FIRST and never coerced to zero.
    """
    try:
        v = float(x)
    except (TypeError, ValueError):
        raise ValueError(f"{name} is not a number: {x!r}")
    if not math.isfinite(v):
        raise ValueError(f"{name} must be finite, got {v!r}")
    return v


@dataclass(frozen=True)
class BalancePoint:
    """One customer's level-DD position after a single billed period."""

    month: str            # 'YYYY-MM' of the bill's period_end
    collected_gbp: float  # the fixed level DD INSTRUCTED that month (DD1 reads this)
    consumed_gbp: float   # the actual cost of that month's energy (the bill)
    balance_gbp: float    # running (banked - consumed); +ve = held credit
    # 2026-08-03 collection-outcome overlay. No defaults ON PURPOSE: a default
    # would let a caller construct a point whose banked figure was never
    # decided, which is the fail-open this overlay exists to close.
    banked_gbp: float               # what actually reached the bank that month
    collection_outcome: str         # collected / failed / assumed


@dataclass
class DDBalanceBook:
    """Per-customer level-DD seasonal balance trajectories + the portfolio
    held-credit-liability time series they aggregate to."""

    # customer_id -> ordered list of BalancePoint
    trajectories: dict = field(default_factory=dict)
    # 'YYYY-MM' -> aggregate across all DD customers active that month
    monthly: dict = field(default_factory=dict)

    def _months_sorted(self) -> list:
        return sorted(self.monthly)

    def summary(self) -> dict:
        months = self._months_sorted()
        if not months:
            return {
                "n_customers": 0,
                "n_ever_in_credit": 0,
                "peak_held_credit_gbp": 0.0,
                "peak_month": None,
                "trough_held_credit_gbp": 0.0,
                "trough_month": None,
                "mean_held_credit_gbp": 0.0,
                "portfolio_final_balance_gbp": 0.0,
                "portfolio_final_held_credit_gbp": 0.0,
                "n_failed_collections": 0,
                "uncollected_level_dd_gbp": 0.0,
                "n_collections_with_known_outcome": 0,
            }
        held_series = [(m, self.monthly[m]["held_credit_gbp"]) for m in months]
        peak_month, peak = max(held_series, key=lambda t: t[1])
        trough_month, trough = min(held_series, key=lambda t: t[1])
        mean_held = sum(v for _, v in held_series) / len(held_series)
        last = self.monthly[months[-1]]
        n_ever = sum(
            1 for pts in self.trajectories.values()
            if any(p.balance_gbp > 0 for p in pts)
        )
        all_points = [p for pts in self.trajectories.values() for p in pts]
        failed = [p for p in all_points if p.collection_outcome == OUTCOME_FAILED]
        return {
            "n_customers": len(self.trajectories),
            "n_ever_in_credit": n_ever,
            "peak_held_credit_gbp": round(peak, 2),
            "peak_month": peak_month,
            "trough_held_credit_gbp": round(trough, 2),
            "trough_month": trough_month,
            "mean_held_credit_gbp": round(mean_held, 2),
            "portfolio_final_balance_gbp": round(last["portfolio_balance_gbp"], 2),
            "portfolio_final_held_credit_gbp": round(last["held_credit_gbp"], 2),
            # 2026-08-03 collection-outcome overlay: money INSTRUCTED but never
            # banked. It is not held credit, and the gap between the two is the
            # honest measure of how much of the "cash-rich" position is fiction.
            "n_failed_collections": len(failed),
            "uncollected_level_dd_gbp": round(sum(p.collected_gbp for p in failed), 2),
            "n_collections_with_known_outcome": sum(
                1 for p in all_points if p.collection_outcome != OUTCOME_ASSUMED
            ),
        }

    def basis(self) -> dict:
        """R14 -- every published financial figure carries its clock.

        Held customer credit is NOT a settled-clock figure and never was. Its
        consumption side is the company's own ISSUED BILLS (the billed clock);
        its collection side is the real DD collection outcome (the banked
        clock). Saying so is the point: a basis-less liability is a defect.
        """
        note = (
            "Held customer credit = level DD actually BANKED (failed collections "
            "excluded) less the customer's own ISSUED BILLS. Consumption side is "
            "the billed clock (issued bills, not settlement); collection side is "
            "the banked clock (real Bacs collection outcomes). Months whose "
            "collection outcome has not arrived are labelled 'assumed' and keep "
            "the instructed amount -- a pending outcome is not recoded as a "
            "failure. Not a settled-clock figure and not reconcilable to one."
        )
        entry = {"clock": "billed-and-banked", "provisional": True, "note": note}
        return {
            "peak_held_credit_gbp": entry,
            "portfolio_final_held_credit_gbp": entry,
            "held_credit_gbp": entry,
            "uncollected_level_dd_gbp": {
                "clock": "banked",
                "provisional": True,
                "note": (
                    "Level DD instructed but never banked (failed Bacs "
                    "collections). Banked clock by construction."
                ),
            },
        }

    def serialise(self) -> dict:
        """JSON-safe form for the run-output surface (mirrors
        ``dd_review_runner.DDReviewRunResult.serialise``): the summary, the
        portfolio monthly held-credit series, and a bounded set of real
        per-customer trajectories a business page can render directly."""
        months = self._months_sorted()
        sample_ids = sorted(self.trajectories)[:_SAMPLE_TRAJECTORY_CUSTOMERS]
        return {
            "summary": self.summary(),
            "basis": self.basis(),
            "monthly_held_credit_series": [
                {
                    "month": m,
                    "held_credit_gbp": round(self.monthly[m]["held_credit_gbp"], 2),
                    "portfolio_balance_gbp": round(self.monthly[m]["portfolio_balance_gbp"], 2),
                    "n_in_credit": self.monthly[m]["n_in_credit"],
                }
                for m in months
            ],
            "sample_trajectories": {
                cid: [dataclasses.asdict(p) for p in self.trajectories[cid]]
                for cid in sample_ids
            },
        }


def collection_outcomes_from_attempts(
    bills: list[dict], attempts: list[dict]
) -> dict[tuple[str, str], str]:
    """Join ``dd_collection_book``'s real Bacs collection attempts onto the
    billed months they answer, producing the overlay ``build_dd_balance_book``
    consumes.

    ``dd_collection_book`` emits exactly one attempt per direct-debit bill, in
    ``(customer_id, period_end)`` order, and each attempt carries the bill's own
    ``total_amount_gbp``. So the join is POSITIONAL per customer -- and the
    amount carried on both sides is an INDEPENDENT cross-check of that join
    (the bill list and the attempt list are separate structures; if the walk
    ever slipped, the amounts would stop agreeing). A disagreement raises rather
    than silently attributing one customer's failure to another's month: R15
    fail-closed, because a mis-joined outcome is worse than no outcome.

    C-S1: the attempt stream may be SHORT (outcomes still arriving). Trailing
    bills simply get no entry and stay ``assumed``. It may not be REORDERED --
    attempts are sorted here by ``attempt_date`` before the walk, so late
    arrival is fine and out-of-order arrival is normalised.
    """
    dd_bills: dict[str, list[tuple[str, str, float]]] = {}
    for b in bills:
        amount = _finite(b["total_amount_gbp"], "bill total_amount_gbp")
        method = payment_method(
            b.get("segment", "resi"), amount, b["customer_id"],
            b.get("commodity", "electricity"),
        )
        if method != "direct_debit":
            continue
        dd_bills.setdefault(b["customer_id"], []).append(
            (b["period_end"], b["period_end"][:7], amount)
        )

    by_cust_attempts: dict[str, list[dict]] = {}
    for a in attempts:
        by_cust_attempts.setdefault(a["customer_id"], []).append(a)

    overlay: dict[tuple[str, str], str] = {}
    for cid, rows in dd_bills.items():
        rows.sort(key=lambda t: t[0])
        cust_attempts = sorted(
            by_cust_attempts.get(cid, []), key=lambda a: a["attempt_date"]
        )
        for (_pe, month, amount), attempt in zip(rows, cust_attempts):
            attempt_amount = _finite(attempt["amount_gbp"], "attempt amount_gbp")
            if abs(attempt_amount - amount) > 0.01:
                raise ValueError(
                    "DD collection-outcome join is unsound for customer "
                    f"{cid} at {month}: bill £{amount:.2f} vs attempt "
                    f"£{attempt_amount:.2f}. Refusing to attribute an outcome "
                    "to a month it does not answer."
                )
            outcome = attempt.get("outcome")
            # Anything that is not an explicit success is treated as a failure
            # to bank the money -- fail-CLOSED. An unrecognised outcome string
            # must not read as "collected".
            overlay[(cid, month)] = (
                OUTCOME_COLLECTED if outcome == OUTCOME_COLLECTED else OUTCOME_FAILED
            )
    return overlay


def build_dd_balance_book(
    bills: list[dict],
    collection_outcomes: Optional[Mapping[tuple[str, str], str]] = None,
) -> DDBalanceBook:
    """Carry each direct-debit customer's level-DD credit/debit balance
    tick-by-tick and aggregate the portfolio held-credit liability over time.

    ``collection_outcomes`` is the optional ``(customer_id, 'YYYY-MM') ->
    'collected'|'failed'`` overlay produced by
    :func:`collection_outcomes_from_attempts`. A month absent from it keeps the
    instructed amount and is labelled ``assumed`` (C-S1: an outcome that has not
    arrived is not a failure).

    Pure, deterministic, idempotent (no RNG, no mutation of ``bills`` or any
    ground-truth structure). See the module docstring for the wall-clean basis
    and the exact consistency with ``dd_collection_book`` / ``dd_review_runner``.
    """
    outcomes: Mapping[tuple[str, str], str] = collection_outcomes or {}
    # Group the company's OWN issued bills by customer, direct-debit only --
    # the same population gate dd_collection_book applies (a customer with no DD
    # mandate holds no seasonal DD credit).
    by_cust: dict[str, list[tuple[date, float]]] = {}
    for b in bills:
        # R15 fail-CLOSED: a non-finite bill amount is rejected here, BEFORE any
        # comparison. `nan > 0` is False, so a NaN carried into the balance would
        # quietly drop that customer out of held credit and leave a plausible,
        # wrong liability on the balance sheet.
        amount = _finite(b["total_amount_gbp"], "bill total_amount_gbp")
        method = payment_method(
            b.get("segment", "resi"),
            amount,
            b["customer_id"],
            b.get("commodity", "electricity"),
        )
        if method != "direct_debit":
            continue
        by_cust.setdefault(b["customer_id"], []).append(
            (date.fromisoformat(b["period_end"]), amount)
        )

    book = DDBalanceBook()
    # Per-customer forward-filled balance by month, so the portfolio aggregate
    # at any calendar month sums each customer's most recent known balance while
    # they are active (customers bill in different months / start dates).
    per_cust_month_balance: dict[str, dict[str, float]] = {}

    for cid in sorted(by_cust):
        seq = sorted(by_cust[cid], key=lambda t: t[0])
        anchor = seq[0][0]

        # Standing level DD per 12-month window: window 0 = the naive initial
        # estimate (first issued bill amount, exactly dd_review_runner's and
        # dd_collection_book's initial mandate sizing); each later year resets to
        # the prior year's actual/12 recommendation (dd_review._recommended_
        # monthly) -- the identical year-on-year chain dd_review_runner walks.
        windows: dict[int, list[tuple[date, float]]] = {}
        for d, amt in seq:
            windows.setdefault(_months_between(anchor, d) // 12, []).append((d, amt))
        standing_dd_by_window: dict[int, float] = {}
        standing = seq[0][1]
        for wi in sorted(windows):
            standing_dd_by_window[wi] = standing
            actual_annual = sum(a for _, a in windows[wi])
            # Reset for NEXT year from this completed year's actual spend.
            standing = _recommended_monthly(actual_annual)

        # Carry the balance across every billed month. Opening balance is ZERO
        # (a non-zero prior-tenancy opening balance is W2_12's physics -- see the
        # module docstring; do NOT duplicate it here).
        balance = 0.0
        points: list[BalancePoint] = []
        month_balance: dict[str, float] = {}
        for d, amt in seq:
            wi = _months_between(anchor, d) // 12
            collected = standing_dd_by_window[wi]
            month = f"{d.year:04d}-{d.month:02d}"
            # The instructed amount and the banked amount are two separate
            # events (C-S3). `collected` is what the supplier INSTRUCTED -- DD1's
            # level-fixed invariant reads it and a failed collection must not
            # make a level DD stop being level. `banked` is what actually
            # arrived, and only banked money can be held credit.
            outcome = outcomes.get((cid, month), OUTCOME_ASSUMED)
            banked = 0.0 if outcome == OUTCOME_FAILED else collected
            balance += banked - amt
            points.append(BalancePoint(
                month=month,
                collected_gbp=round(collected, 2),
                consumed_gbp=round(amt, 2),
                balance_gbp=round(balance, 2),
                banked_gbp=round(banked, 2),
                collection_outcome=outcome,
            ))
            # If a customer has >1 bill in a calendar month, the LAST wins (the
            # end-of-month position) -- deterministic under the sorted seq.
            month_balance[month] = balance
        book.trajectories[cid] = points
        per_cust_month_balance[cid] = month_balance

    # Aggregate the portfolio held-credit liability month-by-month. For each
    # calendar month between a customer's first and last billed month, forward-
    # fill their last known balance so an inactive-gap month still counts the
    # credit still owed to them.
    all_months = sorted({m for mb in per_cust_month_balance.values() for m in mb})
    for cid, mb in per_cust_month_balance.items():
        first, last = min(mb), max(mb)
        carried = 0.0
        for m in all_months:
            if m < first or m > last:
                continue
            if m in mb:
                carried = mb[m]
            agg = book.monthly.setdefault(
                m, {"held_credit_gbp": 0.0, "portfolio_balance_gbp": 0.0, "n_in_credit": 0}
            )
            agg["portfolio_balance_gbp"] += carried
            if carried > 0:
                agg["held_credit_gbp"] += carried
                agg["n_in_credit"] += 1

    return book
