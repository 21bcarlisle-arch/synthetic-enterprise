"""A level-return case prints what is still owed on it, and an account's one shortfall prints once.

The page opens a returned level collection's case at the desk's figure for the account on the day
the return counts as missed. Before this fix it printed that figure as owed for ever:
- it ignored the repayment the case itself records. SYN-2016-487's case read ARREARS_REPAID 25.70
  over a 3.07 shortfall and still printed 3.07 owed;
- the figure is the ACCOUNT's, so a two-fuel account's gas return, missed inside the journey the
  electricity return opened, printed the same 3.07 a second time.
On book-4dee9854a4 that was 182 cases, GBP 16,826.18, on 100 accounts
(WORKER_FINDING_A_LEVEL_DD_JOURNEY_CURES_..._2026-11-09.md, "shape A").

The partition: a return with no repayment still owes the desk's whole figure, and a second leg
whose journey figure RISES carries the rise. So the fix cannot pass by zeroing every level case.
"""
import json
from datetime import date

import pytest

import tools.generate_billing_ledger as gbl
from tests.tools.test_generate_billing_ledger_pw import _resi_bill, _run

JAN, FEB = "2019-01-28", "2019-02-28"
LEVEL = ("REPAID", "SHORT", "DUAL", "DUALg", "RISE", "RISEg")


def _row(outcome, amount):
    return {"method": "direct_debit", "outcome": outcome, "days_late": 0, "amount_gbp": amount}


def _gas(bill):
    return {**bill, "commodity": "gas"}


def _journey(acct, *stages):
    return {"account_id": "ACC-" + gbl.billing_account_of(acct),
            "stages": [{"stage": s, "on": on, "overdue_gbp": gbp, "days_overdue": 1}
                       for s, on, gbp in stages]}


@pytest.fixture
def ledger(tmp_path, monkeypatch):
    bills, resolved = [], {}
    for cid in LEVEL:
        for pe, amt, outcome in ((JAN, 100.0, "success"), (FEB, 120.0, "failed")):
            b = _resi_bill(cid, pe, amt)
            bills.append(_gas(b) if cid.endswith("g") else b)
            resolved[(cid, pe, "gas" if cid.endswith("g") else "electricity")] = _row(outcome, amt)
    # REPAID's February case is met by the household's own later payment of the bill.
    credits = {("REPAID", FEB, "electricity"): [
        {"amount_gbp": 120.0, "kind": "repayment", "date": date(2019, 3, 20),
         "credit_period_end": "2019-03-20"}]}
    monkeypatch.setattr(gbl, "_resolved_settlement", lambda *a, **k: (resolved, {}, credits))
    run = _run(bills)
    run["level_dd_collections"] = {
        cid: [{"month": "2019-01", "collection_date": "2019-01-10", "amount_gbp": 110.0},
              {"month": "2019-02", "collection_date": "2019-02-%d" % (25 if cid.endswith("g") else 10),
               "amount_gbp": 110.0}]
        for cid in LEVEL}
    run["collections_journeys"] = [
        _journey("REPAID", ("missed_payment", "2019-02-11", 40.0)),
        _journey("SHORT", ("missed_payment", "2019-02-11", 40.0)),
        # The gas return is missed inside the journey the electricity return opened: same figure.
        _journey("DUAL", ("missed_payment", "2019-02-11", 40.0), ("reminder", "2019-02-26", 40.0)),
        # Here the gas return adds to the account's shortfall: 40 rises to 65.
        _journey("RISE", ("missed_payment", "2019-02-11", 40.0), ("reminder", "2019-02-26", 65.0)),
    ]
    (tmp_path / "run.json").write_text(json.dumps(run))
    return gbl.generate(tmp_path / "run.json", tmp_path / "ledger.json")["customers"]


def _feb(ledger, cid):
    inv = next(i for i in ledger[cid]["invoices"] if i["period_end"] == FEB)
    cases = [c for c in ledger[cid].get("arrears_history") or []
             if c["invoice_number"] == inv["invoice_number"]]
    return inv, cases


def test_every_branch_is_reachable(ledger):
    """The partition: a level case still owed, one repaid, and one never opened all occur."""
    owed = [cid for cid in LEVEL if _feb(ledger, cid)[0]["outstanding_gbp"] > 0]
    met = [cid for cid in LEVEL if _feb(ledger, cid)[1] and _feb(ledger, cid)[0]["outstanding_gbp"] == 0]
    none = [cid for cid in LEVEL if not _feb(ledger, cid)[1]]
    assert owed and met and none, (owed, met, none)


def test_a_case_its_own_repayment_met_prints_nothing_owed(ledger):
    inv, (case,) = _feb(ledger, "REPAID")
    assert inv["outstanding_gbp"] == 0.0, inv
    assert case["repaid_gbp"] == 120.0 and case["credit_applied_gbp"] == 0.0, case
    assert inv["payment_status"] == "paid_late", inv


def test_a_case_nothing_met_owes_the_desk_figure(ledger):
    inv, (case,) = _feb(ledger, "SHORT")
    assert (inv["outstanding_gbp"], case["arrears_gbp"]) == (40.0, 40.0)


def test_an_accounts_one_shortfall_prints_on_one_leg(ledger):
    assert _feb(ledger, "DUAL")[0]["outstanding_gbp"] == 40.0
    assert _feb(ledger, "DUALg") == (_feb(ledger, "DUALg")[0], [])
    assert _feb(ledger, "DUALg")[0]["outstanding_gbp"] == 0.0


def test_a_second_leg_carries_what_the_journey_rose_by(ledger):
    assert _feb(ledger, "RISE")[0]["outstanding_gbp"] == 40.0
    assert _feb(ledger, "RISEg")[0]["outstanding_gbp"] == 25.0
