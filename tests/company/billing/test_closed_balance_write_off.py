"""The company writes off a closed account's unpaid balance a year after its final bill, and nothing else.

Knowledge: `docs/market_research/bad_debt_provisioning.md`, section "When the company writes off
its own closed-account debt, and what the recoveries line counts" (2026-10-15).
"""
import datetime as dt

from company.billing.account_ledger import LedgerBook, LedgerEvent, LedgerEventType
from company.billing.arrears_engine import (
    CLOSED_ACCOUNT_WRITE_OFF_AFTER_FINAL_BILL_DAYS,
    closed_balance_write_offs,
    written_off_and_recovered,
)
from company.compliance.crisis_bad_debt_validator import extract_series_from_run_output
from company.pricing.default_belief import provision_stock

ON = dt.date(2020, 12, 31)
TT = dt.datetime.combine(ON, dt.time(23, 59))


def _at(day: dt.date) -> dt.datetime:
    return dt.datetime.combine(day, dt.time(0, 0))


def _bill(book, acct, gbp, day):
    book.post(LedgerEvent(f"bill:{acct}:{day}", acct, LedgerEventType.BILL_DEBIT, gbp, day, _at(day)))


def _pay(book, acct, gbp, day, recorded=None):
    book.post(LedgerEvent(f"pay:{acct}:{day}:{recorded}", acct, LedgerEventType.PAYMENT_CREDIT, gbp,
                          day, _at(recorded or day)))


def _book():
    """Four accounts, one per branch: closed a year+ and owing; closed but too recently; live and
    owing; closed a year+ but paid up."""
    book = LedgerBook()
    old = ON - dt.timedelta(days=CLOSED_ACCOUNT_WRITE_OFF_AFTER_FINAL_BILL_DAYS)
    _bill(book, "GONE", 100.0, old - dt.timedelta(days=30))
    _bill(book, "GONE", 80.0, old)
    _pay(book, "GONE", 30.0, old)
    _bill(book, "RECENT", 50.0, old + dt.timedelta(days=1))
    _bill(book, "LIVE", 40.0, old - dt.timedelta(days=200))
    _bill(book, "LIVE", 60.0, ON - dt.timedelta(days=10))
    _bill(book, "PAID", 70.0, old - dt.timedelta(days=5))
    _pay(book, "PAID", 70.0, old)
    return book


def test_only_a_closed_account_a_year_past_its_final_bill_is_written_off_and_for_what_it_owes():
    """One control over the whole partition: the rare branch is taken (GONE) AND each refusal holds.
    Defect it names: a sweep that writes off everything owing, or nothing at all."""
    posted = closed_balance_write_offs(_book(), ON, TT)
    assert {e.account_id: e.amount_gbp for e in posted} == {"GONE": 150.0}
    assert posted[0].event_type == LedgerEventType.WRITE_OFF_CREDIT and posted[0].valid_time == ON
    assert "final bill" in posted[0].reason


def test_a_second_sweep_posts_nothing():
    """Defect: a sweep that writes the same balance off twice, doubling the charge."""
    book = _book()
    closed_balance_write_offs(book, ON, TT)
    assert closed_balance_write_offs(book, ON, TT) == []
    # A month on, only the account that has since come due is written off; GONE is not again.
    later = closed_balance_write_offs(book, ON + dt.timedelta(days=31), TT)
    assert [e.account_id for e in later] == ["RECENT"]


def test_the_sweep_reads_the_ledger_as_it_stood_and_late_cash_is_a_recovery():
    """A payment VALUED before the sweep but RECORDED after it was not known on the day. Defect: a
    sweep run after the run reads cash the company did not yet have, and the write-off shrinks."""
    book = _book()
    _pay(book, "GONE", 20.0, ON - dt.timedelta(days=3), recorded=ON + dt.timedelta(days=5))
    posted = closed_balance_write_offs(book, ON, TT)
    assert {e.account_id: e.amount_gbp for e in posted} == {"GONE": 150.0}
    assert written_off_and_recovered(book.ledger("GONE"), ON + dt.timedelta(days=10)) == (150.0, 20.0)
    assert written_off_and_recovered(book.ledger("PAID"), ON) == (0.0, 0.0)


def test_the_write_off_moves_the_charge_by_only_the_unprovisioned_share_of_closed_debt():
    """The stock falls by the provision on what is written off and the write-off is added, so the
    IFRS 9 charge rises by the final-bill row's unprovisioned 12.2%. Defect: a write-off missing from
    the published stock (the charge would FALL by 87.8% of it), or one counted on top of its provision."""
    book = _book()
    method = lambda _a, _d: "direct_debit"  # noqa: E731 -- only LIVE is asked
    before = provision_stock(book, on=ON, payment_method_of=method)
    closed_balance_write_offs(book, ON, TT)
    after = provision_stock(book, on=ON, payment_method_of=method)
    assert (before["written_off_to_date_gbp"], after["written_off_to_date_gbp"]) == (0.0, 150.0)
    charge = (after["provision_gbp"] - before["provision_gbp"]) + after["written_off_to_date_gbp"]
    assert abs(charge - 150.0 * (1 - 0.878)) < 0.02


def test_the_ifrs9_basis_subtracts_recoveries():
    """Defect: recoveries published but left out of the charge (Ofgem App. 2, May 2025, para 3.14)."""
    stock = lambda p, w, r: {"provision_gbp": p, "written_off_to_date_gbp": w,  # noqa: E731
                             "recovered_to_date_gbp": r}
    run = {"company_provision": {"by_date": {"2019-12-31": stock(10.0, 0.0, 0.0),
                                             "2020-12-31": stock(12.0, 5.0, 1.5)}},
           "management_accounts": {"2019": {"income_statement": {"revenue_gbp": 1000.0}},
                                   "2020": {"income_statement": {"revenue_gbp": 1000.0}}}}
    bd, _rev = extract_series_from_run_output(run, "ifrs9_charge")
    assert bd[2020] == 2.0 + 5.0 - 1.5


def test_the_runs_month_end_sweeps_write_off_on_the_first_month_end_the_clock_allows():
    """The triad runs the sweep at every month end once the run is over. Defect: a calendar that
    skips months (the write-off lands in the wrong year) or never reaches `through`."""
    from background.live_payment_triad import LivePaymentTriad

    triad = LivePaymentTriad()
    # The first bill is a month before the final one, so a calendar stepping two months from the
    # first bill misses the March month end.
    _bill(triad._ledger_book, "GONE", 10.0, dt.date(2018, 2, 10))
    _bill(triad._ledger_book, "GONE", 90.0, dt.date(2018, 3, 10))
    assert triad.write_off_closed_balances(dt.date(2019, 3, 30)) == 0
    assert triad.write_off_closed_balances(dt.date(2019, 4, 30)) == 1
    (event,) = [e for e in triad._ledger_book.ledger("GONE").events()
                if e.event_type == LedgerEventType.WRITE_OFF_CREDIT]
    assert (event.valid_time, event.amount_gbp) == (dt.date(2019, 3, 31), 100.0)
