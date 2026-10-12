"""One world payment truth: the P&L's losses come from the payment truth the household
mechanisms act on (2026-10-12, the world lane).

What each control names as its own defect:

  * `test_the_shipped_engine_draws_as_before` -- the switch on by default, or a record without the
    truth read as if it had one.
  * `test_the_engine_takes_each_bills_outcome_from_the_truth_and_draws_only_where_it_has_none` --
    two truths again: the engine's own draw overriding the household's, or no fallback counted.
  * `test_a_repayment_reaches_the_write_off_whole_part_or_not_at_all` -- the partition first
    (written off in full, in part, not at all); a repayment that never reaches the balance.
  * `test_a_repayment_discharges_the_oldest_bill_and_restarts_the_clock` -- the allocation or the
    limitation rule lost.
  * `test_a_kept_plan_repays_more_than_a_broken_one` -- the triad-to-truth build loses the plan,
    or a broken plan repays as if kept.
"""
from __future__ import annotations

import dataclasses
from datetime import date

import simulation.arrears_engine as ae
import simulation.plan_offer_response as por
import simulation.world_payment_truth as wpt
from background.live_payment_triad import LivePaymentTriad
from tests.tools.test_generate_billing_ledger_pw import _resi_bill

MONTHS = ["2022-%02d-28" % m for m in range(1, 13)]


def _book(truth=None, cid="PROS-2016-0001"):
    behavioral = {cid: {"income_stress_trajectory": [{"year": 2022, "stress": "low"}]}}
    if truth is not None:
        behavioral[cid][wpt.RECORD_KEY] = truth
    return [_resi_bill(cid, pe, 100.0 + i) for i, pe in enumerate(MONTHS)], behavioral, cid


def _truth(failed=("2022-03",), repayments=(), months=MONTHS):
    return {"outcomes": {pe[:7]: {"result": "failed" if pe[:7] in failed else "success",
                                  "days_late": 0, "method": "direct_debit"} for pe in months},
            "repayments": list(repayments)}


def test_the_shipped_engine_draws_as_before():
    assert wpt.UNIFIED is False
    bills, behavioral, _ = _book()
    once = ae._resolve_bills(bills, behavioral, 42)
    assert once == ae._resolve_bills(bills, dict(behavioral), 42)
    assert all(r["outcome"] != "repayment" for r in ae._resolve_bills(bills, behavioral, 42))


def test_the_engine_takes_each_bills_outcome_from_the_truth_and_draws_only_where_it_has_none():
    bills, behavioral, cid = _book(_truth(failed=("2022-03", "2022-07"), months=MONTHS[:10]))
    rows = [r for r in ae._resolve_bills(bills, behavioral, 42) if r["outcome"] != "repayment"]
    failed = {r["period_end"][:7] for r in rows if r["outcome"] == "failed"}
    assert {"2022-03", "2022-07"} <= failed
    assert not failed & {pe[:7] for pe in MONTHS[:10]} - {"2022-03", "2022-07"}
    assert wpt.LAST_COUNTS == {"truth_bills": 10, "fallback_bills": 2, "repayment_rows": 0}


def _written_off(truth):
    bills, behavioral, cid = _book(truth)
    return sum(w["amount_gbp"] for w in ae.balance_write_offs(bills, behavioral, {cid}).values())


def test_a_repayment_reaches_the_write_off_whole_part_or_not_at_all():
    march = 102.0  # the third bill's issued amount
    none_repaid = _written_off(_truth())
    settled = _written_off(_truth(repayments=[{"date": "2022-05-10", "kind": "settlement",
                                               "bill_month": "2022-03"}]))
    half = _written_off(_truth(repayments=[{"date": "2022-05-10", "kind": "plan_instalment",
                                            "covered_months": ["2022-03"], "share": 0.5}]))
    assert none_repaid > half > settled == 0, (none_repaid, half, settled)
    assert none_repaid >= march and abs(none_repaid - half - march / 2) < 0.6


def test_a_repayment_discharges_the_oldest_bill_and_restarts_the_clock():
    truth = _truth(failed=("2022-02", "2022-06"),
                   repayments=[{"date": "2022-08-10", "kind": "settlement",
                                 "bill_month": "2022-06"}])
    bills, behavioral, cid = _book(truth)
    wo = ae.balance_write_offs(bills, behavioral, {cid})
    left = {k[1][:7]: v["amount_gbp"] for k, v in wo.items()}
    # 105 repaid against 101 (Feb, oldest) then 4 of June's 105: June is what is left.
    assert left == {"2022-06": 101.0}, left
    resolved = ae._resolve_bills(bills, behavioral, 42)
    repay = [r for r in resolved if r["outcome"] == "repayment"]
    assert len(repay) == 1 and repay[0]["due_date"] == date(2022, 8, 10)


def _plan_world(monkeypatch, break_share):
    world = dataclasses.replace(por.basis_at("high"), take_up_rate=1.0,
                                plan_break_share=break_share)
    monkeypatch.setattr(por, "BASIS", world)
    triad = LivePaymentTriad()
    for i in range(40):
        for m in range(1, 13):
            triad.record_period(customer_id=f"RESI{i:05d}", due_date=date(2020, m, 28),
                                amount_gbp=120.0, income_stress_value="high", segment="resi")
    triad.collections_journeys(date(2022, 12, 31))
    return wpt.build(triad, date(2022, 12, 31))


def test_a_kept_plan_repays_more_than_a_broken_one(monkeypatch):
    kept, broken = _plan_world(monkeypatch, 0.0), _plan_world(monkeypatch, 1.0)
    def plan_share(truth):
        return sum(rp["share"] for t in truth.values() for rp in t["repayments"]
                   if rp["kind"] == "plan_instalment")
    assert plan_share(kept) > plan_share(broken) > 0
    assert any(rp["kind"] == "settlement" for t in kept.values() for rp in t["repayments"])
    assert all(t["outcomes"] for t in kept.values())


# --- The rails and a mover's final bill on the same truth (2026-10-12) ----------------------------
#
#   * `test_the_rails_stop_a_dd_on_the_households_own_returns` -- the rails' second draw: a DD the
#     household always paid stopped, or one it never paid left running; the partition (stopped, not
#     stopped) asserted first.
#   * `test_a_movers_final_bill_is_decided_once_in_the_triad` -- the exit drawn twice, the final
#     bill still sent to the lump route, or the exit never reachable both ways.

from simulation.dd_collection_book import supplier_dd_stop_notices  # noqa: E402


def _dd_cid():
    from simulation.household_segments import PaymentChannel, payment_channel_for_customer
    return next(c for c in (f"PROS-2016-{i:04d}" for i in range(200))
                if payment_channel_for_customer(c, "electricity") is PaymentChannel.DIRECT_DEBIT)


def test_the_rails_stop_a_dd_on_the_households_own_returns():
    cid = _dd_cid()
    bills = [{"customer_id": cid, "period_end": pe, "total_amount_gbp": 100.0, "segment": "resi",
              "commodity": "electricity"} for pe in MONTHS]
    def notices(failed):
        truth = _truth(failed=failed)
        return supplier_dd_stop_notices(bills, {cid: {wpt.RECORD_KEY: truth}}, 42)
    assert cid in notices([pe[:7] for pe in MONTHS])
    assert notices(()) == {}
    off_dd = _truth(failed=[pe[:7] for pe in MONTHS])
    for o in off_dd["outcomes"].values():
        o["method"] = ae.PAY_ON_RECEIPT_METHOD
    assert supplier_dd_stop_notices(bills, {cid: {wpt.RECORD_KEY: off_dd}}, 42) == {}, (
        "a household paying by hand that month is not on the rails")


def test_the_engine_reads_a_movers_final_bill_from_the_truth_and_does_not_redraw_it():
    redrawn_failed = [c for c in (f"PROS-2016-{i:04d}" for i in range(300))
                      if (ae.mover_final_bill_outcome({"moved_out_on": "2022-12-15"}, c,
                                                      "2022-12-28", "electricity", 111.0,
                                                      "direct_debit", "LOW", 42) or ("",))[0]
                      == "failed"][:5]
    assert redrawn_failed, "control: the engine's own exit can fail"
    for cid in redrawn_failed:
        bills, behavioral, _ = _book(_truth(failed=()), cid=cid)
        behavioral[cid]["moved_out_on"] = "2022-12-15"
        dec = [r for r in ae._resolve_bills(bills, behavioral, 42)
               if r["period_end"].startswith("2022-12")]
        assert dec and dec[0]["outcome"] == "success", (cid, dec)


def test_a_movers_final_bill_is_decided_once_in_the_triad(monkeypatch):
    monkeypatch.setattr(wpt, "UNIFIED", True)
    triad = LivePaymentTriad()
    seen = set()
    for i in range(120):
        cid = f"RESI{i:05d}"
        triad.record_period(customer_id=cid, due_date=date(2020, 3, 28), amount_gbp=90.0,
                            income_stress_value="moderate", segment="resi",
                            moved_out_on="2020-03-15")
        method = wpt.engine_method(triad._method_for(cid))
        expect = ae.mover_final_bill_outcome({"moved_out_on": "2020-03-15"}, cid,
                                             "2020-03-28", "electricity", 90.0, method,
                                             "MODERATE", 42)
        if expect is None:
            continue
        got = triad.payment_truth_so_far(cid)["outcomes"]["2020-03"]["result"]
        assert got == expect[0], (cid, got, expect)
        seen.add(got)
        assert triad.records[-1].settled_on is None, "the final-bill model recovers; no lump too"
    assert seen == {"success", "failed"}, seen
