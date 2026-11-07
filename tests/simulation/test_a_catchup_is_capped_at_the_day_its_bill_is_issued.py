"""SLC 21BA.1 bars energy used more than 12 months before "the date the charge recovery action was
taken" (docs/market_research/back_billing_and_liability.md s.1 and s.17). For a bill paid on
receipt that date is the day the bill is issued, not the last day of the month it charges.

The b3ce2a4e73 book held 5 pay-on-receipt catch-ups whose window started 366-583 days before the bill
was issued and exactly 365 before its period end, so none was capped. SYN-2016-048 is one of them:
its Jan 2025 bill was issued 2025-02-07 and its catch-up window opened 2024-02-01.
"""
from datetime import timedelta

import pytest

from company.compliance.domain_invariants import check_back_billing_cap_respected
from simulation.arrears_engine import PAYMENT_TERMS_DAYS, bill_due_date
from simulation.run_phase4c_on_phase2b import (
    build_monthly_bills,
    dated_payment_channel,
    simulated_bill_issue_date,
)
from tests.simulation.test_run_phase4c_on_phase2b import (  # noqa: F401 (fixture)
    _sc_month_records,
    force_estimated_reads,
)

HOME = "SYN-2016-048"


@pytest.fixture
def thirteen_month_run(force_estimated_reads, monkeypatch):  # noqa: F811
    """An actual read on 31 Jan 2024, twelve estimates, and an actual closing read on 31 Jan 2025,
    use rising, so the closing catch-up is an undercharge whose window opens 1 Feb 2024: 365 days
    before the period end, 372 before the day the ledger issues the bill."""
    import simulation.meter_reads as mr

    real_read = mr.simulate_read

    def opening_read_actual(customer_id, period_end, meter_type, kwh, *rest, **meter):
        if period_end == "2024-01-31":
            return mr.MeterReadEvent(customer_id=customer_id, period_end=period_end,
                                     meter_type=meter_type, delay_days=0, status="actual",
                                     true_consumption_kwh=kwh, consecutive_estimated_count=0)
        return real_read(customer_id, period_end, meter_type, kwh, *rest, **meter)

    monkeypatch.setattr(mr, "simulate_read", opening_read_actual)
    records = []
    for i in range(13):
        records.extend(_sc_month_records(HOME, 2024 + i // 12, i % 12 + 1, 200.0 + 40.0 * i,
                                         unit_rate=200.0))
    return records


def test_the_issue_date_is_the_ledgers():
    """Defect caught: billing and the ledger keeping two issue dates, so the cap is tested on a day
    the customer never received the bill."""
    assert simulated_bill_issue_date(HOME, "2025-01-31") == "2025-02-07"
    for cid, period_end in ((HOME, "2025-01-31"), ("C1", "2022-03-31"), ("SYN-2016-307g", "2019-03-31")):
        assert simulated_bill_issue_date(cid, period_end) == (
            bill_due_date(cid, period_end) - timedelta(days=PAYMENT_TERMS_DAYS)).isoformat()


def test_a_window_inside_twelve_months_of_the_period_end_but_not_of_the_issue_is_capped(
        thirteen_month_run):
    """Both arms over one run: dated at the period end the window is inside the line and nothing is
    barred; dated at the issue the first week of Feb 2024 is outside it. A cap that never runs, or one
    keyed to the period end, reds.

    Defect caught: `_resolve_catchup` was handed `bill["period_end"]` as the billing date."""
    on_receipt = dated_payment_channel({HOME: [("2023-12-31", None)]})
    at_period_end = build_monthly_bills(
        thirteen_month_run, churned_ids={HOME}, payment_channel_at_feed=on_receipt,
        bill_issue_date_feed=lambda cid, period_end: period_end)[-1]
    issued = build_monthly_bills(thirteen_month_run, churned_ids={HOME},
                                 payment_channel_at_feed=on_receipt)[-1]

    for bill in (at_period_end, issued):
        assert bill["period_end"] == "2025-01-31"
        assert bill["catchup_direction"] == "undercharge"
        assert bill["catchup_period_start"] == "2024-02-01"
        assert bill["catchup_back_billing_basis"] == "pay_on_bill_true_vs_billed"
    assert at_period_end["catchup_back_billing_cap_applied"] is False
    assert at_period_end["catchup_written_off_gbp"] == 0.0
    assert issued["catchup_back_billing_cap_applied"] is True
    assert issued["catchup_written_off_gbp"] > 0
    # The pre-bill gate re-derives the write-off at the stamped day. On this bill a period-end
    # re-derivation would also pass (no cap there, so nothing to compare): the control that reds on a
    # gate dated at the period end is test_the_desk_is_asked_the_capped_catchup_the_page_prints.py,
    # whose 16-month write-off differs in size by the issue delay and was held.
    assert issued["catchup_billing_date"] == "2025-02-07"
    assert check_back_billing_cap_respected(issued)
