"""W2_13 — occupancy → consumption VOLUME and SHAPE.

Every assertion here is against the ANCHORED SHAPE of the published response
(DESNZ NEED 2023 per-adult medians; DESNZ/BRE EFUS 2017 daytime occupancy),
never against a value re-derived from the code under test (R15). Each control
test names the defect it fires on, and the mutation tests prove it fires.

The defect this atom fixes, stated as a test (`test_the_defect_w2_13_fixes`):
before W2_13 a 4-person and a 1-person household on the same base profile and
the same weather ended the day at the SAME daily total — occupancy only
redistributed load across the day.
"""
import random

import pytest

import simulation.demand_model as dm
from simulation.demand_model import (
    CHILD_ADULT_EQUIVALENT_RANGE,
    DAYTIME_RATE_TO_KWH_ELASTICITY_RANGE,
    EV_CHARGING_KWH_PER_NIGHT,
    HOUSEHOLD_SIZE_POPULATION_SHARE,
    PERIODS_PER_DAY,
    UnanchoredReferencePopulation,
    build_demand_shape,
    child_adult_equivalence,
    daytime_rate_elasticity,
    daytime_shape_is_mean_neutral,
    need_volume_index,
    occupancy_multiplier,
    occupancy_volume_factor,
    population_mean_daytime_multiplier,
    population_mean_volume_factor,
    volume_factor_is_unbiased,
    volume_factor_normaliser,
)

FLAT_SHAPE = [1.0] * PERIODS_PER_DAY
MILD_TEMP = 16.0  # no heating or cooling degree days

# The ONS TS017 reference population, as (sizes, weights).
_POP_SIZES = list(HOUSEHOLD_SIZE_POPULATION_SHARE)
_POP_WEIGHTS = [HOUSEHOLD_SIZE_POPULATION_SHARE[n] for n in _POP_SIZES]

# Periods used by name so the window claims are readable.
_MIDDAY = 25          # 12:00-12:30 — inside the composition-response window
_EVENING = 40         # 19:30-20:00 — EFUS 88% occupied regardless of composition
_OVERNIGHT = 4        # 01:30-02:00 — EFUS 94% occupied regardless of composition


def elec_property(occupancy="single", people_count=None, **extra):
    record = {
        "heating_system": "electric_storage",
        "occupancy_pattern": occupancy,
        "assets": {"ev": False, "solar": False, "smart_meter": True},
    }
    if people_count is not None:
        record["people_count"] = people_count
    record.update(extra)
    return record


# ---------------------------------------------------------------------------
# The defect
# ---------------------------------------------------------------------------

def test_the_defect_w2_13_fixes_headcount_now_moves_the_daily_total():
    """A 4-person and a 1-person home on the same profile used to end the day
    on the same total. They must not any more — and the gap must be of the
    order NEED publishes (a 4-adult home's median electricity is 1.89x a
    1-adult home's), not a rounding difference."""
    one = build_demand_shape(FLAT_SHAPE, MILD_TEMP, "electricity",
                             elec_property(people_count=1, customer_id="H1"))
    four = build_demand_shape(FLAT_SHAPE, MILD_TEMP, "electricity",
                              elec_property(people_count=4, customer_id="H4"))
    # Pre-W2_13 this ratio was exactly 1.0 for any two headcounts.
    assert sum(four) / sum(one) > 1.8

    # The VOLUME component alone reproduces the published NEED A14 ratio
    # (3,772 / 1,993 = 1.893) — asserted against the medians directly, not
    # against anything the module computed. The daily total sits a little
    # ABOVE it because the daytime SHAPE response also rises with headcount
    # (aggregate-neutral across the population, not per household).
    volume_ratio = (occupancy_volume_factor(4, "electricity")
                    / occupancy_volume_factor(1, "electricity"))
    assert volume_ratio == pytest.approx(3772.0 / 1993.0, rel=0.005)
    assert sum(four) / sum(one) >= volume_ratio


# ---------------------------------------------------------------------------
# VOLUME — the NEED per-adult sublinear curve
# ---------------------------------------------------------------------------

def test_electricity_volume_step_is_sublinear_first_step_dominates():
    """NEED A14: +43.8% for the 2nd adult, +9.5% for the 5th. The 1→2 step
    must be MATERIALLY larger than the 4→5 step — that sublinearity is the
    anchor, and a flat linear per-person scalar would make the two equal."""
    f = {n: occupancy_volume_factor(n, "electricity") for n in range(1, 6)}
    first_step = (f[2] - f[1]) / f[1]
    last_step = (f[5] - f[4]) / f[4]
    assert first_step == pytest.approx(2867.0 / 1993.0 - 1.0, rel=0.01)
    assert last_step == pytest.approx(4129.0 / 3772.0 - 1.0, rel=0.01)
    assert first_step > 3.0 * last_step  # published ratio is 43.8/9.5 ≈ 4.6


def test_gas_first_step_is_much_smaller_than_the_electricity_first_step():
    """NEED A13 vs A14: gas +24.3% on 1→2 vs electricity +43.8%. Space heating
    tracks the dwelling, not the headcount; the shared electrical fixed base
    is what makes the electricity step so steep."""
    e = occupancy_volume_factor(2, "electricity") / occupancy_volume_factor(1, "electricity")
    g = occupancy_volume_factor(2, "gas") / occupancy_volume_factor(1, "gas")
    assert g == pytest.approx(10624.0 / 8546.0, rel=0.01)
    assert g < e - 0.15


def test_volume_factor_is_monotonically_increasing_and_flat_above_the_top_band():
    for commodity in ("electricity", "gas"):
        f = [occupancy_volume_factor(n, commodity) for n in range(1, 6)]
        assert f == sorted(f)
        assert all(b > a for a, b in zip(f, f[1:]))
        # NEED's top band is "5 or more" — flat above it, never extrapolated.
        assert occupancy_volume_factor(9, commodity) == pytest.approx(f[-1])


def test_population_mean_volume_factor_is_one_for_both_commodities():
    """The response must REDISTRIBUTE volume between households, not re-level
    the aggregate. Expected value is the constant 1.0, not anything computed
    from the module (R15)."""
    for commodity in ("electricity", "gas"):
        mean = population_mean_volume_factor(_POP_SIZES, _POP_WEIGHTS, commodity)
        assert mean == pytest.approx(1.0, abs=1e-9)
        assert volume_factor_is_unbiased(_POP_SIZES, _POP_WEIGHTS, commodity)


def test_unbiased_control_FIRES_when_the_normalisation_is_removed(monkeypatch):
    """R15 mutation: drop the normaliser (the classic 'anchored on a 1-adult
    home' bug) and the control must fire — raw NEED would multiply national
    electricity demand by ~1.45 overnight."""
    monkeypatch.setattr(dm, "volume_factor_normaliser", lambda commodity, ref=None: 1.0)
    mean = dm.population_mean_volume_factor(_POP_SIZES, _POP_WEIGHTS, "electricity")
    assert mean > 1.4
    assert not dm.volume_factor_is_unbiased(_POP_SIZES, _POP_WEIGHTS, "electricity")


def test_unbiased_control_FIRES_on_a_uniformly_inflated_factor(monkeypatch):
    """R15 mutation 2: a 5% across-the-board lift is exactly the silent
    baseline shift this control exists to catch."""
    real = dm.occupancy_volume_factor
    monkeypatch.setattr(dm, "occupancy_volume_factor",
                        lambda *a, **k: real(*a, **k) * 1.05)
    assert not dm.volume_factor_is_unbiased(_POP_SIZES, _POP_WEIGHTS, "gas")


def test_volume_controls_are_not_fail_open_on_empty_or_bad_input():
    with pytest.raises(ValueError):
        population_mean_volume_factor([], [], "electricity")
    with pytest.raises(ValueError):
        population_mean_volume_factor([1, 2], [0.0, 0.0], "electricity")
    with pytest.raises(ValueError):
        population_mean_volume_factor([1, 2], [0.5], "electricity")


@pytest.mark.parametrize("people,children", [(0, 0), (-1, 0), (2, 2), (3, -1), (float("nan"), 0)])
def test_nonsense_headcount_raises_rather_than_silently_returning_one(people, children):
    with pytest.raises(ValueError):
        occupancy_volume_factor(people, "electricity", children_count=children)


# ---------------------------------------------------------------------------
# R10 GAP (a) — adults vs children
# ---------------------------------------------------------------------------

def test_a_child_contributes_less_volume_than_an_adult():
    """NEED is adults-only; EFUS §5.2.2 shows children dampen per-person
    intensity. Four people of whom two are children must sit strictly between
    a 2-adult and a 4-adult household."""
    four_adults = occupancy_volume_factor(4, "electricity", household_key="K")
    two_kids = occupancy_volume_factor(4, "electricity", children_count=2, household_key="K")
    two_adults = occupancy_volume_factor(2, "electricity", household_key="K")
    assert two_adults < two_kids < four_adults


def test_child_weight_is_sampled_from_a_range_never_a_point_estimate():
    """R10: the marginal child increment is unanchored, so it must vary across
    households and stay inside the declared interval."""
    lo, hi = CHILD_ADULT_EQUIVALENT_RANGE
    draws = {child_adult_equivalence(f"H{i}") for i in range(200)}
    assert len(draws) > 150               # genuinely sampled, not a constant
    assert all(lo <= d <= hi for d in draws)
    assert min(draws) < lo + 0.1 and max(draws) > hi - 0.1
    assert hi < 1.0                       # a child never counts as a full adult


def test_elasticity_is_sampled_from_a_range_never_a_point_estimate():
    """R10 GAP (b): the occupancy-rate → kWh conversion magnitude."""
    lo, hi = DAYTIME_RATE_TO_KWH_ELASTICITY_RANGE
    draws = {daytime_rate_elasticity(f"H{i}") for i in range(200)}
    assert len(draws) > 150
    assert all(lo <= d <= hi for d in draws)
    assert 0.0 < lo and hi < 1.0          # neither zero pass-through nor full


def test_missing_household_key_returns_the_interval_midpoint_not_a_global_draw():
    for fn, rng in ((child_adult_equivalence, CHILD_ADULT_EQUIVALENT_RANGE),
                    (daytime_rate_elasticity, DAYTIME_RATE_TO_KWH_ELASTICITY_RANGE)):
        assert fn("") == pytest.approx(sum(rng) / 2.0)


# ---------------------------------------------------------------------------
# C-S2 — RNG substream discipline
# ---------------------------------------------------------------------------

def test_draws_are_deterministic_in_key_and_seed():
    assert child_adult_equivalence("H7", 42) == child_adult_equivalence("H7", 42)
    assert child_adult_equivalence("H7", 42) != child_adult_equivalence("H7", 43)
    assert child_adult_equivalence("H7", 42) != child_adult_equivalence("H8", 42)


def test_draws_do_not_touch_the_global_rng_stream():
    """C-S2: a draw in this substream can never shift another subsystem's
    sequence. The global `random` sequence must be identical with and without
    this atom's draws interleaved."""
    random.seed(1234)
    clean = [random.random() for _ in range(5)]
    random.seed(1234)
    dirty = []
    for _ in range(5):
        child_adult_equivalence(f"X{random.getstate()[1][0]}")
        daytime_rate_elasticity("Y")
        dirty.append(random.random())
    assert clean == dirty


def test_this_atoms_stream_is_distinct_from_w1_5s():
    from simulation import premise_demand
    assert dm.STREAM_NAME != premise_demand.STREAM_NAME
    # Same key, different stream name → different value. The two responses
    # multiply independently; neither re-derives the other.
    assert child_adult_equivalence("P1") != premise_demand.idiosyncratic_factor("P1")


def test_volume_factor_is_deterministic_not_noise():
    """couples_with W1_5: the volume factor is a DETERMINISTIC occupancy
    response. With no children it does not depend on the household key at all
    — the idiosyncratic noise term is W1_5's, and stays W1_5's."""
    a = occupancy_volume_factor(3, "electricity", household_key="A")
    b = occupancy_volume_factor(3, "electricity", household_key="B")
    assert a == b


# ---------------------------------------------------------------------------
# SHAPE — the EFUS daytime composition response
# ---------------------------------------------------------------------------

def test_no_people_count_reproduces_the_pre_w2_13_category_multipliers():
    """The 3-way category is the coarse FALLBACK. These literals are the
    pre-W2_13 shipped values, pinned here independently of the code."""
    assert occupancy_multiplier("single", _MIDDAY) == 0.75
    assert occupancy_multiplier("single", _EVENING) == 1.25
    assert occupancy_multiplier("family", _MIDDAY) == 0.85
    assert occupancy_multiplier("family", _EVENING) == 1.4
    assert occupancy_multiplier("elderly", _MIDDAY) == 1.2
    assert occupancy_multiplier("elderly", _EVENING) == 1.1
    assert occupancy_multiplier("unknown", _EVENING) == occupancy_multiplier("single", _EVENING)


def test_daytime_window_rises_with_household_size():
    """EFUS: 1-person 37% home all day vs 5+-person 67%."""
    values = [occupancy_multiplier("single", _MIDDAY, people_count=n, household_key="K")
              for n in range(1, 6)]
    assert values == sorted(values)
    assert values[-1] > values[0] * 1.1


def test_evening_and_overnight_are_untouched_by_composition():
    """EFUS measures 88% evening / 94% overnight occupancy regardless of
    composition, so there is no composition signal to apply there."""
    for period in list(range(1, 13)) + list(range(34, 49)):
        base = occupancy_multiplier("family", period)
        for n in (1, 5):
            assert occupancy_multiplier("family", period, people_count=n,
                                        household_key="K") == base


def test_the_response_is_confined_to_the_efus_daytime_window():
    """The set of periods the composition response actually moves must be
    exactly 21-33 (10:00-16:30) — EFUS's 09:00-17:00 window minus the morning
    ramp and evening peak."""
    moved = {
        p for p in range(1, PERIODS_PER_DAY + 1)
        if occupancy_multiplier("single", p, people_count=5, household_key="K")
        != occupancy_multiplier("single", p)
    }
    assert moved == set(range(21, 34))


def test_pensioner_presence_and_unemployment_raise_the_daytime_response():
    """EFUS: pensioner-present 63% vs no-pensioner 34%; all-unemployed 60% vs
    someone-employed 35%."""
    kw = dict(people_count=2, household_key="K")
    assert (occupancy_multiplier("single", _MIDDAY, pensioner_present=True, **kw)
            > occupancy_multiplier("single", _MIDDAY, pensioner_present=False, **kw))
    assert (occupancy_multiplier("single", _MIDDAY, someone_employed=False, **kw)
            > occupancy_multiplier("single", _MIDDAY, someone_employed=True, **kw))


def test_population_mean_daytime_multiplier_is_neutral():
    mean = population_mean_daytime_multiplier(_POP_SIZES, _POP_WEIGHTS, period=_MIDDAY)
    assert mean == pytest.approx(1.0, abs=0.02)
    assert daytime_shape_is_mean_neutral(_POP_SIZES, _POP_WEIGHTS, period=_MIDDAY)


def test_shape_neutrality_control_FIRES_when_centred_on_the_wrong_rate(monkeypatch):
    """R15 mutation: centring on EFUS's headline all-household 43% instead of
    this population's own mean daytime rate silently lifts daytime demand ~5%.
    The control must catch it."""
    monkeypatch.setattr(dm, "_reference_daytime_rate", lambda *a, **k: 0.43)
    mean = dm.population_mean_daytime_multiplier(_POP_SIZES, _POP_WEIGHTS, period=_MIDDAY)
    assert mean > 1.02
    assert not dm.daytime_shape_is_mean_neutral(_POP_SIZES, _POP_WEIGHTS, period=_MIDDAY)


# --- The reference is PER CUT-SET (2026-09-23) -----------------------------
# The defect: `_daytime_occupancy_rate` averages the cuts it was GIVEN, so a
# size-only rate and a three-cut rate sit on different scales with different
# population means (0.470 and 0.443). While every caller supplied size alone
# that was invisible. The property record now supplies all three, and a single
# constant centre would score them against the wrong one.

def _three_cut_population():
    """The TS017 sizes crossed with both composition cuts at their EFUS-implied
    shares — the population the property record actually produces now."""
    sizes, weights, pens, emp = [], [], [], []
    for n in _POP_SIZES:
        w = HOUSEHOLD_SIZE_POPULATION_SHARE[n]
        for p, pw in ((True, dm.PENSIONER_PRESENT_POPULATION_SHARE),
                      (False, 1.0 - dm.PENSIONER_PRESENT_POPULATION_SHARE)):
            for e, ew in ((True, dm.SOMEONE_EMPLOYED_POPULATION_SHARE),
                          (False, 1.0 - dm.SOMEONE_EMPLOYED_POPULATION_SHARE)):
                sizes.append(n)
                weights.append(w * pw * ew)
                pens.append(p)
                emp.append(e)
    return sizes, weights, pens, emp


def test_the_marginal_shares_are_efus_own_headline_inverted():
    """Not picked. EFUS publishes each cut's two rates AND the 43% headline they
    average to, which DETERMINES the share. Asserted as the relation, not as
    today's number, so correcting a rate against the source moves the share
    with it instead of reddening this."""
    p = dm.PENSIONER_PRESENT_POPULATION_SHARE
    e = dm.SOMEONE_EMPLOYED_POPULATION_SHARE
    assert (dm.EFUS_DAYTIME_RATE_PENSIONER_PRESENT * p
            + dm.EFUS_DAYTIME_RATE_NO_PENSIONER * (1 - p)
            == pytest.approx(dm.EFUS_DAYTIME_RATE_ALL_HOUSEHOLDS))
    assert (dm.EFUS_DAYTIME_RATE_SOMEONE_EMPLOYED * e
            + dm.EFUS_DAYTIME_RATE_ALL_UNEMPLOYED * (1 - e)
            == pytest.approx(dm.EFUS_DAYTIME_RATE_ALL_HOUSEHOLDS))


def test_a_three_cut_population_is_also_mean_neutral():
    sizes, weights, pens, emp = _three_cut_population()
    mean = population_mean_daytime_multiplier(
        sizes, weights, period=_MIDDAY, pensioners_present=pens, someone_employed=emp)
    assert mean == pytest.approx(1.0, abs=0.02)
    assert daytime_shape_is_mean_neutral(
        sizes, weights, period=_MIDDAY, pensioners_present=pens, someone_employed=emp)


def test_shape_neutrality_control_FIRES_on_a_three_cut_book_centred_size_only(monkeypatch):
    """R15 mutation, and it is the defect this change was written for: pin the
    reference back to the single size-only constant it was before, and the
    three-cut book the property record now produces is re-levelled DOWNWARD —
    measured at 0.9587 on the live 144-home book, a 4.1% silent cut to daytime
    demand wearing a composition response's clothes. The control must fire.

    Note the direction: the older mutation above pushes the mean ABOVE 1.0 and
    this one BELOW it, so a control that only ever caught inflation would pass
    this and is not what is asserted."""
    size_only = dm._reference_daytime_rate(False, False)
    monkeypatch.setattr(dm, "_reference_daytime_rate", lambda *a, **k: size_only)
    sizes, weights, pens, emp = _three_cut_population()
    mean = dm.population_mean_daytime_multiplier(
        sizes, weights, period=_MIDDAY, pensioners_present=pens, someone_employed=emp)
    assert mean < 0.98
    assert not dm.daytime_shape_is_mean_neutral(
        sizes, weights, period=_MIDDAY, pensioners_present=pens, someone_employed=emp)


def test_the_size_only_caller_is_byte_identical_to_before():
    """The legacy path must not move at all. A caller who knows only the
    headcount is centred on 0.470 exactly as it was pre-2026-09-23."""
    assert dm._reference_daytime_rate(False, False) == pytest.approx(
        sum(share * dm._daytime_occupancy_rate(n, None, None)
            for n, share in HOUSEHOLD_SIZE_POPULATION_SHARE.items())
    )
    assert dm._reference_daytime_rate(True, True) < dm._reference_daytime_rate(False, False)


# --- The VOLUME centre is per cut-set too (2026-09-23, instance TWO) -------
# The same class, one function along. `occupancy_volume_factor`'s numerator is
# `adults + w·children` — a VARIABLE number of terms — and its denominator was
# `volume_factor_normaliser(commodity)`, cached on commodity alone and computed
# over households read as ALL ADULTS. So the mean-1 claim held only for the
# all-adult cut-set, and nothing said so.
#
# WHAT MAKES THIS INSTANCE DIFFERENT, and it is the finding: the R15 band over
# it (0.02) is WIDER than the defect (measured 1.5% on the live book), so the
# control built to catch exactly this class could not catch this instance. The
# mechanism here is therefore a named REFUSAL, not a band.

#: An illustrative joint `(people_count, children_count, share)` reference.
#: NOT an anchor and deliberately not published as one — the population split
#: is R10 GAP (a) and `CHILDREN_WITHIN_SIZE_REFERENCE` is `None` in the module
#: because of it. Its job here is to be A reference, so the PROPERTY below can
#: be asserted over whatever reference a caller supplies.
_CHILDREN_REF = ((1, 0, 0.301), (2, 0, 0.340),
                 (3, 0, 0.100), (3, 1, 0.060),
                 (4, 0, 0.060), (4, 2, 0.069),
                 (5, 0, 0.030), (5, 2, 0.040))


@pytest.mark.parametrize("commodity", ["electricity", "gas"])
def test_every_cut_set_is_mean_one_over_its_OWN_reference_population(commodity):
    """THE PROPERTY, asserted to the float rather than to a band.

    Whatever cut-set a caller describes, the response must leave the aggregate
    of THAT cut-set's own reference population exactly where it found it. Not
    "within 2%" — exactly, because over the reference population this is an
    identity, and an identity asserted at a tolerance is a claim that can rot
    by 1.9% without anyone hearing. The band control below is for BOOKS, which
    are samples; this is for the reference, which is not.

    Keyed to the property and not to today's answer: replace the NEED curve,
    the size shares or the children reference and this stays green; make the
    centre disagree with the population it centres and it goes red.
    """
    sizes = sorted(HOUSEHOLD_SIZE_POPULATION_SHARE)
    weights = [HOUSEHOLD_SIZE_POPULATION_SHARE[n] for n in sizes]
    assert population_mean_volume_factor(sizes, weights, commodity) == pytest.approx(1.0, abs=1e-12)

    people = [n for n, _, _ in _CHILDREN_REF]
    kids = [k for _, k, _ in _CHILDREN_REF]
    shares = [s for _, _, s in _CHILDREN_REF]
    assert population_mean_volume_factor(
        people, shares, commodity, children_counts=kids, children_reference=_CHILDREN_REF,
    ) == pytest.approx(1.0, abs=1e-12)


@pytest.mark.parametrize("commodity", ["electricity", "gas"])
def test_the_volume_centre_FIRES_when_a_children_book_is_centred_all_adult(commodity):
    """R15 mutation, and the defect this change was written for: hand the
    children cut-set the all-adult centre — which is what every caller got
    before today — and the book is re-levelled DOWNWARD.

    The assertion is the DIRECTION and the IDENTITY, not the size: the cut's
    magnitude is a property of whichever children reference is in play, and
    pinning 1.5% here would key the control to one fixture. What must hold is
    that the wrong centre is not neutral and the right one is.
    """
    people = [n for n, _, _ in _CHILDREN_REF]
    kids = [k for _, k, _ in _CHILDREN_REF]
    shares = [s for _, _, s in _CHILDREN_REF]
    wrong = sum(
        s * occupancy_volume_factor(n, commodity, children_count=k)
        for n, k, s in _CHILDREN_REF
    )
    assert wrong < 1.0
    assert volume_factor_normaliser(commodity, _CHILDREN_REF) < volume_factor_normaliser(commodity)
    assert population_mean_volume_factor(
        people, shares, commodity, children_counts=kids, children_reference=_CHILDREN_REF,
    ) == pytest.approx(1.0, abs=1e-12)


def test_the_band_control_CANNOT_see_this_defect_which_is_why_the_refusal_exists():
    """The measured reason the mechanism is a refusal rather than a wider band.

    On the live 144-home book with the children `premise_trace` already draws
    for itself, the all-adult centre puts the mean volume factor at 0.9846 —
    a real 1.5% cut, and INSIDE `VOLUME_FACTOR_BIAS_TOL`. So `volume_factor_
    is_unbiased` would have returned True while the book was being cut.

    Asserted as the relation "the defect fits inside the band", so tightening
    the band below the defect is what turns this red — which is the state in
    which the refusal would no longer be the only mechanism. A control pinned
    to 0.9846 would instead go red the day the book changes, which tells you
    nothing about the band.
    """
    bias = 1.0 - sum(
        s * occupancy_volume_factor(n, "electricity", children_count=k)
        for n, k, s in _CHILDREN_REF
    )
    assert 0.0 < bias < dm.VOLUME_FACTOR_BIAS_TOL


def test_the_four_cut_set_states_are_distinct_and_the_refusal_is_reachable(monkeypatch):
    """One control over the WHOLE partition, because a guard that refuses
    everything passes every per-branch test.

    THE PARTITION GREW A SHAPE when `CHILDREN_WITHIN_SIZE_REFERENCE` was
    sourced, and the shapes are counted here rather than the states, because
    N states asserted over N+1 shapes is blind to two shapes collapsing into
    one:

      1. no children               -> the size-only centre
      2. children + EXPLICIT ref   -> that reference's centre
      3. children + NO ref, source present -> the SOURCED centre (2 and 3
         agree only when the explicit ref IS the sourced one — asserted
         distinct here by passing a different one)
      4. children + NO ref, source WITHDRAWN -> refuses

    Shapes 2 and 3 are the pair that would silently collapse if the resolution
    ignored an explicit argument, and 3 and 4 are the pair that collapses if
    the guard is keyed on the argument being omitted rather than on the
    resolved reference being absent.
    """
    size_only = volume_factor_normaliser("electricity")
    with_children = volume_factor_normaliser("electricity", _CHILDREN_REF)
    assert size_only != with_children

    book = ([4, 2], [0.5, 0.5], "electricity")
    kids = [2, 0]
    explicit = population_mean_volume_factor(
        *book, children_counts=kids, children_reference=_CHILDREN_REF)
    resolved = population_mean_volume_factor(*book, children_counts=kids)
    # shape 2 != shape 3: an explicit reference is honoured, not overridden
    assert explicit != resolved
    # ... and neither is the size-only reading
    assert resolved != sum(
        w * occupancy_volume_factor(n, "electricity", children_count=k)
        for n, k, w in zip(book[0], kids, book[1])
    )

    # shape 4 -- reachable: withdraw the source and the refusal fires again
    monkeypatch.setattr(dm, "CHILDREN_WITHIN_SIZE_REFERENCE", None)
    with pytest.raises(UnanchoredReferencePopulation):
        population_mean_volume_factor([4, 2], [0.5, 0.5], "electricity", children_counts=[2, 0])
    with pytest.raises(UnanchoredReferencePopulation):
        volume_factor_is_unbiased([4, 2], [0.5, 0.5], "electricity", children_counts=[2, 0])
    # ... and NOT on a book that does not, nor when a reference is supplied.
    # The assertion is that these two ANSWER — a two-home book is not the
    # reference population and is free to be biased; what it may not do is
    # refuse. Asserting True here would be asserting the fixture's arithmetic,
    # not the partition.
    assert isinstance(
        volume_factor_is_unbiased([4, 2], [0.5, 0.5], "electricity", children_counts=[0, 0]), bool)
    assert population_mean_volume_factor(
        [4, 2], [0.5, 0.5], "electricity", children_counts=[2, 0],
        children_reference=_CHILDREN_REF) > 0.0


def test_the_population_half_of_R10_GAP_a_is_a_distribution_or_an_honest_absence():
    """The constant must be EITHER an honest `None` OR a real distribution —
    never a plausible fill.

    THIS CONTROL USED TO BE `assert CHILDREN_WITHIN_SIZE_REFERENCE is None`,
    and that was keyed to the day's answer rather than to the property: it
    would have gone RED the moment the gap was CLOSED, which is the one thing
    it should have welcomed. It is rewritten here as the property that holds
    on both sides of that event — the shape is a valid population or it is
    absent, and there is no third state where something shaped like an answer
    sits in the slot without being one.
    """
    ref = dm.CHILDREN_WITHIN_SIZE_REFERENCE
    if ref is None:
        return
    assert all(isinstance(r, tuple) and len(r) == 3 for r in ref)
    assert all(0 <= k < n for n, k, _ in ref), "every household needs at least one adult"
    assert sum(s for _, _, s in ref) == pytest.approx(1.0, abs=1e-9)
    # A distribution, not a point: a single row would be a fill wearing a
    # population's shape.
    assert len({n for n, _, _ in ref}) > 1 and any(k for _, k, _ in ref)


def test_the_sourced_centre_makes_its_OWN_population_an_identity():
    """The finding's own lesson, asserted at the strength it earns.

    Neutrality over a BOOK is an estimate and any tolerance wide enough for
    sampling is wide enough to hide a re-levelling (which is how the 1.5% cut
    sat inside the 0.02 band). Neutrality over the REFERENCE POPULATION is an
    IDENTITY, so it is asserted at 1e-12 — and it is the only place that
    strength is available.

    FIRES when the reference and the centre come apart: change a share, a
    children count, or the child weight the normaliser uses, and this goes red
    while every band-shaped control stays green.
    """
    ref = dm.CHILDREN_WITHIN_SIZE_REFERENCE
    if ref is None:
        pytest.skip("gap re-opened; the honest-absence control above covers that state")
    for commodity in ("electricity", "gas"):
        assert dm.population_mean_volume_factor(
            [n for n, _, _ in ref], [s for _, _, s in ref], commodity,
            children_counts=[k for _, k, _ in ref], children_reference=ref,
        ) == pytest.approx(1.0, abs=1e-12)


def test_a_book_with_children_reaches_the_sourced_centre_without_being_told():
    """The constant must be REACHED by the aggregate path, not merely exist.

    A sourced number sitting unwired beside the live one is this project's
    most expensive recurring shape (the £55/£150 acquisition cost). So the
    assertion is not "the constant parses" but "a caller who supplies children
    and says nothing about a reference is scored against the SOURCED centre" —
    i.e. the same answer as passing it explicitly, and a DIFFERENT answer from
    the all-adult centre.
    """
    ref = dm.CHILDREN_WITHIN_SIZE_REFERENCE
    if ref is None:
        pytest.skip("gap re-opened")
    people, kids, weights = [4, 3, 2], [2, 1, 0], [0.4, 0.35, 0.25]
    implicit = dm.population_mean_volume_factor(
        people, weights, "electricity", children_counts=kids)
    explicit = dm.population_mean_volume_factor(
        people, weights, "electricity", children_counts=kids, children_reference=ref)
    all_adult = sum(
        w * dm.occupancy_volume_factor(n, "electricity", children_count=k)
        for n, k, w in zip(people, kids, weights)
    )
    assert implicit == explicit
    assert implicit != all_adult


def test_the_refusal_is_still_REACHABLE_when_the_source_is_withdrawn(monkeypatch):
    """The guard's subject is the RESOLVED reference, not the omitted argument.

    Wiring the constant turned the old refusal branch into one that no book
    can reach any more — and a guard nothing can reach is a deleted guard that
    still reads like a control. It is re-keyed to the property it was always
    about: a book that declares children is never scored against a centre that
    does not cover them. Withdraw the source and it must refuse again.

    MUTATION: resolving to `HOUSEHOLD_SIZE_POPULATION_SHARE` instead, or
    dropping the inner `if`, makes this the only red.
    """
    monkeypatch.setattr(dm, "CHILDREN_WITHIN_SIZE_REFERENCE", None)
    with pytest.raises(UnanchoredReferencePopulation):
        dm.population_mean_volume_factor(
            [4, 2], [0.5, 0.5], "electricity", children_counts=[2, 0])
    with pytest.raises(UnanchoredReferencePopulation):
        dm.volume_factor_is_unbiased(
            [4, 2], [0.5, 0.5], "electricity", children_counts=[2, 0])
    # ... and a book WITHOUT children is unaffected by the withdrawal: the
    # all-adult cut-set never needed this reference.
    assert isinstance(dm.volume_factor_is_unbiased(
        [4, 2], [0.5, 0.5], "electricity", children_counts=[0, 0]), bool)


#: ONS Census 2021 England and Wales, the HOUSEHOLD-based products — a
#: DIFFERENT population type from the person-based table
#: `CHILDREN_WITHIN_SIZE_REFERENCE` is derived from, fetched the same day.
#:
#: `P(any dependent child | size)` from `HH` x (`hh_size_9a`,
#: `hh_dependent_children_3a`), and `P(exactly one dependent child | size)`
#: from `HH` x (`hh_size_9a`, `hh_family_composition_37a`). Between them they
#: pin the d=0 and d=1 mass at every size, and therefore the d>=2 mass too —
#: leaving only the split WITHIN "two or more", which is the one thing the
#: Census does not publish and the constant's comment names as its assumption.
_CENSUS_ANY_CHILD_BY_SIZE = {
    1: 0.000482, 2: 0.086951, 3: 0.569026, 4: 0.806125,
    5: 0.863657, 6: 0.878488, 7: 0.894076, 8: 0.894046,
}
_CENSUS_ONE_CHILD_BY_SIZE = {
    1: 0.000000, 2: 0.086481, 3: 0.435679, 4: 0.135876,
    5: 0.131937, 6: 0.106335, 7: 0.098924, 8: 0.067155,
}


def test_the_conditional_children_split_agrees_with_two_INDEPENDENT_census_products():
    """The control over the CONDITIONAL, which is the constant's whole content.

    THE HOLE THIS FILLS, found by mutation and not by reading. Every other
    control here is invariant to moving mass BETWEEN children counts within a
    size: the identity holds because centre and population move together, the
    all-adult read holds because the children column is zeroed, and the size
    marginal is untouched by construction. So `(3, 2, s) -> (3, 1, s)` — the
    reference silently disagreeing with its source — passed all of them. A
    mutation nothing catches is a missing test, and this is it.

    It is keyed to SEPARATE Census products rather than to the table the
    reference came from, because a figure checked against its own source
    agrees with itself by construction.

    The two disagreements are the derivation's two documented clamps, and they
    are asserted as bounded rather than waived:
      * size 1 — 3,606 one-person households are recorded WITH a dependent
        child; `adult_equivalents` refuses a household with no adult, so they
        are clamped to zero children here.
      * size 8 — the band is "8 OR MORE", so the person-based conversion
        (persons / 8) overcounts households whose true size is larger.
    """
    ref = dm.CHILDREN_WITHIN_SIZE_REFERENCE
    if ref is None:
        pytest.skip("gap re-opened")
    by_size, any_child, one_child = {}, {}, {}
    for n, k, s in ref:
        by_size[n] = by_size.get(n, 0.0) + s
        if k >= 1:
            any_child[n] = any_child.get(n, 0.0) + s
        if k == 1:
            one_child[n] = one_child.get(n, 0.0) + s

    for n in sorted(by_size):
        ours = any_child.get(n, 0.0) / by_size[n]
        published = _CENSUS_ANY_CHILD_BY_SIZE[n]
        if n == 1:
            # the clamp, stated as a quantity: we carry NO children at size 1
            # and the source carries a whisker over zero.
            assert ours == 0.0 and published < 0.001
        elif n == 8:
            assert abs(ours - published) < 0.005
        else:
            assert abs(ours - published) < 1e-5, f"size {n}: {ours} vs {published}"

    for n in sorted(by_size):
        ours = one_child.get(n, 0.0) / by_size[n]
        # 0.25pp: the two products carry INDEPENDENT cell-key perturbation, so
        # they are not expected to agree exactly — and a real edit to a row
        # moves this by percentage points, not by a quarter of one.
        assert abs(ours - _CENSUS_ONE_CHILD_BY_SIZE[n]) < 0.0025, f"size {n}"


def test_reading_the_children_reference_as_all_adults_reproduces_the_all_adult_centre():
    """THE ATTRIBUTABILITY CONTROL, and the reason it can be this strong.

    Two centres now exist and the whole claim of the per-cut-set repair is
    that the difference between them is CHILDREN — not a different size mix
    smuggled in alongside. That is testable as an identity rather than argued:
    zero out the children column of the reference and the centre it produces
    must be the all-adult centre, which it shares no code path with.

    It holds to 9e-08 — the 7-dp rounding of the published shares — and at
    full precision it is exact, because `need_volume_index` is FLAT at and
    above five adults, so the reference's finer 6/7/8 tail cannot move the
    all-adult centre however it is split.

    FIRES the moment the size marginal here drifts from the world's own draw
    (`dwelling_records.HOUSEHOLD_SIZE_SHARE_ONS_TS017`), which is a divergence
    with no other symptom — and is exactly the divergence that has been live
    between that constant and `HOUSEHOLD_SIZE_POPULATION_SHARE` since
    2026-09-17 without changing any centre.
    """
    ref = dm.CHILDREN_WITHIN_SIZE_REFERENCE
    if ref is None:
        pytest.skip("gap re-opened")
    for commodity in ("electricity", "gas"):
        as_all_adults = sum(
            s * dm.need_volume_index(n, commodity, children_count=0) for n, _, s in ref)
        assert as_all_adults == pytest.approx(
            dm.volume_factor_normaliser(commodity), abs=1e-6)


def test_the_children_reference_reconciles_with_the_size_distribution_the_world_draws():
    """The derivation's own control, run on the numbers that were landed.

    `CHILDREN_WITHIN_SIZE_REFERENCE` is not lifted from a published table —
    none states it. It is converted from a PERSON-based Census cross-tab by
    households(n, d) = persons(n, d) / n. That conversion is the step that
    could silently be wrong, and the check on it is that summing it back over
    d reproduces the household size marginal a SEPARATE Census product
    publishes and the world draws households from.

    Pinned at the tolerance the 7-dp rounding earns, so it fires if a row is
    edited, dropped or re-scaled, and not merely because the shares are
    quoted rather than computed.
    """
    ref = dm.CHILDREN_WITHIN_SIZE_REFERENCE
    if ref is None:
        pytest.skip("gap re-opened")
    from simulation.dwelling_records import HOUSEHOLD_SIZE_SHARE_ONS_TS017
    by_size = {}
    for n, _, s in ref:
        by_size[n] = by_size.get(n, 0.0) + s
    assert by_size.keys() == {n for n, _ in HOUSEHOLD_SIZE_SHARE_ONS_TS017}
    for n, published in HOUSEHOLD_SIZE_SHARE_ONS_TS017:
        assert by_size[n] == pytest.approx(published, abs=1e-6)
    # The tail the source stops at: "three or more" is published AS three, so
    # no household in the reference carries more than three children. This is
    # the row that says the understatement is DELIBERATE rather than a lost
    # tail — see the constant's own comment for what it is worth (0.268%).
    assert max(k for _, k, _ in ref) == 3


def test_a_children_reference_that_is_not_a_distribution_is_refused():
    """FAIL-CLOSED: a reference whose shares do not sum to 1 is not a
    population, and a centre computed over it is not a mean. Refused rather
    than silently producing a divisor."""
    for bad in ((), ((2, 0, 0.5), (3, 1, 0.2)), ((2, 0, 0.5), (3, 1, 0.9))):
        with pytest.raises(ValueError):
            volume_factor_normaliser("electricity", bad)


def test_the_size_only_volume_caller_is_byte_identical_to_before():
    """P5. The legacy path must not move at all — these are the exact floats
    the module returned before the cut-set key was added, so every existing
    caller in the world is unchanged."""
    assert volume_factor_normaliser("electricity") == 1.4456452584044155
    assert volume_factor_normaliser("gas") == 1.2512721741165458
    assert volume_factor_normaliser("electricity", None) == volume_factor_normaliser("electricity")


def test_shape_control_is_not_fail_open():
    with pytest.raises(ValueError):
        population_mean_daytime_multiplier([], [], period=_MIDDAY)
    with pytest.raises(ValueError):
        # Outside the response window the ratio is trivially 1.0 — a control
        # that cannot fire must refuse to run, not pass.
        population_mean_daytime_multiplier(_POP_SIZES, _POP_WEIGHTS, period=_EVENING)


# ---------------------------------------------------------------------------
# Integration through build_demand_shape
# ---------------------------------------------------------------------------

def test_a_record_without_people_count_is_unchanged_from_legacy():
    """Backward compatibility, exactly: no people_count → base * category
    multiplier, with no volume term at all."""
    got = build_demand_shape(FLAT_SHAPE, MILD_TEMP, "electricity", elec_property("family"))
    want = [s * occupancy_multiplier("family", p) for p, s in enumerate(FLAT_SHAPE, start=1)]
    assert got == pytest.approx(want)


def test_volume_and_shape_both_apply_and_are_separable():
    prop = elec_property("family", people_count=5, customer_id="H5")
    shape = build_demand_shape(FLAT_SHAPE, MILD_TEMP, "electricity", prop)
    vf = occupancy_volume_factor(5, "electricity", household_key="H5")
    want = [
        s * occupancy_multiplier("family", p, people_count=5, household_key="H5") * vf
        for p, s in enumerate(FLAT_SHAPE, start=1)
    ]
    assert shape == pytest.approx(want)


def test_ev_charging_is_not_scaled_by_headcount():
    """EV load is asset-driven, not people-driven: it is added AFTER the
    volume factor, so the EV delta must be exactly the per-night figure
    whatever the headcount."""
    for n in (1, 5):
        no_ev = build_demand_shape(FLAT_SHAPE, MILD_TEMP, "electricity",
                                   elec_property(people_count=n, customer_id="E"))
        with_ev = dict(elec_property(people_count=n, customer_id="E"))
        with_ev["assets"] = {"ev": True, "solar": False, "smart_meter": True}
        got = build_demand_shape(FLAT_SHAPE, MILD_TEMP, "electricity", with_ev)
        assert sum(got) - sum(no_ev) == pytest.approx(EV_CHARGING_KWH_PER_NIGHT)


def test_gas_and_electricity_use_their_own_anchored_curves():
    gas_prop = {"heating_system": "gas_boiler", "occupancy_pattern": "single",
                "assets": {"ev": False, "solar": False, "smart_meter": True},
                "people_count": 4, "customer_id": "G"}
    elec_prop = dict(gas_prop, heating_system="electric_storage")
    gas_ratio = sum(build_demand_shape(FLAT_SHAPE, MILD_TEMP, "gas", gas_prop)) / sum(
        build_demand_shape(FLAT_SHAPE, MILD_TEMP, "gas", dict(gas_prop, people_count=1)))
    elec_ratio = sum(build_demand_shape(FLAT_SHAPE, MILD_TEMP, "electricity", elec_prop)) / sum(
        build_demand_shape(FLAT_SHAPE, MILD_TEMP, "electricity", dict(elec_prop, people_count=1)))
    # Gas must respond LESS to headcount than electricity — NEED A13 vs A14
    # (12,734/8,546 = 1.49 against 3,772/1,993 = 1.89). The shape response is
    # identical for both commodities, so the ordering is the volume curves'.
    assert gas_ratio < elec_ratio
    assert (occupancy_volume_factor(4, "gas") / occupancy_volume_factor(1, "gas")
            == pytest.approx(12734.0 / 8546.0, rel=0.005))
    assert (occupancy_volume_factor(4, "electricity") / occupancy_volume_factor(1, "electricity")
            == pytest.approx(3772.0 / 1993.0, rel=0.005))


def test_need_volume_index_is_relative_to_a_one_adult_household():
    assert need_volume_index(1, "electricity") == pytest.approx(1.0)
    assert need_volume_index(1, "gas") == pytest.approx(1.0)
    assert volume_factor_normaliser("electricity") > 1.0


# ===========================================================================
# THE PRODUCTION CALL SITE IS CENTRED PER CUT-SET TOO (2026-09-23)
#
# `population_mean_volume_factor` was made cut-set-keyed when the children
# reference landed, and that closed the AGGREGATE claim. `build_demand_shape`
# is the ONE-HOUSEHOLD call site of the same rule, and it was still dividing
# by the all-adult centre — harmless while `children_count` was 0 on every
# record in the book, and a silent 1.5% cut to the whole book's volume from
# the moment `dwelling_records` started drawing the Census conditional.
#
# Which is why these legs land in the same commit as that draw. A control
# written after the field is wired is a control written after the defect.
# ===========================================================================

def _volume_probe(children_count, *, declare=True, people_count=4):
    prop = {"heating_system": "electric_storage", "occupancy_pattern": "single",
            "assets": {"ev": False, "solar": False, "smart_meter": True},
            "people_count": people_count, "customer_id": "VOL-CUTSET-0001"}
    if declare:
        prop["children_count"] = children_count
    return sum(build_demand_shape(FLAT_SHAPE, MILD_TEMP, "electricity", prop))


def _centre_ratio():
    """all-adult centre / Census-children centre. The EXACT factor by which a household's volume
    moves when the call site resolves the reference, and the thing these legs measure."""
    return (dm.volume_factor_normaliser("electricity")
            / dm.volume_factor_normaliser("electricity", dm.CHILDREN_WITHIN_SIZE_REFERENCE))


def test_a_record_declaring_children_is_centred_on_the_children_population(monkeypatch):
    """The defect: `occupancy_volume_factor` with a `children_count` and no `children_reference`
    divides by the ALL-ADULT centre. That is not a small deviation, it is the divisor being wrong
    — measured 0.9846 on the live book, a 1.5% cut sitting INSIDE `VOLUME_FACTOR_BIAS_TOL`, so no
    band could ever have caught it.

    MEASURED BY WITHDRAWING THE SOURCE, not by predicting a kWh. Every other term in
    `build_demand_shape` — the occupancy SHAPE multiplier, the heating load, the child weight
    draw — is identical across the two runs, so their ratio is the divisor and nothing else. That
    also keys this to the PROPERTY (the call site reads the reference) rather than to today's
    answer, so re-deriving the Census population moves the target with it.
    """
    assert dm.CHILDREN_WITHIN_SIZE_REFERENCE is not None, (
        "R10 GAP (a)'s population half has been withdrawn; this leg's subject does not exist"
    )
    expected = _centre_ratio()
    assert expected > 1.0, (
        "a child weighs less than an adult, so the children centre must sit BELOW the all-adult "
        "one; if these are equal the reference is not being read at all"
    )
    with_ref = _volume_probe(2)
    monkeypatch.setattr(dm, "CHILDREN_WITHIN_SIZE_REFERENCE", None)
    without_ref = _volume_probe(2)
    assert with_ref / without_ref == pytest.approx(expected, rel=1e-9), (
        f"withdrawing the reference moved this home by {with_ref / without_ref:.6f} where the two "
        f"centres differ by {expected:.6f} — the call site is not dividing by the one it declares"
    )


def test_the_centre_is_keyed_on_declaring_the_field_not_on_having_a_child(monkeypatch):
    """THE DIVISOR IS A POPULATION PROPERTY, NOT A HOUSEHOLD ONE. Keying the reference on
    `children_count > 0` would put two homes in one book on two different centres — the
    variable-numerator-against-a-fixed-denominator defect turned around — so a record that
    DECLARES 0 children must move by the same factor as one that declares 2.

    This is the leg that fails if someone 'optimises' the call site to skip the reference when
    there is no child to weight, which looks like a free short-circuit and is not one.
    """
    expected = _centre_ratio()
    with_ref = _volume_probe(0, declare=True)
    monkeypatch.setattr(dm, "CHILDREN_WITHIN_SIZE_REFERENCE", None)
    without_ref = _volume_probe(0, declare=True)
    assert with_ref / without_ref == pytest.approx(expected, rel=1e-9), (
        "a record declaring zero children was not centred on the Census population; it is a "
        "zero-children MEMBER of that population and is centred on it exactly as a 2-child one is"
    )


def test_a_record_that_never_declares_children_keeps_the_pre_w2_13_centre(monkeypatch):
    """The other side of the same partition, and the promise `build_demand_shape`'s docstring
    makes to SME defaults and pre-W2_13 fixtures: a record with no `children_count` key at all is
    byte-identical to what it always was, reference or no reference.

    Asserted TOGETHER with the DISTINCTNESS of the two branches rather than in isolation, because
    a call site that resolved the reference for NOBODY would pass this leg alone — and that is
    precisely the defect the three legs here exist to catch.
    """
    undeclared_with_ref = _volume_probe(0, declare=False)
    monkeypatch.setattr(dm, "CHILDREN_WITHIN_SIZE_REFERENCE", None)
    assert _volume_probe(0, declare=False) == pytest.approx(undeclared_with_ref, rel=1e-12), (
        "withdrawing the reference moved a record that never declared the field; the pre-W2_13 "
        "path is supposed to be untouched by it"
    )
    monkeypatch.undo()
    # And the two branches are genuinely DISTINCT — declaring zero is not the same as not saying.
    assert _volume_probe(0, declare=True) != pytest.approx(undeclared_with_ref, rel=1e-6), (
        "declaring zero children and omitting the field give the identical answer, so no leg "
        "here can tell whether the reference is ever resolved"
    )
