"""A level instalment returned in a month whose bill is a credit prints as returned, and the case the
desk opened on it carries the household's repayment.

Defect this file exists to catch: the credit-bill branch of `generate_billing_ledger` printed a level
collection only when it was paid. Its premise was "returned, the bill owes nothing". But the
schedule is owed by the schedule, and the credit is often a catch-up issued weeks after the return.
SYN-2016-215 on 8a300fa561: owed 144.07 on 15 Jul 2020, July's 162.80 was returned, the desk opened
on 16 Jul and the household repaid 162.80 on 29 Jul. Invoice 33407 (-56.33) was issued on 3 Aug. The
page printed no July row and hung the 162.80 on June's successful collection, as if a paid
collection had been "repaid" (3 legs; SEAT_FINDING_A_LEVEL_RETURN_ON_A_CREDIT_BILL_MONTH_..._2026-11-16).

The partition comes first. A paid credit-month collection still prints as paid, and a return the desk
found nothing short on prints its row with no case. So the fix cannot pass by failing every
credit-month collection, or by opening a case on every return.
"""
import json

import pytest

import tools.generate_billing_ledger as gbl
from tests.tools.test_generate_billing_ledger_pw import _run
from tests.tools.test_the_walk_and_the_page_pair_the_same_level_collections import _bill

JUN, JUL = "2020-06-30", "2020-07-31"
LEGS = ("SHORT", "PAID", "IN-CREDIT")


@pytest.fixture
def ledger(tmp_path, monkeypatch):
    # July is a read catch-up credit, as SYN-2016-215's invoice 33407 was.
    bills = [dict(_bill(pe, amt), customer_id=cid) for cid in LEGS
             for pe, amt in ((JUN, 97.19), (JUL, -56.33))]
    resolved = {}
    for cid, told in zip(LEGS, ("failed", "success", "failed")):
        resolved[(cid, JUN, "electricity")] = {"method": "direct_debit", "outcome": "success",
                                               "days_late": 0, "amount_gbp": 97.19}
        resolved[(cid, JUL, "electricity")] = {"method": None, "outcome": "credit", "days_late": 0,
                                               "amount_gbp": -56.33, "collection_result": told}
    # The world's repayment: 162.80 on 29 Jul, naming July as the month it settles. An earlier
    # repayment settling another month must stay where the catch-up files it.
    truth = [{"customer_id": "SHORT", "period_end": "2020-07-29", "amount_gbp": 162.80,
              "settles_month": "2020-07", "outcome": "repayment"},
             {"customer_id": "SHORT", "period_end": "2020-07-20", "amount_gbp": 5.00,
              "settles_month": "2020-06", "outcome": "repayment"}]

    def settle(*_a, repayments_out, **_k):
        repayments_out.extend(truth)
        return resolved, {}, {}
    monkeypatch.setattr(gbl, "_resolved_settlement", settle)
    run = _run(bills)
    run["level_dd_collections"] = {
        cid: [{"month": "2020-06", "collection_date": "2020-06-15", "amount_gbp": 162.80},
              {"month": "2020-07", "collection_date": "2020-07-15", "amount_gbp": 162.80}]
        for cid in LEGS}
    # The desk found SHORT owed 144.07 the day after its July return; IN-CREDIT, nothing.
    run["collections_journeys"] = [{"account_id": "ACC-" + gbl.billing_account_of("SHORT"),
                                    "stages": [{"stage": "missed_payment", "on": "2020-07-16",
                                                "overdue_gbp": 144.07, "days_overdue": 1}]}]
    (tmp_path / "run.json").write_text(json.dumps(run))
    return gbl.generate(tmp_path / "run.json", tmp_path / "ledger.json")["customers"]


def _level(ledger, cid):
    return sorted((p["payment_date"], p["outcome"]) for p in ledger[cid]["payments"]
                  if p.get("level_dd"))


def test_a_credit_month_collection_prints_paid_or_returned_as_it_was(ledger):
    assert _level(ledger, "PAID") == [("2020-06-15", "success"), ("2020-07-15", "success")]
    assert _level(ledger, "SHORT") == [("2020-06-15", "success"), ("2020-07-15", "failed")]
    assert _level(ledger, "IN-CREDIT") == [("2020-06-15", "success"), ("2020-07-15", "failed")]


def test_the_desks_case_opens_on_the_return_and_carries_its_own_repayment(ledger):
    (case,) = ledger["SHORT"]["arrears_history"]
    assert (case["opened_date"], case["arrears_gbp"], case["repaid_gbp"]) == \
        ("2020-07-16", 0.0, 162.80), case
    assert case["stages"][-1]["stage"] == "ARREARS_REPAID", case["stages"]


def test_no_repayment_hangs_on_a_successful_level_collection_that_did_not_settle_it(ledger):
    june = next(p for p in ledger["SHORT"]["payments"] if p["payment_date"] == "2020-06-15")
    assert june.get("repayments") == [{"date": "2020-07-20", "amount_gbp": 5.0}], june


def test_a_return_the_desk_found_nothing_short_on_opens_no_case(ledger):
    assert not ledger["IN-CREDIT"].get("arrears_history")
    assert not ledger["PAID"].get("arrears_history")
