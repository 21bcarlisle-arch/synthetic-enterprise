"""DD4a (atom DD_seasonal_cashflow_physics) -- the annual DD review as a
FIRST-CLASS, LIVE event.

Before this, ``company/billing/dd_review.py`` held complete, correct review
logic (the SLC 27.15 duty, applied at a +/-5% modelling-convention band,
recommended = actual/12) but had
ZERO live callers anywhere in ``simulation/`` or ``saas/`` -- the exact
"paper compliance" shape the payments-maturity audit named: a mechanism that
cannot "live in time" because nothing drives it over the real portfolio. This
module is the missing driver: at each customer's own 12-month anniversary it
re-estimates the standing DD against the year's actual spend and emits a
review event, so "annual DD review" is a thing that actually happens in a run.

Safe-by-construction, mirroring the ``simulation/dd_collection_book.py``
precedent exactly (a new company-observable artefact where none existed
before, NO existing number changed): this is purely additive and read-only
against ground truth. It reads only the company's OWN issued bills
(``customer_id``, ``period_end``, ``total_amount_gbp`` -- all
company-observable, wall-clean: a real supplier knows what it billed) and
produces a review book + event log. It does NOT mutate bills, records, the
ledger, or any financial figure, and draws no RNG (a pure, deterministic,
idempotent function of the bill list -- C-S2: replaying the same bills
reproduces identical reviews).

DD4b -- the CONSEQUENCE half -- is the registered NEXT gated step, NOT built
here: routing a ``large_increase`` review into the live churn/resentment
engine (``company/core/resentment_ledger.py::ChurnJourneyRegister.
record_friction`` via the ``simulation/run_phase2b.py`` complaint-flow
analogue, ~lines 1329-1392). That crossing shifts ground-truth churn and
therefore published financial figures, and needs population-level run
verification plus RNG-substream care -- deliberately NOT rushed in an additive
tick, exactly as ``dd_collection_book`` deliberately did not touch the
ground-truth arrears/bad-debt pipeline. This module already emits the
``large_increase`` flag DD4b will route on, so the seam is ready.
"""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from datetime import date
from typing import Mapping

from company.billing.dd_review import DDAction, DDReviewBook, review

# A DD INCREASE whose year of actual spend exceeds the standing DD-implied
# annual by more than this percent is a "bill-shock"-class jump -- the
# magnitude a real customer notices and reacts to, and the cut DD4b will route
# into the satisfaction/complaint/churn organ. The review itself already fires
# at +/-5% (a modelling convention under the SLC 27.15 duty, in
# dd_review.review -- there is no SLC 27B); this SECOND, larger cut marks
# the *material shock* subset. Deliberately conservative and NOT sourced to a
# specific published figure -- a documented modelling choice, never a
# fabricated precision claim.
LARGE_INCREASE_THRESHOLD_PCT = 15.0


def _months_between(anchor: date, d: date) -> int:
    """Whole calendar months from ``anchor`` to ``d`` (>=0 for d>=anchor)."""
    return (d.year - anchor.year) * 12 + (d.month - anchor.month)


@dataclass(frozen=True)
class DDReviewEvent:
    """One annual-review event: the company re-estimating a customer's
    standing DD against the year just elapsed. Company-observable throughout."""

    customer_id: str
    review_date: str                # ISO date the review fires (year completed)
    window_index: int               # 0 = first completed year, 1 = second, ...
    current_dd_gbp: float           # standing monthly DD entering the review
    actual_annual_spend_gbp: float  # the company's own issued bills over the year
    recommended_monthly_gbp: float  # actual/12, ceiling-to-pound (dd_review)
    variance_pct: float             # (actual - implied_annual) / implied_annual * 100
    action: str                     # DDAction value: increase / decrease / maintain
    large_increase: bool            # INCREASE beyond LARGE_INCREASE_THRESHOLD_PCT


@dataclass
class DDReviewRunResult:
    book: DDReviewBook
    events: list = field(default_factory=list)
    #: Customer IDs with issued bills but NO established opening DD amount --
    #: households whose direct debit we cannot say was set from anything. A
    #: result, not an error: it is published rather than filled, and it is the
    #: denominator's missing half for any claim about DD review coverage.
    unestimated_customers: list = field(default_factory=list)

    def summary(self) -> dict:
        n = len(self.events)
        unestimated = len(self.unestimated_customers)
        if n == 0:
            return {
                "total_reviews": 0,
                "increase_count": 0,
                "decrease_count": 0,
                "maintain_count": 0,
                "large_increase_count": 0,
                "avg_variance_pct": 0.0,
                "unestimated_customers": unestimated,
            }
        return {
            "total_reviews": n,
            "unestimated_customers": unestimated,
            "increase_count": sum(1 for e in self.events if e.action == DDAction.INCREASE.value),
            "decrease_count": sum(1 for e in self.events if e.action == DDAction.DECREASE.value),
            "maintain_count": sum(1 for e in self.events if e.action == DDAction.MAINTAIN.value),
            "large_increase_count": sum(1 for e in self.events if e.large_increase),
            "avg_variance_pct": round(sum(e.variance_pct for e in self.events) / n, 1),
        }

    def serialise(self) -> dict:
        """JSON-safe form for the run-output surface (mirrors
        ``_serialize_dd_collection_book``): summary plus every event, so a
        per-customer business surface can render one real, evidenced instance."""
        return {
            "summary": self.summary(),
            "events": [dataclasses.asdict(e) for e in self.events],
        }


def run_annual_reviews(
    bills: list[dict],
    *,
    opening_dd_gbp: Mapping[str, float] | None = None,
    large_increase_threshold_pct: float = LARGE_INCREASE_THRESHOLD_PCT,
) -> DDReviewRunResult:
    """Drive ``dd_review.review`` over the portfolio at each customer's own
    12-month anniversary.

    The standing DD entering a customer's FIRST review is the amount the
    supplier SET when the account opened, supplied per customer in
    ``opening_dd_gbp``. Each subsequent year it is the PRIOR review's
    recommendation, so the reviews form the real year-on-year re-estimation
    chain "estimate meets reality".

    THE FIRST BILL IS NOT AN ESTIMATE, AND THIS USED TO PRETEND IT WAS.
    Until 2026-09-02 this function opened every customer at ``seq[0][1]`` --
    their first issued bill -- under the comment "initial estimate = first
    issued bill". That made the standing DD an accident of which month the
    account started in: a first bill falling in January over-sizes the whole
    year, one falling in July under-sizes it. The director's correction of
    2026-09-01: *"There's no such thing as a half-month direct debit -- an
    annualised plan divides estimated annual cost by twelve whatever the start
    date."* An annualised opening amount now comes from
    ``company/billing/annual_consumption_estimate.py``, which sizes it from
    what a supplier actually holds (metered history, the registration EAC/AQ,
    the customer's declaration, or Ofgem's published TDCV) under SLC 27.15.

    **A customer with no opening amount is REFUSED, not invented.** They are
    counted in ``summary()["unestimated_customers"]`` and emit no review at
    all, because there is no established standing DD for the first year to be
    reviewed against and every later year's chain descends from it. That count
    is a result and belongs on the surface: it is the number of households whose
    direct debit we cannot yet say was set from anything. Silently falling back
    to the first bill is exactly the defect this parameter removes, so there is
    no fallback -- ``tests/company/billing/
    test_the_opening_dd_is_never_the_first_issued_bill.py`` fails if one returns.

    Deterministic and idempotent: pure function of its inputs, no RNG, no
    mutation of any input or ground-truth structure.
    """
    by_cust: dict[str, list[tuple[date, float]]] = {}
    for b in bills:
        # Company's OWN issued bills only -- company-observable (wall-clean).
        cid = b["customer_id"]
        by_cust.setdefault(cid, []).append(
            (date.fromisoformat(b["period_end"]), float(b["total_amount_gbp"]))
        )

    result = DDReviewRunResult(book=DDReviewBook(), events=[])

    for cid in sorted(by_cust):
        seq = sorted(by_cust[cid], key=lambda t: t[0])
        anchor = seq[0][0]

        # Bucket the customer's bills into consecutive 12-month windows from
        # their first bill. A window is only REVIEWED once a later window has
        # data -- i.e. once a full year has demonstrably elapsed (matches
        # dd_review.overdue_for_review's ">12 months" gate; never reviews a
        # part-year).
        windows: dict[int, list[tuple[date, float]]] = {}
        max_wi = 0
        for d, amt in seq:
            wi = _months_between(anchor, d) // 12
            windows.setdefault(wi, []).append((d, amt))
            if wi > max_wi:
                max_wi = wi

        # The amount the supplier SET at registration, annualised. Absent ->
        # this customer is refused and counted, never opened from a bill.
        opening = (opening_dd_gbp or {}).get(cid)
        if opening is None or opening <= 0.0:
            result.unestimated_customers.append(cid)
            continue
        standing_dd = float(opening)
        for wi in range(0, max_wi):  # windows 0..max_wi-1 have a following window
            wbills = windows.get(wi)
            if not wbills:
                continue  # gap year (no bills issued); standing DD carries forward
            actual_annual = sum(a for _, a in wbills)
            next_bills = windows.get(wi + 1)
            review_date = (
                min(d for d, _ in next_bills)
                if next_bills
                else max(d for d, _ in wbills)
            )
            r = review(cid, review_date, standing_dd, actual_annual)
            result.book.record(r)
            large = (
                r.action == DDAction.INCREASE
                and r.variance_pct > large_increase_threshold_pct
            )
            result.events.append(
                DDReviewEvent(
                    customer_id=cid,
                    review_date=review_date.isoformat(),
                    window_index=wi,
                    current_dd_gbp=round(standing_dd, 2),
                    actual_annual_spend_gbp=round(actual_annual, 2),
                    recommended_monthly_gbp=r.recommended_monthly_gbp,
                    variance_pct=r.variance_pct,
                    action=r.action.value,
                    large_increase=large,
                )
            )
            # The review resets the DD to its recommendation for next year --
            # what a real supplier's ADDR does after an annual review.
            standing_dd = r.recommended_monthly_gbp

    return result
