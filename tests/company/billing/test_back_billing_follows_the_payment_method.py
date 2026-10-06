"""The back-billing limit bars the quantity the payment method makes recoverable.

SLC 21BA bars a charge recovery action for energy used more than 12 months before it. For a
customer who pays each bill, the bill is the demand; for direct debit the debit is, and "a direct
debit statement is not charge recovery action" (Energy Ombudsman). So the estimate error is the
barred quantity only for pay-on-bill; for direct debit it is the old collection shortfall.
Scenarios A and B are the Ombudsman's, as written in docs/market_research/back_billing_and_liability.md.
"""
from __future__ import annotations

import datetime as dt

from company.billing.back_billing import (
    BackBillingAssessment,
    BackBillingReason,
    RecoveryPeriod,
    barred_unrecovered_gbp,
)
from company.billing.monthly_bill_assembly import (
    BASIS_DD_AT_RECOVERY_ACTION,
    BASIS_DD_SHORTFALL,
    BASIS_ESTIMATE_ERROR,
    _resolve_catchup,
)
from company.compliance.domain_invariants import check_back_billing_cap_respected

DEMAND = "2024-06-01"


def _months(n: int, start=(2023, 1)) -> list[tuple[str, str]]:
    y, m = start
    out = []
    for _ in range(n):
        s = dt.date(y, m, 1)
        m += 1
        if m > 12:
            y, m = y + 1, 1
        out.append((s.isoformat(), dt.date(y, m, 1).isoformat()))
    return out


def _run(true_gbp: float, billed_gbp: float, collected_gbp: float | None) -> list[dict]:
    """Seventeen monthly periods ending at the demand date."""
    run = []
    for start, end in _months(17):
        p = {
            "period_start": start,
            "period_end": end,
            "true_total_amount_gbp": true_gbp,
            "total_amount_gbp": billed_gbp,
            "billed_kwh": billed_gbp * 4,
            "used_kwh": true_gbp * 4,
        }
        if collected_gbp is not None:
            p["recovered_gbp"] = collected_gbp
        run.append(p)
    assert run[-1]["period_end"] == DEMAND
    return run


def _bill(catchup: dict) -> dict:
    """The fields the assembly stamps on a material catch-up bill, as the invariant reads them."""
    bill = {
        "customer_id": "C1",
        "segment": "resi",
        "period_end": DEMAND,
        "catchup_applied": True,
        "catchup_period_start": catchup["period_start"],
        "catchup_period_end": catchup["period_end"],
        "catchup_direction": catchup["direction"],
        "catchup_raw_delta_gbp": catchup["raw_delta_gbp"],
        "catchup_written_off_gbp": catchup["written_off_gbp"],
        "catchup_back_billing_basis": catchup["back_billing_basis"],
    }
    if "recovery_periods" in catchup:
        bill["catchup_recovery_periods"] = catchup["recovery_periods"]
    return bill


def test_scenario_a_accurate_bills_on_a_short_direct_debit_lose_the_shortfall_older_than_12_months():
    """The defect: with nothing to correct in the estimate, the old comparator wrote off nothing,
    though the debit took £10 a month less than the bills for 17 months. The shortfall from the
    five-plus months before the window is lost; the recent shortfall is still recoverable."""
    catchup = _resolve_catchup("C1", "resi", _run(50.0, 50.0, 40.0), DEMAND, "direct_debit")
    assert catchup["back_billing_basis"] == BASIS_DD_SHORTFALL
    assert catchup["raw_delta_gbp"] == 0.0
    # 2023-01..05 wholly before the window (2023-06-02), plus one day of June 2023.
    assert catchup["written_off_gbp"] == round(50.0 + 10.0 * 1 / 30, 2)
    assert catchup["back_billing_cap_applied"] is True
    assert catchup["write_off_adjustment_id"].startswith("ADJ-BB-C1-")
    assert check_back_billing_cap_respected(_bill(catchup)) is True
    # The same run on the estimate comparator bars nothing: that was the miss.
    assert _resolve_catchup("C1", "resi", _run(50.0, 50.0, 40.0), DEMAND)["written_off_gbp"] == 0.0


def test_scenario_b_no_bills_but_a_direct_debit_that_covered_the_use_has_nothing_barred():
    """The defect: bills far below the truth for 17 months made the old comparator write off the
    old part of the estimate error, though the debit (£50) more than covered the use. Back-billing
    "is not intended to refund customers' payments made for energy that they have used"."""
    true_monthly = 50.0 - 7.43 / 17  # the Ombudsman's £7.43 credit when billing resumes
    catchup = _resolve_catchup("C1", "resi", _run(true_monthly, 10.0, 50.0), DEMAND, "direct_debit")
    assert catchup["back_billing_basis"] == BASIS_DD_SHORTFALL
    assert catchup["raw_delta_gbp"] > 0
    assert catchup["written_off_gbp"] == 0.0
    assert catchup["chargeable_gbp"] == catchup["raw_delta_gbp"]
    assert check_back_billing_cap_respected(_bill(catchup)) is True
    # The estimate comparator on the same run writes off money that is not owed.
    assert _resolve_catchup("C1", "resi", _run(true_monthly, 10.0, 50.0), DEMAND)["written_off_gbp"] > 0


def test_a_pay_on_bill_catch_up_keeps_true_use_against_billed():
    run = _run(50.0, 30.0, None)
    catchup = _resolve_catchup("C1", "resi", run, DEMAND, "standard_credit")
    expected = BackBillingAssessment(
        account_id="C1",
        billing_date=dt.date(2024, 6, 1),
        consumption_period_start=dt.date(2023, 1, 1),
        consumption_period_end=dt.date(2024, 6, 1),
        billed_amount_gbp=catchup["raw_delta_gbp"],
        reason=BackBillingReason.ESTIMATED_READ_CORRECTED,
    ).written_off_gbp
    assert catchup["back_billing_basis"] == BASIS_ESTIMATE_ERROR
    assert catchup["written_off_gbp"] == expected > 0
    assert _resolve_catchup("C1", "resi", run, DEMAND)["written_off_gbp"] == expected


def test_a_direct_debit_catch_up_without_its_collections_writes_nothing_off_because_a_statement_is_not_a_demand():
    """The defect: the estimate error was written off on the statement, and the balance book bars
    the same account's old shortfall at the final bill, so booking both takes it twice."""
    catchup = _resolve_catchup("C1", "resi", _run(50.0, 30.0, None), DEMAND, "direct_debit")
    assert catchup["back_billing_basis"] == BASIS_DD_AT_RECOVERY_ACTION
    assert catchup["written_off_gbp"] == 0.0
    assert catchup["chargeable_gbp"] == catchup["raw_delta_gbp"] > 0
    assert catchup["barred_kwh"] is None
    # The same run on pay-on-bill is barred, so the zero above is the payment method's doing.
    assert _resolve_catchup("C1", "resi", _run(50.0, 30.0, None), DEMAND)["written_off_gbp"] > 0


def test_the_invariant_refuses_a_write_off_on_a_direct_debit_statement():
    bill = _bill(_resolve_catchup("C1", "resi", _run(50.0, 30.0, None), DEMAND, "direct_debit"))
    assert check_back_billing_cap_respected(bill) is True
    assert check_back_billing_cap_respected({**bill, "catchup_written_off_gbp": 12.0}) is False


def test_every_comparator_basis_is_reachable():
    """Partition control: a selector that always answered one basis would pass the tests above
    that only check one leg each."""
    reached = {
        _resolve_catchup("C1", "resi", _run(50.0, 30.0, 40.0), DEMAND, ch)["back_billing_basis"]
        for ch in ("direct_debit", "standard_credit", None)
    } | {_resolve_catchup("C1", "resi", _run(50.0, 30.0, None), DEMAND, "direct_debit")[
        "back_billing_basis"]}
    assert reached == {BASIS_DD_SHORTFALL, BASIS_ESTIMATE_ERROR, BASIS_DD_AT_RECOVERY_ACTION}


def test_the_invariant_holds_a_direct_debit_catch_up_to_the_collection_shortfall():
    """The old invariant re-derived the estimate comparator, so it passed a Scenario A bill that
    wrote off nothing. It now refuses one that under-writes-off, and fails closed without periods."""
    bill = _bill(_resolve_catchup("C1", "resi", _run(50.0, 50.0, 40.0), DEMAND, "direct_debit"))
    assert check_back_billing_cap_respected(bill) is True
    assert check_back_billing_cap_respected({**bill, "catchup_written_off_gbp": 0.0}) is False
    no_periods = {k: v for k, v in bill.items() if k != "catchup_recovery_periods"}
    assert check_back_billing_cap_respected(no_periods) is False
    broken = {**bill, "catchup_recovery_periods": [{"period_start": "x"}]}
    assert check_back_billing_cap_respected(broken) is False


def test_shortfall_recovered_by_later_overpayment_is_not_barred():
    """Capped at what is still unrecovered: an old shortfall the debit later made good is gone."""
    periods = [
        RecoveryPeriod(dt.date(2023, 1, 1), dt.date(2023, 2, 1), 100.0, 0.0),
        RecoveryPeriod(dt.date(2024, 4, 1), dt.date(2024, 5, 1), 0.0, 90.0),
    ]
    assert barred_unrecovered_gbp(periods, dt.date(2024, 6, 1)) == 10.0


def test_the_microbusiness_limit_starts_on_1_november_2018_not_1_may():
    """The defect: the domestic start date was applied to microbusinesses."""
    def assess(billing_date, **kw):
        return BackBillingAssessment(
            account_id="M1",
            billing_date=billing_date,
            consumption_period_start=dt.date(2016, 1, 1),
            consumption_period_end=billing_date,
            billed_amount_gbp=1000.0,
            reason=BackBillingReason.ESTIMATED_READ_CORRECTED,
            **kw,
        )
    august = dt.date(2018, 8, 1)
    assert assess(august, is_domestic=False, is_microbusiness=True).cap_applies is False
    assert assess(august).cap_applies is True
    assert assess(dt.date(2018, 11, 1), is_domestic=False, is_microbusiness=True).cap_applies is True
    old = [RecoveryPeriod(dt.date(2016, 1, 1), dt.date(2016, 2, 1), 100.0, 0.0)]
    assert barred_unrecovered_gbp(old, august, is_domestic=False, is_microbusiness=True) == 0.0
    assert barred_unrecovered_gbp(old, august) == 100.0
