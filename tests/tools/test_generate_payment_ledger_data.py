"""Tests for tools/generate_payment_ledger_data.py -- BILLING_AND_PAYMENTS_LEDGER.md
(Phase RP): per-account chronological ledger (invoice/payment/notice/write-off/
recovery) with a running balance, patched onto site/data/customers/<cid>.json,
built from the same real billing_ledger.json invoices/payments/arrears_history
already used by generate_invoice_data.py / generate_billing_ledger.py."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.generate_payment_ledger_data import build_account_ledger, _book_as_of_date


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
