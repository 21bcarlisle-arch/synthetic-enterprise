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


# --- slice 2: the run asks the layer --------------------------------------------------------

import datetime as dt  # noqa: E402
import json  # noqa: E402

from sim.customer_state_layer import (  # noqa: E402
    first_move_out,
    moves_active,
    term_window_under_move,
)

_T0, _T1 = dt.date(2020, 3, 1), dt.date(2021, 3, 1)


def test_every_outcome_of_the_term_window_is_reachable():
    """Defect: a gate that cuts every term (or none) passes each per-branch assertion."""
    outcomes = {
        term_window_under_move(_T0, _T1, None),
        term_window_under_move(_T0, _T1, dt.date(2020, 9, 1)),
        term_window_under_move(_T0, _T1, _T0),
        term_window_under_move(_T0, _T1, _T1),
    }
    assert outcomes == {(_T1, False), (dt.date(2020, 9, 1), True), (None, False)}


def test_a_move_on_the_terms_first_day_takes_the_whole_term_and_on_its_end_takes_none():
    """Defect: an off-by-one that bills the mover a day after leaving, or drops a supplied term."""
    assert term_window_under_move(_T0, _T1, _T0) == (None, False)
    assert term_window_under_move(_T0, _T1, _T0 + dt.timedelta(days=1)) == (
        _T0 + dt.timedelta(days=1), True)
    assert term_window_under_move(_T0, _T1, _T1) == (_T1, False)


def test_the_first_move_out_is_the_yearly_draw_unchanged():
    """Defect: the run's window re-keying the draw, so a household's moves depend on its start."""
    found = 0
    for i in range(400):
        occ = Occupancy.of_customer(f"R{i}", TenureType.PRIVATE_RENTER)
        move = first_move_out(occ, dt.date(2016, 1, 1), dt.date(2025, 6, 8), 7)
        if move is None:
            continue
        found += 1
        assert move == draw_home_move(occ, move.move_date.year, 7)
        assert all(draw_home_move(occ, y, 7) is None for y in range(2016, move.move_date.year))
    assert found > 0


def test_a_move_before_the_supply_window_is_not_a_departure_from_the_book():
    """Defect: a household won mid-run losing its first term to a move drawn before it joined."""
    occ = next(
        o for o in (Occupancy.of_customer(f"P{i}", TenureType.PRIVATE_RENTER) for i in range(500))
        if draw_home_move(o, 2019, 3) is not None
    )
    moved = draw_home_move(occ, 2019, 3).move_date
    later = first_move_out(occ, moved, dt.date(2025, 1, 1), 3)
    assert later is None or later.move_date > moved


def test_the_book_moves_at_the_sourced_rate_over_a_year():
    """Defect: the window reading drops or doubles a year, so the run's rate is not the EHS one."""
    p = home_move_rate_per_household_year(TenureType.PRIVATE_RENTER)
    n = 4000
    moved = sum(
        first_move_out(Occupancy.of_customer(f"Y{i}", TenureType.PRIVATE_RENTER),
                       dt.date(2021, 1, 1), dt.date(2022, 1, 1), 5) is not None
        for i in range(n)
    )
    # Window is (Jan 1, Jan 1): a move drawn ON Jan 1 is excluded, about 1/365 of moves.
    assert abs(moved / n - p) < 4 * math.sqrt(p * (1 - p) / n)


def test_the_activation_file_says_on_or_off_and_nothing_else(tmp_path):
    """Defect: a malformed or absent switch silently read as one of its two values."""
    f = tmp_path / "a.json"
    for value in (True, False):
        f.write_text(json.dumps({"activated": {"value": value}}))
        assert moves_active(f) is value
    f.write_text(json.dumps({"activated": {"value": "true"}}))
    with pytest.raises(ValueError):
        moves_active(f)
    with pytest.raises(FileNotFoundError):
        moves_active(tmp_path / "absent.json")
    assert isinstance(moves_active(), bool)


def test_only_a_domestic_account_record_moves_home():
    """Defect: the domestic EHS hazard applied to an I&C or SME site, or to a missing record."""
    from sim.customer_state_layer import account_move_out

    window = (dt.date(2016, 1, 1), dt.date(2025, 6, 8), 9)
    domestic = [{"customer_id": f"H{i}", "segment": "resi"} for i in range(200)]
    movers = [c for c in domestic if account_move_out(c, *window) is not None]
    assert movers
    for segment in ("ic", "sme"):
        assert all(account_move_out({**c, "segment": segment}, *window) is None for c in movers)
    assert account_move_out(None, *window) is None
    assert account_move_out({"customer_id": movers[0]["customer_id"]}, *window) is not None
