"""INV_PAYMENT_RECORD_RECONCILES_TO_COLLECTIONS_DUE is graded on the publisher's own path.

The defect this names: `load_printed`, the loader `_domain_invariant_gate_permits_publish` reads the
published customer files through, never built `payment_record`, so the row read NOT_IN_EXPORT on
every real book. The level-DD half of the dunning defect (45 breaches on fa915ac0d7) was visible
only to a scratch grader that built the record in memory; the gate Monday's publish reads passed it
unseen. The control is keyed to reachability (the row is evaluated, on a page file, through the
loader the publisher calls), not to how many breach. The page file is written by the export, so
the test is red if either half is missing: the export carrying it, or the loader reading it.
"""
from __future__ import annotations

import inspect
import json

from background import process_run_complete as prc
from tools import domain_invariant_runner as runner
from tools import generate_payment_ledger_data as gpl

ROW = "INV_PAYMENT_RECORD_RECONCILES_TO_COLLECTIONS_DUE"


def _grade(tmp_path, paid_on):
    """Bill 1 due 2020-02-15, paid by direct debit on `paid_on`; the book runs to 2020-06-30. The
    page file is written by the export itself (`generate_payment_ledger_data`), then read by the
    publisher's loader."""
    customers = tmp_path / "customers"
    customers.mkdir(exist_ok=True)
    bill = {"invoice_number": 1, "document_type": "bill", "date": "2020-02-01", "period_start": "2020-01-01",
            "period_end": "2020-01-31", "due_date": "2020-02-15", "amount_gbp": 60.0, "commodity": "electricity"}
    (customers / "P.json").write_text(json.dumps({"base_account_id": "P", "commodity": "electricity",
                                                  "invoices": [bill]}))
    ledger = tmp_path / "billing_ledger.json"
    ledger.write_text(json.dumps({"customers": {
        "P": {"invoices": [{"invoice_number": 1, "issue_date": "2020-02-01", "due_date": "2020-02-15",
                            "total_amount_gbp": 60.0}],
              "payments": [{"invoice_number": 1, "payment_date": paid_on, "amount_gbp": 60.0,
                            "method": "direct_debit", "outcome": "success"}], "arrears_history": []},
        "Q": {"invoices": [{"invoice_number": 1, "issue_date": "2020-06-30", "total_amount_gbp": 1.0}],
              "payments": [], "arrears_history": []}}}))
    assert gpl.generate(customers_dir=customers, ledger_path=ledger) == 1
    raw = tmp_path / "raw.json"
    raw.write_text(json.dumps({"P": {"customer_id": "P", "segment": "resi", "payments": [], "periods": [
        {"period_start": "2020-01-01", "period_end": "2020-01-31", "commodity": "electricity"}]}}))
    book = runner.load_book(raw_path=raw, printed_path=customers)
    return runner.run([i for i in runner.load_invariants() if i["id"] == ROW], book)[0]


def test_the_row_is_evaluated_from_the_published_page_file(tmp_path):
    paid = _grade(tmp_path, "2020-02-10")
    assert paid["status"] not in ("NOT_IN_EXPORT", "UNREACHED", "NO_EVALUATOR"), paid
    assert paid["checked"] > 0, paid


def test_a_dd_missed_without_a_return_breaches_through_the_same_path(tmp_path):
    """The other side of the partition: the exported record can carry a breach, not only a pass.
    A variable-DD bill paid weeks late with no return is missed, and a missed DD with no return
    breaches the row's third leg."""
    late = _grade(tmp_path, "2020-04-01")
    assert late["status"] == "BREACHED", late


def test_the_publisher_reads_the_published_page_files():
    """The loader above is the publisher's: its gate hands `load_book` the customer files."""
    src = inspect.getsource(prc._domain_invariant_gate_permits_publish)
    assert "printed_path=" in src and '"customers"' in src
