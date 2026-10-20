"""The household save carry (fuel page §8a): a saved dual household's riding leg is billed the rate
its household was saved on, when that leg's term is priced.

Defect guarded: no run has exercised the carry. The full-window run graded 2026-10-20 had one save,
on a single-leg household, so nothing was ever written to it; a seed sweep buys under one two-offer
save per seed. The write and the take are reached here through the run's own helpers, fed the real
household decision.

Mutations, run 2026-10-20, each red: refusal dropped (1), above-chain guard dropped (1), splice guard
dropped (1), pop made a get (3), carry never written (1).

The latent case (SEAT_PREREG_THE_SAVE_OFFER_RUN_READS_ITS_SWITCH_AND_ANSWERS_BOTH_NOTICES_2026-10-19):
a gas decision leg's carry to `C1` would be lost, because the heap prices `C1` before `C1g`. RULED
OUT, not fixed: gas decides only where the household has no electricity point, so it has no leg to
carry to. The write refuses any carry to a point the heap has already priced, so that stays true.

Inputs as `test_the_household_save_answers_both_notices_at_the_roll.py` (published 2024-Q2 default
and best-deal gap; illustrative forwards and volumes).
"""
from __future__ import annotations

import heapq

import pytest

import simulation.run_phase2b as run
from company.interfaces.save_offer import published_best_deal_gap_share, request_household_save
from simulation.customer_events import departure_decision_leg
from simulation.household import household_of
from simulation.registration_loss_feed import supply_points_on_supply
from tests.simulation.test_the_household_save_answers_both_notices_at_the_roll import (
    DAY,
    ELEC,
    GAS,
    ON,
    _company_volume,  # noqa: F401  (autouse fixture)
    _held,
)


def _saved_household_rates() -> dict:
    points = [("H1", "electricity"), ("H1g", "gas")]
    legs = run._household_save_legs(
        "H1", "electricity", ELEC, DAY, ELEC["unit_rate_gbp_per_mwh"], 110.0, 3_000.0,
        points, {"H1": [ELEC]}, {"H1g": [GAS]}, settled=None)
    rates, _ = request_household_save(
        _held(points), legs, DAY, published_best_deal_gap_share(DAY), ON)
    return rates


def test_a_saved_dual_households_riding_leg_is_billed_its_carried_rate():
    """Asserted first: the carry is written and read at all."""
    rates = _saved_household_rates()
    carry: dict = {}
    run._write_household_save_carry(carry, rates, "H1", DAY)
    assert carry == {("H1g", DAY): rates["H1g"]}
    chain_rate = GAS["unit_rate_gbp_per_mwh"]
    assert rates["H1g"] < chain_rate
    assert run._take_household_save_carry(carry, "H1g", DAY, chain_rate, spliced=False) == rates["H1g"]
    assert carry == {}


def test_a_carry_above_the_chains_rate_is_consumed_and_not_billed():
    carry = {("H1g", DAY): 70.0}
    assert run._take_household_save_carry(carry, "H1g", DAY, 62.0, spliced=False) is None
    assert carry == {}


def test_a_spliced_default_segment_consumes_the_carry_and_is_not_billed_it():
    carry = {("H1g", DAY): 50.0}
    assert run._take_household_save_carry(carry, "H1g", DAY, 62.0, spliced=True) is None
    assert carry == {}


def test_the_carry_is_read_only_because_the_riding_leg_pops_after_the_deciding_leg():
    """The run's heap key is (term_start, point, seq); the gas leg of `H1` is `H1g`."""
    heap = [(DAY, "H1g", 0, "gas"), (DAY, "H1", 1, "electricity")]
    heapq.heapify(heap)
    assert [heapq.heappop(heap)[1] for _ in range(2)] == ["H1", "H1g"]
    assert household_of("H1g") == "H1"


def test_a_gas_decision_leg_has_no_electricity_leg_to_carry_to():
    elec, gas = {}, {"H2g": [GAS]}
    accounts_with_elec = {household_of(c) for c, s in elec.items() if s}
    assert departure_decision_leg("H2", accounts_with_an_electricity_leg=accounts_with_elec) == "gas"
    assert supply_points_on_supply("H2", DAY, elec, gas) == [("H2g", "gas")]
    # ...and with an electricity point the household decides on electricity, never gas.
    elec = {"H2": [ELEC]}
    accounts_with_elec = {household_of(c) for c, s in elec.items() if s}
    assert departure_decision_leg("H2", accounts_with_an_electricity_leg=accounts_with_elec) == (
        "electricity")


def test_a_carry_to_a_point_the_heap_has_already_priced_is_refused_by_name():
    carry: dict = {}
    with pytest.raises(ValueError, match="before the deciding leg 'H1g'"):
        run._write_household_save_carry(carry, {"H1g": 50.0, "H1": 200.0}, "H1g", DAY)
    assert carry == {}
