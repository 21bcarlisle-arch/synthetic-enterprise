"""The world's payment truth records the cash a settlement carried, not the face of the bill it
settles.

The triad sends a household's later settlement cut to what is still open on its contract
(`LivePaymentTriad._cross_settlement`, debt_and_collections.md s.7.3). The truth it hands the engine
(`world_payment_truth.build`) kept only the bill month, so `repayment_rows` re-priced every
settlement at the bill's face. On the 8c7489e0d9 book that read as 19 settlements (GBP 682.47)
"carrying more cash than the engine's walk holds open". SYN-2016-047's row said 64.38, the face of
its failed Jul 2021 bill. What crossed was 20.71, after a 43.67 read-catch-up credit. The engine
cut the face again, so the P&L was right, but no reader could tell the cash the world sent from a
face the engine re-derived.
"""
import datetime as dt

from background.live_payment_triad import LivePaymentTriad
from simulation import world_payment_truth as wpt
from simulation.arrears_engine import open_on_contract_gbp


def _post(triad, cid, due, month, amount=0.0, credit=0.0):
    return triad.record_period(customer_id=cid, due_date=due, bill_month=month, amount_gbp=amount,
                               credit_gbp=credit, income_stress_value="low")


def _book(credit_gbp):
    # "CRED-42"'s Feb 2018 DD fails, and the world settles it on 28 Mar (the seeded draw that
    # tests/background/test_a_nil_ask_presents_no_collection.py names). A credit bill lands between.
    triad = LivePaymentTriad()
    _post(triad, "CRED-42", dt.date(2018, 2, 14), "2018-01", amount=50.0)
    _post(triad, "CRED-42", dt.date(2018, 3, 14), "2018-02", amount=100.0)
    _post(triad, "CRED-42", dt.date(2018, 3, 20), "2018-03", credit=credit_gbp)
    triad.collections_journeys(dt.date(2018, 6, 30))
    return triad


def _bill_rows():
    return [{"customer_id": "CRED-42", "period_end": "2018-01-31", "commodity": "electricity",
             "amount_gbp": 50.0, "due_date": dt.date(2018, 2, 14), "outcome": "success",
             "days_late": 0, "method": None},
            {"customer_id": "CRED-42", "period_end": "2018-02-28", "commodity": "electricity",
             "amount_gbp": 100.0, "due_date": dt.date(2018, 3, 14), "outcome": "failed",
             "days_late": 0, "method": None},
            {"customer_id": "CRED-42", "period_end": "2018-03-31", "commodity": "electricity",
             "amount_gbp": -30.0, "due_date": dt.date(2018, 3, 20), "outcome": "credit",
             "days_late": 0, "method": None}]


def test_the_engine_row_carries_the_cash_that_crossed_not_the_bills_face():
    triad = _book(credit_gbp=30.0)
    # The branch this test is about was taken: the triad cut the settlement.
    assert triad.later_settlements()["cut_to_balance"] == 1
    truth = wpt.build(triad, dt.date(2018, 6, 30))["CRED-42"]
    [settlement] = [r for r in truth["repayments"] if r["kind"] == "settlement"]
    assert settlement["amount_gbp"] == 70.0, settlement
    bill_rows = _bill_rows()
    [row] = wpt.repayment_rows(truth, "CRED-42", bill_rows)
    assert row["amount_gbp"] == 70.0, "the engine was handed the bill's face, not the cash"
    # What crossed is exactly what the engine's walk holds open on the day: one walk, not two.
    assert row["amount_gbp"] == open_on_contract_gbp(bill_rows, row["due_date"])


def test_an_uncut_settlement_still_carries_the_whole_bill():
    # The control: with no credit between, the cash is the bill, so the record did not just shrink.
    triad = _book(credit_gbp=0.0)
    assert triad.later_settlements()["cut_to_balance"] == 0
    truth = wpt.build(triad, dt.date(2018, 6, 30))["CRED-42"]
    [row] = wpt.repayment_rows(truth, "CRED-42", _bill_rows()[:2])
    assert row["amount_gbp"] == 100.0


def test_a_book_written_before_the_cash_was_recorded_still_prices_at_the_face():
    # Saved books carry settlements without an amount; they keep the face fallback.
    truth = {"outcomes": {}, "repayments": [
        {"date": "2018-03-28", "kind": "settlement", "bill_month": "2018-02"}]}
    [row] = wpt.repayment_rows(truth, "CRED-42", _bill_rows()[:2])
    assert row["amount_gbp"] == 100.0
