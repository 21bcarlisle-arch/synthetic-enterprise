"""B7 slice 6: after a move-out the vacated home is VOID for its tenure's register length, billed to
the owner as standing charges only, and the incoming occupier (and its unnamed window) starts at
the void's end. Director, 2026-10-08: "Rare-event order: approved. Voids first".

One short run (2016, moves forced on). Everything a test needs is a pure function of the result or
of the register, so `tests/conftest.py`'s book reset between tests cannot change what is read.
"""
from __future__ import annotations

import datetime as dt

import pytest

import simulation.arrears_engine as ae
import simulation.run_phase2b as run
from sim.customer_state_layer import (
    VOID_TOGGLE_BY_TENURE,
    unnamed_until,
    void_end,
)
from simulation.household import household_of
from simulation.household_segments import TenureType, tenure_for_customer
from simulation.meter_reads import assumption_toggle_or_gap
from simulation.policy_costs import (
    get_electricity_standing_charge_per_day,
    get_gas_standing_charge_per_day,
)
from tests.tools.test_generate_billing_ledger_pw import _resi_bill


@pytest.fixture(scope="module")
def void_run():
    patch = pytest.MonkeyPatch()
    patch.setattr(run, "moves_active", lambda: True)
    try:
        yield run.main(report_end="2016-12-31")
    finally:
        patch.undo()


def _rows_of(result, leg):
    return [r for r in result["all_records"] if r["customer_id"] == leg]


def test_each_tenure_reads_its_own_register_row():
    """Defect: the social and private rows swapped, or a void typed in for the owner GAP."""
    for tenure, toggle in VOID_TOGGLE_BY_TENURE.items():
        months, gap = assumption_toggle_or_gap(toggle)
        start = dt.date(2018, 3, 1)
        end, reason = void_end(start, tenure)
        if months is None:
            assert (end, reason) == (start, gap) and "GAP" in reason, tenure
        else:
            assert reason is None and (end - start).days == round(months * 365.25 / 12.0), tenure
    assert void_end(dt.date(2018, 3, 1), TenureType.SOCIAL_RENTER)[0] > void_end(
        dt.date(2018, 3, 1), TenureType.PRIVATE_RENTER)[0]


def test_the_void_length_follows_the_vacated_homes_tenure(void_run):
    """Defect: the void read from the INCOMING occupier's tenure, or from none. The first assertion
    is the partition control: a run with no void, or only voids, passes the loop vacuously."""
    ins = void_run["home_move_ins"]
    assert [m for m in ins if m["void_days"] > 0] and [m for m in ins if m["void_days"] == 0]
    for m in ins:
        mover_tenure = tenure_for_customer(household_of(m["premise"]))
        assert m["vacated_tenure"] == mover_tenure.value, m
        expected, _ = void_end(dt.date.fromisoformat(m["account_opened"]), mover_tenure)
        assert m["supply_start"] == expected.isoformat(), m


def test_the_incoming_occupier_starts_at_void_end_and_its_unnamed_window_starts_there(void_run):
    """Defect: the unnamed window still runs from the move date, so the owner's void is booked as
    the occupier's debt, or the occupier's supply starts on the move date regardless."""
    voided = [m for m in void_run["home_move_ins"] if m["void_days"] > 0]
    assert voided
    for m in voided:
        opened = dt.date.fromisoformat(m["account_opened"])
        start = dt.date.fromisoformat(m["supply_start"])
        assert (start - opened).days == m["void_days"], m
        assert m["unnamed_until"] == unnamed_until(start).isoformat(), m
        rows = _rows_of(void_run, m["customer_id"])
        debt_days = sorted(r["settlement_date"][:10] for r in rows if "occupier_debt_gbp" in r)
        assert debt_days and debt_days[0] == m["supply_start"], m


def test_an_owner_occupiers_home_has_no_void_and_says_why(void_run):
    """Defect: a void invented for the owner GAP, or no reason recorded for its absence."""
    owners = [m for m in void_run["home_move_ins"] if m["vacated_tenure"] == "owner_occupier"]
    renters = [m for m in void_run["home_move_ins"] if m["vacated_tenure"] != "owner_occupier"]
    assert owners and renters
    for m in owners:
        assert m["void_days"] == 0 and m["supply_start"] == m["account_opened"], m
        assert "GAP" in m["void_reason"] and m["void_owner_charge_gbp"] == 0.0, m
        assert not [r for r in _rows_of(void_run, m["customer_id"])
                    if "void_owner_charge_gbp" in r]
    assert all(m["void_reason"] is None for m in renters)


def test_a_void_day_carries_the_standing_charge_and_no_energy(void_run):
    """Defect: the void settled at the premise's normal use, or billed nothing, or the void field
    spilling past the occupier's arrival."""
    voided = [m for m in void_run["home_move_ins"] if m["void_days"] > 0]
    assert {m["commodity"] for m in voided} == {"electricity", "gas"}
    total = 0.0
    for m in voided:
        rows = _rows_of(void_run, m["customer_id"])
        inside = [r for r in rows if r["settlement_date"][:10] < m["supply_start"]]
        after = [r for r in rows if r["settlement_date"][:10] >= m["supply_start"]]
        assert inside and [r for r in after if r["consumption_kwh"] > 0.0], m
        assert not [r for r in after if "void_owner_charge_gbp" in r]
        assert m["void_consumption_unknown_reason"]
        for r in inside:
            day = r["settlement_date"][:10]
            if m["commodity"] == "gas":
                per_day = get_gas_standing_charge_per_day(day)
            else:
                per_day = (get_electricity_standing_charge_per_day(day)
                           * r["settlement_periods_folded"] / 48.0)
            assert r["consumption_kwh"] == 0.0 and r["wholesale_cost_gbp"] == 0.0, r
            assert r["void_owner_charge_gbp"] == pytest.approx(per_day), r
            assert r["revenue_gbp"] == pytest.approx(per_day), r
            assert "occupier_debt_gbp" not in r and r["bad_debt_gbp"] == 0.0, r
        assert m["void_owner_charge_gbp"] == pytest.approx(
            sum(r["void_owner_charge_gbp"] for r in inside)), m
        total += m["void_owner_charge_gbp"]
    assert void_run["total_void_owner_charge"] == pytest.approx(total)


def test_a_wholly_void_bill_is_stamped_as_the_owners(void_run):
    """Defect: the void month's bill reaches the arrears engine unmarked, so the incoming occupier
    is asked to pay the owner's standing charges."""
    from simulation.run_phase4c_on_phase2b import build_monthly_bills
    start = {m["customer_id"]: m["supply_start"] for m in void_run["home_move_ins"]
             if m["void_days"] > 0}
    bills = [b for b in build_monthly_bills(void_run["all_records"]) if b["customer_id"] in start]
    whole = [b for b in bills if b["period_end"] < start[b["customer_id"]]]
    after = [b for b in bills if b["period_start"] >= start[b["customer_id"]]]
    assert whole and after
    assert all(b["void_owner_share"] == 1.0 for b in whole), whole
    assert not [b for b in after if "void_owner_share" in b]


def _book():
    bills, behavioral = [], {}
    for i in range(40):
        cid = f"B7S6-{i:02d}"
        behavioral[cid] = {"income_stress_trajectory": [{"year": 2022, "stress": "high"}]}
        bills += [_resi_bill(cid, "2022-%02d-28" % m, 150.0) for m in range(1, 5)]
    return bills, behavioral


def test_the_arrears_engine_never_asks_a_named_payer_for_the_owners_void():
    """Defect: `_resolve_bills` reads the occupier's share and not the owner's, so a void month is
    collected (or written off) as the incoming household's bill. Month 1 wholly void, month 2 void
    then unnamed (the two shares make the whole), month 3 a 40% void, month 4 unmarked."""
    bills, behavioral = _book()
    marked = []
    for b in bills:
        b, month = dict(b), int(b["period_end"][5:7])
        if month == 1:
            b["void_owner_share"] = 1.0
        elif month == 2:
            b["void_owner_share"], b["occupier_share"] = 0.3, 0.7
        elif month == 3:
            b["void_owner_share"] = 0.4
        marked.append(b)
    rows = ae._resolve_bills(marked, behavioral, 42)
    months = {}
    for r in rows:
        months.setdefault(int(r["period_end"][5:7]), []).append(r["amount_gbp"])
    assert 1 not in months and 2 not in months
    assert set(months[3]) == {90.0} and set(months[4]) == {150.0}
