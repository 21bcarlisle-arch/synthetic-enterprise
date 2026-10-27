"""Tests for tools/generate_payment_ledger_data.py -- BILLING_AND_PAYMENTS_LEDGER.md
(Phase RP): per-account chronological ledger (invoice/payment/notice/write-off/
recovery) with a running balance, patched onto site/data/customers/<cid>.json,
built from the same real billing_ledger.json invoices/payments/arrears_history
already used by generate_invoice_data.py / generate_billing_ledger.py."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.generate_payment_ledger_data import _book_as_of_date, build_account_ledger

_INV_PAID = dict(invoice_number=1, issue_date="2020-01-31", total_amount_gbp=100.0)
_PAY_SUCCESS = dict(invoice_number=1, payment_date="2020-02-14", amount_gbp=100.0,
                     method="direct_debit", outcome="success")


def _cust(invoices, payments, arrears_history=None):
    return dict(invoices=invoices, payments=payments, arrears_history=arrears_history or [])


def _stage(stage, date, note, amount_gbp=None):
    d = dict(stage=stage, date=date, note=note)
    if amount_gbp is not None:
        d["amount_gbp"] = amount_gbp
    return d


def test_book_as_of_date_is_max_issue_date_across_all_customers():
    ledger_customers = dict(
        C1=dict(invoices=[dict(issue_date="2020-01-31"), dict(issue_date="2020-06-30")]),
        C2=dict(invoices=[dict(issue_date="2021-03-31")]),
    )
    assert _book_as_of_date(ledger_customers) == "2021-03-31"


def test_book_as_of_date_none_when_no_invoices():
    assert _book_as_of_date(dict(C1=dict(invoices=[]))) is None


def test_simple_paid_invoice_settles_to_zero():
    cust = _cust([_INV_PAID], [_PAY_SUCCESS])
    ledger = build_account_ledger(cust, as_of="2025-01-01")
    assert ledger["current_balance_gbp"] == 0.0
    assert ledger["total_billed_gbp"] == 100.0
    assert ledger["total_collected_gbp"] == 100.0
    assert ledger["total_written_off_gross_gbp"] == 0.0
    types = [e["type"] for e in ledger["entries"]]
    assert types == ["invoice_raised", "payment_received"]


def test_reconciliation_identity_holds_for_paid_invoice():
    cust = _cust([_INV_PAID], [_PAY_SUCCESS])
    ledger = build_account_ledger(cust, as_of="2025-01-01")
    lhs = ledger["total_collected_gbp"] + ledger["current_balance_gbp"] + ledger["total_written_off_gross_gbp"]
    assert round(lhs, 2) == ledger["total_billed_gbp"]


def test_unpaid_invoice_within_terms_stays_open_no_arrears_case():
    inv = dict(invoice_number=1, issue_date="2025-05-20", total_amount_gbp=50.0)
    pay = dict(invoice_number=1, payment_date="2025-06-03", amount_gbp=50.0,
               method="direct_debit", outcome="success")
    cust = _cust([inv], [pay])
    ledger = build_account_ledger(cust, as_of="2025-05-25")
    assert ledger["current_balance_gbp"] == 50.0
    assert ledger["total_collected_gbp"] == 0.0


def test_written_off_invoice_zeroes_balance_with_write_off_entry():
    inv = dict(invoice_number=7, issue_date="2016-01-31", total_amount_gbp=75.60)
    pay = dict(invoice_number=7, payment_date="2016-02-14", amount_gbp=75.60,
               method="direct_debit", outcome="failed")
    arr = dict(invoice_number=7, arrears_gbp=75.60, opened_date="2016-02-14", stages=[
        _stage("DD_FAILED", "2016-02-14", "Direct debit returned"),
        _stage("FIRST_NOTICE", "2016-02-21", "First notice"),
        _stage("SECOND_NOTICE", "2016-03-07", "Second notice"),
        _stage("WRITTEN_OFF", "2016-05-14", "Debt written off"),
        _stage("PLACED_WITH_DCA", "2016-06-13", "Placed with DCA"),
        _stage("RECOVERED", "2016-12-10", "DCA recovered GBP12.85 net of commission", amount_gbp=12.85),
    ])
    cust = _cust([inv], [pay], [arr])
    ledger = build_account_ledger(cust, as_of="2025-01-01")
    assert ledger["current_balance_gbp"] == 0.0
    assert ledger["total_written_off_gross_gbp"] == 75.60
    assert ledger["total_recovered_gbp"] == 12.85
    assert ledger["total_collected_gbp"] == 0.0
    types = [e["type"] for e in ledger["entries"]]
    assert types == ["invoice_raised", "payment_failed", "notice", "notice", "write_off", "recovery_note"]
    write_off_entry = next(e for e in ledger["entries"] if e["type"] == "write_off")
    recovery_entry = next(e for e in ledger["entries"] if e["type"] == "recovery_note")
    assert write_off_entry["running_balance_gbp"] == 0.0
    assert recovery_entry["running_balance_gbp"] == 0.0
    assert recovery_entry["amount_gbp"] == 0.0
    assert recovery_entry["info_amount_gbp"] == 12.85


def test_point_in_time_honesty_future_stages_withheld():
    inv = dict(invoice_number=7, issue_date="2016-01-31", total_amount_gbp=75.60)
    pay = dict(invoice_number=7, payment_date="2016-02-14", amount_gbp=75.60,
               method="direct_debit", outcome="failed")
    arr = dict(invoice_number=7, arrears_gbp=75.60, opened_date="2016-02-14", stages=[
        _stage("DD_FAILED", "2016-02-14", "Direct debit returned"),
        _stage("FIRST_NOTICE", "2016-02-21", "First notice"),
        _stage("SECOND_NOTICE", "2016-03-07", "Second notice"),
        _stage("WRITTEN_OFF", "2016-05-14", "Debt written off"),
        _stage("PLACED_WITH_DCA", "2016-06-13", "Placed with DCA"),
        _stage("RECOVERED", "2016-12-10", "DCA recovered GBP12.85 net of commission", amount_gbp=12.85),
    ])
    cust = _cust([inv], [pay], [arr])
    ledger = build_account_ledger(cust, as_of="2016-03-07")
    types = [e["type"] for e in ledger["entries"]]
    assert types == ["invoice_raised", "payment_failed", "notice", "notice"]
    assert ledger["current_balance_gbp"] == 75.60
    assert ledger["total_written_off_gross_gbp"] == 0.0
    assert ledger["total_recovered_gbp"] == 0.0


def test_resolved_arrears_case_counts_as_collected_not_written_off():
    inv = dict(invoice_number=3, issue_date="2018-01-31", total_amount_gbp=60.0)
    pay = dict(invoice_number=3, payment_date="2018-02-14", amount_gbp=60.0,
               method="direct_debit", outcome="failed")
    arr = dict(invoice_number=3, arrears_gbp=60.0, opened_date="2018-02-14", stages=[
        _stage("DD_FAILED", "2018-02-14", "Direct debit returned"),
        _stage("FIRST_NOTICE", "2018-02-21", "First notice"),
        _stage("SECOND_NOTICE", "2018-03-07", "Second notice"),
        _stage("RESOLVED", "2018-03-31", "Arrears cleared via payment plan"),
    ])
    cust = _cust([inv], [pay], [arr])
    ledger = build_account_ledger(cust, as_of="2025-01-01")
    assert ledger["current_balance_gbp"] == 0.0
    assert ledger["total_collected_gbp"] == 60.0
    assert ledger["total_written_off_gross_gbp"] == 0.0
    resolved = next(e for e in ledger["entries"] if e["type"] == "arrears_resolved")
    assert resolved["method"] == "payment_plan"


def test_ic_dispute_terminal_payment_plan_agreed_counts_as_collected():
    inv = dict(invoice_number=5, issue_date="2019-06-30", total_amount_gbp=5000.0)
    pay = dict(invoice_number=5, payment_date="2019-07-14", amount_gbp=5000.0,
               method="bacs", outcome="dispute")
    arr = dict(invoice_number=5, arrears_gbp=5000.0, opened_date="2019-07-14", stages=[
        _stage("INVOICE_DISPUTED", "2019-07-14", "Invoice disputed"),
        _stage("DISPUTE_NOTICE", "2019-07-28", "Dispute notice"),
        _stage("PAYMENT_PLAN_AGREED", "2019-08-13", "Payment plan agreed"),
    ])
    cust = _cust([inv], [pay], [arr])
    ledger = build_account_ledger(cust, as_of="2025-01-01")
    assert ledger["current_balance_gbp"] == 0.0
    assert ledger["total_collected_gbp"] == 5000.0


def test_debt_sale_uses_debt_sale_method_and_stays_informational():
    inv = dict(invoice_number=9, issue_date="2016-01-31", total_amount_gbp=200.0)
    pay = dict(invoice_number=9, payment_date="2016-02-14", amount_gbp=200.0,
               method="direct_debit", outcome="failed")
    arr = dict(invoice_number=9, arrears_gbp=200.0, opened_date="2016-02-14", stages=[
        _stage("DD_FAILED", "2016-02-14", "Direct debit returned"),
        _stage("FIRST_NOTICE", "2016-02-21", "First notice"),
        _stage("SECOND_NOTICE", "2016-03-07", "Second notice"),
        _stage("WRITTEN_OFF", "2016-05-14", "Debt written off"),
        _stage("PLACED_WITH_DCA", "2016-06-13", "Placed with DCA"),
        _stage("SOLD", "2016-09-11", "Debt sold to purchaser", amount_gbp=30.0),
    ])
    cust = _cust([inv], [pay], [arr])
    ledger = build_account_ledger(cust, as_of="2025-01-01")
    sold = next(e for e in ledger["entries"] if e["type"] == "recovery_note")
    assert sold["method"] == "debt_sale"
    assert sold["info_amount_gbp"] == 30.0
    assert ledger["total_recovered_gbp"] == 30.0
    assert ledger["current_balance_gbp"] == 0.0


def test_generate_end_to_end_patches_ledger_key(tmp_path):
    import tools.generate_payment_ledger_data as gpl

    cust_dir = tmp_path / "customers"
    cust_dir.mkdir()
    (cust_dir / "C1.json").write_text(json.dumps(dict(account_id="C1")))

    ledger_path = tmp_path / "billing_ledger.json"
    ledger_path.write_text(json.dumps(dict(customers=dict(C1=_cust([_INV_PAID], [_PAY_SUCCESS])))))

    count = gpl.generate(customers_dir=cust_dir, ledger_path=ledger_path)
    assert count == 1
    updated = json.loads((cust_dir / "C1.json").read_text())
    assert "ledger" in updated
    # as_of is the invoice's own issue_date; the payment (2020-02-14) is dated
    # after that, so per point-in-time honesty it is correctly withheld here --
    # the account is still "open" as of the book's only known reference date.
    assert updated["ledger"]["as_of_date"] == "2020-01-31"
    assert updated["ledger"]["current_balance_gbp"] == 100.0


def test_generate_skips_customers_with_no_existing_json_file(tmp_path):
    import tools.generate_payment_ledger_data as gpl

    cust_dir = tmp_path / "customers"
    cust_dir.mkdir()

    ledger_path = tmp_path / "billing_ledger.json"
    ledger_path.write_text(json.dumps(dict(customers=dict(C1=_cust([_INV_PAID], [_PAY_SUCCESS])))))

    count = gpl.generate(customers_dir=cust_dir, ledger_path=ledger_path)
    assert count == 0


def test_generate_returns_zero_when_ledger_missing(tmp_path):
    import tools.generate_payment_ledger_data as gpl

    count = gpl.generate(customers_dir=tmp_path, ledger_path=tmp_path / "no_such_ledger.json")
    assert count == 0


def test_a_credit_comes_off_the_next_paid_bill_and_the_account_settles_to_zero():
    """home_moves.md s.8.8a choice 11: the bill after a credit asks for its charges less the
    credit. Defect (2026-10-25): every later bill was paid in full beside the credit, so the
    account held the household's money until the move. Both fates: covered in part (a smaller
    payment) and covered whole (no payment received at all, not a GBP 0 one)."""
    credit = dict(invoice_number=1, issue_date="2020-01-31", total_amount_gbp=-130.0)
    part = dict(invoice_number=2, issue_date="2020-02-29", total_amount_gbp=100.0)
    whole = dict(invoice_number=3, issue_date="2020-03-31", total_amount_gbp=20.0)
    # 130 of credit: 100 covers bill 2 whole, the other 30 covers bill 3 whole.
    pays = [dict(invoice_number=2, payment_date="2020-03-14", amount_gbp=0.0,
                 method="direct_debit", outcome="success", credit_applied_gbp=100.0),
            dict(invoice_number=3, payment_date="2020-04-14", amount_gbp=0.0,
                 method="direct_debit", outcome="success", credit_applied_gbp=20.0)]
    ledger = build_account_ledger(_cust([credit, part, whole], pays), as_of="2025-01-01")
    assert [e["type"] for e in ledger["entries"]].count("payment_received") == 0
    assert ledger["current_balance_gbp"] == -10.0  # the 10 of credit nothing has used yet
    partial = [dict(invoice_number=2, payment_date="2020-03-14", amount_gbp=70.0,
                    method="direct_debit", outcome="success", credit_applied_gbp=30.0)]
    credit30 = dict(credit, total_amount_gbp=-30.0)
    ledger = build_account_ledger(_cust([credit30, part], partial), as_of="2025-01-01")
    assert ledger["total_collected_gbp"] == 70.0 and ledger["current_balance_gbp"] == 0.0
    lhs = ledger["total_collected_gbp"] + ledger["current_balance_gbp"]
    assert round(lhs, 2) == ledger["total_billed_gbp"]


def test_the_scheme_credit_lowers_the_balance_and_is_not_collected():
    """A bill the EBSS covered in part is paid for the rest, and one it covered whole is paid not
    at all; both settle to zero. Before the 2026-10-27 finding the first was collected in full and
    the second stood owed for ever.
    """
    invoices = [dict(invoice_number=1, issue_date="2022-12-05", total_amount_gbp=100.0),
                dict(invoice_number=2, issue_date="2023-01-05", total_amount_gbp=40.0)]
    payments = [dict(invoice_number=1, payment_date="2022-12-20", amount_gbp=34.0,
                     scheme_credit_gbp=66.0, method="direct_debit", outcome="success"),
                dict(invoice_number=2, payment_date="2023-01-20", amount_gbp=0.0,
                     scheme_credit_gbp=40.0, method="scheme_credit", outcome="credit")]
    ledger = build_account_ledger(_cust(invoices, payments), as_of="2025-01-01")
    assert ledger["current_balance_gbp"] == 0.0
    assert ledger["total_collected_gbp"] == 34.0
    assert ledger["total_scheme_credit_gbp"] == 106.0
    assert [e["type"] for e in ledger["entries"]] == [
        "invoice_raised", "scheme_credit", "payment_received", "invoice_raised", "scheme_credit"]


def test_the_months_whole_scheme_credit_is_posted_so_the_bills_it_later_settles_are_not_owed():
    """Cold read O27 (OCC-f6813bf9f05e): a GBP 67 month on a GBP 34.69 bill. The payment's share is
    capped at the bill and the engine carries the rest as the account's credit, which settles a later
    bill (`credit_applied_gbp`). Posting only the share left that later bill owed for ever; the
    account sat at GBP 92.19 for two years with nothing chasing it. Both partitions: a month whose
    credit the bill used whole, and one whose excess a later bill drew down."""
    invoices = [dict(invoice_number=1, issue_date="2023-02-02", total_amount_gbp=34.69,
                     scheme_credit_month_gbp=67.0),
                dict(invoice_number=2, issue_date="2023-03-03", total_amount_gbp=50.0,
                     scheme_credit_month_gbp=50.0),
                dict(invoice_number=3, issue_date="2023-05-01", total_amount_gbp=40.0)]
    payments = [dict(invoice_number=1, payment_date="2023-02-16", amount_gbp=0.0,
                     scheme_credit_gbp=34.69, method="scheme_credit", outcome="credit"),
                dict(invoice_number=2, payment_date="2023-03-17", amount_gbp=0.0,
                     scheme_credit_gbp=50.0, method="scheme_credit", outcome="credit"),
                dict(invoice_number=3, payment_date="2023-05-15", amount_gbp=7.69,
                     method="direct_debit", outcome="success", credit_applied_gbp=32.31)]
    ledger = build_account_ledger(_cust(invoices, payments), as_of="2025-01-01")
    assert ledger["current_balance_gbp"] == 0.0
    assert ledger["total_scheme_credit_gbp"] == 117.0
    assert ledger["total_collected_gbp"] == 7.69
    entries = ledger["entries"]
    # The excess shows as credit on the statement until the later bill uses it.
    assert entries[1]["type"] == "scheme_credit" and entries[1]["running_balance_gbp"] == -32.31
