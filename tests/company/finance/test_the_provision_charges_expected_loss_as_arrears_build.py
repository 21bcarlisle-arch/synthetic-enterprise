"""E6's first slice: the roll-rate provision (`bad_debt_provision.roll_rate_provision_stock`) moves in
the quarter the run's own arrears stock builds, not a year later.

The clock is always the book's own arrears stock: money on bills unpaid more than 30 days, at each
quarter end. Never the published 1.3%-2.8% level. Whether the crisis charge reaches that level is a
separate question, and a world one (the world's non-payment does not step up in 2021-22), filed
against the world's debt atom and not asked here.

Two measures of the lag, both pre-registered before the run was read (prediction: 0 quarters on both):
- `lag_peak`: the quarter with the largest rise in the charge, from the arrears build quarter `Qa`
  through `Qa`+4, minus `Qa`. `Qa` is the quarter with the largest rise in arrears.
- `lag_xcorr`: the L in 0..4 that maximises corr(dP(q+L), dA(q)) over quarters where P is rated.
"""
from __future__ import annotations

import datetime as dt
import statistics

import pytest

from company.billing.account_ledger import LedgerBook
from company.finance import bad_debt_provision as bdp
from tests.company.finance.test_roll_rate_provision import START, _method, _post

MAX_LAG = 4


def _deltas(series):
    return [None if a is None or b is None else b - a for a, b in zip(series, series[1:])]


def build_quarter(arrears, lo, hi):
    d = _deltas(arrears)
    window = [i for i in range(lo, min(hi, len(d))) if d[i] is not None]
    return max(window, key=lambda i: d[i])


def lag_peak(arrears, provision, lo=0, hi=None):
    qa = build_quarter(arrears, lo, len(arrears) - 1 if hi is None else hi)
    dp = _deltas(provision)
    window = [i for i in range(qa, min(qa + MAX_LAG + 1, len(dp))) if dp[i] is not None]
    if not window:
        return None
    return max(window, key=lambda i: dp[i]) - qa


def lag_xcorr(arrears, provision):
    da, dp = _deltas(arrears), _deltas(provision)
    best, best_r = None, None
    for lag in range(MAX_LAG + 1):
        pairs = [(da[i], dp[i + lag]) for i in range(len(da) - lag)
                 if da[i] is not None and dp[i + lag] is not None]
        if len(pairs) < 3:
            continue
        xs, ys = zip(*pairs)
        if statistics.pstdev(xs) == 0 or statistics.pstdev(ys) == 0:
            continue
        r = statistics.correlation(xs, ys)
        if best_r is None or r > best_r:
            best, best_r = lag, r
    return best


def _quarterly(book, months):
    """Arrears stock (unpaid more than 30 days) and the roll-rate provision at each quarter end."""
    arrears, provision, memo = [], [], {}
    for m in range(3, months, 3):
        on = START + dt.timedelta(days=30 * m)
        owed = sum(gbp for acct in book.accounts()
                   for billed, gbp in bdp._residuals(book.ledger(acct), on, cash_only=False).items()
                   if (on - billed).days > 30)
        arrears.append(owed)
        stock = bdp.roll_rate_provision_stock(book, on=on, payment_method_of=_method, memo=memo)
        provision.append(stock["matrix_provision_gbp"])
    return arrears, provision


def test_the_instrument_reads_a_lag_when_there_is_one_defect_a_lag_measure_that_always_says_zero():
    """The rare branch first: a charge that trails its arrears by a year must read as 4 quarters on
    both measures, and one that moves with them as 0. Without this, a green verdict below proves
    nothing about the run."""
    arrears = [100, 100, 100, 100, 400, 700, 800, 800, 800, 800, 800, 800, 800, 800]
    with_it = [10, 10, 10, 10, 40, 70, 80, 80, 80, 80, 80, 80, 80, 80]
    a_year_late = [10] * 4 + with_it[:-4]
    assert lag_peak(arrears, with_it) == 0 and lag_xcorr(arrears, with_it) == 0
    assert lag_peak(arrears, a_year_late) == 4 and lag_xcorr(arrears, a_year_late) == 4


def _stepped_book(stop, months=44, missed=3):
    """Eight households that always pay, two that stop at month 2 (so the matrix has seen the tail),
    and four that miss `missed` bills from month `stop` and then pay their current bills again: the
    arrears stock grows at a steady rate and steps up once, in the quarter of `stop`."""
    book = LedgerBook()
    for k in range(months):
        for i in range(8):
            _post(book, f"PAY{i}", k, 60.0, 60.0)
        for i in range(2):
            _post(book, f"EARLY{i}", k, 60.0, 60.0 if k < 2 else 0.0)
        for i in range(4):
            _post(book, f"CRISIS{i}", k, 60.0, 0.0 if stop <= k < stop + missed else 60.0)
    return book


@pytest.mark.parametrize("stop", [24, 27, 30])
def test_on_a_live_book_the_charge_moves_in_the_build_quarter_defect_the_provision_lags_arrears(stop):
    """The shipped code: wherever the step falls, the charge rises most in that same quarter."""
    arrears, provision = _quarterly(_stepped_book(stop), 44)
    assert build_quarter(arrears, 0, len(arrears) - 1) == stop // 3 - 1
    assert provision[build_quarter(arrears, 0, len(arrears) - 1)] is not None
    assert lag_peak(arrears, provision) == 0
    assert lag_xcorr(arrears, provision) == 0
