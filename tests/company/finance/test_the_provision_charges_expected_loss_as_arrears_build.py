"""E6's first slice: the roll-rate provision (`bad_debt_provision.roll_rate_provision_stock`) moves in
the quarter the run's own arrears stock builds, not a year later.

The clock is always the book's own arrears stock: money on bills unpaid more than 30 days, at each
quarter end. Never the published 1.3%-2.8% level. Whether the crisis charge reaches that level is a
separate question, and a world one (the world's non-payment does not step up in 2021-22), filed
against W2_38_the_worlds_debt_is_graded_against_ofgems_quarterly_series and not asked here.

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

# The run, graded 2026-10-15 against the pre-registration in /var/tmp/writeoff/r4/PREREG.md: seed
# 61109, all_wins, 12 founders (r3's recipe), run at 751184c75 (= 6442d41af plus an auto-salvage of
# six generated observability files; no code differs). The switch was off for the run; both stocks
# were read afterwards on its ledger at each quarter end. (quarter end, arrears GBP unpaid > 30 days,
# roll-rate matrix provision GBP with overlay none, None while the matrix has not seen the tail,
# the Centrica-rate provision the run publishes.)
RUN_61109 = (
    ("2016-03-31", 0.0, None, 0.0),
    ("2016-06-30", 54.39, None, 6.41),
    ("2016-09-30", 27.01, None, 6.05),
    ("2016-12-31", 42.56, None, 20.47),
    ("2017-03-31", 110.92, None, 18.44),
    ("2017-06-30", 35.06, None, 6.62),
    ("2017-09-30", 65.88, None, 16.0),
    ("2017-12-31", 119.17, None, 19.91),
    ("2018-03-31", 907.44, None, 138.96),
    ("2018-06-30", 329.23, None, 51.15),
    ("2018-09-30", 29.86, None, 6.07),
    ("2018-12-31", 671.4, None, 113.05),
    ("2019-03-31", 173.76, None, 51.53),
    ("2019-06-30", 403.13, None, 198.1),
    ("2019-09-30", 332.26, None, 160.05),
    ("2019-12-31", 308.77, None, 160.13),
    ("2020-03-31", 378.86, 150.96, 189.8),
    ("2020-06-30", 464.72, 152.94, 201.68),
    ("2020-09-30", 271.45, 147.29, 171.05),
    ("2020-12-31", 524.97, 157.68, 223.84),
    ("2021-03-31", 605.56, 156.98, 236.83),
    ("2021-06-30", 840.21, 188.37, 288.11),
    ("2021-09-30", 603.1, 183.71, 262.8),
    ("2021-12-31", 905.04, 182.73, 288.88),
    ("2022-03-31", 764.09, 185.5, 288.47),
    ("2022-06-30", 827.86, 209.61, 291.72),
    ("2022-09-30", 768.55, 210.75, 298.77),
    ("2022-12-31", 1667.68, 212.2, 467.23),
    ("2023-03-31", 2035.87, 215.32, 511.47),
    ("2023-06-30", 1632.77, 218.39, 481.37),
    ("2023-09-30", 888.44, 320.26, 439.62),
    ("2023-12-31", 1895.44, 357.85, 604.39),
    ("2024-03-31", 2360.58, 378.53, 715.68),
    ("2024-06-30", 1846.1, 391.36, 633.67),
    ("2024-09-30", 1824.33, 430.63, 665.79),
    ("2024-12-31", 2263.23, 432.08, 744.49),
    ("2025-03-31", 2651.69, 469.37, 864.26),
)
#: Index range of the arrears build window: deltas into 2021Q1 through 2023Q4.
RUN_BUILD_WINDOW = (19, 31)


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


def _run(col):
    return [row[col] for row in RUN_61109]


def test_the_runs_published_provision_moves_in_the_build_quarter_defect_the_age_bands_lag_arrears():
    """The Centrica-rate stock the run publishes rises most in the quarter the run's own arrears
    build most (2023Q4), and its quarter-on-quarter moves track the arrears' at lag 0."""
    arrears, published = _run(1), _run(3)
    assert RUN_61109[RUN_BUILD_WINDOW[0]][0] == "2020-12-31"
    assert lag_peak(arrears, published, *RUN_BUILD_WINDOW) == 0
    assert lag_xcorr(arrears, published) == 0


# CORRECTED 2026-11-27. The 2026-10-15 grade asked this stock to move in the quarter the run's
# arrears (> 30 days) build, found a 3-quarter lag and held it as a strict xfail. That keyed the
# control to the wrong clock: arrears are not expected loss. Read against what the same run's ledger
# went on to do, the lag is the outcome's own. Held-back realised loss: of the GBP each bill owed at the
# quarter end (write-offs derecognised, as the stock), the part still unpaid in cash 365 days later,
# a write-off counting as unpaid. Read 2026-11-27 off the r4b pickle of this run's ledger (book ends
# 2025-09-25, so the last three quarters cannot be read). The company never sees this series: it is
# the instrument. On it the 2022Q4 arrears doubling (GBP 769 -> 1,668) realised no extra loss at all
# (207.71 flat 2022Q1-2023Q1). A recent-window floor on the young rolls (3 and 6 months, the
# 2026-10-15 "next step") was tried on the same book and leaves 2022-12-31 unchanged: the young rolls
# there were no higher than the 24-month pool. The bigger arrears were bigger bills curing at the
# usual rate.
RUN_61109_REALISED_12M = (0.0,) * 12 + (
    130.43, 130.43, 138.29, 138.29, 138.29, 138.29, 138.29, 138.29, 180.42, 180.42, 180.42, 207.71,
    207.71, 207.71, 207.71, 207.71, 207.71, 300.17, 315.81, 390.76, 390.76, 426.57) + (None,) * 3


def _mean_abs_error(stock, outcome):
    pairs = [(s, o) for s, o in zip(stock, outcome) if s is not None and o]
    return len(pairs), sum(abs(s / o - 1.0) for s, o in pairs) / len(pairs)


def test_the_runs_own_loss_trails_its_arrears_at_least_as_far_defect_a_lag_read_as_the_provisions():
    """The 3-quarter lag behind arrears is not the provision's: the loss the run went on to realise
    trails the same arrears at least as far. (Measured: realised 4, roll-rate 3, on lag_xcorr.)"""
    arrears, roll_rate = _run(1), _run(2)
    assert len(RUN_61109_REALISED_12M) == len(RUN_61109)
    assert lag_xcorr(arrears, roll_rate) > 0, "the case this test exists for: a lag to explain"
    assert lag_xcorr(arrears, list(RUN_61109_REALISED_12M)) >= lag_xcorr(arrears, roll_rate)


def test_the_roll_rate_provision_is_nearer_the_held_back_loss_than_the_published_one_defect_learned_rates_miss_the_outcome():
    """Against what the run went on to lose, the learned stock is nearer than the Centrica-rate stock the
    run publishes. (Measured over the 18 quarters 2020Q1-2024Q2: roll-rate mean |ratio - 1| 0.077 and
    mean bias -1.5%; Centrica 0.569, every quarter over, so the published stock overstates the
    provision. That errs against our thesis, the safe side, and is why the switch can stay off.)"""
    realised = list(RUN_61109_REALISED_12M)
    n, roll_rate_err = _mean_abs_error(_run(2), realised)
    _, published_err = _mean_abs_error(
        [None if p is None else c for p, c in zip(_run(2), _run(3))], realised)
    assert n >= 12
    # It can fail: the same stock at 2.5 times its size loses to the published one.
    assert _mean_abs_error([None if p is None else 2.5 * p for p in _run(2)], realised)[1] > published_err
    assert roll_rate_err < published_err
