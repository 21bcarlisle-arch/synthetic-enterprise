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
  billing all carry the same way. That claim was FALSE until 2026-08-03 and is
  now true by construction: the loop collected exactly ONE standing DD per
  BILL, so a quarterly-billed customer was modelled as paying four direct
  debits a year instead of twelve, under-collecting by 3x and manufacturing a
  debit balance out of the billing cadence alone. A level DD is collected
  MONTHLY regardless of how often the customer is billed, so the collection is
  now ``months_elapsed_since_previous_bill * standing`` (>=1). Byte-identical
  for the monthly-billed book this repo runs; correct for every other cadence.
* The DD-customer population and the standing level-DD chain are IDENTICAL to
  the two sibling artefacts so the three stay mutually consistent: the DD
  population is ``payment_method(...) == "direct_debit"`` (same gate as
  ``dd_collection_book``); the standing monthly DD is the amount the supplier SET
  AT REGISTRATION in the first year (handed in through ``opening_dd_gbp``, never
  read off a bill), then each subsequent year is the amount the supplier
  SET after reviewing the prior year's actual spend, asked for through
  ``company/interfaces/dd_review_outcome.py`` -- the very same year-on-year
  re-estimation chain ``dd_review_runner`` walks. (KNIFE pass 3, B4: this used to
  import the company's PRIVATE ``dd_review._recommended_monthly``. The world is
  told the amount; the routine that chose it stays behind the door.)

Deferred / NOT built here (registered, not silently dropped):

* DD3 -- booking this held-credit balance as a LIABILITY in the double-entry
  chart of accounts -- is the registered next step. This module EMITS the
  liability figure DD3 will book (``portfolio_final_held_credit_gbp``); it does
  not itself post to any ledger.
* DD-H -- the belief-vs-truth solvency gap organ -- consumes this module's
  held-credit series (the TRUTH of what is owed back) against the company's
  believed cash-on-hand. Not built here; this is its input.
* The OPENING level-DD balance is ZERO for every customer. The note that used
  to stand here said a non-zero opening was "the prior tenancy's debt this
  customer inherits", parked behind ``W2_12_change_of_tenancy_debt_physics``.
  BOTH halves of that were wrong, corrected 2026-08-03:

  1. **It is not the prior occupant's debt.** SLC 27 / SLC 12.2 -- and
     ``company/crm/change_of_tenancy_register.py``'s own opening lines -- put
     the debt on the PERSON, not the property; an incoming occupant inherits
     nothing and cannot be refused supply over it. A real non-zero opening is
     the occupant's OWN deemed-supply arrears: energy they burned between day 1
     of possession (``DeemedLeg.NEW_OCCUPANT``) and the day their own DD mandate
     started, billed in arrears once they registered.
  2. **W2_12 landing does not unblock it.** W2_12 reached its level target, but
     ``TenancyChangeCoupler`` has no production caller anywhere in the repo
     (only its own tests), and ``simulation/life_events.py`` emits no move
     event of any kind -- the SIM has no tenancy-change stream to couple. So
     there is no live source of deemed-supply windows to open a balance from,
     and wiring an ``opening_balances`` argument now would be a live mechanism
     with a permanently dead input. Registered as work on W2_12's own wiring,
     not silently carried here as a DD residual that looks drawable and is not.

* The OPENING STANDING DD used to be sized from the customer's FIRST ISSUED BILL
  (``seq[0][1]``), which was a measured fidelity defect pinned as a strict xfail
  in this module's suite
  (``test_opening_dd_size_must_not_depend_on_the_join_month``).
  One month's bill annualised flat is a seasonal number: on the real
  book the year-0 standing DD missed the customer's own realised year-0 average
  by +33.2% (gas, April join) and -46.3% (gas, July join), against 2.1% / -1.0%
  / 2.6% for the weakly-seasonal electricity accounts. The error was a function
  of WHICH MONTH the customer joined, which is exactly what a real supplier's
  opening estimate is built to be independent of.

  CORRECTED 2026-09-02 (atom ``D_opening_dd_seasonal_sizing``, level 0 -> 1).
  The amount now arrives as ``opening_dd_gbp``, sized company-side at
  registration from ``company/billing/annual_consumption_estimate.py`` against
  the SLC 27.15 precedence (declaration / industry EAC-AQ / Ofgem TDCV), and no
  coefficient was invented to do it. The xfail is discharged.

  A customer for whom the company could establish NO opening amount is REFUSED,
  not defaulted: they land in ``unestimated_customers`` and get no trajectory.
  There is deliberately no fallback to ``seq[0][1]`` -- restoring one turns
  ``tests/company/billing/test_the_opening_dd_is_never_the_first_issued_bill.py``
  red, and its source leg reads THIS file as well as the runner.
"""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from datetime import date
from typing import Mapping

from company.interfaces.bill_assembly import barred_at_charge_recovery
from company.interfaces.dd_review_outcome import reviewed_monthly_amount
from simulation.arrears_engine import payment_method

# How many per-customer trajectories to carry on the serialised surface so a
# business page can render a REAL customer's seasonal saw-tooth (not a synthetic
# illustration). Deterministic pick: the first N direct-debit customers by id.
_SAMPLE_TRAJECTORY_CUSTOMERS = 6


def _months_between(anchor: date, d: date) -> int:
    """Whole calendar months from ``anchor`` to ``d`` (>=0 for d>=anchor)."""
    return (d.year - anchor.year) * 12 + (d.month - anchor.month)


@dataclass(frozen=True)
class BalancePoint:
    """One customer's level-DD position after a single billed period."""

    month: str            # 'YYYY-MM' of the bill's period_end
    collected_gbp: float  # the fixed STANDING monthly level DD (per collection)
    consumed_gbp: float   # the actual cost of that period's energy (the bill)
    balance_gbp: float    # running (collected*n - consumed); +ve = held credit
    # How many monthly DD collections this bill period spans (C-S5). 1 under
    # monthly billing, 3 under quarterly. Kept SEPARATE from collected_gbp so
    # that field stays the single source of the standing amount DD1's
    # ``dd_level_collection_book`` sizes its fixed collections from -- folding
    # the multiple into it would make DD1 emit one treble-sized collection a
    # quarter instead of three monthly ones, and silently flip its own
    # ``all_schedules_level_fixed`` guard.
    n_collections: int = 1
    #: What the period's energy truly cost: the bill where it was read, the true charge where it
    #: was estimated, and a catch-up bill less the catch-up it carried for earlier periods.
    true_charge_gbp: float | None = None


@dataclass
class DDBalanceBook:
    """Per-customer level-DD seasonal balance trajectories + the portfolio
    held-credit-liability time series they aggregate to."""

    # customer_id -> ordered list of BalancePoint
    trajectories: dict = field(default_factory=dict)
    # 'YYYY-MM' -> aggregate across all DD customers active that month
    monthly: dict = field(default_factory=dict)
    #: DD customers with issued bills but NO established opening amount. They
    #: carry no trajectory and no held credit: without a standing DD there is no
    #: level payment. A result to be published, not a gap to be filled.
    unestimated_customers: list = field(default_factory=list)
    #: SLC 21BA at a direct debit's charge recovery actions -- see `build_dd_balance_book`.
    seek_balance_at_review: bool = False
    barred_at_reviews_gbp: float = 0.0
    barred_at_final_bills_gbp: float = 0.0
    barred_if_sought_at_run_end_gbp: float = 0.0
    barred_by_customer: dict = field(default_factory=dict)
    #: One row per bar actually taken -- `{customer_id, date, amount_gbp, action}` -- which is
    #: what the supplier's books write off (`company/finance/accounting_close`). An exposure on an
    #: open account is not an action and is not here.
    bar_actions: list = field(default_factory=list)

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
                **self._back_billing_summary(),
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
            **self._back_billing_summary(),
        }

    def _back_billing_summary(self) -> dict:
        return {
            "seek_balance_at_review": self.seek_balance_at_review,
            "back_billing_barred_at_reviews_gbp": round(self.barred_at_reviews_gbp, 2),
            "back_billing_barred_at_final_bills_gbp": round(self.barred_at_final_bills_gbp, 2),
            "back_billing_barred_if_sought_at_run_end_gbp": round(
                self.barred_if_sought_at_run_end_gbp, 2),
            "n_customers_barred": sum(1 for v in self.barred_by_customer.values() if v > 0),
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


def _true_charges(bills: list[dict]) -> dict[int, float]:
    """What each period's energy truly cost, as the supplier knows it: `id(bill) -> charge`.

    A read period's bill is its true charge. An estimated period's is its estimate plus a share of
    the catch-up the next read billed, pro rata to the estimates in that run (the estimates are
    already shaped by the company's own seasonal profile). A catch-up bill's own period excludes
    the catch-up it carried for earlier periods. Never the world's `true_total_amount_gbp`: the
    figure is booked, so it must be one the supplier could have formed. A catch-up below the
    materiality threshold was never billed, and leaves its run at the estimates.
    """
    out = {id(b): float(b["total_amount_gbp"]) for b in bills}
    by_supply: dict[tuple, list[dict]] = {}
    for b in bills:
        by_supply.setdefault((b["customer_id"], b.get("commodity")), []).append(b)
    for supply in by_supply.values():
        for c in supply:
            if not c.get("catchup_applied"):
                continue
            out[id(c)] -= float(c.get("catchup_adjustment_gbp") or 0.0)
            run = [b for b in supply if b is not c
                   and c["catchup_period_start"][:10] <= b["period_start"][:10]
                   and b["period_end"][:10] <= c["catchup_period_end"][:10]]
            if not run:
                continue
            delta = float(c.get("catchup_raw_delta_gbp") or 0.0)
            weight = sum(float(b["total_amount_gbp"]) for b in run)
            for b in run:
                share = float(b["total_amount_gbp"]) / weight if weight > 0 else 1.0 / len(run)
                out[id(b)] += delta * share
    return out


def _settle_oldest_first(periods: list[list], amount: float) -> None:
    """Mark `amount` of the oldest open shortfall as settled, so a bar taken once is not taken
    again at the next recovery action."""
    for p in periods:
        take = min(max(p[2] - p[3], 0.0), amount)
        p[3] += take
        amount -= take


def build_dd_balance_book(
    bills: list[dict],
    opening_dd_gbp: Mapping[str, float] | None = None,
    closed_ids: set[str] | None = None,
    seek_balance_at_review: bool = False,
) -> DDBalanceBook:
    """Carry each direct-debit customer's level-DD credit/debit balance
    tick-by-tick and aggregate the portfolio held-credit liability over time.

    ``opening_dd_gbp`` is the monthly amount the supplier SET when each account
    opened -- the world is told the amount, never the routine that chose it
    (the same property the ``reviewed_monthly_amount`` seam exists to hold).
    A customer with no opening amount carries NO balance trajectory and is
    counted in ``unestimated_customers``: without a standing DD there is no
    level payment, and therefore no credit to build or draw down. Inventing one
    from their first bill is the defect this parameter removes.

    SLC 21BA AT EACH CHARGE RECOVERY ACTION. For direct debit the statement is not a demand; the
    debit is, and so is the final bill that asks for the closing balance. At each such action the
    part of the balance owed for energy used more than 12 months before it is barred
    (``bill_assembly.barred_at_charge_recovery``: each period's true charge against what the
    debit collected, surplus paying the oldest shortfall), never more than the debit balance the
    action seeks -- the balance is kept on what was BILLED, and a supplier loses only what it asks
    for. The actions taken here:

    * the FINAL BILL of an account in ``closed_ids`` -> ``barred_at_final_bills_gbp``;
    * the ANNUAL REVIEW, only when ``seek_balance_at_review`` -- the review then raises the debit
      by a twelfth of the debit balance it finds, after writing off the barred part
      -> ``barred_at_reviews_gbp``. Whether a GB supplier's review normally seeks the balance is
      unpublished; the director ruled it an assumption toggle (2026-10-05). False is the review
      as it was: it resets the debit to last year's spend and never asks for the balance, so the
      balance is first sought at the final bill and the trajectories are byte-identical;
    * an account still open at the run's end has had no action seeking its old balance, so its
      figure is an exposure, not a loss: ``barred_if_sought_at_run_end_gbp``.

    The true charge of an estimated period is the supplier's own (`_true_charges`): the run's total
    is known at the read, its split is the company's estimate shape. Each bar taken is listed in
    ``bar_actions`` and written off on the ledger; the held-credit balance itself is still not
    booked as a liability (DD3 is owed).

    Pure, deterministic, idempotent (no RNG, no mutation of ``bills`` or any
    ground-truth structure). See the module docstring for the wall-clean basis
    and the exact consistency with ``dd_collection_book`` / ``dd_review_runner``.
    """
    # Group the company's OWN issued bills by customer, direct-debit only --
    # the same population gate dd_collection_book applies (a customer with no DD
    # mandate holds no seasonal DD credit).
    by_cust: dict[str, list[tuple[date, float]]] = {}
    true_by_cust: dict[str, list[tuple[date, date, float]]] = {}
    true_charge_of = _true_charges(bills)
    for b in bills:
        method = payment_method(
            b.get("segment", "resi"),
            float(b["total_amount_gbp"]),
            b["customer_id"],
            b.get("commodity", "electricity"),
        )
        if method != "direct_debit":
            continue
        by_cust.setdefault(b["customer_id"], []).append(
            (date.fromisoformat(b["period_end"]), float(b["total_amount_gbp"]))
        )
        end = date.fromisoformat(b["period_end"])
        start = (date.fromisoformat(b["period_start"][:10]) if b.get("period_start")
                 else end.replace(day=1))
        true_by_cust.setdefault(b["customer_id"], []).append((end, start, true_charge_of[id(b)]))

    book = DDBalanceBook(seek_balance_at_review=seek_balance_at_review)
    # Per-customer forward-filled balance by month, so the portfolio aggregate
    # at any calendar month sums each customer's most recent known balance while
    # they are active (customers bill in different months / start dates).
    per_cust_month_balance: dict[str, dict[str, float]] = {}

    for cid in sorted(by_cust):
        seq = sorted(by_cust[cid], key=lambda t: t[0])
        truth = sorted(true_by_cust[cid], key=lambda t: t[0])
        anchor = seq[0][0]

        # Standing level DD per 12-month window: window 0 is the amount the
        # supplier SET at registration (an annualised estimate, told to the
        # world through `opening_dd_gbp`); each later year resets to the amount
        # the supplier set at that review, asked for at the seam
        # (reviewed_monthly_amount) -- the identical year-on-year chain
        # dd_review_runner walks.
        #
        # WINDOW 0 USED TO BE `seq[0][1]` -- THE FIRST ISSUED BILL. That made
        # every household's level payment, and therefore the whole seasonal
        # credit trajectory and the portfolio held-credit liability this module
        # exists to measure, an accident of which month the account opened in.
        # Corrected 2026-09-02 with dd_review_runner, which carried the same
        # line: one defect, two implementations, exactly the shape CLAUDE.md
        # names. Held by tests/company/billing/
        # test_the_opening_dd_is_never_the_first_issued_bill.py, whose source
        # leg reads THIS file too.
        opening = (opening_dd_gbp or {}).get(cid)
        if opening is None or opening <= 0.0:
            book.unestimated_customers.append(cid)
            continue
        windows: dict[int, list[tuple[date, float]]] = {}
        for d, amt in seq:
            windows.setdefault(_months_between(anchor, d) // 12, []).append((d, amt))
        standing_dd_by_window: dict[int, float] = {}
        standing = float(opening)
        for wi in sorted(windows):
            standing_dd_by_window[wi] = standing
            actual_annual = sum(a for _, a in windows[wi])
            # Reset for NEXT year from this completed year's actual spend.
            standing = reviewed_monthly_amount(actual_annual)
        # [start, end, true charge, collected] per period, for the recovery actions below.
        recovery: list[list] = []
        barred_here = 0.0

        # Carry the balance across every billed month. Opening balance is ZERO
        # (a non-zero prior-tenancy opening balance is W2_12's physics -- see the
        # module docstring; do NOT duplicate it here).
        balance = 0.0
        points: list[BalancePoint] = []
        month_balance: dict[str, float] = {}
        prev_d: date | None = None
        prev_wi = 0
        for (d, amt), (_, start, true_charge) in zip(seq, truth):
            wi = _months_between(anchor, d) // 12
            if seek_balance_at_review and wi != prev_wi and balance < 0:
                barred = min(-balance, barred_at_charge_recovery(
                    [tuple(p) for p in recovery], start, is_domestic=True))
                _settle_oldest_first(recovery, barred)
                balance += barred
                book.barred_at_reviews_gbp += barred
                if barred > 0:
                    book.bar_actions.append({"customer_id": cid, "date": start.isoformat(),
                                             "amount_gbp": round(barred, 2), "action": "review"})
                barred_here += barred
                standing_dd_by_window[wi] += max(0.0, -balance) / 12.0
            prev_wi = wi
            # A level DD is collected MONTHLY however often the customer is
            # billed (C-S5). Collect one standing DD per month the bill period
            # spans -- 1 under monthly billing (byte-identical to the original),
            # 3 under quarterly. The first bill collects the single DD that
            # funds it; anything less would open every customer in debt by
            # construction.
            n_collections = 1 if prev_d is None else max(1, _months_between(prev_d, d))
            standing = standing_dd_by_window[wi]
            balance += standing * n_collections - amt
            recovery.append([start, d, true_charge, standing * n_collections])
            prev_d = d
            month = f"{d.year:04d}-{d.month:02d}"
            points.append(BalancePoint(
                month=month,
                collected_gbp=round(standing, 2),
                consumed_gbp=round(amt, 2),
                balance_gbp=round(balance, 2),
                n_collections=n_collections,
                true_charge_gbp=round(true_charge, 2),
            ))
            # If a customer has >1 bill in a calendar month, the LAST wins (the
            # end-of-month position) -- deterministic under the sorted seq.
            month_balance[month] = balance
        closing = min(max(0.0, -balance), barred_at_charge_recovery(
            [tuple(p) for p in recovery], seq[-1][0]))
        if closed_ids is not None and cid in closed_ids:
            book.barred_at_final_bills_gbp += closing
            barred_here += closing
            if closing > 0:
                book.bar_actions.append({"customer_id": cid, "date": seq[-1][0].isoformat(),
                                         "amount_gbp": round(closing, 2), "action": "final_bill"})
        else:
            book.barred_if_sought_at_run_end_gbp += closing
        book.barred_by_customer[cid] = round(barred_here, 2)
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
