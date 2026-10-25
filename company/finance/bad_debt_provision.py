"""Bad debt provisioning by arrears age: the flat table, and a matrix learned from the book's own roll rates.

TWO THINGS LIVE HERE, AND ONLY THE SECOND IS FORWARD-LOOKING IN IFRS 9's SENSE.

- `_PROVISION_RATES` and `build_provision`: a flat age table with no origin and no production caller
  (`docs/market_research/bad_debt_provisioning.md` s.5.1 recommends retiring it). Kept for its tests.
- `roll_rate_provision_stock`: a provision matrix (IFRS 9 B5.5.35) whose loss rate per age is the
  product of the company's OWN monthly roll rates, learned point in time from its ledger, with the
  forward-looking overlay (B5.5.52) run at both of its published ends. The knowledge it builds on, and
  every choice below, is the page's section "A provision matrix whose loss rates come from the
  company's own roll rates" (2026-10-14). Shipped off: `ROLL_RATE_PROVISION`.
- `with_crisis_overlay`: the overlay sized at each date from what a supplier held then -- the cap in
  force against the cap a year earlier -- on the run's published stock. The page's section "Sizing the
  forward-looking overlay from what a supplier held in 2022" (2026-10-24). Default off:
  `DecisionPolicy.provision_crisis_overlay`.
- `arrears_overlay_share`: the second signal, arrears per indebted account on the company's own book
  against its own pre-crisis growth, taken as `max(cap, arrears)` with the cap term, never the sum.
  The page's section "The arrears-per-account signal" (2026-10-24), choices 1-3, 4(a) and 5. Default
  on since 2026-10-25, when the arm met the filed switch-on rule: `DecisionPolicy.provision_arrears_overlay`.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Dict, List, Optional, Tuple


class AgingBucket(str, Enum):
    CURRENT = 'current'
    DAYS_30 = '31_60_days'
    DAYS_60 = '61_90_days'
    DAYS_90 = '91_180_days'
    DAYS_180_PLUS = '180_plus_days'


_PROVISION_RATES = {
    AgingBucket.CURRENT: 0.005,
    AgingBucket.DAYS_30: 0.05,
    AgingBucket.DAYS_60: 0.20,
    AgingBucket.DAYS_90: 0.50,
    AgingBucket.DAYS_180_PLUS: 0.90,
}


def classify_age(days_outstanding: int) -> AgingBucket:
    if days_outstanding <= 30:
        return AgingBucket.CURRENT
    if days_outstanding <= 60:
        return AgingBucket.DAYS_30
    if days_outstanding <= 90:
        return AgingBucket.DAYS_60
    if days_outstanding <= 180:
        return AgingBucket.DAYS_90
    return AgingBucket.DAYS_180_PLUS


@dataclass(frozen=True)
class ArrearsLedgerItem:
    customer_id: str
    outstanding_gbp: float
    days_outstanding: int
    is_vulnerable: bool = False

    @property
    def aging_bucket(self) -> AgingBucket:
        return classify_age(self.days_outstanding)

    @property
    def provision_rate(self) -> float:
        return _PROVISION_RATES[self.aging_bucket]

    @property
    def provision_gbp(self) -> float:
        return round(self.outstanding_gbp * self.provision_rate, 2)


@dataclass(frozen=True)
class BadDebtProvision:
    as_of: dt.date
    items: tuple

    @property
    def total_arrears_gbp(self) -> float:
        return round(sum(i.outstanding_gbp for i in self.items), 2)

    @property
    def total_provision_gbp(self) -> float:
        return round(sum(i.provision_gbp for i in self.items), 2)

    @property
    def provision_coverage_pct(self) -> float:
        if self.total_arrears_gbp == 0:
            return 0.0
        return round(self.total_provision_gbp / self.total_arrears_gbp * 100, 1)

    def by_bucket(self) -> dict:
        buckets: dict = {}
        for i in self.items:
            b = i.aging_bucket.value
            if b not in buckets:
                buckets[b] = {'count': 0, 'arrears_gbp': 0.0, 'provision_gbp': 0.0}
            buckets[b]['count'] += 1
            buckets[b]['arrears_gbp'] = round(buckets[b]['arrears_gbp'] + i.outstanding_gbp, 2)
            buckets[b]['provision_gbp'] = round(buckets[b]['provision_gbp'] + i.provision_gbp, 2)
        return buckets

    def vulnerable_provision_gbp(self) -> float:
        return round(sum(i.provision_gbp for i in self.items if i.is_vulnerable), 2)

    def summary(self) -> dict:
        return {
            'as_of': self.as_of.isoformat(),
            'total_customers': len(self.items),
            'total_arrears_gbp': self.total_arrears_gbp,
            'total_provision_gbp': self.total_provision_gbp,
            'provision_coverage_pct': self.provision_coverage_pct,
            'vulnerable_provision_gbp': self.vulnerable_provision_gbp(),
            'by_bucket': self.by_bucket(),
        }


def build_provision(as_of: dt.date, items: List[ArrearsLedgerItem]) -> BadDebtProvision:
    return BadDebtProvision(as_of=as_of, items=tuple(items))


# --- The roll-rate matrix (2026-10-14) -------------------------------------------------------------

#: SHIPPED OFF. With it on, the company's provision reader publishes the roll-rate stock beside the
#: Centrica-rate matrix (`company.pricing.default_belief.provision_stock`), which stays the run's
#: provision either way. Off, the reader's output is byte-identical to before this switch existed.
ROLL_RATE_PROVISION = False

#: The span of rolls a matrix learns from: Centrica's 2025 auditor "assessed historical debt
#: collection patterns over 2024 and 2025" (docs/market_research/bad_debt_provisioning.md s.2.2). A
#: named choice -- no GB supplier publishes its learning window (GAP).
ROLL_RATE_WINDOW_MONTHS = 24

#: The overlay's two ends, as a share of the total provision (overlay / (matrix + overlay)). Never a
#: midpoint: how a supplier sizes its overlay is GAP. "none" is the matrix alone; "published_high" is
#: `prov_forward_looking_overlay_share`'s high, Centrica ARA 2023, GBP 175m / GBP 1,309m
#: (docs/market_research/assumption_toggles.yaml; bad_debt_provisioning.md s.3.2).
OVERLAY_SHARE_ENDS = (("none", 0.0), ("published_high", 0.134))

#: The weights that turn the cap's two unit rates into one level: Ofgem's typical domestic
#: consumption values, 2,700 kWh electricity and 11,500 kWh gas a year (bad_debt_provisioning.md,
#: "Sizing the forward-looking overlay", 2026-10-24). Unit rates only: the commons artefact holds no
#: standing charges, a named simplification that errs low in 2022.
CAP_LEVEL_KWH = (("electricity", 2700.0), ("gas", 11500.0))

#: The year end at which the overlay reaches the published high: Centrica's crisis overlay sat on its
#: 31 Dec 2022 balance sheet (bad_debt_provisioning.md s.3.2). The ratio there is READ off the cap
#: table, never typed: it is the anchor's own reading of the same signal (2.04 on the commons table).
CRISIS_OVERLAY_ANCHOR = dt.date(2022, 12, 31)

FOOTING_LIVE_DIRECT_DEBIT = "live_direct_debit"
FOOTING_LIVE_OTHER = "live_other"
FOOTING_CLOSED = "closed"
FOOTINGS = (FOOTING_LIVE_DIRECT_DEBIT, FOOTING_LIVE_OTHER, FOOTING_CLOSED)

_DAYS_PER_MONTH = 365.25 / 12


def _terminal_months() -> int:
    from company.finance.cash_forecast_provision import HORIZON_MONTHS
    return HORIZON_MONTHS


def _age_months(billed: dt.date, on: dt.date) -> int:
    return int((on - billed).days // _DAYS_PER_MONTH)


def _month_ends(start: dt.date, end: dt.date) -> List[dt.date]:
    out = []
    y, m = start.year, start.month
    while True:
        nxt = dt.date(y + (m == 12), m % 12 + 1, 1)
        last = nxt - dt.timedelta(days=1)
        if last > end:
            return out
        out.append(last)
        y, m = nxt.year, nxt.month


def _residuals(ledger, on: dt.date, *, cash_only: bool) -> Dict[dt.date, float]:
    """Unpaid GBP per bill date on `on`, oldest bill first (the ledger's FIFO, as
    `arrears_engine.fifo_unpaid_bills`). `cash_only` leaves write-offs out of the credits, so a
    written-off bill stays unpaid and rolls on to the terminal state as the loss it is (IFRS 9
    5.4.4: a write-off is a derecognition, not a recovery)."""
    from company.billing.account_ledger import LedgerEventType
    events = ledger.events_through(on)
    credit = round(sum(e.amount_gbp for e in events if not e.event_type.is_debit
                       and not (cash_only and e.event_type == LedgerEventType.WRITE_OFF_CREDIT)), 2)
    out: Dict[dt.date, float] = {}
    for b in (e for e in events if e.event_type == LedgerEventType.BILL_DEBIT):
        if credit >= round(b.amount_gbp, 2) - 0.005:
            credit = round(credit - b.amount_gbp, 2)
            continue
        unpaid = round(b.amount_gbp - credit, 2)
        credit = 0.0
        if unpaid > 0.005:
            out[b.valid_time] = out.get(b.valid_time, 0.0) + unpaid
    return out


def _footing(ledger, account: str, on: dt.date, payment_method_of) -> Optional[str]:
    from company.billing.account_ledger import LedgerEventType
    from company.pricing.default_belief import CLOSED_IF_UNBILLED_DAYS
    bills = [e.valid_time for e in ledger.events_through(on) if e.event_type == LedgerEventType.BILL_DEBIT]
    if not bills:
        return None
    if (on - max(bills)).days >= CLOSED_IF_UNBILLED_DAYS:
        return FOOTING_CLOSED
    return (FOOTING_LIVE_DIRECT_DEBIT if payment_method_of(account, on) == "direct_debit"
            else FOOTING_LIVE_OTHER)


def _snapshot(book, account: str, on: dt.date, payment_method_of, memo) -> Tuple[Optional[str], dict]:
    key = (account, on)
    if memo is not None and key in memo:
        return memo[key]
    ledger = book.ledger(account)
    snap = (_footing(ledger, account, on, payment_method_of), _residuals(ledger, on, cash_only=True))
    if memo is not None:
        memo[key] = snap
    return snap


@dataclass(frozen=True)
class RollRateMatrix:
    """Loss rate per footing and age in months, learned point in time. `loss_rate[f][k]` is None
    where the book has never had money at an age the chain must pass through."""
    as_of: dt.date
    rolls: Dict[str, List[Optional[float]]]
    loss_rate: Dict[str, List[Optional[float]]]
    transitions: int
    reason: Optional[str] = None


def learn_roll_rates(book, *, as_of: dt.date, payment_method_of: Callable,
                     window_months: int = ROLL_RATE_WINDOW_MONTHS, memo=None) -> RollRateMatrix:
    """Monthly roll rates by footing and age, from rolls whose LATER month-end is on or before
    `as_of` and inside the window: of the GBP a bill still owed (cash only) at month-end s, aged k
    months, the share it still owed at the next month-end. Footing is read at s."""
    from company.finance.cash_forecast_provision import PRIOR_TRANSITIONS
    terminal = _terminal_months()
    start = as_of - dt.timedelta(days=int(window_months * _DAYS_PER_MONTH) + 31)
    ends = _month_ends(start, as_of)
    exposure = {f: [0.0] * terminal for f in FOOTINGS}
    survived = {f: [0.0] * terminal for f in FOOTINGS}
    counts = {f: [0] * terminal for f in FOOTINGS}
    n = 0
    for account in book.accounts():
        for s, s_next in zip(ends, ends[1:]):
            footing, now = _snapshot(book, account, s, payment_method_of, memo)
            if footing is None or not now:
                continue
            _, later = _snapshot(book, account, s_next, payment_method_of, memo)
            for billed, owed in now.items():
                k = _age_months(billed, s)
                if k >= terminal:
                    continue
                exposure[footing][k] += owed
                survived[footing][k] += min(owed, later.get(billed, 0.0))
                counts[footing][k] += 1
                n += 1
    pooled = []
    for k in range(terminal):
        e = sum(exposure[f][k] for f in FOOTINGS)
        pooled.append(sum(survived[f][k] for f in FOOTINGS) / e if e > 0 else None)
    rolls = {}
    for f in FOOTINGS:
        row = []
        for k in range(terminal):
            if pooled[k] is None:
                row.append(None)
                continue
            own = survived[f][k] / exposure[f][k] if exposure[f][k] > 0 else pooled[k]
            c = counts[f][k]
            row.append((c * own + PRIOR_TRANSITIONS * pooled[k]) / (c + PRIOR_TRANSITIONS))
        rolls[f] = row
    loss = {}
    for f in FOOTINGS:
        row = []
        for k in range(terminal):
            product: Optional[float] = 1.0
            for r in rolls[f][k:]:
                if r is None:
                    product = None if product else 0.0
                    break
                product *= r
            row.append(product)
        loss[f] = row
    # A chain that meets an unobserved age after a zero roll multiplies out to 0.0, so a young book
    # whose debt has never reached the last age before terminal reads "no loss" (2017-18 at seed
    # 61109: 320 and 517 rolls, a 0.00 stock). It has not seen the tail, so it cannot say.
    if not n:
        reason = "no roll observed in the window: the book cannot tell its own loss rates yet"
    elif pooled[terminal - 1] is None:
        reason = (f"no debt in the window has reached {terminal - 1} months unpaid: the book has not "
                  f"seen the tail its loss rates run through, so it cannot tell them yet")
    else:
        reason = None
    return RollRateMatrix(as_of=as_of, rolls=rolls, loss_rate=loss, transitions=n, reason=reason)


def roll_rate_provision_stock(book, *, on: dt.date, payment_method_of: Callable, memo=None) -> dict:
    """The provision on `on`: the ledger's receivable (write-offs derecognised), per bill, times the
    learned loss rate for its footing and age (1.0 once it is past the terminal age), then grossed up
    for each overlay end so the overlay is its stated share of the total. Money at an age the book
    cannot rate is reported unprovisioned with the reason, never rated off a borrowed row. While the
    matrix carries a reason the stock is None and the whole receivable is unrated."""
    from company.billing.account_ledger import LedgerEventType
    matrix = learn_roll_rates(book, as_of=on, payment_method_of=payment_method_of, memo=memo)
    terminal = _terminal_months()
    receivable = provided = unrated = written_off = 0.0
    for account in book.accounts():
        ledger = book.ledger(account)
        written_off += sum(e.amount_gbp for e in ledger.events_through(on)
                           if e.event_type == LedgerEventType.WRITE_OFF_CREDIT)
        owed = _residuals(ledger, on, cash_only=False)
        if not owed:
            continue
        footing = _footing(ledger, account, on, payment_method_of)
        for billed, gbp in owed.items():
            receivable += gbp
            k = _age_months(billed, on)
            rate = 1.0 if k >= terminal else matrix.loss_rate[footing][k]
            if rate is None:
                unrated += gbp
            else:
                provided += gbp * rate
    if matrix.reason:
        provided, unrated = None, receivable
    return {
        "as_of": on.isoformat(),
        "window_months": ROLL_RATE_WINDOW_MONTHS,
        "terminal_months": terminal,
        "transitions": matrix.transitions,
        "receivable_gbp": round(receivable, 2),
        "matrix_provision_gbp": None if provided is None else round(provided, 2),
        "unrated_receivable_gbp": round(unrated, 2),
        "by_overlay": {name: None if provided is None else round(provided / (1.0 - share), 2)
                       for name, share in OVERLAY_SHARE_ENDS},
        "written_off_to_date_gbp": round(written_off, 2),
        "loss_rate": {f: [None if r is None else round(r, 4) for r in row]
                      for f, row in matrix.loss_rate.items()},
        "reason": matrix.reason,
    }


def cap_level(on: dt.date) -> Optional[float]:
    """The cap in force on `on`, net of EPG, as one figure: each fuel's unit rate (GBP/MWh) times the
    typical consumption (`CAP_LEVEL_KWH`). None before the cap existed. The window in force on a
    date was always published by that date, so this reads nothing a supplier did not hold."""
    from company.pricing.ofgem_price_cap import get_cap_unit_rate_for_date
    rates = [(get_cap_unit_rate_for_date(fuel, on), kwh) for fuel, kwh in CAP_LEVEL_KWH]
    if any(r is None for r, _ in rates):
        return None
    return sum(r * kwh / 1000.0 for r, kwh in rates)


def _year_earlier(on: dt.date) -> dt.date:
    return on.replace(year=on.year - 1, day=28 if (on.month, on.day) == (2, 29) else on.day)


def cap_ratio(on: dt.date) -> Optional[float]:
    """The cap level on `on` over the level a year earlier; None where either side has no cap."""
    now, then = cap_level(on), cap_level(_year_earlier(on))
    return None if now is None or then is None else now / then


def crisis_overlay_share(on: dt.date) -> Tuple[float, Optional[float], Optional[str]]:
    """(share, ratio, reason): the overlay as a share of the total provision on `on`.

    Linear in the cap's rise, zero when the cap did not rise, and the published high at the anchor
    year end's own ratio and above (the page's choice 1). B5.5.52: an adjustment for conditions the
    history did not hold, moving with the signal. With no cap a year earlier the share is 0.0 and the
    reason says so -- before 2019 there is no published level to read, not a calm year."""
    ratio = cap_ratio(on)
    if ratio is None:
        return 0.0, None, "no published cap a year earlier: the signal cannot be read on this date"
    high = dict(OVERLAY_SHARE_ENDS)["published_high"]
    anchor = cap_ratio(CRISIS_OVERLAY_ANCHOR)
    return min(high, high * max(0.0, ratio - 1.0) / (anchor - 1.0)), ratio, None


#: Ofgem's definition of arrears: owed more than 91 days, per account (bad_debt_provisioning.md, "The
#: arrears-per-account signal", 2026-10-24, and debt_and_collections.md s.2.1). NAMED SIMPLIFICATION:
#: Ofgem's figure excludes debt on a repayment plan; the ledger read here does not know which bills a
#: plan covers, so it counts them. To do it properly, net the collections desk's agreed plans out.
ARREARS_AGE_DAYS = 91

#: The book's own pre-crisis growth is the mean of its year-on-year change at these three year ends,
#: the page's 2017-2019 pre-COVID window (bad_debt_provisioning.md, "The arrears-per-account signal",
#: choice 3). Read only once all three have passed, so nothing is read before it was known.
ARREARS_BASELINE_YEAR_ENDS = (dt.date(2017, 12, 31), dt.date(2018, 12, 31), dt.date(2019, 12, 31))

#: The growth above baseline at which the term reaches the published high: Ofgem's average electricity
#: arrears rose 26.8% to Q4 2023 against a 4.8% 2017-19 baseline (bad_debt_provisioning.md, "The
#: arrears-per-account signal", the record table; 0.268 - 0.048, derived). A look-ahead on any date
#: before 2024, labelled as the 0.134 it scales to is (the page's choice 5).
ARREARS_EXCESS_GROWTH_AT_PUBLISHED_HIGH = 0.268 - 0.048


def arrears_per_indebted_account(book, on: dt.date) -> Tuple[Optional[float], int]:
    """(GBP per indebted account, indebted accounts) on `on`: what each account still owes on bills
    more than `ARREARS_AGE_DAYS` old (the ledger's FIFO, write-offs as credits, so a written-off
    bill has left the receivable), averaged over the accounts owing any. None with no account owing.
    Reads only events valued on or before `on`."""
    cutoff = on - dt.timedelta(days=ARREARS_AGE_DAYS)
    total, heads = 0.0, 0
    for account in book.accounts():
        owed = sum(g for billed, g in _residuals(book.ledger(account), on, cash_only=False).items()
                   if billed < cutoff)
        if owed > 0.005:
            total += owed
            heads += 1
    return (round(total / heads, 2) if heads else None), heads


def arrears_overlay_share(book, on: dt.date, memo=None) -> dict:
    """The arrears term on `on`: the year-on-year growth in arrears per indebted account on the
    company's own book, above the book's own pre-crisis growth, scaled so that the excess the record
    shows for 2023 carries the published high, and never past it. `share` is None, with the reason,
    where the signal cannot be read: before the baseline's last year end has passed, on a book with no
    arrears at a year end the baseline needs (younger than three years), or with none a year earlier.
    None is not zero (K2): the caller takes the cap term alone and says why.

    The 2024 release is left to the signal (choice 4a): a book whose arrears keep growing holds the
    term up, which errs toward a larger provision, the safe direction."""
    memo = {} if memo is None else memo

    def series(d):
        if d not in memo:
            memo[d] = arrears_per_indebted_account(book, d)
        return memo[d]

    per_account, heads = series(on)
    out = {"per_account_gbp": per_account, "indebted_accounts": heads,
           "growth": None, "baseline_growth": None, "share": None, "reason": None}
    if on < ARREARS_BASELINE_YEAR_ENDS[-1]:
        out["reason"] = "the pre-crisis baseline is not complete until 31 Dec 2019"
        return out
    points = [series(_year_earlier(ARREARS_BASELINE_YEAR_ENDS[0]))[0]] + [
        series(d)[0] for d in ARREARS_BASELINE_YEAR_ENDS]
    if any(p is None for p in points):
        out["reason"] = "the book holds no arrears at a year end the baseline needs (younger than three years)"
        return out
    baseline = sum(b / a - 1.0 for a, b in zip(points, points[1:])) / len(ARREARS_BASELINE_YEAR_ENDS)
    then = series(_year_earlier(on))[0]
    out["baseline_growth"] = round(baseline, 4)
    if per_account is None or then is None:
        out["reason"] = "no arrears on the book on the date or a year earlier: the growth cannot be read"
        return out
    growth = per_account / then - 1.0
    high = dict(OVERLAY_SHARE_ENDS)["published_high"]
    share = min(high, high * max(0.0, growth - baseline) / ARREARS_EXCESS_GROWTH_AT_PUBLISHED_HIGH)
    out.update(growth=round(growth, 4), share=round(share, 4))
    return out


def with_crisis_overlay(stock: dict, on: dt.date, arrears: Optional[dict] = None) -> dict:
    """The published provision stock with the crisis overlay grossed onto its `provision_gbp`, so the
    overlay is its stated share of the total. The matrix-only figure stays beside it as
    `matrix_provision_gbp`, so one run's ledger grades both arms. Reads only the date and the
    stock: no ledger, no world. With `arrears` (`arrears_overlay_share`'s reading) the share is the
    larger of the two terms, never their sum: both answer one shock, and a sum would count it twice."""
    cap_share, ratio, reason = crisis_overlay_share(on)
    share, driver = cap_share, "cap"
    if arrears is not None and arrears["share"] is not None and arrears["share"] > cap_share:
        share, driver = arrears["share"], "arrears"
    matrix = float(stock["provision_gbp"])
    total = round(matrix / (1.0 - share), 2)
    overlay = {"share": round(share, 4),
               "cap_ratio": None if ratio is None else round(ratio, 4),
               "overlay_gbp": round(total - matrix, 2), "reason": reason}
    if arrears is not None:
        overlay.update(cap_share=round(cap_share, 4), driver=driver, arrears=arrears)
    return {**stock, "matrix_provision_gbp": stock["provision_gbp"], "provision_gbp": total,
            "crisis_overlay": overlay}
