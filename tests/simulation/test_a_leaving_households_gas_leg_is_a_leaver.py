"""A household that leaves takes its gas leg with it.

`churned_billing_accounts` is keyed by household (`C1`); bills are keyed by supply point (`C1`,
`C1g`). Every consumer in `run_phase4c_on_phase2b.main` and `generate_billing_ledger` asked
`bill["customer_id"] in roster`, so a gas leg of a leaving household read as a stayer. It got no
SLC 21B final read, and the arrears engine priced its unpaid bills as a stayer's. On the
2026-09-28 book that was 28 gas legs, and 17 of them closed on an estimate. The
`defect4` gate caught it as `PROS-2020-0132` 2021: billed 47.83 against a margin of 69.18.

Each control names the defect it fails on:

* the partition fails if the helper returns the roster alone (the defect) or every supply point
  (a leaver set that swallows the stayers);
* the bill-assembly control fails if the helper's set stops reaching the final-read override.
  It runs the real assembly with every read forced to an estimate, so only that override can make
  a closing bill actual. The bare-roster arm is asserted too: it shows the gas leg really does
  close on an estimate when the id does not match, so the repaired arm is not green by accident.

`main()`'s own wiring is held by `test_run_phase4c_on_phase2b.py::
test_main_window_holds_a_churned_accounts_final_read`, which reads the live run by household.
"""
import calendar

import pytest

from simulation.household import supply_points_that_left
from simulation.run_phase4c_on_phase2b import build_monthly_bills


def test_a_departed_households_gas_leg_is_a_leaver_and_a_stayers_is_not():
    left = supply_points_that_left({"C1", "C1_2"}, ["C1", "C1g", "C2", "C2g", "C1_2"])

    assert left == {"C1", "C1g", "C1_2"}


@pytest.fixture
def every_read_estimated(monkeypatch):
    import simulation.meter_reads as mr

    monkeypatch.setattr(mr, "TRADITIONAL_ACTUAL_READ_PROBABILITY", 0.0)
    monkeypatch.setattr(mr, "HARD_TO_READ_ACTUAL_READ_PROBABILITY", 0.0)
    monkeypatch.setattr(mr, "SMART_METER_NOT_COMMUNICATING_RATE", 1.0)


def _month_records(cid, year, month, kwh):
    days = calendar.monthrange(year, month)[1]
    return [{
        "customer_id": cid,
        "settlement_date": f"{year}-{month:02d}-{d:02d}",
        "settlement_period": 1,
        "consumption_kwh": kwh / days,
        "unit_rate_gbp_per_mwh": 60.0,
        "revenue_gbp": kwh / days * 0.06 + 0.30,
        "standing_charge_gbp": 0.30,
        "wholesale_cost_gbp": 0.0,
        "margin_gbp": 0.0,
    } for d in range(1, days + 1)]


def _last_basis(bills, cid):
    return max((b for b in bills if b["customer_id"] == cid),
               key=lambda b: b["period_end"])["billing_basis"]


def test_the_gas_leg_of_a_leaving_household_closes_on_a_final_read(every_read_estimated):
    records = [r for m in range(1, 9) for cid in ("C1", "C1g")
               for r in _month_records(cid, 2022, m, 900.0 if cid == "C1g" else 250.0)]

    bare_roster = build_monthly_bills(records, churned_ids={"C1"})
    assert _last_basis(bare_roster, "C1") == "actual"
    assert _last_basis(bare_roster, "C1g") == "estimated", (
        "the bare roster no longer strands the gas leg, so this control has lost its defect")

    repaired = build_monthly_bills(
        records, churned_ids=supply_points_that_left({"C1"}, {r["customer_id"] for r in records}))
    assert _last_basis(repaired, "C1") == "actual"
    assert _last_basis(repaired, "C1g") == "actual"
