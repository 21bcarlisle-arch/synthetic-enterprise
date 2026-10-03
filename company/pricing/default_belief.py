"""What this company has itself seen its customers fail to pay, by payment method and arrears state,
read off its own ledger as of a date -- and the default belief that follows from it.

WHY IT EXISTS. `saas.payment_behaviour.bad_debt_provision_gbp` prices bad debt off a four-segment
table (0.5% low to 8% vulnerable) that nothing ever graded, keyed to a credit-risk register that
holds four hand-typed customers -- so on a run every account is "medium" at 2%. Since `e0370bf94`
the value rule replaces that prior with the account's own unpaid share where the ledger has one,
which prices a currently-clean account at ZERO expected loss next year: the persistence assumption,
and on a clean record it says nothing at all. The book the company has already billed does say
something: how much of a year's billing, by method and by where the account stood when the year
began, was still unpaid a year after the year ended. That is the base rate this module learns.

WHAT ONE OBSERVATION COUNTS. One account-year: the bills issued in `[T, T + 365)`, where `T` is the
account's first bill plus a whole number of years (the anniversary a renewal falls on), and the
BAD-DEBT CHARGE the company books against that account over the year -- the change in its
provision plus anything it wrote off, which is what a supplier's P&L charges for bad debt (Ofgem
Appendix 2 Dec 2024 s.2.4-2.6, knowledge map *Bad debt (DD book)*). The provision at a date is the
unpaid money on the account (FIFO over the rolling balance, `fifo_unpaid_bills`) at its age on the
Centrica Note 17 rows the pricing arm already reads (`value_based_renewal`): the FINAL-BILL row
once the account has closed, else its live row. So the charge is the company's own number, off its
own ledger and the one published table, and no figure that is not on it.

WHY A CHARGE AND NOT "THE SHARE OF THIS YEAR'S BILLS STILL UNPAID". On a rolling balance a later
payment clears the OLDEST bill first, so a household that has owed GBP 200 for three years shows
every one of its first-year bills as paid and the debt as fresh. Reading a year's own bills would
therefore find no default on exactly the persistent debtor. The provision follows the balance
wherever FIFO puts it, and the change in it is the loss the year added.

The observation is dated at the year's end -- or, for an account's last year, at the date it reads
as closed, so the jump to the final-bill row lands in the year the account left. A decision dated
earlier cannot see it. Its covariates are what the decision at `T` could see: payment method, and
the arrears state at `T` (`unknown` in an account's first year, before anything was billed).

THE BELIEF. Per arrears state, the money-weighted charge share observed so far, shrunk towards a
whole-book prior by `PRIOR_ACCOUNT_YEARS` account-years of weight. With no resolved observation in
the state the belief IS the prior. NOT KEYED ON PAYMENT METHOD, on purpose: the price this feeds may
not depend on how a household pays (see the prior). Method enters only in READING a charge, because
the published provision rows are per method; a method with no live row (prepayment) yields no
charge on a live account that owes money, and that year is counted but not learned from.

Pure: plain values and a company `LedgerBook` in, plain values out. No world import.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Callable, Iterable, Optional

from company.billing.account_ledger import LedgerBook, LedgerEventType
from company.billing.arrears_engine import fifo_unpaid_bills
from company.crm.churn_model import ARREARS_STATE_UNKNOWN
from company.pricing.value_based_renewal import (
    _LIVE_PROVISION_ROW_BY_METHOD,
    RECEIVABLE_PROVISION_RATE_FINAL_BILL,
    _banded_rate,
    _live_rate,
)

#: THE PRIOR: residential bad debt at 2.0% of revenue (`docs/market_research/ASSUMPTIONS.md`,
#: *Bad debt rate -- residential*, range 1-3%, Ofgem Annual Report and Cornwall Insight). A WHOLE-BOOK
#: figure, deliberately. Ofgem's cap allowance is published per payment method (DD 1.4%, standard
#: credit 6.5%, prepayment 0.6%, same file's C1(b)), and keying the prior on it would put payment
#: method into the renewal price, which the director ruled out on 2026-09-23 as the prepayment
#: cost-shift (`tests/company/pricing/test_the_price_rests_only_on_observables_a_supplier_may_use.py`).
PRIOR_LOSS_RATE = 0.020

#: A year of bills is one observation, because a renewal prices a year.
OBSERVATION_YEAR_DAYS = 365

#: NAMED SIMPLIFICATION: an account billed nothing in this many days before the reading is read as
#: closed, and its unpaid money is a final-bill receivable. The company bills monthly, so two
#: missed cycles is a closed account and not a late bill. Done properly this reads the company's
#: own loss-of-supply record, which this ledger does not carry.
CLOSED_IF_UNBILLED_DAYS = 62

#: NAMED SIMPLIFICATION: the prior counts as this many account-years of observation in its cell.
#: One is the weakest prior that still gives an answer before any outcome resolves; a thin cell
#: therefore moves fast. To do it properly, fit the weight from the between-cell dispersion of the
#: book's own outcomes (empirical Bayes) once the book is big enough to have one.
PRIOR_ACCOUNT_YEARS = 1.0


@dataclass(frozen=True)
class AccountYear:
    account_id: str
    payment_method: str
    arrears_state: str           # at the start of the year, as the decision then could see it
    year_start: dt.date
    resolved_on: dt.date         # the first date the company could know this outcome
    billed_gbp: float
    closed: bool                 # the account had closed by `resolved_on`
    charge_gbp: Optional[float]  # None: no published live row for this method, so no charge read

    @property
    def charge_share(self) -> Optional[float]:
        if self.charge_gbp is None or self.billed_gbp <= 0.0:
            return None
        return self.charge_gbp / self.billed_gbp


@dataclass(frozen=True)
class DefaultBelief:
    rate: float                  # expected bad-debt charge as a share of a year's bill
    prior_rate: float
    account_years: int           # resolved observations in the cell that carried a loss
    billed_gbp: float
    charge_gbp: float
    reason: Optional[str] = None


def observe_book(
    book: LedgerBook,
    *,
    as_of: dt.date,
    payment_method_of: Callable[[str], Optional[str]],
    arrears_state_at: Callable[[str, dt.date], str],
    memo: Optional[dict] = None,
) -> list[AccountYear]:
    """Every account-year in `book` whose outcome the company knew by `as_of`, oldest first.

    `memo`, if given, keeps each account-year once it has been read, keyed by account and year
    start, so a run that asks at every renewal walks each resolved year once. What is kept is what
    the company knew when it first read it, which is the point-in-time reading in any case.

    `arrears_state_at(account, date)` is the company's own arrears read
    (`PaymentObservationConsumer.arrears_state` with its previous-period clock); it is passed in
    rather than built here so the state this learns from is the one the renewal is priced on.
    """
    out: list[AccountYear] = []
    for account in book.accounts():
        ledger = book.ledger(account)
        bills = sorted((e.valid_time, float(e.amount_gbp)) for e in ledger.events()
                       if e.event_type == LedgerEventType.BILL_DEBIT)
        if not bills:
            continue
        method = payment_method_of(account) or ""
        first, last = bills[0][0], bills[-1][0]
        closes_on = last + dt.timedelta(days=CLOSED_IF_UNBILLED_DAYS)
        opened = first
        k = 0
        while True:
            start = first + dt.timedelta(days=k * OBSERVATION_YEAR_DAYS)
            if start > last:
                break
            end = start + dt.timedelta(days=OBSERVATION_YEAR_DAYS)
            final_year = last < end
            resolved = max(end, closes_on) if final_year else end
            if resolved > as_of:
                break
            k += 1
            if memo is not None and (account, start) in memo:
                kept = memo[(account, start)]
                if kept is not None:
                    out.append(kept)
                    opened = kept.resolved_on
                continue
            billed = sum(g for d, g in bills if start <= d < end)
            if billed <= 0.0:
                if memo is not None:
                    memo[(account, start)] = None
                continue
            charge = _provision(ledger, resolved, method, closes_on)
            if charge is not None:
                before = _provision(ledger, opened, method, closes_on) if k > 1 else 0.0
                written_off = sum(
                    float(e.amount_gbp) for e in ledger.events()
                    if e.event_type == LedgerEventType.WRITE_OFF_CREDIT and opened < e.valid_time <= resolved)
                charge = None if before is None else charge - before + written_off
            year = AccountYear(
                account_id=account,
                payment_method=method,
                arrears_state=ARREARS_STATE_UNKNOWN if k == 1 else arrears_state_at(account, start),
                year_start=start,
                resolved_on=resolved,
                billed_gbp=round(billed, 2),
                closed=resolved >= closes_on,
                charge_gbp=None if charge is None else round(charge, 2),
            )
            if memo is not None:
                memo[(account, start)] = year
            out.append(year)
            opened = resolved
    return sorted(out, key=lambda o: (o.resolved_on, o.account_id))


def _provision(ledger, on: dt.date, method: str, closes_on: dt.date) -> Optional[float]:
    """What the company provisions against this account's unpaid money on `on`."""
    unpaid = [(d, g) for d, g in fifo_unpaid_bills(ledger, on) if g > 0.005]
    if on >= closes_on:
        return sum(g * _banded_rate(RECEIVABLE_PROVISION_RATE_FINAL_BILL, (on - d).days)
                   for d, g in unpaid)
    live_row = _LIVE_PROVISION_ROW_BY_METHOD.get(method)
    if live_row is None:
        return None if unpaid else 0.0
    return sum(g * _live_rate(live_row, (on - d).days) for d, g in unpaid)


def default_belief(
    observations: Iterable[AccountYear],
    *,
    decided_on: dt.date,
    arrears_state: str,
) -> DefaultBelief:
    """The expected charge share for one renewal, from outcomes the company knew BEFORE `decided_on`.

    Point-in-time by construction: an observation resolved on or after the decision date is not
    read, so a renewal priced before any outcome resolved gets exactly the prior.
    """
    cell = [o for o in observations
            if o.resolved_on < decided_on and o.arrears_state == arrears_state
            and o.charge_gbp is not None]
    if not cell:
        return DefaultBelief(rate=PRIOR_LOSS_RATE, prior_rate=PRIOR_LOSS_RATE, account_years=0,
                             billed_gbp=0.0, charge_gbp=0.0,
                             reason="no resolved outcome in this arrears state yet: the prior")
    billed = sum(o.billed_gbp for o in cell)
    charge = sum(o.charge_gbp for o in cell)
    n = len(cell)
    observed = charge / billed if billed > 0 else 0.0
    rate = (PRIOR_ACCOUNT_YEARS * PRIOR_LOSS_RATE + n * observed) / (PRIOR_ACCOUNT_YEARS + n)
    return DefaultBelief(rate=rate, prior_rate=PRIOR_LOSS_RATE, account_years=n,
                         billed_gbp=round(billed, 2), charge_gbp=round(charge, 2))


def tabulate(observations: Iterable[AccountYear]) -> dict:
    """The comparison table: the book's bad-debt charge per GBP billed, by arrears state (what the
    belief learns on), by method x state and by method (diagnostic only), and whole-book."""
    rows: dict = {}
    for o in observations:
        for key in (f"*|{o.arrears_state}", f"{o.payment_method}|{o.arrears_state}",
                    f"{o.payment_method}|*", "*|*"):
            r = rows.setdefault(key, {"account_years": 0, "closed": 0, "billed_gbp": 0.0,
                                      "charge_gbp": 0.0, "charge_unread": 0})
            r["account_years"] += 1
            r["closed"] += int(o.closed)
            if o.charge_gbp is None:
                r["charge_unread"] += 1
                continue
            r["billed_gbp"] += o.billed_gbp
            r["charge_gbp"] += o.charge_gbp
    for r in rows.values():
        b = r["billed_gbp"]
        r["charge_share"] = round(r["charge_gbp"] / b, 4) if b else None
        r["billed_gbp"], r["charge_gbp"] = round(b, 2), round(r["charge_gbp"], 2)
    return dict(sorted(rows.items()))
