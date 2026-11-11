"""A level direct debit is collected in a month whose bill the EBSS credit met whole, and the page
posts it (payments_and_direct_debit_2026-10-25.md, "What a level direct debit must be").

Defect this file exists to catch (class L'): the page taking a level collection only while posting a
bill whose method is `direct_debit`. A bill the scheme credit met is a credit to the engine and
`scheme_credit` on the page, so the cash the household's bank paid that month had no row:
PROS-2019-0318's 62.48 of 28 Dec 2022 and of 24 Mar 2023, 99 rows (GBP 4,474.09) on 78f82e4242.
The world's walk (`arrears_engine.level_collection_difference`) already paired that month.

Both results over the partition: a page that dropped the month fails the paid leg, and one that
posted every presented collection whatever its result fails the returned leg. The January bill
after it checks the slot: popping nothing in December would hand January December's collection.
"""
import json

import pytest

import tools.generate_billing_ledger as gbl
from tests.tools.test_generate_billing_ledger_pw import _resi_bill, _run

DEC, JAN = "2022-12-28", "2023-01-28"


@pytest.fixture
def ledger(tmp_path, monkeypatch):
    legs = ("PAID", "RETURNED")
    bills = [_resi_bill(cid, pe, amt) for cid in legs for pe, amt in ((DEC, 30.0), (JAN, 140.0))]
    resolved = {}
    for cid, told in zip(legs, ("success", "failed")):
        # December's 30.00 bill, less the month's 66-67 EBSS credit, asks nothing: a credit row.
        resolved[(cid, DEC, "electricity")] = {"method": None, "outcome": "credit", "days_late": 0,
                                               "amount_gbp": -36.0, "collection_result": told}
        resolved[(cid, JAN, "electricity")] = {"method": "direct_debit", "outcome": "success",
                                               "days_late": 0, "amount_gbp": 73.0}
    monkeypatch.setattr(gbl, "_resolved_settlement", lambda *a, **k: (resolved, {}, {}))
    run = _run(bills)
    run["level_dd_collections"] = {
        cid: [{"month": "2022-12", "collection_date": "2022-12-12", "amount_gbp": 61.0},
              {"month": "2023-01", "collection_date": "2023-01-12", "amount_gbp": 62.0}]
        for cid in legs}
    (tmp_path / "run.json").write_text(json.dumps(run))
    return gbl.generate(tmp_path / "run.json", tmp_path / "ledger.json")["customers"]


def _level(ledger, cid):
    return sorted((p["payment_date"], p["amount_gbp"]) for p in ledger[cid]["payments"]
                  if p.get("level_dd"))


def test_a_paid_collection_in_a_scheme_credit_month_is_money_in_and_a_returned_one_is_not(ledger):
    assert _level(ledger, "PAID") == [("2022-12-12", 61.0), ("2023-01-12", 62.0)]
    assert _level(ledger, "RETURNED") == [("2023-01-12", 62.0)]


def test_the_scheme_credit_still_meets_the_bill(ledger):
    dec = next(i for i in ledger["PAID"]["invoices"] if i["period_end"] == DEC)
    assert dec.get("scheme_credit_gbp") == 30.0, dec
