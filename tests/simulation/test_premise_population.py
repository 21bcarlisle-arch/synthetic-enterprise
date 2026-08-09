"""Controls on the stock-representative premise draw (`C14` L2->L3, population half).

R15 IS THE POINT OF THIS FILE. A population draw is unusually good at producing
controls that cannot fail: it is trivially easy to write a test that the drawn
shares "look about right" and never discovers that the draw degenerated, that the
raking silently failed, or that the tilt did nothing at all. Every control here is
paired with the mutation that makes it fire, and the mutation is applied to the
SOURCE VALUES the control reads — not to a fixture built alongside it.

THE DEFECT THIS MODULE EXISTS TO PREVENT is recorded: `simulation.household.
make_household` defaults an attribute-less customer record to `suburban_semi`, so
the "population" the fabric triad would otherwise have measured on is a set of
clones. `test_the_recorded_clone_defect_is_what_this_draw_replaces` pins that
directly rather than describing it.
"""

from __future__ import annotations

import datetime as dt

import pytest

from simulation import premise_population as pp
from simulation.household import (
    BuildEra,
    HeatingSystem,
    InsulationLevel,
    PropertyType,
    make_household,
)

AS_OF = dt.date(2022, 5, 1)
SEED = 17

# Large enough that binomial noise on the smallest judged share is well inside the
# tolerance below, so a FAILURE means a biased draw rather than a small sample.
BIG_N = 4_000
# 3 percentage points. The largest published share is 44.8%; its binomial sd at
# n=4000 is 0.79pp, so 3pp is ~3.8 sd — a band a correct draw clears comfortably
# and a 1-in-20 wrong weight does not.
MARGINAL_TOLERANCE_PP = 0.03


@pytest.fixture(scope="module")
def population():
    return pp.draw_premise_population(BIG_N, base_seed=SEED, as_of=AS_OF)


# ---------------------------------------------------------------------------
# The three published marginals
# ---------------------------------------------------------------------------
def test_published_marginals_are_recovered(population):
    recovery = pp.published_marginal_recovery(population)
    for axis, worst in recovery.items():
        assert worst < MARGINAL_TOLERANCE_PP, (
            f"{axis} departs from its published marginal by {worst * 100:.2f}pp"
        )


def test_marginal_control_fires_on_a_wrong_published_share(monkeypatch):
    """MUTATION. Move ONE published share and the recovery control must fire.

    The mutation is on the source constant, so the draw and the check move
    together — if the control were reading the drawn population back against
    itself (the tautology shape) this test would PASS and prove nothing. It
    fails, which is what says the published figure is an independent referent.
    """
    poisoned = dict(pp.PUBLISHED_PROPERTY_TYPE_SHARE)
    poisoned[PropertyType.FLAT] = 0.05
    poisoned[PropertyType.TERRACED] = 0.45
    monkeypatch.setattr(pp, "PUBLISHED_PROPERTY_TYPE_SHARE", poisoned)

    drawn = pp.draw_premise_population(BIG_N, base_seed=SEED, as_of=AS_OF)
    # Judge the poisoned draw against the TRUE published shares.
    observed = pp.observed_shares(drawn)["property_type"]
    worst = max(
        abs(observed.get(k, 0.0) - v)
        for k, v in {
            PropertyType.TERRACED: 0.29,
            PropertyType.SEMI_DETACHED: 0.25,
            PropertyType.DETACHED: 0.25,
            PropertyType.FLAT: 0.21,
        }.items()
    )
    assert worst > MARGINAL_TOLERANCE_PP, (
        "a 16-point error in a published share left the drawn marginal inside "
        "tolerance — the control cannot fail and is worth nothing"
    )


# ---------------------------------------------------------------------------
# The ORACLE: a published conditional that was NOT a raking target
# ---------------------------------------------------------------------------
def test_fitted_joint_reproduces_the_published_conditional_it_was_not_fitted_to():
    share = pp.conditional_share_in_bands(
        pp.raked_joint(), eras=pp.OLD_STOCK_ERAS, bands=pp.BANDS_D_TO_G
    )
    assert share >= pp.OLD_STOCK_MIN_SHARE_IN_BANDS_D_TO_G, (
        f"old stock lands in bands D-G only {share:.3f} of the time, against the "
        f"published-and-diluted bar {pp.OLD_STOCK_MIN_SHARE_IN_BANDS_D_TO_G}"
    )


def test_the_independent_product_FAILS_the_same_oracle():
    """The oracle discriminates, and this is the proof — not a mutation invented
    for the test but the ACTUAL alternative construction (cross the three
    marginals independently, which is what a draw without a fitted joint does)."""
    share = pp.conditional_share_in_bands(
        pp.independent_joint(), eras=pp.OLD_STOCK_ERAS, bands=pp.BANDS_D_TO_G
    )
    assert share < pp.OLD_STOCK_MIN_SHARE_IN_BANDS_D_TO_G, (
        "crossing the marginals independently ALSO satisfies the published "
        "conditional, so the conditional is not evidence that the joint is fitted"
    )


def test_oracle_fires_when_the_era_tilt_is_removed(monkeypatch):
    """MUTATION on the source: flatten the era tilt to 1.0 everywhere. Raking
    still reproduces all three marginals exactly, and the oracle still fails —
    which is precisely why a marginal check alone is not enough."""
    flat = {era: {b: 1.0 for b in pp.EPC_BANDS} for era in pp.PUBLISHED_BUILD_ERA_SHARE}
    monkeypatch.setattr(pp, "_EPC_TILT_BY_ERA", flat)
    joint = pp.raked_joint()

    marginal = pp._marginal(joint, 1)
    for era, want in pp.PUBLISHED_BUILD_ERA_SHARE.items():
        assert abs(marginal[era] - want) < 1e-6, "raking still fits the marginals"

    share = pp.conditional_share_in_bands(
        joint, eras=pp.OLD_STOCK_ERAS, bands=pp.BANDS_D_TO_G
    )
    assert share < pp.OLD_STOCK_MIN_SHARE_IN_BANDS_D_TO_G


def test_the_drawn_population_carries_the_conditional_too(population):
    """The joint being right is not the same as the DRAW being right."""
    observed = pp.observed_shares(population)
    assert observed["old_stock_n"] > 500, "not enough old stock drawn to judge"
    assert observed["old_stock_share_in_bands_d_to_g"] >= pp.OLD_STOCK_MIN_SHARE_IN_BANDS_D_TO_G


# ---------------------------------------------------------------------------
# Raking itself
# ---------------------------------------------------------------------------
def test_raked_joint_is_not_the_independent_product():
    """VACUITY GUARD. If the tilts were ineffective the raked joint would collapse
    to the product of the marginals and every conditional claim above would be
    accidental."""
    raked, independent = pp.raked_joint(), pp.independent_joint()
    worst = max(abs(raked[c] - independent[c]) for c in raked)
    assert worst > 1e-3, (
        "the fitted joint is indistinguishable from the independent product — "
        "the tilt did nothing"
    )


def test_rake_raises_rather_than_returning_an_unconverged_joint():
    """FAIL-CLOSED. A quiet return would hand back a joint whose marginals are not
    the published ones while every caller believed they were."""
    with pytest.raises(RuntimeError, match="did not converge"):
        pp.rake(
            pp.seed_joint(),
            (
                pp.PUBLISHED_PROPERTY_TYPE_SHARE,
                pp.PUBLISHED_BUILD_ERA_SHARE,
                {b: pp.PUBLISHED_EPC_BAND_SHARE[b] for b in pp.EPC_BANDS},
            ),
            max_iterations=1,
        )


def test_rake_refuses_a_marginal_that_is_worse_than_publication_rounding():
    """The EPC bands legitimately sum to 100.1%; a share that is simply wrong must
    not be laundered by the same normalisation."""
    with pytest.raises(ValueError, match="wrong share, not a rounded one"):
        pp.rake(
            pp.seed_joint(),
            (
                pp.PUBLISHED_PROPERTY_TYPE_SHARE,
                pp.PUBLISHED_BUILD_ERA_SHARE,
                {b: pp.PUBLISHED_EPC_BAND_SHARE[b] * 1.5 for b in pp.EPC_BANDS},
            ),
        )


def test_published_epc_bands_really_do_need_the_rounding_slack():
    """Pins the reason the slack exists. If EHS ever republishes bands summing to
    exactly 1, this fails and the comment explaining the slack gets re-read rather
    than quietly outliving its cause."""
    total = sum(pp.PUBLISHED_EPC_BAND_SHARE.values())
    assert total != pytest.approx(1.0, abs=1e-9)
    assert abs(total - 1.0) <= pp.MAX_PUBLISHED_ROUNDING_SLACK


# ---------------------------------------------------------------------------
# The clone defect this whole module replaces
# ---------------------------------------------------------------------------
def test_the_recorded_clone_defect_is_what_this_draw_replaces():
    """`make_household` on attribute-less customer records yields ONE cell.

    This is the recorded blocker, pinned as an executable fact rather than a
    sentence in an evidence field: `SyntheticCustomer` carries no home_type,
    epc_rating or bedrooms, so every draw defaults to the same suburban semi.
    """
    clones = [make_household({"customer_id": f"C{i}"}) for i in range(200)]
    cells = {(h.property_type, h.build_era, h.epc_rating) for h in clones}
    assert len(cells) == 1, (
        "the clone defect has been fixed elsewhere — re-read whether this module "
        "is still the right way to get a population"
    )


def test_the_drawn_population_occupies_many_cells(population):
    assert pp.distinct_cells(population) >= 40


def test_distinct_cells_would_catch_a_degenerate_draw():
    """MUTATION: collapse the joint to a single cell and the clone detector fires."""
    only = (PropertyType.SEMI_DETACHED, BuildEra.ERA_1945_1964, "D")
    drawn = [
        pp.draw_premise(f"P{i:04d}", base_seed=SEED, as_of=AS_OF, joint={only: 1.0})
        for i in range(200)
    ]
    assert pp.distinct_cells(drawn) == 1


# ---------------------------------------------------------------------------
# C-S2: substream discipline
# ---------------------------------------------------------------------------
def test_same_seed_draws_the_same_population():
    a = pp.draw_premise_population(50, base_seed=SEED, as_of=AS_OF)
    b = pp.draw_premise_population(50, base_seed=SEED, as_of=AS_OF)
    assert a == b


def test_a_different_seed_draws_a_different_population():
    a = pp.draw_premise_population(50, base_seed=SEED, as_of=AS_OF)
    b = pp.draw_premise_population(50, base_seed=SEED + 1, as_of=AS_OF)
    assert a != b


def test_growing_the_population_appends_and_never_reshuffles():
    """C-S2. If premise P0007 changed when the population grew, every measurement
    taken at one size would be incomparable with the next, and the reason would be
    invisible."""
    small = pp.draw_premise_population(10, base_seed=SEED, as_of=AS_OF)
    large = pp.draw_premise_population(400, base_seed=SEED, as_of=AS_OF)
    assert large[: len(small)] == small


def test_moving_as_of_changes_staleness_but_not_composition():
    """A population whose COMPOSITION moves with the clock is an artefact — the
    same measurement taken on two dates would differ for a reason nobody named.
    Certificate AGE is supposed to move; property type, era and band are not.
    """
    early = pp.draw_premise_population(200, base_seed=SEED, as_of=dt.date(2019, 5, 1))
    late = pp.draw_premise_population(200, base_seed=SEED, as_of=dt.date(2025, 5, 1))

    def composition(pop):
        return [(p.household.property_type, p.household.build_era, p.epc_band, p.household.bedrooms) for p in pop]

    assert composition(early) == composition(late)

    # Certificate AGE must be identical and the DATES must have moved by exactly
    # the shift in `as_of`. Comparing the date ranges instead would prove nothing:
    # [as_of-10y, as_of) for 2019 and 2025 overlap over 2015-2019, so a draw that
    # ignored `as_of` entirely could still pass a range comparison.
    shift = dt.date(2025, 5, 1) - dt.date(2019, 5, 1)
    certified = 0
    for before, after in zip(early, late):
        assert (before.epc_lodged is None) == (after.epc_lodged is None)
        if before.epc_lodged is not None:
            assert after.epc_lodged - before.epc_lodged == shift
            certified += 1
    assert certified > 0, "no premise had a certificate — the check was vacuous"


# ---------------------------------------------------------------------------
# Fail-open guards
# ---------------------------------------------------------------------------
def test_drawing_from_an_empty_distribution_raises():
    import random

    with pytest.raises(ValueError, match="total weight"):
        pp._weighted_choice(random.Random(0), {})
    with pytest.raises(ValueError, match="total weight"):
        pp._weighted_choice(random.Random(0), {"a": 0.0, "b": 0.0})


def test_a_conditional_over_an_empty_conditioning_set_raises():
    """VACUITY. Returning 1.0 (or 0.0) for "100% of no homes" would let the oracle
    pass on a population containing no old stock at all."""
    with pytest.raises(ValueError, match="undefined"):
        pp.conditional_share_in_bands(
            pp.raked_joint(), eras=[], bands=pp.BANDS_D_TO_G
        )


def test_an_empty_population_cannot_be_measured():
    with pytest.raises(ValueError):
        pp.observed_shares([])
    with pytest.raises(ValueError):
        pp.draw_premise_population(0, base_seed=SEED, as_of=AS_OF)


# ---------------------------------------------------------------------------
# The observation side: heating, cadence, certificates
# ---------------------------------------------------------------------------
def test_heating_weights_renormalise_over_the_representable_stock_only():
    weights = pp.published_heating_weights()
    assert sum(weights.values()) == pytest.approx(1.0)
    representable = 1.0 - pp.EXCLUDED_HEATING_SHARE
    assert weights[HeatingSystem.HEAT_PUMP_AIR] == pytest.approx(
        pp._HEAT_PUMP_SHARE / representable, rel=1e-6
    )
    gas = weights[HeatingSystem.GAS_BOILER_COMBI] + weights[HeatingSystem.GAS_BOILER_SYSTEM]
    assert gas == pytest.approx(pp._GAS_FIRED_SHARE / representable, rel=1e-6)


def test_district_heat_and_oil_are_excluded_rather_than_folded_into_gas(population):
    """Folding an oil-heated home into gas would put a gas meter read on a premise
    with no gas meter. The exclusion is declared as a share, so it can be checked."""
    assert HeatingSystem.DISTRICT_HEAT not in pp.published_heating_weights()
    assert all(
        p.household.heating_system in pp.published_heating_weights() for p in population
    )
    assert pp.EXCLUDED_HEATING_SHARE > 0.0


def test_every_premise_meters_a_commodity_the_trace_generator_produces(population):
    assert {p.commodity for p in population} == {"gas", "electricity"}
    for premise in population:
        expected = "gas" if premise.household.is_gas_heated else "electricity"
        assert premise.commodity == expected


def test_electric_heat_is_present_but_rare(population):
    """Both directions matter. A population with NO electrically heated homes
    would silently delete a whole heating regime; one where they were common would
    not be England."""
    electric = [p for p in population if not p.household.is_gas_heated]
    share = len(electric) / len(population)
    assert 0.0 < share < 0.20, f"electrically heated share {share:.3f} is not England"
    assert any(p.household.heating_system == HeatingSystem.HEAT_PUMP_AIR for p in electric)


def test_smart_read_share_interpolates_between_the_published_anchors():
    assert pp.smart_read_share(2016) == pytest.approx(0.106 * 0.90, rel=1e-9)
    assert pp.smart_read_share(2024) == pytest.approx(0.689 * 0.90, rel=1e-9)
    assert pp.smart_read_share(2020) == pytest.approx((0.106 + 0.689) / 2 * 0.90, rel=1e-9)
    # Clamped OUTSIDE the anchored range rather than extrapolated: a linear
    # extrapolation to 2040 would report a penetration above 100%.
    assert pp.smart_read_share(2040) == pp.smart_read_share(2024)
    assert pp.smart_read_share(1990) == pp.smart_read_share(2016)


def test_all_three_meter_cadences_are_present(population):
    """C14's measured error runs 0.2% -> 18% across the cadence range, so a
    population read entirely daily would flatter the company with smart-meter
    evidence it does not have."""
    cadences = {p.meter_cadence_days for p in population}
    assert cadences == {
        pp.DAILY_CADENCE_DAYS,
        pp.MONTHLY_CADENCE_DAYS,
        pp.QUARTERLY_CADENCE_DAYS,
    }
    daily = sum(1 for p in population if p.meter_cadence_days == pp.DAILY_CADENCE_DAYS)
    assert daily / len(population) == pytest.approx(pp.smart_read_share(AS_OF.year), abs=0.03)


def test_some_premises_have_no_certificate_at_all(population):
    """EPC ABSENCE is one of the three error sources this atom exists to model; a
    population with a certificate on every home would delete it while every gap
    number still computed happily."""
    absent = sum(1 for p in population if p.epc_lodged is None)
    assert absent > 0
    assert absent / len(population) == pytest.approx(1.0 - pp.EPC_COVERAGE_SHARE, abs=0.03)


def test_certificates_span_the_full_validity_window(population):
    """Staleness is part of the measurement. If every certificate were fresh the
    company's prior would be uniformly narrow and the register would look better
    than it is."""
    ages = [(AS_OF - p.epc_lodged).days / 365.25 for p in population if p.epc_lodged]
    assert min(ages) < 1.0
    assert max(ages) > pp.EPC_VALIDITY_YEARS - 1.0


# ---------------------------------------------------------------------------
# The premise records are usable by the physics that consumes them
# ---------------------------------------------------------------------------
def test_every_drawn_premise_is_domestic_and_has_a_floor_area(population):
    from simulation import fabric_physics as fp

    for premise in population:
        assert premise.household.is_residential
        assert fp.floor_area_m2(premise.household) > 0.0
        assert fp.fabric_parameters(premise.household).heat_loss_coefficient_kw_per_k > 0.0


def test_insulation_follows_the_drawn_band(population):
    """The EPC letter reaches the fabric ONLY through insulation, so a draw that
    lost the link would produce a population whose bands meant nothing."""
    seen: dict[str, set] = {}
    for premise in population:
        seen.setdefault(premise.epc_band, set()).add(premise.household.insulation)
    assert seen["AB"] == {InsulationLevel.FULL}
    assert seen["G"] <= {InsulationLevel.POOR}
    assert seen["D"] == {InsulationLevel.PARTIAL}


def test_the_population_spans_a_wide_range_of_true_heat_loss(population):
    """The whole point of an unchosen population is that it contains homes a
    chosen panel would not. If the drawn HLC range were narrow, the gap measured
    on it would be no more informative than the panel's."""
    from simulation import fabric_physics as fp

    hlc = sorted(
        fp.fabric_parameters(p.household).heat_loss_coefficient_kw_per_k for p in population
    )
    assert hlc[-1] / hlc[0] > 10.0
