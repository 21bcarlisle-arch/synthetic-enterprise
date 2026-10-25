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
    assert outcomes == {(_T1, False), (dt.date(2020, 9, 1), True), (None, False), (_T1, True)}


def test_a_move_on_the_terms_first_day_takes_the_whole_term_and_on_its_end_closes_it():
    """Defect: an off-by-one that bills the mover a day after leaving, or drops a supplied term."""
    assert term_window_under_move(_T0, _T1, _T0) == (None, False)
    assert term_window_under_move(_T0, _T1, _T0 + dt.timedelta(days=1)) == (
        _T0 + dt.timedelta(days=1), True)
    assert term_window_under_move(_T0, _T1, _T1) == (_T1, True)


def test_every_move_in_the_window_is_seen_by_exactly_one_of_consecutive_terms():
    """Defect: a move dated on a term boundary falls between two terms and is seen by neither, so
    the vacated meter is never admitted (seed 61102: SYN-2016-572's electricity leg on 2017-07-01,
    a cap-quarter start). Swept over every day of four quarterly terms, boundaries included."""
    starts = [dt.date(2017, 1, 1), dt.date(2017, 4, 1), dt.date(2017, 7, 1),
              dt.date(2017, 10, 1), dt.date(2018, 1, 1)]
    terms = list(zip(starts, starts[1:]))
    day = starts[0] + dt.timedelta(days=1)
    boundary_moves = 0
    while day <= starts[-1]:
        seen = [t for t in terms if term_window_under_move(*t, day)[1]]
        assert len(seen) == 1, f"a move on {day} is seen by {len(seen)} terms"
        boundary_moves += day in starts
        day += dt.timedelta(days=1)
    assert boundary_moves == 4, "the sweep must reach every boundary, or it proves nothing"


def test_an_occupant_admitted_at_a_boundary_move_can_be_priced_and_an_undrawn_id_cannot():
    """Defect: the run creates an incoming household whose electricity leg was never registered,
    and the C30 contact's elasticity draw refuses it (B_61102 and C_61102 died on OCC-b9601279e7d4).

    The run's own steps, in its order: each leg's consecutive terms are asked about the household's
    one move, and a leg that reports it admits the incoming occupant's record onto the book. The
    move here lands on the electricity leg's quarter boundary and inside the gas leg's term."""
    from company.interfaces.supply_book import incoming_occupant_supply_points
    from saas.customers import get_customer
    from sim.customer_state_layer import incoming_occupant_record
    from simulation.household import GAS_LEG_ID_SUFFIX, household_of
    from simulation.population_draw import price_elasticity_for_customer

    occupancy = Occupancy.of_customer("C1", TenureType.PRIVATE_RENTER)
    move = next(m for y in range(2016, 2026) for s in range(1, 400)
                if (m := draw_home_move(occupancy, y, s)) is not None)
    boundary = move.move_date
    elec_terms = [(boundary - dt.timedelta(days=91), boundary),
                  (boundary, boundary + dt.timedelta(days=92))]
    gas_terms = [(boundary - dt.timedelta(days=200), boundary + dt.timedelta(days=165))]
    book = incoming_occupant_supply_points()
    try:
        for leg_id, terms in (("C1", elec_terms), ("C1" + GAS_LEG_ID_SUFFIX, gas_terms)):
            for term in terms:
                if term_window_under_move(*term, boundary)[1]:
                    book.append(incoming_occupant_record(get_customer(leg_id), move))
        household = household_of(book[-1]["customer_id"])
        assert household == move.incoming.occupancy_id
        assert price_elasticity_for_customer(household, 20260724) > 0.0
        with pytest.raises(ValueError, match="no supply point"):
            price_elasticity_for_customer("OCC-000000000000", 20260724)
    finally:
        book.clear()


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


def _register_row(toggle_id: str) -> dict:
    import yaml

    from simulation.meter_reads import ASSUMPTION_TOGGLES_PATH
    rows = yaml.safe_load(ASSUMPTION_TOGGLES_PATH.read_text())["toggles"]
    return next(r for r in rows if r["id"] == toggle_id)


@pytest.mark.parametrize("setting", ["low", "default", "high"])
def test_the_unnamed_window_is_the_registers_toggle_at_every_setting(setting):
    """Defect: a CoT duration typed into the layer, or one setting wired to another's value."""
    row = _register_row("q1_unnamed_months_per_cot")
    assert csl.unnamed_months_per_move(setting) == float(row[setting])
    assert csl.unnamed_kwh_after_move(1200.0, setting) == pytest.approx(100.0 * float(row[setting]))


def test_the_unnamed_energy_moves_with_the_meter_points_annual_quantity_and_the_setting():
    """Defect: a flat per-move kWh, or a rate that ignores the toggle's range."""
    low, mid, high = (csl.unnamed_kwh_after_move(2700.0, s) for s in ("low", "default", "high"))
    assert 0.0 < low < mid < high
    assert csl.unnamed_kwh_after_move(5400.0) == pytest.approx(2 * mid)


def test_the_unnamed_window_ends_the_registers_months_after_the_move_at_every_setting():
    """B7 slice 4. Defect: the window typed as a day count, or not moving with the toggle."""
    moved = dt.date(2016, 4, 21)
    days = {s: (csl.unnamed_until(moved, s) - moved).days for s in ("low", "default", "high")}
    for setting, n in days.items():
        assert n == round(csl.unnamed_months_per_move(setting) * 365.25 / 12.0), setting
    assert 0 < days["low"] < days["default"] < days["high"]


@pytest.mark.parametrize("annual", [None, 0.0, -1.0, float("nan")])
def test_no_annual_quantity_is_no_answer_not_a_zero_gap(annual):
    """Defect: a missing rate reported as 0 kWh, which reads as "this move left no gap"."""
    assert csl.unnamed_kwh_after_move(annual) is None


def test_the_incoming_account_is_the_premises_meter_under_a_new_occupancy():
    """B7 slice 3. Defect: the incoming record keeps the mover's id or terms, or drops the meter
    point's annual quantity, or carries the void onto the supplier's book."""
    from sim.customer_state_layer import incoming_leg_id, incoming_occupant_record

    seed = 7
    for year in range(2016, 2060):
        move = draw_home_move(Occupancy.of_customer("C9", TenureType.PRIVATE_RENTER), year, seed)
        if move is not None:
            break
    assert move is not None
    gas_leg = {"customer_id": "C9g", "commodity": "gas", "aq_kwh": 12000, "successor_of": "C8",
               "tariff_type": "fixed", "acquisition_date": "2016-01-01"}
    record = incoming_occupant_record(gas_leg, move)
    assert record["customer_id"] == incoming_leg_id(move.incoming.occupancy_id, "C9g")
    assert record["customer_id"] == move.incoming.occupancy_id + "g"
    assert incoming_leg_id(move.incoming.occupancy_id, "C9") == move.incoming.occupancy_id
    assert record["aq_kwh"] == 12000 and record["incoming_occupant_of"] == "C9g"
    assert record["acquisition_date"] == move.move_date.isoformat()
    assert (record["terms"], record["tariff_type"]) == ("deemed_contract", "svt")
    assert "successor_of" not in record
    assert not {"occupancy_start_unknown_reason", "start_date", "move_date"} & set(record)
    assert gas_leg["customer_id"] == "C9g" and gas_leg["tariff_type"] == "fixed"


# ── B7 slice (e)1: a sole occupant's death ───────────────────────────────────────────────────

from sim.customer_state_layer import (  # noqa: E402
    ESTATE_PAYER,
    SOLE_OCCUPANT_DEATH_HAZARD_BY_YEAR,
    draw_sole_occupant_death,
    first_sole_occupant_death,
    is_sole_pensioner_home,
    sole_occupant_death_hazard,
)


def _deaths(year: int = 2020, n: int = N, *, people: int = 1, pensioner: bool = True):
    return [draw_sole_occupant_death(Occupancy.of_customer(f"D{i}", TenureType.OWNER_OCCUPIER),
                                     year, 13, people_count=people, pensioner_present=pensioner)
            for i in range(n)]


def test_a_death_can_be_drawn_and_only_a_sole_pensioner_home_can_draw_one():
    """Defect: an eligibility guard that refuses everything passes every per-death assertion;
    one that admits everything kills the occupant of a family home and ends their account."""
    eligible = _deaths()
    assert any(d is None for d in eligible) and any(d is not None for d in eligible)
    assert all(d is None for d in _deaths(people=2))
    assert all(d is None for d in _deaths(pensioner=False))


def test_the_drawn_rate_is_the_derived_hazard_within_its_sampling_bound():
    """Defect: the hazard restated, read from the wrong year, or detached from its table. Graded
    against the TABLE, not `sole_occupant_death_hazard`: a draw checked against the function it
    calls agrees with any number that function returns (a 0.0065 mutant passed that way)."""
    n = 20000
    for year in (2019, 2020):
        p = SOLE_OCCUPANT_DEATH_HAZARD_BY_YEAR[year]
        observed = sum(d is not None for d in _deaths(year, n)) / n
        assert abs(observed - p) < 4 * math.sqrt(p * (1 - p) / n), year


def test_the_hazard_covers_the_run_window_and_refuses_outside_it():
    """Defect: a year past the ONS series silently borrows a neighbour, or reads zero."""
    assert set(SOLE_OCCUPANT_DEATH_HAZARD_BY_YEAR) == set(range(2016, 2026))
    with pytest.raises(ValueError, match="2016-2025"):
        sole_occupant_death_hazard(2026)


def test_the_hazard_is_mortality_per_home_not_the_household_floor():
    """Defect: the 0.6-0.7% share of ALL households typed in as the per-home hazard (§5 choice 4).
    And the record's COVID year flattened away."""
    assert all(0.04 < h < 0.06 for h in SOLE_OCCUPANT_DEATH_HAZARD_BY_YEAR.values())
    assert max(SOLE_OCCUPANT_DEATH_HAZARD_BY_YEAR, key=SOLE_OCCUPANT_DEATH_HAZARD_BY_YEAR.get) == 2020


def test_a_death_is_one_credit_exit_with_a_named_payer_and_one_deemed_entry():
    death = next(d for d in _deaths() if d is not None)
    ended, incoming = death.transitions
    assert isinstance(ended, OccupancyEnded) and isinstance(incoming, OccupancyStarted)
    assert ended.premise_id == incoming.premise_id
    assert ended.occupancy_id != incoming.occupancy_id
    assert ended.end_date == death.death_date == incoming.starts_no_earlier_than
    assert incoming.terms == DEEMED_TERMS
    assert incoming.start_date is None and incoming.start_date_unknown_reason
    assert death.payer == ESTATE_PAYER


def test_the_insolvent_estate_share_is_a_named_gap_not_the_movers_gone_away_rate():
    """Defect: the move-out's 0.12 borrowed for a debtor who has not gone away (§5 choice 1(b))."""
    death = next(d for d in _deaths() if d is not None)
    assert death.insolvent_share is None
    assert "gone-away" in death.insolvent_share_unknown_reason


def test_a_window_ending_on_new_year_does_not_ask_the_year_past_the_record():
    occ = Occupancy.of_customer("D7", TenureType.OWNER_OCCUPIER)
    first_sole_occupant_death(occ, dt.date(2016, 1, 1), dt.date(2026, 1, 1), 13,
                              people_count=1, pensioner_present=True)
    with pytest.raises(ValueError, match="2016-2025"):
        first_sole_occupant_death(occ, dt.date(2016, 1, 1), dt.date(2026, 1, 2), 13,
                                  people_count=1, pensioner_present=True)


def test_the_first_death_falls_inside_the_window_and_is_the_yearly_draw_unchanged():
    for i in range(400):
        occ = Occupancy.of_customer(f"W{i}", TenureType.SOCIAL_RENTER)
        found = first_sole_occupant_death(occ, dt.date(2017, 3, 1), dt.date(2024, 6, 1), 9,
                                          people_count=1, pensioner_present=True)
        if found is None:
            continue
        assert dt.date(2017, 3, 1) < found.death_date < dt.date(2024, 6, 1)
        assert found == draw_sole_occupant_death(occ, found.death_date.year, 9, people_count=1,
                                                 pensioner_present=True)


def test_adding_the_death_streams_left_every_move_draw_identical(monkeypatch):
    """Defect: the death draw keyed on a move stream, so turning deaths on re-picks who moves."""
    before = _moves(TenureType.PRIVATE_RENTER, n=1500)
    trimmed = tuple(s for s in csl.SUBSTREAMS if s not in ("sole_occupant_death", "death_date"))
    monkeypatch.setattr(csl, "SUBSTREAMS", trimmed)
    assert _moves(TenureType.PRIVATE_RENTER, n=1500) == before


@pytest.mark.parametrize("people, pensioner", [(0, True), (True, True), (1.0, True), (1, 1)])
def test_a_malformed_home_fails_closed(people, pensioner):
    with pytest.raises((ValueError, TypeError)):
        is_sole_pensioner_home(people, pensioner)
