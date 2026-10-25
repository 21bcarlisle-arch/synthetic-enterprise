"""The bad-debt provision is a stock over the company's OWN receivables, on the published rows.

Defect each control names:
  * the published "provision" is the world's default incidence on revenue, which no supplier holds
    (the run's figure until 2026-10-11): a world-truth input reaching the company's provision reds
    `test_the_runs_provision_is_read_from_the_company_ledger_and_nothing_else`;
  * a closed account's money is provisioned on a live row (Centrica: 87.8% against 7.4-50.3% past
    90 days);
  * money with no published row is provisioned at a borrowed rate, or dropped from the receivable;
  * a bill the company had not yet issued on the reading date decides whether the account is live;
  * one of the four footings is unreachable, so a control on it passes vacuously.
"""

import ast
import datetime as dt
import importlib.util
from pathlib import Path

from company.billing.account_ledger import LedgerBook, LedgerEvent, LedgerEventType
from company.billing.payment_observation_consumer import PaymentObservationConsumer
from company.pricing.default_belief import (
    BUCKET_FINAL_BILL,
    BUCKET_LIVE_DIRECT_DEBIT,
    BUCKET_LIVE_PAY_ON_RECEIPT,
    BUCKET_NO_PUBLISHED_ROW,
    PROVISION_BUCKETS,
    provision_stock,
)


def _source(module: str) -> str:
    return Path(importlib.util.find_spec(module).origin).read_text()

TT = dt.datetime(2030, 1, 1)
ON = dt.date(2019, 12, 31)
FIRST = dt.date(2017, 1, 1)


def _post(book, acct, *, months, unpaid=(), amount=100.0, first=FIRST):
    for m in range(months):
        day = first + dt.timedelta(days=30 * m)
        book.post(LedgerEvent(f"{acct}-b{m}", acct, LedgerEventType.BILL_DEBIT, amount, day, TT))
        if m not in unpaid:
            book.post(LedgerEvent(f"{acct}-p{m}", acct, LedgerEventType.PAYMENT_CREDIT, amount,
                                  day + dt.timedelta(days=10), TT))


def _book():
    """One account on each footing. The last bill of a 36-month account is 2019-11-17, 44 days
    before `ON`; a 37-month account's is 2019-12-17, 14 days before."""
    book = LedgerBook()
    _post(book, "DD", months=37, unpaid=(36,))            # 14 days old, inside re-presentation
    _post(book, "DD_LATE", months=36, unpaid=(35,))       # 44 days old, re-rated to pay on receipt
    _post(book, "SC", months=36, unpaid=(33,))            # FIFO moves it to the newest: 44 days
    _post(book, "GONE", months=24, unpaid=(23,))          # last billed 2018-10-23: closed
    _post(book, "PPM", months=36, unpaid=(35,))
    _post(book, "SME", months=36, unpaid=(35,))
    _post(book, "PAID", months=36)
    return book


METHODS = {"DD": "direct_debit", "DD_LATE": "direct_debit", "SC": "standard_credit",
           "GONE": "standard_credit", "PPM": "prepayment", "SME": None, "PAID": "direct_debit"}


def _stock(book=None, on=ON):
    return provision_stock(book or _book(), on=on, payment_method_of=lambda a, d: METHODS[a])


def test_every_footing_is_reachable_and_each_reads_its_own_published_row():
    stock = _stock()
    b = stock["buckets"]
    assert all(b[k]["accounts"] for k in PROVISION_BUCKETS), b
    # Centrica ARA 2025 Note 17 p.175, read by hand at these ages.
    assert b[BUCKET_LIVE_DIRECT_DEBIT]["by_age"]["lt_30d"] == {"receivable_gbp": 100.0,
                                                               "provision_gbp": 0.0}
    assert b[BUCKET_LIVE_PAY_ON_RECEIPT]["by_age"]["30_90d"] == {"receivable_gbp": 200.0,
                                                                 "provision_gbp": 30.2}
    assert b[BUCKET_FINAL_BILL]["by_age"]["gt_90d"] == {"receivable_gbp": 100.0,
                                                        "provision_gbp": 87.8}
    assert stock["provision_gbp"] == 118.0
    assert stock["receivable_gbp"] == 600.0


def test_money_no_published_row_covers_is_owed_and_carries_no_provision():
    b = _stock()["buckets"][BUCKET_NO_PUBLISHED_ROW]
    assert b["accounts"] == 2 and b["receivable_gbp"] == 200.0
    assert b["provision_gbp"] is None and "prepayment" in b["reason"]
    assert all(c["provision_gbp"] is None for c in b["by_age"].values())


def test_closed_is_asked_of_the_bills_the_company_had_on_the_reading_date():
    """A bill posted after the reading date cannot make the account live on it."""
    book = LedgerBook()
    _post(book, "GONE", months=24, unpaid=(23,))
    book.post(LedgerEvent("GONE-late", "GONE", LedgerEventType.BILL_DEBIT, 50.0,
                          dt.date(2020, 2, 1), TT))
    assert _stock(book)["buckets"][BUCKET_FINAL_BILL]["accounts"] == 1
    later = _stock(book, on=dt.date(2020, 2, 10))["buckets"]
    assert later[BUCKET_FINAL_BILL]["accounts"] == 0
    assert later[BUCKET_LIVE_PAY_ON_RECEIPT]["accounts"] == 1


def test_the_consumer_door_reads_its_own_ledger():
    book = _book()
    consumer = PaymentObservationConsumer(ledger_book=book)
    assert consumer.provision_stock(ON, payment_method_of=lambda a, d: METHODS[a]) == _stock(book)
    book.post(LedgerEvent("GONE-paid", "GONE", LedgerEventType.PAYMENT_CREDIT, 100.0,
                          dt.date(2019, 6, 1), TT))
    assert consumer.provision_stock(
        ON, payment_method_of=lambda a, d: METHODS[a])["buckets"][BUCKET_FINAL_BILL]["accounts"] == 0


#: What the run's provision may be computed from: the company's ledger (through the triad door), the
#: reading date, and the company's own method register. Anything else is a new input to review.
_ALLOWED_CALL_NAMES = {"_company_provision_by_year_end", "_payment_triad", "effective_end",
                       "_book_method_of"}
_ALLOWED_BODY_NAMES = {"triad", "effective_end", "payment_method_of", "date", "int", "range",
                       "REPORT_START", "end", "dates", "d", "y", "stocks", "Exception", "exc",
                       "print", "repr", "str", "dict", "write_offs"}
#: The company's own policy switch for the crisis overlay (`bad_debt_provision.with_crisis_overlay`),
#: which reads only the date and the stock.
_ALLOWED_CALL_NAMES |= {"policy"}
_ALLOWED_BODY_NAMES |= {"crisis_overlay", "bool"}
#: ...and for the arrears term, which reads the same ledger through the triad (`arrears_overlay_share`).
_ALLOWED_BODY_NAMES |= {"arrears_overlay"}


def _names(node):
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}


def test_the_runs_provision_is_read_from_the_company_ledger_and_nothing_else():
    tree = ast.parse(_source("simulation.run_phase2b"))
    values = [v for n in ast.walk(tree) if isinstance(n, ast.Dict)
              for k, v in zip(n.keys, n.values)
              if isinstance(k, ast.Constant) and k.value == "company_provision"]
    assert len(values) == 1, "the run records the company's provision exactly once"
    assert _names(values[0]) <= _ALLOWED_CALL_NAMES, _names(values[0]) - _ALLOWED_CALL_NAMES
    fn = next(n for n in ast.walk(tree)
              if isinstance(n, ast.FunctionDef) and n.name == "_company_provision_by_year_end")
    assert _names(fn) <= _ALLOWED_BODY_NAMES, _names(fn) - _ALLOWED_BODY_NAMES
    reads = [c for c in ast.walk(fn) if isinstance(c, ast.Call)
             and isinstance(c.func, ast.Attribute) and c.func.attr == "provision_stock"]
    assert reads, "the stock is the triad's (the company ledger's) reading"


def _run_output(**phase2b):
    base = {"all_records": [], "committee_wake_ups": [], "hedge_evolution": {},
            "starting_treasury": 0.0, "final_treasury": 0.0, "total_gross": 0.0,
            "total_capital": 0.0, "administration_event": None, "customer_events": []}
    base.update(phase2b)
    return {"phase2b": base, "years": {"2017": {}}}


def test_the_published_provision_is_the_companys_and_the_worlds_figure_does_not_move_it():
    from saas.reporting.annual_report import extract_report_data

    stock = {"by_date": {ON.isoformat(): _stock()}, "closing": _stock()}
    one = extract_report_data(_run_output(company_provision=stock, provisioned_total_bad_debt=1.0))
    two = extract_report_data(_run_output(company_provision=stock, provisioned_total_bad_debt=9e9))
    assert one["company_provision"] == two["company_provision"] == stock
    # A run that did not record the company's stock publishes none: the world's figure never stands in.
    assert extract_report_data(_run_output(provisioned_total_bad_debt=5.0))["company_provision"] is None


def test_the_companys_provision_imports_nothing_but_the_company_and_the_standard_library():
    tree = ast.parse(_source("company.pricing.default_belief"))
    imported = {(n.module or "") for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)} | {
        a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
    assert imported, "the parse found the module's imports"
    own_root = provision_stock.__module__.partition(".")[0]
    assert {m for m in imported if m.split(".")[0] != own_root} <= {
        "__future__", "datetime", "dataclasses", "typing"}, imported


def test_the_stop_notice_board_is_cleared_only_after_the_provision_has_read_it():
    """The company provision asks `get_payment_method(as_of=)`, which refuses once the run's DD
    stop-notice board is cleared. Cleared before the read (42b2eb254 to 2026-10-12), every run
    published "could not be read". Fires if any clear in `_main` precedes the read."""
    tree = ast.parse(_source("simulation.run_phase2b"))
    main = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "_main")
    reads = [k.lineno for n in ast.walk(main) if isinstance(n, ast.Dict)
             for k in n.keys if isinstance(k, ast.Constant) and k.value == "company_provision"]
    clears = [n.lineno for n in ast.walk(main) if isinstance(n, ast.Call)
              and getattr(n.func, "id", None) == "install_stop_notice_board"
              and n.args and isinstance(n.args[0], ast.Constant) and n.args[0].value is None]
    assert reads and clears, (reads, clears)
    assert min(clears) > max(reads), (
        f"the board is cleared at line {min(clears)}, before the provision reads it at {max(reads)}")
