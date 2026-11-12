"""Cash that crossed before a level collection was returned is not posted as that return's repayment.

The engine's walk can net older cash against a later return. The no-case branch of `generate_billing_ledger`
then printed it under the returned bill, dated before the return happened: OCC-6387bf64272ag's 2017 cash under
a 2019 bill, 58 rows on the 6fe7827ab2 book (SEAT_FINDING_A_LEVEL_RETURNS_REPAYMENT_NAMES_A_BILL_NOT_YET_ISSUED).
That cash goes to the catch-up instead, on its own day, under the bill of its settles_month.

One leg carries both kinds of cash, so the test fails if the branch refuses everything as well as if it
refuses nothing: the later cash must still post on the return. Its settles_month names JANUARY on purpose:
were it February, a branch that refused everything would hand it to the catch-up, which files it under the
same February bill, and the refuse-all mutation would survive as an equivalence.
"""
import json
from datetime import date

import pytest

import tools.generate_billing_ledger as gbl
from tests.tools.test_generate_billing_ledger_pw import _resi_bill, _run

JAN, FEB = "2019-01-28", "2019-02-28"
EARLY, LATE = "2019-01-20", "2019-03-05"   # FEB's level collection is returned on 2019-02-10


def _row(outcome, amount):
    return {"method": "direct_debit", "outcome": outcome, "days_late": 0, "amount_gbp": amount}


@pytest.fixture
def leg(tmp_path, monkeypatch):
    bills = [_resi_bill("L1", pe, amt) for pe, amt in ((JAN, 100.0), (FEB, 120.0))]
    resolved = {("L1", JAN, "electricity"): _row("success", 100.0),
                ("L1", FEB, "electricity"): _row("failed", 120.0)}
    netted_on = date(2019, 3, 14)
    credits = {("L1", FEB, "electricity"): [
        {"amount_gbp": 20.0, "kind": "repayment", "date": netted_on, "credit_period_end": EARLY},
        {"amount_gbp": 30.0, "kind": "repayment", "date": netted_on, "credit_period_end": LATE}]}
    truth = [{"customer_id": "L1", "period_end": EARLY, "amount_gbp": 20.0, "settles_month": "2019-01"},
             {"customer_id": "L1", "period_end": LATE, "amount_gbp": 30.0, "settles_month": "2019-01"}]

    def settle(*a, repayments_out=None, **k):
        repayments_out.extend(truth)
        return resolved, {}, credits

    monkeypatch.setattr(gbl, "_resolved_settlement", settle)
    run = _run(bills)
    run["level_dd_collections"] = {"L1": [
        {"month": "2019-01", "collection_date": "2019-01-10", "amount_gbp": 110.0},
        {"month": "2019-02", "collection_date": "2019-02-10", "amount_gbp": 110.0}]}
    (tmp_path / "run.json").write_text(json.dumps(run))
    return gbl.generate(tmp_path / "run.json", tmp_path / "ledger.json")["customers"]["L1"]


def _pay(leg, period_end):
    inv = next(i for i in leg["invoices"] if i["period_end"] == period_end)
    (pay,) = [p for p in leg["payments"] if p["invoice_number"] == inv["invoice_number"]]
    return pay


def test_cash_before_the_return_posts_under_the_month_it_settled(leg):
    assert not leg.get("arrears_history"), "the return opened a case: the no-case branch was not taken"
    returned = _pay(leg, FEB)
    assert returned["payment_date"] == "2019-02-10" and returned["outcome"] != "success", returned
    assert returned.get("repayments") == [{"date": LATE, "amount_gbp": 30.0}], returned.get("repayments")
    assert _pay(leg, JAN).get("repayments") == [{"date": EARLY, "amount_gbp": 20.0}]
