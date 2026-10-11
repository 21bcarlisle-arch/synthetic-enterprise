"""The expected-loss provision from a forward cash forecast per account -- the first piece of the
payment-and-debt engine (`docs/staging/SEAT_PROPOSAL_A_PERSONAL_PAYMENT_PLAN_AND_DEBT_AS_A_NEXT_BEST_
ACTION_DESIGNED_AS_ONE_2026-10-11.md` §9a-9b).

WHAT IT COUNTS. IFRS 9 defines a credit loss as the cash due less the cash the entity expects to
receive, probability-weighted (Appendix A; B5.5.28; `docs/market_research/bad_debt_provisioning.md`,
"An expected-loss provision from a forward cash forecast", 2026-10-11). So the provision here is, per
account at a forecast date: the balance owed on bills already issued (the ledger's FIFO walk, the
company's own convention), less the cash the forecast expects to receive against it within the
write-off horizon, probability-weighted over the account's paths. Bills not yet issued are NOT
provisioned -- that is the expected loss on future billing, a pricing quantity, and is never added in.

THE FORECAST, month by month over `HORIZON_MONTHS`:
- the amount due each month: the account's recent direct-debit instalment, or (any other method) the
  bill the forecast expects -- its own last-year bill for that calendar month where it has a year of
  bills, else its mean bill so far (a named simplification until the one consumption forecast of the
  forecast finding lands, priced at rates in force and forward);
- whether it is paid: a monthly ROLL-RATE chain learned from the company's own book -- P(pays / misses /
  closes next month | payment method on the company's register, consecutive months missed 0/1/2/3+);
- after a close, the learned share of the closing balance the company later recovers.

POINT IN TIME. Everything is learned from the company's ledger and method register as of the forecast
date: a transition is read only once its month, and the close window after it, have passed. With no
resolved transition anywhere in the book the provision is None with its reason -- "cannot tell" -- not
a prior dressed as an answer (no GB roll rate is published: knowledge page GAP table).

Pure: a company `LedgerBook` and the company's method register in, plain values out. Nothing from
the world: `tests/company/finance/test_cash_forecast_provision.py` holds that by import census.
"""

from __future__ import annotations

import datetime as dt
import statistics
from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Optional, Tuple

from company.billing.account_ledger import AccountLedger, LedgerBook, LedgerEventType
from company.billing.arrears_engine import fifo_unpaid_bills
from company.pricing.default_belief import CLOSED_IF_UNBILLED_DAYS

#: The write-off point: the forecast runs this many months and money still owed at its end, by an
#: account not then paying, is the loss. Inside Centrica's stated default range of "six to twelve
#: months from the issuance of a final bill" (`prov_final_bill_default_months`, 6-12); the far end,
#: because the clock here starts at the forecast date, not at a final bill.
HORIZON_MONTHS = 12

#: NAMED SIMPLIFICATION: a month counts as PAID when the cash received in it is at least this share of
#: the account's median monthly bill. Half separates "paid this month" from "a stray part-payment"
#: on a monthly-billed book; nothing published sets it. Its sensitivity is the grading's to print.
PAID_MONTH_SHARE_OF_MEDIAN_BILL = 0.5

#: Track-record states: consecutive months with no paid month, capped (the roll-rate buckets).
MISSED_STATES = (0, 1, 2, 3)

#: NAMED SIMPLIFICATION: a cell's own transitions are shrunk to the book's pooled transitions (same
#: missed state, all methods) with this many observations of weight -- the default belief's
#: `PRIOR_ACCOUNT_YEARS` shape. Empirical-Bayes fitting of it is owed once the book is large.
PRIOR_TRANSITIONS = 4.0

#: Post-close recovery before the book has seen a closed account resolve: one minus Centrica's 2025
#: final-bill >90-day coverage (0.878, `prov_coverage_final_bill_over_90d`, range 0.755-0.896, Note 17)
#: -- the published share of an old closed balance a supplier does not provide for. Weighted as one
#: closed account, then the book's own observed recovery takes over.
PRIOR_POST_CLOSE_RECOVERY = round(1.0 - 0.878, 3)
PRIOR_CLOSED_ACCOUNTS = 1.0

#: A post-close recovery is read over this many days after the account's last bill.
POST_CLOSE_RECOVERY_DAYS = 365

_CASH = LedgerEventType.PAYMENT_CREDIT
_BILL = LedgerEventType.BILL_DEBIT


def month_ends(start: dt.date, end: dt.date) -> List[dt.date]:
    """Every calendar month-end in `[start, end]`."""
    out = []
    d = _month_end(start)
    while d <= end:
        out.append(d)
        d = _month_end(d + dt.timedelta(days=1))
    return out


def _month_end(d: dt.date) -> dt.date:
    nxt = (d.replace(day=28) + dt.timedelta(days=4)).replace(day=1)
    return nxt - dt.timedelta(days=1)


@dataclass(frozen=True)
class _History:
    bills: Tuple[Tuple[dt.date, float], ...]
    cash: Tuple[Tuple[dt.date, float], ...]

    @classmethod
    def of(cls, ledger: AccountLedger, through: dt.date) -> "_History":
        ev = ledger.events_through(through)
        return cls(tuple((e.valid_time, float(e.amount_gbp)) for e in ev if e.event_type == _BILL),
                   tuple((e.valid_time, float(e.amount_gbp)) for e in ev if e.event_type == _CASH))

    def cash_in(self, lo: dt.date, hi: dt.date) -> float:
        """Cash received in `(lo, hi]`."""
        return sum(g for d, g in self.cash if lo < d <= hi)

    def median_bill(self, through: dt.date) -> Optional[float]:
        recent = [g for d, g in self.bills if through - dt.timedelta(days=365) < d <= through and g > 0]
        return statistics.median(recent) if recent else None

    def last_bill(self, through: dt.date) -> Optional[dt.date]:
        ds = [d for d, _ in self.bills if d <= through]
        return ds[-1] if ds else None


def _closed(hist: _History, on: dt.date) -> bool:
    last = hist.last_bill(on)
    return last is not None and (on - last).days > CLOSED_IF_UNBILLED_DAYS


def _paid(hist: _History, month_end: dt.date) -> Optional[bool]:
    median = hist.median_bill(month_end)
    if median is None:
        return None
    start = month_end.replace(day=1) - dt.timedelta(days=1)
    return hist.cash_in(start, month_end) >= PAID_MONTH_SHARE_OF_MEDIAN_BILL * median


def missed_state(hist: _History, on: dt.date) -> Optional[int]:
    """Consecutive complete months to `on` with no paid month, capped at 3; None before a first bill."""
    first = hist.bills[0][0] if hist.bills else None
    if first is None or first > on:
        return None
    n = 0
    m = _month_end(on) if _month_end(on) == on else _month_end(on.replace(day=1) - dt.timedelta(days=1))
    while m > first and n < MISSED_STATES[-1]:
        p = _paid(hist, m)
        if p is None or p:
            break
        n += 1
        m = m.replace(day=1) - dt.timedelta(days=1)
    return n


@dataclass
class RollRates:
    """What the book has shown, as of a date: next-month outcomes by (method, missed state)."""
    as_of: dt.date
    counts: Dict[Tuple[str, int], Dict[str, float]] = field(default_factory=dict)
    cash_ratio_num: float = 0.0       # cash received in paid months ...
    cash_ratio_den: float = 0.0       # ... over the amount due those months
    closed_due_gbp: float = 0.0       # balances owed at close, resolved
    closed_recovered_gbp: float = 0.0  # cash later received against them
    closed_accounts: int = 0

    @property
    def transitions(self) -> int:
        return int(sum(sum(c.values()) for c in self.counts.values()))

    def probabilities(self, method: str, state: int) -> Optional[Dict[str, float]]:
        """P(pay / miss / close next month), the cell shrunk to the book's pooled state. None when the
        book has never seen a transition out of this missed state."""
        pooled = {"pay": 0.0, "miss": 0.0, "close": 0.0}
        for (_m, s), c in self.counts.items():
            if s == state:
                for k in pooled:
                    pooled[k] += c.get(k, 0.0)
        n_pool = sum(pooled.values())
        if n_pool == 0:
            return None
        cell = self.counts.get((method, state), {})
        n_cell = sum(cell.values())
        out = {}
        for k in pooled:
            out[k] = (cell.get(k, 0.0) + PRIOR_TRANSITIONS * pooled[k] / n_pool) / (n_cell + PRIOR_TRANSITIONS)
        return out

    @property
    def paid_month_cash_ratio(self) -> float:
        """Cash received in a paid month over the amount due -- 1.0 until the book has a paid month."""
        return self.cash_ratio_num / self.cash_ratio_den if self.cash_ratio_den > 0 else 1.0

    @property
    def post_close_recovery(self) -> float:
        """Share of a closing balance later recovered: the book's money-weighted share over the
        closed accounts it has resolved, shrunk to the published prior by account count."""
        n = self.closed_accounts
        if n == 0 or self.closed_due_gbp <= 0:
            return PRIOR_POST_CLOSE_RECOVERY
        observed = self.closed_recovered_gbp / self.closed_due_gbp
        return (PRIOR_CLOSED_ACCOUNTS * PRIOR_POST_CLOSE_RECOVERY + n * observed) / (PRIOR_CLOSED_ACCOUNTS + n)


def _amount_due(hist: _History, method: str, on: dt.date, month_end: dt.date) -> float:
    """What the account is expected to be asked for in the month ending `month_end`."""
    if method == "direct_debit":
        recent = [g for d, g in hist.cash if on - dt.timedelta(days=95) < d <= on]
        if recent:
            return statistics.median(recent)
    return expected_bill(hist, on, month_end)


def expected_bill(hist: _History, on: dt.date, month_end: dt.date) -> float:
    """The bill the forecast expects for the calendar month ending `month_end`: the account's own
    bill for that month last year where it has a year of bills, else its mean bill so far."""
    past = [(d, g) for d, g in hist.bills if d <= on]
    if not past:
        return 0.0
    if (on - past[0][0]).days >= 365:
        same = [g for d, g in past if d.month == month_end.month and (on - d).days < 365]
        if same:
            return same[-1]
    return sum(g for _, g in past) / len(past)


def learn(book: LedgerBook, *, as_of: dt.date,
          payment_method_of: Callable[[str, dt.date], Optional[str]]) -> RollRates:
    """Every transition the company could have resolved by `as_of`, off its own ledger."""
    rr = RollRates(as_of=as_of)
    for account in book.accounts():
        hist = _History.of(book.ledger(account), as_of)
        if not hist.bills:
            continue
        first = hist.bills[0][0]
        for m in month_ends(first, as_of):
            nxt = _month_end(m + dt.timedelta(days=1))
            if nxt + dt.timedelta(days=CLOSED_IF_UNBILLED_DAYS) > as_of:
                break
            if _closed(hist, m):
                break
            method = payment_method_of(account, m)
            if method is None:
                continue
            state = missed_state(hist, m)
            if state is None:
                continue
            if not any(m < d for d, _ in hist.bills):
                outcome = "close"
            else:
                paid = _paid(hist, nxt)
                if paid is None:
                    continue
                outcome = "pay" if paid else "miss"
                if paid:
                    rr.cash_ratio_num += hist.cash_in(m, nxt)
                    rr.cash_ratio_den += _amount_due(hist, method, m, nxt)
            cell = rr.counts.setdefault((method, state), {"pay": 0.0, "miss": 0.0, "close": 0.0})
            cell[outcome] += 1
        last = hist.last_bill(as_of)
        if last is not None and last + dt.timedelta(days=POST_CLOSE_RECOVERY_DAYS) <= as_of:
            due = sum(g for _, g in fifo_unpaid_bills(book.ledger(account), last))
            if due > 0.005:
                got = hist.cash_in(last, last + dt.timedelta(days=POST_CLOSE_RECOVERY_DAYS))
                rr.closed_due_gbp += due
                rr.closed_recovered_gbp += min(due, got)
                rr.closed_accounts += 1
    return rr


@dataclass(frozen=True)
class AccountProvision:
    account_id: str
    owed_gbp: float               # unpaid on bills issued by the forecast date (FIFO)
    oldest_unpaid_days: int       # age of the oldest unpaid bill, the flat bands' clock
    method: Optional[str]
    missed_state: Optional[int]
    closed: bool
    expected_loss_gbp: Optional[float]
    reason: Optional[str] = None


def account_provision(ledger: AccountLedger, *, as_of: dt.date, method: Optional[str],
                      rates: RollRates) -> AccountProvision:
    """The expected unpaid part of what this account owes at `as_of`, at the write-off point."""
    hist = _History.of(ledger, as_of)
    unpaid = [(d, g) for d, g in fifo_unpaid_bills(ledger, as_of) if g > 0.005]
    owed = round(sum(g for _, g in unpaid), 2)
    oldest = (as_of - unpaid[0][0]).days if unpaid else 0
    closed = _closed(hist, as_of)
    state = missed_state(hist, as_of)
    base = dict(account_id=ledger.account_id, owed_gbp=owed, oldest_unpaid_days=oldest,
                method=method, missed_state=state, closed=closed)
    if owed <= 0:
        return AccountProvision(**base, expected_loss_gbp=0.0)
    recovery = rates.post_close_recovery
    if closed:
        # NAMED SIMPLIFICATION: what a closed account still owes is recovered at the book's
        # post-close share until its recovery window has passed, and not at all after.
        last = hist.last_bill(as_of)
        if last is not None and (as_of - last).days >= POST_CLOSE_RECOVERY_DAYS:
            return AccountProvision(**base, expected_loss_gbp=owed)
        return AccountProvision(**base, expected_loss_gbp=round(owed * (1.0 - recovery), 2))
    if method is None or state is None:
        return AccountProvision(**base, expected_loss_gbp=None,
                                reason="no payment method on the company's register for this date")
    months = [as_of]
    for _ in range(HORIZON_MONTHS):
        months.append(_month_end(months[-1] + dt.timedelta(days=1)))
    ratio = rates.paid_month_cash_ratio
    # Distribution over (missed state, cash applied so far, capped at what is owed): exact, and small
    # because cash beyond `owed` no longer changes the loss.
    dist: Dict[Tuple[int, float], float] = {(state, 0.0): 1.0}
    loss = 0.0
    for m in months[1:]:
        due = _amount_due(hist, method, as_of, m) * ratio
        nxt: Dict[Tuple[int, float], float] = {}
        for (s, cash), p in dist.items():
            probs = rates.probabilities(method, s)
            if probs is None:
                return AccountProvision(**base, expected_loss_gbp=None, reason=(
                    f"the book has resolved no transition out of {s} missed month(s) by {as_of}"))
            if probs["close"] > 0:
                loss += p * probs["close"] * (owed - cash) * (1.0 - recovery)
            if probs["pay"] > 0:
                k = (0, round(min(owed, cash + due), 2))
                nxt[k] = nxt.get(k, 0.0) + p * probs["pay"]
            if probs["miss"] > 0:
                k = (min(s + 1, MISSED_STATES[-1]), cash)
                nxt[k] = nxt.get(k, 0.0) + p * probs["miss"]
        dist = nxt
    # At the write-off point: what an account still not paying owes is lost but for the post-close
    # recovery share; an account paying in the last month is expected to clear the rest.
    for (s, cash), p in dist.items():
        if s > 0:
            loss += p * (owed - cash) * (1.0 - recovery)
    return AccountProvision(**base, expected_loss_gbp=round(min(owed, max(0.0, loss)), 2))


@dataclass(frozen=True)
class BookProvision:
    as_of: dt.date
    accounts: Tuple[AccountProvision, ...]
    transitions_learned: int
    reason: Optional[str] = None

    @property
    def owed_gbp(self) -> float:
        return round(sum(a.owed_gbp for a in self.accounts), 2)

    @property
    def expected_loss_gbp(self) -> Optional[float]:
        """The book's provision, or None when any owing account cannot be forecast -- a partial
        total would read as the whole book's."""
        if self.reason is not None or any(a.expected_loss_gbp is None for a in self.accounts):
            return None
        return round(sum(a.expected_loss_gbp for a in self.accounts), 2)


def book_provision(book: LedgerBook, *, as_of: dt.date,
                   payment_method_of: Callable[[str, dt.date], Optional[str]],
                   accounts: Optional[Iterable[str]] = None) -> BookProvision:
    """Every account's expected-loss provision at `as_of`, rolled up to the book."""
    rates = learn(book, as_of=as_of, payment_method_of=payment_method_of)
    chosen = list(accounts) if accounts is not None else book.accounts()
    rows = tuple(account_provision(book.ledger(a), as_of=as_of,
                                   method=payment_method_of(a, as_of), rates=rates)
                 for a in chosen)
    reason = None if rates.transitions else (
        f"the book has resolved no month's payment outcome by {as_of}: cannot tell")
    return BookProvision(as_of=as_of, accounts=rows, transitions_learned=rates.transitions,
                         reason=reason)
