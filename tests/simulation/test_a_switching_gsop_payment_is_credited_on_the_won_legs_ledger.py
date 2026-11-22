"""A switching standard payment the company pays by account credit (reg 8(2)) is netted on the won
leg's own ledger, oldest bill first, and one owed to a win with no ledger is refused by name
(switching_mechanics_2026-10-25.md s.6, "Posting the payment").

The defect this catches: `switching_gsop_payments` was published and never reached any ledger, so
the book carried a payment no customer's account showed (SEAT_FINDING_A_WON_SWITCH_IS_NEVER_PUT_ON_
SUPPLY_SO_THE_SWITCHING_GSOP_HAS_NO_ACCOUNT_TO_CREDIT_2026-11-21). The expected count on today's
volume is under one, so the gain is constructed with an agreed erroneous transfer, and the branch is
asserted taken before what it does.
"""
from __future__ import annotations

import datetime as dt

from company.interfaces.switching_gsop import switching_payments_on_gains
from simulation.arrears_engine import LEG_CLOSE, balance_settlement_from_outcomes
from simulation.gain_registration import account_credits_from_switching_payments

_WON, _GAS_ONLY, _UNBILLED = "SYN-2016-144_3", "SYN-2016-163_3", "SYN-2016-777_3"


def _gain(cid: str, agreed: str | None) -> dict:
    return {"customer_id": cid, "information_received_on": "2020-06-01", "contract_on": "2020-06-01",
            "registration_confirmed_on": "2020-06-01", "erroneous_transfer_agreed_on": agreed}


def _posting():
    payments = switching_payments_on_gains(
        [_gain(_WON, "2020-06-29"), _gain(_GAS_ONLY, "2020-06-29"), _gain(_UNBILLED, "2020-06-29"),
         _gain("SYN-2016-001_3", None)])
    not_supplied = [{"customer_id": _GAS_ONLY, "reason": "won from a gas-only household"}]
    return payments, account_credits_from_switching_payments(payments, {_WON}, not_supplied)


def test_the_erroneous_transfer_payment_is_owed_and_both_doors_are_taken():
    """The partition first: a 6ZB payment exists, one is posted, and one is refused per reason."""
    payments, (credits, refused) = _posting()
    assert [p["standard"] for p in payments if p["customer_id"] == _WON] == ["erroneous_transfer"]
    assert len(payments) == 3, "a gain with no agreed erroneous transfer owes nothing"
    assert list(credits) == [_WON] and len(credits[_WON]) == 1
    assert {r["customer_id"] for r in refused} == {_GAS_ONLY, _UNBILLED}


def test_each_refusal_names_its_reason():
    _, (_, refused) = _posting()
    why = {r["customer_id"]: r["refused_reason"] for r in refused}
    assert why[_GAS_ONLY].startswith("win not on supply: won from a gas-only household")
    assert "no issued bill" in why[_UNBILLED]


def _bill(period_end: str, outcome: str, amount: float) -> dict:
    return {"customer_id": _WON, "period_end": period_end, "commodity": "electricity",
            "due_date": dt.date.fromisoformat(period_end) + dt.timedelta(days=14),
            "outcome": outcome, "amount_gbp": amount, "days_late": 0, "method": "cash_cheque"}


_ROWS = [_bill("2020-06-30", "failed", 20.0), _bill("2020-07-31", "failed", 40.0),
         _bill("2020-08-31", "success", 50.0)]


def test_the_credit_meets_the_oldest_outstanding_bill_first_and_cuts_the_write_off():
    _, (credits, _) = _posting()
    amount = credits[_WON][0]["amount_gbp"]
    closing_without: dict[str, float] = {}
    without, _ = balance_settlement_from_outcomes(_ROWS, {_WON}, closing_without)
    closing_with: dict[str, float] = {}
    written, credited = balance_settlement_from_outcomes(_ROWS, {_WON}, closing_with,
                                                         account_credits=credits)
    june, july = (_WON, "2020-06-30", "electricity"), (_WON, "2020-07-31", "electricity")
    # GBP 30: all of June's 20 and 10 of July's 40, oldest first.
    assert amount == 30.0
    assert [c["amount_gbp"] for c in credited[june]] == [20.0]
    assert [c["amount_gbp"] for c in credited[july]] == [10.0]
    assert june not in written and written[july]["amount_gbp"] == 30.0
    assert written[july]["leg"] == LEG_CLOSE
    assert round(sum(w["amount_gbp"] for w in without.values()), 2) == 60.0
    assert closing_without[_WON] - closing_with[_WON] == amount


def test_a_credit_with_nothing_outstanding_waits_and_comes_off_the_next_paid_bill():
    credits = {_WON: [{"date": dt.date(2020, 8, 1), "amount_gbp": 30.0, "reason": "6ZB"}]}
    rows = [_bill("2020-08-31", "success", 50.0)]
    _, credited = balance_settlement_from_outcomes(rows, set(), account_credits=credits)
    assert [c["amount_gbp"] for c in credited[(_WON, "2020-08-31", "electricity")]] == [30.0]


def test_a_credit_after_the_last_event_is_still_on_the_closing_balance():
    """Posted at close, as a set-off is: a leaver is refunded it, never silently dropped."""
    credits = {_WON: [{"date": dt.date(2021, 3, 1), "amount_gbp": 30.0, "reason": "6ZB"}]}
    closing: dict[str, float] = {}
    balance_settlement_from_outcomes([_bill("2020-08-31", "success", 50.0)], {_WON}, closing,
                                     account_credits=credits)
    assert closing[_WON] == -30.0
