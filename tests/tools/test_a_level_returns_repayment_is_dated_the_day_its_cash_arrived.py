"""A level return that opens no case posts the household's repayment on the day the cash arrived.

The no-case branch of `generate_billing_ledger` dated the share `c["date"]`, the day the walk netted the
credit against a bill, while keying `repaid_posted` by `c["credit_period_end"]`, the cash's own day. On
the 6fe7827ab2 book that put 146 page rows on days no cash crossed on the leg, 110 of them on the very
bill the cash settled (docs/design/LEVEL_DD_AREA_MAP_2026-11-11.md s.9, line N).

The netting day is deliberately LATER than the cash day here, as it is on the book, and the first
assertion is that the branch wrote a row at all: a page that dropped the repayment would date nothing
wrongly and pass a date-only check.
"""
import json
from datetime import date

import pytest

import tools.generate_billing_ledger as gbl
from tests.tools.test_generate_billing_ledger_pw import _resi_bill, _run

JAN, FEB = "2019-01-28", "2019-02-28"
CASH_DAY, NETTED_ON = "2019-03-05", date(2019, 3, 14)


def _row(outcome, amount):
    return {"method": "direct_debit", "outcome": outcome, "days_late": 0, "amount_gbp": amount}


@pytest.fixture
def leg(tmp_path, monkeypatch):
    bills = [_resi_bill("L1", pe, amt) for pe, amt in ((JAN, 100.0), (FEB, 120.0))]
    resolved = {("L1", JAN, "electricity"): _row("success", 100.0),
                ("L1", FEB, "electricity"): _row("failed", 120.0)}
    credits = {("L1", FEB, "electricity"): [{"amount_gbp": 30.0, "kind": "repayment",
                                             "date": NETTED_ON, "credit_period_end": CASH_DAY}]}
    monkeypatch.setattr(gbl, "_resolved_settlement", lambda *a, **k: (resolved, {}, credits))
    run = _run(bills)
    # Level DD, in credit on the schedule, and no desk journey: the return opens no case.
    run["level_dd_collections"] = {"L1": [
        {"month": "2019-01", "collection_date": "2019-01-10", "amount_gbp": 110.0},
        {"month": "2019-02", "collection_date": "2019-02-10", "amount_gbp": 110.0}]}
    (tmp_path / "run.json").write_text(json.dumps(run))
    return gbl.generate(tmp_path / "run.json", tmp_path / "ledger.json")["customers"]["L1"]


def test_the_no_case_branch_posts_the_repayment_on_its_cash_day(leg):
    assert not leg.get("arrears_history"), "the return opened a case: the no-case branch was not taken"
    feb = next(i for i in leg["invoices"] if i["period_end"] == FEB)
    (pay,) = [p for p in leg["payments"] if p["invoice_number"] == feb["invoice_number"]]
    assert pay.get("repayments"), "the no-case branch posted no repayment"
    assert pay["repayments"] == [{"date": CASH_DAY, "amount_gbp": 30.0}], pay["repayments"]
