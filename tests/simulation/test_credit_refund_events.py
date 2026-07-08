"""Phase 3 (CORE_FIDELITY_PHASES.md item 2): SLC 14 credit-refund activation.

Tests simulation/credit_refund_events.py: DD smoothing balance math, refund
only firing for churned DD customers with a real positive balance, and the
SLA on-time/breach split.
"""
from simulation.credit_refund_events import (
    ON_TIME_WORKING_DAYS,
    LATE_WORKING_DAYS,
    dd_smoothing_balance_at_closure,
    generate_credit_refund_log,
)


def bill(cid, period_end, total):
    return {"customer_id": cid, "period_end": period_end, "total_amount_gbp": total}


def test_dd_smoothing_balance_empty():
    assert dd_smoothing_balance_at_closure([]) == 0.0


def test_dd_smoothing_balance_first_bill_no_history_is_zero():
    bills = [bill("C1", "2020-01-31", 100.0)]
    assert dd_smoothing_balance_at_closure(bills) == 0.0


def test_dd_smoothing_balance_positive_when_consumption_falls():
    # Flat DD stays anchored to an earlier higher trailing mean while actual
    # bills fall (e.g. moving into summer) -- customer overpays via DD.
    bills = [
        bill("C1", "2020-01-31", 200.0),
        bill("C1", "2020-02-29", 200.0),
        bill("C1", "2020-03-31", 50.0),
    ]
    balance = dd_smoothing_balance_at_closure(bills)
    assert balance > 0


def test_dd_smoothing_balance_negative_when_consumption_rises():
    bills = [
        bill("C1", "2020-01-31", 50.0),
        bill("C1", "2020-02-29", 50.0),
        bill("C1", "2020-03-31", 200.0),
    ]
    balance = dd_smoothing_balance_at_closure(bills)
    assert balance < 0


def test_generate_log_skips_non_churned_customers():
    bills = [
        bill("C1", "2020-01-31", 200.0),
        bill("C1", "2020-02-28", 50.0),
    ]
    log = generate_credit_refund_log(bills, {"C1": "resi"}, churned_ids=set())
    assert log == []


def test_generate_log_skips_non_dd_segments():
    bills = [
        bill("C_IC1", "2020-01-31", 20000.0),
        bill("C_IC1", "2020-02-28", 5000.0),
    ]
    log = generate_credit_refund_log(bills, {"C_IC1": "ic"}, churned_ids={"C_IC1"})
    assert log == []


def test_generate_log_fires_for_churned_dd_customer_with_credit():
    bills = [
        bill("C1", "2020-01-31", 200.0),
        bill("C1", "2020-02-29", 200.0),
        bill("C1", "2020-03-31", 50.0),
    ]
    log = generate_credit_refund_log(bills, {"C1": "resi"}, churned_ids={"C1"})
    assert len(log) == 1
    entry = log[0]
    assert entry["customer_id"] == "C1"
    assert entry["trigger"] == "account_closure"
    assert entry["credit_amount_gbp"] > 0
    assert entry["paid_date"] >= entry["request_date"]
    assert isinstance(entry["breached_slc14_deadline"], bool)


def test_generate_log_skips_churned_customer_with_debit_balance():
    bills = [
        bill("C1", "2020-01-31", 50.0),
        bill("C1", "2020-02-29", 200.0),
    ]
    log = generate_credit_refund_log(bills, {"C1": "resi"}, churned_ids={"C1"})
    assert log == []


def test_on_time_and_late_windows_dont_overlap():
    assert ON_TIME_WORKING_DAYS[1] < LATE_WORKING_DAYS[0]


def test_generate_log_deterministic():
    bills = [
        bill("C1", "2020-01-31", 200.0),
        bill("C1", "2020-02-29", 200.0),
        bill("C1", "2020-03-31", 50.0),
    ]
    log1 = generate_credit_refund_log(bills, {"C1": "resi"}, churned_ids={"C1"})
    log2 = generate_credit_refund_log(bills, {"C1": "resi"}, churned_ids={"C1"})
    assert log1 == log2
