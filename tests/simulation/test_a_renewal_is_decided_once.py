"""PB6, 2026-09-29: a household's engagement at a renewal has one answer, not two.

THE DEFECT. The schedule builders roll `rolls_active_renewal` on `{household}_{k}` with the
archetype x payment-channel probability and send a passive household to an SVT stint. The
departure branch in `run_phase2b` rolled the same seed again with the archetype alone. For a
channel multiplier above 1, a household in the band `[p, p*m)` reached a fixed renewal as active
and was then charged `PASSIVE_CHURN_CAP` as passive. On the live roster that was 15 of 212 reached
electricity decisions (14 direct debit, 1 standard credit, no prepayment), so per decision the
world made a prepayment household the MORE likely one to leave.
(`docs/staging/WORKER_FINDING_PB6_THE_ENGAGEMENT_FACTOR_IS_USED_PER_DECISION_AND_ITS_PRIOR_IS_PER_EXPOSURE_2026-09-29.md`)

Mutations, run on a copy and recorded as observed:

  * `active_renewal_probability_at_a_decision` returns the archetype alone for resi (the old
    departure roll) -> red: `..._every_resi_decision_reached_is_decided_active`, 8 of 82 gas
    renewals reached.
  * the departure branch reverted to `active_renewal_probability(_engagement_level)` -> red:
    `..._the_departure_branch_asks_the_decision_probability`.
  * the non-resi leg returns 1.0 (passive cap made unreachable) -> red:
    `..._the_passive_cap_is_still_reachable_for_a_business_renewal`, `{True}`.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from simulation.household import household_of
from simulation.household_segments import (
    active_renewal_probability_at_a_decision,
    active_renewal_probability_for_customer,
)
from simulation.renewal_engagement import ftc_withdrawn_at, rolls_active_renewal

_REPO = Path(__file__).resolve().parents[2]
_WORLD = _REPO / "simulation" / "run_phase2b.py"


@pytest.fixture(scope="module")
def gas_book():
    """Every resi gas leg's schedule, built as `run_phase2b` builds it. Gas and not electricity
    because it needs only the NBP file, and the gas builder asks the same roll on the same seed
    grammar (`test_the_gas_leg_rolls_onto_the_cap_like_the_electricity_one.py` holds that)."""
    if not (_REPO / "sim" / "gas_data" / "nbp_sap.csv").exists():
        pytest.skip("NBP gas price data not available; this control needs the real feed")
    from sim.gas_prices_history import load_nbp_history
    from simulation.run_phase2b import (
        GAS_CUSTOMERS,
        REPORT_END,
        _build_gas_renewal_schedule,
        resolved_tariff_type,
    )

    records = load_nbp_history()
    return {
        c["customer_id"]: _build_gas_renewal_schedule(
            c, records, report_end=REPORT_END, tariff_type=resolved_tariff_type(c))
        for c in GAS_CUSTOMERS if c.get("segment", "resi") == "resi"
    }


def test_every_resi_decision_reached_is_decided_active(gas_book):
    """The departure branch's roll, asked of every fixed renewal the schedule reached, says active.

    Keyed to the property, not to a count: any resi term that is fixed at k >= 1 was reached
    BECAUSE the schedule rolled active on this seed, so a passive answer here is the second,
    disagreeing answer this file exists to prevent.
    """
    reached = 0
    disagree = []
    for cid, schedule in gas_book.items():
        household = household_of(cid)
        for k, term in enumerate(schedule):
            if k == 0 or term.get("tariff_type", "fixed") != "fixed":
                continue
            reached += 1
            start = term["acquisition_date"]
            if not rolls_active_renewal(
                start, f"{household}_{k}",
                active_renewal_probability_at_a_decision(household, "resi"),
            ):
                disagree.append((cid, k, start))
    assert reached > 20, f"only {reached} fixed renewals reached; the control has no subject"
    assert not disagree, (
        f"{len(disagree)} of {reached} resi renewals reached a fixed term as active and are then "
        f"decided passive by the departure roll: {disagree[:5]}")


def test_the_decision_probability_is_the_one_the_schedule_rolls_for_resi():
    from simulation.run_phase2b import ELEC_CUSTOMERS

    households = {household_of(c["customer_id"]) for c in ELEC_CUSTOMERS
                  if c.get("segment", "resi") == "resi"}
    assert households
    for household in households:
        assert active_renewal_probability_at_a_decision(household, "resi") == (
            active_renewal_probability_for_customer(household))


def test_the_passive_cap_is_still_reachable_for_a_business_renewal():
    """The rare branch CAN be taken: a non-resi renewal has no SVT to roll to, so this roll is its
    only answer, and it must be able to come out passive or `PASSIVE_CHURN_CAP` is dead code."""
    from simulation.run_phase2b import _ALL_KNOWN_CUSTOMERS

    business = [c for c in _ALL_KNOWN_CUSTOMERS if c.get("segment", "resi") != "resi"]
    if not business:
        pytest.skip("no non-resi account on the roster")
    outcomes = set()
    for c in business:
        household = household_of(c["customer_id"])
        p = active_renewal_probability_at_a_decision(household, c["segment"])
        for year in range(2016, 2026):
            start = f"{year}-03-01"
            if ftc_withdrawn_at(start):
                continue
            outcomes.add(rolls_active_renewal(start, f"{household}_{year - 2015}", p))
    assert outcomes == {True, False}, f"a business renewal only ever rolls {outcomes}"


def test_the_departure_branch_asks_the_decision_probability():
    """Reaches the SOURCE because the defect is how many probabilities one event is asked with,
    and the departure branch sits in a loop only a full-window run reaches."""
    tree = ast.parse(_WORLD.read_text())
    probabilities = []
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "rolls_active_renewal" and len(node.args) == 3
                and isinstance(node.args[2], ast.Call)
                and isinstance(node.args[2].func, ast.Name)):
            probabilities.append(node.args[2].func.id)
    assert len(probabilities) == 2, f"expected the gas-leg roll and the departure roll: {probabilities}"
    assert "active_renewal_probability" not in probabilities, (
        "a roll in run_phase2b asks the archetype alone -- the departure branch has gone back to "
        "a second answer for a renewal the schedule already decided")
    assert "active_renewal_probability_at_a_decision" in probabilities
