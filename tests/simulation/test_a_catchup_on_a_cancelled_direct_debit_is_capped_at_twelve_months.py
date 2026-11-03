"""N14: a catch-up on a bill the account pays on receipt, because its direct debit had ended, is a
demand, so SLC 21BA caps it at 12 months (docs/market_research/back_billing_and_liability.md s.17).

The seventh cold read found 11 such catch-ups uncapped on the 0a6391d186 book (PROS-2018-0016, bill
of 31 May 2024: 27 estimated months, GBP 25.40 charged, nothing written off, paid on receipt). The
undated feed answered "direct_debit" for every one, so billing deferred the bar to a DD recovery
action that never comes for a DD that has ended.
"""
import pytest

from simulation.household_segments import PaymentChannel, payment_channel_for_customer
from simulation.run_phase4c_on_phase2b import build_monthly_bills, dated_payment_channel
from tests.simulation.test_run_phase4c_on_phase2b import (  # noqa: F401 (fixture)
    _sc_month_records,
    force_estimated_reads,
)

DD_HOME = "C1"


@pytest.fixture
def sixteen_month_run(force_estimated_reads, monkeypatch):  # noqa: F811
    """One actual opening read, then 15 estimates and an actual closing read, use rising, so the
    closing catch-up is an undercharge whose window starts 16 months before the bill."""
    import simulation.meter_reads as mr

    real_read = mr.simulate_read

    def opening_read_actual(customer_id, period_end, meter_type, kwh, *rest, **meter):
        if period_end == "2022-01-31":
            return mr.MeterReadEvent(customer_id=customer_id, period_end=period_end,
                                     meter_type=meter_type, delay_days=0, status="actual",
                                     true_consumption_kwh=kwh, consecutive_estimated_count=0)
        return real_read(customer_id, period_end, meter_type, kwh, *rest, **meter)

    monkeypatch.setattr(mr, "simulate_read", opening_read_actual)
    records = []
    for i in range(16):
        records.extend(_sc_month_records(DD_HOME, 2022 + i // 12, i % 12 + 1, 200.0 + 40.0 * i,
                                         unit_rate=200.0))
    return records


def test_the_catchup_follows_the_method_in_force_at_its_own_bill(sixteen_month_run):
    """Both arms over one run, so a cap that never runs, or one that runs on every DD account, reds.

    Defect caught: the catch-up read the method the account was set up on (`simulated_payment_
    channel`, undated), so a household whose DD ended mid-run was billed back past 12 months."""
    assert payment_channel_for_customer(DD_HOME) is PaymentChannel.DIRECT_DEBIT

    still_dd = build_monthly_bills(sixteen_month_run, churned_ids={DD_HOME},
                                   payment_channel_at_feed=dated_payment_channel({}))[-1]
    assert still_dd["catchup_direction"] == "undercharge"
    assert still_dd["catchup_back_billing_basis"] == (
        "direct_debit_barred_at_the_charge_recovery_action")
    assert still_dd["catchup_written_off_gbp"] == 0.0

    # The supplier's own record: the last bill presented by DD was June 2022's, and no mandate since.
    ended = dated_payment_channel({DD_HOME: [("2022-06-30", None)]})
    on_receipt = build_monthly_bills(sixteen_month_run, churned_ids={DD_HOME},
                                     payment_channel_at_feed=ended)[-1]
    assert on_receipt["catchup_direction"] == "undercharge"
    assert on_receipt["catchup_back_billing_basis"] == "pay_on_bill_true_vs_billed"
    assert on_receipt["catchup_back_billing_cap_applied"] is True
    assert on_receipt["catchup_written_off_gbp"] > 0


def test_the_dated_answer_is_the_ledgers_key():
    """The spell bounds are the ones `arrears_engine.paying_method` gives the ledger: off after the
    last bill presented by DD, on again from the bill after a re-mandate. Defect caught: an
    off-by-one that disagrees with the ledger on the bill either side of a stop."""
    at = dated_payment_channel({DD_HOME: [("2022-06-30", "2022-09-30")]})
    home = {"customer_id": DD_HOME, "segment": "resi", "commodity": "electricity"}
    assert [at(home, d) for d in ("2022-06-30", "2022-07-31", "2022-09-30", "2022-10-31")] == [
        "direct_debit", "standard_credit", "standard_credit", "direct_debit"]


def test_the_second_pass_rebills_only_the_account_whose_dd_ended(sixteen_month_run, monkeypatch):
    """The published run's splice: C1's DD ended, C2's did not. Defect caught: a second pass that
    leaves the first-pass catch-up in place, rebills the whole book, or lets bills and read events
    fall out of step (the read log is projected one event per bill)."""
    import simulation.dd_collection_book as dcb
    from simulation.run_phase4c_on_phase2b import rebill_catchups_off_direct_debit

    other = [dict(r, customer_id="C2") for r in sixteen_month_run]
    records = sixteen_month_run + other
    events: list = []
    first = build_monthly_bills(records, churned_ids={"C1", "C2"}, read_events_out=events)
    monkeypatch.setattr(dcb, "supplier_dd_spells",
                        lambda bills, behavioral, seed=42: {"C1": [("2022-06-30", None)]})

    bills, out_events = rebill_catchups_off_direct_debit(
        records, first, events, {}, churned_ids={"C1", "C2"})

    assert len(bills) == len(out_events) == len(first)
    assert all(e.customer_id == b["customer_id"] for b, e in zip(bills, out_events))
    assert [b for b in bills if b["customer_id"] == "C2"] == [
        b for b in first if b["customer_id"] == "C2"]
    c1 = [b for b in bills if b["customer_id"] == "C1"][-1]
    assert c1["catchup_back_billing_basis"] == "pay_on_bill_true_vs_billed"
    assert c1["catchup_written_off_gbp"] > 0
