"""B7 slice 7: a home mover's final bill is decided by the world's exit model, `final_bill_outcome`.

Until this slice the mover's last bill went through `payment_outcome` at the mid-tenure rate. At LOW
stress that lost 0.74% at issue. `final_bill_outcome` loses about 15%, and Centrica provides 32-37%
(home_moves.md s5.1). `arrears_engine.mover_final_bill_outcome` is now the one exit rule. The P&L
(`_resolve_bills`), the billing ledger and the DD book each ask it first, so they agree on the bill.

Each control names the defect it fails on:

* the partition control fails if any one of the three exits (paid, part paid, unpaid) cannot be
  reached. Every other control here would stay green against a rule that always says "unpaid";
* the scope control fails if the rule reaches a mover's earlier bills, a stayer, a prepayment
  statement, or a bill before the last supplied month;
* the rate control fails if the stamp stops reaching the draw (the defect this slice removes). It
  is keyed to the PROPERTY that an exit loses several times what a mid-tenure bill loses, not to
  today's figure;
* the ledger controls fail if the ledger re-derives the bill at the mid-tenure rate again, or books
  a part payment that leaves a balance nobody owes;
* the DD control fails if the rails present the mover's final bill on its old draw.

The run stamps `moved_out_on`: `test_a_home_move_ends_supply_in_the_run.py` holds that leg.
"""
import json

import pytest

import simulation.arrears_engine as ae
from tests.tools.test_generate_billing_ledger_pw import _resi_bill

MOVE_DATE = "2022-06-20"
N = 400


def _book(stress="HIGH", stamped=True):
    bills, behavioral = [], {}
    for i in range(N):
        cid = f"B7S7-{i:03d}"
        behavioral[cid] = {"income_stress_trajectory": [{"year": 2022, "stress": stress}]}
        if stamped:
            behavioral[cid]["moved_out_on"] = MOVE_DATE
        bills += [_resi_bill(cid, "2022-%02d-28" % m, 150.0) for m in range(1, 7)]
    return bills, behavioral


def _key(r):
    return (r["customer_id"], r["period_end"], r["commodity"])


def _final(rows):
    return [r for r in rows if r["period_end"] == "2022-06-28"]


def test_every_exit_is_reachable_paid_part_paid_and_unpaid():
    bills, behavioral = _book()
    finals = _final(ae._resolve_bills(bills, behavioral, 42))
    paid = [r for r in finals if r["outcome"] == "success"]
    part = [r for r in finals if r["outcome"] == "failed" and 0 < r["amount_gbp"] < 150.0]
    unpaid = [r for r in finals if r["outcome"] == "failed" and r["amount_gbp"] == 150.0]
    assert paid and part and unpaid, (len(paid), len(part), len(unpaid))
    assert len(paid) + len(part) + len(unpaid) == N


def test_only_the_movers_final_bill_is_the_exit():
    bills, behavioral = _book()
    _, unstamped = _book(stamped=False)
    plain = {_key(r): r for r in ae._resolve_bills(bills, unstamped, 42)}
    moved = {_key(r): r for r in ae._resolve_bills(bills, behavioral, 42)}
    earlier = [k for k in plain if k[1] != "2022-06-28"]
    assert earlier and all(plain[k] == moved[k] for k in earlier)
    assert [k for k in plain if k[1] == "2022-06-28" and plain[k] != moved[k]]

    stamp = {"moved_out_on": MOVE_DATE}
    exit_ = ae.mover_final_bill_outcome
    assert exit_(stamp, "X", "2022-06-28", "electricity", 150.0, "direct_debit", "LOW", 42)
    assert exit_(stamp, "X", "2022-05-31", "electricity", 150.0, "direct_debit", "LOW", 42) is None
    assert exit_({}, "X", "2022-06-28", "electricity", 150.0, "direct_debit", "LOW", 42) is None
    assert exit_(stamp, "X", "2022-06-28", "electricity", 150.0, "prepayment", "LOW", 42) is None
    assert exit_(stamp, "X", "2022-06-28", "electricity", -5.0, "direct_debit", "LOW", 42) is None
    # A move on the 1st: the last supplied day is the month before, and that month's bill is final.
    first = {"moved_out_on": "2022-06-01"}
    assert exit_(first, "X", "2022-05-31", "electricity", 150.0, "direct_debit", "LOW", 42)


def test_a_movers_final_bill_loses_several_times_what_a_mid_tenure_bill_loses():
    bills, behavioral = _book(stress="LOW")
    _, unstamped = _book(stress="LOW", stamped=False)

    def unpaid(beh):
        return sum(r["amount_gbp"] for r in _final(ae._resolve_bills(bills, beh, 42))
                   if r["outcome"] == "failed")

    mid_tenure, exit_ = unpaid(unstamped), unpaid(behavioral)
    assert exit_ > 5 * max(mid_tenure, 150.0), (mid_tenure, exit_)


@pytest.fixture
def ledger(tmp_path):
    from tools.generate_billing_ledger import generate
    bills, behavioral = _book()
    run = {"bills": bills, "per_customer_behavioral": behavioral, "churned_billing_accounts": [],
           "home_move_outs": [{"household": cid, "customer_id": cid, "commodity": "electricity",
                               "move_date": MOVE_DATE} for cid in behavioral]}
    path = tmp_path / "run.json"
    path.write_text(json.dumps(run))
    return bills, behavioral, generate(path, tmp_path / "ledger.json")


def test_the_ledger_writes_off_what_the_pnl_writes_off_on_a_movers_final_bill(ledger):
    bills, behavioral, result = ledger
    pnl = ae.balance_write_offs(bills, behavioral, set(behavioral), seed=42)
    finals = {k: v["amount_gbp"] for k, v in pnl.items() if k[1] == "2022-06-28"}
    booked = {}
    for cid, cust in result["customers"].items():
        numbers = {i["invoice_number"]: i["period_end"] for i in cust["invoices"]}
        for arr in cust["arrears_history"]:
            if numbers[arr["invoice_number"]] == "2022-06-28":
                assert any(st["stage"] == "WRITTEN_OFF" for st in arr["stages"]), arr
                booked[(cid, "2022-06-28", "electricity")] = arr["arrears_gbp"]
    assert finals and booked == finals


def test_a_part_paid_final_bill_leaves_no_balance_once_written_off(ledger):
    from tools.generate_payment_ledger_data import build_account_ledger
    _, _, result = ledger
    part_paid = [cust for cust in result["customers"].values()
                 if any(p.get("part_paid_gbp") for p in cust["payments"])]
    assert part_paid
    for cust in part_paid:
        account = build_account_ledger(cust, "2099-01-01")
        assert account["current_balance_gbp"] == pytest.approx(0.0, abs=0.01), account["entries"]
        assert cust["total_paid_gbp"] + account["total_written_off_gross_gbp"] == pytest.approx(
            cust["total_billed_gbp"], abs=0.01)


def test_the_dd_rails_present_a_movers_final_bill_on_the_exit_draw():
    from simulation.dd_collection_book import build_dd_collection_book
    bills, behavioral = _book()
    dd = {b["customer_id"] for b in bills
          if ae.payment_method("resi", 150.0, b["customer_id"], "electricity") == "direct_debit"}
    finals = [b for b in bills if b["customer_id"] in dd and b["period_end"] == "2022-06-28"]
    resolved = {r["customer_id"]: r["outcome"]
                for r in _final(ae._resolve_bills(finals, behavioral, 42))}
    book = build_dd_collection_book(finals, behavioral, seed=42)
    # The rails say "collected" where the engine says "success".
    rails = {a.customer_id: {"collected": "success"}.get(a.outcome, a.outcome)
             for a in book.all_attempts()}
    assert "failed" in rails.values() and "success" in rails.values()
    assert rails == {cid: o for cid, o in resolved.items() if cid in rails}
    assert len(rails) == len(resolved)


def test_a_gone_away_balance_is_booked_wholly_unpaid(monkeypatch):
    """Defect: the gone-away recovery band taken as a part payment, so the register's post-close
    recovery is applied on top of it and one collection is counted twice."""
    import simulation.final_bill_outcome as fbo

    def resolved(gone_away):
        def fake(exposure, as_of, stress="LOW", income_stress_trajectory=None, seed=None):
            return fbo.FinalBillResolution(
                account_id="X", supply_point_id="X", fuel="electricity", resolved_on=as_of,
                outcome=fbo.FinalBillOutcome.PARTIALLY_PAID, billed_gbp=150.0,
                recovered_gbp=15.0, gone_away=gone_away)
        return fake

    stamp = {"moved_out_on": MOVE_DATE}
    args = (stamp, "X", "2022-06-28", "electricity", 150.0, "direct_debit", "LOW", 42)
    monkeypatch.setattr(fbo, "resolve_final_bill", resolved(True))
    assert ae.mover_final_bill_outcome(*args) == ("failed", 0, 0.0)
    monkeypatch.setattr(fbo, "resolve_final_bill", resolved(False))
    assert ae.mover_final_bill_outcome(*args) == ("failed", 0, 15.0)
