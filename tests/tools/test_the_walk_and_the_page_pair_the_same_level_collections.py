"""The world's closing walk and the page pair the same level direct-debit collections.

Defect this file exists to catch: the walk (`arrears_engine.level_collection_pairs`) and the page
(`tools.generate_billing_ledger`) each decide, by a predicate of their own, which months' level
collections count as money in. The walk's closing balance sizes the refund, and the page prints the
balance. So when the walk counts a collection the page does not post, the run refunds cash the
page never shows arriving, and the household is pushed into page debit: six legs, GBP 833.30 on
068b5e3cc8 (SYN-2016-369 refunded 6 x 44.83, its Oct 2022-Mar 2023 collections in months the EBSS
credit met whole). That was class L' fixed on the page alone (7cf859beff); its control pins that
one branch. This one pins the property over every branch, so a third predicate cannot reopen it.

One leg runs through every pairing the walk makes, each with a paid and a returned collection:
a DD bill, a read catch-up credit bill, and a bill the EBSS credit met whole.
"""
import json

import pytest

import simulation.arrears_engine as ae
import tools.generate_billing_ledger as gbl
from tests.tools.test_generate_billing_ledger_pw import _resi_bill, _run

CID = "LEG"
# (period_end, printed total, resolved row, collection result): the walk's three kinds x two results.
MONTHS = [
    ("2022-09-28", 80.0, {"method": "direct_debit", "outcome": "success", "amount_gbp": 80.0}, None),
    ("2022-11-28", 30.0, {"method": None, "outcome": "credit", "amount_gbp": -36.0}, "success"),
    ("2022-12-28", 30.0, {"method": None, "outcome": "credit", "amount_gbp": -36.0}, "failed"),
    ("2023-05-28", -20.0, {"method": None, "outcome": "credit", "amount_gbp": -20.0}, "success"),
    ("2023-06-28", -20.0, {"method": None, "outcome": "credit", "amount_gbp": -20.0}, "failed"),
    ("2023-07-28", 90.0, {"method": "direct_debit", "outcome": "failed", "amount_gbp": 90.0}, None),
]


def _bill(period_end, total):
    """A charge bill, or a read catch-up credit: a 30.00 month less a 50.00 overcharge refunded."""
    if total >= 0:
        return _resi_bill(CID, period_end, total)
    bill = _resi_bill(CID, period_end, 30.0)
    bill.update(catchup_applied=True, catchup_adjustment_gbp=round(total - 30.0, 2),
                catchup_direction="overcharge", catchup_period_start=period_end[:8] + "01",
                catchup_period_end=period_end, catchup_written_off_gbp=0.0,
                catchup_back_billing_cap_applied=False, total_amount_gbp=total)
    return bill


@pytest.fixture
def both(tmp_path, monkeypatch):
    resolved = {}
    for pe, _amt, row, told in MONTHS:
        r = {"customer_id": CID, "period_end": pe, "commodity": "electricity", "days_late": 0,
             "due_date": pe, **row}
        if told is not None:
            r["collection_result"] = told
        resolved[(CID, pe, "electricity")] = r
    monkeypatch.setattr(gbl, "_resolved_settlement", lambda *a, **k: (resolved, {}, {}))
    run = _run([_bill(pe, amt) for pe, amt, _r, _t in MONTHS])
    collections = {CID: [{"month": pe[:7], "collection_date": pe[:8] + "12", "amount_gbp": 50.0 + n}
                         for n, (pe, *_rest) in enumerate(MONTHS)]}
    run["level_dd_collections"] = collections
    (tmp_path / "run.json").write_text(json.dumps(run))
    page = gbl.generate(tmp_path / "run.json", tmp_path / "ledger.json")["customers"][CID]
    pairs = list(ae.level_collection_pairs(list(resolved.values()), collections))
    return page, pairs


def test_every_kind_of_pairing_is_taken_paid_and_returned(both):
    _page, pairs = both
    kinds = {(r["outcome"] if r.get("method") else ("ebss" if face == 0.0 and r["amount_gbp"] == -36.0
                                                     else "credit_bill"), result)
             for r, _c, result, face in pairs}
    assert {("ebss", "success"), ("ebss", "failed"), ("credit_bill", "success"),
            ("credit_bill", "failed"), ("success", "success"), ("failed", "failed")} <= kinds, kinds


def test_the_page_posts_exactly_the_collections_the_walk_counts_as_paid(both):
    page, pairs = both
    walk_paid = sorted((c["collection_date"], round(c["amount_gbp"], 2))
                       for _r, c, result, _f in pairs if result == "success")
    page_paid = sorted((p["payment_date"], p["amount_gbp"]) for p in page["payments"]
                       if p.get("level_dd") and p["outcome"] == "success")
    assert page_paid == walk_paid
