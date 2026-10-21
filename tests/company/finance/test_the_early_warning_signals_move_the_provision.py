"""The early warning of the forward-cash-forecast provision (`company/finance/cash_forecast_provision.py`,
§9c of the payment-and-debt engine): an ARUDD code 0, a second code 0 inside the month, a missed manual
payment. Each test names the defect it fires on.

The book is synthetic: payers; direct-debit households whose collection comes back code 0 twice and who
then stop paying; households with one code 0 who pay again the month after; households whose mandate
comes back code 1 (cancelled) and who go on paying on receipt; manual payers, one cohort of whom miss a
due date and stop. Subjects are read sixteen days after their last bill, inside its month, their oldest unpaid bill well inside 91 days.
"""
from __future__ import annotations

import datetime as dt

import pytest

from company.billing.account_ledger import LedgerBook, LedgerEvent, LedgerEventType
from company.billing.payment_observation_consumer import DDFailureObservation
from company.finance import cash_forecast_provision as cfp
from interface.contracts.payment_observable_seam import BacsReasonCategory as R

TT = dt.datetime(2020, 1, 1)
START = dt.date(2018, 1, 10)
MONTHS = 30


def _day(k):
    return START + dt.timedelta(days=30 * k)


AS_OF = _day(29) + dt.timedelta(days=16)


def _book(subjects=()):
    """`subjects`: (account, kind, reason) -- `dd` (a code `reason` return on its last collection),
    `dd_twice` (the same, re-presented inside the month and returned again), `manual` (a missed
    due date on its last bill)."""
    book, fails, credit_from = LedgerBook(), {}, {}

    def bill(a, k, paid, pay_day=5):
        book.post(LedgerEvent(f"{a}-b{k}", a, LedgerEventType.BILL_DEBIT, 60.0, _day(k), TT))
        if paid:
            book.post(LedgerEvent(f"{a}-p{k}", a, LedgerEventType.PAYMENT_CREDIT, 60.0,
                                  _day(k) + dt.timedelta(days=pay_day), TT))

    def ret(a, k, reason, offset=5):
        v = _day(k) + dt.timedelta(days=offset)
        fails.setdefault(a, []).append(DDFailureObservation(
            f"M-{a}", a, 60.0, reason, reason.value, v,
            dt.datetime.combine(v + dt.timedelta(days=1), dt.time(8))))

    for i in range(8):
        for k in range(MONTHS):
            bill(f"PAY{i}", k, True)
    for i in range(4):
        a = f"FAIL{i}"
        credit_from[a] = _day(16)
        for k in range(MONTHS):
            bill(a, k, k < 14)
        ret(a, 14, R.INSUFFICIENT_FUNDS)
        ret(a, 15, R.INSUFFICIENT_FUNDS)
    for i in range(4):
        a = f"WOB{i}"
        for k in range(MONTHS):
            bill(a, k, k != 10)
        ret(a, 10, R.INSUFFICIENT_FUNDS)
    for i in range(3):
        a = f"CAN{i}"
        credit_from[a] = _day(13)
        for k in range(MONTHS):
            bill(a, k, k != 12)
        ret(a, 12, R.INSTRUCTION_CANCELLED)
    for i in range(4):
        a = f"MAN{i}"
        credit_from[a] = START
        for k in range(MONTHS):
            bill(a, k, True)
    for i in range(4):
        a = f"MANSTOP{i}"
        credit_from[a] = START
        for k in range(MONTHS):
            bill(a, k, k < 20)
    for a, kind, reason in subjects:
        if kind == "manual":
            credit_from[a] = START
            for k in range(MONTHS):
                bill(a, k, k < 29)
            continue
        for k in range(MONTHS):
            bill(a, k, k < 29)
        ret(a, 29, reason)
        if kind == "dd_twice":
            ret(a, 29, reason, offset=7)

    def method(a, on):
        return "standard_credit" if a in credit_from and on >= credit_from[a] else "direct_debit"

    def signals_of(a, on):
        return cfp.early_warning_signals(book.ledger(a), fails.get(a, []), as_of=on,
                                         payment_method_of=method)
    return book, method, signals_of


def _both(subjects, as_of=AS_OF):
    book, method, signals_of = _book(subjects)
    off = cfp.book_provision(book, as_of=as_of, payment_method_of=method)
    on = cfp.book_provision(book, as_of=as_of, payment_method_of=method, signals_of=signals_of)
    return ({a.account_id: a for a in off.accounts}, {a.account_id: a for a in on.accounts}, off, on)


def test_every_signal_is_read_on_some_account_defect_an_early_warning_branch_no_book_can_take():
    """Partition control, asked before any test of what a signal does: each of the three is the
    reading at a forecast date for some account in missed state 0."""
    _, on, _, _ = _both([("S0", "dd", R.INSUFFICIENT_FUNDS), ("S2", "dd_twice", R.INSUFFICIENT_FUNDS),
                         ("SM", "manual", None)])
    read = {a.signal for a in on.values() if a.signal is not None}
    assert read == set(cfp.SIGNALS), read
    assert all(on[a].missed_state == 0 for a in ("S0", "S2", "SM"))


def test_a_code_0_return_raises_the_accounts_expected_loss_in_its_month_defect_the_provision_waits_for_the_age_band():
    off, on, _, _ = _both([("S0", "dd", R.INSUFFICIENT_FUNDS)])
    before, after = off["S0"], on["S0"]
    assert after.signal == cfp.SIGNAL_CODE_0
    assert after.oldest_unpaid_days < 91 and after.missed_state == 0
    # Read in the month the return arrived: the collection was due on day 5, the return seen on day 6.
    assert (AS_OF - (_day(29) + dt.timedelta(days=6))).days < 31
    assert after.expected_loss_gbp > 10 * max(before.expected_loss_gbp, 0.01)
    assert after.expected_loss_gbp <= after.owed_gbp


def test_a_missed_manual_payment_raises_the_accounts_expected_loss_defect_manual_misses_unread():
    off, on, _, _ = _both([("SM", "manual", None)])
    assert on["SM"].signal == cfp.SIGNAL_MANUAL_MISSED
    assert on["SM"].oldest_unpaid_days < 91
    assert on["SM"].expected_loss_gbp > off["SM"].expected_loss_gbp


def test_a_household_one_bill_behind_that_pays_monthly_misses_no_payment_defect_fifo_arrears_read_as_a_miss():
    """CAN* fell one bill behind at their cancellation and pay every bill on receipt since: by FIFO
    each later bill is unpaid on its due date, and none of those is a missed payment."""
    book, method, signals_of = _book()
    assert sum(g for _, g in cfp.fifo_unpaid_bills(book.ledger("CAN0"), AS_OF)) > 0
    assert [k for _, k in signals_of("CAN0", AS_OF) if k == cfp.SIGNAL_MANUAL_MISSED] == []
    assert [k for _, k in signals_of("MANSTOP0", AS_OF) if k == cfp.SIGNAL_MANUAL_MISSED]


@pytest.mark.parametrize("reason", [r for r in R if r != R.INSUFFICIENT_FUNDS])
def test_a_return_with_any_other_code_is_not_read_as_code_0_defect_return_codes_pooled(reason):
    off, on, _, _ = _both([("SX", "dd", reason)])
    assert on["SX"].signal is None
    assert on["SX"].expected_loss_gbp == off["SX"].expected_loss_gbp


def test_off_is_the_first_slice_unchanged_defect_the_switch_moves_the_book():
    """No signals in, or a source that reports none, is the first slice's book to the penny; and on,
    every account the signals do not touch is too, because the chain is learned beside them."""
    book, method, signals_of = _book([("S0", "dd", R.INSUFFICIENT_FUNDS)])
    off = cfp.book_provision(book, as_of=AS_OF, payment_method_of=method)
    silent = cfp.book_provision(book, as_of=AS_OF, payment_method_of=method,
                                signals_of=lambda a, on: [])
    on = cfp.book_provision(book, as_of=AS_OF, payment_method_of=method, signals_of=signals_of)
    assert silent.accounts == off.accounts
    assert on.expected_loss_gbp != off.expected_loss_gbp, "the switch moved nothing: the on arm is untested"
    for a, b in zip(off.accounts, on.accounts):
        if b.signal is None:
            assert a == b
    rr_off = cfp.learn(book, as_of=AS_OF, payment_method_of=method)
    rr_on = cfp.learn(book, as_of=AS_OF, payment_method_of=method, signals_of=signals_of)
    assert rr_on.counts == rr_off.counts and rr_on.signal_counts and not rr_off.signal_counts


def test_a_signal_the_book_has_never_resolved_is_a_named_gap_defect_a_picked_lift():
    """This book never re-presents inside a month, so it has learned nothing after a second code 0:
    the account that has one cannot be forecast, and the book's total says so rather than summing
    the rest."""
    _, on, _, book_on = _both([("S2", "dd_twice", R.INSUFFICIENT_FUNDS)])
    assert on["S2"].signal == cfp.SIGNAL_CODE_0_AGAIN
    assert on["S2"].expected_loss_gbp is None and "GAP" in on["S2"].reason
    assert book_on.expected_loss_gbp is None


def test_a_signal_after_a_missed_month_is_left_to_the_chain_defect_one_miss_counted_twice():
    """FAIL* miss every due date for a year: the chain carries them at missed state 3 and a signal
    adds nothing."""
    off, on, _, _ = _both([])
    assert on["FAIL0"].missed_state == 3 and on["FAIL0"].signal is None
    assert on["FAIL0"].expected_loss_gbp == off["FAIL0"].expected_loss_gbp


def test_a_return_not_yet_observed_is_not_read_defect_look_ahead_on_the_bacs_feed():
    """The return's collection was due on day 5 and the ARUDD line seen on day 6: on day 5 it is
    not known -- neither read at the forecast date nor listed among the signals known by it (the
    reading alone would pass: a signal is dated when it was seen, and the window ends at the date)."""
    as_of = _day(29) + dt.timedelta(days=5)
    _, on, _, _ = _both([("S0", "dd", R.INSUFFICIENT_FUNDS)], as_of=as_of)
    assert on["S0"].signal is None
    _, _, signals_of = _book([("S0", "dd", R.INSUFFICIENT_FUNDS)])
    assert [d for d, _ in signals_of("S0", as_of) if d > _day(28)] == []
    assert [d for d, _ in signals_of("S0", as_of + dt.timedelta(days=1)) if d > _day(28)]
