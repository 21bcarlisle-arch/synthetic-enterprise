"""THE SAMPLER HAD NO IMPORTER BECAUSE THE WORLD COULD NOT EXPRESS WHAT IT MEASURES.

Director console, 2026-09-10: *"demand_vector_coverage, stock_joint_generator, space_filling_sample
and demand_case_coverage have no importer anywhere. The world still draws 4,400 households the old
way while the apparatus we spent four days measuring sits beside it measuring a cloud it draws
itself. Connect it."*

The reason nothing connected was not that someone forgot to call a module.

**AND THE FIRST ANSWER TO "WHY" WAS TOO STRONG, corrected here rather than quietly dropped.** The
claim was that the demand vector was *unmeasurable* on the world's population because `Household`
had no floor area. It always evaluated: `fabric_physics.floor_area_m2` derives an area from
property type and bedroom count. What was actually true is narrower — the area was inferred from a
bedroom count drawn from property type alone and so carried nothing the property type did not,
`insulation` was a lookup on the EPC letter giving the whole country six values, and `has_solar`
was hardcoded `False` on every drawn home.

The consequence is a LEVEL error, not a missing capability, and it is on the mission's own
quantity: the mean remaining insulation ceiling — what a household could still be sold — was
41.5 W/K under the old draw and is 61.4 W/K measured, with a tenth of homes previously sitting at
exactly zero because an A/B rating mapped to FULL insulation by construction.

This file holds the properties of the repair. The chooser (`choose_for_difference` + `fit_weights`)
is deliberately NOT wired into the stock: measured against random draws at the world's own size it
is 1.04x better, and the measurement is in the pre-registration beside this work.
"""
from __future__ import annotations

import collections
import datetime as dt
import math

import pytest

from simulation import premise_population as pp
from simulation.household import BuildEra, HeatingSystem, InsulationLevel, PropertyType
from simulation.net_new_acquisition import PROSPECTS_PER_YEAR, year_premise_stock

SEED = 20260724
AS_OF = dt.date(2019, 1, 1)


@pytest.fixture(scope="module")
def stock_new():
    return year_premise_stock(2019, base_seed=SEED, n=PROSPECTS_PER_YEAR, from_fitted_joint=True)


@pytest.fixture(scope="module")
def stock_old():
    return year_premise_stock(2019, base_seed=SEED, n=PROSPECTS_PER_YEAR, from_fitted_joint=False)


# ── the margins the published record owns ───────────────────────────────────────────────────────

def test_the_raked_fitted_joint_carries_every_published_margin_it_claims_to():
    """EVIDENCE SUPPLIES THE STRUCTURE, THE PUBLISHED RECORD SUPPLIES THE MARGINS.

    NEED is a survey and the canon is explicit that it is EVIDENCE, NOT POPULATION. Its own
    property-type and EPC composition is not GB's, so a joint fitted to it and used unraked would
    be a fidelity REGRESSION dressed as an improvement -- the world would gain real co-occurrence
    and lose the published marginals it already had.
    """
    joint = pp.fitted_stock_joint()
    total = sum(joint.values())
    assert total == pytest.approx(1.0, abs=1e-9)

    def marginal(axis):
        out = collections.defaultdict(float)
        for cell, weight in joint.items():
            out[cell[axis]] += weight / total
        return out

    published_type = {t.name: s for t, s in pp.PUBLISHED_PROPERTY_TYPE_SHARE.items()}
    for name, share in marginal(pp._FITTED_PROPERTY_TYPE_AXIS).items():
        assert share == pytest.approx(published_type[name], abs=1e-6), name

    for band, share in marginal(pp._FITTED_AGE_BAND_AXIS).items():
        assert share == pytest.approx(pp.published_age_band_share()[band], abs=1e-6), band

    epc_target = pp._published_need_epc_share()
    scale = sum(epc_target.values())
    for need_class, share in marginal(pp._FITTED_EPC_AXIS).items():
        assert share == pytest.approx(epc_target[need_class] / scale, abs=1e-6), need_class


def test_the_published_era_marginal_survives_the_round_trip_exactly():
    """SIX ERAS THROUGH FOUR BANDS AND BACK, and it has to be exact rather than close.

    The joint is raked on NEED's four AGE BANDS because that is the axis it has; the world's homes
    need one of six ERAS. `published_age_band_share` projects one way and `era_posterior_by_band`
    inverts it, and the two are only a matched pair if going out and back reproduces the published
    era shares. If it does not, the world's era composition is silently whatever the projection
    happened to leave -- a published marginal replaced by an artefact of the mapping.

    MUTATION: drop `share *` from either function and this fails at the third decimal.
    """
    bands = pp.published_age_band_share()
    posterior = pp.era_posterior_by_band()

    reconstructed: dict[BuildEra, float] = collections.defaultdict(float)
    for band, mass in bands.items():
        for era, conditional in posterior[band].items():
            reconstructed[era] += mass * conditional

    for era, published in pp.PUBLISHED_BUILD_ERA_SHARE.items():
        assert reconstructed[era] == pytest.approx(published, abs=1e-12), era.name


def test_the_representative_band_to_era_map_would_have_erased_two_eras():
    """SAME TABLE, DIFFERENT SUBJECT — the trap this build walked up to and stopped at.

    `demand_case_coverage.AGE_TO_ERA` maps each of NEED's four bands to ONE representative era. It
    is correct for what it is for: computing a fabric vector, where a band needs a representative
    age. Used to populate the world it would erase `ERA_1919_1944` and `ERA_1965_1980` from the
    country entirely and move the published era marginal by about fifteen points.

    The control is on the PROPERTY, not on today's code: whatever the world draws from, every
    published era must be reachable.
    """
    from tools import demand_case_coverage as dcc

    representative = {BuildEra[name] for name in dcc.AGE_TO_ERA.values()}
    missing = set(pp.PUBLISHED_BUILD_ERA_SHARE) - representative
    assert missing, (
        "AGE_TO_ERA now covers every era, so this control no longer describes a real trap — "
        "check whether the posterior split is still needed rather than deleting the test")

    reachable = {era for column in pp.era_posterior_by_band().values() for era in column}
    assert reachable == set(pp.PUBLISHED_BUILD_ERA_SHARE), (
        f"the world cannot reach {set(pp.PUBLISHED_BUILD_ERA_SHARE) - reachable}")


# ── the rake's own promise ──────────────────────────────────────────────────────────────────────

def test_a_rake_that_returns_carries_the_margins_on_the_axes_it_was_GIVEN():
    """THE PROMISE `fitted_stock_joint` RESTS ON: a returned joint carries its targets.

    Adding `axes` split the rescaling sweep from the convergence grade — the sweep moved to the
    selected axes and the grade was still `enumerate(targets)`, i.e. axes 0..n-1. That was
    repaired before shipping.

    HONEST ABOUT WHAT THAT REPAIR WAS WORTH. R15 asks whether restoring the defect breaks a test,
    and here it does not break this one: measured on the real call, the mis-paired grade compares
    the EPC target's keys against axis 2 (`area_band`), finds none of them, and RAISES — worst
    marginal error 0.448. The mutation is LOUD, so the repair was DEFENSIVE rather than a caught
    live defect, and saying otherwise would be claiming a catch this file did not make.

    What it does guard is the case that would be silent: a wrong-axis target whose value set
    happens to match the right one's. This control asserts the property instead of the pairing,
    which holds either way and does not depend on today's axis vocabularies staying distinct.
    """
    joint = pp.fitted_stock_joint()
    total = sum(joint.values())
    axes_and_targets = (
        (pp._FITTED_PROPERTY_TYPE_AXIS,
         {t.name: s for t, s in pp.PUBLISHED_PROPERTY_TYPE_SHARE.items()}),
        (pp._FITTED_AGE_BAND_AXIS, pp.published_age_band_share()),
    )
    for axis, target in axes_and_targets:
        scale = sum(target.values())
        observed: dict = collections.defaultdict(float)
        for cell, weight in joint.items():
            observed[cell[axis]] += weight / total
        for key, share in target.items():
            assert observed[key] == pytest.approx(share / scale, abs=1e-6), (axis, key)


def test_a_target_naming_a_value_the_axis_does_not_have_is_refused():
    """FAIL CLOSED on an unfittable request. A margin the joint cannot reach must raise rather
    than return the closest thing, because every caller reads the result as carrying it."""
    joint = {("a", "x", "only"): 0.5, ("b", "y", "only"): 0.5}
    with pytest.raises(RuntimeError, match="did not converge"):
        pp.rake(joint, ({"a": 0.5, "b": 0.5}, {"only": 0.5, "absent": 0.5}),
                axes=(0, 2), max_iterations=20)


def test_positional_raking_is_untouched_by_the_axes_parameter():
    """The parameter is ADDITIVE. Every caller that predates it must be byte-identical, and
    `raked_joint()` is one of them — it feeds the pre-2026-09-10 stock path, which is the
    counterfactual arm this change is measured against. A drift there would make the comparison
    meaningless in the direction that flatters the change."""
    # A FULL FACTORIAL, because three margins over three cells have no joint that fits them and
    # the first version of this fixture asked IPF for one -- it raised, correctly, and the test
    # read as a regression in the parameter it was checking. A fixture that cannot be satisfied
    # tests the error path, not the property.
    joint = {(a, b, c): 1.0 + i
             for i, (a, b, c) in enumerate(
                 (a, b, c) for a in "ab" for b in "xy" for c in "pq")}
    targets = ({"a": 0.4, "b": 0.6}, {"x": 0.7, "y": 0.3}, {"p": 0.5, "q": 0.5})
    assert pp.rake(joint, targets) == pp.rake(joint, targets, axes=(0, 1, 2))


def test_a_missing_NEED_file_refuses_by_name_instead_of_falling_back():
    """A NEW PRECONDITION ON THE WHOLE WORLD, and the failure mode it must NOT have.

    `raked_joint()` needs only published constants, so before this change the world was buildable
    from the repository alone. The fitted joint is measured from DESNZ NEED, which lives in
    `~/.cache/synthetic-enterprise/` and is deliberately not in the tree — so a fresh checkout can
    no longer draw a home. That is a real cost and it is accepted with its eyes open.

    What it must not do is fall back. A quiet drop to the published joint gives a SECOND population
    that no output carries a marker for, and "which world produced this figure" becomes
    unanswerable afterwards. The refusal has to name the file, say it is outside the repo on
    purpose, and name the one-line override — including the warning that the override changes the
    population.
    """
    from tools import stock_joint_generator as gen

    pp.fitted_stock_joint.cache_clear()
    original = gen.fit_joint

    def absent(*_a, **_k):
        raise FileNotFoundError("/home/nobody/.cache/synthetic-enterprise/need_2026/anon.csv")

    gen.fit_joint = absent
    try:
        with pytest.raises(RuntimeError) as caught:
            pp.fitted_stock_joint()
    finally:
        gen.fit_joint = original
        pp.fitted_stock_joint.cache_clear()

    message = str(caught.value)
    assert "OUTSIDE the repository" in message
    assert "STOCK_FROM_FITTED_JOINT" in message, "the refusal does not name its own remedy"
    assert "different population" in message, (
        "the refusal offers the override without saying it changes the population — that is how "
        "two worlds get published under one set of figures")


def test_a_joint_with_no_rated_dwelling_is_refused_rather_than_returned():
    """FAIL CLOSED. The unrated rows are dropped before raking on the EPC axis; if the drop left
    nothing, returning the unrated joint would hand back a population whose EPC axis means the
    opposite of what every caller reads it as."""
    from tools import stock_joint_generator as gen

    unrated_only = collections.Counter({
        ("FLAT", "1", "2", pp.NEED_UNRATED, "0", "0", "0", "1"): 10.0})
    pp.fitted_stock_joint.cache_clear()
    original = gen.fit_joint
    gen.fit_joint = lambda *a, **k: unrated_only
    try:
        with pytest.raises(RuntimeError, match="no rated dwelling"):
            pp.fitted_stock_joint()
    finally:
        gen.fit_joint = original
        pp.fitted_stock_joint.cache_clear()


# ── what the world gained ───────────────────────────────────────────────────────────────────────

def test_the_dwelling_now_carries_measured_attributes_rather_than_inferred_ones(
        stock_new, stock_old):
    """THE DELIVERABLE, stated at the strength the evidence supports.

    Not "the demand vector becomes computable" — it always was. What changes is that the floor
    area, the loft and cavity measures and the PV flag are now MEASURED facts on the record rather
    than inferred from a bedroom count, read off an EPC letter, or absent.
    """
    assert all(p.household.floor_area_band is None for p in stock_old)
    assert all(p.household.has_loft_insulation is None for p in stock_old)

    assert all(p.household.floor_area_band is not None for p in stock_new)
    assert all(isinstance(p.household.has_loft_insulation, bool) for p in stock_new)
    assert all(isinstance(p.household.has_cavity_wall_insulation, bool) for p in stock_new)
    assert len({p.household.floor_area_band for p in stock_new}) >= 4


def test_None_means_not_drawn_from_the_joint_and_never_no_insulation(stock_old):
    """An honest `None` with a named reason beats a plausible `False`. A dwelling minted by the
    older path has no MEASURED loft flag, and `False` there is a claim the evidence never made —
    which any consumer counting uninsulated homes would read as fact."""
    for premise in stock_old[:50]:
        assert premise.household.has_loft_insulation is not False
        assert premise.household.has_cavity_wall_insulation is not False
        assert premise.household.has_mains_gas_supply is not False


def test_solar_stopped_being_false_for_every_home_in_the_country(stock_new, stock_old):
    """`has_solar=False` was HARDCODED on the drawn path. Omission is not neutrality: it asserted
    that no home in Great Britain has a panel, and zero is the one value we knew was wrong."""
    assert not any(p.household.has_solar for p in stock_old)
    with_solar = [p for p in stock_new if p.household.has_solar]
    assert with_solar, "the PV flag is not reaching the world"
    assert all(p.household.solar_kwp > 0.0 for p in with_solar)
    assert all(p.household.solar_kwp == 0.0 for p in stock_new if not p.household.has_solar)


def test_insulation_stopped_being_a_lookup_on_the_epc_letter(stock_new, stock_old):
    """Six distinct values in the whole country, because `insulation` was a dict keyed on the EPC
    band. The measured loft and cavity flags are what an installer actually did."""
    old_pairs = {(p.household.epc_rating, p.household.insulation) for p in stock_old}
    assert len(old_pairs) == len({p.household.epc_rating for p in stock_old})

    new_triples = {(p.household.epc_rating, p.household.has_loft_insulation,
                    p.household.has_cavity_wall_insulation) for p in stock_new}
    assert len(new_triples) > len(old_pairs)

    for premise in stock_new:
        installed = (int(premise.household.has_loft_insulation)
                     + int(premise.household.has_cavity_wall_insulation))
        expected = (InsulationLevel.FULL if installed == 2
                    else InsulationLevel.PARTIAL if installed == 1 else InsulationLevel.POOR)
        assert premise.household.insulation is expected


def test_the_meter_fact_is_not_folded_into_the_heating_system(stock_new):
    """TWO CONCEPTS, AND THE WHOLE POINT IS THAT THEY STAY TWO.

    NEED's `MAIN_HEAT_FUEL` is derived from whether a gas meter was matched, so it answers "is
    there a gas supply this dwelling is billed on". `heating_system` answers "what burns". The
    2026-09-07 measurement found 50.3% of flats reading as "not gas" when they are communal or
    unmetered, not off-grid.

    This control exists because folding one into the other is the obvious tidy-up, it would look
    like an improvement, and it is the *bill shock* mistake in new clothes — one word, two
    populations. A later lane that maps `has_mains_gas_supply` onto `heating_system` fails here.
    """
    gas_systems = (HeatingSystem.GAS_BOILER_COMBI, HeatingSystem.GAS_BOILER_SYSTEM)
    cross = collections.Counter(
        (p.household.has_mains_gas_supply, p.household.heating_system in gas_systems)
        for p in stock_new)
    assert cross[(False, True)] > 0, (
        "no dwelling has a gas boiler without a matched gas meter — the supply flag has been "
        "folded into the heating system, and the disagreement the two facts exist to show is gone")
    assert cross[(True, False)] > 0, "no dwelling has a gas supply and a non-gas heating system"


def test_bedrooms_are_derived_from_floor_area_not_drawn_beside_it(stock_new):
    """Area is the physical quantity the heat loss is computed from; bedrooms is what an estate
    agent counts. Deriving the second from the first is the right direction, and drawing both
    independently would let a one-bedroom home have 230 m2."""
    from simulation import fabric_physics as fp
    from tools import demand_case_coverage as dcc

    by_band: dict[str, set[int]] = collections.defaultdict(set)
    for premise in stock_new:
        by_band[premise.household.floor_area_band].add(premise.household.bedrooms)
        area = dcc.AREA_MIDPOINT[premise.household.floor_area_band]
        base = fp._FLOOR_AREA_BASE_M2[premise.household.property_type]
        expected = int(max(1, min(6, round(2 + (area - base) / fp._FLOOR_AREA_PER_BEDROOM_M2))))
        assert premise.household.bedrooms == expected

    biggest = max(by_band)
    smallest = min(by_band)
    assert min(by_band[biggest]) > min(by_band[smallest]), (
        "the largest floor-area band does not carry more bedrooms than the smallest")


def test_a_premise_is_identical_whatever_else_is_in_the_population():
    """C-S2, and it is what makes a win attributable to the campaign rather than to the draw.

    Every attribute takes its own substream keyed on the premise id — including the four that are
    new here. Sharing one stream would make a home's EPC depend on whether it happened to have
    solar, and growing the stock would re-roll homes nobody touched.
    """
    one = pp.draw_premise_from_joint("PSTK-2019-0007", base_seed=SEED, as_of=AS_OF)
    again = pp.draw_premise_from_joint("PSTK-2019-0007", base_seed=SEED, as_of=AS_OF)
    other = pp.draw_premise_from_joint("PSTK-2019-0008", base_seed=SEED, as_of=AS_OF)

    assert one == again
    assert one != other

    small = year_premise_stock(2019, base_seed=SEED, n=10, from_fitted_joint=True)
    large = year_premise_stock(2019, base_seed=SEED, n=400, from_fitted_joint=True)
    assert small == large[:10], "growing the stock re-rolled a home nobody touched"


def test_the_published_margins_hold_across_seeds_and_not_only_this_one():
    """THE FIRST GRADING OF THIS CHANGE WAS AGAINST ONE SEED AND IT MISREAD A COINCIDENCE.

    On seed 20260724 `ERA_1919_1944` came out 3.29 standard errors light, which looks like a
    biased mapping. It is not: across five seeds its mean z is -0.09, and no era's mean |z| exceeds
    0.44. A single-seed reading of a sampled marginal cannot separate a bias from a draw, which is
    the same lesson as "a reading of chance has two causes".

    Kept as a CONTROL rather than as a note, because a real bias in the era mapping would be
    invisible to every other test in this file.
    """
    published = {e.name: s for e, s in pp.PUBLISHED_BUILD_ERA_SHARE.items()}
    scale = sum(published.values())
    published = {k: v / scale for k, v in published.items()}

    totals: dict[str, float] = collections.defaultdict(float)
    seeds = (20260724, 11111, 22222)
    for seed in seeds:
        counts = collections.Counter(
            p.household.build_era.name
            for p in year_premise_stock(2019, base_seed=seed, n=PROSPECTS_PER_YEAR,
                                        from_fitted_joint=True))
        n = sum(counts.values())
        for era, share in published.items():
            se = math.sqrt(share * (1 - share) / n)
            totals[era] += (counts[era] / n - share) / se

    for era, z_sum in totals.items():
        assert abs(z_sum / len(seeds)) < 1.5, (
            f"{era} is {z_sum / len(seeds):+.2f} SE from published on average across "
            f"{len(seeds)} seeds — that is a mapping bias, not a draw")


def test_the_chooser_is_deliberately_not_wired_into_the_stock():
    """A REFUSAL, RECORDED AS A CONTROL. Measured at the world's own size, `choose_for_difference`
    + `fit_weights` is 1.04x better than a random draw on worst KS across the six demand axes —
    its value is compression and at 4,400 draws there is nothing to compress.

    This test exists so that wiring it in later is a DECISION with a measurement to overturn,
    rather than something that drifts in because the module name sounds like it belongs.

    READ AS CODE, NOT AS TEXT. The first version grepped the source for the name and went red on
    the COMMENT that explains why the chooser is absent — a control firing on its own subject's
    explanation, which is how a correct control gets deleted by the next person who meets it. The
    AST carries calls and imports; comments are not in it, and a docstring is a `Constant` rather
    than the `Name`/`Attribute`/`alias` nodes checked here.

    MUTATION: add `from tools.demand_vector_coverage import choose_for_difference` to either
    module and this fires; write the word in a comment and it does not.
    """
    import ast
    from pathlib import Path

    import simulation.net_new_acquisition as nna
    import simulation.premise_population as ppm

    watched = {"choose_for_difference", "fit_weights", "smallest_n_chosen"}
    for module in (nna, ppm):
        tree = ast.parse(Path(module.__file__).read_text(encoding="utf-8"))
        referenced = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                referenced.add(node.id)
            elif isinstance(node, ast.Attribute):
                referenced.add(node.attr)
            elif isinstance(node, ast.ImportFrom):
                referenced.update(a.name for a in node.names)
        hit = watched & referenced
        assert not hit, (
            f"{module.__name__} now references {sorted(hit)} as code — if that is intended, the "
            "1.04x measurement in the 2026-09-10 pre-registration is what has to be overturned "
            "first, not worked around")


def test_the_old_path_still_exists_and_still_differs(stock_new, stock_old):
    """The counterfactual arm has to remain runnable. A change that deletes what it is measured
    against cannot be graded, and P5 of the pre-registration is graded on exactly this pair."""
    assert len(stock_new) == len(stock_old) == PROSPECTS_PER_YEAR
    assert stock_new != stock_old
    assert all(isinstance(p.household.property_type, PropertyType) for p in stock_new)
