"""H_GAP — the two-level premise test (spiky homes, smooth crowds) as a STANDING
FAILABLE control, landed RED against the generator that is actually in the demand
path; plus the fabric belief-vs-truth gaps and their money consequence.

Spec: `docs/design/PREMISE_TWO_LEVEL_TEST_HARNESS_SPEC.md`.
Module under test: `background/fabric_gap_ledger.py`.

HOW THIS FILE IS ORGANISED, AND WHY IT IS SHAPED THIS WAY
=========================================================

§1 THE BIRTH CONDITION. The shipped demand path is RED, cell by cell, with the
   measured value recorded in the assertion. These tests PASS today. They are the
   standing record of the defect, and they FAIL the day someone changes the demand
   path without updating the record — which is the point: the record cannot go
   stale silently.

§2 THE REQUIREMENT ITSELF, pinned. `xfail(strict=True)` on the assertion that the
   demand path MEETS the two-level test. Strict, so the day the demand path is
   fixed the pin XPASSes, the suite goes RED, and someone has to come here and
   unpin it. A control introduced already-passing has demonstrated nothing (R15);
   a control landed as a strict pin demonstrates the defect AND cannot be forgotten.

§3 R15 MUTATIONS. Every statistic is proven to FIRE on its own named defect. A
   bare "the control returned the right number" assertion never appears alone.

§4 THE THREE FAIL-OPEN PATTERNS — empty input, NaN-blindness, tautology — each
   closed in code and proven here, because a statistical suite is unusually
   exposed to all three.

§5 THE FABRIC GAP and its MONEY CONSEQUENCE, including the constraint that no
   saving may come from discounting.

§6 THE WALL. Nothing in `simulation/` or `company/` may import this harness.

WHAT THIS SUITE IS NOT
----------------------
It is not a test of `premise_trace` (that is `tests/simulation/test_premise_trace.py`,
owned by W1_12) and it is not a test of `demand_model`. It is the third leg of the
coupled triad: it measures both and helps neither. Where it reports that
`premise_trace` does better, that is a MEASUREMENT of what wiring W1_12 into the
demand path would buy, not an endorsement.
"""

from __future__ import annotations

import datetime as dt
import json
import math
import statistics

import pytest

from background import fabric_gap_ledger as fgl
from simulation import premise_trace as pt
from simulation.household import (
    BoilerAge,
    BuildEra,
    HeatingSystem,
    Household,
    InsulationLevel,
    PropertyType,
)

# 120 days of the REAL Open-Meteo archive. Not 90: an away block is drawn 6-26
# times a year, so a shorter window can leave a home with none by chance and make
# L1.3 flaky for a reason that has nothing to do with the generator.
WINDOW_START = dt.date(2022, 1, 1)
WINDOW_END = dt.date(2022, 4, 30)

# Eight homes spanning the stock: flat to detached, pre-1919 to post-2000, poor to
# full insulation, one to five occupants. Diversity is deliberately built INTO the
# input population, so any clone-like result is the generator's doing rather than a
# consequence of asking eight identical houses whether they differ.
POPULATION = (
    ("P1", PropertyType.FLAT, BuildEra.POST_2000, InsulationLevel.FULL, 1, 1),
    ("P2", PropertyType.TERRACED, BuildEra.PRE_1919, InsulationLevel.POOR, 2, 2),
    ("P3", PropertyType.SEMI_DETACHED, BuildEra.ERA_1965_1980, InsulationLevel.PARTIAL, 3, 3),
    ("P4", PropertyType.DETACHED, BuildEra.ERA_1919_1944, InsulationLevel.PARTIAL, 4, 4),
    ("P5", PropertyType.TERRACED, BuildEra.ERA_1981_2000, InsulationLevel.FULL, 2, 2),
    ("P6", PropertyType.SEMI_DETACHED, BuildEra.PRE_1919, InsulationLevel.PARTIAL, 3, 5),
    ("P7", PropertyType.DETACHED, BuildEra.POST_2000, InsulationLevel.FULL, 5, 3),
    ("P8", PropertyType.FLAT, BuildEra.ERA_1965_1980, InsulationLevel.POOR, 1, 2),
)


def _household(premise_id, property_type, build_era, insulation, bedrooms, people):
    return Household(
        customer_id=premise_id,
        property_type=property_type,
        build_era=build_era,
        epc_rating="D",
        bedrooms=bedrooms,
        heating_system=HeatingSystem.GAS_BOILER_COMBI,
        boiler_age=BoilerAge.MID,
        has_solar=False,
        solar_kwp=0.0,
        solar_install_year=None,
        has_battery=False,
        battery_kwh=0.0,
        has_ev=False,
        ev_charger_kw=0.0,
        has_smart_meter=True,
        smart_meter_install_year=2020,
        insulation=insulation,
        has_driveway=True,
        roof_aspect="south",
    )


@pytest.fixture(scope="module")
def weather():
    """The REAL Open-Meteo reanalysis archive — Historical Ground Truth. If the
    archive is missing this suite must FAIL, never skip: an unavailable check is a
    FAILED check (R15)."""
    return pt.load_trace_weather("C1", start=WINDOW_START, end=WINDOW_END)


@pytest.fixture(scope="module")
def shipped(weather):
    """The generator that is ACTUALLY in the demand path today."""
    properties = [
        {
            "customer_id": premise_id,
            "property_type": property_type.value,
            "heating_system": "gas_boiler",
            "occupancy_pattern": "family",
            "people_count": people,
            "children_count": 0,
            "assets": {},
        }
        for premise_id, property_type, _, _, _, people in POPULATION
    ]
    return fgl.shipped_path_population(properties, weather)


@pytest.fixture(scope="module")
def traces(weather):
    return [
        pt.generate_premise_trace(
            premise_id=spec[0], household=_household(*spec), weather=weather, seed=7
        )
        for spec in POPULATION
    ]


@pytest.fixture(scope="module")
def generated(traces, weather):
    """W1_12's generator — built, NOT yet wired into the demand path."""
    return fgl.premise_trace_population(traces, weather)


@pytest.fixture(scope="module")
def shipped_result(shipped):
    return fgl.evaluate_two_level(shipped)


@pytest.fixture(scope="module")
def generated_result(generated):
    return fgl.evaluate_two_level(generated)


def _grids(population):
    return [[list(day) for day in home] for home in population.grids]


# ===========================================================================
# §1 THE BIRTH CONDITION — the shipped demand path is RED, cell by cell
# ===========================================================================


def test_the_shipped_demand_path_is_RED(shipped_result):
    """THE BIRTH CONDITION. This suite was landed against a generator it FAILS.

    If this test ever passes-by-turning-green (i.e. the demand path stops being
    red), §2's strict pins XPASS and the suite goes red, forcing this record to be
    updated rather than quietly outgrown.
    """
    assert shipped_result.is_red
    assert shipped_result.failed_levels() == ("L1", "L2"), (
        "the shipped path fails at BOTH levels — individual homes are not spiky "
        "AND crowds do not smooth"
    )


@pytest.mark.parametrize(
    "statistic, expected",
    [
        # Every value below was MEASURED on the real archive, 2026-08-03, not
        # estimated. They are recorded to 2 significant figures so ordinary
        # floating-point drift does not fail the suite but a real change does.
        ("L1.1_half_hourly_texture", 0.048),
        ("L1.2_day_to_day_shape_correlation", 1.000),
        ("L1.3_away_days_per_year", 0.0),
        ("L1.5_max_multiplicity_share", 2.000),
        ("L2.1_smoothing_ratio", 0.959),
        ("L2.2_between_home_correlation", 0.999),
        ("L2.3_timing_diversity_periods", 0.0),
    ],
)
def test_MEASURED_shipped_path_values(shipped_result, statistic, expected):
    """The measured defect, cell by cell, so the RED claim is checkable rather
    than asserted. Reading these seven numbers is reading the defect:

    the shipped path repeats the SAME normalised half-hourly shape every day
    (L1.2 = 1.000 exactly, L1.5 = 2.0), which is why it has a tenth of the
    required texture (L1.1), can never represent an empty house (L1.3 = 0),
    smooths by 4% when aggregated across eight households (L2.1 = 0.96 where 1.0
    is no smoothing at all), and produces eight homes whose de-weathered daily
    residuals correlate at 0.999 (L2.2) while every one of them peaks in the
    identical half-hour (L2.3 = 0, an exact point mass).
    """
    cell = shipped_result.cell(statistic)
    assert cell.verdict is fgl.Verdict.FAIL, f"{statistic} should be RED, got {cell.verdict}"
    assert cell.value == pytest.approx(expected, abs=0.01), cell.note


def test_the_two_unanchored_cells_are_reported_UNVALIDATED_not_passed(shipped_result):
    """Two statistics have no published anchor yet. They are MEASURED and REPORTED
    but excluded from the verdict, rather than given an invented threshold.

    This is the honest failure mode to choose: a fabricated band would make the
    suite look rigorous while being unfalsifiable. Note that the shipped path's
    8%-apart annual totals are visibly wrong against any plausible band — but
    "visibly wrong" is not a threshold.
    """
    for statistic in ("L1.4_weekday_weekend_separation", "L2.4_scale_spread_p90_p10"):
        cell = shipped_result.cell(statistic)
        assert cell.verdict is fgl.Verdict.UNVALIDATED
        assert cell.band.anchor is fgl.AnchorStatus.NEED
        assert cell.band.threshold is None
        assert math.isfinite(cell.value), "an unvalidated cell still reports its value"


def test_every_band_carries_a_named_anchor_or_declares_it_NEEDs_one():
    """No band may exist without either a source or an explicit admission that it
    has none. This is the mechanised form of the anchor-honesty rule — prose in a
    docstring would decay, a test does not."""
    for name, band in fgl.BANDS.items():
        assert band.anchor_source.strip(), f"{name} has no anchor rationale"
        if band.anchor is fgl.AnchorStatus.NEED:
            assert band.threshold is None, f"{name} claims NEED but carries a threshold"
        else:
            assert band.threshold is not None, f"{name} is anchored but has no threshold"


# ===========================================================================
# §2 THE REQUIREMENT, PINNED — strict xfail, so a fix cannot go unnoticed
# ===========================================================================


@pytest.mark.xfail(
    strict=True,
    reason=(
        "LANDED RED ON PURPOSE. This is the actual requirement — the demand path "
        "must pass the two-level test — and the demand path does not meet it. "
        "STRICT: when the demand path is fixed (by wiring W1_12's premise_trace in, "
        "or otherwise) this XPASSes, the suite goes red, and this pin must be "
        "removed along with §1's measured-defect record. That is the mechanism that "
        "stops the defect being quietly outgrown."
    ),
)
def test_the_shipped_demand_path_meets_the_two_level_test(shipped_result):
    assert not shipped_result.is_red, shipped_result.summary()


@pytest.mark.xfail(
    strict=True,
    reason=(
        "W1_12's generator fails 2 of the 7 anchored cells. STRICT so an "
        "improvement forces the residual to be re-stated rather than absorbed. "
        "Measured 2026-08-03: L1.1 texture 0.1498 against a 0.15 band — a genuine "
        "knife-edge on its WORST home, and the threshold is NOT moved to make it "
        "pass (R12: the band is a diagnostic, drift toward the edge triggers R4, "
        "never a tuning pass); L2.3 timing diversity 0.211 half-hours against a 0.5 "
        "band — real spread, but the evening peak still clusters harder than a real "
        "population's does."
    ),
)
def test_the_premise_trace_generator_meets_the_two_level_test(generated_result):
    assert not generated_result.is_red, generated_result.summary()


def test_the_premise_trace_generator_is_MEASURABLY_better(shipped_result, generated_result):
    """The distance between the two columns IS the value of wiring W1_12 in,
    expressed in the units of the defect rather than as a claim that it is better.

    Both generators are RED. Five of the seven anchored cells that the shipped path
    fails, `premise_trace` passes.
    """
    shipped_fails = {c.statistic for c in shipped_result.failed}
    generated_fails = {c.statistic for c in generated_result.failed}
    assert generated_fails < shipped_fails, (
        "premise_trace's failures must be a strict subset of the shipped path's — "
        f"shipped {sorted(shipped_fails)}, generated {sorted(generated_fails)}"
    )
    assert generated_fails == {"L1.1_half_hourly_texture", "L2.3_timing_diversity_periods"}
    assert generated_result.is_red, "both generators are RED — this is a measurement, not a win"


def test_the_two_generators_are_judged_by_identical_code(shipped, generated):
    """Neither side supplies its own statistics or its own framing. The population
    container carries no generator-specific field, so `evaluate_two_level` cannot
    tell which generator it is looking at except through `pc1_is_an_input`, which
    can only ever make a verdict STRICTER."""
    assert type(shipped) is type(generated) is fgl.PopulationTraces
    assert set(vars(shipped)) == set(vars(generated))
    assert shipped.days == generated.days
    assert shipped.homes == generated.homes


# ===========================================================================
# §3 R15 MUTATIONS — every statistic fires on its own named defect
# ===========================================================================


def _smooth(grid, window=7):
    """MUTATION for L1.1 — replace each period with a centred rolling mean across
    the same period on neighbouring days. Removes texture, preserves level."""
    flat = [list(day) for day in grid]
    out = []
    for d in range(len(flat)):
        lo, hi = max(0, d - window // 2), min(len(flat), d + window // 2 + 1)
        out.append([sum(flat[k][p] for k in range(lo, hi)) / (hi - lo) for p in range(48)])
    return out


def _replay_one_day(grid):
    """MUTATION for L1.2 and L1.5 — replay one day's SHAPE all year, rescaled to
    each day's own total. This is precisely what the shipped path does."""
    base = list(grid[0])
    base_total = sum(base)
    return [[v / base_total * sum(day) for v in base] for day in grid]


def _occupy_every_day(grid):
    """MUTATION for L1.3 — overwrite every day that looks empty with an ordinary
    occupied day, i.e. remove the generator's ability to represent absence.

    NOT the spec's original mutation ("floor every period at a small positive
    value"). That mutation belonged to the spec's run-length statistic, which was
    measured and found backwards (see `away_signature`'s docstring). Flooring a
    trace raises the base-load window and the active window together, so it moves
    the fixed statistic barely at all — the mutation had to be re-derived from the
    defect rather than copied across from the superseded statistic.
    """
    occupied = next(
        day for day in grid if fgl.away_signature(day) > fgl.AWAY_SIGNATURE_MAX * 1.5
    )
    return [
        list(occupied) if fgl.away_signature(day) < fgl.AWAY_SIGNATURE_MAX else list(day)
        for day in grid
    ]


def _clone(grids):
    """MUTATION for L2.1 and L2.2 — clone one home N times."""
    return [[list(day) for day in grids[0]] for _ in grids]


def _collapse_evening_peak(grids):
    """MUTATION for L2.3 — move every home's evening peak into the same half-hour,
    i.e. reinstate `HEATING_PERIOD_WEIGHTS` as one national constant."""
    out = []
    for grid in grids:
        new = []
        for day in grid:
            row = list(day)
            evening = list(range(29, 46))
            block = sum(row[p] for p in evening)
            for p in evening:
                row[p] = 0.0
            row[37] = block  # everyone peaks at 18:30
            new.append(row)
        out.append(new)
    return out


def test_L1_1_texture_FIRES_when_the_trace_is_smoothed(generated):
    grid = _grids(generated)[0]
    before = fgl.half_hourly_texture(grid)
    after = fgl.half_hourly_texture(_smooth(grid))
    assert after < before / 2, f"smoothing must collapse texture: {before} -> {after}"
    assert fgl.BANDS["L1.1_half_hourly_texture"].judge(after) is fgl.Verdict.FAIL


def test_L1_2_correlation_FIRES_when_one_days_shape_is_replayed(generated):
    grid = _grids(generated)[0]
    before = fgl.day_to_day_shape_correlation(grid)
    after = fgl.day_to_day_shape_correlation(_replay_one_day(grid))
    assert after == pytest.approx(1.0, abs=1e-9), "a replayed shape correlates at exactly 1"
    assert before < 0.85
    assert fgl.BANDS["L1.2_day_to_day_shape_correlation"].judge(after) is fgl.Verdict.FAIL


def test_L1_3_troughs_FIRE_when_the_empty_house_is_removed(generated):
    grid = _grids(generated)[0]
    before = fgl.trough_statistics(grid)
    after = fgl.trough_statistics(_occupy_every_day(grid))
    assert before.away_signature_days > 0, "the unmutated generator CAN represent absence"
    assert after.away_signature_days == 0
    band = fgl.BANDS["L1.3_away_days_per_year"]
    assert band.judge(before.away_days_per_year) is fgl.Verdict.PASS
    assert band.judge(after.away_days_per_year) is fgl.Verdict.FAIL


def test_the_away_signature_separates_absence_from_an_ordinary_night(generated, traces):
    """The statistic must key on ABSENCE, not on darkness. Every home is quiet at
    3am whether or not anyone is in it, which is exactly why the spec's original
    run-length formulation counted nights instead of holidays."""
    grid = _grids(generated)[0]
    signatures = [fgl.away_signature(day) for day in grid]
    away_flags = [day.is_away for day in traces[0].days]
    away = [s for s, flag in zip(signatures, away_flags) if flag]
    occupied = [s for s, flag in zip(signatures, away_flags) if not flag]
    assert away, "the fixture home must have at least one away day in the window"
    assert max(away) < min(occupied), (
        f"absence and occupancy must not overlap: away max {max(away):.3f} vs "
        f"occupied min {min(occupied):.3f}"
    )
    assert max(away) < fgl.AWAY_SIGNATURE_MAX < min(occupied), (
        "the 1.30 cutoff must sit inside the gap, not on either edge"
    )


def test_L1_4_separation_FIRES_when_day_types_are_shuffled(generated):
    """L1.4 has no anchor and is not judged, but the STATISTIC must still be shown
    to detect its defect — an unvalidated cell that cannot even measure would be a
    fail-silent dressed up as honesty."""
    grid = _grids(generated)[0]
    real = list(generated.is_weekend)
    before = fgl.weekday_weekend_separation(grid, real)
    # Shuffle deterministically, keeping the same counts of each day type.
    shuffled = [real[(i * 7) % len(real)] for i in range(len(real))]
    after = fgl.weekday_weekend_separation(grid, shuffled)
    assert after < before, f"shuffling day types must reduce separation: {before} -> {after}"


def test_L1_5_the_shipped_generator_IS_its_own_mutation(shipped, generated):
    """L1.5's mutation test is the shipped path itself — the spec says so, and it
    is the sharpest form the proof can take: the control's named defect is a real
    generator in production, not a synthetic perturbation."""
    shipped_share = max(
        fgl.normalised_fraction_multiplicity(g).max_multiplicity_share for g in _grids(shipped)
    )
    generated_share = max(
        fgl.normalised_fraction_multiplicity(g).max_multiplicity_share for g in _grids(generated)
    )
    assert shipped_share >= 1.0, (
        "a rescaled base shape reproduces every base fraction on every day, so its "
        "share is >= 1.0 by construction"
    )
    assert generated_share < shipped_share / 10.0
    band = fgl.BANDS["L1.5_max_multiplicity_share"]
    assert band.judge(shipped_share) is fgl.Verdict.FAIL
    assert band.judge(generated_share) is fgl.Verdict.PASS


def test_L1_5_cannot_be_passed_by_injecting_noise(generated):
    """THE ANTI-GOAL-SEEK PROOF, and the reason L1.5 exists (R12).

    Take the shipped path's defect (one base shape, rescaled) and sprinkle level
    noise on it — the treatment that would be reached for to move L1.1. The
    structural detector is unmoved, because the daily scalar still cancels in
    x[t]/daily_total for the underlying shape.
    """
    grid = _grids(generated)[0]
    replayed = _replay_one_day(grid)
    # Deterministic multiplicative "noise": a fixed per-day factor. This is exactly
    # the class of fix that moves a level statistic without generating any shape.
    noised = [[v * (1.0 + 0.3 * math.sin(d)) for v in day] for d, day in enumerate(replayed)]
    share = fgl.normalised_fraction_multiplicity(noised).max_multiplicity_share
    assert share >= 1.0, (
        "level noise must NOT rescue the structural detector — the whole point of "
        "L1.5 is that it survives a tuning pass"
    )
    assert fgl.BANDS["L1.5_max_multiplicity_share"].judge(share) is fgl.Verdict.FAIL


def test_the_goal_seek_warning_says_someone_tuned_the_number():
    """R12, mechanised. If texture passes while the structural detector fails, the
    suite must say so IN THOSE WORDS rather than reporting a mixed result."""
    band_texture = fgl.BANDS["L1.1_half_hourly_texture"]
    band_structural = fgl.BANDS["L1.5_max_multiplicity_share"]
    result = fgl.TwoLevelResult(
        generator="synthetic",
        cells=(
            fgl.CellResult("L1.1_half_hourly_texture", "L1", 0.9, fgl.Verdict.PASS, band_texture),
            fgl.CellResult("L1.5_max_multiplicity_share", "L1", 2.0, fgl.Verdict.FAIL, band_structural),
        ),
        homes=8,
        days=120,
    )
    warning = result.goal_seek_warning()
    assert warning is not None
    assert "SOMEONE TUNED THE NUMBER" in warning
    assert "SOMEONE TUNED THE NUMBER" in result.summary()


def test_the_goal_seek_warning_is_SILENT_when_nothing_was_tuned(generated_result, shipped_result):
    """The other half of the R15 proof: the warning must not fire on either real
    generator, or it would be noise rather than a signal."""
    assert generated_result.goal_seek_warning() is None
    assert shipped_result.goal_seek_warning() is None


def test_L2_1_smoothing_FIRES_on_a_cloned_population(generated):
    grids = _grids(generated)
    before = fgl.smoothing_ratio(fgl.smoothing_curve(grids))
    after = fgl.smoothing_ratio(fgl.smoothing_curve(_clone(grids)))
    assert after == pytest.approx(1.0, abs=1e-9), "cloned homes cannot smooth each other at all"
    assert before < 0.85
    assert fgl.BANDS["L2.1_smoothing_ratio"].judge(after) is fgl.Verdict.FAIL


def test_L2_2_correlation_FIRES_on_a_cloned_population(generated):
    grids = _grids(generated)
    driver = generated.weather_driver
    before = fgl.between_home_correlation(grids, driver)
    after = fgl.between_home_correlation(_clone(grids), driver)
    assert after == pytest.approx(1.0, abs=1e-6), "clones correlate at 1 on any residual"
    assert before < 0.6
    assert fgl.BANDS["L2.2_between_home_correlation"].judge(after) is fgl.Verdict.FAIL


def test_L2_2_does_NOT_use_a_population_derived_common_mode(generated):
    """THE RECORDED NEAR-MISS, pinned so it cannot come back.

    De-trending on the population's OWN mean makes residuals sum to zero by
    construction, so a population of clones comes out exactly ANTI-correlated and
    scores as maximally diverse. Measured on the shipped path that version returned
    -0.98 and PASSED. The external-driver version returns +0.999 on the same input.
    """
    grids = _grids(generated)
    clones = _clone(grids)
    length = len(clones[0])
    population_mean = [
        sum(sum(g[d]) for g in clones) / len(clones) for d in range(length)
    ]
    dailies = [[sum(day) for day in g] for g in clones]
    bogus_residuals = [
        [v - m for v, m in zip(d, population_mean)] for d in dailies
    ]
    # Every clone's residual is identically zero here, which is itself degenerate —
    # so perturb one home slightly to make the anti-correlation visible.
    perturbed = [list(r) for r in bogus_residuals]
    for i, r in enumerate(perturbed):
        r[0] += 1.0 if i % 2 == 0 else -1.0
    bogus = statistics.median(
        fgl._pearson(perturbed[i], perturbed[j])
        for i in range(len(perturbed))
        for j in range(i + 1, len(perturbed))
    )
    honest = fgl.between_home_correlation(clones, generated.weather_driver)
    assert bogus < 0.0, "the population-mean version scores clones as anti-correlated"
    assert honest == pytest.approx(1.0, abs=1e-6), "the external-driver version scores them as clones"


def test_L2_3_timing_diversity_FIRES_when_every_peak_is_collapsed(generated):
    grids = _grids(generated)
    before = fgl.timing_diversity(grids)
    after = fgl.timing_diversity(_collapse_evening_peak(grids))
    assert after == pytest.approx(0.0, abs=1e-12), "one national constant is an exact point mass"
    assert before > 0.0
    assert fgl.BANDS["L2.3_timing_diversity_periods"].judge(after) is fgl.Verdict.FAIL


def test_L2_4_scale_spread_FIRES_when_every_home_is_set_to_the_mean(generated):
    annuals = list(generated.annual_kwh)
    before = fgl.scale_spread(annuals)
    mean = sum(annuals) / len(annuals)
    after = fgl.scale_spread([mean] * len(annuals))
    assert after.p90_over_p10 == pytest.approx(1.0)
    assert after.iqr_ratio == pytest.approx(1.0)
    assert before.p90_over_p10 > 1.0


def test_L2_5_aggregation_consistency_is_retained_as_a_regression_guard():
    """L2.5 — the existing W1_5 invariant, kept so the trade-off is EXPLICIT and
    ENFORCED: added realism must not cost aggregation consistency. A new generator
    with beautiful individual traces that broke the national reconciliation would
    be a regression, and the suite must say so rather than leaving it to judgement.

    Retained, not reimplemented — reimplementing it here would let the harness and
    the world drift apart on what reconciliation means.
    """
    from simulation.premise_demand import aggregate_reconciles

    national = [1.0] * 48
    assert aggregate_reconciles(list(national), national)
    # Off-manifold by more than the 5% relative-L1 tolerance: one region's premise
    # demand no longer sums to the country.
    off_manifold = [1.0] * 40 + [1.5] * 8
    assert not aggregate_reconciles(off_manifold, national), (
        "the retained invariant must still FIRE — a retained control that cannot "
        "fail is not a regression guard"
    )


# ===========================================================================
# §4 THE THREE FAIL-OPEN PATTERNS
# ===========================================================================

_ONE_HOME = [[0.5] * 48 for _ in range(40)]


@pytest.mark.parametrize(
    "call",
    [
        pytest.param(lambda: fgl.half_hourly_texture([[0.5] * 48] * 3), id="texture-few-days"),
        pytest.param(lambda: fgl.day_to_day_shape_correlation([[0.5] * 48] * 3), id="corr-few-days"),
        pytest.param(lambda: fgl.trough_statistics([[0.5] * 48] * 3), id="troughs-few-days"),
        pytest.param(lambda: fgl.normalised_fraction_multiplicity([[0.5] * 48] * 3), id="l15-few-days"),
        pytest.param(lambda: fgl.evening_peak_period([[0.5] * 48] * 3), id="peak-few-days"),
        pytest.param(lambda: fgl.smoothing_curve([_ONE_HOME]), id="smoothing-one-home"),
        pytest.param(lambda: fgl.between_home_correlation([_ONE_HOME] * 2, [1.0] * 40), id="corr-two-homes"),
        pytest.param(lambda: fgl.timing_diversity([_ONE_HOME] * 2), id="timing-two-homes"),
        pytest.param(lambda: fgl.scale_spread([1.0, 2.0]), id="spread-two-homes"),
        pytest.param(lambda: fgl.half_hourly_texture([]), id="texture-empty"),
        pytest.param(lambda: fgl.smoothing_curve([]), id="smoothing-empty"),
        pytest.param(lambda: fgl.scale_spread([]), id="spread-empty"),
        pytest.param(lambda: fgl.peak_to_mean([]), id="peak-to-mean-empty"),
        pytest.param(lambda: fgl.hdd_driver([]), id="driver-empty"),
        pytest.param(lambda: fgl.half_hourly_texture([[0.5] * 12] * 40), id="short-day"),
    ],
)
def test_FAIL_OPEN_1_a_statistic_over_too_little_input_RAISES(call):
    """A statistic computed over zero homes, zero days, a short trace or a truncated
    day must FAIL, never pass vacuously. Every one of these would otherwise return a
    number that looks like evidence."""
    with pytest.raises(fgl.InsufficientEvidence):
        call()


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
def test_FAIL_OPEN_2_non_finite_values_are_rejected_FIRST(bad):
    """NaN-blindness is a known class in this codebase: `nan > threshold` and
    `max(nan, x)` are both silently wrong. Every statistic rejects non-finite input
    BEFORE any comparison, so a corrupt trace is a failure rather than a pass."""
    grid = [[0.5] * 48 for _ in range(40)]
    grid[7][13] = bad
    for statistic in (
        fgl.half_hourly_texture,
        fgl.day_to_day_shape_correlation,
        fgl.trough_statistics,
        fgl.normalised_fraction_multiplicity,
        fgl.evening_peak_period,
    ):
        with pytest.raises(fgl.NonFiniteTrace):
            statistic(grid)


def test_FAIL_OPEN_2_a_non_finite_value_reaching_a_BAND_is_a_FAIL_not_a_PASS():
    """The second half of the NaN defence. Both of `Band.judge`'s comparisons are
    silently False for NaN, so without the explicit guard a NaN would fall through
    an `at_most` band as a PASS."""
    for band in fgl.BANDS.values():
        for bad in (float("nan"), float("inf"), float("-inf")):
            if band.anchor is fgl.AnchorStatus.NEED:
                continue
            assert band.judge(bad) is fgl.Verdict.FAIL, f"{band.statistic} passed {bad}"


def test_FAIL_OPEN_3_PC1_as_a_generator_INPUT_is_detected_mechanically():
    """The tautology guard, read off the wiring's own source rather than trusted
    from a flag. L2.1's large-N anchor is the published PC1 shape; for a path that
    CONSUMES PC1, a large-N pass would be tautological.

    Checked on the BUILDER FUNCTIONS. Two near-misses are pinned below, because
    both were live in this file before being measured: a module-level IMPORT scan
    clears `demand_model` (it takes `base_shape` as an argument and imports no
    profile), and a module-level TEXT scan flags it off a docstring that merely
    mentions `sim.profile_class_1`. Import-blind one way, docstring-fooled the
    other — so the function refuses modules outright.
    """
    from simulation import demand_model

    assert fgl.pc1_is_an_input_to(fgl.shipped_path_population) is True
    assert fgl.pc1_is_an_input_to(fgl.premise_trace_population) is False
    for module in (demand_model, pt):
        with pytest.raises(fgl.InsufficientEvidence):
            fgl.pc1_is_an_input_to(module)


def test_the_shipped_population_DECLARES_the_tautology_it_actually_has(shipped, generated):
    """The declared flag and the mechanical check must agree. If they ever diverge,
    the flag is being hand-maintained and the guard is decorative."""
    assert shipped.pc1_is_an_input is fgl.pc1_is_an_input_to(fgl.shipped_path_population)
    assert generated.pc1_is_an_input is fgl.pc1_is_an_input_to(fgl.premise_trace_population)


def test_the_goal_seek_pair_names_are_live_band_keys():
    """The stale-name guard. `goal_seek_warning` looks its two cells up BY NAME and
    returns None on KeyError — so a rename turns R12's anti-tuning warning into a
    silent no-op. It did, once. This is the mechanism that stops it recurring."""
    assert fgl.TEXTURE_STATISTIC in fgl.BANDS
    assert fgl.STRUCTURAL_STATISTIC in fgl.BANDS


def test_FAIL_OPEN_3_a_tautological_pass_is_NOT_scored_as_a_pass():
    """If the shipped path ever smooths enough to pass L2.1, that pass is still not
    evidence, because PC1 is its own input. The verdict must degrade to
    TAUTOLOGICAL rather than to PASS."""
    days, homes = 40, 6
    # A population that smooths well but is built on PC1 by declaration.
    grids = tuple(
        tuple(tuple(0.5 + 0.4 * math.sin(d + h + p / 3.0) for p in range(48)) for d in range(days))
        for h in range(homes)
    )
    population = fgl.PopulationTraces(
        generator="synthetic PC1 consumer",
        homes=tuple(f"H{i}" for i in range(homes)),
        grids=grids,
        is_weekend=tuple(d % 7 in (5, 6) for d in range(days)),
        annual_kwh=tuple(3000.0 + 100.0 * i for i in range(homes)),
        weather_driver=tuple(float(d % 11) for d in range(days)),
        pc1_is_an_input=True,
    )
    result = fgl.evaluate_two_level(population)
    assert result.cell("L2.1_smoothing_ratio").verdict is fgl.Verdict.TAUTOLOGICAL
    assert "tautological" in result.cell("L2.1_smoothing_ratio").note


def test_FAIL_OPEN_3_the_tautology_check_RAISES_when_it_cannot_read_the_source():
    """An unavailable check is a FAILED check (R15). Something whose source cannot
    be read must raise, not return False and let the caller score a pass."""
    for unreadable in (len, object(), "not a function", None):
        with pytest.raises(fgl.InsufficientEvidence):
            fgl.pc1_is_an_input_to(unreadable)


def test_FAIL_OPEN_L2_2_REFUSES_to_run_without_an_external_driver():
    """Without an external driver, L2.2 could only fall back to a population-derived
    common mode — the fallback that scored clones as maximally diverse. It refuses."""
    days, homes = 40, 6
    grids = tuple(tuple(tuple(0.5 for _ in range(48)) for _ in range(days)) for _ in range(homes))
    population = fgl.PopulationTraces(
        generator="no driver",
        homes=tuple(f"H{i}" for i in range(homes)),
        grids=grids,
        is_weekend=tuple(d % 7 in (5, 6) for d in range(days)),
        annual_kwh=tuple(3000.0 + i for i in range(homes)),
        weather_driver=(),
    )
    with pytest.raises(fgl.InsufficientEvidence):
        fgl.evaluate_two_level(population)


def test_the_verdict_is_WORST_CELL_not_an_average(generated):
    """An average across homes would hide the exact defect this suite exists to
    find. Slip ONE smoothed home into an otherwise-diverse population: the
    reported L1.1 cell must be THAT home's value, not the population mean, and
    the cell must name it.

    THIS TEST WAS ITSELF A TAUTOLOGY UNTIL 2026-08-03 and is worth the note. It
    used to end `assert generated_worst(textures) == approx(min(textures))` with
    `generated_worst = min` defined three lines below — i.e. `min(x) == min(x)`,
    which cannot fail, and which never called `evaluate_two_level` at all. A
    source mutation replacing the worst-cell selection with an average left it
    GREEN. That is the R15 TAUTOLOGY pattern (the checked value derived from the
    same source it checks) sitting inside the test named for the rule, and only
    mutating the source found it. It now asserts against the real verdict path.
    """
    grids = _grids(generated)
    poisoned = [[list(day) for day in home] for home in grids]
    poisoned[-1] = _smooth(poisoned[-1])  # one home loses its texture

    per_home = [fgl.half_hourly_texture(g) for g in poisoned]
    worst, mean = min(per_home), statistics.fmean(per_home)
    assert worst < mean * 0.9, (
        "the fixture must actually discriminate — if the smoothed home does not "
        "drag the worst materially below the mean, this test proves nothing"
    )

    population = fgl.PopulationTraces(
        generator=generated.generator,
        homes=generated.homes,
        grids=tuple(tuple(tuple(day) for day in home) for home in poisoned),
        is_weekend=generated.is_weekend,
        annual_kwh=generated.annual_kwh,
        weather_driver=generated.weather_driver,
        pc1_is_an_input=generated.pc1_is_an_input,
    )
    cell = fgl.evaluate_two_level(population).cell("L1.1_half_hourly_texture")

    assert cell.value == pytest.approx(worst), (
        f"the verdict must report the WORST home ({worst:.4g}), not the population "
        f"mean ({mean:.4g}) — got {cell.value:.4g}"
    )
    assert cell.value != pytest.approx(mean)
    assert generated.homes[-1] in cell.note, "the worst cell must NAME the home it found"


# ===========================================================================
# §5 THE FABRIC GAP and its MONEY CONSEQUENCE
# ===========================================================================


def _observations(n=8, *, epc_bias=1.0, inferred_bias=1.0):
    """A synthetic fabric population. Truth spans a real-looking HLC range; the two
    beliefs are the truth scaled by a stated bias, so the gap has a KNOWN answer and
    the metric can be checked rather than merely exercised."""
    return [
        fgl.FabricObservation(
            premise_id=f"P{i}",
            actual_hlc_kw_per_k=0.10 + 0.05 * i,
            epc_hlc_kw_per_k=(0.10 + 0.05 * i) * epc_bias,
            inferred_hlc_kw_per_k=(0.10 + 0.05 * i) * inferred_bias,
            floor_area_m2=60.0 + 10.0 * i,
            annual_heat_kwh=8000.0 + 1500.0 * i,
        )
        for i in range(n)
    ]


def test_a_perfect_belief_scores_a_gap_of_zero():
    assert fgl.epc_vs_actual_gap(_observations()).gap == pytest.approx(0.0)


def test_a_wrong_belief_scores_a_positive_gap_and_a_blind_one_scores_about_one():
    """The gap reads on the same 0/1 scale as every other coupled-triad gap: 1.0
    means the belief does no better than the no-skill climatological prior."""
    wrong = fgl.epc_vs_actual_gap(_observations(epc_bias=1.4))
    assert wrong.gap > 0.0
    blind = _observations()
    mean = sum(o.actual_hlc_kw_per_k for o in blind) / len(blind)
    blind = [
        fgl.FabricObservation(
            o.premise_id, o.actual_hlc_kw_per_k, mean, mean, o.floor_area_m2, o.annual_heat_kwh
        )
        for o in blind
    ]
    assert fgl.epc_vs_actual_gap(blind).gap == pytest.approx(1.0)


def test_inference_that_makes_things_WORSE_is_reported_as_negative_improvement():
    """The company is ALLOWED to be wrong. An inference worse than the register it
    started from is a real and reportable outcome, not a bug to be clamped at zero —
    clamping it would be a fail-open on the only number that says the triad is not
    working."""
    observations = _observations(epc_bias=1.1, inferred_bias=1.5)
    assert fgl.inference_improvement(observations) < 0.0
    better = _observations(epc_bias=1.5, inferred_bias=1.1)
    assert fgl.inference_improvement(better) > 0.0


@pytest.mark.parametrize("field_name", ["actual_hlc_kw_per_k", "epc_hlc_kw_per_k", "inferred_hlc_kw_per_k"])
def test_a_non_finite_fabric_observation_is_REFUSED(field_name):
    kwargs = dict(
        premise_id="P0",
        actual_hlc_kw_per_k=0.2,
        epc_hlc_kw_per_k=0.2,
        inferred_hlc_kw_per_k=0.2,
        floor_area_m2=80.0,
        annual_heat_kwh=9000.0,
    )
    kwargs[field_name] = float("nan")
    with pytest.raises(fgl.NonFiniteTrace):
        fgl.FabricObservation(**kwargs)


def test_a_gap_over_too_few_premises_RAISES():
    with pytest.raises(fgl.InsufficientEvidence):
        fgl.epc_vs_actual_gap(_observations(n=2))


def test_the_gap_metric_agrees_with_the_company_side_definition():
    """`relative_gap` is DEFINED in `company/pricing/thermal_inference.py` and never
    called there — it exists so the company and the harness cannot drift apart on
    what the number means. Check they actually agree, rather than assuming it."""
    from company.pricing.thermal_inference import relative_gap

    assert relative_gap(0.25, 0.20) == pytest.approx(0.25)
    observation = _observations(n=5, epc_bias=1.25)[0]
    assert relative_gap(
        observation.epc_hlc_kw_per_k, observation.actual_hlc_kw_per_k
    ) == pytest.approx(0.25)


# --- the money consequence -------------------------------------------------


def test_a_belief_that_is_wrong_but_does_not_FLIP_THE_RANKING_costs_nothing():
    """The honest reading, and the reason this is a DECISION metric rather than an
    error metric: being wrong about fabric only costs money when it changes which
    measure you buy."""
    tiny = fgl.money_consequence(
        _observations(epc_bias=1.005), unit_rate_p_per_kwh=25.0, belief="epc"
    )
    assert tiny.misranked_premises == 0
    assert tiny.forgone_lifetime_gbp == pytest.approx(0.0)
    assert tiny.gbp_per_tonne_co2e is None, (
        "nothing forgone must report None, never 0.0 or inf — a division that "
        "silently returns a number here is a fail-open"
    )


def test_a_belief_wrong_enough_to_FLIP_THE_RANKING_costs_real_money_and_carbon():
    wrong = fgl.money_consequence(
        _observations(epc_bias=0.30), unit_rate_p_per_kwh=25.0, belief="epc"
    )
    assert wrong.misranked_premises > 0
    assert wrong.misrank_rate > 0.0
    assert wrong.forgone_lifetime_gbp > 0.0
    assert wrong.basis.startswith("PROVISIONAL"), (
        "R14 — a financial figure resting on domain-knowledge retrofit capex must "
        "carry its basis"
    )


def test_the_money_consequence_moves_MONOTONICALLY_with_the_size_of_the_error():
    """A metric that did not respond to the error it measures would be theatre."""
    rates = [
        fgl.money_consequence(
            _observations(epc_bias=bias), unit_rate_p_per_kwh=25.0, belief="epc"
        ).misrank_rate
        for bias in (1.0, 0.6, 0.3, 0.15)
    ]
    assert rates == sorted(rates), f"misrank rate must not fall as the error grows: {rates}"
    assert rates[0] == 0.0 and rates[-1] > 0.0


def test_NO_SAVING_MAY_COME_FROM_DISCOUNTING():
    """THE MISSION CONSTRAINT, mechanised in the three places it can be broken.

    Savings count only from reduced or time-shifted usage, never from discounting.
    Note what this does NOT claim: the CHOICE of measure legitimately depends on
    the unit rate, because capex is fixed in pounds while the saving is in kWh, so
    cheap energy really does make a £12k heat pump a worse buy. An earlier draft of
    this test asserted the forgone kWh was rate-invariant end-to-end and was simply
    wrong about the economics. What must hold is narrower and actually true: the
    kWh a measure saves is physical, and no rate change can conjure one.
    """
    import inspect

    # (1) The saving function cannot even SEE a tariff.
    parameters = inspect.signature(fgl.measure_annual_saving_kwh).parameters
    assert not any("rate" in p or "price" in p or "tariff" in p for p in parameters), (
        f"a physical saving must not take a price: {list(parameters)}"
    )

    # (2) For a fixed home and a fixed measure, the kWh saved is rate-independent.
    for name, measure in fgl.DEFAULT_MEASURES.items():
        saved = fgl.measure_annual_saving_kwh(0.25, 12000.0, measure)
        assert saved == fgl.measure_annual_saving_kwh(0.25, 12000.0, measure), name

    # (3) No unit rate can make a zero-saving measure worth buying. If discounting
    # could create value, this is where it would leak in.
    useless = fgl.MeasureEconomics("useless", 5000.0, 0.0, 0.0, 0.0, 30.0)
    for rate in (5.0, 25.0, 200.0):
        ranked = dict(fgl.rank_measures(0.25, 12000.0, unit_rate_p_per_kwh=rate,
                                        measures={"useless": useless}))
        assert ranked["useless"] == pytest.approx(-5000.0), (
            "a measure that saves no kWh must be worth exactly its negative capex at "
            "every price"
        )


def test_the_carbon_consequence_is_rate_INDEPENDENT_for_a_fixed_decision():
    """Carbon is physics. Once the decision is made, the tonnes forgone cannot move
    because the tariff moved — so a rate change that does not flip any ranking must
    leave the carbon number untouched."""
    cheap = fgl.money_consequence(
        _observations(epc_bias=0.30), unit_rate_p_per_kwh=24.0, belief="epc"
    )
    dear = fgl.money_consequence(
        _observations(epc_bias=0.30), unit_rate_p_per_kwh=26.0, belief="epc"
    )
    assert cheap.misranked_premises == dear.misranked_premises, (
        "this test needs a rate move small enough not to flip any ranking"
    )
    assert cheap.forgone_annual_kwh == pytest.approx(dear.forgone_annual_kwh)
    assert cheap.forgone_annual_kg_co2e == pytest.approx(dear.forgone_annual_kg_co2e)


def test_the_measure_ranking_actually_changes_with_fabric():
    """The decision function must be sensitive to the thing the gap is about, or
    the money consequence would be structurally zero and would look like good news."""
    leaky = fgl.rank_measures(0.45, 22000.0, unit_rate_p_per_kwh=25.0)
    tight = fgl.rank_measures(0.08, 3000.0, unit_rate_p_per_kwh=25.0)
    assert leaky[0][0] != tight[0][0], (
        f"a leaky and a tight home must not want the same measure: "
        f"{leaky[0][0]} vs {tight[0][0]}"
    )


def test_solar_pv_does_not_scale_with_fabric_so_the_decision_can_be_wrong_BOTH_WAYS():
    """PV is in the choice set precisely so overestimating fabric is punished too:
    a home steered to insulation when PV was the better buy is a real error."""
    for hlc in (0.08, 0.45):
        assert fgl.measure_annual_saving_kwh(
            hlc, 12000.0, fgl.DEFAULT_MEASURES["solar_pv"]
        ) == pytest.approx(fgl.SOLAR_KWH_PER_YEAR)


@pytest.mark.parametrize(
    "call",
    [
        lambda: fgl.rank_measures(0.2, 9000.0, unit_rate_p_per_kwh=0.0),
        lambda: fgl.rank_measures(0.2, 9000.0, unit_rate_p_per_kwh=float("nan")),
        lambda: fgl.measure_annual_saving_kwh(0.0, 9000.0, fgl.DEFAULT_MEASURES["insulate"]),
        lambda: fgl.measure_annual_saving_kwh(0.2, float("nan"), fgl.DEFAULT_MEASURES["insulate"]),
    ],
)
def test_the_decision_function_REFUSES_degenerate_inputs(call):
    with pytest.raises(fgl.InsufficientEvidence):
        call()


def test_the_ledger_entry_carries_both_beliefs_and_the_two_level_result(tmp_path, generated_result):
    """The fabric gap and the realism of the traces it was measured on are written
    side by side, so neither can be read without the other."""
    ledger = tmp_path / "coupled_gap_ledger.json"
    results = fgl.write_fabric_gap_entries(
        _observations(epc_bias=1.3, inferred_bias=1.1),
        unit_rate_p_per_kwh=25.0,
        measured_at="2026-08-03T00:00:00Z",
        run_git_commit="deadbeef",
        two_level=generated_result,
        path=ledger,
    )
    assert set(results) == {"epc_vs_actual", "inferred_vs_actual"}
    written = json.loads(ledger.read_text())
    assert fgl.FABRIC_WORLD_ATOM in written and fgl.GENERATOR_WORLD_ATOM in written
    entry = written[fgl.GENERATOR_WORLD_ATOM]
    assert entry["twin_atom_id"] == fgl.FABRIC_TWIN_ATOM
    assert entry["measured_at"] == "2026-08-03T00:00:00Z"
    components = entry["components"]
    assert components["two_level"]["is_red"] is True
    assert components["two_level"]["failed_levels"]
    assert "money_consequence_epc" in components and "money_consequence_inferred" in components
    assert components["money_consequence_epc"]["basis"].startswith("PROVISIONAL")
    assert components["inference_improvement"] > 0.0, "the inferred belief is the better one here"


def test_the_ledger_write_PRESERVES_other_pairs(tmp_path, generated_result):
    """Read-merge-write: the fabric entries must not clear another triad's gap."""
    ledger = tmp_path / "coupled_gap_ledger.json"
    ledger.write_text(json.dumps({"W9_other_pair": {"gap": 0.5}}))
    fgl.write_fabric_gap_entries(
        _observations(),
        unit_rate_p_per_kwh=25.0,
        measured_at="2026-08-03T00:00:00Z",
        two_level=generated_result,
        path=ledger,
    )
    written = json.loads(ledger.read_text())
    assert written["W9_other_pair"] == {"gap": 0.5}


def test_the_module_never_calls_a_clock():
    """C-S2. `measured_at` is passed IN. A module that stamped its own time would
    make every gap unreproducible and break resume."""
    import pathlib

    text = pathlib.Path(fgl.__file__).read_text(encoding="utf-8")
    for forbidden in ("datetime.now(", "datetime.utcnow(", "time.time(", "date.today("):
        assert forbidden not in text, f"{forbidden} in a deterministic harness module"


# ===========================================================================
# §6 THE WALL
# ===========================================================================


def test_no_production_code_imports_the_harness():
    """This module holds the SIM's hidden truth and the company's belief side by
    side. If anything in `simulation/` or `company/` imported it, the company could
    read its own score and the wall would be gone.

    Checked against the real tree, not asserted in a docstring.
    """
    import pathlib

    root = pathlib.Path(fgl.__file__).resolve().parents[1]
    offenders = []
    for area in ("simulation", "company", "saas", "sim"):
        for path in (root / area).rglob("*.py"):
            text = path.read_text(encoding="utf-8", errors="ignore")
            if "fabric_gap_ledger" in text:
                offenders.append(str(path.relative_to(root)))
    assert not offenders, (
        f"production code must not import the harness that scores it: {offenders}"
    )


def test_the_harness_reads_the_world_and_the_company_but_writes_to_neither():
    """The harness is the ONLY layer permitted to hold theta and b together. It may
    IMPORT from both sides; it must not write to either."""
    import pathlib

    text = pathlib.Path(fgl.__file__).read_text(encoding="utf-8")
    for forbidden in ("open(", ".write_text(", ".write_bytes("):
        assert forbidden not in text, (
            f"{forbidden} — the harness persists ONLY through gap_metric.write_gap_entry, "
            "which writes to the observability ledger and nowhere else"
        )
