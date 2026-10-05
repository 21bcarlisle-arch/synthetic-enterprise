"""D48 slice 1: billed against what the reads later showed, by kind (K2 true-up, K3 barred).

The bills come from the company's own `build_monthly_bills`, driven by a scripted read feed, so
these tests import nothing from the world. The feed estimates a flat 200 kWh a month while use
climbs, so the closing read is an undercharge, and a run of 14 estimates outlasts the 12-month
limit.
"""

from __future__ import annotations

import calendar
import datetime as dt
from dataclasses import dataclass

import pytest

from company.billing.billing_accuracy import (
    account_billing_accuracy,
    billing_accuracy_summary,
)
from company.billing.monthly_bill_assembly import build_monthly_bills

FLAT_ESTIMATE_KWH = 200.0
MONTHS = 16


def _use(i: int) -> float:
    return 200.0 + 40.0 * i


def _month_records(cid, year, month, kwh, unit_rate=200.0, sc_per_day=0.50):
    days = calendar.monthrange(year, month)[1]
    return [{
        "customer_id": cid,
        "settlement_date": f"{year}-{month:02d}-{d:02d}",
        "settlement_period": 1,
        "consumption_kwh": kwh / days,
        "unit_rate_gbp_per_mwh": unit_rate,
        "revenue_gbp": (kwh / days / 1000) * unit_rate + sc_per_day,
        "standing_charge_gbp": sc_per_day,
        "wholesale_cost_gbp": 0.0,
        "margin_gbp": 0.0,
    } for d in range(1, days + 1)]


def _records(cid="C1"):
    out = []
    for i in range(MONTHS):
        out.extend(_month_records(cid, 2022 + i // 12, i % 12 + 1, _use(i)))
    return out


@dataclass
class _Read:
    status: str
    estimated_consumption_kwh: float | None
    consecutive_estimated_count: int


class _ScriptedFeed:
    """An actual read in the opening month; after that, `actual_after_opening` decides."""

    def __init__(self, actual_after_opening: bool):
        self.actual_after_opening = actual_after_opening

    def meter_type_for(self, customer):
        return "traditional"

    def read_for(self, customer_id, period_end, meter_type, true_kwh, trailing, consecutive,
                 trailing_days=None, period_days=None):
        if period_end.startswith("2022-01") or self.actual_after_opening:
            return _Read("actual", None, 0)
        return _Read("estimated", FLAT_ESTIMATE_KWH, consecutive + 1)

    def final_read_for(self, customer_id, period_end, meter_type, true_kwh):
        return _Read("actual", None, 0)


def _bills(actual_after_opening: bool, closed: bool = True):
    return build_monthly_bills(
        _records(), _ScriptedFeed(actual_after_opening),
        churned_ids={"C1"} if closed else None,
    )


def _expected_barred_kwh(true_up_kwh: float) -> float:
    """SLC 21BA by days, restated here from the dates: the run is Feb 2022 - Mar 2023 (14
    estimates), billed on the closing read at 2023-04-30, protected from 2022-04-30."""
    run_start, run_end = dt.date(2022, 2, 1), dt.date(2023, 3, 31)
    protected_start = dt.date(2023, 4, 30) - dt.timedelta(days=365)
    allowed = (run_end - protected_start).days / (run_end - run_start).days
    return true_up_kwh * (1.0 - allowed)


def test_an_estimated_run_is_measured_and_its_barred_energy_is_found_and_none_when_every_read_is_actual():
    """Defect caught: a measure that never sees an estimate. Both arms are asserted in one
    statement, so a measure that reports zero everywhere fails it, and so does one that reports
    the same figure whatever the reads were."""
    estimating = account_billing_accuracy(_bills(actual_after_opening=False))[0]
    every_read_actual = account_billing_accuracy(_bills(actual_after_opening=True))[0]

    assert (estimating["estimated_kwh"] > 0 and estimating["barred_kwh"] > 0
            and every_read_actual["estimated_kwh"] == 0 and every_read_actual["barred_kwh"] == 0
            and every_read_actual["true_ups"] == 0), (estimating, every_read_actual)

    billed_on_estimates = FLAT_ESTIMATE_KWH * 14
    used_over_run = sum(_use(i) for i in range(1, 15))
    assert estimating["estimated_bills"] == 14
    assert estimating["estimated_kwh"] == pytest.approx(billed_on_estimates)
    assert estimating["true_ups"] == 1
    assert estimating["true_up_kwh"] == pytest.approx(used_over_run - billed_on_estimates)
    assert estimating["undercharge_kwh"] == pytest.approx(estimating["true_up_kwh"])
    assert estimating["barred_kwh"] == pytest.approx(_expected_barred_kwh(estimating["true_up_kwh"]))
    assert estimating["open_estimated_kwh"] == 0
    assert estimating["longest_run_without_read_bill"] == 14
    # The closing bill is on a final read, so at the account's last bill it has had one.
    assert estimating["no_read_bill_in_last_12"] is False
    assert every_read_actual["billed_kwh"] == pytest.approx(sum(_use(i) for i in range(MONTHS)))


def test_a_run_no_read_has_ended_is_open_and_its_true_up_is_not_guessed():
    row = account_billing_accuracy(_bills(actual_after_opening=False, closed=False))[0]
    assert row["true_ups"] == 0 and row["barred_kwh"] == 0
    assert row["open_estimated_kwh"] == pytest.approx(FLAT_ESTIMATE_KWH * (MONTHS - 1))
    assert row["no_read_bill_in_last_12"] is True


def test_the_no_read_snapshot_counts_only_accounts_on_supply_at_the_end():
    """Citizens Advice's measure is a snapshot of accounts on supply. Defect caught: counting a
    leaver, whose last bill is on a forced final read, so the share is flattered. A stayer with
    an open run counts as unread. The leaver, closed two months earlier, is not in the snapshot."""
    feed = _ScriptedFeed(actual_after_opening=False)
    leaver = [r for r in _records("C2") if r["settlement_date"] < "2023-03"]
    bills = build_monthly_bills(_records("C1") + leaver, feed, churned_ids={"C2"})
    summary = billing_accuracy_summary(bills)
    elec = summary["by_fuel"]["electricity"]
    assert summary["snapshot_month"] == "2023-04"
    assert (elec["accounts"], elec["snapshot_accounts"], elec["snapshot_no_read_bill_in_12"]) == (
        2, 1, 1)
    assert elec["K2_snapshot_share_no_read_bill_in_12"] == 1.0


def test_world_truth_on_an_estimated_bill_does_not_move_the_measure():
    """An estimated bill carries `true_consumption_kwh`, the world's use in a month the supplier
    only estimated. Defect caught: the measure reading it. Scrambling it on every estimated bill
    leaves the summary unchanged; the read-time true-up, which the supplier does hold, moves it."""
    bills = _bills(actual_after_opening=False)
    baseline = billing_accuracy_summary(bills)

    scrambled = [dict(b, true_consumption_kwh=b.get("true_consumption_kwh", 0.0) * 7.0 + 1.0)
                 if b["billing_basis"] == "estimated" else b for b in bills]
    assert billing_accuracy_summary(scrambled) == baseline

    moved = [dict(b, read_true_up_kwh=b["read_true_up_kwh"] + 1.0)
             if "read_true_up_kwh" in b else b for b in bills]
    assert billing_accuracy_summary(moved) != baseline


def test_an_immaterial_true_up_is_still_measured():
    """The money correction is not billed below the materiality threshold, but the register moved.
    Defect caught: the energy stamp gated on materiality like the money fields."""
    feed = _ScriptedFeed(actual_after_opening=False)
    records = []
    for i in range(3):
        records.extend(_month_records("C1", 2022, i + 1, FLAT_ESTIMATE_KWH + 0.5))
    closing = build_monthly_bills(records, feed, churned_ids={"C1"})[-1]
    assert "catchup_applied" not in closing
    assert closing["read_true_up_kwh"] == pytest.approx(0.5)


def test_the_summary_totals_by_fuel_and_names_its_shares():
    summary = billing_accuracy_summary(_bills(actual_after_opening=False))
    elec = summary["by_fuel"]["electricity"]
    assert set(summary["kinds"]) == {"K2", "K3"}
    assert elec["accounts"] == 1 and elec["snapshot_accounts"] == 1
    assert elec["snapshot_no_read_bill_in_12"] == 0
    assert elec["K2_estimated_share_of_billed_kwh"] == pytest.approx(
        elec["estimated_kwh"] / elec["billed_kwh"])
    assert 0 < elec["K3_barred_share_of_undercharge_kwh"] < 1

    actual = billing_accuracy_summary(_bills(actual_after_opening=True))["by_fuel"]["electricity"]
    assert actual["K3_barred_share_of_undercharge_kwh"] is None

