"""PB8 L2: once the supplier stops a household's Direct Debit, the world's money side stops
paying that household's bills by DD.

The desk's stop used to reach only the DD rails register. The engine's resolved bills (the P&L,
write-offs, provision) and the billing ledger still read the fixed-for-life channel draw. So a
stopped household's later failures were filed as returned Direct Debits against a mandate that no
longer existed.
"""
import json

import simulation.arrears_engine as ae
import simulation.dd_collection_book as dcb
from simulation.household_segments import PaymentChannel, payment_channel_for_customer
from tests.tools.test_generate_billing_ledger_pw import _resi_bill, _run
from tools.generate_billing_ledger import generate

N_HOUSEHOLDS = 40


def _book():
    """A stressed year for 40 resi households on their own drawn channels."""
    bills, behavioral = [], {}
    for i in range(N_HOUSEHOLDS):
        cid = f"PB8L2-{i:02d}"
        behavioral[cid] = {"income_stress_trajectory": [{"year": 2022, "stress": "high"}]}
        bills += [_resi_bill(cid, "2022-%02d-28" % m, 150.0) for m in range(1, 13)]
    return bills, behavioral


def _is_dd(cid):
    return payment_channel_for_customer(cid, "electricity") is PaymentChannel.DIRECT_DEBIT


def test_some_dd_households_are_stopped_and_some_are_not():
    """Partition control first: a rule that stopped every DD household, or none, passes every
    other leg in this file and fails here."""
    bills, behavioral = _book()
    stops = dcb.supplier_dd_stops(bills, behavioral, 42)
    dd = {b["customer_id"] for b in bills if _is_dd(b["customer_id"])}
    assert stops and set(stops) < dd, (len(stops), len(dd))


def test_every_bill_after_the_stop_is_paid_on_receipt_and_none_before_it():
    bills, behavioral = _book()
    stops = dcb.supplier_dd_stops(bills, behavioral, 42)
    rows = ae._resolve_bills(bills, behavioral, 42)
    after = [r for r in rows if r["customer_id"] in stops
             and r["period_end"] > stops[r["customer_id"]]]
    assert after, "no stopped household had a bill after its stop"
    for r in rows:
        cid = r["customer_id"]
        if not _is_dd(cid):
            continue
        stopped = cid in stops and r["period_end"] > stops[cid]
        assert r["method"] == ("standard_credit" if stopped else "direct_debit"), r


def test_the_stop_moves_no_outcome(monkeypatch):
    """A resi outcome is drawn the same way for DD and standard credit, and fuel poverty stays on the
    household's drawn channel. So following the stop relabels the bill and changes no money. If this
    goes red, published bad debt moved, and that needs its own pre-registration."""
    bills, behavioral = _book()
    followed = ae._resolve_bills(bills, behavioral, 42)
    monkeypatch.setattr(dcb, "supplier_dd_stops", lambda *a, **k: {})
    ignored = ae._resolve_bills(bills, behavioral, 42)
    assert any(f["method"] != i["method"] for f, i in zip(followed, ignored))
    assert [(r["outcome"], r["days_late"]) for r in followed] == \
           [(r["outcome"], r["days_late"]) for r in ignored]


def test_fuel_poverty_is_read_on_the_households_own_channel(monkeypatch):
    """The household is no more fuel poor the day its mandate is cancelled. The standard-credit rate
    (0.185) is twice the DD rate (0.088), so reading it on the paying channel would move a stopped
    household into fuel poverty on the same uniform draw."""
    bills, behavioral = _book()
    seen = []
    real = ae._fuel_poor_for_bill
    monkeypatch.setattr(ae, "_fuel_poor_for_bill",
                        lambda method, cid: seen.append((cid, method)) or real(method, cid))
    stops = dcb.supplier_dd_stops(bills, behavioral, 42)
    ae._resolve_bills(bills, behavioral, 42)
    asked = {m for cid, m in seen if cid in stops}
    assert asked == {"direct_debit"}, asked


def test_the_ledger_opens_no_returned_dd_case_after_the_stop(tmp_path):
    """The billing ledger reads the same paying channel as the engine: its payments after the stop
    are standard credit, and no arrears case after the stop opens as a returned Direct Debit."""
    bills, behavioral = _book()
    stops = dcb.supplier_dd_stops(bills, behavioral, 42)
    rj = tmp_path / "run.json"
    rj.write_text(json.dumps(_run(bills, beh=behavioral)))
    ledger = generate(rj, tmp_path / "l.json")["customers"]
    checked = 0
    for cid, stop in stops.items():
        cust = ledger[cid]
        by_invoice = {inv["invoice_number"]: inv for inv in cust["invoices"]}
        for pay in cust["payments"]:
            pe = by_invoice[pay["invoice_number"]]["period_end"]
            assert pay["method"] == ("standard_credit" if pe > stop else "direct_debit"), (cid, pe)
            checked += pe > stop
        for case in cust["arrears_history"]:
            pe = by_invoice[case["invoice_number"]]["period_end"]
            if pe > stop:
                assert case["stages"][0]["stage"] != "DD_FAILED", (cid, pe)
    assert checked
