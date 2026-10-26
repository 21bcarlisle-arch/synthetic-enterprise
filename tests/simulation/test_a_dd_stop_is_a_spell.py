"""PB8: a stop off Direct Debit is a spell, not the end. The desk invites an account back onto DD on its
own ledger of on-receipt bills, and once a household signs, the register, the money side and the seam
all see it back on DD from the same bill.

The take-up rate is None in the shipped world (no published figure), so nobody is invited and every
spell stays open. These tests supply a rate to show that setting one later moves all three readers
together, which is the precondition the 26 Oct finding named before any rate is set.
"""
import json

import pytest

import simulation.arrears_engine as ae
import simulation.bacs_rails as br
import simulation.dd_collection_book as dcb
import simulation.run_phase4c_on_phase2b as p4c
from simulation.household_segments import PaymentChannel, payment_channel_for_customer
from tests.tools.test_generate_billing_ledger_pw import _resi_bill, _run
from tools.generate_billing_ledger import generate

YEARS = (2022, 2023)


def _book():
    """40 resi households, stressed in 2022 and back to low stress in 2023: enough months after a
    stop for three on-time on-receipt bills in a row."""
    bills, behavioral = [], {}
    for i in range(40):
        cid = f"PB8L2-{i:02d}"
        behavioral[cid] = {"income_stress_trajectory": [
            {"year": y, "stress": "high" if y == 2022 else "low"} for y in YEARS]}
        bills += [_resi_bill(cid, "%d-%02d-28" % (y, m), 150.0) for y in YEARS for m in range(1, 13)]
    return bills, behavioral


def _is_dd(cid):
    return payment_channel_for_customer(cid, "electricity") is PaymentChannel.DIRECT_DEBIT


def _off(spells, cid, period_end):
    return any(off < period_end and (on is None or period_end <= on) for off, on in spells.get(cid, ()))


@pytest.fixture
def half(monkeypatch):
    monkeypatch.setattr(br, "REMANDATE_ACCEPTANCE_PROBABILITY", 0.5)


def test_with_no_rate_every_spell_stays_open():
    """The shipped world: nobody is invited, so a stop is still terminal and no number moves."""
    assert br.REMANDATE_ACCEPTANCE_PROBABILITY is None
    spells = dcb.supplier_dd_spells(*_book(), 42)
    assert spells and all(len(s) == 1 and s[0][1] is None for s in spells.values()), spells


def test_some_stopped_households_come_back_and_some_do_not(half):
    """Partition control: a rate that re-signed everyone, or no one, passes every other leg here."""
    spells = dcb.supplier_dd_spells(*_book(), 42)
    back = {c for c, s in spells.items() if s[-1][1] is not None}
    assert back and back < set(spells), spells
    for s in spells.values():
        for off, on in s:
            assert on is None or on > off


def test_the_register_has_the_household_back_on_dd(half):
    bills, behavioral = _book()
    spells = dcb.supplier_dd_spells(bills, behavioral, 42)
    notices = dcb.supplier_dd_spell_notices(bills, behavioral, 42)
    register = dcb.build_dd_collection_book(bills, behavioral, seed=42)
    collected_after = 0
    for cid, s in spells.items():
        mandate = register.get_mandate(cid)
        assert (mandate.status == "active") == (s[-1][1] is not None), (cid, mandate.status, s)
        if s[-1][1] is not None:
            assert mandate.setup_confirmed_date == notices[cid][-1][1]
            later = [a for a in register.attempts_for_customer(cid)
                     if a.mandate_reference == mandate.mandate_reference]
            # A re-mandate on the last bill has nothing after it to collect.
            assert bool(later) == (s[-1][1] < "2023-12-28"), (cid, s, len(later))
            collected_after += bool(later)
    assert collected_after


def test_the_money_side_pays_by_dd_again_from_the_bill_after_the_re_mandate(half):
    bills, behavioral = _book()
    spells = dcb.supplier_dd_spells(bills, behavioral, 42)
    rows = ae._resolve_bills(bills, behavioral, 42)
    seen_back = 0
    for r in rows:
        cid = r["customer_id"]
        if not _is_dd(cid):
            continue
        off = _off(spells, cid, r["period_end"])
        assert r["method"] == ("standard_credit" if off else "direct_debit"), r
        seen_back += any(on is not None and r["period_end"] > on for _o, on in spells.get(cid, ()))
    assert seen_back


def test_a_re_mandate_moves_no_outcome(half, monkeypatch):
    """A resi outcome is drawn the same way on either channel, so coming back onto DD relabels bills
    and changes no money. If this goes red, published bad debt moved: pre-register it."""
    bills, behavioral = _book()
    back = [(r["outcome"], r["days_late"], r["method"]) for r in ae._resolve_bills(bills, behavioral, 42)]
    monkeypatch.setattr(br, "REMANDATE_ACCEPTANCE_PROBABILITY", None)
    never = [(r["outcome"], r["days_late"], r["method"]) for r in ae._resolve_bills(bills, behavioral, 42)]
    assert any(b[2] != n[2] for b, n in zip(back, never))
    assert [b[:2] for b in back] == [n[:2] for n in never]


def test_the_ledger_pays_by_dd_again_after_the_re_mandate(half, tmp_path):
    bills, behavioral = _book()
    spells = dcb.supplier_dd_spells(bills, behavioral, 42)
    rj = tmp_path / "run.json"
    rj.write_text(json.dumps(_run(bills, beh=behavioral)))
    ledger = generate(rj, tmp_path / "l.json")["customers"]
    checked = 0
    for cid, s in spells.items():
        by_invoice = {inv["invoice_number"]: inv for inv in ledger[cid]["invoices"]}
        for pay in ledger[cid]["payments"]:
            pe = by_invoice[pay["invoice_number"]]["period_end"]
            assert pay["method"] == ("standard_credit" if _off(spells, cid, pe) else "direct_debit")
            checked += s[-1][1] is not None and pe > s[-1][1]
    assert checked


def test_the_seam_reports_on_dd_again_once_auddis_confirms(half, monkeypatch):
    """The board, asked month by month as the run asks it, follows the full run's spells: told of the
    stop from its notice, and back on DD from the day the new mandate was confirmed."""
    bills, behavioral = _book()
    full = dcb.supplier_dd_spell_notices(bills, behavioral, 42)
    monkeypatch.setattr(p4c, "build_monthly_bills", lambda records, churned: list(records))
    monkeypatch.setattr("company.interfaces.bill_assembly.issued_bills", lambda b: b)
    board = dcb.StopNoticeBoard(lambda cid: behavioral[cid]["income_stress_trajectory"])
    board.observe([{**b, "settlement_date": b["period_end"]} for b in bills])
    dates = ["%d-%02d-%02d" % (y, m, d) for y in (*YEARS, 2024) for m in range(1, 13) for d in (1, 15)]
    for cid in sorted(full):
        for d in dates:
            want = next((off for off, on in full[cid] if off <= d and (on is None or d < on)), None)
            assert board.notice_as_of(cid, d) == want, (cid, d, want)
    back = {c: s[-1] for c, s in full.items() if s[-1][1] is not None}
    assert back
    for cid, (off_from, on_from) in back.items():
        assert board.notice_as_of(cid, off_from) == off_from
        assert board.notice_as_of(cid, on_from) is None, (cid, on_from)


def test_a_household_that_cancelled_at_its_bank_and_signed_again_is_collected_again(monkeypatch):
    """DD4b's own cancellation persists on the household's record from its month on. Once it signs a
    new mandate that cancellation is spent: the rails present its bills again and the money side reads
    them as DD, or the register and the P&L split on exactly the household this rate is about."""
    from simulation.dd_shock_response import RECORD_KEY
    monkeypatch.setattr(br, "REMANDATE_ACCEPTANCE_PROBABILITY", 1.0)
    monkeypatch.setattr(dcb, "payment_method", lambda *a, **k: "direct_debit")
    monkeypatch.setattr(ae, "payment_method", lambda *a, **k: "direct_debit")
    behavioral = {"CANCELS": {
        "income_stress_trajectory": [{"year": 2020, "stress": "LOW"}],
        RECORD_KEY: [{"review_month": "2020-03", "cancelled_month": "2020-03",
                      "failure_multiplier": 1.0}]}}
    bills = [{"customer_id": "CANCELS", "segment": "resi", "total_amount_gbp": 90.0,
              "period_end": f"2020-{m:02d}-28", "commodity": "electricity"} for m in range(1, 13)]
    [(off_after, on_after)] = dcb.supplier_dd_spells(bills, behavioral, 42)["CANCELS"]
    assert off_after == "2020-03-28" and on_after is not None and on_after < "2020-12-28", on_after
    book = dcb.build_dd_collection_book(bills, behavioral, seed=42)
    mandate = book.get_mandate("CANCELS")
    assert mandate.status == "active"
    assert [a for a in book.attempts_for_customer("CANCELS")
            if a.mandate_reference == mandate.mandate_reference]
    rows = ae._resolve_bills(bills, behavioral, 42)
    assert {r["method"] for r in rows if r["period_end"] > on_after} == {"direct_debit"}
