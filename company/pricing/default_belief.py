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

WHAT IS LEARNED IS THE LOSS ON EACH YEAR'S OWN BILLS, READ BY VINTAGE. A year's whole charge
mixes the provision on that year's billing with the movement on earlier years' (Ofgem App. 2 May
2025 s.4.29, `docs/market_research/bad_debt_provisioning.md`, *The expected loss on new billing*).
The second part is negative when an account pays down arrears it began the year with, and a thin
cell of such accounts learned a negative expected loss: a debtor priced as a source of value
(`df9792c57`). The provision is per bill, so the company can say which year's billing each pound
sits on. A year's reading is the provision on its own bills plus what was written off against
them, a sum of non-negative terms. Each later resolution of the account re-reads it, so a release
lowers the reading of the year the provision was made on, and only that year's. A persistent
debtor stays charged: the debt FIFO moves onto this year's bills is this year's loss, and last
year's reading drops as its bills are paid. Over an account's years the latest readings sum to the
telescoped charge, so nothing is lost or counted twice.

The observation is dated at the year's end -- or, for an account's last year, at the date it reads
as closed, so the jump to the final-bill row lands in the year the account left. A decision dated
earlier cannot see it. Its covariates are what the decision at `T` could see: payment method, and
the arrears state at `T` (`unknown` in an account's first year, before anything was billed).

METHOD IS ASKED AS OF A DATE, because it changes: the company's own collections desk stops a
failing direct debit and the household then pays on receipt (PB8). Each provision is read on the
row for the method the company held ON THAT PROVISION'S DATE, so an account stopped mid-year is
re-provisioned on the pay-on-receipt row at the year's end. That re-rating is a charge a supplier
books. The year's method covariate is the one at `T`. Read once per account for its whole life,
the stopped household stayed on the DD row, and the book's per-method shape was the household's
drawn channel rather than the supplier's own mandate record.

THE BELIEF. Per arrears state, the money-weighted charge share observed so far, shrunk towards a
whole-book prior by `PRIOR_ACCOUNT_YEARS` account-years of weight. With no resolved observation in
the state the belief IS the prior. NOT KEYED ON PAYMENT METHOD, on purpose: the price this feeds may
not depend on how a household pays (see the prior). Method enters only in READING a charge, because
the published provision rows are per method; a method with no live row (prepayment) yields no
charge on a live account that owes money, and that year is counted but not learned from.

Pure: plain values and a company `LedgerBook` in, plain values out. No world import.
"""

from __future__ import annotations

import dataclasses
import datetime as dt
from dataclasses import dataclass
from typing import Callable, Iterable, Optional

from company.billing.account_ledger import LedgerBook, LedgerEventType
from company.billing.arrears_engine import (
    _fifo_unpaid,
    fifo_unpaid_bills,
    written_off_and_recovered,
)
from company.compliance.domain_invariants import refuse_expected_loss_belief_out_of_range
from company.crm.churn_model import ARREARS_STATE_UNKNOWN
from company.pricing.value_based_renewal import (
    _LIVE_PROVISION_ROW_BY_METHOD,
    DIRECT_DEBIT_REPRESENTATION_WINDOW_DAYS,
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
    payment_method_of: Callable[[str, dt.date], Optional[str]],
    arrears_state_at: Callable[[str, dt.date], str],
    memo: Optional[dict] = None,
) -> list[AccountYear]:
    """Every reading of an account-year's loss the company had made by `as_of`, oldest first.

    A year is first read when it resolves. Each later resolution of the same account re-reads it,
    and a reading that moved is returned as a REVISION: the same account and `year_start`, a later
    `resolved_on`. `default_belief` and `tabulate` take the latest reading of each year that was
    known by their date.

    `memo`, if given, keeps what each resolution produced, keyed by account and year start, so a
    run that asks at every renewal walks each resolution once. What is kept is what the company knew
    when it first read it, which is the point-in-time reading in any case.

    `payment_method_of(account, date)` is the company's own method register on that date; it is
    only ever asked of dates at or before `as_of`. `None` means the account is not one the price
    learns from, and none of its years is read. This used to become `""` and the year was kept: the
    run's SME accounts (C5, C6) entered the resi belief's `unknown` cell, one of them with the
    whole of a GBP 75 final-bill charge.

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

        def method_on(day: dt.date, _account=account) -> str:
            return payment_method_of(_account, day) or ""
        first, last = bills[0][0], bills[-1][0]
        closes_on = last + dt.timedelta(days=CLOSED_IF_UNBILLED_DAYS)
        latest: dict[dt.date, AccountYear] = {}   # each year's latest reading, by year start
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
                readings = memo[(account, start)]
            else:
                readings = _readings_at(
                    ledger, account, latest, start=start, end=end, resolved=resolved, k=k,
                    first=first, closes_on=closes_on, bills=bills, method_on=method_on,
                    learned=payment_method_of(account, start) is not None,
                    arrears_state_at=arrears_state_at)
                if memo is not None:
                    memo[(account, start)] = readings
            for r in readings:
                latest[r.year_start] = r
            out.extend(readings)
    return sorted(out, key=lambda o: (o.resolved_on, o.account_id, o.year_start))


def _readings_at(ledger, account, latest, *, start, end, resolved, k, first, closes_on, bills,
                 method_on, learned, arrears_state_at) -> tuple:
    """What resolving the year `[start, end)` on `resolved` adds: that year's first reading, and a
    revision of every earlier year whose loss reads differently now."""
    billed = sum(g for d, g in bills if start <= d < end)
    by_year = _loss_by_year(ledger, resolved, method_on(resolved), closes_on, first)
    readings = []
    if billed > 0.0 and learned:
        charge = None if by_year is None else by_year.get(start, 0.0)
        readings.append(AccountYear(
            account_id=account,
            payment_method=method_on(start),
            arrears_state=ARREARS_STATE_UNKNOWN if k == 1 else arrears_state_at(account, start),
            year_start=start,
            resolved_on=resolved,
            billed_gbp=round(billed, 2),
            closed=resolved >= closes_on,
            charge_gbp=None if charge is None else round(charge, 2),
        ))
    if by_year is not None:
        for year_start, was in latest.items():
            now = round(by_year.get(year_start, 0.0), 2)
            if was.charge_gbp is not None and now != was.charge_gbp:
                readings.append(dataclasses.replace(
                    was, resolved_on=resolved, closed=resolved >= closes_on, charge_gbp=now))
    return tuple(readings)


def _loss_by_year(ledger, on: dt.date, method: str, closes_on: dt.date,
                  first: dt.date) -> Optional[dict]:
    """The loss the company reads on `on` against each year of this account's billing, keyed by the
    year's start: the provision on that year's unpaid bills plus what was written off against them.
    Both are by bill, so a release of an earlier year's provision lowers that year's reading and
    never another's. None where `_provision` reads no charge (no published live row)."""
    def year_of(day: dt.date) -> dt.date:
        return first + dt.timedelta(days=((day - first).days // OBSERVATION_YEAR_DAYS)
                                    * OBSERVATION_YEAR_DAYS)
    rated = _provision(ledger, on, method, closes_on, by_bill=True)
    if rated is None:
        return None
    out: dict[dt.date, float] = {}
    for d, p in rated:
        out[year_of(d)] = out.get(year_of(d), 0.0) + p
    for d, g in _written_off_by_bill(ledger, on):
        out[year_of(d)] = out.get(year_of(d), 0.0) + g
    return out


def _provision(ledger, on: dt.date, method: str, closes_on: dt.date, *, by_bill: bool = False):
    """What the company provisions against this account's unpaid money on `on`; with `by_bill`,
    `(bill date, provision)` for each unpaid bill."""
    unpaid = [(d, g) for d, g in fifo_unpaid_bills(ledger, on) if g > 0.005]
    if on >= closes_on:
        rated = [(d, g * _banded_rate(RECEIVABLE_PROVISION_RATE_FINAL_BILL, (on - d).days))
                 for d, g in unpaid]
    else:
        live_row = _LIVE_PROVISION_ROW_BY_METHOD.get(method)
        if live_row is None:
            if unpaid:
                return None
            rated = []
        else:
            rated = [(d, g * _live_rate(live_row, (on - d).days)) for d, g in unpaid]
    return rated if by_bill else sum(p for _, p in rated)


def _written_off_by_bill(ledger, through: dt.date) -> list[tuple]:
    """`(bill date, GBP)` for each write-off dated on or before `through`, split over the bills it
    cleared: a write-off is a credit, and FIFO spends it on the oldest unpaid bill."""
    out = []
    for e in ledger.events_through(through):
        if e.event_type != LedgerEventType.WRITE_OFF_CREDIT:
            continue
        prefix = list(ledger.events_through(e.valid_time))
        before = dict(_fifo_unpaid([x for x in prefix if x is not e]))
        after = dict(_fifo_unpaid(prefix))
        out.extend((d, g - after.get(d, 0.0)) for d, g in before.items()
                   if g - after.get(d, 0.0) > 0.005)
    return out


#: The footings a provision stock is read on. Three are Centrica Note 17's rows; the fourth is the
#: money no published row covers, reported beside the figure and never provisioned at a borrowed rate.
BUCKET_LIVE_DIRECT_DEBIT = "live_direct_debit"
BUCKET_LIVE_PAY_ON_RECEIPT = "live_pay_on_receipt"
BUCKET_FINAL_BILL = "final_bill"
BUCKET_NO_PUBLISHED_ROW = "no_published_row"
PROVISION_BUCKETS = (BUCKET_LIVE_DIRECT_DEBIT, BUCKET_LIVE_PAY_ON_RECEIPT, BUCKET_FINAL_BILL,
                     BUCKET_NO_PUBLISHED_ROW)
#: Centrica's own age bands, by days beyond invoice date.
AGE_BANDS = ((30, "lt_30d"), (90, "30_90d"), (None, "gt_90d"))
NO_PUBLISHED_ROW_REASON = (
    "Centrica ARA 2025 Note 17 publishes live rows for direct debit and pay on receipt only: no "
    "prepayment row, and its business table is not transcribed "
    "(docs/market_research/dd_failure_basis_and_live_arrears_provision_rates.md, C6). An account "
    "the method register does not answer for (business) or answers prepayment for is owed this "
    "money and carries no provision, rather than one read off a row that is not its own.")


def _band(days: int) -> str:
    for upper, name in AGE_BANDS:
        if upper is None or days < upper:
            return name
    raise AssertionError("the last band is open")


def provision_stock(
    book: LedgerBook,
    *,
    on: dt.date,
    payment_method_of: Callable[[str, dt.date], Optional[str]],
) -> dict:
    """The provision this company holds against its own receivables on `on`: a STOCK, read bucket by
    bucket on the published rows, off its own ledger and its own method register and nothing else.

    The same reading `_provision` gives one account, kept per footing and age band so the figure
    shows where it sits. An account is closed on `on` when nothing was billed to it in the
    `CLOSED_IF_UNBILLED_DAYS` before, asked of the bills it had by then (a later bill is not known).
    `payment_method_of` is asked only of an account that owes money on a live footing.
    """
    buckets = {b: {band: {"receivable_gbp": 0.0,
                          "provision_gbp": None if b == BUCKET_NO_PUBLISHED_ROW else 0.0}
                   for _, band in AGE_BANDS}
               for b in PROVISION_BUCKETS}
    accounts = {b: set() for b in PROVISION_BUCKETS}
    written_off = recovered = 0.0
    for account in book.accounts():
        ledger = book.ledger(account)
        account_written_off, account_recovered = written_off_and_recovered(ledger, on)
        written_off += account_written_off
        recovered += account_recovered
        unpaid = [(d, g) for d, g in fifo_unpaid_bills(ledger, on) if g > 0.005]
        if not unpaid:
            continue
        last_bill = max(e.valid_time for e in ledger.events_through(on)
                        if e.event_type == LedgerEventType.BILL_DEBIT)
        closed = (on - last_bill).days >= CLOSED_IF_UNBILLED_DAYS
        method = None if closed else payment_method_of(account, on)
        live_row = None if closed else _LIVE_PROVISION_ROW_BY_METHOD.get(method or "")
        for billed, gbp in unpaid:
            days = (on - billed).days
            if closed:
                bucket, rate = BUCKET_FINAL_BILL, _banded_rate(RECEIVABLE_PROVISION_RATE_FINAL_BILL, days)
            elif live_row is None:
                bucket, rate = BUCKET_NO_PUBLISHED_ROW, None
            else:
                # `_live_rate` moves a DD bill unpaid past the re-presentation window onto the
                # pay-on-receipt row, so the bucket follows the row the rate was read on.
                rate = _live_rate(live_row, days)
                bucket = (BUCKET_LIVE_DIRECT_DEBIT if method == "direct_debit"
                          and days < DIRECT_DEBIT_REPRESENTATION_WINDOW_DAYS
                          else BUCKET_LIVE_PAY_ON_RECEIPT)
            cell = buckets[bucket][_band(days)]
            cell["receivable_gbp"] += gbp
            if rate is not None:
                cell["provision_gbp"] += gbp * rate
            accounts[bucket].add(account)

    out: dict = {"as_of": on.isoformat(), "buckets": {}}
    for bucket in PROVISION_BUCKETS:
        bands = {band: {"receivable_gbp": round(c["receivable_gbp"], 2),
                        "provision_gbp": None if c["provision_gbp"] is None
                        else round(c["provision_gbp"], 2)}
                 for band, c in buckets[bucket].items()}
        out["buckets"][bucket] = {
            "accounts": len(accounts[bucket]),
            "receivable_gbp": round(sum(c["receivable_gbp"] for c in bands.values()), 2),
            "provision_gbp": (None if bucket == BUCKET_NO_PUBLISHED_ROW
                              else round(sum(c["provision_gbp"] for c in bands.values()), 2)),
            "by_age": bands,
        }
    out["buckets"][BUCKET_NO_PUBLISHED_ROW]["reason"] = NO_PUBLISHED_ROW_REASON
    out["provision_gbp"] = round(sum(
        b["provision_gbp"] for b in out["buckets"].values() if b["provision_gbp"] is not None), 2)
    out["receivable_gbp"] = round(sum(b["receivable_gbp"] for b in out["buckets"].values()), 2)
    out["unprovisioned_receivable_gbp"] = out["buckets"][BUCKET_NO_PUBLISHED_ROW]["receivable_gbp"]
    # What the IFRS 9 charge adds to the stock's movement: write-offs, less recoveries (Ofgem App. 2,
    # May 2025, para 3.14). To date, so a year's flow is the difference of two stocks.
    out["written_off_to_date_gbp"] = round(written_off, 2)
    out["recovered_to_date_gbp"] = round(recovered, 2)
    return out


def default_belief(
    observations: Iterable[AccountYear],
    *,
    decided_on: dt.date,
    arrears_state: str,
) -> DefaultBelief:
    """The expected charge share for one renewal, from outcomes the company knew BEFORE `decided_on`.

    Point-in-time by construction: a reading made on or after the decision date is not read, so a
    renewal priced before any outcome resolved gets exactly the prior. Of each account-year, only
    its latest reading before the decision counts.
    """
    known: dict = {}
    for o in observations:
        if o.resolved_on < decided_on and o.arrears_state == arrears_state:
            key = (o.account_id, o.year_start)
            if key not in known or o.resolved_on > known[key].resolved_on:
                known[key] = o
    cell = [o for o in known.values() if o.charge_gbp is not None]
    if not cell:
        return DefaultBelief(rate=PRIOR_LOSS_RATE, prior_rate=PRIOR_LOSS_RATE, account_years=0,
                             billed_gbp=0.0, charge_gbp=0.0,
                             reason="no resolved outcome in this arrears state yet: the prior")
    billed = sum(o.billed_gbp for o in cell)
    charge = sum(o.charge_gbp for o in cell)
    n = len(cell)
    observed = charge / billed if billed > 0 else 0.0
    rate = (PRIOR_ACCOUNT_YEARS * PRIOR_LOSS_RATE + n * observed) / (PRIOR_ACCOUNT_YEARS + n)
    refuse_expected_loss_belief_out_of_range(
        rate, where=f"default_belief({arrears_state!r}, {decided_on}, {n} account-years)")
    return DefaultBelief(rate=rate, prior_rate=PRIOR_LOSS_RATE, account_years=n,
                         billed_gbp=round(billed, 2), charge_gbp=round(charge, 2))


def tabulate(observations: Iterable[AccountYear]) -> dict:
    """The comparison table: the book's bad-debt charge per GBP billed, by arrears state (what the
    belief learns on), by method x state and by method (diagnostic only), and whole-book. Each
    account-year counts once, at its latest reading."""
    latest: dict = {}
    for o in observations:
        key = (o.account_id, o.year_start)
        if key not in latest or o.resolved_on > latest[key].resolved_on:
            latest[key] = o
    rows: dict = {}
    for o in latest.values():
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
