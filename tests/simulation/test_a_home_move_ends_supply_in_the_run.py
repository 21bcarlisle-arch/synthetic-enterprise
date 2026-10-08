"""B7 slice 2: with home moves on, the run stops supplying a mover at the move date.

One short run (2016 only, about a minute and a half) with the curriculum switch forced on. The
unit tests in `tests/sim/test_customer_state_layer.py` cannot see whether the run asks the layer at
all; this is the control that goes red if the call site is removed and every unit test stays green.
"""
from __future__ import annotations

import datetime as dt

import pytest

import simulation.run_phase2b as run
from sim.customer_state_layer import unnamed_months_per_move


@pytest.fixture(scope="module")
def moved_run():
    patch = pytest.MonkeyPatch()
    patch.setattr(run, "moves_active", lambda: True)
    try:
        result = run.main(report_end="2016-12-31")
        # THE RUN'S OWN ANNUAL QUANTITIES, taken before any test tears down. tests/conftest.py's
        # autouse `_phase2b_book_is_put_back` (5941e47a9) resets the module's book to the drawn
        # state after EVERY test, so a later test reading `run.get_customer(...)` live saw the
        # drawn EAC, not the one this run settled on, and failed only when it did not run first.
        result["_annual_kwh_by_leg"] = {
            m["customer_id"]: run.get_customer(m["customer_id"]).get(
                "aq_kwh" if m["commodity"] == "gas" else "eac_kwh")
            for m in result.get("home_move_outs") or []}
        yield result
    finally:
        patch.undo()


def test_the_run_draws_moves_when_the_layer_is_on(moved_run):
    """Defect: the layer switched on and never asked -- the CoT stack's state for months."""
    assert moved_run["home_move_outs"]


def test_a_movers_supply_ends_on_the_move_date_and_never_resumes(moved_run):
    """Defect: the move recorded while the account goes on being billed past it, or a term lost."""
    rows = moved_run["account_state_log"]
    for move in moved_run["home_move_outs"]:
        moved = dt.date.fromisoformat(move["move_date"])
        own = [r for r in rows if r["customer_id"] == move["customer_id"]]
        assert [r for r in own if r["term_end"][:10] == move["move_date"]], move
        assert not [r for r in own if dt.date.fromisoformat(r["term_start"][:10]) >= moved], move


def test_a_move_is_the_one_churn_the_journey_calls_uncatchable(moved_run):
    """Defect: the move leaves the journey on a funnel state, so churn recall is scored on it."""
    assert {(m["journey_state"], m["catchable"]) for m in moved_run["home_move_outs"]} == {
        ("home_move_churned", False)}


def test_a_business_account_never_moves_home(moved_run):
    """Defect: the domestic hazard applied to an I&C or SME site."""
    segment = {c["customer_id"]: c.get("segment", "resi") for c in run._ALL_KNOWN_CUSTOMERS}
    assert {segment.get(m["household"], "resi") for m in moved_run["home_move_outs"]} == {"resi"}


def test_each_move_out_leaves_its_premise_unnamed_for_the_registers_window(moved_run):
    """W2_36 slice 3. Defect: the gap not computed in the run, or priced from the other fuel's
    annual quantity. Both fuels must be present, or the fuel choice is never exercised."""
    assert {m["commodity"] for m in moved_run["home_move_outs"]} == {"electricity", "gas"}
    for move in moved_run["home_move_outs"]:
        annual = moved_run["_annual_kwh_by_leg"][move["customer_id"]]
        assert move["unnamed_kwh_expected"] == pytest.approx(
            annual / 12.0 * unnamed_months_per_move()), move


def test_a_vacated_premise_is_supplied_the_day_after_the_movers_last_day(moved_run):
    """B7 slice 3. Defect: the premise stops at the move, so every move reads as a lost premise.

    Every move-out leg has an incoming leg at the same meter point whose supply starts on the move
    date, which is the day after the mover's last supplied day. A settled term for that leg starts
    on that day. The first assertion is the partition control: a run whose moves all fall too late
    to settle would pass the loop vacuously."""
    rows = moved_run["account_state_log"]
    incoming = {m["premise"]: m for m in moved_run["home_move_ins"]}
    assert [m for m in incoming.values() if m["segments"]]
    for move in moved_run["home_move_outs"]:
        leg = incoming[move["customer_id"]]
        assert leg["supply_start"] == move["move_date"], move
        assert leg["commodity"] == move["commodity"], move
        assert [r for r in rows if r["customer_id"] == leg["customer_id"]
                and r["term_start"][:10] == move["move_date"]], move


def test_the_incoming_occupant_is_its_own_household_on_the_default_tariff(moved_run):
    """Defect: the incoming leg billed under the mover's account, so the supplier never sees the
    account end and B11 has no move to split. Or it is put on a struck fix nobody agreed to."""
    movers = {m["household"] for m in moved_run["home_move_outs"]}
    ins = moved_run["home_move_ins"]
    assert not movers & {m["household"] for m in ins}
    assert {(m["terms"], m["tariff_type"]) for m in ins} == {("deemed_contract", "svt")}
    supplied = {m["customer_id"] for m in ins}
    assert {r["tariff_type"] for r in moved_run["account_state_log"]
            if r["customer_id"] in supplied} == {"svt"}


def test_a_dual_fuel_premise_keeps_both_legs_in_one_incoming_household(moved_run):
    """Defect: the two fuel legs of one vacated home handed to two different new households."""
    by_mover: dict[str, set[str]] = {}
    premise_household = {m["customer_id"]: m["household"] for m in moved_run["home_move_outs"]}
    for leg in moved_run["home_move_ins"]:
        by_mover.setdefault(premise_household[leg["premise"]], set()).add(leg["household"])
    assert [h for h, legs in by_mover.items()
            if {m["commodity"] for m in moved_run["home_move_outs"] if m["household"] == h}
            == {"electricity", "gas"}]
    assert all(len(households) == 1 for households in by_mover.values()), by_mover


def test_the_change_of_tenancy_window_is_occupier_debt_and_the_rest_is_collected_as_usual(
        moved_run):
    """B7 slice 4. Defect: the incoming account counted as paying for energy used before anyone
    was named, or the debt booked past the window, or booked on the mover's or anyone else's
    rows. The first assertion is the partition control: rows on BOTH sides of a window must
    exist, or a rule that books everything or nothing would pass the loop."""
    until = {m["customer_id"]: m["unnamed_until"] for m in moved_run["home_move_ins"]}
    rows = [r for r in moved_run["all_records"] if r["customer_id"] in until]
    inside = [r for r in rows if r["settlement_date"][:10] < until[r["customer_id"]]]
    after = [r for r in rows if r["settlement_date"][:10] >= until[r["customer_id"]]]
    assert inside and after and [r for r in inside if r.get("revenue_gbp", 0.0) > 0.0]
    for rec in inside:
        assert rec["occupier_debt_gbp"] == pytest.approx(rec.get("revenue_gbp", 0.0)), rec
        assert rec["bad_debt_gbp"] == 0.0, rec
    assert not [r for r in after if "occupier_debt_gbp" in r]
    assert not [r for r in moved_run["all_records"]
                if "occupier_debt_gbp" in r and r["customer_id"] not in until]
    assert moved_run["total_occupier_debt"] == pytest.approx(
        sum(r["occupier_debt_gbp"] for r in inside))


def test_a_bill_carries_the_share_of_its_charges_that_is_occupier_debt(moved_run):
    """B7 slice 5. Defect: the window's bills reach the arrears engine unmarked, so the energy is
    written off at the ordinary rate on top of its occupier debt. All three kinds of month must
    exist -- wholly inside, the month the occupant is named, and after -- or a stamp that marked
    every bill, or none, or only whole months would pass."""
    from simulation.run_phase4c_on_phase2b import build_monthly_bills
    until = {m["customer_id"]: m["unnamed_until"] for m in moved_run["home_move_ins"]}
    bills = [b for b in build_monthly_bills(moved_run["all_records"])
             if b["customer_id"] in until]
    whole = [b for b in bills if b["period_end"] < until[b["customer_id"]]]
    split = [b for b in bills
             if b["period_start"] < until[b["customer_id"]] <= b["period_end"]]
    after = [b for b in bills if b["period_start"] >= until[b["customer_id"]]]
    assert whole and split and after
    assert all(b["occupier_share"] == 1.0 for b in whole), whole
    assert all(0.0 < b["occupier_share"] < 1.0 for b in split), split
    assert not [b for b in after if "occupier_share" in b]
