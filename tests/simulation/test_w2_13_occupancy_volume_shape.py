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
    monkeypatch.setattr(dm, "volume_factor_normaliser", lambda commodity: 1.0)
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
    monkeypatch.setattr(dm, "_reference_daytime_rate", lambda: 0.43)
    mean = dm.population_mean_daytime_multiplier(_POP_SIZES, _POP_WEIGHTS, period=_MIDDAY)
    assert mean > 1.02
    assert not dm.daytime_shape_is_mean_neutral(_POP_SIZES, _POP_WEIGHTS, period=_MIDDAY)


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
