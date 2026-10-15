"""The provision matrix learned from the company's own roll rates (`company/finance/bad_debt_provision.py`).

Each test names the defect it fires on. The book is synthetic: households that always pay by direct
debit, a few that stop paying early (so the book has seen money at every age), and a crisis cohort
that stops paying at `CRISIS_AT` months.
"""
from __future__ import annotations

import datetime as dt

import pytest

from company.billing.account_ledger import LedgerBook, LedgerEvent, LedgerEventType
from company.finance import bad_debt_provision as bdp

TT = dt.datetime(2020, 1, 1)
START = dt.date(2018, 1, 10)
CRISIS_AT = 24


def _post(book, acct, k, bill, paid):
    day = START + dt.timedelta(days=30 * k)
    book.post(LedgerEvent(f"{acct}-b{k}", acct, LedgerEventType.BILL_DEBIT, bill, day, TT))
    if paid:
        book.post(LedgerEvent(f"{acct}-p{k}", acct, LedgerEventType.PAYMENT_CREDIT, paid,
                              day + dt.timedelta(days=5), TT))


def _book(months=40, crisis=3, write_off_at_months=None):
    book = LedgerBook()
    for i in range(8):
        for k in range(months):
            _post(book, f"PAY{i}", k, 60.0, 60.0)
    for i in range(2):  # early stoppers: the book sees money at every age before the crisis
        for k in range(months):
            _post(book, f"EARLY{i}", k, 60.0, 60.0 if k < 2 else 0.0)
    for i in range(crisis):
        for k in range(months):
            _post(book, f"CRISIS{i}", k, 60.0, 60.0 if k < CRISIS_AT else 0.0)
    if write_off_at_months is not None:
        for acct in [a for a in book.accounts() if not a.startswith("PAY")]:
            for k in range(months):
                bill_day = START + dt.timedelta(days=30 * k)
                wo_day = bill_day + dt.timedelta(days=int(30.5 * write_off_at_months))
                if (acct.startswith("EARLY") and k >= 2) or (acct.startswith("CRISIS") and k >= CRISIS_AT):
                    book.post(LedgerEvent(f"{acct}-w{k}", acct, LedgerEventType.WRITE_OFF_CREDIT, 60.0,
                                          wo_day, TT))
    return book


def _method(acct, on):
    return "direct_debit" if acct.startswith("PAY") else "standard_credit"


def _on(months):
    return START + dt.timedelta(days=30 * months)


def test_the_learned_matrix_reads_nothing_after_its_date_defect_look_ahead():
    """Two books identical up to T and different after it must give the same matrix at T."""
    T = _on(CRISIS_AT - 1)
    pre, post = _book(crisis=3, months=CRISIS_AT), _book(crisis=3)
    a = bdp.learn_roll_rates(pre, as_of=T, payment_method_of=_method)
    b = bdp.learn_roll_rates(post, as_of=T, payment_method_of=_method)
    assert a.transitions > 0
    assert (a.transitions, a.rolls, a.loss_rate) == (b.transitions, b.rolls, b.loss_rate)
    # And the later months DO move it, so the equality above is not two empty matrices agreeing.
    later = bdp.learn_roll_rates(post, as_of=_on(CRISIS_AT + 4), payment_method_of=_method)
    assert later.rolls != b.rolls


def test_the_provision_steps_up_inside_the_year_the_arrears_build_defect_charged_a_year_late():
    """The property the finding asks for: arrears that start building at month 24 are charged
    within the same year, not when the horizon has passed and they are written off."""
    book = _book(crisis=3)
    memo = {}
    before = bdp.roll_rate_provision_stock(book, on=_on(CRISIS_AT - 1), payment_method_of=_method,
                                           memo=memo)
    after = bdp.roll_rate_provision_stock(book, on=_on(CRISIS_AT + 4), payment_method_of=_method,
                                          memo=memo)
    assert before["unrated_receivable_gbp"] == 0.0 and after["unrated_receivable_gbp"] == 0.0
    added_receivable = after["receivable_gbp"] - before["receivable_gbp"]
    added_provision = after["matrix_provision_gbp"] - before["matrix_provision_gbp"]
    assert added_receivable > 500
    assert added_provision > 0.5 * added_receivable


def test_a_write_off_is_a_loss_when_rates_are_learned_not_a_cure_defect_write_off_read_as_cash():
    """With write-offs at three months, a learner that counted them as credits would see the
    stoppers' money vanish at age 3 and learn a near-zero loss rate for it."""
    T = _on(CRISIS_AT - 1)
    plain = bdp.learn_roll_rates(_book(crisis=0), as_of=T, payment_method_of=_method)
    written = bdp.learn_roll_rates(_book(crisis=0, write_off_at_months=3), as_of=T,
                                   payment_method_of=_method)
    assert plain.loss_rate["live_other"][1] > 0.9
    assert written.loss_rate["live_other"][1] == pytest.approx(plain.loss_rate["live_other"][1])


def test_the_overlay_runs_at_both_ends_and_never_between_defect_a_picked_strength():
    book = _book(crisis=3)
    got = bdp.roll_rate_provision_stock(book, on=_on(CRISIS_AT + 4), payment_method_of=_method)
    ends = dict(bdp.OVERLAY_SHARE_ENDS)
    assert set(got["by_overlay"]) == set(ends) == {"none", "published_high"}
    assert ends["none"] == 0.0 and ends["published_high"] == 0.134
    m = got["matrix_provision_gbp"]
    assert m > 0
    assert got["by_overlay"]["none"] == pytest.approx(m, abs=0.01)
    # The overlay is its stated share of the TOTAL: overlay / (matrix + overlay) = 0.134.
    hi = got["by_overlay"]["published_high"]
    assert (hi - m) / hi == pytest.approx(0.134, abs=1e-3)


def test_a_book_with_no_rolls_says_it_cannot_tell_defect_a_prior_dressed_as_an_answer():
    book = LedgerBook()
    _post(book, "NEW", 0, 60.0, 0.0)
    got = bdp.roll_rate_provision_stock(book, on=_on(0) + dt.timedelta(days=3),
                                        payment_method_of=_method)
    assert got["transitions"] == 0 and got["reason"]
    assert got["receivable_gbp"] == 60.0
    assert got["unrated_receivable_gbp"] == 60.0 and got["matrix_provision_gbp"] is None
    assert set(got["by_overlay"].values()) == {None}


def test_a_book_that_has_never_seen_the_tail_says_so_defect_a_zero_roll_read_as_no_loss():
    """Ten months of a book whose stoppers' debt is never older than nine months: plenty of rolls,
    but none at the last age before terminal. The stock is None with that reason, not 0.00. And the
    branch is not stuck: the same book at month 30 has seen the tail and provides."""
    young = _book(crisis=0, months=10)
    got = bdp.roll_rate_provision_stock(young, on=_on(10), payment_method_of=_method)
    assert got["transitions"] > 0
    assert got["matrix_provision_gbp"] is None and "tail" in got["reason"]
    assert got["unrated_receivable_gbp"] == got["receivable_gbp"] > 0
    grown = bdp.roll_rate_provision_stock(_book(crisis=0, months=30), on=_on(30),
                                          payment_method_of=_method)
    assert grown["reason"] is None and grown["matrix_provision_gbp"] > 0


def test_the_reader_publishes_the_roll_rate_stock_only_with_the_switch_on_defect_shipped_on(monkeypatch):
    """Partition control: the switch must be able to take BOTH branches, and off must leave the
    published provision exactly as `default_belief.provision_stock` gives it."""
    from company.billing.payment_observation_consumer import PaymentObservationConsumer
    from company.pricing.default_belief import provision_stock

    assert bdp.ROLL_RATE_PROVISION is False
    consumer = PaymentObservationConsumer.__new__(PaymentObservationConsumer)
    book = _book(crisis=3)
    consumer.ledger_book = book
    on = _on(CRISIS_AT + 4)
    off = consumer.provision_stock(on, payment_method_of=_method)
    assert off == provision_stock(book, on=on, payment_method_of=_method)
    monkeypatch.setattr(bdp, "ROLL_RATE_PROVISION", True)
    on_ = consumer.provision_stock(on, payment_method_of=_method)
    assert "roll_rate" not in off and "roll_rate" in on_
    assert {k: v for k, v in on_.items() if k != "roll_rate"} == off


def test_a_loss_rate_compounds_every_later_roll_defect_one_months_roll_read_as_the_loss():
    """Households that fall two months behind and then clear their arrears cure money at age 2. A
    young balance's loss rate must carry that later cure, so it sits below its own first roll."""
    book = _book(crisis=0)
    for i in range(4):
        for k in range(30):
            day = START + dt.timedelta(days=30 * k)
            book.post(LedgerEvent(f"LATE{i}-b{k}", f"LATE{i}", LedgerEventType.BILL_DEBIT, 60.0, day, TT))
            if k % 3 == 2:  # pays the quarter's three bills in one go, 75 days after the first
                book.post(LedgerEvent(f"LATE{i}-p{k}", f"LATE{i}", LedgerEventType.PAYMENT_CREDIT,
                                      180.0, day + dt.timedelta(days=15), TT))
    m = bdp.learn_roll_rates(book, as_of=_on(CRISIS_AT - 1), payment_method_of=_method)
    rolls, loss = m.rolls["live_other"], m.loss_rate["live_other"]
    assert min(rolls[1:3]) < 0.9
    assert loss[0] < rolls[0] - 0.05
