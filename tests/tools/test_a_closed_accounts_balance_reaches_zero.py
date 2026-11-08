"""INV_CLOSED_ACCOUNT_BALANCE_REACHES_ZERO: a closed fuel leg's one balance, graded on its page.

The defect this names (ninth cold read, O7 and O20, on the af31e73fa7 book): 421 legs with no bill
for a year still held a balance on the page, GBP 15,694 of credit and GBP 21,554 of debt, and no row
graded a closed account's balance. 420 of them are level-DD legs, and the close was never built for
one. The row reads the page's own final-bill dates (`load_printed`'s `final_bills`), so it is red if
the loader stops reading them (NOT_IN_EXPORT) as well as if the evaluator stops grading.

Every leg is asserted reachable on both sides: a refunded credit passes and an unrefunded one
breaches, a write-off within the balance passes and one above it breaches, and a standing debt is a
flag, never a breach (no rule dates its collection).
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

from tools import domain_invariant_runner as runner

ROW = "INV_CLOSED_ACCOUNT_BALANCE_REACHES_ZERO"
FILE = Path(runner.__file__).resolve().parent.parent / "docs/design/DOMAIN_INVARIANTS.yaml"


def _entry(on, kind, amount, balance):
    return {"date": on, "type": kind, "amount_gbp": amount, "running_balance_gbp": balance}


def _page(final_bill, entries, segment="resi"):
    return {"segment": segment, "commodity": "electricity", "base_account_id": "H",
            "timeline": [{"type": "final_bill", "date": final_bill}],
            "invoices": [{"date": final_bill, "amount_gbp": 50.0}],
            "ledger": {"as_of_date": "2025-07-04", "entries": entries}}


#: A level-DD leg closed on 27 Sep 2021: the last instalment (76) ran ahead of the final bill (65.34).
LEVEL_DD_CLOSE = [_entry("2021-09-20", "payment_received", -76.0, -139.23),
                  _entry("2021-10-04", "invoice_raised", 65.34, -73.89)]


def _grade(tmp_path, pages):
    d = tmp_path / "customers"
    d.mkdir()
    for cid, page in pages.items():
        (d / f"{cid}.json").write_text(json.dumps(page))
    printed = runner.load_printed(d)
    book = {cid: {"segment": pages[cid]["segment"], "printed": pr} for cid, pr in printed.items()}
    inv = next(i for i in yaml.safe_load(FILE.read_text())["invariants"] if i["id"] == ROW)
    row = runner.run([inv], book)[0]
    tally = runner.ev_closed_account_balance(inv, [runner.Account(c, r) for c, r in book.items()])
    return row, {b["where"].split()[0] for b in tally.breaches}, {f["where"].split()[0] for f in tally.flags}


def test_every_leg_of_the_row_can_pass_and_can_breach(tmp_path):
    pages = {
        "CREDIT_KEPT": _page("2021-09-27", LEVEL_DD_CLOSE),
        "CREDIT_REFUNDED": _page("2021-09-27", LEVEL_DD_CLOSE + [_entry("2021-10-11", "refund_debit", 73.89, 0.0)]),
        # The refund on the 11th working day after the posting on 4 Oct is late: 10 working days end 18 Oct.
        "CREDIT_REFUNDED_LATE": _page("2021-09-27", LEVEL_DD_CLOSE + [_entry("2021-10-19", "refund_debit", 73.89, 0.0)]),
        "BEFORE_REG_6D": _page("2019-03-29", [_entry("2019-04-01", "invoice_raised", 10.0, -20.0)]),
        "WRITE_OFF_WITHIN": _page("2020-06-30", [_entry("2020-07-01", "invoice_raised", 40.0, 40.0),
                                                 _entry("2021-07-01", "write_off", -40.0, 0.0)]),
        "WRITE_OFF_ABOVE": _page("2020-06-30", [_entry("2020-07-01", "invoice_raised", 20.0, 20.0),
                                                _entry("2021-07-01", "write_off", -50.0, -30.0)]),
        "DEBT_STANDING": _page("2020-06-30", [_entry("2020-07-01", "invoice_raised", 40.0, 40.0)]),
    }
    row, breached, flagged = _grade(tmp_path, pages)
    assert row["status"] == "BREACHED", row
    assert breached == {"CREDIT_KEPT", "CREDIT_REFUNDED_LATE", "WRITE_OFF_ABOVE"}
    # The pre-2019 credit is still the customer's money, but reg 6D's deadline did not bind it.
    assert "BEFORE_REG_6D" not in breached
    # A standing debt is evidence to explain: flagged, never breached.
    assert flagged == {"DEBT_STANDING"}


def test_an_instalment_taken_after_the_final_bill_restarts_the_refund_clock(tmp_path):
    """A debt at the final bill, turned into a credit by a level instalment collected after it, is owed
    back on the same terms. Graded at the deadline from the final bill alone it would read as a debt."""
    entries = [_entry("2020-10-06", "invoice_raised", 50.0, 11.73),
               _entry("2020-10-26", "payment_received", -93.04, -81.31)]
    _, breached, _ = _grade(tmp_path, {"SYN-2016-089": _page("2020-10-06", entries)})
    assert breached == {"SYN-2016-089"}


def test_the_row_is_not_graded_when_the_page_carries_no_final_bill(tmp_path):
    page = _page("2021-09-27", LEVEL_DD_CLOSE)
    page["timeline"] = []
    row, _, _ = _grade(tmp_path, {"OPEN": page})
    assert row["status"] == "NOT_IN_EXPORT", row
