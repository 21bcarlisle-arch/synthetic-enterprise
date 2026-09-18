"""`J_svt` has no published value, and what the record DOES establish is a floor — held as one.

WHAT THIS IS ABOUT. `J_svt` is the rate at which a household on the default tariff takes a fixed
deal with its EXISTING supplier. The world needs it to say how often an SVT household converts, and
no published series carries it: Ofgem CIM question C4 measures internal switching over ALL
households, which mixes the default-tariff route with fixed-term active renewal, and nothing cuts
that row by the tariff the respondent was on BEFORE the move.

`tools.published_route_split` answers that in two pieces, and the SHAPE of the answer is what these
controls hold: `SVT_INTERNAL_CONVERSION_RATE = None` with a named reason, and
`svt_internal_conversion_floor()` — a BOUND, derived from the identity the module already states
and never a number anyone picked:

    I = s*J_svt + (1-s)*0.35*(1-phi)   =>   J_svt >= (I - (1-s)*0.35) / s

WHY A FILE FOR THIS AND NOT A LEG ON THE WORLD'S OWN SUITE. The world-side control — that the
conversion rate the world PRODUCES clears this floor — belongs beside the builder that produces it
and is not here. What is here is the arithmetic and the epistemics of the bound itself, which stand
whether or not any world reads them, and which would otherwise be checked by nothing: a floor that
silently became a maximum, or a `None` that silently became the floor, moves no test in `simulation/`.

WHAT EACH TEST NAMES AS ITS OWN DEFECT (CONTROLS_THAT_CANNOT_FAIL):

  * `test_the_point_estimate_is_a_named_gap_and_not_the_floor_wearing_its_name` — the defect where
    `SVT_INTERNAL_CONVERSION_RATE` acquires the floor's value. A bound written into a slot named
    for a point estimate is read as established within a week, and this repository has paid for
    that shape repeatedly. Also refuses a bare `None`: the gap must carry its reason, because a
    silent `None` and a declared `None` collapse into the flattering branch at the first reader.
  * `test_the_binding_floor_is_the_minimum_across_waves_and_not_the_most_permissive_one` — the
    defect where the binding figure is taken from the wave that allows the largest floor, which is
    the claim only one wave supports dressed as the claim every wave supports.
  * `test_every_wave_floor_is_recomputed_from_that_waves_own_published_inputs` — the defect where
    the table is a pasted set of literals that no longer follows from the register it cites. The
    floors are recomputed here from `default_tariff_share`, `_renewal_route_internal_ceiling` and
    the observation's own counts, so a drifting input reds this rather than passing quietly.
  * `test_the_default_share_is_taken_at_the_LARGEST_published_value` — the defect where the
    conservative direction is flipped. `s` divides the excess, so a SMALLER `s` RAISES the floor;
    taking the largest published share is what makes a world that clears the floor unarguable, and
    the flip would be invisible in every other assertion here.
  * `test_the_rate_is_the_un_annualised_six_month_one_and_the_reading_says_so` — the defect where
    `I` is annualised to match the annual ceiling it is netted against. That raises the floor too,
    and it is the one choice a reader would assume had been made. The unit field is asserted to
    state the six months, because a bound whose unit is not on its face gets compared to anything.
  * `test_a_wave_with_no_established_default_share_is_named_and_not_silently_dropped` — the defect
    where a wave the record cannot price disappears from the reading and `waves_with_a_floor`
    reads as though the record covered everything. An empty evidence set reads as no complaint.
  * `test_the_floor_is_strictly_positive_because_that_is_the_whole_fidelity_claim` — the defect
    where the identity is rearranged into a bound that is true of every world. If the published
    internal rate did NOT exceed the renewal route's ceiling the floor would be <= 0, the bound
    would constrain nothing, and a world with no SVT-to-fixed route at all would clear it.

R15 MUTATIONS, EXECUTED against a local expression of the reading rather than by editing the shared
module — the subject is imported by live builders and a mutation is a shared-tree write. OBSERVED
result recorded below, not intended result; live binding floor 0.044919, per-wave floors
[0.068685, 0.060856, 0.083203, 0.044919, 0.050957, 0.051386]:

    M1  `binding_floor` taken as max(floors) instead of min  -> 0.044919 -> 0.083203
        -> `binding_floor_is_the_minimum` FIRES, alone
    M2  `s` taken at the SMALLEST published default share    -> 0.044919 -> 0.050534
        -> `default_share_is_taken_at_the_LARGEST` FIRES, and so does
           `every_wave_floor_is_recomputed`. TWO legs, and the second is the honest one to name:
           recomputation catches the arithmetic, the share leg catches the DIRECTION and says so.
           A silent M2 would have been the flattering reading — it is not silent, and the reason
           it fires twice is that recomputation is keyed to the same register.
    M3  `SVT_INTERNAL_CONVERSION_RATE` and the reading's `the_point_estimate_is` set to the floor
        -> `point_estimate_is_a_named_gap` FIRES, alone
    M4  wave 6 dropped from `per_wave` and `binding_floor` recomputed over the remainder
        -> FOUR legs fire: `every_wave_floor_is_recomputed` on the count,
           `a_wave_with_no_established_default_share_is_named` on the wave set, and the
           presence guards in `default_share_is_taken_at_the_LARGEST` and
           `rate_is_the_un_annualised_six_month_one`. Those two guards exist because without
           them a dropped wave raised `KeyError` — a red, but an unnamed one, and a reader
           chasing a KeyError does not learn that a published wave went missing.
           THE BINDING FLOOR DID NOT MOVE (0.044919 either way), because wave 6 is not the
           binding wave: a control keyed to the published figure alone passes this mutation.
"""
from __future__ import annotations

from tools.published_route_split import (
    SVT_INTERNAL_CONVERSION_RATE,
    SVT_INTERNAL_CONVERSION_RATE_GAP,
    SWITCHER_SPLIT_OBSERVATIONS,
    _renewal_route_internal_ceiling,
    svt_internal_conversion_floor,
)
from tools.published_tariff_mix import default_tariff_share


def _reading() -> dict:
    return svt_internal_conversion_floor()


def test_the_point_estimate_is_a_named_gap_and_not_the_floor_wearing_its_name():
    assert SVT_INTERNAL_CONVERSION_RATE is None, (
        "J_svt has acquired a value. Nothing published establishes the rate at which a default "
        "household takes a fix with its existing supplier -- only the floor this module derives -- "
        "and a bound written into a slot named for a point estimate is read as established."
    )
    assert SVT_INTERNAL_CONVERSION_RATE_GAP.strip(), (
        "the gap is silent. A `None` that declares its reason and a `None` that is silence collapse "
        "into the flattering branch at the first reader who has to choose between them."
    )
    reading = _reading()
    assert reading["the_point_estimate_is"] is None, (
        f"the reading publishes {reading['the_point_estimate_is']} as the point estimate. The "
        f"module's constant and the reading it feeds must say the same `None`, or a reader takes "
        f"whichever of the two is more convenient."
    )
    assert reading["why_there_is_no_point_estimate"].strip(), (
        "the reading's gap carries no reason, so a reader cannot tell an unestablished quantity "
        "from one nobody looked up"
    )
    assert reading["binding_floor"] != SVT_INTERNAL_CONVERSION_RATE, (
        "the reading hands back the floor as the point estimate, which is the whole distinction "
        "this pair of fields exists to keep"
    )


def test_the_binding_floor_is_the_minimum_across_waves_and_not_the_most_permissive_one():
    reading = _reading()
    floors = [w["floor_on_j_svt"] for w in reading["per_wave"] if w["floor_on_j_svt"] is not None]
    assert floors, "no wave produced a floor; this control has nothing to grade"
    assert reading["binding_floor"] == min(floors), (
        f"the binding floor is {reading['binding_floor']} against a per-wave minimum of "
        f"{min(floors)}. The binding figure must be the rate EVERY wave independently establishes, "
        f"not the largest one some wave permits -- max would give {max(floors)}."
    )
    assert reading["waves_with_a_floor"] == len(floors)


def test_every_wave_floor_is_recomputed_from_that_waves_own_published_inputs():
    by_wave = {w["wave"]: w for w in _reading()["per_wave"]}
    assert len(by_wave) == len(SWITCHER_SPLIT_OBSERVATIONS), (
        "a published wave is missing from the reading"
    )
    for obs in SWITCHER_SPLIT_OBSERVATIONS:
        row = by_wave[obs.wave]
        ceiling = _renewal_route_internal_ceiling(obs.recall_window_years)["ceiling"]
        shares = [default_tariff_share(y, "all_domestic") for y in obs.recall_window_years]
        established = [b[1] for b in shares if b is not None]
        expected = (
            None if (ceiling is None or not established)
            else round((obs.internal_rate_of_all_households - ceiling) / max(established), 6)
        )
        assert row["floor_on_j_svt"] == expected, (
            f"wave {obs.wave}'s floor is {row['floor_on_j_svt']} but its own published inputs give "
            f"{expected}. The table has come loose from the register it cites."
        )
        assert row["renewal_route_internal_ceiling"] == ceiling
        assert row["internal_rate_of_all_households_6mo"] == round(
            obs.internal_rate_of_all_households, 6
        )


def test_the_default_share_is_taken_at_the_LARGEST_published_value():
    """`s` divides the excess, so a SMALLER `s` gives a LARGER floor. The direction is the point."""
    by_wave = {w["wave"]: w for w in _reading()["per_wave"]}
    checked = 0
    for obs in SWITCHER_SPLIT_OBSERVATIONS:
        assert obs.wave in by_wave, (
            f"wave {obs.wave} is published but absent from the reading, so the choice of `s` this "
            f"control grades is made for it somewhere nothing can see"
        )
        bands = [default_tariff_share(y, "all_domestic") for y in obs.recall_window_years]
        established = [b for b in bands if b is not None]
        if not established:
            continue
        upper = max(b[1] for b in established)
        lower = min(b[0] for b in established)
        assert by_wave[obs.wave]["largest_published_default_share"] == upper, (
            f"wave {obs.wave} prices its floor against a default share of "
            f"{by_wave[obs.wave]['largest_published_default_share']} when the record's largest is "
            f"{upper}. Dividing by a SMALLER SVT population raises the floor, which is the "
            f"un-conservative direction and the one this bound must never take."
        )
        if upper != lower:
            checked += 1
    assert checked, (
        "every published default share is a point, so this control cannot tell an upper bound from "
        "a lower one and is not grading the choice it names"
    )


def test_the_rate_is_the_un_annualised_six_month_one_and_the_reading_says_so():
    reading = _reading()
    unit = reading["binding_floor_unit"].lower()
    assert "six month" in unit or "six_month" in unit or "SIX MONTH".lower() in unit, (
        f"the floor's unit does not state its recall window: {reading['binding_floor_unit']!r}. A "
        f"bound whose unit is not on its face gets compared to anything."
    )
    by_wave = {w["wave"]: w for w in reading["per_wave"]}
    for obs in SWITCHER_SPLIT_OBSERVATIONS:
        assert obs.wave in by_wave, (
            f"wave {obs.wave} is published but absent from the reading, so its recall window is "
            f"not graded by anything here"
        )
        assert by_wave[obs.wave]["internal_rate_of_all_households_6mo"] == round(
            obs.internal_weighted / obs.base_weighted, 6
        ), (
            f"wave {obs.wave}'s internal rate has been annualised or otherwise scaled. It is netted "
            f"against an ANNUAL ceiling un-annualised on purpose: annualising raises the floor, and "
            f"an annual J_svt is at least its own six-month rate, so the six-month floor is a valid "
            f"annual floor and a conservative one."
        )


def test_a_wave_with_no_established_default_share_is_named_and_not_silently_dropped():
    reading = _reading()
    for row in reading["per_wave"]:
        assert "years_with_no_established_default_share" in row, (
            f"wave {row['wave']} does not say which of its years the record could not price"
        )
        if row["floor_on_j_svt"] is None:
            assert (
                row["years_with_no_established_default_share"]
                or row["renewal_route_internal_ceiling"] is None
            ), (
                f"wave {row['wave']} produced no floor and named no reason. An unpriceable wave "
                f"that vanishes leaves `waves_with_a_floor` reading as though the record covered "
                f"everything."
            )
    named = {w["wave"] for w in reading["per_wave"]}
    assert named == {o.wave for o in SWITCHER_SPLIT_OBSERVATIONS}, (
        "a wave has been dropped from the reading rather than carried with its reason"
    )


def test_the_floor_is_strictly_positive_because_that_is_the_whole_fidelity_claim():
    """A bound at or below zero is true of a world with no SVT-to-fixed route at all."""
    reading = _reading()
    assert reading["binding_floor"] is not None, "the record establishes no floor at all"
    assert reading["binding_floor"] > 0, (
        f"the binding floor is {reading['binding_floor']}, which constrains nothing: a world where "
        f"no default-tariff household ever takes a fix clears it. The bound is only informative "
        f"because published internal switching EXCEEDS what the fixed-renewal route can produce, "
        f"and a non-positive floor means that excess has gone -- which is a finding about the "
        f"record, not a test to relax."
    )
    for row in reading["per_wave"]:
        if row["floor_on_j_svt"] is not None:
            assert row["floor_on_j_svt"] > 0, (
                f"wave {row['wave']} establishes a non-positive floor ({row['floor_on_j_svt']}), so "
                f"its internal switching no longer exceeds the renewal route's ceiling. The "
                f"binding floor is a MINIMUM over these and would silently become vacuous."
            )
