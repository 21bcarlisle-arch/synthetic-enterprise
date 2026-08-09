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

import dataclasses
import datetime as dt
import json
import math
import statistics

import pytest

from background import fabric_gap_ledger as fgl
from company.pricing import fabric_intervention as fi
from company.pricing.thermal_inference import (
    EvidenceBasis,
    InsufficientObservationError,
    is_actionable_belief,
    log_normal_interval_95,
)
from simulation import fabric_physics as fp
from simulation import premise_population as ppop
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


def _household(premise_id, property_type, build_era, insulation, bedrooms, people,
               heating_system=HeatingSystem.GAS_BOILER_COMBI):
    return Household(
        customer_id=premise_id,
        property_type=property_type,
        build_era=build_era,
        epc_rating="D",
        bedrooms=bedrooms,
        heating_system=heating_system,
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
            premise_id=spec[0],
            household=_household(*spec),
            weather=weather,
            seed=7,
            # `latitude_deg` lost its default when the fabric build closed the
            # fail-open of silently siting every premise at 53 degN. The panel is
            # the C1 weather site, so it is sited there and nowhere else.
            latitude_deg=fp.latitude_for_weather_site("C1"),
        )
        for spec in POPULATION
    ]


@pytest.fixture(scope="module")
def generated(traces, weather):
    """W1_12's generator — built, NOT yet wired into the demand path."""
    return fgl.premise_trace_population(traces, weather)


POPULATION_N = fgl.MIN_HOMES_FOR_L1_RATE
POPULATION_SEED = 17
POPULATION_AS_OF = dt.date(2022, 5, 1)


@pytest.fixture(scope="module")
def population(weather):
    """A DRAWN population, not an authored panel, at exactly the size the rate
    statistic needs to have power (`MIN_HOMES_FOR_L1_RATE`).

    Drawn from `simulation.premise_population`, whose composition is raked onto
    published EHS marginals — so the homes in it are chosen by the stock, not by
    anyone with an interest in the answer. That is the whole reason the panel could
    not be the verdict: a result on a chosen panel cannot be separated from the
    chooser's taste, and the panel's ten homes contained no storage heater at all.
    """
    drawn = ppop.draw_premise_population(
        POPULATION_N, base_seed=POPULATION_SEED, as_of=POPULATION_AS_OF
    )
    traces = [
        pt.generate_premise_trace(
            premise_id=p.premise_id,
            household=p.household,
            weather=weather,
            seed=7,
            latitude_deg=fp.latitude_for_weather_site("C1"),
        )
        for p in drawn
    ]
    return fgl.premise_trace_population(traces, weather)


@pytest.fixture(scope="module")
def population_result(population):
    return fgl.evaluate_two_level(population)


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
        # For an L1 cell this is the WORST HOME's value, which is what these
        # numbers always were; the cell's own `value` became the population
        # violation rate on 2026-08-09 and is pinned separately below.
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
    measured = cell.value if cell.worst_value is None else cell.worst_value
    assert measured == pytest.approx(expected, abs=0.01), cell.note


def test_the_shipped_path_fails_at_EVERY_home_not_at_one_of_them(shipped_result):
    """The L1 verdict is a population VIOLATION RATE, and on the shipped path it is
    1.0 on every judged cell — every single home is outside the band.

    This is the number that distinguishes a broken generator from an unlucky
    sample, and it is the reason the suite no longer reports a worst-of-N: a rate
    of 1.0 over 8 homes and a rate of 1.0 over 800 homes say the same thing, where
    a worst-of-N would have said something different for each.
    """
    for statistic in ("L1.1_half_hourly_texture", "L1.2_day_to_day_shape_correlation",
                      "L1.3_away_days_per_year", "L1.5_max_multiplicity_share"):
        cell = shipped_result.cell(statistic)
        assert cell.value == 1.0, f"{statistic}: {cell.note}"
        assert cell.homes_violating == cell.homes_judged == shipped_result.homes
        assert cell.homes_unjudged == 0


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


def test_the_EIGHT_HOME_PANEL_is_INSUFFICIENT_and_never_was_evidence(generated_result):
    """THE FINDING, PINNED (2026-08-09). Eight homes cannot clear this suite, and
    the version that let them was fail-open.

    A clean sheet over eight homes rules out a true violation rate no smaller than
    3/8 = 37.5% (rule of three), so "green on the panel" meant only "no more than
    three homes in eight are broken". Every judged L1 cell on the panel is now
    INSUFFICIENT rather than PASS, and the suite's verdict comes from the drawn
    population instead — see `population_result`.

    Note the direction: this is STRICTLY less flattering than what it replaced.
    The panel's numbers were never wrong, they were never enough.
    """
    assert generated_result.homes < fgl.MIN_HOMES_FOR_L1_RATE
    assert not generated_result.failed, (
        "the panel breaches no band — its problem is power, not fidelity: "
        + generated_result.summary()
    )
    inconclusive = {c.statistic for c in generated_result.inconclusive}
    assert inconclusive == {
        "L1.1_half_hourly_texture",
        "L1.2_day_to_day_shape_correlation",
        "L1.3_away_days_per_year",
        "L1.5_max_multiplicity_share",
    }, generated_result.summary()
    assert generated_result.is_red, (
        "an unavailable check is a FAILED check (R15) — a suite that cannot judge "
        "is not a suite that passed"
    )
    for cell in generated_result.inconclusive:
        assert cell.resolution == pytest.approx(fgl.RULE_OF_THREE / generated_result.homes)


@pytest.mark.xfail(
    strict=True,
    reason=(
        "LANDED RED AT POPULATION SCALE, 2026-08-09. On the eight-home panel this "
        "generator failed no anchored cell, and on a drawn population of 60 it "
        "fails two: L1.2 day-to-day shape correlation (1/60, P0033 at 0.9253 vs a "
        "band of 0.85) and L1.5 max multiplicity share (1/60, P0032 at 0.1167 vs "
        "0.10). Both are ONE home each — a violation rate of 1.7% — which is "
        "exactly the size of defect the panel could never have seen. AND IT IS NOT "
        "A SEED ARTEFACT: the runner's own independent draw (trace seed 17, written "
        "to the coupled gap ledger the same day) fails the same two cells at the "
        "same 1/60, on different homes (P0033 at 0.8595, P0056 at 0.1333). NEITHER "
        "BAND WAS MOVED (R12): the homes are registered for diagnosis against "
        "W1_12, and this pin is STRICT so closing them cannot pass unnoticed."
    ),
)
def test_the_premise_trace_generator_meets_the_two_level_test(population_result):
    """The requirement, held against the POPULATION rather than the panel.

    Previous residual, retained because it is still the record of how the panel's
    two cells were closed (2026-08-08) — both by naming their mechanism, neither by
    moving a band. L2.3 timing diversity 0.211 -> 1.02 half-hours: every day's
    event start was drawn from the NATIONAL window, so each home varied day to day
    while its long-run centre converged on the envelope mean — a population point
    mass hiding behind within-home variation, fixed with a persistent per-premise
    `routine_offset_periods`. L1.1 texture 0.1499 -> 0.15353: lighting and
    electronics were a per-person wattage times an occupancy FRACTION, constant
    across an occupancy block, fixed by switching them at the same expected load.
    """
    assert not population_result.is_red, population_result.summary()


def test_MEASURED_population_values(population_result):
    """The population verdict, pinned cell by cell, so "RED at population scale" is
    a checkable claim and not an adjective.

    The two numbers that carry the finding: L1.1 PASSES at 0/60 — it failed at
    n=200 under the old boolean band purely because three resistive homes were
    being judged by a heat-pump threshold — while L1.2 and L1.5 each fail on ONE
    home. A panel of eight could not have produced either statement.
    """
    assert population_result.homes >= fgl.MIN_HOMES_FOR_L1_RATE
    expected = {
        "L1.1_half_hourly_texture": (fgl.Verdict.PASS, 0.0),
        "L1.2_day_to_day_shape_correlation": (fgl.Verdict.FAIL, 1 / 60),
        "L1.3_away_days_per_year": (fgl.Verdict.PASS, 0.0),
        "L1.5_max_multiplicity_share": (fgl.Verdict.FAIL, 1 / 60),
    }
    for statistic, (verdict, rate) in expected.items():
        cell = population_result.cell(statistic)
        assert cell.verdict is verdict, cell.note
        assert cell.value == pytest.approx(rate, abs=1e-9), cell.note
        assert cell.homes_judged == 60 and cell.homes_unjudged == 0, cell.note
        assert cell.resolution == pytest.approx(0.05)
    assert {c.statistic for c in population_result.failed} == {
        "L1.2_day_to_day_shape_correlation",
        "L1.5_max_multiplicity_share",
    }
    assert not population_result.inconclusive, population_result.summary()


def test_the_DRAWN_population_actually_contains_the_regime_the_fix_is_about(
    population, population_result
):
    """The vacuity guard on the regime fix. A population with no resistive home in
    it would exercise none of this and pass regardless — the ten-home panel had
    exactly that hole, which is how the boolean band survived as long as it did."""
    regimes = {fgl.HEATING_REGIMES.get(s, "UNREGISTERED") for s in population.heating_systems}
    assert "L1.1r_half_hourly_texture_resistive_heat" in regimes, (
        f"the drawn population must contain resistive-heated homes; got {regimes}"
    )
    cell = population_result.cell(fgl.TEXTURE_STATISTIC)
    assert cell.homes_unjudged == 0, cell.note


def test_the_premise_trace_generator_is_MEASURABLY_better(shipped_result, generated_result):
    """The distance between the two columns IS the value of wiring W1_12 in,
    expressed in the units of the defect rather than as a claim that it is better.

    The shipped path is RED. As of 2026-08-08 `premise_trace` fails NO anchored
    cell, so the gap between the columns is now the whole of the shipped path's
    failure set. The subset assertion is kept as the standing regression guard:
    any cell `premise_trace` starts failing that the shipped path passes is a
    regression, and this test says so.
    """
    shipped_fails = {c.statistic for c in shipped_result.failed}
    generated_fails = {c.statistic for c in generated_result.failed}
    assert generated_fails < shipped_fails, (
        "premise_trace's failures must be a strict subset of the shipped path's — "
        f"shipped {sorted(shipped_fails)}, generated {sorted(generated_fails)}"
    )
    assert generated_fails == set()
    assert shipped_result.is_red, (
        "the shipped demand path is still RED — wiring premise_trace in is the "
        "open work this measurement exists to size, and it is NOT done"
    )


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


def _flatten_within_day(grid):
    """MUTATION for the WORST-CELL selection test — collapse each day to its own
    flat mean. Texture becomes exactly 0 while every day's total, and therefore
    the home's annual kWh, is untouched.

    `_smooth` is the right mutation for "does the L1.1 BAND fire", because it is
    the realistic failure (a generator that reuses a rolling shape). It is the
    WRONG mutation for "does the verdict pick the worst HOME", because it only
    averages across days at the same period and so leaves a spiky home's INTRA-day
    shape intact: on 2026-08-08 it took P8 from 0.2888 to 0.1556, which is above
    P7's natural 0.1535, so the poisoned home was no longer the population's worst
    and the test failed on its naming assertion while the verdict logic was in fact
    correct. A mutation that has to out-run the natural spread is a mutation whose
    strength depends on the fixture; this one is 0 by construction, so it dominates
    any population however diverse."""
    return [[sum(day) / len(day)] * len(day) for day in grid]


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
# §3b SOURCE MUTATIONS — the two 2026-08-08 fixes are proven LOAD-BEARING
#
# The mutations above act on the trace DATA, which proves the statistics fire.
# These act on the GENERATOR, which is the only thing that proves the mechanism
# that closed each cell is what is holding it open. A fix whose removal leaves
# the cell green was never the fix (R15; and mutating only the data is exactly
# how a tautology survives inside an R15 test).
# ===========================================================================


def _regenerated_result(monkeypatch, weather, **patches):
    """Re-run the whole two-level evaluation against a MUTATED generator."""
    for name, value in patches.items():
        monkeypatch.setattr(pt, name, value)
    traces = [
        pt.generate_premise_trace(
            premise_id=spec[0],
            household=_household(*spec),
            weather=weather,
            seed=7,
            latitude_deg=fp.latitude_for_weather_site("C1"),
        )
        for spec in POPULATION
    ]
    return fgl.evaluate_two_level(fgl.premise_trace_population(traces, weather))


def test_L2_3_FIRES_when_every_HOUSEHOLD_CLOCK_is_collapsed(monkeypatch, weather):
    """MUTATION for the routine offset — clamp every household's own clock to
    zero and the population is back to one national timetable.

    This is the defect as it actually was: each home still varies day to day, so
    nothing looks constant, but every home's long-run centre is the same.
    """
    mutated = _regenerated_result(monkeypatch, weather, _MAX_ROUTINE_OFFSET_PERIODS=0.0)
    failed = {c.statistic for c in mutated.failed}
    assert "L2.3_timing_diversity_periods" in failed, (
        "collapsing the per-home routine MUST re-open L2.3 — if it does not, the "
        f"routine is not what is holding the cell open. Got: {mutated.summary()}"
    )


def test_L1_1_FIRES_when_the_SWITCHED_LOADS_are_made_CONTINUOUS_again(monkeypatch, weather):
    """MUTATION for the switched lighting/electronics banks — replace the chain
    with its own expectation, which is precisely the per-person-wattage-times-
    occupancy form that made the base load flat inside every occupancy block.

    Because the mutation is the chain's MEAN, the trace keeps the same energy and
    the same level; only the texture goes. That the cell re-opens under a
    mean-preserving mutation is the evidence that L1.1 was closed by generating
    texture rather than by moving energy around.
    """
    mutated = _regenerated_result(
        monkeypatch,
        weather,
        switched_units_on=lambda rng, units, occupancy, state, **kw: units * occupancy,
    )
    failed = {c.statistic for c in mutated.failed}
    assert "L1.1_half_hourly_texture" in failed, (
        "making the switched banks continuous MUST re-open L1.1 — if it does not, "
        f"the switching is not what is holding the cell open. Got: {mutated.summary()}"
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
    poisoned[-1] = _flatten_within_day(poisoned[-1])  # one home loses its texture

    per_home = [fgl.half_hourly_texture(g) for g in poisoned]
    worst, mean = min(per_home), statistics.fmean(per_home)
    assert worst < mean * 0.9, (
        "the fixture must actually discriminate — if the smoothed home does not "
        "drag the worst materially below the mean, this test proves nothing"
    )
    # ...and it must discriminate for the RIGHT REASON. The guard above passes
    # whenever ANY home sits well below the mean, so on 2026-08-08 it stayed green
    # while the poisoned home was not the worst at all and the naming assertion
    # below failed with a message about the verdict rather than about the fixture.
    # A fixture that has stopped setting up its own premise must say so itself.
    assert per_home.index(worst) == len(per_home) - 1, (
        f"the poisoned home {generated.homes[-1]} must BE the population's worst "
        f"({worst:.4g}), else this test is checking the naming of some other home: "
        f"argmin is {generated.homes[per_home.index(worst)]}"
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

    # THE CONTRACT MOVED ON 2026-08-09 and this test moved with it. The judged
    # quantity is now the population VIOLATION RATE, and the worst home is carried
    # as `worst_value`/`worst_home` — so there are two things to prove, not one:
    # the cell still finds and NAMES the poisoned home, and the rate still reflects
    # a single broken home rather than being diluted by the seven good ones.
    assert cell.worst_value == pytest.approx(worst), (
        f"the verdict must report the WORST home ({worst:.4g}), not the population "
        f"mean ({mean:.4g}) — got {cell.worst_value}"
    )
    assert cell.worst_value != pytest.approx(mean)
    assert cell.worst_home == generated.homes[-1]
    assert generated.homes[-1] in cell.note, "the worst cell must NAME the home it found"
    # An AVERAGE of the per-home statistic would sit at 0.1877, comfortably above
    # the 0.15 band, and the cell would read green. The rate does not average: one
    # home in eight is outside its band and the cell says 1/8.
    assert mean > fgl.BANDS["L1.1_half_hourly_texture"].threshold, (
        "the fixture must be one where an average WOULD have hidden the defect, "
        "else this test proves nothing about averaging"
    )
    assert cell.homes_violating == 1
    assert cell.value == pytest.approx(1 / len(generated.homes))


# ===========================================================================
# §5 THE FABRIC GAP and its MONEY CONSEQUENCE
# ===========================================================================


# A UK heating season at the 15.5 C published base, in K.day. Fixed here so the
# fabric SHARE of each fixture premise's demand is stated rather than incidental.
FIXTURE_DEGREE_DAYS = 2000.0

# Tight enough to be actionable on the company's own rule, and identical on both
# beliefs by DEFAULT — so a difference in outcome between the two arms can only come
# from the estimate, never from one arm having been quietly handed more confidence.
FIXTURE_RELATIVE_SD = 0.20

# The unit rate the decision fixtures are priced at, and it is NOT arbitrary — see
# `test_a_high_enough_unit_rate_SATURATES_the_decision_and_fabric_stops_mattering`
# below, which is where this number is justified rather than merely chosen. 12 p/kWh
# sits inside the 2022-23 UK domestic GAS range; the previous fixtures used 25 p/kWh,
# which is an ELECTRICITY rate and at which the decision is saturated.
FIXTURE_UNIT_RATE = 12.0


def _observations(
    n=8,
    *,
    epc_bias=1.0,
    inferred_bias=1.0,
    epc_relative_sd=FIXTURE_RELATIVE_SD,
    inferred_relative_sd=FIXTURE_RELATIVE_SD,
    epc_basis=EvidenceBasis.EPC_ONLY,
    inferred_basis=EvidenceBasis.METER_AND_EPC,
):
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
            annual_degree_days_k_day=FIXTURE_DEGREE_DAYS,
            epc_relative_sd=epc_relative_sd,
            inferred_relative_sd=inferred_relative_sd,
            epc_basis=epc_basis,
            inferred_basis=inferred_basis,
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
        dataclasses.replace(o, epc_hlc_kw_per_k=mean, inferred_hlc_kw_per_k=mean)
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


@pytest.mark.parametrize(
    "field_name",
    [
        "actual_hlc_kw_per_k",
        "epc_hlc_kw_per_k",
        "inferred_hlc_kw_per_k",
        # ADDED 2026-08-09 with the fields themselves: a NaN degree-day count or a
        # NaN uncertainty would slide straight past every threshold in the decision
        # (`nan <= 0.35` is False), so they must be refused at construction like the
        # three fabric numbers already are.
        "annual_degree_days_k_day",
        "epc_relative_sd",
        "inferred_relative_sd",
    ],
)
def test_a_non_finite_fabric_observation_is_REFUSED(field_name):
    kwargs = dict(
        premise_id="P0",
        actual_hlc_kw_per_k=0.2,
        epc_hlc_kw_per_k=0.2,
        inferred_hlc_kw_per_k=0.2,
        floor_area_m2=80.0,
        annual_heat_kwh=9000.0,
        annual_degree_days_k_day=FIXTURE_DEGREE_DAYS,
        epc_relative_sd=FIXTURE_RELATIVE_SD,
        inferred_relative_sd=FIXTURE_RELATIVE_SD,
        epc_basis=EvidenceBasis.EPC_ONLY,
        inferred_basis=EvidenceBasis.METER_AND_EPC,
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


def test_a_belief_wrong_enough_to_FLIP_THE_DECISION_costs_real_money_and_carbon():
    wrong = fgl.money_consequence(
        _observations(epc_bias=0.30), unit_rate_p_per_kwh=FIXTURE_UNIT_RATE, belief="epc"
    )
    # A belief 70% low under-attributes the bill to fabric, so the company either
    # buys the wrong measure or declines outright. BOTH are charged, and the test
    # asserts the total rather than one channel: a version of this that only checked
    # `misranked_premises` would have gone green on a company that simply stopped
    # deciding.
    assert wrong.misranked_premises + wrong.declined_where_value_existed > 0
    assert wrong.forgone_lifetime_gbp > 0.0
    assert wrong.basis.startswith("PROVISIONAL"), (
        "R14 — a financial figure resting on domain-knowledge retrofit capex must "
        "carry its basis"
    )


def test_the_money_consequence_moves_MONOTONICALLY_with_the_size_of_the_error():
    """A metric that did not respond to the error it measures would be theatre."""
    rates = [
        fgl.money_consequence(
            _observations(epc_bias=bias), unit_rate_p_per_kwh=FIXTURE_UNIT_RATE, belief="epc"
        ).forgone_lifetime_gbp
        for bias in (1.0, 0.6, 0.3, 0.15)
    ]
    assert rates == sorted(rates), f"forgone value must not fall as the error grows: {rates}"
    assert rates[0] == 0.0 and rates[-1] > 0.0


def test_the_VALUE_DESTROYING_counter_can_actually_FIRE():
    """R15. `value_destroying_recommendations` reads 0 on the live panel, and a
    counter that has only ever been observed at zero is indistinguishable from one
    that cannot count. This constructs the case it exists for: a belief that
    OVERSTATES fabric badly enough that insulation looks worth buying, on a premise
    where the truth says it destroys value.

    Note what the outcome is NOT: it is not a misrank between two profitable
    measures. The company spends real capex on a home where every measure loses
    money — the failure mode that was structurally unreportable before the do-nothing
    option existed, and the whole reason this counter is separate from the misrank.
    """
    inflated = fgl.money_consequence(
        _observations(epc_bias=3.0), unit_rate_p_per_kwh=FIXTURE_UNIT_RATE, belief="epc"
    )
    assert inflated.value_destroying_recommendations > 0, (
        "an inflated fabric belief must be able to buy something that loses money"
    )
    assert inflated.value_destroying_recommendations <= inflated.misranked_premises, (
        "a value-destroying recommendation is a SUBSET of the wrong purchases, not a "
        "separate population — if it ever exceeds them the two are being counted from "
        "different denominators"
    )
    assert inflated.forgone_lifetime_gbp > 0.0


def test_the_DECLINED_WHERE_VALUE_EXISTED_counter_can_actually_FIRE():
    """R15, and the reason a decline had to be charged at all: a company that simply
    refuses every premise makes no wrong purchases, and a metric counting only wrong
    purchases would score it as flawless.

    The belief here is CORRECT to three decimal places and still costs money, because
    it rests on a stock prior — which C14 refuses to act on however tight its band.
    Honest caution has a price and this is it.
    """
    refused = fgl.money_consequence(
        _observations(epc_basis=EvidenceBasis.STOCK_PRIOR),
        unit_rate_p_per_kwh=FIXTURE_UNIT_RATE,
        belief="epc",
    )
    assert refused.misranked_premises == 0, "the belief is exact — nothing is misbought"
    assert refused.declined_where_value_existed > 0
    assert refused.forgone_lifetime_gbp > 0.0, (
        "a company that declines everything must NOT score as costless"
    )


def test_a_high_enough_unit_rate_SATURATES_the_decision_and_fabric_stops_mattering():
    """A REAL PROPERTY OF THE MODEL, recorded rather than hidden — and the reason the
    decision fixtures are priced at a gas rate and not an electricity one.

    Only `insulate` scales with the fabric belief; `heat_pump` earns its saving from
    delivered efficiency on the whole heat demand, whatever the fabric. So above some
    unit rate the heat pump wins everywhere and NO fabric error can change the
    decision — the money consequence goes to zero not because the company got fabric
    right but because fabric stopped being decision-relevant.

    That is worth a standing test in both directions. If it ever fails it means the
    measure economics moved, and every fabric decision number in the ledger should be
    re-read before it is believed. It was found the hard way: these fixtures were
    priced at 25 p/kWh, and at 25 p/kWh a belief 85% low costs exactly nothing.
    """
    saturated = fgl.money_consequence(
        _observations(epc_bias=0.15), unit_rate_p_per_kwh=25.0, belief="epc"
    )
    assert saturated.forgone_lifetime_gbp == pytest.approx(0.0), (
        "at 25 p/kWh the heat pump should dominate regardless of fabric"
    )
    biting = fgl.money_consequence(
        _observations(epc_bias=0.15), unit_rate_p_per_kwh=FIXTURE_UNIT_RATE, belief="epc"
    )
    assert biting.forgone_lifetime_gbp > 0.0, (
        f"at {FIXTURE_UNIT_RATE} p/kWh the same error must cost something, or the "
        f"fixture rate is in the saturated region too and every decision test below "
        f"it is vacuous"
    )


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

    # (1) The saving function cannot even SEE a tariff. Checked on the COMPANY's
    # function, because that is the one a decision now calls — checking the harness
    # wrapper would prove nothing about the rule that actually runs.
    parameters = inspect.signature(fi.offer_annual_saving_kwh).parameters
    assert not any("rate" in p or "price" in p or "tariff" in p for p in parameters), (
        f"a physical saving must not take a price: {list(parameters)}"
    )

    # (2) For a fixed home and a fixed measure, the kWh saved is rate-independent.
    for name, measure in fi.OFFER_BOOK.items():
        saved = fi.offer_annual_saving_kwh(0.25, 12000.0, FIXTURE_DEGREE_DAYS, measure)
        assert saved == fi.offer_annual_saving_kwh(
            0.25, 12000.0, FIXTURE_DEGREE_DAYS, measure
        ), name

    # (3) No unit rate can make a zero-saving measure worth buying. If discounting
    # could create value, this is where it would leak in.
    useless = fi.RetrofitOffer("useless", 5000.0, 0.0, 0.0, 0.0, 30.0)
    for rate in (5.0, 25.0, 200.0):
        ranked = dict(fi.rank_offers(0.25, 12000.0, FIXTURE_DEGREE_DAYS,
                                     unit_rate_p_per_kwh=rate,
                                     offers={"useless": useless}))
        assert ranked["useless"] == pytest.approx(-5000.0), (
            "a measure that saves no kWh must be worth exactly its negative capex at "
            "every price"
        )
        # ...and it must LOSE to doing nothing at every price, which is the check
        # that could not exist before there was a do-nothing to lose to.
        assert ranked[fi.DO_NOTHING] == 0.0


def _decision_vector(observations, rate, belief="epc"):
    """The (chosen, truth-best) pair for every premise, computed here from the
    company's own rule. Deliberately INDEPENDENT of `money_consequence`'s counters:
    a test that used those counters to decide whether the decisions matched would be
    asking the metric to vouch for itself."""
    out = []
    for o in observations:
        held, sd, basis = o.belief_arm(belief)
        lower, _ = log_normal_interval_95(held, sd)
        chosen = fi.decide(
            o.premise_id, held, hlc_pessimistic_kw_per_k=lower,
            actionable=is_actionable_belief(basis, sd),
            annual_heat_kwh=o.annual_heat_kwh,
            annual_degree_days_k_day=o.annual_degree_days_k_day,
            unit_rate_p_per_kwh=rate,
        ).measure
        best = fi.decide(
            o.premise_id, o.actual_hlc_kw_per_k,
            hlc_pessimistic_kw_per_k=o.actual_hlc_kw_per_k, actionable=True,
            annual_heat_kwh=o.annual_heat_kwh,
            annual_degree_days_k_day=o.annual_degree_days_k_day,
            unit_rate_p_per_kwh=rate,
        ).measure
        out.append((chosen, best))
    return out


def test_the_carbon_consequence_is_rate_INDEPENDENT_for_a_fixed_decision():
    """Carbon is physics. Once the decision is made, the tonnes forgone cannot move
    because the tariff moved — so a rate change that does not flip any decision must
    leave the carbon number untouched.

    THE GUARD HAD TO BE STRENGTHENED (2026-08-09). It previously asserted only that
    the two rates produced the same NUMBER of misranked premises, which is not the
    same as producing the same decisions: a rate move that flipped one premise from
    `insulate` to `heat_pump` and another the opposite way kept the count identical
    while changing every kWh in the sum. That is exactly what happened on the first
    run of this test after the decision moved to the company, and the assertion that
    caught it is the decision VECTOR, not its cardinality.
    """
    observations = _observations(epc_bias=0.30)
    cheap_rate, dear_rate = FIXTURE_UNIT_RATE - 0.05, FIXTURE_UNIT_RATE + 0.05
    assert _decision_vector(observations, cheap_rate) == _decision_vector(
        observations, dear_rate
    ), "this test needs a rate move small enough not to flip any decision"
    cheap = fgl.money_consequence(
        observations, unit_rate_p_per_kwh=cheap_rate, belief="epc"
    )
    dear = fgl.money_consequence(
        observations, unit_rate_p_per_kwh=dear_rate, belief="epc"
    )
    assert cheap.forgone_annual_kwh == pytest.approx(dear.forgone_annual_kwh)
    assert cheap.forgone_annual_kg_co2e == pytest.approx(dear.forgone_annual_kg_co2e)


def test_the_measure_ranking_actually_changes_with_fabric():
    """The decision function must be sensitive to the thing the gap is about, or
    the money consequence would be structurally zero and would look like good news."""
    leaky = fi.rank_offers(0.45, 22000.0, FIXTURE_DEGREE_DAYS, unit_rate_p_per_kwh=25.0)
    tight = fi.rank_offers(0.08, 3000.0, FIXTURE_DEGREE_DAYS, unit_rate_p_per_kwh=25.0)
    assert leaky[0][0] != tight[0][0], (
        f"a leaky and a tight home must not want the same measure: "
        f"{leaky[0][0]} vs {tight[0][0]}"
    )


def test_solar_pv_does_not_scale_with_fabric_so_the_decision_can_be_wrong_BOTH_WAYS():
    """PV is in the choice set precisely so overestimating fabric is punished too:
    a home steered to insulation when PV was the better buy is a real error."""
    for hlc in (0.08, 0.45):
        assert fi.offer_annual_saving_kwh(
            hlc, 12000.0, FIXTURE_DEGREE_DAYS, fi.OFFER_BOOK["solar_pv"]
        ) == pytest.approx(fi.SOLAR_KWH_PER_YEAR)


@pytest.mark.parametrize(
    "call",
    [
        lambda: fi.rank_offers(0.2, 9000.0, 2000.0, unit_rate_p_per_kwh=0.0),
        lambda: fi.rank_offers(0.2, 9000.0, 2000.0, unit_rate_p_per_kwh=float("nan")),
        lambda: fi.offer_annual_saving_kwh(0.0, 9000.0, 2000.0, fi.OFFER_BOOK["insulate"]),
        lambda: fi.offer_annual_saving_kwh(0.2, float("nan"), 2000.0, fi.OFFER_BOOK["insulate"]),
        lambda: fi.offer_annual_saving_kwh(0.2, 9000.0, 0.0, fi.OFFER_BOOK["insulate"]),
    ],
)
def test_the_decision_function_REFUSES_degenerate_inputs(call):
    """The decision now lives in the company, so its refusals are the company's
    exception type. `InsufficientObservationError` is what C14 already raises for an
    input it cannot decide on, and reusing it keeps one refusal vocabulary."""
    with pytest.raises(InsufficientObservationError):
        call()


def test_the_ledger_entry_carries_both_beliefs_and_the_two_level_result(tmp_path, population_result):
    """The fabric gap and the realism of the traces it was measured on are written
    side by side, so neither can be read without the other."""
    ledger = tmp_path / "coupled_gap_ledger.json"
    results = fgl.write_fabric_gap_entries(
        _observations(epc_bias=1.3, inferred_bias=1.1),
        unit_rate_p_per_kwh=25.0,
        measured_at="2026-08-03T00:00:00Z",
        run_git_commit="deadbeef",
        two_level=population_result,
        path=ledger,
    )
    assert set(results) == {"epc_vs_actual", "inferred_vs_actual"}
    written = json.loads(ledger.read_text())
    assert fgl.FABRIC_WORLD_ATOM in written and fgl.GENERATOR_WORLD_ATOM in written
    entry = written[fgl.GENERATOR_WORLD_ATOM]
    assert entry["twin_atom_id"] == fgl.FABRIC_TWIN_ATOM
    assert entry["measured_at"] == "2026-08-03T00:00:00Z"
    components = entry["components"]
    # The recorded verdict is cross-checked against the recorded CELLS rather than
    # trusted on its own: `is_red`, `failed`, `inconclusive` and the per-cell
    # verdicts are serialised separately, so a writer that reported a flag its own
    # cells contradict is caught here.
    two_level = components["two_level"]
    assert two_level["is_red"] is True
    assert set(two_level["failed"]) == {
        s for s, c in two_level["cells"].items() if c["verdict"] == fgl.Verdict.FAIL.value
    }
    assert two_level["inconclusive"] == []
    assert two_level["failed_levels"] == ["L1"]
    # A READER MUST BE ABLE TO SIZE THE FAILURE, which is the whole reason the
    # population fields are on the wire: two homes in sixty, not "red".
    assert two_level["homes"] == fgl.MIN_HOMES_FOR_L1_RATE
    for statistic in two_level["failed"]:
        cell = two_level["cells"][statistic]
        assert cell["homes_violating"] == 1
        assert cell["homes_judged"] == fgl.MIN_HOMES_FOR_L1_RATE
        assert cell["worst_home"]
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



# ===========================================================================
# §8 THE HEATING-CONDITIONED L1.1 BAND (2026-08-09)
#
# L1.1 is a ratio to the home's OWN mean, and a heat pump is a large, slowly-
# varying load in that denominator. One national floor applied to every home
# regardless of heating system is the same one-national-constant defect W1_12
# exists to remove, reappearing in the CONTROL — diagnosed in
# `docs/staging/WORKER_FINDING_L1_TEXTURE_BAND_IS_GAS_SHAPED_2026-08-08.md`,
# where the whole of the only failing home's deficit decomposed to its denominator.
#
# The second band is DERIVED FROM PUBLISHED FIGURES, not declared. Every test
# below exists to stop it becoming the loose band that lets anything through.
# R15's three killers are taken in turn — TAUTOLOGY (the heating fact must come
# from the register, never from the numbers being judged), FAIL-OPEN (a missing
# register fact must land on the STRICTER band), and a control that cannot fail
# (the mutation must fire on a real heat-pump trace, at the same sensitivity to
# the actual defect as the band it sits beside).
# ===========================================================================


def _flatten_blend(grid, weight):
    """MUTATION for a heating-conditioned L1.1 — blend each day toward its own
    flat daily mean. Weight 0 is the trace itself, weight 1 has texture exactly 0,
    and every day's TOTAL is preserved at every weight, so the mutation attacks
    within-day shape and nothing else.

    Used in place of `_smooth` for anything electrically heated, because
    `_smooth` IS NOT A TEXTURE-DESTROYING MUTATION ON A HEAT-PUMP HOME — measured,
    not assumed: on the matched pair below it takes the gas home 0.2471 -> 0.1539
    but RAISES the heat-pump home 0.1069 -> 0.1430. Averaging the same period
    across neighbouring days removes day-specific appliance noise while leaving
    the heat pump's repeated diurnal cycle standing, and the median step of what
    is left is larger than the median step of the original. Pinned by
    `test_the_SMOOTH_mutation_is_INVALID_on_an_electrically_heated_home`.
    """
    flat = [[sum(day) / 48.0] * 48 for day in grid]
    return [
        [(1 - weight) * grid[d][p] + weight * flat[d][p] for p in range(48)]
        for d in range(len(grid))
    ]


def _critical_flatten_weight(grid, threshold):
    """How much within-day flattening a home can absorb before it drops under a
    given band. The unit in which two bands with DIFFERENT thresholds can be
    compared for strictness: both answer "how broken must this home be to fire?"."""
    lo, hi = 0.0, 1.0
    for _ in range(40):
        mid = (lo + hi) / 2
        if fgl.half_hourly_texture(_flatten_blend(grid, mid)) < threshold:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def _matched_household(premise_id, heating_system):
    """The SAME household in every respect except how it heats — semi-detached,
    1965-80, partial insulation, three bedrooms, three people. A matched pair is
    what makes the comparison below a statement about the heating system rather
    than about two different houses."""
    return _household(
        premise_id, PropertyType.SEMI_DETACHED, BuildEra.ERA_1965_1980,
        InsulationLevel.PARTIAL, 3, 3, heating_system=heating_system,
    )


@pytest.fixture(scope="module")
def matched_pair(weather):
    """One heat-pump home and one gas home from the REAL generator, identical in
    every other respect. Not synthetic series: a hand-built trace could be given
    whatever texture the author wanted, and the point of these mutations is that
    they fire on the generator actually under test."""
    return tuple(
        pt.generate_premise_trace(
            premise_id=premise_id,
            household=_matched_household(premise_id, heating),
            weather=weather,
            seed=7,
            latitude_deg=fp.latitude_for_weather_site("C1"),
        )
        for premise_id, heating in (
            ("HP1", HeatingSystem.HEAT_PUMP_AIR),
            ("G1", HeatingSystem.GAS_BOILER_COMBI),
        )
    )


def test_the_electric_band_is_DERIVED_from_published_figures_not_declared():
    """The threshold is arithmetic over four published numbers. This test re-does
    that arithmetic independently of the function, so a hand-edit of the threshold
    that is not also an edit to a published input FAILS — which is the shape a
    quiet relaxation would take."""
    heat = 9500.0 * 0.825          # Ofgem TDCV gas medium x EST in-situ combi efficiency
    hp_electricity = heat / 2.78   # EoH median ASHP SPFH4
    behavioural_share = 2500.0 / (2500.0 + hp_electricity)   # Ofgem TDCV electricity medium
    expected = 0.15 * behavioural_share

    assert fgl.electric_heat_texture_threshold() == pytest.approx(expected, rel=1e-12)
    assert fgl.BANDS["L1.1e_half_hourly_texture_electric_heat"].threshold == pytest.approx(
        expected, rel=1e-12
    )
    # The published inputs themselves, pinned so a change to one is a visible diff
    # against the source cited in the band's anchor_source rather than a silent
    # re-derivation.
    assert fgl._TDCV_ELECTRICITY_MEDIUM_KWH == 2500.0
    assert fgl._TDCV_GAS_MEDIUM_KWH == 9500.0
    assert fgl._COMBI_BOILER_IN_SITU_EFFICIENCY == 0.825
    assert fgl._ASHP_MEDIAN_SPFH4 == 2.78
    assert fgl._GAS_TEXTURE_THRESHOLD == 0.15


def test_the_electric_band_is_ROBUST_across_the_published_spreads():
    """The band must not rest on a point estimate. Taken at the JOINT corners of
    the two published spreads — SPFH4 over the EoH interquartile range crossed
    with the boiler efficiency over +/-1sd of the EST trial — the whole envelope
    is 0.0655-0.0758, so no defensible reading of the sources produces a band that
    would change any verdict this suite reaches."""
    corners = [
        0.15 * (2500.0 / (2500.0 + (9500.0 * eff) / spf))
        for spf in (2.55, 3.05)
        for eff in (0.785, 0.865)
    ]
    assert min(corners) == pytest.approx(0.0655, abs=5e-4)
    assert max(corners) == pytest.approx(0.0758, abs=5e-4)
    assert min(corners) < fgl.electric_heat_texture_threshold() < max(corners)


def test_the_SMOOTH_mutation_is_INVALID_on_an_electrically_heated_home(matched_pair):
    """Recorded because it is the trap this section walked into, and a later reader
    reaching for the obvious mutation deserves to find it already measured.

    `_smooth` is the file's mutation for L1.1 and it is sound on a gas home. On a
    heat-pump home it moves texture the WRONG WAY. Had the electric band been
    R15-proven with it, the proof would have been vacuous in the direction that
    matters — a mutation that raises the statistic cannot demonstrate that a band
    fires."""
    heat_pump, gas = matched_pair
    hp_grid = [list(day) for day in heat_pump.half_hourly("electricity")]
    gas_grid = [list(day) for day in gas.half_hourly("electricity")]

    assert fgl.half_hourly_texture(_smooth(gas_grid)) < fgl.half_hourly_texture(gas_grid)
    assert fgl.half_hourly_texture(_smooth(hp_grid)) > fgl.half_hourly_texture(hp_grid), (
        "if this ever reverses, _smooth has become a valid mutation for electric "
        "heat and the reason for _flatten_blend should be re-stated, not deleted"
    )


def test_L1_1_ELECTRIC_band_FIRES_when_a_real_heat_pump_home_is_FLATTENED(matched_pair):
    """R15 — the mutation. A band that cannot fail is worse than none, and a
    numerically lower band is exactly where that failure hides."""
    heat_pump, _ = matched_pair
    grid = [list(day) for day in heat_pump.half_hourly("electricity")]
    band = fgl.BANDS["L1.1e_half_hourly_texture_electric_heat"]

    before = fgl.half_hourly_texture(grid)
    assert band.judge(before) is fgl.Verdict.PASS, (
        f"the unmutated heat-pump trace should clear its own band: {before}"
    )
    # Monotone in the mutation, so "it fired" is not an artefact of one weight.
    values = [fgl.half_hourly_texture(_flatten_blend(grid, w)) for w in (0.0, 0.25, 0.5, 0.75, 1.0)]
    assert values == sorted(values, reverse=True), values
    assert band.judge(values[-1]) is fgl.Verdict.FAIL
    assert band.judge(fgl.half_hourly_texture(_flatten_blend(grid, 0.5))) is fgl.Verdict.FAIL


def test_the_electric_band_is_NOT_LOOSER_THAN_THE_GAS_BAND_against_the_same_defect(matched_pair):
    """The charge this band has to answer: that a threshold was lowered so the
    thing it judges would stop failing (R12 goal-seek). Thresholds on different
    denominators cannot be compared directly — 0.0705 against 0.15 says nothing.
    What CAN be compared is how broken each home must be before its own band
    fires, on a MATCHED PAIR that differs only in heating system.

    Measured: the heat-pump home fires at 0.349 of the way to a flat day, the gas
    home at 0.396. The electric band is if anything the STRICTER of the two in the
    only unit that matters — sensitivity to the actual defect. It is a rescaling
    of the denominator, not a relaxation."""
    heat_pump, gas = matched_pair
    hp_grid = [list(day) for day in heat_pump.half_hourly("electricity")]
    gas_grid = [list(day) for day in gas.half_hourly("electricity")]

    hp_critical = _critical_flatten_weight(hp_grid, fgl.electric_heat_texture_threshold())
    gas_critical = _critical_flatten_weight(gas_grid, 0.15)

    assert hp_critical == pytest.approx(0.349, abs=0.02)
    assert gas_critical == pytest.approx(0.396, abs=0.02)
    assert hp_critical <= gas_critical + 0.05, (
        f"the electric band tolerates materially more damage than the gas band "
        f"before firing ({hp_critical:.3f} vs {gas_critical:.3f}) — that IS a "
        f"relaxation, whatever the derivation says"
    )


def test_the_heating_fact_comes_from_the_REGISTER_not_from_the_numbers(matched_pair, weather):
    """R15 TAUTOLOGY. The flag that selects the band must be a register fact — the
    household's heating system, which is what a real supplier holds as
    `main_heating_fuel`. Inferring "this looks smooth, so it must be a heat pump"
    from the very statistic being judged would make the band unfalsifiable.

    Proven by holding the NUMBERS fixed and changing only the claim: the identical
    trace judged as a gas home FAILS and judged as a heat-pump home PASSES. If the
    flag were derived from the series, both would reach the same verdict."""
    heat_pump, _ = matched_pair
    texture = fgl.half_hourly_texture([list(d) for d in heat_pump.half_hourly("electricity")])

    assert fgl.BANDS["L1.1_half_hourly_texture"].judge(texture) is fgl.Verdict.FAIL
    assert fgl.BANDS["L1.1e_half_hourly_texture_electric_heat"].judge(texture) is fgl.Verdict.PASS
    # ...and the builder reads that fact off the trace's register field, which is
    # itself set from `household.is_gas_heated` at generation time.
    assert heat_pump.heating_commodity == "electricity"
    assert fgl.premise_trace_population([heat_pump], weather).heating_systems == (
        HeatingSystem.HEAT_PUMP_AIR.value,
    )


def test_the_band_selection_is_FAIL_CLOSED_when_the_register_fact_is_MISSING(matched_pair, weather):
    """R15 FAIL-OPEN. A population built without the heating flags must judge every
    home by the STRICTER gas band. A caller who forgets the register fact gets a
    false RED, never a false GREEN — the lenient direction has to be asserted."""
    heat_pump, _ = matched_pair
    grid = tuple(tuple(day) for day in heat_pump.half_hourly("electricity"))
    homes = tuple(f"HP{i}" for i in range(fgl.MIN_HOMES_FOR_DIVERSITY))

    blind = fgl.PopulationTraces(
        generator="test — heating fact withheld",
        homes=homes,
        grids=tuple(grid for _ in homes),
        is_weekend=tuple(bool(d.is_weekend) for d in weather),
        annual_kwh=tuple(3000.0 for _ in homes),
        weather_driver=fgl.hdd_driver(weather),
    )
    assert blind.heating_systems == ()

    cell = fgl.evaluate_two_level(blind).cell(fgl.TEXTURE_STATISTIC)
    assert cell.band.threshold == 0.15, "a missing register fact must land on the gas band"
    assert cell.verdict is fgl.Verdict.FAIL


def test_a_MISALIGNED_heating_flag_is_REFUSED_not_silently_truncated(matched_pair, weather):
    """The other half of the fail-closed argument: a flag tuple that does not line
    up with the homes is a caller bug, and zipping it silently would judge the
    wrong home by the wrong band."""
    heat_pump, _ = matched_pair
    grid = tuple(tuple(day) for day in heat_pump.half_hourly("electricity"))
    with pytest.raises(fgl.InsufficientEvidence):
        fgl.PopulationTraces(
            generator="test — misaligned flags",
            homes=("A", "B"),
            grids=(grid, grid),
            is_weekend=tuple(bool(d.is_weekend) for d in weather),
            annual_kwh=(3000.0, 3000.0),
            heating_systems=(HeatingSystem.HEAT_PUMP_AIR.value,),
        )


def test_the_worst_L1_1_cell_is_the_worst_MARGIN_not_the_lowest_RAW_value(generated, matched_pair):
    """With two thresholds live, the lowest raw texture is no longer the home in
    most trouble. The worst cell must be the worst margin against each home's OWN
    band, or a gas home sitting just under 0.15 would be hidden behind a heat-pump
    home comfortably clearing 0.0705 with a smaller number — a fail-open created
    by the very fix that closed the false red."""
    heat_pump, _ = matched_pair
    hp_grid = [list(day) for day in heat_pump.half_hourly("electricity")]
    gas_band = fgl.BANDS["L1.1_half_hourly_texture"]

    # A REAL gas home mutated just under its own band, rather than an invented
    # series: 0.6 of the way to a flat day takes the fixture's first home there.
    failing_gas = _flatten_blend(_grids(generated)[0], 0.6)
    gas_texture = fgl.half_hourly_texture(failing_gas)
    hp_texture = fgl.half_hourly_texture(hp_grid)

    assert gas_band.judge(gas_texture) is fgl.Verdict.FAIL, gas_texture
    assert hp_texture < gas_texture, (
        "the premise of this test is that the heat-pump home carries the LOWER raw "
        f"number: hp {hp_texture} vs gas {gas_texture}"
    )

    others = _grids(generated)[1:]
    population = fgl.PopulationTraces(
        generator="test — margin selection",
        homes=("HP", "GAS") + tuple(f"F{i}" for i in range(len(others))),
        grids=(
            tuple(tuple(d) for d in hp_grid),
            tuple(tuple(d) for d in failing_gas),
        ) + tuple(tuple(tuple(d) for d in g) for g in others),
        is_weekend=generated.is_weekend,
        annual_kwh=(3000.0, 3000.0) + generated.annual_kwh[1:],
        heating_systems=(HeatingSystem.HEAT_PUMP_AIR.value,
                         HeatingSystem.GAS_BOILER_COMBI.value)
                        + (HeatingSystem.GAS_BOILER_COMBI.value,) * len(others),
        weather_driver=generated.weather_driver,
    )

    cell = fgl.evaluate_two_level(population).cell(fgl.TEXTURE_STATISTIC)
    assert cell.worst_home == "GAS", (
        f"the failing gas home must be the reported worst cell, not the numerically "
        f"lower heat-pump home: {cell.note}"
    )
    assert "worst home GAS" in cell.note
    assert cell.verdict is fgl.Verdict.FAIL
    assert cell.band.threshold == 0.15
    # And the RATE says how many homes are in trouble, which the worst-of-N form
    # could never do: exactly one, the gas home that was mutated under its band.
    assert cell.homes_violating == 1 and cell.homes_judged == len(population.homes)


# ===========================================================================
# §7 SCALE INVARIANCE — the verdict must be about the generator, not about n
#
# `docs/staging/WORKER_FINDING_WORST_OF_N_CONTROL_IS_NOT_SCALE_INVARIANT_2026-08-09.md`.
# The old L1 form was a worst-of-N, which is monotone in N by construction: the
# same generator on the same weather with the same seed scored green at n=25 and
# red at n=200, and nothing in the report said which n produced the verdict.
# ===========================================================================


def _worst_of_n(values, band):
    """THE OLD STATISTIC, kept here as the thing the new one is compared against.

    This is deliberately a re-implementation rather than an import: the point of
    every test below is that these two forms answer differently, and a test that
    could only run while the old code still existed would evaporate the moment it
    was deleted.
    """
    return min(values) if band.direction == "at_least" else max(values)


BROKEN_SHARE = 0.20        # exactly one home in five, at EVERY population size
_PHI = 0.6180339887498949  # low-discrepancy step, so any prefix is a fair subsample


def _graded_pool(grids, size):
    """A pool of `size` homes in which exactly `BROKEN_SHARE` of ANY prefix that is
    a multiple of five is outside the L1.1 band — and in which the broken ones are
    flattened to DIFFERENT depths, deepening as the pool grows.

    Both properties are deliberate, and they are what make the comparison below a
    test rather than a demonstration. The constant share is the truth about the
    world that a scale-invariant statistic must recover at any n; the deepening
    tail is the artefact that a worst-of-N reports instead.
    """
    out = []
    for i in range(size):
        broken = (i % 5) == 0
        # A broken home's depth is drawn from a low-discrepancy sequence, so the
        # deepest ones only appear as the pool grows — exactly how a real rare tail
        # reveals itself, and exactly what drags a worst-of-N around.
        # The unbroken homes are left EXACTLY as generated. Even a 5% blend pushes
        # the panel's tightest home (0.1535) under the 0.15 band, which would make
        # the "broken" share a number nobody chose — measured, on the first run.
        weight = (0.55 + 0.25 * ((i * _PHI) % 1.0)) if broken else 0.0
        out.append(_flatten_blend(grids[i % len(grids)], weight))
    return out


def test_the_RATE_is_invariant_in_n_where_the_WORST_OF_N_is_not(generated):
    """THE FINDING, REPRODUCED AS A STANDING TEST.

    One pool of homes, looked at twice: a 50-home prefix and the whole 200. The
    world does not change between the two reads — one home in five is outside the
    band at both sizes. The rate recovers exactly that, at both sizes. The
    worst-of-N reports two different numbers, and always in the same direction,
    because a min over a bigger sample can only go one way.

    Read the two assertions together: the first says the new form is right, the
    second says the old form could not have been, ON THE SAME DATA. Either alone
    would be an argument rather than a measurement.
    """
    band = fgl.BANDS["L1.1_half_hourly_texture"]
    pool = _graded_pool(_grids(generated), 200)
    textures = [fgl.half_hourly_texture(g) for g in pool]

    def cell(n):
        # Through the PRODUCTION cell, not a re-implementation of it. A test that
        # computed the rate itself would demonstrate a property of arithmetic and
        # assert nothing about the code under test — the tautology pattern that has
        # already been found once inside this file's own R15 tests.
        return _texture_cell(
            textures[:n], (band,) * n, tuple(f"H{i}" for i in range(n))
        )

    small, large = 50, 200
    for n in (small, large):
        assert cell(n).value == pytest.approx(BROKEN_SHARE), (
            f"the cell must report the share of the population that is broken "
            f"({BROKEN_SHARE}), whatever n: got {cell(n).value} at n={n}"
        )
        assert cell(n).homes_violating == int(n * BROKEN_SHARE)

    worst_small = _worst_of_n(textures[:small], band)
    worst_large = _worst_of_n(textures[:large], band)
    assert worst_large < worst_small, (
        "the fixture must actually exhibit the defect being guarded against — a "
        "worst-of-N that does not degrade with n proves nothing here: "
        f"{worst_small:.4g} at n={small} vs {worst_large:.4g} at n={large}"
    )
    assert worst_small / worst_large > 1.15, (
        f"and it must degrade MATERIALLY, else the two forms are interchangeable: "
        f"{worst_small:.4g} -> {worst_large:.4g}"
    )


def _clone_population(grid, n, weather, *, heating=None):
    homes = tuple(f"H{i}" for i in range(n))
    return fgl.PopulationTraces(
        generator="test — clones",
        homes=homes,
        grids=tuple(tuple(tuple(d) for d in grid) for _ in homes),
        is_weekend=tuple(bool(d.is_weekend) for d in weather),
        annual_kwh=tuple(3000.0 for _ in homes),
        weather_driver=fgl.hdd_driver(weather),
        heating_systems=() if heating is None else tuple(heating for _ in homes),
    )


def _texture_cell(values, bands, homes):
    return fgl._l1_rate_cell(
        fgl.TEXTURE_STATISTIC, values=values, bands=bands, homes=homes
    )


@pytest.mark.parametrize(
    "n, expected",
    [
        (fgl.MIN_HOMES_FOR_L1_RATE - 1, fgl.Verdict.INSUFFICIENT),
        (fgl.MIN_HOMES_FOR_L1_RATE, fgl.Verdict.PASS),
    ],
)
def test_a_CLEAN_SHEET_only_PASSES_once_it_could_have_SEEN_a_defect(n, expected):
    """THE FAIL-OPEN DIRECTION, closed at its exact boundary.

    Zero violations in n homes rules out a true violation rate no smaller than 3/n
    (rule of three). At 59 homes that is 5.08% and this suite claims to see 5%, so
    the clean sheet is INSUFFICIENT; at 60 it is 5.00% and the same clean sheet is
    a PASS. Nothing about the homes changes between the two rows — only whether
    enough of them were looked at, which is precisely the thing the old form never
    said out loud.
    """
    band = fgl.BANDS["L1.1_half_hourly_texture"]
    passing = band.threshold * 1.5
    cell = _texture_cell(
        [passing] * n, (band,) * n, tuple(f"H{i}" for i in range(n))
    )
    assert cell.verdict is expected, cell.note
    assert cell.value == 0.0
    assert cell.resolution == pytest.approx(fgl.RULE_OF_THREE / n)


@pytest.mark.parametrize("n", [fgl.MIN_HOMES_FOR_DIVERSITY, 20, 500])
def test_ONE_violating_home_FAILS_at_EVERY_n(n):
    """The other half of the asymmetry, and the half that must NOT be n-dependent.

    A violation is evidence of a mechanism however small the sample, so the FAIL
    direction has no power requirement at all. Waiting for a bigger sample before
    admitting a breach would be a fail-open dressed as statistical caution.
    """
    band = fgl.BANDS["L1.1_half_hourly_texture"]
    values = [band.threshold * 1.5] * n
    values[0] = band.threshold * 0.5
    cell = _texture_cell(values, (band,) * n, tuple(f"H{i}" for i in range(n)))
    assert cell.verdict is fgl.Verdict.FAIL, cell.note
    assert cell.homes_violating == 1
    assert cell.value == pytest.approx(1 / n)


def test_the_RESOLUTION_the_verdict_rests_on_is_REPORTED_not_implied(population_result):
    """A reader must be able to tell a worse generator from a bigger sample, and
    that means n and the resolution it bought travel WITH the verdict — on the
    cell, and in the printed summary. This is the reporting half of the finding
    and it is the half a rate statistic alone would not have fixed."""
    text = population_result.summary()
    for cell in population_result.cells:
        if cell.rate_band is None:
            continue
        assert cell.homes_judged is not None and cell.resolution is not None
        assert f"{cell.homes_violating}/{cell.homes_judged} homes outside band" in text
        assert f"resolution {cell.resolution:.3g}" in text


def test_the_goal_seek_warning_needs_a_PREVALENCE_not_a_single_home(population_result):
    """R15, and this control's first recorded FALSE POSITIVE (2026-08-09).

    The warning reads "L1.1 passes while L1.5 fails" as tuning — level noise
    sprinkled onto a rescaled base shape. That inference was sound when both cells
    were worst-of-N. Under a rate it is not: the population's L1.5 breach is ONE
    home in sixty, and a rescaled base shape is a property of the generator, so it
    would be in every home it makes. The warning is silent here, and it must still
    fire when the artefact is actually widespread.
    """
    assert population_result.cell(fgl.TEXTURE_STATISTIC).verdict is fgl.Verdict.PASS
    assert population_result.cell(fgl.STRUCTURAL_STATISTIC).verdict is fgl.Verdict.FAIL
    assert population_result.cell(fgl.STRUCTURAL_STATISTIC).value < 0.05
    assert population_result.goal_seek_warning() is None, (
        "one home in sixty is a home to diagnose (R4), not evidence that someone "
        "moved a number"
    )

    # ...and the silence is not a broken control: raise the prevalence past the
    # floor on the SAME result object and the warning comes back.
    widespread = dataclasses.replace(
        population_result,
        cells=tuple(
            dataclasses.replace(c, value=0.9)
            if c.statistic == fgl.STRUCTURAL_STATISTIC else c
            for c in population_result.cells
        ),
    )
    assert widespread.goal_seek_warning() is not None, (
        "with the artefact in 90% of homes this IS the tuning signature and the "
        "warning must fire"
    )


# ===========================================================================
# §8 THE HEATING REGIME IS A RATIO, NOT A CATEGORY (R10 class closure)
#
# `docs/staging/WORKER_FINDING_HEATING_REGIME_CONDITIONING_IS_BINARY_2026-08-09.md`.
# The 2026-08-08 fix conditioned the L1.1 band on `is_gas_heated`, a BOOLEAN, while
# the physics is keyed on delivered efficiency — so a resistive storage heater was
# judged by a threshold derived from heat-pump arithmetic.
# ===========================================================================


REGIME_FIXTURES = (
    ("G1", HeatingSystem.GAS_BOILER_COMBI, "L1.1_half_hourly_texture"),
    ("HP1", HeatingSystem.HEAT_PUMP_AIR, "L1.1e_half_hourly_texture_electric_heat"),
    ("ST1", HeatingSystem.ELECTRIC_STORAGE, "L1.1r_half_hourly_texture_resistive_heat"),
    ("ED1", HeatingSystem.ELECTRIC_DIRECT, "L1.1r_half_hourly_texture_resistive_heat"),
)


@pytest.fixture(scope="module")
def matched_regimes(weather):
    """The SAME household with four different machines in it — the panel the
    boolean band never had. Real generated traces, not synthetic series."""
    return {
        heating: pt.generate_premise_trace(
            premise_id=premise_id,
            household=_matched_household(premise_id, heating),
            weather=weather,
            seed=7,
            latitude_deg=fp.latitude_for_weather_site("C1"),
        )
        for premise_id, heating, _ in REGIME_FIXTURES
    }


def test_EVERY_heating_system_is_registered_or_explicitly_UNANCHORED():
    """THE CLASS GUARD (R10). The instance was a storage heater judged by a heat
    pump's band; the class is a heating system reaching L1.1 through somebody
    else's threshold.

    A member may legitimately map to the NEED band — what it may not do is fall
    through silently. This test fails the moment a new machine appears in the
    generator's enum with no entry here, which is the only reason the register is
    written out as strings rather than derived from the enum: a register derived
    from the thing it is supposed to constrain could not fail.
    """
    for system in HeatingSystem:
        assert system.value in fgl.HEATING_REGIMES, (
            f"{system.value} has no entry in HEATING_REGIMES — it would be judged "
            "by the unregistered band by default, which is visible, but a NEW "
            "machine deserves a decision rather than a fallback"
        )
        assert fgl.HEATING_REGIMES[system.value] in fgl.BANDS


def test_the_RESISTIVE_band_is_DERIVED_from_the_same_published_figures():
    """Re-derived from the constants, not pinned as a literal, so a change to any
    published input moves the band in a diff instead of silently disagreeing with
    the docstring that explains it."""
    heat = 9500.0 * 0.825
    resistive_electricity = heat / 1.0
    share = 2500.0 / (2500.0 + resistive_electricity)
    assert fgl.resistive_heat_texture_threshold() == pytest.approx(0.15 * share)
    assert fgl.resistive_heat_texture_threshold() == pytest.approx(0.03628, abs=1e-5)
    assert fgl.BANDS["L1.1r_half_hourly_texture_resistive_heat"].threshold == (
        pytest.approx(fgl.resistive_heat_texture_threshold())
    )


@pytest.mark.parametrize("efficiency", [1.0, 1.5, 2.0, 2.78, 3.5, 5.0])
def test_the_band_is_MONOTONE_in_delivered_efficiency(efficiency):
    """The class property that makes this a ratio and not a category: a machine
    that delivers the same heat for less electricity leaves MORE of the meter to
    behaviour, so its band is HIGHER. Any future regime slots onto this curve
    without a new branch — which is what closing the class means."""
    band = fgl.heating_texture_threshold(efficiency)
    assert fgl.heating_texture_threshold(efficiency * 0.9) < band
    assert band < fgl.heating_texture_threshold(efficiency * 1.1)
    assert band < fgl._GAS_TEXTURE_THRESHOLD, (
        "no electrically-heated machine may score a band above the gas one — its "
        "heat is in the denominator and gas's is not"
    )


@pytest.mark.parametrize("efficiency", [0.0, -1.0, float("nan"), float("inf")])
def test_a_DEGENERATE_efficiency_is_REFUSED_not_absorbed(efficiency):
    """Fail-open pattern 2. A non-finite or non-positive efficiency reaching the
    division would produce a band nobody could read, and `nan > t` is silently
    False — so it raises before any arithmetic."""
    with pytest.raises(fgl.InsufficientEvidence):
        fgl.heating_texture_threshold(efficiency)


@pytest.mark.parametrize("premise_id, heating, expected_band", REGIME_FIXTURES)
def test_each_REGIME_is_judged_by_its_OWN_band(matched_regimes, premise_id, heating,
                                               expected_band):
    """Every registered machine reaches the band derived for IT, on a real trace.

    The storage-heated row is the finding: measured at 0.0484 it clears its own
    resistive band (0.0363) and FAILS the heat-pump band (0.0705) it used to be
    judged by. The band moved because the physics changed, not because a number
    was inconvenient — and the assertion below is what makes that checkable rather
    than assertable.
    """
    trace = matched_regimes[heating]
    texture = fgl.half_hourly_texture([list(d) for d in trace.half_hourly("electricity")])
    band = fgl.texture_band_for(heating.value)
    assert band.statistic == expected_band
    assert band.judge(texture) is fgl.Verdict.PASS, (
        f"{premise_id} texture {texture:.4g} vs its own band {band.threshold:.4g}"
    )
    if expected_band == "L1.1r_half_hourly_texture_resistive_heat":
        ashp = fgl.BANDS["L1.1e_half_hourly_texture_electric_heat"]
        assert ashp.judge(texture) is fgl.Verdict.FAIL, (
            f"{premise_id} at {texture:.4g} would have passed the heat-pump band "
            "too, so this row proves nothing about the regime fix"
        )


@pytest.mark.parametrize("premise_id, heating, expected_band", REGIME_FIXTURES)
def test_the_MUTATION_that_proves_each_band_is_VALID_on_THAT_regime(
    matched_regimes, premise_id, heating, expected_band
):
    """R15, and the class behind
    `WORKER_FINDING_MUTATION_VALID_ON_ONE_SUBPOPULATION_ONLY_2026-08-09.md`.

    A mutation is the evidence that a band CAN fail. `_smooth` moves the statistic
    the wrong way on a heat-pump home, so reusing it for an electrically-heated
    band would have produced an R15 proof that was vacuous in the only direction
    that matters. The guard against a repeat is per-regime rather than per-band:
    for EVERY registered machine, the mutation must move that machine's own
    statistic DOWN and take it below its own band.

    A new regime added to `HEATING_REGIMES` with no fixture here fails
    `test_EVERY_heating_system_is_registered_or_explicitly_UNANCHORED` first, so
    the class cannot be reopened quietly.
    """
    trace = matched_regimes[heating]
    grid = [list(d) for d in trace.half_hourly("electricity")]
    band = fgl.texture_band_for(heating.value)
    before = fgl.half_hourly_texture(grid)
    after = fgl.half_hourly_texture(_flatten_blend(grid, 0.9))
    assert after < before, (
        f"the mutation must DESTROY texture on a {heating.value} home, not raise it: "
        f"{before:.4g} -> {after:.4g}"
    )
    assert band.judge(before) is fgl.Verdict.PASS
    assert band.judge(after) is fgl.Verdict.FAIL, (
        f"{heating.value}: the mutation left {after:.4g}, still inside a band of "
        f"{band.threshold:.4g} — this band has no proof that it can fire"
    )


def test_an_UNREGISTERED_machine_is_COUNTED_never_folded_into_another_band(weather,
                                                                          matched_regimes):
    """The register hole is VISIBLE. A ground-source heat pump has no published
    SPFH4 in this file, and both silent folds are wrong in a different direction:
    reading it as gas fails a correct heat pump, reading it as an air-source heat
    pump passes a smooth resistive home. It is measured, counted, and excluded
    from the rate."""
    assert fgl.HEATING_REGIMES[HeatingSystem.HEAT_PUMP_GROUND.value] == (
        fgl.UNREGISTERED_TEXTURE_BAND
    )
    band = fgl.texture_band_for(HeatingSystem.HEAT_PUMP_GROUND.value)
    assert band.threshold is None and band.anchor is fgl.AnchorStatus.NEED

    gas = fgl.BANDS["L1.1_half_hourly_texture"]
    n = 100
    values = [gas.threshold * 1.5] * n
    bands = [gas] * n
    bands[0] = band                       # one unregistered machine
    cell = _texture_cell(values, tuple(bands), tuple(f"H{i}" for i in range(n)))
    assert cell.homes_unjudged == 1
    assert cell.homes_judged == n - 1
    assert cell.verdict is fgl.Verdict.PASS, cell.note


def test_a_population_MOSTLY_unregistered_is_INSUFFICIENT_not_clean():
    """The vacuity guard. A population control that reports a clean rate while
    most of its homes were never judged is the exact shape this codebase has
    already been bitten by (1557/1557 passing while the field was absent)."""
    gas = fgl.BANDS["L1.1_half_hourly_texture"]
    unregistered = fgl.BANDS[fgl.UNREGISTERED_TEXTURE_BAND]
    n = 100
    unjudged = int(n * fgl.MAX_UNJUDGED_SHARE) + 1
    bands = [unregistered] * unjudged + [gas] * (n - unjudged)
    cell = _texture_cell(
        [gas.threshold * 1.5] * n, tuple(bands), tuple(f"H{i}" for i in range(n))
    )
    assert cell.verdict is fgl.Verdict.INSUFFICIENT, cell.note
    assert "coverage floor" in cell.note


def test_a_population_with_NO_judgeable_band_at_all_is_INSUFFICIENT():
    """And the degenerate end of the same guard: zero judged homes is not a clean
    sheet, it is no measurement. An unavailable check is a FAILED check."""
    unregistered = fgl.BANDS[fgl.UNREGISTERED_TEXTURE_BAND]
    n = 10
    cell = _texture_cell(
        [0.5] * n, (unregistered,) * n, tuple(f"H{i}" for i in range(n))
    )
    assert cell.verdict is fgl.Verdict.INSUFFICIENT
    assert cell.homes_judged == 0 and cell.homes_unjudged == n
    assert "the register is the hole" in cell.note


def test_the_MISSING_register_fact_still_fails_CLOSED_onto_the_gas_band(weather,
                                                                       matched_regimes):
    """Absence and the unknown are treated DIFFERENTLY, deliberately. A caller that
    supplies nothing gets the strictest band (a false red, never a false green); a
    caller that names a machine nobody has registered gets the visible hole. Both
    directions are asserted because either one alone would be an argument."""
    heat_pump = matched_regimes[HeatingSystem.HEAT_PUMP_AIR]
    grid = [list(d) for d in heat_pump.half_hourly("electricity")]
    blind = _clone_population(grid, fgl.MIN_HOMES_FOR_DIVERSITY, weather)
    assert blind.heating_systems == ()
    cell = fgl.evaluate_two_level(blind).cell(fgl.TEXTURE_STATISTIC)
    assert cell.band.threshold == fgl._GAS_TEXTURE_THRESHOLD
    assert cell.verdict is fgl.Verdict.FAIL
    assert cell.homes_unjudged == 0, "absence is judged strictly, not left unjudged"

    # The same trace, with the register fact supplied, at the population size the
    # rate statistic needs — so the PASS direction is actually reachable and the
    # comparison is band-selection against band-selection, not power against power.
    named = _clone_population(
        grid, fgl.MIN_HOMES_FOR_L1_RATE, weather,
        heating=HeatingSystem.HEAT_PUMP_AIR.value,
    )
    cell = fgl.evaluate_two_level(named).cell(fgl.TEXTURE_STATISTIC)
    assert cell.band.threshold == pytest.approx(fgl.electric_heat_texture_threshold())
    assert cell.verdict is fgl.Verdict.PASS
    assert cell.homes_violating == 0 and cell.homes_unjudged == 0
