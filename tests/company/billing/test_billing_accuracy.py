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
    estimated_share_by_year_and_meter,
    move_out_final_bills,
    published_view,
    unbilled_accrual,
)
from company.billing.monthly_bill_assembly import build_monthly_bills
from company.interfaces.bill_assembly import billing_accuracy as billing_accuracy_door

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

    def final_read_for(self, customer_id, period_end, meter_type, true_kwh, consecutive):
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
    assert set(summary["kinds"]) == {"K1", "K2", "K3", "K1_unbilled"}
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


def _one_run(cid: str, billed: float, true_up: float) -> list[dict]:
    """One estimated December bill and the January read that grades its run."""
    return [
        {"customer_id": cid, "period_end": "2022-12-31", "billing_basis": "estimated",
         "total_amount_gbp": 100.0, "total_consumption_kwh": billed},
        {"customer_id": cid, "period_end": "2023-01-31", "billing_basis": "actual",
         "total_amount_gbp": 100.0, "total_consumption_kwh": billed,
         "read_true_up_kwh": true_up, "read_true_up_billed_kwh": billed},
    ]


def test_the_k1_grade_names_the_run_that_sets_its_net_and_the_net_without_it():
    """Defect caught (2026-10-16): one unread EV home's single read set electricity's K1 net at
    +8% to +12% for fifty month ends and was read as a population bias, because the grade states no
    concentration. Here one run of +100 kWh carries a net of +50 against two runs netting -50: the
    largest run is 200% of the net, and without it the population nets -2.5%."""
    bills = _one_run("C1", 1000.0, 100.0) + _one_run("C2", 1000.0, -20.0) + _one_run(
        "C3", 1000.0, -30.0)
    grade = estimated_billing_outstanding_grade(bills, "2022-12")
    assert grade["graded_runs"] == 3
    assert grade["graded_net_true_up_share"] == pytest.approx(50 / 3000)
    assert grade["graded_largest_run_account"] == "C1"
    assert grade["graded_largest_run_true_up_kwh"] == pytest.approx(100.0)
    assert grade["graded_largest_run_share_of_net"] == pytest.approx(2.0)
    assert grade["graded_net_true_up_share_without_largest_run"] == pytest.approx(-50 / 2000)
    # The largest is by size, not sign: a -100 run is the one named when it is the biggest.
    flipped = estimated_billing_outstanding_grade(
        _one_run("C1", 1000.0, -100.0) + _one_run("C2", 1000.0, 20.0), "2022-12")
    assert flipped["graded_largest_run_account"] == "C1"
    assert flipped["graded_net_true_up_share_without_largest_run"] == pytest.approx(0.02)


def _estimates_then(cid: str, last: dict) -> list[dict]:
    """A read, three estimated months, then `last`: the same run, ended three ways."""
    def bill(period_end, basis, **extra):
        return {"customer_id": cid, "commodity": "electricity", "period_end": period_end,
                "period_start": period_end[:8] + "01",
                "billing_basis": basis, "total_amount_gbp": 50.0, "total_consumption_kwh": 300.0,
                **extra}
    return ([bill("2022-08-31", "actual")]
            + [bill(f"2022-{m}-30", "estimated") for m in ("09", "10", "11")]
            + [bill("2022-12-31", **last)])


def test_an_estimated_final_bill_closes_its_run_and_the_position_holds_only_runs_a_read_can_end():
    """Defect caught (2026-10-24): an account that closed on an estimated final bill was counted as
    awaiting a read for ever. No read will come; the closing estimate is the deemed read it is
    settled on. On run 904a091f7b that was £118,549 of the ledger's £199,366 billed-on-estimate
    position, and 298 of the 348 never-read electricity runs at 2024-12.

    One run of three estimates is ended three ways. All three outcomes are asserted reachable in
    one statement before what each holds: ON_SUPPLY's run is still open, CLOSED_EST closed on an
    estimate (counted beside the position, never in it), CLOSED_READ closed on an actual read."""
    from saas.ledger import estimated_billing_outstanding, estimates_closed_by_final_bill

    on_supply = _estimates_then("ON_SUPPLY", {"basis": "estimated"})
    closed_est = _estimates_then("CLOSED_EST", {"basis": "estimated", "final_bill": True})
    closed_read = _estimates_then("CLOSED_READ", {"basis": "actual", "final_bill": True})
    bills = on_supply + closed_est + closed_read

    grade = estimated_billing_outstanding_grade(bills, "2022-12")
    rows = {r["account_id"]: r for r in account_billing_accuracy(bills)}
    ledger = estimated_billing_outstanding(bills)
    assert (grade["open_runs"] and grade["closed_on_estimated_final_runs"]
            and grade["closed_immaterial_bills"]), grade

    # Each run is four estimates (or three and a read) of 300 kWh at £50.
    assert (grade["open_runs"], grade["open_bills"]) == (1, 4)
    assert (grade["closed_on_estimated_final_runs"],
            grade["closed_on_estimated_final_bills"]) == (1, 4)
    assert grade["closed_on_estimated_final_gbp"] == pytest.approx(200.0)
    assert grade["closed_on_estimated_final_kwh"] == pytest.approx(1200.0)
    assert grade["closed_immaterial_bills"] == 3  # CLOSED_READ's run, ended by its actual final read
    assert grade["never_read_runs"] == 1  # ON_SUPPLY only: a closed account is not "never read"
    assert grade["outstanding_gbp"] == pytest.approx(200.0)

    assert rows["ON_SUPPLY"]["open_estimated_kwh"] == pytest.approx(1200.0)
    assert rows["ON_SUPPLY"]["closed_on_estimated_final_kwh"] == 0.0
    assert rows["CLOSED_EST"]["open_estimated_kwh"] == 0.0
    assert rows["CLOSED_EST"]["closed_on_estimated_final_kwh"] == pytest.approx(1200.0)
    assert rows["CLOSED_READ"]["open_estimated_kwh"] == 0.0
    assert rows["CLOSED_READ"]["closed_on_estimated_final_kwh"] == 0.0

    # The ledger states the same rule once, and the grade agrees with it to the bill.
    assert ledger["outstanding_bill_count"] == grade["outstanding_bills"] == 4
    assert set(ledger["by_customer"]) == {"ON_SUPPLY"}
    assert {b["customer_id"] for b in estimates_closed_by_final_bill(bills)} == {"CLOSED_EST"}
    assert len(estimates_closed_by_final_bill(bills)) == grade["closed_on_estimated_final_bills"]

    # As of a month end before the final bill, the account had not closed: its run is open.
    before_close = estimated_billing_outstanding_grade(closed_est, "2022-11")
    assert (before_close["open_runs"], before_close["closed_on_estimated_final_runs"]) == (1, 0)


def test_a_held_estimated_final_bill_closes_nothing_in_the_accrual():
    """A final bill the pre-bill gate held reached nobody. Defect caught: the final-bill rule,
    read through the shared predicate, dropping a held closing run out of the unbilled accrual."""
    closed_est = _estimates_then("CLOSED_EST", {"basis": "estimated", "final_bill": True})
    held = {("CLOSED_EST", b["period_end"]) for b in closed_est[1:]}
    accrual = unbilled_accrual(closed_est, held, "2022-12", issued_late={})
    assert accrual["by_fuel"]["electricity"]["held_estimates"] == 4
    assert accrual["by_fuel"]["electricity"]["kwh"] == pytest.approx(1200.0)


def test_the_published_k1_is_graded_from_the_bills_so_an_older_run_output_carries_the_figure():
    """Defect caught: the concentration reaching the page only at the next run. A summary whose
    stored K1 predates the field publishes it from the run's own bills; without bills it publishes
    the field as an absence, never a KeyError."""
    bills = _one_run("C1", 1000.0, 100.0) + _one_run("C2", 1000.0, -20.0)
    summary = billing_accuracy_summary(_bills(actual_after_opening=False))
    stale = {k: v for k, v in summary["K1_year_end_grades"]["electricity"][0].items()
             if not k.startswith("graded_largest") and "without" not in k}
    summary["K1_year_end_grades"] = {"electricity": [stale]}
    absent = published_view(summary)["by_fuel"]["electricity"]["K1_year_end_grades"][0]
    assert absent["graded_largest_run_share_of_net"] is None
    graded = published_view(summary, bills=bills)["by_fuel"]["electricity"]["K1_year_end_grades"]
    assert graded[0]["graded_largest_run_account"] == "C1"
    assert graded[0]["graded_largest_run_share_of_net"] == pytest.approx(100 / 80)


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
                           "never_read_runs", "closed_on_estimated_final_gbp",
                           "closed_on_estimated_final_runs", "graded_net_true_up_share",
                           "graded_gross_true_up_share", "graded_largest_run_account",
                           "graded_largest_run_share_of_net",
                           "graded_net_true_up_share_without_largest_run")}
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


def _bill(cid, period_end, basis, kwh, total=100.0, vat=5.0, commodity="electricity", **extra):
    return {"customer_id": cid, "period_end": period_end, "billing_basis": basis,
            "total_consumption_kwh": kwh, "total_amount_gbp": total, "vat_gbp": vat,
            "commodity": commodity, **extra}


def test_the_unbilled_accrual_takes_every_branch_and_counts_only_energy_never_issued():
    """Defect caught: an accrual that counts every held bill, or none, or an issued one. Each
    branch is asserted reachable in one statement before what it holds: a held estimate a read
    ended (out), a held estimate no read ended on a closed account (in, older than 12 months), a
    held actual-read bill whose catch-up went out with nobody (in, with its chargeable true-up),
    an issued estimate (out), and a fuel with nothing held (a zero row, not an absence)."""
    bills = [
        _bill("C1", "2023-02-28", "estimated", 200.0),
        _bill("C1", "2023-03-31", "actual", 210.0),
        _bill("C2", "2022-03-31", "estimated", 400.0, total=60.0, vat=3.0),
        _bill("C3", "2023-05-31", "actual", 300.0, total=90.0, vat=4.0, catchup_applied=True,
              read_true_up_kwh=50.0, read_true_up_barred_kwh=10.0),
        _bill("C3", "2023-06-30", "actual", 280.0),
        _bill("C4", "2023-06-30", "estimated", 250.0),
        _bill("C5", "2023-06-30", "actual", 900.0, commodity="gas"),
    ]
    held = {("C1", "2023-02-28"), ("C2", "2022-03-31"), ("C3", "2023-05-31")}
    accrual = unbilled_accrual(bills, held, "2023-06")
    elec, gas = accrual["by_fuel"]["electricity"], accrual["by_fuel"]["gas"]

    assert (elec["held_estimates"], elec["held_actuals"], elec["accounts"]) == (1, 1, 2), elec
    assert elec["kwh"] == pytest.approx(400.0 + 300.0 + 50.0 - 10.0)
    assert elec["gbp"] == pytest.approx((60.0 - 3.0) + (90.0 - 4.0))
    assert elec["older_than_12_months_kwh"] == pytest.approx(400.0)
    assert elec["closed_account_kwh"] == pytest.approx(400.0)
    assert gas == {"accounts": 0, "held_estimates": 0, "held_actuals": 0, "kwh": 0.0, "gbp": 0.0,
                   "older_than_12_months_kwh": 0.0, "closed_account_kwh": 0.0}
    # Before C1's read, its held estimate is still unbilled.
    assert unbilled_accrual(bills, held, "2023-02")["by_fuel"]["electricity"]["held_estimates"] == 2


def test_the_run_door_carries_the_accrual_and_it_counts_a_bill_the_gate_held():
    """Defect caught: the accrual dropped from the summary, or the door that decides issuance not
    naming the held bills. Both arms in one statement: the company's own bills, all issued, accrue
    nothing; the same bills with one estimate the pre-bill gate holds (its total no longer foots)
    accrue exactly that estimate's energy at the run's last month."""
    issued = _bills(actual_after_opening=False, closed=False)
    one_held = [dict(b) for b in issued]
    victim = next(b for b in one_held if b["billing_basis"] == "estimated")
    victim["total_amount_gbp"] += 1000.0

    def last(bills):
        accrual = billing_accuracy_door(bills)["K1_unbilled_accrual"]
        return accrual["available"] and accrual["month_ends"][-1]["by_fuel"]["electricity"]

    clean, held = last(issued), last(one_held)
    assert (clean["kwh"] == 0 and held["held_estimates"] == 1
            and held["kwh"] == pytest.approx(victim["total_consumption_kwh"])), (clean, held)


def test_a_summary_without_the_held_set_publishes_the_accrual_as_an_absence():
    accrual = billing_accuracy_summary(_bills(actual_after_opening=False))["K1_unbilled_accrual"]
    assert accrual["available"] is False and "held" in accrual["reason"]


def test_a_held_bill_is_never_counted_as_billed():
    """Defect caught: `account_billing_accuracy` or the K1 grades reading a bill the pre-bill gate
    held, which nobody received, as billed. The held arm must be reachable first: the door names
    the bill as held and the accrual carries it. Then, against the same bills all issued, billed
    and estimated kWh fall by exactly its energy and the billed-on-estimate grades lose it, so the
    two halves of unread revenue never count one bill."""
    issued = _bills(actual_after_opening=False, closed=False)
    one_held = [dict(b) for b in issued]
    victim = next(b for b in one_held if b["billing_basis"] == "estimated")
    victim["total_amount_gbp"] += 1000.0
    clean, held = billing_accuracy_door(issued), billing_accuracy_door(one_held)
    accrued = held["K1_unbilled_accrual"]["month_ends"][-1]["by_fuel"]["electricity"]
    assert accrued["held_estimates"] == 1, accrued

    c, h = clean["by_fuel"]["electricity"], held["by_fuel"]["electricity"]
    kwh = victim["total_consumption_kwh"]
    assert h["billed_kwh"] == pytest.approx(c["billed_kwh"] - kwh)
    assert h["estimated_kwh"] == pytest.approx(c["estimated_kwh"] - kwh)
    open_bills = [g["outstanding_bills"] for g in clean["K1_year_end_grades"]["electricity"]
                  if g["as_of"] >= victim["period_end"][:7]]
    held_open = [g["outstanding_bills"] for g in held["K1_year_end_grades"]["electricity"]
                 if g["as_of"] >= victim["period_end"][:7]]
    assert open_bills and all(n == o - 1 for n, o in zip(held_open, open_bills)), (
        open_bills, held_open)


def test_the_published_view_rebuilds_from_the_bills_with_the_held_set_and_carries_the_accrual():
    """Defect caught: a run output written before the accrual publishes it absent, and counts its
    held bills as billed, even though the publish holds the bills and the held set. Both arms:
    without the held set the accrual is a named absence; with it the view is rebuilt."""
    from company.interfaces.bill_assembly import held_bills

    issued = _bills(actual_after_opening=False, closed=False)
    one_held = [dict(b) for b in issued]
    victim = next(b for b in one_held if b["billing_basis"] == "estimated")
    victim["total_amount_gbp"] += 1000.0
    stale = billing_accuracy_summary(one_held)  # an older run: no held set, accrual absent
    absent = published_view(stale, "old.json", one_held)
    rebuilt = published_view(stale, "old.json", one_held, held_bills(one_held))
    assert absent["K1_unbilled_accrual"]["available"] is False and absent["K1_unbilled_accrual"]["reason"]
    assert rebuilt["K1_unbilled_accrual"]["available"] is True
    assert rebuilt["by_fuel"]["electricity"]["billed_kwh"] == pytest.approx(
        stale["by_fuel"]["electricity"]["billed_kwh"] - victim["total_consumption_kwh"])


def _split_bills():
    """S is smart all year (one estimate of four), T traditional (three of four), X has no meter
    type on record, and E is exchanged to smart at its last bill of 2024."""
    bills, types = [], {}
    for cid, kind, bases in (("S", "smart", "eaaa"), ("T", "traditional", "eeea"),
                             ("X", None, "ea"), ("E", "traditional", "eee")):
        for m, basis in enumerate(bases, start=1):
            end = f"2024-{m:02d}-28"
            bills.append(_bill(cid, end, "estimated" if basis == "e" else "actual", 100.0))
            if kind:
                types[(cid, end)] = kind
    types[("E", "2024-03-28")] = "smart"
    return bills, types


def test_the_estimated_share_splits_by_meter_and_counts_meters_at_the_years_last_bill():
    """Defect caught: one blended K2 reads 67% on a book whose smart meters bill about 8% on
    estimates and whose traditional meters about 80%, so a reader cannot tell the reading from the
    book's meters (Expert Hour 2026-10-14, #5). Every branch taken: smart, traditional, a bill with
    no meter type (counted as unknown, never guessed), and an exchange inside the year (the meter at
    the account's last bill is the one counted)."""
    bills, types = _split_bills()
    row = estimated_share_by_year_and_meter(bills, types)["by_fuel"]["electricity"][0]
    kinds = row["by_meter_type"]
    assert set(kinds) == {"smart", "traditional", "unknown"}
    assert kinds["smart"]["estimated_share"] == pytest.approx(2 / 5)  # S's 1 of 4, E's last 1
    assert kinds["traditional"]["estimated_share"] == pytest.approx(5 / 6)  # T's 3 of 4, E's 2
    assert kinds["unknown"]["estimated_share"] == pytest.approx(1 / 2)
    assert row["estimated_share"] == pytest.approx(8 / 13)
    assert row["accounts"] == 4
    assert row["traditional_share_of_accounts"] == pytest.approx(1 / 4)  # T only: E ends smart


def test_the_split_reads_the_meter_type_and_never_the_worlds_use():
    """Defect caught: the split reading `true_consumption_kwh`, the world's use on an estimated bill."""
    bills, types = _split_bills()
    before = estimated_share_by_year_and_meter(bills, types)
    for b in bills:
        b["true_consumption_kwh"] = 9999.0
    assert estimated_share_by_year_and_meter(bills, types) == before


def test_the_published_split_is_an_absence_without_meter_types_and_counts_no_held_bill():
    """Both arms: no meter types publishes a named absence and no figure; with them the split is
    read over the issued bills only, as the rest of the view is."""
    from company.interfaces.bill_assembly import held_bills

    issued = _bills(actual_after_opening=False, closed=False)
    one_held = [dict(b) for b in issued]
    next(b for b in one_held if b["billing_basis"] == "estimated")["total_amount_gbp"] += 1000.0
    summary = billing_accuracy_summary(one_held)
    assert held_bills(one_held), "the fixture must hold a bill or the issued-only leg proves nothing"
    absent = published_view(summary, "x.json", one_held, held_bills(one_held))
    assert absent["K2_by_year_and_meter_type"]["available"] is False
    assert absent["K2_by_year_and_meter_type"]["reason"] and "by_fuel" not in absent["K2_by_year_and_meter_type"]
    types = {(b["customer_id"], b["period_end"]): "traditional" for b in one_held}
    split = published_view(summary, "x.json", one_held, held_bills(one_held), types)
    rows = split["K2_by_year_and_meter_type"]["by_fuel"]["electricity"]
    assert sum(r["billed_kwh"] for r in rows) == pytest.approx(
        split["by_fuel"]["electricity"]["billed_kwh"])
    assert split["K2_by_year_and_meter_type"]["published_traditional_share_of_domestic_meters_end_2024"] == {
        "electricity": 0.358, "gas": 0.453}


# --- a mover's final bill (home_moves.md §8.8) ---------------------------------------------------

def _final(cid, period_end, basis="actual", **extra):
    return {"customer_id": cid, "period_end": period_end, "billing_basis": basis,
            "final_bill": True, "total_consumption_kwh": 50.0, **extra}


def _move_fixture():
    bills = [
        _final("ON", "2020-03-14"),                                        # issued at period end
        _final("LATE", "2020-03-14", "estimated", issue_date="2020-05-01"),  # 48 days after move
        _final("GONE", "2019-12-31"),                                      # closed before the move
        {"customer_id": "RUN", "period_end": "2021-06-30", "billing_basis": "actual",
         "total_consumption_kwh": 1.0},
    ]
    moves = [{"customer_id": c, "commodity": "electricity", "move_date": "2020-03-15"}
             for c in ("ON", "LATE", "GONE", "NOFINAL")]
    refunds = [
        {"customer_id": "ON", "trigger": "account_closure", "paid_date": "2020-03-20"},
        {"customer_id": "LATE", "trigger": "account_closure", "paid_date": "2020-06-01"},
    ]
    return bills, moves, refunds


def test_every_final_bill_branch_can_be_taken():
    """The partition control: on one fixture, every grade the rules allow is reached, so a guard
    that refuses everything, or passes everything, reds here."""
    out = move_out_final_bills(*_move_fixture(), closing_balances={"ON": -12.0, "LATE": 40.0})
    assert out["final_bill"]["on_time"] and out["final_bill"]["late"]
    assert out["final_bill"]["missing"] and out["final_bill"]["closed_before_move"]
    assert out["credit"]["on_time"] and out["credit"]["late"]
    assert out["closing_read"]["actual"] and out["closing_read"]["estimated"]
    assert out["debt"]["carried"] and out["debt"]["credit"]


def test_a_final_bill_issued_after_six_weeks_is_late():
    out = move_out_final_bills(*_move_fixture())
    row = {r["account_id"]: r for r in out["accounts"]}
    assert row["LATE"]["days_move_to_final_bill"] == 47
    assert row["LATE"]["final_bill"] == "late"
    assert row["ON"]["final_bill"] == "on_time"
    # A mixed basis is not the convention, so the cannot-fire caveat is not printed over it.
    assert out["final_bill"]["late_cannot_fire_because"] is None


def test_the_refund_clock_runs_from_the_final_bills_issue_not_the_move():
    """LATE's refund is 19 working days after its issue on 1 May (two bank holidays); from the move
    it would be 52."""
    row = {r["account_id"]: r for r in move_out_final_bills(*_move_fixture())["accounts"]}
    assert row["LATE"]["credit_refund_working_days"] == 19
    assert row["ON"]["credit_refund_working_days"] == 5


def test_period_end_issue_dates_say_the_late_branch_cannot_fire():
    bills, moves, refunds = _move_fixture()
    bills = [b for b in bills if b["customer_id"] != "LATE"]
    out = move_out_final_bills(bills, moves, refunds)
    assert out["final_bill"]["late"] == 0
    assert out["final_bill"]["late_cannot_fire_because"]


def test_the_debt_is_unmeasured_without_closing_balances_rather_than_zero():
    out = move_out_final_bills(*_move_fixture())
    assert out["debt"]["unmeasured_because"]
    assert all(r["debt"] is None for r in out["accounts"])


def test_no_move_register_is_not_nobody_moved():
    assert move_out_final_bills([], None)["available"] is False
