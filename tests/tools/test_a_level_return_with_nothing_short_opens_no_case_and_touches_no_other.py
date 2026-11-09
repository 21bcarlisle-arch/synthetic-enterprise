"""A returned level DD that leaves nothing short opens no arrears case, and touches no other case.

a3136e29fa (level DD step 2b) let the page skip the case when the desk had no shortfall on the
day a level return counts as missed (`outcome_case = None`). But the block that finishes a case
was still keyed on the engine's raw `outcome`, so it called `arr.update(...)` on whatever `arr`
the loop last held. On the first such bill in a book it raised UnboundLocalError: the
e50e7b8f68 book (8 Nov), the first carrying step 2b, could not build its billing ledger at all.
Later in a book, it rewrote the previous bill's case, possibly another household's, with this
bill's face and credits.

The third household is the partition control: a return the desk DID find short still opens its
case, at the desk's figure, so the fix cannot pass by never opening a level case.
"""
import json

import pytest

import tools.generate_billing_ledger as gbl
from tests.tools.test_generate_billing_ledger_pw import _resi_bill, _run

JAN, FEB = "2019-01-28", "2019-02-28"


def _row(outcome, amount):
    return {"method": "direct_debit", "outcome": outcome, "days_late": 0, "amount_gbp": amount}


@pytest.fixture
def ledger(tmp_path, monkeypatch):
    bills = [_resi_bill(cid, pe, amt) for cid in ("A0-PLAIN", "L1-CREDIT", "L2-SHORT")
             for pe, amt in ((JAN, 100.0), (FEB, 120.0))]
    resolved = {
        ("A0-PLAIN", JAN, "electricity"): _row("failed", 100.0),
        ("A0-PLAIN", FEB, "electricity"): _row("success", 120.0),
        ("L1-CREDIT", JAN, "electricity"): _row("success", 100.0),
        ("L1-CREDIT", FEB, "electricity"): _row("failed", 120.0),
        ("L2-SHORT", JAN, "electricity"): _row("success", 100.0),
        ("L2-SHORT", FEB, "electricity"): _row("failed", 120.0),
    }
    monkeypatch.setattr(gbl, "_resolved_settlement", lambda *a, **k: (resolved, {}, {}))
    run = _run(bills)
    run["level_dd_collections"] = {
        cid: [{"month": "2019-01", "collection_date": "2019-01-10", "amount_gbp": 110.0},
              {"month": "2019-02", "collection_date": "2019-02-10", "amount_gbp": 110.0}]
        for cid in ("L1-CREDIT", "L2-SHORT")}
    # The desk found L2 short by 40 on the day after its February return; L1 (in credit) not at all.
    run["collections_journeys"] = [{"account_id": "ACC-" + gbl.billing_account_of("L2-SHORT"),
                                    "stages": [{"stage": "missed_payment", "on": "2019-02-11",
                                                "overdue_gbp": 40.0, "days_overdue": 1}]}]
    (tmp_path / "run.json").write_text(json.dumps(run))
    return gbl.generate(tmp_path / "run.json", tmp_path / "ledger.json")["customers"]


def _cases(ledger, cid):
    return ledger[cid].get("arrears_history") or []


def test_a_level_return_in_credit_opens_no_case_and_owes_nothing(ledger):
    assert _cases(ledger, "L1-CREDIT") == []
    feb = next(i for i in ledger["L1-CREDIT"]["invoices"] if i["period_end"] == FEB)
    assert feb["outstanding_gbp"] == 0.0


def test_the_previous_households_case_keeps_its_own_bill(ledger):
    """On a3136e29fa, L1's February rewrote A0's January case with L1's 120 face."""
    (case,) = _cases(ledger, "A0-PLAIN")
    assert case["face_gbp"] == 100.0, case


def test_a_level_return_the_desk_found_short_opens_its_case_at_the_desk_figure(ledger):
    (case,) = _cases(ledger, "L2-SHORT")
    assert (case["arrears_gbp"], case["opened_date"]) == (40.0, "2019-02-11"), case
