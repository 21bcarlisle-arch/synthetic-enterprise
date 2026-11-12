"""A household that settles a credit-bill month in cash has that cash reach the engine.

A level household's credit-bill month still presents its level collection. When the bank returns it,
the household later settles the month, and the desk counts that cash. `repayment_rows` treated a
month as issued only if its bill row was failed, dispute or success. A credit row is none of those,
so the cash was dropped before the engine. On the 6fe7827ab2 book that was 6 of the 12 settlements
the engine dropped (GBP 446.13). SYN-2016-217g's GBP 22.00 of 15 May 2022, for a -6.68 gas bill,
held three level-DD cures on the page that the desk had made (LEVEL_DD_AREA_MAP s.9.4).
"""
import datetime as dt

from simulation import world_payment_truth as wpt

CID = "SYN-2016-217g"


def _row(month, outcome, amount, **extra):
    return {"customer_id": CID, "period_end": f"{month}-28", "commodity": "gas",
            "amount_gbp": amount, "due_date": dt.date.fromisoformat(f"{month}-28"),
            "method": None, "outcome": outcome, "days_late": 0, **extra}


BILLS = [_row("2022-02", "failed", 40.0),
         _row("2022-03", "credit", -6.68, collection_result="failed"),
         _row("2022-04", "success", 30.0)]


def _truth(*repayments):
    return {"outcomes": {}, "repayments": list(repayments)}


def test_the_settlement_of_a_credit_month_whose_collection_was_returned_reaches_the_engine():
    truth = _truth({"date": "2022-05-15", "kind": "settlement", "bill_month": "2022-03",
                    "amount_gbp": 22.0})
    [row] = wpt.repayment_rows(truth, CID, BILLS)
    assert (row["amount_gbp"], row["commodity"], row["settles_month"]) == (22.0, "gas", "2022-03")


def test_a_settlement_of_a_month_with_no_bill_is_still_dropped():
    # The guard is still a guard: it is not "pass every settlement".
    truth = _truth({"date": "2022-08-15", "kind": "settlement", "bill_month": "2022-07",
                    "amount_gbp": 22.0})
    assert wpt.repayment_rows(truth, CID, BILLS) == []


def test_both_branches_are_live_on_one_book():
    truth = _truth({"date": "2022-05-15", "kind": "settlement", "bill_month": "2022-03",
                    "amount_gbp": 22.0},
                   {"date": "2022-08-15", "kind": "settlement", "bill_month": "2022-07",
                    "amount_gbp": 9.0})
    assert [r["settles_month"] for r in wpt.repayment_rows(truth, CID, BILLS)] == ["2022-03"]


def test_a_credit_bills_face_does_not_shrink_a_plan_instalment():
    # A plan covering the failed month and the credit month repays a share of what was ASKED: the
    # failed bill's 40.00. The credit's -6.68 is not an ask.
    truth = _truth({"date": "2022-06-01", "kind": "plan", "covered_months": ["2022-02", "2022-03"],
                    "share": 0.5})
    [row] = wpt.repayment_rows(truth, CID, BILLS)
    assert row["amount_gbp"] == 20.0


def test_a_saved_settlement_without_its_cash_on_a_credit_month_is_not_priced_negative():
    # Old books carry no `amount_gbp`, and the face fallback for a credit month is no ask at all.
    truth = _truth({"date": "2022-05-15", "kind": "settlement", "bill_month": "2022-03"})
    assert wpt.repayment_rows(truth, CID, BILLS) == []
