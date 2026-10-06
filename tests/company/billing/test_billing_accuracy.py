"""D48 slice 1: billed against what the reads later showed, by kind (K2 true-up, K3 barred).

The bills come from the company's own `build_monthly_bills`, driven by a scripted read feed, so
these tests import nothing from the world. The estimate is scripted at a flat 200 kWh a month while
use climbs, so the closing read is an undercharge, and a run of 14 estimates outlasts the 12-month
limit.
"""

from __future__ import annotations

import calendar
import datetime as dt
from dataclasses import dataclass

import pytest

from company.billing.billing_accuracy import (
    PUBLISHED_MEDIAN_SUPPLIER_SHARE_NO_READ_BILL_IN_12,
    account_billing_accuracy,
    billing_accuracy_summary,
    direct_debit_money_line,
    estimated_billing_outstanding_grade,
    published_view,
)
from company.billing.monthly_bill_assembly import build_monthly_bills

FLAT_ESTIMATE_KWH = 200.0
MONTHS = 16


@pytest.fixture(autouse=True)
def _a_flat_estimate_is_billed(monkeypatch):
    """These tests grade the MEASURE, so a flat scripted estimate is their instrument. The company
    makes its own estimate (slices 3-4; the feed reports status only), so the script replaces the
    company's estimator here. The estimator has its own tests."""
    def flat(*_args):
        return FLAT_ESTIMATE_KWH
    monkeypatch.setattr("company.billing.monthly_bill_assembly.estimate_unread_kwh", flat)
    monkeypatch.setattr("company.billing.monthly_bill_assembly.opening_estimate_kwh", flat)


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

    def read_for(self, customer_id, period_end, meter_type, true_kwh, consecutive):
        if period_end.startswith("2022-01") or self.actual_after_opening:
            return _Read("actual", None, 0)
        return _Read("estimated", None, consecutive + 1)

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
    assert set(summary["kinds"]) == {"K1", "K2", "K3"}
    assert elec["accounts"] == 1 and elec["snapshot_accounts"] == 1
    assert elec["snapshot_no_read_bill_in_12"] == 0
    assert elec["K2_estimated_share_of_billed_kwh"] == pytest.approx(
        elec["estimated_kwh"] / elec["billed_kwh"])
    assert 0 < elec["K3_barred_share_of_undercharge_kwh"] < 1

    actual = billing_accuracy_summary(_bills(actual_after_opening=True))["by_fuel"]["electricity"]
    assert actual["K3_barred_share_of_undercharge_kwh"] is None



# --- K1: the ledger's billed-on-estimate position, graded (slice 2) -----------------------------

#: Per account: its monthly use, and the months (index from Jan 2022) its read is actual.
#: MATERIAL closes a climbing run in July (a material undercharge); IMMATERIAL closes a run half a
#: kWh a month out in April (under the threshold); OPEN is unread over the 2022 year end and read
#: in March 2023; NEVER is never read after January. The ids are the company registry's own.
MATERIAL, IMMATERIAL, OPEN, NEVER = "C1", "C2", "C3", "C4"
_K1_ACCOUNTS = {
    MATERIAL: (_use, {0} | set(range(6, MONTHS))),
    IMMATERIAL: (lambda i: FLAT_ESTIMATE_KWH + 0.5, {0} | set(range(3, MONTHS))),
    OPEN: (_use, {0, 14, 15}),
    NEVER: (_use, {0}),
}


class _PerAccountFeed(_ScriptedFeed):
    def __init__(self):
        super().__init__(actual_after_opening=False)

    def read_for(self, customer_id, period_end, meter_type, true_kwh, consecutive):
        year, month = int(period_end[:4]), int(period_end[5:7])
        if (year - 2022) * 12 + month - 1 in _K1_ACCOUNTS[customer_id][1]:
            return _Read("actual", None, 0)
        return _Read("estimated", None, consecutive + 1)


def _k1_bills():
    records = []
    for cid, (use, _) in _K1_ACCOUNTS.items():
        for i in range(MONTHS):
            records.extend(_month_records(cid, 2022 + i // 12, i % 12 + 1, use(i)))
    return build_monthly_bills(records, _PerAccountFeed())


def test_the_k1_grade_takes_every_branch_and_each_holds_the_account_it_should():
    """Defect caught: a grade that puts every uncovered estimate in one bucket. All four branches
    are asserted reachable in one statement before what each holds."""
    bills = _k1_bills()
    grade = estimated_billing_outstanding_grade(bills, "2022-12")
    assert (grade["closed_immaterial_bills"] and grade["graded_runs"]
            and grade["never_read_runs"] and grade["open_runs"]), grade

    by = {cid: [b for b in bills if b["customer_id"] == cid and b["period_end"] < "2023-01"]
          for cid in _K1_ACCOUNTS}
    est = {cid: [b for b in bs if b["billing_basis"] == "estimated"] for cid, bs in by.items()}
    assert any(b.get("catchup_applied") for b in by[MATERIAL])
    assert not any(b.get("catchup_applied") for b in by[IMMATERIAL])
    assert grade["closed_immaterial_bills"] == len(est[IMMATERIAL]) == 2
    assert grade["closed_immaterial_gbp"] == pytest.approx(
        sum(b["total_amount_gbp"] for b in est[IMMATERIAL]))
    assert (grade["open_runs"], grade["graded_runs"], grade["never_read_runs"]) == (2, 1, 1)
    assert grade["open_bills"] == len(est[OPEN]) + len(est[NEVER]) == 22
    assert grade["never_read_kwh"] == pytest.approx(FLAT_ESTIMATE_KWH * 11)

    # OPEN's run is graded by its March 2023 read: the whole run Feb 2022 - Feb 2023, not the
    # eleven bills billed by the year end.
    closing = next(b for b in bills if b["customer_id"] == OPEN and "read_true_up_kwh" in b)
    assert closing["period_end"].startswith("2023-03")
    assert grade["graded_run_billed_kwh"] == pytest.approx(FLAT_ESTIMATE_KWH * 13)
    assert grade["graded_run_true_up_kwh"] == pytest.approx(
        sum(_use(i) for i in range(1, 14)) - FLAT_ESTIMATE_KWH * 13)
    assert grade["graded_net_true_up_share"] == pytest.approx(
        grade["graded_run_true_up_kwh"] / grade["graded_run_billed_kwh"])


def test_the_k1_grade_partitions_exactly_what_the_ledger_carries():
    """The grade reads the position `saas.ledger.estimated_billing_outstanding` carries; it does
    not restate it. Defect caught: the ledger counting an estimate a read has already ended with an
    immaterial correction (it did until 2026-10-05, 83% of the decade run's figure), or the grade
    drifting from the ledger's rule. At the last billed month both read the same bills."""
    from saas.ledger import estimated_billing_outstanding

    bills = _k1_bills()
    ledger = estimated_billing_outstanding(bills)
    grade = estimated_billing_outstanding_grade(bills)
    assert grade["as_of"] == "2023-04"
    assert grade["outstanding_bills"] == ledger["outstanding_bill_count"]
    assert grade["outstanding_gbp"] == pytest.approx(ledger["estimated_billing_outstanding_gbp"],
                                                     abs=0.01)
    # The book holds an immaterially closed run, so the equality above can tell the two rules apart.
    assert grade["closed_immaterial_bills"] == 2


def test_the_year_end_grades_are_in_the_summary():
    summary = billing_accuracy_summary(_k1_bills())
    assert [g["as_of"] for g in summary["K1_year_end_grades"]["electricity"]] == ["2022-12"]
    assert summary["K1_year_end_grades"]["electricity"][0] == estimated_billing_outstanding_grade(
        _k1_bills(), "2022-12")


def _snapshot_summary(unread: int, accounts: int) -> dict:
    summary = billing_accuracy_summary(_bills(actual_after_opening=False))
    fuel = summary["by_fuel"]["electricity"]
    fuel["snapshot_accounts"], fuel["snapshot_no_read_bill_in_12"] = accounts, unread
    fuel["K2_snapshot_share_no_read_bill_in_12"] = unread / accounts if accounts else None
    return summary


def test_the_published_snapshot_takes_every_verdict_and_its_interval_holds_the_share():
    """The partition first: a view that always said "cannot be told apart" would pass every leg
    below. 0 of 2000 sits under the published band, 400 of 2000 over it, 2 of 48 (the decade
    capture's electricity) straddles it."""
    verdicts = {}
    for unread, accounts in ((0, 2000), (400, 2000), (2, 48), (0, 0)):
        snap = published_view(_snapshot_summary(unread, accounts))["by_fuel"]["electricity"]["snapshot"]
        verdicts[(unread, accounts)] = snap["against_published"]
        if accounts:
            assert snap["ci95"][0] <= snap["share"] <= snap["ci95"][1]
        else:
            assert snap["ci95"] is None and snap["share"] is None
    assert verdicts == {
        (0, 2000): "fewer_unread_than_the_median_supplier",
        (400, 2000): "more_unread_than_the_median_supplier",
        (2, 48): "cannot_be_told_apart_from_the_median_supplier",
        (0, 0): "no_accounts",
    }


def test_the_published_comparator_is_the_share_without_a_read_bill():
    assert [round(x, 4) for x in sorted(PUBLISHED_MEDIAN_SUPPLIER_SHARE_NO_READ_BILL_IN_12)] == [
        0.052, 0.056]


def test_a_missing_measure_is_published_as_an_absence_with_its_reason_and_no_figures():
    for missing in (None, {}, {"by_fuel": {}}):
        view = published_view(missing, "run_output_x.json")
        assert view["available"] is False and view["reason"] and "by_fuel" not in view


def test_the_published_example_is_the_account_with_the_most_barred_energy():
    view = published_view(billing_accuracy_summary(
        _bills(actual_after_opening=False) + [dict(b, customer_id="C2")
                                              for b in _bills(actual_after_opening=True)]))
    assert view["available"] is True
    assert view["example_account"]["account_id"] == "C1"
    assert view["example_account"]["barred_kwh"] > 0
    assert view["by_fuel"]["electricity"]["K1_year_end_grades"] == [
        {k: g[k] for k in ("as_of", "outstanding_gbp", "outstanding_bills", "graded_runs",
                           "never_read_runs", "graded_net_true_up_share",
                           "graded_gross_true_up_share")}
        for g in billing_accuracy_summary(
            _bills(actual_after_opening=False) + [dict(b, customer_id="C2") for b in
                                                  _bills(actual_after_opening=True)]
        )["K1_year_end_grades"]["electricity"]]


# The DD balance book's per-account rows, in the shape `simulation/dd_balance_book` writes: two
# accounts that left (one barred, one not), one still open with an exposure.
_DD_ROWS = [
    {"customer_id": "D1", "closed": True, "met_recovery_action": True, "barred_gbp": 300.0,
     "exposure_gbp": 0.0},
    {"customer_id": "D2", "closed": True, "met_recovery_action": True, "barred_gbp": 0.0,
     "exposure_gbp": 0.0},
    {"customer_id": "D3", "closed": False, "met_recovery_action": False, "barred_gbp": 0.0,
     "exposure_gbp": 120.0},
]


def test_the_dd_money_line_is_never_folded_into_k3():
    """K3 is pay-on-bill energy. The DD bar is money a debit could not ask for. Supplying the line
    must leave every K-figure, measured and published, exactly as it was."""
    bills = _bills(actual_after_opening=False)
    line = direct_debit_money_line(_DD_ROWS)
    without, with_line = billing_accuracy_summary(bills), billing_accuracy_summary(bills, line)
    assert with_line["by_fuel"] == without["by_fuel"]
    assert with_line["by_fuel"]["electricity"]["barred_kwh"] > 0  # K3 itself is non-trivial here
    assert published_view(with_line)["by_fuel"] == published_view(without)["by_fuel"]
    assert published_view(with_line)["direct_debit_money_line"]["barred_gbp"] == 300.0
    assert "DD" not in with_line["kinds"] and not any(
        "gbp" in k for k in with_line["by_fuel"]["electricity"])


def test_the_dd_money_line_is_bounded_over_the_accounts_that_met_a_recovery_action():
    line = direct_debit_money_line(_DD_ROWS, unmeasured_accounts=2)
    # Every leg of the partition is taken: barred, met-and-not-barred, open with an exposure.
    assert (line["accounts_barred"], line["accounts_met_recovery_action"], line["open_accounts"]) \
        == (1, 2, 1)
    assert line["barred_gbp"] == 300.0 and line["open_exposure_gbp"] == 120.0
    assert line["dd_accounts"] == 3 and line["unmeasured_accounts"] == 2
    low, high = line["share_barred_ci95"]
    assert low < line["share_barred"] == 0.5 < high
    low, high = line["mean_barred_gbp_ci95"]
    assert low <= line["mean_barred_gbp"] == 150.0 < high


def test_a_missing_dd_money_line_is_an_absence_with_its_reason_never_a_zero():
    for summary in (billing_accuracy_summary(_bills(actual_after_opening=False)),
                    dict(billing_accuracy_summary(_bills(actual_after_opening=False)),
                         direct_debit_money_line=None)):
        line = published_view(summary)["direct_debit_money_line"]
        assert line["available"] is False and line["reason"] and "barred_gbp" not in line
