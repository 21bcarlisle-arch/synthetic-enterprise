"""A closing set-off moves the statement walk on both legs, as it moves the page.

Defect it names: `account_events` read `refunds` and `desk_write_offs` but not `set_offs`, so on the
6fe7827ab2 run with N29's set-off replay the walk closed away from the page on 84 of 1,302 legs, each
by exactly its set-off
(`docs/staging/SEAT_FINDING_THE_STATEMENT_WALK_DOES_NOT_CARRY_THE_CLOSING_SET_OFF_2026-11-14.md`).
"""
from company.billing.statement_export import account_events
from tools.generate_billing_ledger import post_refunds_and_set_offs
from tools.generate_payment_ledger_data import build_account_ledger

AS_OF = "2021-06-30"
CLOSE = "2020-05-14"


def _leg(billed, paid):
    pays = [{"invoice_number": 1, "payment_date": "2020-04-10", "amount_gbp": paid,
             "outcome": "success", "method": "direct_debit"}] if paid else []
    return {"invoices": [{"invoice_number": 1, "issue_date": "2020-04-01",
                          "total_amount_gbp": billed}], "payments": pays, "arrears_history": []}


def _close(credit_on_e, owed_on_g, set_off, refunded):
    legs = {"E": _leg(60.0, 60.0 + credit_on_e), "Eg": _leg(owed_on_g, 0.0)}
    post_refunds_and_set_offs(legs, [{
        "customer_id": "E", "paid_date": CLOSE, "credit_amount_gbp": refunded,
        "set_off_gbp": set_off, "set_off_against": "Eg"}])
    out = {}
    for cid, rec in legs.items():
        page = build_account_ledger(rec, AS_OF)["current_balance_gbp"]
        walk = account_events({**rec, "balance_as_of_date": AS_OF})
        assert abs(page + walk[-1]["balance_after_gbp"]) < 0.005, (cid, page, walk[-1])
        out[cid] = (page, [e for e in walk if e["date"] == CLOSE])
    return legs, out


def test_the_set_off_moves_both_legs_of_the_walk_on_its_own_day():
    # The credit leg's 40 pays 40 of the gas leg's 70: the credit leg closes at zero, the gas owes 30.
    legs, out = _close(credit_on_e=40.0, owed_on_g=70.0, set_off=40.0, refunded=0.0)
    assert legs["E"]["set_offs"] and legs["Eg"]["set_offs"]  # the branch is taken on both legs
    assert out["E"][0] == 0.0 and out["Eg"][0] == 30.0
    assert [e["moves_balance_gbp"] for e in out["E"][1]] == [-40.0]
    assert [e["moves_balance_gbp"] for e in out["Eg"][1]] == [40.0]
    # The credit exceeds the debt: 30 set off, 20 refunded, both legs close at zero, set-off first.
    legs, out = _close(credit_on_e=50.0, owed_on_g=30.0, set_off=30.0, refunded=20.0)
    assert out["E"][0] == 0.0 and out["Eg"][0] == 0.0
    assert [e["moves_balance_gbp"] for e in out["E"][1]] == [-30.0, -20.0]


def test_a_leg_with_no_set_off_walks_as_before():
    legs, out = _close(credit_on_e=25.0, owed_on_g=10.0, set_off=0.0, refunded=25.0)
    assert "set_offs" not in legs["E"] and "set_offs" not in legs["Eg"]
    assert out["E"][0] == 0.0 and out["Eg"][0] == 10.0
