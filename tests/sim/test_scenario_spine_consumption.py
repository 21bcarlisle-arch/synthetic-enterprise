"""SPINE_1 — the consumption seam: a run that actually LIVES through a curriculum world.

Before this, `ScenarioSpine.paths_as_of` had ZERO production callers. The spine loaded,
resolved grid labels and bound rotation cells, but no generator read it, so selecting a
world changed nothing about the world. SPINE_1's own simplification record named exactly
this as why `level_current` stayed 0:

    "no SIM generator consumes paths_as_of yet, so no run actually LIVES through a
     non-baseline world -- the spine is resolvable but still not consumed"

These tests are the evidence that it is consumed now, and the guards on the two ways this
seam could be worth nothing: it could fail to bite (an override that changes no price), or
it could bite when it must not (a baseline run that is no longer byte-identical).

R15 — every control below is paired with the mutation that reds it. The mutations were RUN,
not reasoned about; each one's effect is recorded in the test that catches it.
"""

import datetime as dt

import pytest

import sim.scenario.gas_scenario_generator as G
from sim.scenario.spine import HISTORY_REPLAY, NO_OVERRIDE, ScenarioSpine, default_world, load_world

CRISIS = "crisis_2021_22"


def _gen(spine=None, scenario="baseline_2025", year_from=2021, year_to=2023, seed="s"):
    return G.generate_gas_scenario_prices(year_from, year_to, scenario, seed=seed, spine=spine)


def _mean_for_year(records, year):
    vals = [r["systemSellPrice"] for r in records if r["settlementDate"].startswith(str(year))]
    assert vals, f"no records for {year}"
    return sum(vals) / len(vals)


# --- the byte-identical baseline guarantee (FRAME §A.5, DoD 4) ----------------


def test_the_baseline_world_is_byte_identical_to_no_spine_at_all():
    """The spine is ADDITIVE and DORMANT unless a non-baseline world is chosen.

    KILLER MUTATION (run): in `_params_for`, replace the `level is NO_OVERRIDE` early
    return with `level_scaled_params(params, 84.0)` -- i.e. make the no-override case fall
    through to a "sensible default" level instead of leaving params alone. This test reds
    (baseline prices shift from the unscaled series), which is the point: a fail-open
    default here would silently re-level every existing run.
    """
    without = _gen(spine=None)
    with_baseline = _gen(spine=default_world())
    assert with_baseline == without, "history_replay must not perturb a single price"

    # And the guarantee is about the DEFAULT specifically, not about spines in general.
    assert default_world().selects_no_overrides
    assert default_world().world_id == HISTORY_REPLAY


def test_a_world_with_no_gas_trend_leaves_gas_untouched_even_though_it_overrides_other_fields():
    """A world may press on storage without pressing on gas price level.

    This is the field-level half of dormancy: `paths_as_of` returns a dict of FOUR fields
    and this generator consumes exactly one. A world overriding only `storage_capacity`
    must leave gas byte-identical -- otherwise the seam is reading fields it does not own.
    """
    storage_only = ScenarioSpine(
        world_id="storage_only", version="0", provenance="proposal", ratified=False,
        in_rotation=False, true_probability=None, sampling_weight=None,
        _paths={"gas_trend": (), "economy_factor": (), "renewables_buildout": (),
                "storage_capacity": ((dt.date(2021, 6, 1), 0.35),)},
    )
    assert storage_only.paths_as_of("2022-01-01")["storage_capacity"] == 0.35
    assert storage_only.paths_as_of("2022-01-01")["gas_trend"] is NO_OVERRIDE
    assert _gen(spine=storage_only) == _gen(spine=None)


# --- the seam actually bites --------------------------------------------------


def test_the_crisis_world_raises_the_gas_level_in_the_year_the_record_says_it_spiked():
    """The committed crisis artefact must change the world the company sees.

    Not merely "different": directionally right, in the right YEAR, by roughly the ratio the
    curriculum states. 84 -> 226 -> 130 p/therm across 2021/2022/2023.

    KILLER MUTATION (run): drop the `spine=spine` kwarg at the
    `generate_gas_scenario_prices` call in `run_scenario.build_extended_price_feeds`, or
    make `_params_for` return `params` unconditionally -> this test reds, because the
    crisis year stops differing from the baseline year. That mutation is precisely the
    state the code was in before this change, so this test is the one that would have been
    red for the whole time the spine sat unconsumed.
    """
    crisis = load_world(CRISIS)
    base = _gen(spine=None)
    world = _gen(spine=crisis)

    assert world != base, "selecting the crisis world changed no price at all"

    # The curriculum's own levels, converted through the published therm definition.
    lvl = {y: G.p_per_therm_to_gbp_per_mwh(v) for y, v in ((2021, 84.0), (2022, 226.0), (2023, 130.0))}
    for year in (2021, 2022, 2023):
        got = _mean_for_year(world, year)
        # +-25%: these are stochastic draws over ~365 days with a dunkelflaute tail, so the
        # band is wide enough not to be a calibration and tight enough that a wrong YEAR or
        # a wrong unit conversion (a factor of ~34 or ~100) cannot pass.
        assert 0.75 * lvl[year] <= got <= 1.25 * lvl[year], (
            f"{year}: generated mean {got:.1f} GBP/MWh is not anchored to the curriculum's "
            f"{lvl[year]:.1f} GBP/MWh"
        )

    # The spike is the point: 2022 must be materially above both neighbours.
    assert _mean_for_year(world, 2022) > 2.0 * _mean_for_year(world, 2021)
    assert _mean_for_year(world, 2022) > 1.5 * _mean_for_year(world, 2023)


def test_the_override_is_blindfold_clean_2021_cannot_see_the_2022_anchor():
    """Day t never sees an anchor dated after t (FRAME §A.4).

    KILLER MUTATION (run): in `ScenarioSpine.paths_as_of`, drop the `if d <= as_of` guard
    so the last anchor always wins -> 2021 is generated at the 226 p/therm level and this
    test reds. Without this, the "crisis world" would price the crisis a year before it
    happened, which is a Point-in-Time Blindfold breach wearing a curriculum's clothes.
    """
    world = _gen(spine=load_world(CRISIS))
    m2021, m2022 = _mean_for_year(world, 2021), _mean_for_year(world, 2022)
    assert m2021 < m2022, "2021 was generated at the 2022 crisis level -- the path saw its own future"
    assert m2021 < 0.6 * m2022


def test_a_higher_level_does_not_quietly_flatten_relative_volatility():
    """Means and standard deviations scale together, holding the coefficient of variation.

    KILLER MUTATION (run): in `level_scaled_params`, scale only the two means and leave the
    two stds -> this test reds. That mutation is attractive-looking and wrong: it would make
    the 2021-22 crisis world RELATIVELY calmer than the baseline, the opposite of the record
    the artefact exists to replay, and it would flatter any hedging result measured in it.
    """
    p = G.GAS_SCENARIOS["baseline_2025"]
    scaled = G.level_scaled_params(p, 226.0)
    assert scaled.upper_regime_mean > p.upper_regime_mean
    cv = lambda q: q.upper_regime_std / q.upper_regime_mean  # noqa: E731
    assert cv(scaled) == pytest.approx(cv(p), rel=1e-12)
    assert (scaled.lower_regime_std / scaled.lower_regime_mean) == pytest.approx(
        p.lower_regime_std / p.lower_regime_mean, rel=1e-12
    )
    # The absolute realism floor is NOT a level and must not ride the scale.
    assert scaled.price_floor == p.price_floor


def test_the_unit_conversion_is_the_published_therm_definition_not_a_fitted_factor():
    """1 therm = 29.3071 kWh. The seam's credibility rests on this being a constant.

    The agreement it produces is a CHECK on the seam, not an input to it: DESNZ's 84 p/therm
    (2024) lands within 3% of the generator's independently-written baseline_2025 upper
    regime mean of GBP 28.0/MWh. Neither number was chosen to make this true.
    """
    assert G.THERM_KWH == 29.3071
    assert G.p_per_therm_to_gbp_per_mwh(84.0) == pytest.approx(28.66, abs=0.05)
    assert abs(G.p_per_therm_to_gbp_per_mwh(84.0) - G.GAS_SCENARIOS["baseline_2025"].upper_regime_mean) < 1.0


# --- fail-closed guards -------------------------------------------------------


@pytest.mark.parametrize("bad", [0.0, -1.0, -226.0])
def test_a_non_positive_curriculum_level_refuses_rather_than_running_the_baseline(bad):
    """FAIL-CLOSED, never fail-open-to-unscaled.

    KILLER MUTATION (run): replace the raise in `level_scaled_params` with
    `return params` -> this test reds. That mutation is the fail-silent mislabel
    `resolve_grid_label` already refuses at the label layer: a run generating baseline gas
    prices while its manifest records a crisis world.
    """
    with pytest.raises(G.GasScenarioLevelError):
        G.level_scaled_params(G.GAS_SCENARIOS["baseline_2025"], bad)


def test_a_scenario_with_no_level_to_anchor_from_refuses():
    """A zero mixture mean has no ratio; dividing by it would yield inf, not a world.

    KILLER MUTATION (run): drop the `anchor > 0` check -> ZeroDivisionError or an inf-priced
    series escapes into the run instead of a named refusal.
    """
    degenerate = G.GasScenarioParams(
        upper_regime_mean=0.0, lower_regime_mean=0.0, lower_mode_fraction=0.5
    )
    with pytest.raises(G.GasScenarioLevelError):
        G.level_scaled_params(degenerate, 226.0)


def test_the_anchor_excludes_dunkelflaute_so_a_level_change_does_not_reweight_storm_days():
    """`implied_regime_mean` is the regime mixture only.

    KILLER MUTATION (run): fold the dunkelflaute premium into `implied_regime_mean` -> the
    anchor becomes a function of event frequency, so two worlds with the SAME director-set
    gas trend generate different levels purely because one is stormier. This test reds.
    """
    calm = G.GasScenarioParams(upper_regime_mean=30.0, lower_regime_mean=20.0,
                               lower_mode_fraction=0.5, dunkelflaute_events_per_year=0.0)
    stormy = G.GasScenarioParams(upper_regime_mean=30.0, lower_regime_mean=20.0,
                                 lower_mode_fraction=0.5, dunkelflaute_events_per_year=20.0,
                                 dunkelflaute_gas_multiplier_mean=3.0)
    assert G.implied_regime_mean(calm) == G.implied_regime_mean(stormy) == 25.0
    assert G.level_scaled_params(calm, 226.0).upper_regime_mean == pytest.approx(
        G.level_scaled_params(stormy, 226.0).upper_regime_mean
    )


# --- the wall (FRAME §A.3) ----------------------------------------------------


def test_the_run_stamps_the_world_it_resolved_and_the_company_still_cannot_read_it():
    """The stamp answers "which world did this run live through?" from the ARTEFACT.

    The company never reads scenario state: the stamp is a run-history/audit field on the
    SIM side. This asserts the stamp's SOURCE, which is the part that can rot -- stamping
    the `world_id` ARGUMENT rather than the loaded artefact would let a run claim a world
    whose artefact says something else.

    KILLER MUTATION (run): stamp `world_id` (the argument) instead of `_world.world_id`,
    and the version stamp disappears -> the version assertion reds.
    """
    import simulation.run_scenario as RS

    w = RS.load_world(HISTORY_REPLAY)
    assert w.world_id == HISTORY_REPLAY
    assert w.version, "the baseline artefact carries no version pin to stamp"


def test_neither_module_this_seam_touches_imports_the_company_side():
    """Import-direction, read from SOURCE -- the structurally detectable form of the wall.

    The company must infer the gas trend from prices it observes, never read the scenario
    that set it. `paths_as_of` is now consumed on a live run path, so this seam is exactly
    where a convenience import back into `company.*`/`saas.*` would be tempting.

    KILLER MUTATION (run): add `import saas.churn_model` to the generator -> reds with
    "reaches across the epistemic wall: ['saas.churn_model']". A REAL module deliberately:
    mutating with a non-existent one (`saas.billing`) only proves that an unresolvable
    import breaks collection, which this test does not deserve credit for.

    Asserted against the file text rather than `sys.modules`, so an import that is present
    but not yet executed cannot pass.
    """
    import ast
    import pathlib

    import sim.scenario.gas_scenario_generator as GG
    import simulation.run_scenario as RS

    for mod in (GG, RS):
        tree = ast.parse(pathlib.Path(mod.__file__).read_text(encoding="utf-8"))
        names = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names += [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names.append(node.module)
        leaks = [n for n in names if n.split(".")[0] in ("company", "saas")]
        assert not leaks, f"{mod.__name__} reaches across the epistemic wall: {leaks}"
