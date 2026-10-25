"""The move-out credit refund fires from the ledger's closing balance (home_moves.md s.8.8a).

Tests simulation/credit_refund_events.py: a closed domestic account is refunded exactly when the
run's `closing_balances` holds it in credit, for that credit, whatever it paid by; the SLA
on-time/breach split is unchanged.
"""
from simulation.credit_refund_events import (
    LATE_WORKING_DAYS,
    ON_TIME_WORKING_DAYS,
    generate_credit_refund_log,
)


def bill(cid, period_end, total):
    return {"customer_id": cid, "period_end": period_end, "total_amount_gbp": total}


BILLS = [
    bill("C1", "2020-01-31", 200.0), bill("C1", "2020-03-31", 50.0),
    bill("C2", "2020-01-31", 50.0), bill("C2", "2020-02-29", 200.0),
    bill("C3", "2020-02-29", 80.0),
]


def test_the_partition_is_takeable_a_credit_is_refunded_and_a_debt_and_a_settled_are_not():
    # Defect: a refund that fires for every leaver, or for none, passes a test of one leg only.
    log = generate_credit_refund_log(BILLS, {}, {"C1": -12.5, "C2": 27.64, "C3": 0.0})
    assert [e["customer_id"] for e in log] == ["C1"]
    assert log[0]["credit_amount_gbp"] == 12.5
    assert log[0]["trigger"] == "account_closure"
    assert log[0]["request_date"] == "2020-03-31"  # the last bill closes the account
    assert log[0]["paid_date"] >= log[0]["request_date"]
    assert isinstance(log[0]["breached_slc14_deadline"], bool)


def test_a_ledger_debtor_is_never_refunded_whatever_its_bills_look_like():
    # Defect (SYN-2016-052, 2026-10-25): falling bills made a level-DD smoothing balance positive,
    # so an account owing GBP 27.64 on the ledger was paid a refund.
    falling = [bill("D", "2016-11-30", 42.63), bill("D", "2016-12-31", 44.99), bill("D", "2017-01-13", 1.17)]
    assert generate_credit_refund_log(falling, {}, {"D": 27.64}) == []


def test_a_ledger_credit_is_refunded_even_when_bills_rose():
    # Defect: the 7 ledger credits at 60 founders were refunded none of them; rising bills made the
    # smoothing balance negative while a credit bill sat on the account.
    rising = [bill("E", "2018-01-31", 66.87), bill("E", "2018-02-28", 55.40), bill("E", "2018-03-07", -37.92)]
    log = generate_credit_refund_log(rising, {}, {"E": -37.92})
    assert [e["credit_amount_gbp"] for e in log] == [37.92]


def test_a_non_direct_debit_domestic_credit_is_refunded():
    # Reg 6D binds a domestic credit however it was paid: the payment method is not read.
    log = generate_credit_refund_log([bill("PREPAY-1", "2020-01-31", 10.0)], {"PREPAY-1": "resi"},
                                     {"PREPAY-1": -3.0})
    assert len(log) == 1


def test_a_non_domestic_credit_is_not_graded_against_the_domestic_standard():
    log = generate_credit_refund_log([bill("C_IC1", "2020-01-31", 20000.0)], {"C_IC1": "ic"},
                                     {"C_IC1": -500.0})
    assert log == []


def test_an_account_with_no_closing_balance_is_not_evaluated():
    # No balance is not a credit: a stayer, or a leaver the walk never reached, is not refunded.
    assert generate_credit_refund_log(BILLS, {}, {}) == []


def test_on_time_and_late_windows_dont_overlap():
    assert ON_TIME_WORKING_DAYS[1] < LATE_WORKING_DAYS[0]


def test_generate_log_deterministic():
    closing = {"C1": -12.5}
    assert generate_credit_refund_log(BILLS, {}, closing) == generate_credit_refund_log(BILLS, {}, closing)
