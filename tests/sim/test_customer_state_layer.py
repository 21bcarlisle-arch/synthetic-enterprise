"""B7 slice 1: a home move is a credit exit plus two deemed entries, on its own substreams."""
from __future__ import annotations

import math

import pytest

import sim.customer_state_layer as csl
from sim.customer_state_layer import (
    DEEMED_TERMS,
    Occupancy,
    OccupancyEnded,
    OccupancyStarted,
    draw_home_move,
    move_hazard_per_year,
)
from simulation.arrival_route import home_move_rate_per_household_year
from simulation.household_segments import TenureType

N = 6000


def _moves(tenure: TenureType, year: int = 2021, seed: int = 11, n: int = N):
    return [draw_home_move(Occupancy.of_customer(f"C{i}", tenure), year, seed) for i in range(n)]


def test_both_branches_are_reachable_before_either_is_graded():
    """Defect: a hazard that never fires (or always fires) passes every per-move assertion."""
    drawn = _moves(TenureType.PRIVATE_RENTER)
    assert any(m is None for m in drawn) and any(m is not None for m in drawn)


@pytest.mark.parametrize("tenure", list(TenureType))
def test_the_drawn_rate_is_the_sourced_rate_within_its_sampling_bound(tenure):
    """Defect: a hazard restated, inverted or detached from the EHS figure it imports."""
    p = home_move_rate_per_household_year(tenure)
    observed = sum(m is not None for m in _moves(tenure)) / N
    assert abs(observed - p) < 4 * math.sqrt(p * (1 - p) / N)


def test_tenure_orders_the_hazard_as_the_record_does():
    """Defect: tenure ignored. EHS gives private renting several times owner-occupation."""
    private = sum(m is not None for m in _moves(TenureType.PRIVATE_RENTER))
    owner = sum(m is not None for m in _moves(TenureType.OWNER_OCCUPIER))
    assert private > 2 * owner


def test_a_move_is_one_credit_exit_and_two_deemed_entries_at_two_premises():
    """Defect: the vacated premise not re-occupied, or the mover not re-housed (BACKLOG B7 exit test)."""
    moves = [m for m in _moves(TenureType.PRIVATE_RENTER) if m is not None]
    assert moves
    for m in moves:
        ended = [t for t in m.transitions if isinstance(t, OccupancyEnded)]
        started = [t for t in m.transitions if isinstance(t, OccupancyStarted)]
        assert len(ended) == 1 and len(started) == 2
        assert {s.terms for s in started} == {DEEMED_TERMS}
        assert m.incoming.premise_id == m.vacated.premise_id
        assert m.incoming.occupancy_id != m.vacated.occupancy_id
        assert m.mover_arrives.occupancy_id == m.vacated.occupancy_id
        assert m.mover_arrives.premise_id != m.vacated.premise_id
        # Non-overlapping windows at the vacated premise: liability passes, it is never held twice.
        assert m.incoming.starts_no_earlier_than >= m.vacated.end_date
        assert m.move_date.year == 2021


def test_the_void_is_a_named_gap_not_a_guessed_date():
    """Defect: a plausible void length typed in to make the incoming leg billable."""
    m = next(m for m in _moves(TenureType.PRIVATE_RENTER) if m is not None)
    assert m.incoming.start_date is None
    assert "§2.4" in m.incoming.start_date_unknown_reason
    assert m.mover_arrives.start_date == m.move_date


def test_the_credit_exit_opens_a_final_bill_on_the_premise_it_left():
    m = next(m for m in _moves(TenureType.PRIVATE_RENTER) if m is not None)
    x = m.vacated.final_bill_exposure("ACC1", "electricity", 37.0)
    assert (x.supply_point_id, x.closure_date, x.customer_id) == (
        m.vacated.premise_id, m.move_date, m.vacated.occupancy_id)


def test_an_unmoved_occupancy_is_the_customer_it_was_drawn_as():
    """Defect: the identity split leaking into households that never move."""
    occ = Occupancy.of_customer("C42", TenureType.OWNER_OCCUPIER)
    assert occ.premise_id == occ.occupancy_id == "C42"


def test_replay_is_deterministic():
    assert _moves(TenureType.SOCIAL_RENTER, n=800) == _moves(TenureType.SOCIAL_RENTER, n=800)
    assert _moves(TenureType.SOCIAL_RENTER, n=800) != _moves(TenureType.SOCIAL_RENTER, seed=12, n=800)


def test_redrawing_the_date_cannot_change_who_moves(monkeypatch):
    """Defect: onset and date sharing a stream, so a date-distribution change reshuffles the movers
    (the 01:09Z shared-RNG shape)."""
    before = [m is not None for m in _moves(TenureType.PRIVATE_RENTER, n=1500)]
    real = csl._substream

    def other_date_stream(base_seed, stream, *key):
        return real(base_seed + (1 if stream == "move_date" else 0), stream, *key)

    monkeypatch.setattr(csl, "_substream", other_date_stream)
    after = _moves(TenureType.PRIVATE_RENTER, n=1500)
    assert [m is not None for m in after] == before
    assert any(m is not None for m in after)


def test_onset_is_the_hazard_streams_own_first_draw_and_the_date_is_not_tied_to_it():
    """Defect: the date drawn from the onset stream, or before the onset on a shared generator.
    Either makes the date a function of the roll that chose the mover, so movers' dates cluster."""
    p = home_move_rate_per_household_year(TenureType.PRIVATE_RENTER)
    for i in range(400):
        occ = Occupancy.of_customer(f"C{i}", TenureType.PRIVATE_RENTER)
        roll = csl._substream(11, "move_hazard", occ.premise_id, occ.occupancy_id, "2021").random()
        assert (draw_home_move(occ, 2021, 11) is not None) == (roll < p)
    movers = [m for m in _moves(TenureType.PRIVATE_RENTER) if m is not None]
    second_half = sum(m.move_date.month > 6 for m in movers) / len(movers)
    assert abs(second_half - 0.5) < 4 * math.sqrt(0.25 / len(movers))


def test_each_registered_stream_draws_independently_of_the_others():
    """Defect: the stream name dropped from the key, so every stream replays the same sequence."""
    first = {s: csl._substream(3, s, "P", "O", "2020").getrandbits(64) for s in csl.SUBSTREAMS}
    assert len(set(first.values())) == len(csl.SUBSTREAMS)


def test_registering_a_new_stream_leaves_every_existing_draw_identical(monkeypatch):
    before = _moves(TenureType.PRIVATE_RENTER, n=1500)
    monkeypatch.setattr(csl, "SUBSTREAMS", csl.SUBSTREAMS + ("income_shock_onset",))
    assert _moves(TenureType.PRIVATE_RENTER, n=1500) == before


def test_an_unregistered_stream_refuses_rather_than_sharing_a_generator():
    with pytest.raises(KeyError, match="not a registered"):
        csl._substream(1, "composition_change", "P")


def test_a_malformed_tenure_or_hazard_fails_closed(monkeypatch):
    with pytest.raises(TypeError):
        move_hazard_per_year("private_renter")
    monkeypatch.setattr(csl, "home_move_rate_per_household_year", lambda t: float("nan"))
    with pytest.raises(ValueError, match="not a probability"):
        draw_home_move(Occupancy.of_customer("C1", TenureType.OWNER_OCCUPIER), 2020, 1)
