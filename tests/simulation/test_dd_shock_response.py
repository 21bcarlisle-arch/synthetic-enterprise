"""DD4b -- a household answers a direct-debit shock (`simulation/dd_shock_response.py`).

What each control names as its own defect:

  * `test_every_response_can_fire_and_can_fail_to_fire` -- a response that never fires (or always
    fires) at a non-zero strength. Asserted over the whole partition first, before anything below
    asserts what a response does.
  * `test_nothing_is_drawn_while_the_toggles_are_off` -- the shipped world moves at strength zero.
  * `test_only_a_material_rise_on_a_level_payment_is_answered` -- population B, a fall, an
    unmeasurable shock (None) or a below-threshold rise read as a shock.
  * `test_a_stretched_household_cancels_more_readily` -- the hidden finances not read, or read
    backwards.
  * `test_a_leaver_cancels_nothing_and_a_cancelled_mandate_is_not_cancelled_twice` -- a response
    applied to a mandate that no longer exists.
  * `test_the_calendar_of_one_cancellation_and_one_uplift` -- the cancelled month not returned,
    later months still collected by DD, or the uplift outliving the reviewed year.
  * `test_the_arrears_engine_returns_the_cancelled_month_and_bills_the_rest_on_receipt` and
    `test_the_rails_put_nothing_on_after_a_cancellation` -- the money side ignoring the response,
    so bad debt cannot move.
  * `test_the_uplift_raises_returns_in_the_arrears_engine` -- the uplift reaching no draw.
  * `test_the_triad_returns_the_cancelled_collection_and_the_supplier_hears_addacs` -- the company
    never learning of a cancellation.
"""
from __future__ import annotations

from datetime import date

import simulation.arrears_engine as ae
import simulation.bacs_rails as br
import simulation.dd_collection_book as dcb
import simulation.dd_shock_response as d
from background.live_payment_triad import LivePaymentTriad
from simulation.household_segments import PaymentChannel, payment_channel_for_customer
from simulation.payment_behaviour_source import CANCELLED_OTHER
from tests.tools.test_generate_billing_ledger_pw import _resi_bill

ON = d.DDShockStrengths(cancel_share=0.5, failure_uplift=1.0, complaint_share=0.5)
SHOCK = {"population": d.POPULATION_LEVEL_PAYMENT, "shocked": True, "rise_fraction": 0.4}


def _respond(i, **kw):
    args = dict(household=f"H{i:04d}", review_month="2022-04", shock=SHOCK, stress="low",
                stays=True, already_cancelled=False, strengths=ON)
    args.update(kw)
    return d.respond(**args)


def _dd_ids(n):
    out = []
    i = 0
    while len(out) < n:
        cid = f"PROS-2016-{i:04d}"
        if payment_channel_for_customer(cid, "electricity") is PaymentChannel.DIRECT_DEBIT:
            out.append(cid)
        i += 1
    return out


def test_every_response_can_fire_and_can_fail_to_fire():
    rows = [_respond(i) for i in range(200)]
    assert all(r is not None for r in rows)
    cancelled = [r for r in rows if r["cancelled_month"]]
    complained = [r for r in rows if r["complained"]]
    assert 0 < len(cancelled) < len(rows), "cancellation must be reachable and not universal"
    assert 0 < len(complained) < len(rows), "complaint must be reachable and not universal"
    assert all(r["failure_multiplier"] == 2.0 for r in rows), "a stayer's uplift is 1 + uplift"


def test_nothing_is_drawn_while_the_toggles_are_off():
    assert d.DDShockStrengths().off and d.DDShockStrengths.at("default").off
    assert d.STRENGTHS.off, "the shipped world must ship DD4b switched off"
    assert _respond(0, strengths=d.DDShockStrengths()) is None


def test_only_a_material_rise_on_a_level_payment_is_answered():
    assert _respond(0) is not None, "control: the positive case responds"
    for shock in (None,
                  {**SHOCK, "population": "B_standard_credit"},
                  {**SHOCK, "shocked": False},
                  {**SHOCK, "shocked": None}):
        assert _respond(0, shock=shock) is None, shock


def test_a_stretched_household_cancels_more_readily():
    weak = d.DDShockStrengths(cancel_share=0.05)
    low = sum(bool(_respond(i, strengths=weak, stress="low")["cancelled_month"]) for i in range(400))
    high = sum(bool(_respond(i, strengths=weak, stress="high")["cancelled_month"]) for i in range(400))
    assert 0 < low < high, (low, high)


def test_a_leaver_cancels_nothing_and_a_cancelled_mandate_is_not_cancelled_twice():
    leavers = [_respond(i, stays=False) for i in range(100)]
    assert not any(r["cancelled_month"] for r in leavers)
    assert all(r["failure_multiplier"] == 1.0 for r in leavers)
    assert any(r["complained"] for r in leavers), "a leaver can still complain"
    again = [_respond(i, already_cancelled=True) for i in range(100)]
    assert not any(r["cancelled_month"] for r in again)


def test_the_calendar_of_one_cancellation_and_one_uplift():
    cancel = [{"review_month": "2022-04", "cancelled_month": "2022-04", "failure_multiplier": 2.0}]
    assert d.bill_effect(cancel, "2022-03") == d.NO_EFFECT
    assert d.bill_effect(cancel, "2022-04").cancel_return
    assert d.bill_effect(cancel, "2022-05").cancelled and d.bill_effect(cancel, "2023-09").cancelled
    uplift = [{"review_month": "2022-04", "cancelled_month": None, "failure_multiplier": 2.0}]
    assert d.bill_effect(uplift, "2022-03").failure_multiplier == 1.0
    assert d.bill_effect(uplift, "2022-04").failure_multiplier == 2.0
    assert d.bill_effect(uplift, "2023-03").failure_multiplier == 2.0
    assert d.bill_effect(uplift, "2023-04").failure_multiplier == 1.0
    assert d.failure_table(1.0) is None
    table = d.failure_table(2.0)
    assert table["LOW"] == 2 * ae._DD_FAILURE_PROB["LOW"] and max(table.values()) <= 1.0


def _book(ids, response=None, stress="moderate"):
    bills, behavioral = [], {}
    for cid in ids:
        behavioral[cid] = {"income_stress_trajectory": [{"year": 2022, "stress": stress}]}
        if response is not None:
            behavioral[cid][d.RECORD_KEY] = [response]
        bills += [_resi_bill(cid, "2022-%02d-28" % m, 150.0) for m in range(1, 13)]
    return bills, behavioral


def test_the_arrears_engine_returns_the_cancelled_month_and_bills_the_rest_on_receipt(monkeypatch):
    # The cancellation's own trace, with no invitation back: signing again is test_a_dd_stop_is_a_spell's.
    monkeypatch.setattr(br, "REMANDATE_ACCEPTANCE_PROBABILITY", None)
    ids = _dd_ids(20)
    cancel = {"review_month": "2022-04", "cancelled_month": "2022-04", "failure_multiplier": 1.0}
    plain = {(r["customer_id"], r["period_end"]): r
             for r in ae._resolve_bills(*_book(ids, stress="low"), 42)}
    shocked = {(r["customer_id"], r["period_end"]): r
               for r in ae._resolve_bills(*_book(ids, cancel, stress="low"), 42)}
    assert all(r["method"] == "direct_debit" for r in plain.values()), (
        "control: the plain book is on DD throughout, so any change below is the cancellation's")
    for (cid, pe), r in shocked.items():
        month = pe[:7]
        if month < "2022-04":
            assert r == plain[(cid, pe)]
        elif month == "2022-04":
            assert r["outcome"] == "failed" and r["method"] == "direct_debit"
        else:
            assert r["method"] == ae.PAY_ON_RECEIPT_METHOD


def test_the_rails_put_nothing_on_after_a_cancellation(monkeypatch):
    # As above: no invitation back, so nothing after the returned month is presented.
    monkeypatch.setattr(br, "REMANDATE_ACCEPTANCE_PROBABILITY", None)
    ids = _dd_ids(10)
    cancel = {"review_month": "2022-04", "cancelled_month": "2022-04", "failure_multiplier": 1.0}
    plain = dcb.build_dd_collection_book(*_book(ids, stress="low")).all_attempts()
    shocked = dcb.build_dd_collection_book(*_book(ids, cancel, stress="low")).all_attempts()
    by = lambda rows: {c: [a for a in rows if a.customer_id == c] for c in ids}  # noqa: E731
    plain, shocked = by(plain), by(shocked)
    for cid in ids:
        # Bills Jan-Apr are presented; the April one comes back; May-Dec are never presented.
        assert len(plain[cid]) == 12, "control: the plain book presents every month"
        assert len(shocked[cid]) == 4, (cid, [(a.attempt_date, a.outcome) for a in shocked[cid]])
        assert shocked[cid][-1].outcome == "failed"


def test_the_uplift_raises_returns_in_the_arrears_engine():
    ids = _dd_ids(60)
    uplift = {"review_month": "2022-01", "cancelled_month": None, "failure_multiplier": 4.0}
    fails = lambda rows: sum(r["outcome"] == "failed" for r in rows)  # noqa: E731
    base = fails(ae._resolve_bills(*_book(ids), 42))
    up = fails(ae._resolve_bills(*_book(ids, uplift), 42))
    assert base > 0 and up > base, (base, up)


def test_the_triad_returns_the_cancelled_collection_and_the_supplier_hears_addacs():
    cid = _dd_ids(1)[0]
    triad = LivePaymentTriad()
    cancel = [{"review_month": "2022-04", "cancelled_month": "2022-04", "failure_multiplier": 1.0}]
    for m in range(3, 7):
        triad.record_period(customer_id=cid, due_date=date(2022, m, 28), amount_gbp=120.0,
                            income_stress_value="low", segment="resi",
                            dd_shock_effect=d.bill_effect(cancel, f"2022-{m:02d}"))
    by_month = {r.due_date.month: r for r in triad.records}
    assert by_month[3].payment_method == "direct_debit"
    assert by_month[4].result == "failed" and by_month[4].dd_failure_reason == CANCELLED_OTHER
    assert by_month[5].payment_method == ae.PAY_ON_RECEIPT_METHOD
    assert by_month[6].payment_method == ae.PAY_ON_RECEIPT_METHOD
    assert triad._mandate_stream.next_sequence >= 1, "no ADDACS advice reached the supplier"
