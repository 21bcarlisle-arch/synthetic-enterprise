"""The page posts each household repayment once, at the cash the world's payment truth says crossed.

The page posted a repayment only through a case's ARREARS_REPAID stage or a level return's
`repayments`, at the walk's share. Cash the walk put on a PAID bill (an excess drawn from the
account) and a level settlement's cash above the bill's face reached no line: on book 78f82e4242 the
page showed GBP 88,764.23 of GBP 94,133.49 received, short on 157 legs (SYN-2016-256g: 576.40 of
820.40). Two settlements on one day were one key, and the second was lost (SYN-2016-244).

The partition: a leg whose case already posts the whole cash gets no second line, so the fix cannot
pass by posting the truth on top of what the page already shows.
"""
import json
from datetime import date

import pytest

import tools.generate_billing_ledger as gbl
from tests.tools.test_generate_billing_ledger_pw import _resi_bill, _run

JAN, FEB = "2019-01-28", "2019-02-28"
LEGS = ("EXTRA", "CASED", "SAMEDAY")


def _row(outcome, amount):
    return {"method": "direct_debit", "outcome": outcome, "days_late": 0, "amount_gbp": amount}


def _truth(cid, on, cash, month):
    return {"customer_id": cid, "period_end": on, "commodity": "electricity", "amount_gbp": cash,
            "due_date": date.fromisoformat(on), "outcome": "repayment", "settles_month": month}


TRUTH = [_truth("EXTRA", "2019-03-05", 15.0, "2019-01"),
         _truth("CASED", "2019-03-20", 120.0, "2019-02"),
         _truth("SAMEDAY", "2019-03-07", 10.0, "2019-02"),
         _truth("SAMEDAY", "2019-03-07", 5.0, "2019-02")]


@pytest.fixture
def ledger(tmp_path, monkeypatch):
    bills, resolved = [], {}
    for cid in LEGS:
        feb = "failed" if cid == "CASED" else "success"
        for pe, amt, outcome in ((JAN, 100.0, "success"), (FEB, 120.0, feb)):
            bills.append(_resi_bill(cid, pe, amt))
            resolved[(cid, pe, "electricity")] = _row(outcome, amt)
    credits = {
        # The walk drew EXTRA's excess onto a PAID bill: no stage, no return, no line before.
        ("EXTRA", FEB, "electricity"): [{"amount_gbp": 15.0, "kind": "repayment",
                                         "date": date(2019, 3, 14), "credit_period_end": "2019-03-05"}],
        # CASED's case records the whole settlement as ARREARS_REPAID.
        ("CASED", FEB, "electricity"): [{"amount_gbp": 120.0, "kind": "repayment",
                                         "date": date(2019, 3, 20), "credit_period_end": "2019-03-20"}],
    }

    def settle(*_a, repayments_out=None, **_k):
        if repayments_out is not None:
            repayments_out.extend(TRUTH)
        return resolved, {}, credits

    monkeypatch.setattr(gbl, "_resolved_settlement", settle)
    (tmp_path / "run.json").write_text(json.dumps(_run(bills)))
    return gbl.generate(tmp_path / "run.json", tmp_path / "ledger.json")["customers"]


def _posted(leg):
    staged = sum(s.get("amount_gbp") or 0.0 for a in leg.get("arrears_history") or []
                 for s in a["stages"] if s["stage"] == "ARREARS_REPAID")
    lines = [r for p in leg["payments"] for r in p.get("repayments") or []]
    return round(staged, 2), lines


def test_the_cash_on_a_paid_bill_reaches_the_page(ledger):
    staged, lines = _posted(ledger["EXTRA"])
    assert staged == 0.0 and lines == [{"date": "2019-03-05", "amount_gbp": 15.0}]


def test_a_case_that_posts_the_whole_cash_gets_no_second_line(ledger):
    staged, lines = _posted(ledger["CASED"])
    assert staged == 120.0 and lines == []


def test_two_settlements_on_one_day_both_reach_the_page(ledger):
    _staged, lines = _posted(ledger["SAMEDAY"])
    assert sum(r["amount_gbp"] for r in lines) == 15.0


def test_every_leg_matches_the_truth(ledger):
    for cid in LEGS:
        staged, lines = _posted(ledger[cid])
        cash = sum(t["amount_gbp"] for t in TRUTH if t["customer_id"] == cid)
        assert round(staged + sum(r["amount_gbp"] for r in lines), 2) == cash, cid
