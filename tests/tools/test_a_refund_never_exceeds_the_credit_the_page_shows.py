"""INV_REFUND_WITHIN_THE_PAGE_CREDIT: a refund never exceeds the credit the page shows on the day it is paid.

The defect this names (e6c1c11b4, on the 068b5e3cc8 book): six legs were refunded past the credit their
page printed, GBP 833.30 into debit, and no row compared a refund with the page's credit, so the gate
certified a book that refunds debtors. Written blind to the refund code: these pages are built by hand
from the rule (one balance, SLC 27.16) and the page feed's own shape.

The control runs over the whole partition: a refund to exactly nil passes, one past the credit breaches,
one to a leg in debt breaches, a same-day invoice printed before it counts against the credit, a payment
printed after it does not rescue it, and a refund line with no printed balance is a breach, never a pass.
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

from company.compliance.domain_invariants import (
    check_refund_within_the_page_credit,
    refunds_beyond_the_page_credit,
)
from tools import domain_invariant_runner as runner

ROW = "INV_REFUND_WITHIN_THE_PAGE_CREDIT"
FILE = Path(runner.__file__).resolve().parent.parent / "docs/design/DOMAIN_INVARIANTS.yaml"


def _e(on, kind, amount, balance):
    return {"date": on, "type": kind, "amount_gbp": amount, "running_balance_gbp": balance}


#: A leg holding GBP 294.70 of credit after its final bill of 8.95 on 7 Aug.
IN_CREDIT = [_e("2024-08-01", "invoice_raised", 45.50, -303.65), _e("2024-08-07", "invoice_raised", 8.95, -294.70)]

LEGS = {
    "TO_ZERO": IN_CREDIT + [_e("2024-08-20", "refund_debit", 294.70, 0.0)],
    "PART": IN_CREDIT + [_e("2024-08-20", "refund_debit", 200.00, -94.70)],
    # Sized from the credit before the final bill, then the final bill collected apart: one balance broken.
    "PAST_THE_CREDIT": IN_CREDIT + [_e("2024-08-20", "refund_debit", 303.65, 8.95),
                                    _e("2024-08-21", "payment_received", -8.95, 0.0)],
    "TO_A_DEBTOR": [_e("2023-06-01", "invoice_raised", 82.43, 82.43), _e("2023-06-12", "refund_debit", 42.53, 124.96)],
    # The final bill posted the same morning is part of the balance the refund pays back.
    "SAME_DAY_INVOICE": [_e("2022-07-05", "payment_received", -24.46, -24.46),
                         _e("2022-07-14", "invoice_raised", 26.13, 1.67), _e("2022-07-14", "refund_debit", 12.90, 14.57)],
    # Paid into debt, then collected back the same day: the page printed the debt the refund made.
    "COLLECTED_BACK_SAME_DAY": [_e("2021-01-01", "invoice_raised", 10.0, 10.0), _e("2021-01-15", "refund_debit", 30.0, 40.0),
                         _e("2021-01-15", "payment_received", -40.0, 0.0)],
    "UNPRINTED": IN_CREDIT + [_e("2024-08-20", "refund_debit", 1.0, None)],
    # A payment printed before the refund on the same day is credit in hand.
    "PAYMENT_FIRST": [_e("2021-02-01", "invoice_raised", 10.0, 10.0), _e("2021-02-15", "payment_received", -40.0, -30.0),
                      _e("2021-02-15", "refund_debit", 30.0, 0.0)],
}
EXPECTED_BREACHES = {"PAST_THE_CREDIT", "TO_A_DEBTOR", "SAME_DAY_INVOICE", "COLLECTED_BACK_SAME_DAY", "UNPRINTED"}


def test_the_library_predicate_takes_both_branches():
    verdict = {cid: check_refund_within_the_page_credit(es) for cid, es in LEGS.items()}
    assert any(verdict.values()) and not all(verdict.values())
    assert {cid for cid, ok in verdict.items() if not ok} == EXPECTED_BREACHES
    over = refunds_beyond_the_page_credit(LEGS["PAST_THE_CREDIT"])
    assert over == [{"date": "2024-08-20", "refunded_gbp": 303.65, "credit_gbp": 294.70, "excess_gbp": 8.95}]
    assert refunds_beyond_the_page_credit(LEGS["UNPRINTED"])[0]["excess_gbp"] is None


def test_the_gate_row_reads_the_page_and_fires_on_the_named_legs(tmp_path):
    d = tmp_path / "customers"
    d.mkdir()
    for cid, es in LEGS.items():
        (d / f"{cid}.json").write_text(json.dumps({"segment": "resi", "commodity": "electricity",
                                                   "ledger": {"as_of_date": "2025-07-04", "entries": es}}))
    printed = runner.load_printed(d)
    book = {cid: {"segment": "resi", "printed": pr} for cid, pr in printed.items()}
    inv = next(i for i in yaml.safe_load(FILE.read_text())["invariants"] if i["id"] == ROW)
    row = runner.run([inv], book)[0]
    assert row["status"] == "BREACHED", row
    assert row["checked"] == len(LEGS)
    tally = runner.ev_refund_within_page_credit(inv, [runner.Account(c, r) for c, r in book.items()])
    assert {b["where"].split()[0] for b in tally.breaches} == EXPECTED_BREACHES


def test_a_book_read_without_the_page_is_not_in_export_never_clean():
    inv = next(i for i in yaml.safe_load(FILE.read_text())["invariants"] if i["id"] == ROW)
    row = runner.run([inv], {"X": {"segment": "resi", "periods": []}})[0]
    assert row["status"] == "NOT_IN_EXPORT", row
