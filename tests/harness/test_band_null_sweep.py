"""R15 for the H33 band-null sweep — both ways, plus the vacuity guard.

The sweep's own fail-open shapes, and the test that closes each:

* it enumerates NOTHING and reports a clean sheet  -> `test_an_empty_enumeration_RAISES`
* a band has no null spec and is silently skipped  -> `test_a_band_with_no_null_spec_RAISES`
* a band table appears in another module           -> `test_a_band_table_outside_the_swept_set_is_FOUND`
* the null itself injects the structure it removes -> `test_the_null_does_not_INVENT_structure`
* a band's null is read on the wrong load set      -> `test_a_bands_null_is_read_only_on_the_homes_it_JUDGES`
* the verdict cannot move                          -> `test_a_threshold_moved_INTO_its_null_flips_the_verdict`
"""

from __future__ import annotations

import dataclasses
import math
import random
import textwrap

import pytest

from background import band_null_sweep as bns
from background import fabric_gap_ledger as fgl

DAYS = 120
PERIODS = fgl.PERIODS_PER_DAY


def _home(rng: random.Random, *, level: float, peak_period: int) -> list[list[float]]:
    """A synthetic home with all four structures the bands certify: a diurnal
    shape, appliance events, day-to-day variety and occasional absences."""
    grid: list[list[float]] = []
    for d in range(DAYS):
        away = d % 17 == 0
        day: list[float] = []
        for p in range(PERIODS):
            base = level * 0.4
            if 14 <= p <= 20:
                base += level * 0.5
            if abs(p - peak_period) <= 2:
                base += level * (1.4 if not away else 0.05)
            if not away and rng.random() < 0.12:
                base += level * rng.uniform(1.0, 3.0)     # an appliance event
            # The jitter is LARGE on purpose. A real home's half-hour moves in the
            # tens of percent of its own mean (a kettle is 2.8 kW for three
            # minutes), and a fixture that only wobbles by +/-15% is smoother than
            # its own 120-day mean profile — which would make the flat-day null
            # look no smoother than the trace it was built from and prove nothing.
            day.append(max(base * rng.uniform(0.35, 1.9), 0.01))
        grid.append(day)
    return grid


def _population(*, homes: int = 10, heating: tuple[str, ...] | None = None) -> fgl.PopulationTraces:
    rng = random.Random(4)
    grids = [
        _home(rng, level=0.2 + 0.09 * i, peak_period=32 + (i % 7))
        for i in range(homes)
    ]
    return fgl.PopulationTraces(
        generator="fixture",
        homes=tuple(f"H{i}" for i in range(homes)),
        grids=tuple(tuple(tuple(day) for day in g) for g in grids),
        is_weekend=tuple((d % 7) in (5, 6) for d in range(DAYS)),
        annual_kwh=tuple(900.0 * (1 + 0.6 * i) for i in range(homes)),
        weather_driver=tuple(8.0 + 6.0 * math.sin(d / 19.0) for d in range(DAYS)),
        heating_systems=heating or tuple("gas_boiler_combi" for _ in range(homes)),
    )


@pytest.fixture(scope="module")
def population() -> fgl.PopulationTraces:
    return _population()


# ---------------------------------------------------------------------------
# (1) THE ENUMERATION — and the vacuity guard on it
# ---------------------------------------------------------------------------


def test_the_enumeration_is_NON_EMPTY_on_the_live_tree():
    """The vacuity guard. A sweep that finds no bands reports a clean sheet
    indistinguishable from a real one, so an empty enumeration on the live tree
    is the fail-open shape this whole module has to rule out first."""
    bands = bns.anchored_bands()
    assert bands, "the enumeration is empty — the sweep would report a clean sheet"
    for name, band in bands.items():
        assert band.threshold is not None and math.isfinite(band.threshold)
        assert band.anchor in bns.EXTERNAL_ANCHORS, name


def test_the_enumeration_is_DERIVED_from_the_live_table_not_a_copied_list():
    """A band added to the table must appear in the enumeration without anyone
    editing this module. Proven by adding one and looking."""
    invented = fgl.Band(
        statistic="L9.9_invented", level="L1", direction="at_least", threshold=0.4,
        anchor=fgl.AnchorStatus.PUBLISHED, anchor_source="a test",
        observed_on_shipped=None, rationale="a test",
    )
    with pytest.MonkeyPatch.context() as mp:
        mp.setitem(fgl.BANDS, "L9.9_invented", invented)
        assert "L9.9_invented" in bns.anchored_bands()


def test_every_band_is_either_SWEPT_or_EXCLUDED_with_a_reason():
    """No band may fall between the two lists. A band that is in neither is one
    nobody is looking at, which is the same as one nobody found a problem with."""
    swept, excluded = set(bns.anchored_bands()), set(bns.excluded_bands())
    assert swept | excluded == set(fgl.BANDS)
    assert not (swept & excluded)


def test_an_empty_enumeration_RAISES(population):
    """FAIL-SILENT, closed. If the band table moves or the anchor classes are
    renamed, the sweep must refuse to report rather than return []."""
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(fgl, "BANDS", {})
        with pytest.raises(bns.SweepIncomplete, match="EMPTY"):
            bns.sweep(population, replications=2)


def test_a_band_with_no_null_spec_RAISES(population):
    """An unmeasured null is not a clean one. Removing a spec must stop the
    sweep, never quietly shrink its coverage."""
    with pytest.MonkeyPatch.context() as mp:
        specs = dict(bns.NULL_SPECS)
        specs.pop("L2.2_between_home_correlation")
        mp.setattr(bns, "NULL_SPECS", specs)
        with pytest.raises(bns.SweepIncomplete, match="L2.2_between_home_correlation"):
            bns.sweep(population, replications=2)


def test_no_band_table_lives_outside_the_swept_set_on_the_live_tree():
    assert bns.unswept_band_sources() == []


def test_a_band_table_outside_the_swept_set_is_FOUND(tmp_path, monkeypatch):
    """The completeness guard on the enumeration's SOURCE. `anchored_bands` can
    only be as complete as the table it reads; a second table in another module
    would leave it truthfully reporting a clean sweep of the wrong half."""
    (tmp_path / "background").mkdir()
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "other.py").write_text(textwrap.dedent("""
        from background.fabric_gap_ledger import Band, AnchorStatus
        SOMEWHERE_ELSE = Band(
            statistic="L8.8", level="L1", direction="at_least", threshold=0.2,
            anchor=AnchorStatus.PUBLISHED, anchor_source="", observed_on_shipped=None,
            rationale="",
        )
    """), encoding="utf-8")
    monkeypatch.setattr(bns, "PROJECT_DIR", tmp_path)
    assert bns.unswept_band_sources() == ["tools/other.py"]


def test_a_MENTION_of_a_band_is_not_a_declaration(tmp_path, monkeypatch):
    """The guard must not fire on prose. `lcl_household_anchors.py` discusses
    `AnchorStatus.NEED` in its docstring and declares no band; a guard that
    counted that would be red on the live tree from birth, and an always-red
    detector is as ignored as a blind one."""
    (tmp_path / "background").mkdir()
    (tmp_path / "tools").mkdir()
    (tmp_path / "background" / "prose.py").write_text(
        '"""Talks about Band(...) and RateBand(...) and nothing else."""\n'
        "# Band(threshold=0.5) in a comment is still not a band\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(bns, "PROJECT_DIR", tmp_path)
    assert bns.unswept_band_sources() == []


def test_the_applied_window_is_READ_from_the_tool_not_restated():
    """The window is half the measurement. If the coupling tool's window moves
    and this number does not, every margin in the sweep is about a population
    nobody judges."""
    from tools import couple_fabric as cf

    homes, days = bns.applied_window()
    assert homes == len(cf.PANEL)
    assert days == (cf.WINDOW_END - cf.WINDOW_START).days + 1


# ---------------------------------------------------------------------------
# (2) THE NULLS — a null that adds structure is not a null
# ---------------------------------------------------------------------------


def test_the_null_does_not_INVENT_structure(population):
    """The regression test for this module's own two defects, both the same
    mistake: a null that ADDS movement the band measures.

    v1 resampled each day's TOTAL from the home's own days — injecting level
    jumps across the midnight boundary, taking texture from ~0.05 to ~0.35 and
    inventing 120 away days per home, so three bands reported fail-open on
    structure the null had put there. v2 kept a BOOTSTRAP of the mean profile,
    whose sampling noise IS half-hourly movement, inflating the texture null ~30%
    and flipping one band into a defect on the strength of it.

    So: daily totals survive exactly, and the null is deterministic — the same
    population however often it is drawn.
    """
    null = bns._flat_day_null(population, random.Random(1))
    for real_home, null_home in zip(population.grids, null.grids):
        for real_day, null_day in zip(real_home, null_home):
            assert sum(null_day) == pytest.approx(sum(real_day), rel=1e-9)

    again = bns._flat_day_null(population, random.Random(999))
    assert again.grids == null.grids


def test_the_flat_day_null_REMOVES_the_structure_all_three_bands_certify(population):
    """It must actually be structureless: smoother than the real trace (L1.1),
    perfectly repetitive (L1.2), and incapable of an absence (L1.3)."""
    null = bns._flat_day_null(population, random.Random(1))
    for real_home, null_home in zip(population.grids, null.grids):
        assert fgl.half_hourly_texture(null_home) < fgl.half_hourly_texture(real_home)
        assert fgl.day_to_day_shape_correlation(null_home) == pytest.approx(1.0, abs=1e-9)
        assert fgl.trough_statistics(null_home).away_signature_days == 0


# ---------------------------------------------------------------------------
# H37 — L1.3 is now read NET OF SPACE HEAT, so its null has to be taken there
# too. A null taken on the meter and read on the behavioural stream leaves the
# heating machine's own structure in the reading with a minus sign in front of
# it, and the band goes back inside its null on the strength of structure the
# null itself put there. That is this module's founding defect, one cell over.
# ---------------------------------------------------------------------------

# Panel heaters: off through the base-load window, on when the room is used.
# SHAPED on purpose — a constant draw would be a level shift, and a level shift
# is invisible to a ratio, so a flat heat stream could not tell the right null
# from the wrong one.
_RESISTIVE_HEAT_DAY = tuple(0.0 if p in fgl.BASE_LOAD_PERIODS else 0.9 for p in range(PERIODS))


def _electrically_heated_population(*, homes: int = 10) -> fgl.PopulationTraces:
    """The same fixture homes with a panel heater added to the JUDGED meter, and
    the split declared — the population H37 is about."""
    base = _population(homes=homes)
    heat = tuple(tuple(_RESISTIVE_HEAT_DAY) for _ in range(DAYS))
    return dataclasses.replace(
        base,
        grids=tuple(
            tuple(tuple(v + h for v, h in zip(day, _RESISTIVE_HEAT_DAY)) for day in home)
            for home in base.grids
        ),
        heating_systems=tuple("electric_direct" for _ in range(homes)),
        space_heat_grids=tuple(heat for _ in range(homes)),
    )


@pytest.fixture(scope="module")
def electric_population() -> fgl.PopulationTraces:
    return _electrically_heated_population()


def test_H37_the_behavioural_null_LEAVES_THE_HEATING_MACHINE_ALONE(electric_population):
    """What the null must and must not touch: the heat stream survives exactly (it
    is not the structure L1.3 certifies), each day's BEHAVIOURAL total survives
    exactly (that is level, not shape), and the whole thing is deterministic."""
    null = bns._flat_behavioural_day_null(electric_population, random.Random(1))
    assert null.space_heat_grids == electric_population.space_heat_grids
    for k, (real, made) in enumerate(zip(electric_population.grids, null.grids)):
        heat = bns._heat_of(electric_population, k)
        before = fgl.meter_net_of_space_heat([list(d) for d in real], heat)
        after = fgl.meter_net_of_space_heat([list(d) for d in made], heat)
        for b_day, a_day in zip(before, after):
            assert sum(a_day) == pytest.approx(sum(b_day), rel=1e-9)
        assert fgl.day_to_day_shape_correlation(after) == pytest.approx(1.0, abs=1e-9)
    assert bns._flat_behavioural_day_null(
        electric_population, random.Random(999)
    ).grids == null.grids


def test_H37_the_behavioural_null_is_the_METER_null_where_there_is_no_split(population):
    """With nothing to net, the behavioural stream IS the meter — so the new null
    must degrade to the old one exactly, not to something merely similar."""
    assert (
        bns._flat_behavioural_day_null(population, random.Random(1)).grids
        == bns._flat_day_null(population, random.Random(1)).grids
    )


def test_H37_taking_the_null_on_the_METER_puts_L1_3_back_INSIDE_it(electric_population):
    """THE MUTATION. Swap the behavioural null for the meter null — the one change
    this repair is — and L1.3 goes back inside its own null, because the netted
    reading of a flattened meter is a real heating shape inverted. The guard fires
    on its own named defect, and the repaired null is not merely a rename."""
    repaired = bns.measure_null("L1.3_away_days_per_year", electric_population)
    assert repaired.verdict is bns.NullVerdict.SEPARATED, repaired.note

    spec = bns.NULL_SPECS["L1.3_away_days_per_year"]
    with_meter_null = dataclasses.replace(spec, make_null=bns._flat_day_null)
    patched = dict(bns.NULL_SPECS, **{"L1.3_away_days_per_year": with_meter_null})
    original = bns.NULL_SPECS.copy()
    bns.NULL_SPECS.update(patched)
    try:
        mutated = bns.measure_null("L1.3_away_days_per_year", electric_population)
    finally:
        bns.NULL_SPECS.clear()
        bns.NULL_SPECS.update(original)
    assert mutated.verdict is bns.NullVerdict.INSIDE_NULL, (
        f"the meter null read {mutated.null_best} away days per home — if this is "
        "no longer a defect, the behavioural null is proved by nothing"
    )


def test_H37_the_sweep_reads_L1_3_on_the_SAME_load_set_the_ledger_judges(electric_population):
    """The wrong-load-set shape, in the direction that is easy to miss: not the
    wrong HOMES but the wrong STREAM. If the sweep read the raw meter it would
    report a margin for a band nobody applies."""
    from_sweep = bns._per_home_away_days(electric_population)
    from_ledger = [
        float(
            fgl.trough_statistics(
                [list(d) for d in home],
                space_heat=[list(d) for d in electric_population.space_heat_grids[k]],
            ).away_signature_days
        )
        for k, home in enumerate(electric_population.grids)
    ]
    on_the_raw_meter = [
        float(fgl.trough_statistics([list(d) for d in home]).away_signature_days)
        for home in electric_population.grids
    ]
    assert from_sweep == from_ledger
    assert from_sweep != on_the_raw_meter, (
        "this fixture must make the two load sets DISAGREE, or the assertion "
        "above holds for both and proves nothing"
    )


def test_the_exchangeable_homes_null_leaves_homes_with_NO_timing_of_their_own(population):
    """L2.3's null. Dealing the same days back out must preserve the population's
    days exactly — it removes whose they are, not what they contain."""
    null = bns._exchangeable_homes_null(population, random.Random(1))
    def pot(pop):
        return sorted(tuple(day) for home in pop.grids for day in home)
    assert pot(null) == pot(population)
    assert [len(h) for h in null.grids] == [len(h) for h in population.grids]
    assert fgl.timing_diversity(null.grids) < fgl.timing_diversity(population.grids)


def test_the_clone_null_leaves_NOTHING_for_aggregation_to_smooth(population):
    null = bns._clone_population_null(population, random.Random(1))
    assert fgl.smoothing_ratio(fgl.smoothing_curve(null.grids)) == pytest.approx(1.0, abs=1e-6)


# ---------------------------------------------------------------------------
# (3) THE VERDICT — it must be able to move, and only for the right reason
# ---------------------------------------------------------------------------


def test_a_threshold_moved_INTO_its_null_flips_the_verdict(population):
    """R15 the firing direction. L1.2's null is a perfectly repetitive population
    reading 1.0 against an at-most band of 0.85, so it is SEPARATED. Move the
    threshold above 1.0 and the structureless population passes — the band can no
    longer fail on the absence of the variety it certifies."""
    name = "L1.2_day_to_day_shape_correlation"
    clean = bns.measure_null(name, population, replications=3)
    assert clean.verdict is bns.NullVerdict.SEPARATED

    with pytest.MonkeyPatch.context() as mp:
        loosened = fgl.Band(
            statistic=name, level="L1", direction="at_most", threshold=1.5,
            anchor=fgl.AnchorStatus.DOMAIN_KNOWLEDGE, anchor_source="mutation",
            observed_on_shipped=None, rationale="mutation",
        )
        mp.setitem(fgl.BANDS, name, loosened)
        assert bns.measure_null(name, population, replications=3).verdict is (
            bns.NullVerdict.INSIDE_NULL
        )


def test_a_band_separated_by_LESS_than_its_nulls_spread_is_a_finding(population):
    """The middle verdict has to be reachable too, or the sweep is a two-state
    control wearing a three-state label."""
    name = "L1.1_half_hourly_texture"
    measured = bns.measure_null(name, population, replications=40)
    nudged_threshold = measured.null_best + measured.null_spread * 0.5
    with pytest.MonkeyPatch.context() as mp:
        mp.setitem(fgl.BANDS, name, fgl.Band(
            statistic=name, level="L1", direction="at_least",
            threshold=nudged_threshold, anchor=fgl.AnchorStatus.DOMAIN_KNOWLEDGE,
            anchor_source="mutation", observed_on_shipped=None, rationale="mutation",
        ))
        assert bns.measure_null(name, population, replications=40).verdict is (
            bns.NullVerdict.SAME_ORDER
        )


def test_a_band_far_above_its_null_stays_SEPARATED(population):
    """The non-firing direction. A control that reds on everything is as useless
    as one that reds on nothing, and this sweep's whole output is a triage."""
    name = "L2.4_scale_spread_p90_p10"
    assert bns.measure_null(name, population, replications=5).verdict is (
        bns.NullVerdict.SEPARATED
    )


def test_the_null_is_REPRODUCIBLE_at_a_fixed_seed(population):
    a = bns.measure_null("L2.2_between_home_correlation", population, replications=20, seed=7)
    b = bns.measure_null("L2.2_between_home_correlation", population, replications=20, seed=7)
    assert (a.null_best, a.null_spread, a.verdict) == (b.null_best, b.null_spread, b.verdict)


# ---------------------------------------------------------------------------
# (4) THE LOAD SET — the wrong-population shape, closed
# ---------------------------------------------------------------------------


def test_a_bands_null_is_read_only_on_the_homes_it_JUDGES():
    """L1.1e governs heat pumps and L1.1 governs gas homes, and gas homes are
    spikier. Reading the heat-pump band's null off a gas panel would report a
    defect in a load set the band never touches — the wrong-load-set shape."""
    mixed = _population(
        homes=10,
        heating=tuple(["gas_boiler_combi"] * 8 + ["heat_pump_air", "electric_storage"]),
    )
    gas = bns.measure_null("L1.1_half_hourly_texture", mixed, replications=10)
    pump = bns.measure_null("L1.1e_half_hourly_texture_electric_heat", mixed, replications=10)
    resistive = bns.measure_null(
        "L1.1r_half_hourly_texture_resistive_heat", mixed, replications=10
    )
    assert (gas.homes_judged, pump.homes_judged, resistive.homes_judged) == (8, 1, 1)


def test_a_band_with_NO_home_to_judge_is_unmeasurable_not_clean():
    """The vacuity guard at the band level. A band no home is judged by has an
    unknown null, and 'unknown' must not render as 'separated' — it is reported
    as its own state and counts as a hit needing disposition."""
    gas_only = _population(homes=6)
    m = bns.measure_null("L1.1e_half_hourly_texture_electric_heat", gas_only, replications=5)
    assert m.verdict is bns.NullVerdict.UNMEASURABLE
    assert m.homes_judged == 0
    assert m.is_hit


def test_the_subpopulation_follows_the_LIVE_router(population):
    """Routed through `texture_band_for`, so a change to `HEATING_REGIMES` moves
    the sweep's load sets with it instead of desyncing them."""
    with pytest.MonkeyPatch.context() as mp:
        mp.setitem(fgl.HEATING_REGIMES, "gas_boiler_combi",
                   "L1.1e_half_hourly_texture_electric_heat")
        m = bns.measure_null(
            "L1.1e_half_hourly_texture_electric_heat", population, replications=5
        )
        assert m.homes_judged == len(population.homes)


# ---------------------------------------------------------------------------
# (5) THE SWEEP as a whole
# ---------------------------------------------------------------------------


def test_the_sweep_covers_every_anchored_band(population):
    measured = bns.sweep(population, replications=5)
    assert {m.band for m in measured} == set(bns.anchored_bands())


def test_the_sweep_reads_the_SHIPPED_statistics_not_its_own_copies():
    """The tautology guard. If this module re-implemented a statistic, its null
    would be the null of a function that is not the one doing the judging, and it
    would go green while the real band stayed fail-open."""
    import inspect

    source = inspect.getsource(bns)
    for reader in ("half_hourly_texture", "day_to_day_shape_correlation",
                   "trough_statistics", "smoothing_ratio", "between_home_correlation",
                   "timing_diversity", "scale_spread"):
        assert f"fgl.{reader}(" in source
        assert f"def {reader}(" not in source


def test_a_shrinking_window_GROWS_the_sampling_null(population):
    """The atom's central claim, as a test: a band derived at one window can sit
    inside its own null at another while the number in the table never moves.

    L2.3 is a spread-of-means, so its null falls like 1/sqrt(days) — and on the
    live panel the shipped band sat INSIDE it at 40, 60 and 90 days and cleared
    it at 120 by 3.8% of the null's own spread. A control whose verdict on a
    structureless population depends on how long it watched is not measuring what
    its threshold claims to measure.

    THE FLOOR THIS DEMONSTRATES ON IS GONE — it came out on 2026-08-10 (H34) and
    L2.3 is now reported-not-judged, with `L2.3n_timing_diversity_null_ratio`
    doing the judging. So the band is restored HERE, in the test, exactly as it
    was: deleting the demonstration along with the floor would leave the finding
    resting on a note in a design doc, and the next spread-of-means band that
    wants a constant floor deserves to meet this test rather than a paragraph.
    """
    was = dataclasses.replace(
        fgl.BANDS["L2.3_timing_diversity_periods"],
        threshold=0.5, anchor=fgl.AnchorStatus.DOMAIN_KNOWLEDGE,
    )
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(fgl, "BANDS", {**fgl.BANDS, "L2.3_timing_diversity_periods": was})
        measured = bns.window_sensitivity(
            "L2.3_timing_diversity_periods", population, (40, DAYS), replications=40
        )
    short, long = measured
    assert short.days == 40 and long.days == DAYS
    assert short.null_best > long.null_best
    assert short.is_hit, (
        "the floor that was removed must still read as a hit at the short window — "
        f"if it does not, the finding behind H34 no longer reproduces: {short.note}"
    )


def test_truncating_a_population_keeps_every_home_and_shortens_every_grid(population):
    short = bns.truncated(population, 30)
    assert short.days == 30
    assert short.homes == population.homes
    assert all(len(home) == 30 for home in short.grids)
    assert len(short.weather_driver) == 30
    with pytest.raises(bns.SweepIncomplete):
        bns.truncated(population, DAYS + 1)


def test_to_json_carries_the_window_and_the_exclusions(population):
    payload = bns.to_json(bns.sweep(population, replications=3))
    assert payload["window"]["days"] == DAYS
    assert payload["bands_swept"] == len(bns.anchored_bands())
    assert set(payload["excluded"]) == set(bns.excluded_bands())


# ---------------------------------------------------------------------------
# (7) THE RUN MUST FAIL ON A BAND NOBODY EXERCISES — H35, both ways
# ---------------------------------------------------------------------------
#
# The sweep already reported UNMEASURABLE as its own state and counted it a hit
# (§5 above). What it did NOT do until 2026-08-09 was FAIL on it: the runner's
# exit code named INSIDE_NULL only, so `L1.1r` judging zero homes for six weeks
# produced a clean exit 0 beside a green table. "Reported" and "fires" are not the
# same control, which is this project's own recurring finding (an always-red
# detector is as ignored as a blind one; a tripwire that reds as an opportunity is
# not a tripwire). These two tests are the R15 pair for the promotion of that
# state to fatal.


def test_a_band_that_judges_NO_HOME_is_FATAL_and_not_merely_reported():
    """THE DEFECT DIRECTION. A gas-only population leaves the heat-pump band with
    nothing to judge; the run must fail, not report.

    The mutation is applied to the POPULATION rather than to a verdict object,
    so what is exercised is the same path a real unexercised band takes —
    asserting `fatal([NullMeasurement(verdict=UNMEASURABLE)])` would prove only
    that a list comprehension filters, the tautology shape R15 names first.
    """
    gas_only = _population(homes=6)
    measurement = bns.measure_null(
        "L1.1e_half_hourly_texture_electric_heat", gas_only, replications=5
    )
    assert measurement.verdict is bns.NullVerdict.UNMEASURABLE
    assert bns.fatal([measurement]) == [measurement], (
        "a band whose null cannot be measured must fail the run — an unavailable "
        "check is a FAILED check, not a passing one"
    )


def test_the_SAME_band_stops_being_fatal_once_a_home_EXERCISES_it():
    """THE OTHER DIRECTION, and it is the one that matters for whether the guard
    is a control or a wedge. The same band, the same window, the same call — one
    heat-pump home added to the population and the run is no longer fatal FOR
    THAT REASON.

    A guard that can only ever fire is worth no more than one that never does:
    it would make every future sweep red regardless of what was fixed, and the
    fix this guard exists to demand (put a home of that regime on the panel)
    would be indistinguishable from doing nothing.
    """
    mixed = _population(
        homes=6, heating=("gas_boiler_combi",) * 5 + ("heat_pump_air",)
    )
    measurement = bns.measure_null(
        "L1.1e_half_hourly_texture_electric_heat", mixed, replications=5
    )
    assert measurement.homes_judged == 1
    assert measurement.verdict is not bns.NullVerdict.UNMEASURABLE, (
        "one home of the regime is enough to MEASURE the band's null — whether "
        "the null then clears it is the sweep's own separate question"
    )
    # ...and the guard is genuinely capable of returning nothing, which is the
    # half a control that could only ever fire would be missing. Measured on a
    # band the fixture separates from its own null, through the same `fatal`.
    gas = bns.measure_null("L1.1_half_hourly_texture", mixed, replications=5)
    assert gas.verdict in (bns.NullVerdict.SEPARATED, bns.NullVerdict.SAME_ORDER), gas.note
    assert bns.fatal([gas]) == [], (
        "a band that is measured and not inside its null must leave the run "
        "green — a guard that cannot return empty is not a guard"
    )


def test_SAME_ORDER_stays_a_FINDING_and_does_not_fail_the_run():
    """The line the guard draws is 'is this band's null known', not 'is every
    verdict the best one'. A SAME_ORDER band has a measured null and a real
    disposition; making it fatal too would collapse three states into one and
    take the sweep's own diagnosis away from it."""
    assert bns.NullVerdict.SAME_ORDER not in bns.FATAL_VERDICTS
    assert bns.NullVerdict.SEPARATED not in bns.FATAL_VERDICTS
    assert set(bns.FATAL_VERDICTS) == {
        bns.NullVerdict.INSIDE_NULL,
        bns.NullVerdict.UNMEASURABLE,
    }


def test_the_RUNNERS_EXIT_CODE_is_the_one_the_module_declares():
    """R11 no-orphan: the promotion is worthless if the runner keeps its own copy
    of the rule. The runner is imported and its `main` driven against a stub
    population, so what is proven is the EXIT CODE, not that a constant exists.
    """
    import importlib
    import sys

    runner = importlib.import_module("tools.band_null_sweep")
    gas_only = _population(homes=6)
    mixed = _population(
        homes=6,
        heating=("gas_boiler_combi",) * 4 + ("heat_pump_air", "electric_direct"),
    )
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(sys, "argv", ["band_null_sweep.py", "--replications", "3"])
        mp.setattr(runner, "live_population", lambda: gas_only)
        assert runner.main() == 1, (
            "a population that exercises neither electric band must exit non-zero"
        )
        mp.setattr(runner, "live_population", lambda: mixed)
        exercised = runner.main()
    # The second population exercises every texture band; it may still exit 1 for
    # a band that is genuinely inside its null on a synthetic fixture, so what is
    # asserted is that the UNMEASURABLE reason is gone — not a bare 0, which would
    # make this test a hostage to the fixture's own realism.
    fatal_bands = {
        m.band
        for m in bns.fatal(bns.sweep(mixed, replications=3))
        if m.verdict is bns.NullVerdict.UNMEASURABLE
    }
    assert not fatal_bands, fatal_bands
    assert exercised in (0, 1)
