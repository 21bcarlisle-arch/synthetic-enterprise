"""The billing ledger and the P&L write off the same money, per account, on the REAL run output.

Defect this names: at 6ba548633 the P&L (`compute_emergent_bad_debt`) wrote off £19,135 and the
customer ledger £17,359, because the engine resolved payment outcomes on bills the supplier's
pre-bill gate held (never issued, so never due) and on credit bills (nothing to collect). The
fixture tests agreed because no fixture bill is ever held or negative -- only the real book
carries both, so this control reads the real book. A credit also nets against the same
contract's arrears (SLC 27.16), and both sides must net it identically.

It also holds the customer surface honest: a case that is not written off is an open balance,
and nothing in the world clears it, so it may not render as resolved or as a payment plan.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import pytest

from company.billing.pre_bill_validation import validate_bills
from simulation.arrears_engine import BALANCE_OPEN, CREDIT_APPLIED, compute_emergent_bad_debt
from simulation.household import supply_points_that_left
from tools.generate_billing_ledger import generate

RUN = Path(__file__).resolve().parents[2] / "docs" / "reports" / "run_output_latest.json"


@pytest.fixture(scope="module")
def book(tmp_path_factory):
    if not RUN.exists():
        pytest.fail(f"the real run output is absent at {RUN} -- 'could not look' is not 'agrees'")
    data = json.loads(RUN.read_text())
    ledger = generate(RUN, tmp_path_factory.mktemp("ledger") / "billing_ledger.json")
    return data, ledger


def _ledger_write_off_by_account(ledger) -> dict[str, float]:
    out: dict[str, float] = defaultdict(float)
    for cid, cust in ledger["customers"].items():
        for case in cust["arrears_history"]:
            if any(s["stage"] == "WRITTEN_OFF" for s in case["stages"]):
                out[cid] += case["arrears_gbp"]
    return out


def test_the_real_book_carries_the_bills_that_made_the_two_disagree(book):
    """The control below is vacuous on a book with no held bill, no credit and no write-off."""
    data, ledger = book
    _passing, held = validate_bills(data["bills"])
    assert held, "no held bill in the real book -- the held-bill leg cannot be exercised"
    assert any(b["total_amount_gbp"] <= 0 for b in data["bills"]), "no credit bill in the real book"
    assert _ledger_write_off_by_account(ledger), "no write-off in the real book"
    # A credit netted against arrears (SLC 27.16) is the third thing the two must agree on.
    assert any(s["stage"] == CREDIT_APPLIED for cust in ledger["customers"].values()
               for case in cust["arrears_history"] for s in case["stages"]), \
        "no credit netted against arrears in the real book -- the netting leg is untested"


def test_the_ledger_and_the_pnl_write_off_agree_per_account(book):
    data, ledger = book
    pnl: dict[str, float] = defaultdict(float)
    for (cid, _year), gbp in compute_emergent_bad_debt(
            data["bills"], data.get("per_customer_behavioral", {}),
            supply_points_that_left(data.get("churned_billing_accounts", []),
                                    {b["customer_id"] for b in data["bills"]})).items():
        pnl[cid] += gbp
    led = _ledger_write_off_by_account(ledger)
    # A penny per case: the ledger prints each case rounded, the P&L rounds per (account, year).
    disagree = {cid: (round(led.get(cid, 0.0), 2), round(pnl.get(cid, 0.0), 2))
                for cid in set(led) | set(pnl)
                if abs(led.get(cid, 0.0) - pnl.get(cid, 0.0)) > 0.01 * max(1, len(
                    ledger["customers"].get(cid, {}).get("arrears_history", [])))}
    assert not disagree, f"ledger vs P&L write-off (GBP) disagree for {len(disagree)} account(s): " \
                         f"{dict(sorted(disagree.items())[:10])}"
    assert all(v > 0 for v in pnl.values()), "a negative write-off: a credit bill was booked as failed"


def test_no_open_balance_renders_as_resolved(book):
    _data, ledger = book
    finals = [case["stages"][-1] for cust in ledger["customers"].values()
              for case in cust["arrears_history"]]
    assert any(s["stage"] == BALANCE_OPEN for s in finals), "no open case -- the leg is untested"
    wrong = [s for s in finals
             if s["stage"] in ("RESOLVED", "PAYMENT_PLAN_AGREED") or "cleared" in s["note"].lower()]
    assert not wrong, f"{len(wrong)} open balance(s) render as resolved, e.g. {wrong[:2]}"


def test_an_invoice_is_outstanding_by_what_its_case_still_owes_not_by_its_face(book):
    """A failed bill that credit has netted in part, still open, read 'overdue' at its full face
    while its case and the household balance were net of the credit: one fact, two homes."""
    _data, ledger = book
    part_credited_open = 0
    wrong = []
    for cid, cust in ledger["customers"].items():
        case_by_inv = {a["invoice_number"]: a for a in cust["arrears_history"]}
        for inv in cust["invoices"]:
            case = case_by_inv.get(inv["invoice_number"])
            owed = 0.0
            if case is not None and inv["payment_status"] != "written_off":
                owed = case["arrears_gbp"]
            if inv.get("outstanding_gbp") != owed:
                wrong.append((cid, inv["invoice_number"], inv.get("outstanding_gbp"), owed))
            if inv["payment_status"] == "overdue" and 0 < owed < inv["total_amount_gbp"]:
                part_credited_open += 1
    assert part_credited_open, "no open part-credited bill in the real book -- the leg is untested"
    assert not wrong, f"{len(wrong)} invoice(s) outstanding at other than their case's balance: " \
                      f"{wrong[:5]}"
