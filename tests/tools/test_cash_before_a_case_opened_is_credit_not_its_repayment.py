"""Cash that crossed before an arrears case opened is credit already on the account, not that case's repayment.

The engine's walk can meet a returned bill with older credit and hold the household's cash for the NEXT failed
bill. The case branch of `generate_billing_ledger` then booked that cash as the later case's ARREARS_REPAID,
which `with_credits_applied` clamped forward to the case's opening: SYN-2016-380's GBP 102 of 1 Apr 2019 posted
on 19 Sep under a later bill, so the page held the cure the desk made on 1 Apr (55 such stages on the 6fe7827ab2
book, LEVEL_DD map s.9 fix 2). It now posts once on its cash day, under the bill of its settles_month, and the
case notes it as CREDIT_APPLIED.

One case carries both kinds of cash, so the test fails if the branch refuses everything as well as if it
refuses nothing: the later cash must still be the case's own repayment, and must not ALSO reach the catch-up.
"""
import json
from datetime import date

import pytest

import tools.generate_billing_ledger as gbl
from tests.tools.test_generate_billing_ledger_pw import _resi_bill, _run

JAN, FEB = "2019-01-28", "2019-02-28"
EARLY, LATE = "2019-01-20", "2019-04-05"   # FEB's case opens at its due date, between the two


def _row(outcome, amount):
    return {"method": "direct_debit", "outcome": outcome, "days_late": 0, "amount_gbp": amount}


@pytest.fixture
def leg(tmp_path, monkeypatch):
    bills = [_resi_bill("L1", pe, amt) for pe, amt in ((JAN, 100.0), (FEB, 120.0))]
    resolved = {("L1", JAN, "electricity"): _row("success", 100.0),
                ("L1", FEB, "electricity"): _row("failed", 120.0)}
    netted_on = date(2019, 4, 5)
    credits = {("L1", FEB, "electricity"): [
        {"amount_gbp": 20.0, "kind": "repayment", "date": netted_on, "credit_period_end": EARLY},
        {"amount_gbp": 30.0, "kind": "repayment", "date": netted_on, "credit_period_end": LATE}]}
    truth = [{"customer_id": "L1", "period_end": EARLY, "amount_gbp": 20.0, "settles_month": "2019-01"},
             {"customer_id": "L1", "period_end": LATE, "amount_gbp": 30.0, "settles_month": "2019-02"}]

    def settle(*a, repayments_out=None, **k):
        repayments_out.extend(truth)
        return resolved, {}, credits

    monkeypatch.setattr(gbl, "_resolved_settlement", settle)
    (tmp_path / "run.json").write_text(json.dumps(_run(bills)))
    return gbl.generate(tmp_path / "run.json", tmp_path / "ledger.json")["customers"]["L1"]


def _pay(leg, period_end):
    inv = next(i for i in leg["invoices"] if i["period_end"] == period_end)
    (pay,) = [p for p in leg["payments"] if p["invoice_number"] == inv["invoice_number"]]
    return pay


def test_cash_before_the_case_is_posted_on_its_day_and_noted_as_credit_on_the_case(leg):
    (case,) = leg["arrears_history"]
    opened = case["stages"][0]["date"]
    assert EARLY < opened <= LATE, (opened, "the fixture no longer straddles the opening")
    repaid = [(s["date"], s["amount_gbp"]) for s in case["stages"] if s["stage"] == "ARREARS_REPAID"]
    noted = [(s["date"], s["amount_gbp"]) for s in case["stages"] if s["stage"] == "CREDIT_APPLIED"]
    # The case's own money in is the cash that came after it opened, and the catch-up does not post it twice.
    assert repaid == [(LATE, 30.0)] and case["repaid_gbp"] == 30.0, case
    assert not _pay(leg, FEB).get("repayments"), _pay(leg, FEB)
    # The earlier cash is credit met at the opening, and money in on its own day under the bill it settled.
    assert noted == [(opened, 20.0)], case["stages"]
    assert _pay(leg, JAN).get("repayments") == [{"date": EARLY, "amount_gbp": 20.0}]
