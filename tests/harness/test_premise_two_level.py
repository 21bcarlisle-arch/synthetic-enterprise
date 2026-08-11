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
import random
import statistics

import pytest

from background import fabric_gap_ledger as fgl
from background import lcl_household_anchors as anchors
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
def population(weather, drawn_traces):
    """A DRAWN population, not an authored panel, at exactly the size the rate
    statistic needs to have power (`MIN_HOMES_FOR_L1_RATE`).

    Drawn from `simulation.premise_population`, whose composition is raked onto
    published EHS marginals — so the homes in it are chosen by the stock, not by
    anyone with an interest in the answer. That is the whole reason the panel could
    not be the verdict: a result on a chosen panel cannot be separated from the
    chooser's taste, and the panel's ten homes contained no storage heater at all.
    """
    return fgl.premise_trace_population(drawn_traces, weather)


@pytest.fixture(scope="module")
def drawn_traces(weather):
    """The same draw, as TRACES rather than as a population.

    Kept alongside `population` because a diagnosis needs components the
    population form deliberately does not carry: `PopulationTraces` exposes the
    meter and the space-heat split, which is exactly what the harness is allowed
    to judge on, while a decomposition of a breach has to look at what else is in
    the meter (H36's water-heater finding).
    """
    drawn = ppop.draw_premise_population(
        POPULATION_N, base_seed=POPULATION_SEED, as_of=POPULATION_AS_OF
    )
    return [
        pt.generate_premise_trace(
            premise_id=p.premise_id,
            household=p.household,
            weather=weather,
            seed=7,
            latitude_deg=fp.latitude_for_weather_site("C1"),
        )
        for p in drawn
    ]


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
        # L2.3n, not L2.3: the raw spread is still 0.0 and still recorded (in
        # `test_the_shipped_path_is_a_TIMING_POINT_MASS` below), but the floor over
        # it came out on 2026-08-10 and the judging cell is now the null ratio.
        ("L2.3n_timing_diversity_null_ratio", 0.0),
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
    identical half-hour (L2.3n = 0, an exact point mass whose re-deal null is
    degenerate — every day peaks at the same half-hour, so there is no null and
    the cell is scored a definitive violation rather than skipped).
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


def test_the_remaining_unanchored_cells_are_reported_UNVALIDATED_not_passed(shipped_result):
    """A statistic with no anchor is MEASURED and REPORTED but excluded from the
    verdict, rather than given an invented threshold.

    This is the honest failure mode to choose: a fabricated band would make the
    suite look rigorous while being unfalsifiable.

    WAS THREE, IS TWO (2026-08-09). L2.4 left this list when the Low Carbon London
    panel anchored it — see `test_the_L2_4_cell_is_ANCHORED_on_the_LCL_PANEL`.
    L1.4 briefly left it the same day and CAME BACK; the reason is measured and
    pinned in `test_the_L1_4_ANCHOR_DOES_NOT_TRANSFER_to_a_120_day_window`.
    `L1.2h_heating_shape_repeatability` — the quantity L1.2 nets out — has no
    published statistic for how repeatable a thermostat is.
    """
    for statistic in (
        "L1.4_weekday_weekend_separation",
        "L1.2h_heating_shape_repeatability",
    ):
        cell = shipped_result.cell(statistic)
        assert cell.verdict is fgl.Verdict.UNVALIDATED, cell.note
        assert cell.band.anchor is fgl.AnchorStatus.NEED, statistic
        assert cell.band.threshold is None, statistic


def test_the_L2_4_cell_is_ANCHORED_on_the_LCL_PANEL(shipped_result):
    """L2.4 stopped being decorative on 2026-08-09.

    It was `AnchorStatus.NEED` from the day this suite was written, which is honest
    and has a price: an unanchored cell is reported and never judged, so a
    generator can be arbitrarily wrong on it while the suite still reads green.
    The anchor was already in the repo — 304 real Low Carbon London households,
    fetched for an unrelated workload — and it measures exactly this quantity.
    `background/lcl_household_anchors.py` holds the panel, the rule that picked the
    threshold, and what the panel is NOT.

    THE BAND MUST TRACE TO THE PANEL, not to a number typed here: the assertion
    below reads the anchor module, so a threshold edited in the band table without
    the panel behind it fails this test.
    """
    band = fgl.BANDS["L2.4_scale_spread_p90_p10"]
    assert band.anchor is fgl.AnchorStatus.PUBLISHED
    assert band.threshold == anchors.LCL_SCALE_SPREAD_P90_P10_FLOOR
    assert "Low Carbon London" in band.anchor_source

    # AND THE SHIPPED PATH IS RED ON THE CELL THAT COULD ALWAYS SEE IT. It spans
    # 1.58x between its 10th and 90th percentile home; the anchor says real
    # households span 5.38x. "Visibly wrong" was never a threshold, and now it does
    # not have to be. (The 8% recorded when this suite was written was the shipped
    # path's spread over a DIFFERENT panel; the number moved, the verdict did not,
    # which is why the value and the verdict are both asserted.)
    spread = shipped_result.cell("L2.4_scale_spread_p90_p10")
    assert spread.verdict is fgl.Verdict.FAIL, spread.note
    assert spread.value == pytest.approx(1.58, abs=0.05), spread.note
    assert spread.value < band.threshold


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

    THE PANEL DOES NOW BREACH ONE BAND (2026-08-09). L2.4 is a POPULATION
    statistic, not a per-home one, so it is judgeable at eight homes and it is red
    at eight homes — which says the panel's problem is power on the L1 cells AND
    fidelity on L2.4, not power alone. The distinction is kept in the assertion
    below rather than collapsed into "the panel is red".
    """
    assert generated_result.homes < fgl.MIN_HOMES_FOR_L1_RATE
    assert {c.statistic for c in generated_result.failed} == {
        "L2.4_scale_spread_p90_p10"
    }, (
        "the panel breaches only the anchored spread band — every L1 cell's "
        "problem here is power, not fidelity: " + generated_result.summary()
    )
    inconclusive = {c.statistic for c in generated_result.inconclusive}
    assert inconclusive == {
        "L1.1_half_hourly_texture",
        # L1.1n joined on 2026-08-10 (H39) and lands here for the ordinary
        # reason: 0 of 8 panel homes are under their own null (worst 2.391), and
        # 8 homes cannot rule out the 5% rate this suite claims to see.
        "L1.1n_half_hourly_texture_null_ratio",
        "L1.2_day_to_day_shape_correlation",
        "L1.3_away_days_per_year",
        # L1.4n joined the suite on 2026-08-09 and lands HERE rather than in
        # `failed` even though 2 of the 8 panel homes are outside their own null:
        # a 25% violation rate at n=8 cannot be told apart from the 40% tolerance,
        # which is the rate machinery doing its job on a new cell without anyone
        # special-casing it.
        "L1.4n_weekday_weekend_null_ratio",
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
        "RE-PINNED 2026-08-09, and NOT by a generator regression — by an ANCHOR "
        "landing. L2.4 (between-home spread of annual consumption) had been "
        "AnchorStatus.NEED since this suite was written: measured, reported, never "
        "judged. Anchored on 304 real Low Carbon London households it reads 1.80 "
        "against a floor of 4.88 — the drawn population's homes are between two and "
        "three times too ALIKE in scale. Nothing about the generator changed; a cell "
        "that had never been able to fail acquired the ability, and used it "
        "immediately. That is the fourth time this suite's own control SET, not its "
        "controls, turned out to be the hole. STRICT: when the generator's scale "
        "spread reaches the anchor this XPASSes and whoever fixes it writes down "
        "how, exactly as the four cells below were closed."
    ),
)
def test_the_premise_trace_generator_meets_the_two_level_test(population_result):
    """The requirement, held against the POPULATION rather than the panel.

    UNPINNED 2026-08-09, then RE-PINNED the same day when L2.4 was anchored (see
    the decorator). The pin has now done its job in both directions: it caught the
    generator getting better, and it caught the suite getting sharper.

    THE FOUR CELLS THIS GENERATOR HAS CLOSED, EACH BY NAMING A MECHANISM AND NONE
    BY MOVING A BAND — the record is kept whole because the method is the point:

    * L2.3 timing diversity 0.211 -> 1.02 half-hours (2026-08-08). Every day's
      event start was drawn from the NATIONAL window, so each home varied day to
      day while its long-run centre converged on the envelope mean — a population
      point mass hiding behind within-home variation. Fixed with a persistent
      per-premise `routine_offset_periods`.
    * L1.1 texture 0.1499 -> 0.15353 (2026-08-08). Lighting and electronics were a
      per-person wattage times an occupancy FRACTION, constant across an occupancy
      block. Fixed by switching them at the same expected load.
    * L1.5 max multiplicity 7/200 -> 0/200 (2026-08-09). Every stochastic component
      was gated on occupancy, so an away day was a byte-identical clone of every
      other away day. Fixed by making the cold-appliance duty the heat balance it
      physically is, against the premise's own setpoint.
    * L1.2 day-to-day shape correlation 2/200 -> 0/200 (2026-08-09), AND THIS ONE
      WAS THE CONTROL'S DEFECT, NOT THE GENERATOR'S. The two violators were
      electric-storage homes; decomposing them (`meter_net_of_machines`) put the
      whole deficit in the heating stream — 0.9133 on a storage home's ELECTRICITY
      meter against 0.9197 and 0.9080 on gas homes' GAS meters, i.e. the same
      repeatability in every regime — while their behaviour scored 0.32 and 0.11
      against a population median of 0.22. The band is a statement about
      households and was being asked about a thermostat. It is judged on the same
      load set for every home now; the threshold is untouched at 0.85 and the
      quantity removed is reported as `L1.2h_heating_shape_repeatability`.
    """
    assert not population_result.is_red, population_result.summary()


def test_MEASURED_population_values(population, population_result):
    """The population verdict, pinned cell by cell, so "RED at population scale" is
    a checkable claim and not an adjective.

    L1.2 MOVED TO PASS, 2026-08-09, BY JUDGING EVERY HOME ON THE SAME LOAD SET —
    the threshold is untouched at 0.85 and no home was excluded from the count.
    Its two n=200 violators were electric-storage homes whose ELECTRICITY meter
    carries their heat; the heating stream repeats at 0.91-0.96 in EVERY regime
    (gas homes included, on the gas meter, where L1.2 never saw it) while their
    behaviour scores 0.11-0.32 against a population median of 0.22. The cell is
    now computed on the meter net of space heat, the worst home in the population
    is a GAS home at 0.4386, and what was netted out is reported next door as
    `L1.2h_heating_shape_repeatability` rather than dropped.

    L1.5 MOVED TO PASS, 2026-08-09, BY FIXING THE GENERATOR AND NOT THE BAND. The
    0.10 threshold is untouched and no cell was marked UNVALIDATED. On the n=200
    draw the cell failed with 7 homes outside band, and the breach was 100%
    away-day driven: for all seven, EVERY occurrence of the most-repeated
    normalised fraction landed on an away day (measured, not inferred — excluding
    away days dropped all seven to 0.043-0.061 against the 0.10 band). An away day
    had no stochastic component at all, so it was a clone of every other away day
    and the normalised fractions collided exactly. The cold-appliance duty is now
    the heat balance it always physically was — proportional to (room - cabinet),
    against the premise's own comfort setpoint as the reference, so a home at its
    setpoint draws exactly what it drew before — and away days differ because the
    weather does. 7/200 -> 0/200, 1/60 -> 0/60.
    """
    assert population_result.homes >= fgl.MIN_HOMES_FOR_L1_RATE
    expected = {
        fgl.TEXTURE_STATISTIC: (fgl.Verdict.PASS, 0.0),
        "L1.2_day_to_day_shape_correlation": (fgl.Verdict.PASS, 0.0),
        "L1.3_away_days_per_year": (fgl.Verdict.PASS, 0.0),
        "L1.5_max_multiplicity_share": (fgl.Verdict.PASS, 0.0),
    }
    for statistic, (verdict, rate) in expected.items():
        cell = population_result.cell(statistic)
        assert cell.verdict is verdict, cell.note
        assert cell.value == pytest.approx(rate, abs=1e-9), cell.note
        assert cell.homes_judged == 60 and cell.homes_unjudged == 0, cell.note
        assert cell.resolution == pytest.approx(0.05)

    # L1.1 CLOSED ON 2026-08-10 (H38) AND THE FLOOR STILL HAS NOT MOVED. H36 made
    # this cell sharper and opened a 1-in-60 breach (P0008 at 0.1423); H38 took the
    # WATER heater out of the denominator alongside the space heater and it reads
    # 0/60. The worst home is now a GAS home, which is the tell that this was a
    # load-set repair and not a leniency: after it, the marginal home in the
    # population is one the netting never touched.
    texture = population_result.cell(fgl.TEXTURE_STATISTIC)
    assert texture.homes_judged == 60 and texture.homes_unjudged == 0, texture.note
    assert texture.worst_home == "P0036", texture.note
    assert texture.worst_value == pytest.approx(0.1521, abs=5e-4), texture.note
    assert "gas" in population.heating_systems[
        population.homes.index(texture.worst_home)
    ], "the marginal home after the repair must be one the netting did not touch"
    # NOBODY WAS EXCLUDED TO GET HERE. All 60 homes are judged on every anchored
    # cell — the electrically heated ones included — which is the difference
    # between netting a component out of a statistic and dropping the homes that
    # breached it.
    #
    # EVERY L1 CELL IS GREEN AND THE POPULATION IS STILL RED, on the L2 cell that
    # was anchored on 2026-08-09. Pinned as a value and not merely as a verdict, so
    # a generator that closes half the gap is visible as progress rather than as a
    # still-red flag: 60 drawn homes span 2.17x between their 10th and 90th
    # percentile against real households' 5.38x (floor 4.88).
    assert {c.statistic for c in population_result.failed} == {
        "L2.4_scale_spread_p90_p10",
    }, population_result.summary()
    spread = population_result.cell("L2.4_scale_spread_p90_p10")
    assert spread.value == pytest.approx(2.17, abs=0.05), spread.note
    assert not population_result.inconclusive, population_result.summary()
    assert population_result.cell(
        "L1.2_day_to_day_shape_correlation"
    ).worst_value == pytest.approx(0.4386, abs=0.01), "the worst home is a GAS home"


def test_the_L1_1_BREACH_WAS_the_WATER_HEATER_and_the_LOAD_SET_CLOSED_IT(
    drawn_traces, population, population_result
):
    """H38, and it is the decomposition H36 recorded, now run as the closure.

    WHAT WAS OPEN. H36 made this cell sharper by reading it net of SPACE heat, and
    one home in the drawn sixty went under the floor: P0008 at 0.1423 against 0.15.
    The floor was not moved, P0008 was not excluded and the cell was not marked
    UNVALIDATED — any of the three turns it green in one edit while making the
    measurement worse (R12).

    WHAT IT WAS. The same wrong-load-set shape one machine over. What is left after
    the space heater comes out is the WATER heater, 36-40% of what this cell then
    called behaviour, and the floor's own anchor is a gas-heated home's electricity
    meter — where the water is heated by gas. So the anchor population never
    carried this load and the netting restores the load set the floor was derived
    on. It is a DENOMINATOR effect and not a spikiness one: three 12-minute draws a
    day move six steps in 47, and the numerator is a median.

    WHAT CLOSED IT. `machine_draw` puts both machines into the one stream the L1
    cells net out. The floor is still 0.15.
    """
    heated = [t for t in drawn_traces if t.heating_commodity == "electricity"]
    assert len(heated) >= 3, "the diagnosis needs the homes it is about"

    for trace in heated:
        meter = [list(day) for day in trace.half_hourly("electricity")]
        space_heat = [list(day.heating_fuel_kwh) for day in trace.days]
        water_heat = [list(day.dhw_fuel_kwh) for day in trace.days]
        behavioural = fgl.meter_net_of_machines(meter, space_heat)
        water_share = sum(map(sum, water_heat)) / sum(map(sum, behavioural))
        assert 0.30 <= water_share <= 0.45, (
            f"{trace.premise_id}: the water heater is {water_share:.1%} of what "
            "L1.1 called behaviour before this repair — if this has moved, the "
            "diagnosis below is about a different stream"
        )
        net_of_both = fgl.half_hourly_texture(
            meter, machines=fgl.machine_draw(space_heat, water_heat)
        )
        assert net_of_both > fgl.half_hourly_texture(meter, machines=space_heat), (
            f"{trace.premise_id}: taking the water heater out must RAISE texture "
            "— if it does not, this breach was the generator's and not the load "
            "set's, and the repair has to be reconsidered"
        )
        assert fgl.BANDS[fgl.TEXTURE_STATISTIC].judge(
            net_of_both
        ) is fgl.Verdict.PASS, (
            f"{trace.premise_id} does not clear the floor even net of both "
            "machines — then the water heater was not the whole story"
        )

    # ...and the CELL is the thing that had to move, not just the statistic.
    cell = population_result.cell(fgl.TEXTURE_STATISTIC)
    assert cell.verdict is fgl.Verdict.PASS, cell.note
    assert cell.homes_violating == 0 and cell.homes_unjudged == 0, cell.note


def test_the_WATER_HEATER_netting_is_a_LOAD_SET_repair_and_not_a_LOOSENING(
    drawn_traces, population
):
    """R15's hard direction for H38, and the reason it needs its own test.

    Netting space heat was a STRENGTHENING and could be proven as one: homes that
    had been passing with their behaviour destroyed started failing. Netting the
    water heater moves every affected reading UP (0.1423 -> 0.2048), so the same
    proof is not available and the honest question is a different one — is the cell
    now asking an electrically heated home an EASIER question than it asks the gas
    homes whose meters derived the floor?

    Measured in the only unit in which two regimes are comparable: how much of its
    own behaviour a home must lose before the cell fires (`_critical_behaviour_
    weight`, H36's). Raw values are not comparable across regimes; this is.

    THE GAS COLUMN IS THE CONTROL AND IT IS NOT A TARGET. It is identical under
    both readings — a gas home heats its water with gas, so its water-heat stream
    on the electricity meter is zeros — which makes it an independent reference
    rather than something this repair could have tuned toward.
    """
    gas_criticals, electric_before, electric_after = [], [], []
    for trace in drawn_traces:
        meter = [list(day) for day in trace.half_hourly("electricity")]
        on_meter = trace.heating_commodity == "electricity"
        space = [list(day.heating_fuel_kwh) if on_meter else [0.0] * 48
                 for day in trace.days]
        water = [list(day.dhw_fuel_kwh) if on_meter else [0.0] * 48
                 for day in trace.days]
        behaviour = [list(day.behavioural_electricity_kwh) for day in trace.days]
        before = _critical_true_behaviour_weight(meter, behaviour, space)
        after = _critical_true_behaviour_weight(
            meter, behaviour, fgl.machine_draw(space, water)
        )
        if on_meter:
            electric_before.append(before)
            electric_after.append(after)
        else:
            gas_criticals.append(before)
            assert after == pytest.approx(before, abs=1e-9), (
                f"{trace.premise_id}: a gas home must be BIT-FOR-BIT unmoved by the "
                "water-heat netting, or the reference this is measured against is "
                "not independent of the repair"
            )

    assert len(electric_after) >= 3 and len(gas_criticals) >= 30
    gas_median = statistics.median(gas_criticals)
    assert gas_median == pytest.approx(0.3066, abs=0.01)

    # BEFORE: an electrically heated home fired at a fraction of the breakage a gas
    # home needed — P0008 at 0.0000 was already under the floor untouched.
    assert max(electric_before) < gas_median / 3, (
        f"electric homes fired at {sorted(round(v, 4) for v in electric_before)} "
        f"against a gas median of {gas_median:.4f}"
    )
    # AFTER: they answer the same question the anchor population answers. Bounded
    # on BOTH sides — a netting that made them markedly HARDER to fail than a gas
    # home would be a leniency, and this is the assertion that would catch it.
    for value in electric_after:
        assert 0.6 * gas_median <= value <= 1.6 * gas_median, (
            f"after the repair an electrically heated home fires at {value:.4f} "
            f"against a gas median of {gas_median:.4f} — parity with the anchor "
            "population is the claim, and it is not holding"
        )


def _critical_true_behaviour_weight(meter, behaviour, machines):
    """How much of its TRUE behavioural stream a home loses before L1.1 fires.

    Distinct from `_critical_behaviour_weight` further down, and the difference is
    the point of it: that one flattens the RESIDUAL (whatever is left after the
    netting), which is the right mutation for the reading under test. This one
    flattens the generator's own `behavioural_electricity_kwh` and rebuilds the
    meter around it, so the SAME defect is posed to two different readings and the
    answers can be compared. Flattening the residual would pose a different defect
    to each and the comparison would be meaningless.
    """
    flat = [[sum(day) / 48.0] * 48 for day in behaviour]
    rest = [[m - b for m, b in zip(m_day, b_day)]
            for m_day, b_day in zip(meter, behaviour)]
    lo, hi = 0.0, 1.0
    for _ in range(40):
        mid = (lo + hi) / 2
        mutated = [
            [(1 - mid) * b + mid * f + r for b, f, r in zip(b_day, f_day, r_day)]
            for b_day, f_day, r_day in zip(behaviour, flat, rest)
        ]
        if fgl.half_hourly_texture(mutated, machines=machines) < 0.15:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def test_a_water_heater_on_the_OTHER_commodity_is_not_netted(drawn_traces, weather):
    """The netting must be the IDENTITY on a home that heats its water with gas,
    and the population builder is where that is decided.

    This is the arm that keeps the repair a load-set correction rather than a
    rescaling of everybody: 57 of the 60 drawn homes must be bit-for-bit what they
    were, because a gas home's cylinder is on the gas meter and contributes zeros
    to the electricity meter it is judged on.

    THE FAILURE DIRECTION IF THE KEYING IS EVER WRONG IS THE STRICT ONE. A home
    with gas space heat and an electric immersion would contribute zeros here, its
    water heater would stay in the judged meter, and it would be held to a floor
    derived without one — the reading H38 calls too strict. That is a finding, not
    a hole, and it is asserted rather than hoped for.
    """
    population = fgl.premise_trace_population(drawn_traces, weather)
    off_meter = 0
    for k, trace in enumerate(drawn_traces):
        water = population.water_heat_grids[k]
        on_this_meter = trace.heating_commodity == "electricity"
        if on_this_meter:
            assert any(any(day) for day in water), (
                f"{trace.premise_id} heats on the judged meter and must declare a "
                "water-heat stream, or the netting is silently a no-op on it"
            )
            continue
        off_meter += 1
        assert not any(any(day) for day in water), (
            f"{trace.premise_id} heats its water on the OTHER commodity — its "
            "electricity-meter water stream must be zeros, not its gas draw"
        )
        assert sum(sum(d.dhw_fuel_kwh) for d in trace.days) > 0.0, (
            "...and it must genuinely HAVE a water heater, or this asserts nothing"
        )
        grid = [list(day) for day in population.grids[k]]
        assert fgl.half_hourly_texture(
            grid, machines=_machines_of(population, k)
        ) == fgl.half_hourly_texture(grid), f"{trace.premise_id} was not left alone"
    assert off_meter >= 30, "the no-op arm needs a population to be a no-op on"


def test_HALF_a_split_is_NOT_a_split_and_the_WHOLE_meter_is_JUDGED(population):
    """R15 fail-closed, on the rule H38 added rather than the one it inherited.

    `machine_draw` returns None if EITHER stream is absent, so a builder that
    supplies space heat and forgets water heat judges the WHOLE meter instead of
    netting the half it has. The lenient-looking alternative — net what you were
    given — is the fail-open shape: it would report "judged net of the machines"
    over a load set that still carries one, and nothing downstream could tell.

    Both directions, because a rule that only ever returns None is not fail-closed,
    it is broken.
    """
    assert fgl.machine_draw(None, None) is None
    assert fgl.machine_draw([[1.0]], None) is None
    assert fgl.machine_draw(None, [[1.0]]) is None
    assert fgl.machine_draw([[1.0]], [[0.5]]) == [[1.5]]

    full = fgl.evaluate_two_level(population).cell(fgl.TEXTURE_STATISTIC)
    assert "net of space AND water heat" in full.note

    for missing in ("space_heat_grids", "water_heat_grids"):
        half = fgl.evaluate_two_level(
            dataclasses.replace(population, **{missing: ()})
        ).cell(fgl.TEXTURE_STATISTIC)
        assert "no machine split supplied" in half.note, (
            f"dropping {missing} left the cell claiming a netting it did not do"
        )
        # THE WITNESS IS THE UNJUDGED COUNT AND NOT THE WORST VALUE, which is
        # itself a small finding: after the repair the worst home is a GAS home,
        # and a gas home reads the same netted or not — so `worst_value` is blind
        # to this change and an assertion on it would have passed vacuously.
        assert full.homes_unjudged == 0 and half.homes_unjudged == 3, (
            f"dropping {missing} left {half.homes_unjudged} homes unjudged — the "
            "three homes whose heat is on this meter must lose their split with it"
        )
        assert half.verdict is not fgl.Verdict.PASS, half.note


def test_the_REPAIR_ITSELF_fires_its_own_named_defect(population):
    """R15 for H38 as a whole: put the water heater back and the breach it closed
    comes back.

    The mutation is the repair reversed — net only space heat, exactly the H36
    reading — and it must return the cell to FAIL with P0008 named. A repair whose
    removal changes nothing was not the thing that fixed it, and the alternative
    explanations (a population that drifted, a floor that moved, a home that got
    dropped) are all excluded by this going red on the same home and the same
    value H36 recorded.
    """
    live = fgl.evaluate_two_level(population).cell(fgl.TEXTURE_STATISTIC)
    assert live.verdict is fgl.Verdict.PASS and live.homes_violating == 0, live.note

    reverted = fgl.evaluate_two_level(
        dataclasses.replace(
            population,
            water_heat_grids=tuple(
                tuple((0.0,) * len(day) for day in home)
                for home in population.water_heat_grids
            ),
        )
    ).cell(fgl.TEXTURE_STATISTIC)
    assert reverted.verdict is fgl.Verdict.FAIL, reverted.note
    assert reverted.homes_violating == 1 and reverted.worst_home == "P0008", reverted.note
    assert reverted.worst_value == pytest.approx(0.1423, abs=5e-4), reverted.note


def test_the_WATER_HEAT_stream_is_CHECKED_against_the_meter_it_claims_to_be_in(
    population,
):
    """The guard applies to the summed stream, so a water-heat claim is checked as
    hard as a space-heat one. Without this a generator could declare its behaviour
    to be hot water and walk out of the cell — the exact escape
    `_require_component_of_meter` was built to close, re-armed on the second
    stream rather than assumed to extend to it."""
    inflated = dataclasses.replace(
        population,
        water_heat_grids=tuple(
            tuple(tuple(v * 10.0 for v in day) for day in home)
            for home in population.grids
        ),
    )
    with pytest.raises(fgl.InsufficientEvidence, match="COMPONENT"):
        fgl.evaluate_two_level(inflated)

    ragged = dataclasses.replace(
        population,
        water_heat_grids=tuple(
            tuple(day[:-1] for day in home) for home in population.water_heat_grids
        ),
    )
    with pytest.raises(fgl.InsufficientEvidence):
        fgl.evaluate_two_level(ragged)


def test_the_DRAWN_population_actually_contains_the_regime_the_fix_is_about(
    population, population_result
):
    """The vacuity guard on the regime fix. A population with no resistive home in
    it would exercise none of this and pass regardless — the ten-home panel had
    exactly that hole, which is how the boolean band survived as long as it did."""
    heated = {
        s for s in population.heating_systems
        if fgl.HEAT_ON_THE_JUDGED_METER.get(s, True)
    }
    assert heated, (
        "the drawn population must contain homes whose heat is on the judged "
        f"meter; got {set(population.heating_systems)}"
    )
    assert "electric_storage" in heated or "electric_direct" in heated, (
        f"...and resistive heat among them, which the panel never had; got {heated}"
    )
    cell = population_result.cell(fgl.TEXTURE_STATISTIC)
    assert cell.homes_unjudged == 0, cell.note


def test_the_premise_trace_generator_is_MEASURABLY_better(shipped_result, generated_result):
    """The distance between the two columns IS the value of wiring W1_12 in,
    expressed in the units of the defect rather than as a claim that it is better.

    The shipped path is RED. `premise_trace` fails ONE anchored cell — L2.4, since
    it was anchored on 2026-08-09 — and the shipped path fails that one too, and
    worse (1.58 against 2.12 on the same panel), so the gap between the columns is
    still every other cell. The subset assertion is the standing regression guard:
    any cell `premise_trace` starts failing that the shipped path passes is a
    regression, and this test says so.
    """
    shipped_fails = {c.statistic for c in shipped_result.failed}
    generated_fails = {c.statistic for c in generated_result.failed}
    assert generated_fails < shipped_fails, (
        "premise_trace's failures must be a strict subset of the shipped path's — "
        f"shipped {sorted(shipped_fails)}, generated {sorted(generated_fails)}"
    )
    assert generated_fails == {"L2.4_scale_spread_p90_p10"}
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


def _homes_with_heat_on_the_judged_meter(population):
    """The homes whose heating machine draws from the meter L1.2 reads — i.e. the
    only homes the netting can possibly affect."""
    return [
        k for k, grid in enumerate(population.space_heat_grids)
        if any(any(day) for day in grid)
    ]


def _machines_of(population, k):
    """Home `k`'s heating-machine stream composed EXACTLY as the live cell composes
    it — `fgl.machine_draw` of the space and water streams (H38).

    Every mutation below has to rebuild a meter that the cell can then take apart
    again. Composing the machine stream by hand here would let a mutation net a
    different load set from the one under test, and the failure mode is silent: the
    residual picks up the difference between two machine streams and reads as
    behaviour that is not there.
    """
    return fgl.machine_draw(
        [list(d) for d in population.space_heat_grids[k]]
        if population.space_heat_grids else None,
        [list(d) for d in population.water_heat_grids[k]]
        if population.water_heat_grids else None,
    )


def _machines_of_trace(trace, *, on_this_meter=True):
    """A TRACE's heating-machine stream as the shipped cell composes it (H38).

    `on_this_meter=False` returns None — the fail-closed reading for a home whose
    generator states no split. Every mutation below goes through this rather than
    reaching for `heating_fuel_kwh` alone, because a mutation proved against a
    load set the ledger does not judge on is an R15 proof of nothing: that is the
    live-mechanism-with-a-dead-input shape, and it is how H36's proofs would have
    silently stopped covering the shipped reading the moment H38 landed.
    """
    if not on_this_meter:
        return None
    return fgl.machine_draw(
        [list(d.heating_fuel_kwh) for d in trace.days],
        [list(d.dhw_fuel_kwh) for d in trace.days],
    )


def test_the_DRAWN_population_contains_a_home_whose_HEAT_IS_ON_THE_JUDGED_METER(population):
    """THE VACUITY GUARD on the netting, and it is not a formality: a population of
    gas-heated homes exercises none of this and would pass whatever the netting
    did. The authored eight-home panel is exactly that population, which is why
    this fix could only ever have been found on a drawn one."""
    affected = _homes_with_heat_on_the_judged_meter(population)
    assert affected, (
        "no home in the drawn population carries space heat on the electricity "
        "meter, so the L1.2 netting is untested by this fixture"
    )
    assert len(affected) < len(population.homes), (
        "and it must contain homes heated OFF the judged meter too, or the "
        "no-op arm of this fix is vacuous as well"
    )


def test_L1_2_still_FIRES_when_an_ELECTRICALLY_HEATED_homes_BEHAVIOUR_is_replayed(population):
    """R15, THE ARM THAT MATTERS. Netting the heating machines out of L1.2 buys
    leniency; this proves it did not buy immunity.

    The mutation is the cell's own named defect (`_replay_one_day`) applied to the
    stream that is actually judged, on the very home the netting rescued, with its
    real heating stream added back so the meter is a meter. If the control had been
    disarmed rather than corrected, this would pass and nothing else in the suite
    would notice.

    The unmutated call comes first, so a control that fails on everything cannot
    satisfy this test.
    """
    affected = _homes_with_heat_on_the_judged_meter(population)
    assert affected
    k = affected[0]
    clean = fgl.evaluate_two_level(population).cell("L1.2_day_to_day_shape_correlation")
    assert clean.verdict is fgl.Verdict.PASS, clean.note

    heat = _machines_of(population, k)
    behaviour = fgl.meter_net_of_machines([list(d) for d in population.grids[k]], heat)
    replayed = _replay_one_day(behaviour)
    poisoned = [
        tuple(b + h for b, h in zip(bd, hd)) for bd, hd in zip(replayed, heat)
    ]
    grids = list(population.grids)
    grids[k] = tuple(poisoned)
    mutated = dataclasses.replace(population, grids=tuple(grids))

    cell = fgl.evaluate_two_level(mutated).cell("L1.2_day_to_day_shape_correlation")
    assert cell.verdict is fgl.Verdict.FAIL, cell.note
    assert cell.worst_home == population.homes[k], cell.note
    assert cell.worst_value == pytest.approx(1.0, abs=1e-9), (
        "a replayed behavioural shape correlates at exactly 1 THROUGH the netting"
    )


def test_L1_2_judges_the_WHOLE_METER_when_the_generator_supplies_no_split(population):
    """FAIL-CLOSED, proven by removing the fact. The leniency is bought with a
    stated split; a generator that cannot state one has its whole meter judged.

    This is also the direct attribution for the cell's pass (R9): the SAME
    population, the SAME band, the SAME statistic, differing only in whether the
    space-heat split is supplied — red without it, green with it. The pass is a
    property of the netting and not of anything else that moved this week.
    """
    stripped = dataclasses.replace(population, space_heat_grids=())
    cell = fgl.evaluate_two_level(stripped).cell("L1.2_day_to_day_shape_correlation")
    assert cell.verdict is fgl.Verdict.FAIL, cell.note
    assert cell.homes_violating and cell.homes_violating > 0
    assert cell.worst_home in {
        population.homes[k] for k in _homes_with_heat_on_the_judged_meter(population)
    }, "the homes the whole-meter reading fails are the electrically heated ones"


def test_the_netting_CHANGES_NOTHING_for_a_home_heated_off_the_judged_meter(population):
    """The blast radius, measured rather than asserted. A gas-heated home's L1.2 is
    BIT-IDENTICAL before and after, because its space-heat stream is a run of
    zeros — so this change cannot have moved the 190-of-200 majority of the
    population in either direction."""
    affected = set(_homes_with_heat_on_the_judged_meter(population))
    moved = 0
    for k, grid in enumerate(population.grids):
        whole = fgl.day_to_day_shape_correlation([list(d) for d in grid])
        net = fgl.day_to_day_shape_correlation(
            fgl.meter_net_of_machines(
                [list(d) for d in grid],
                [list(d) for d in population.space_heat_grids[k]],
            )
        )
        if k in affected:
            moved += whole != net
        else:
            assert net == whole, f"{population.homes[k]} moved without carrying heat"
    assert moved == len(affected), "every affected home should actually have moved"


def test_the_netting_REFUSES_a_stream_that_is_not_a_COMPONENT_of_the_meter(population):
    """R15 on the guard itself. The split is a claim, and every way of making it a
    false claim is refused rather than netted through — an unchecked subtraction
    would let a generator declare its behaviour to be heat and walk out of the
    cell."""
    meter = [list(day) for day in population.grids[0]]
    ok = fgl.meter_net_of_machines(meter, [[0.0] * len(d) for d in meter])
    assert ok == meter, "the unmutated call must pass, or this proves nothing"

    with pytest.raises(fgl.InsufficientEvidence):
        fgl.meter_net_of_machines(meter, [[v * 2 for v in d] for d in meter])
    with pytest.raises(fgl.InsufficientEvidence):
        fgl.meter_net_of_machines(meter, [[-1e-6] + [0.0] * (len(d) - 1) for d in meter])
    with pytest.raises(fgl.NonFiniteTrace):
        fgl.meter_net_of_machines(
            meter, [[float("nan")] + [0.0] * (len(d) - 1) for d in meter]
        )
    with pytest.raises(fgl.InsufficientEvidence):
        fgl.meter_net_of_machines(meter, [[0.0] * len(d) for d in meter][:-1])
    with pytest.raises(fgl.InsufficientEvidence):
        fgl.meter_net_of_machines(meter, [[0.0] * (len(d) - 1) for d in meter])


def test_the_NETTED_OUT_quantity_is_reported_and_is_ABOVE_the_band_it_left(population_result):
    """The exclusion is not a quiet one. What was taken out of L1.2 is measured on
    the homes it was taken from, reported UNVALIDATED, and — the substantive point
    — sits ABOVE the 0.85 band it was removed from.

    That number is the finding, stated rather than hidden: the model's thermostat
    really does repeat at a level a household never would, on gas and electric
    homes alike. Judging a household band against it was the defect.
    """
    cell = population_result.cell("L1.2h_heating_shape_repeatability")
    assert cell.verdict is fgl.Verdict.UNVALIDATED
    assert cell.band.anchor is fgl.AnchorStatus.NEED and cell.band.threshold is None
    assert math.isfinite(cell.value), "an unvalidated cell still reports its value"
    assert cell.value > fgl.BANDS["L1.2_day_to_day_shape_correlation"].threshold, (
        "if the netted-out stream were INSIDE the household band, netting it out "
        "would have been unnecessary and this fix would be unjustified: " + cell.note
    )


def test_the_netted_out_cell_says_NOTHING_WAS_NETTED_rather_than_going_quiet(shipped_result):
    """The shipped path supplies no split, so nothing is netted anywhere and this
    cell has no homes to measure. It must still APPEAR, saying so — a cell that
    vanishes when its subject is absent is indistinguishable from a cell that
    found nothing to report, and NaN-with-a-reason is the honest form."""
    cell = shipped_result.cell("L1.2h_heating_shape_repeatability")
    assert cell.verdict is fgl.Verdict.UNVALIDATED
    assert math.isnan(cell.value)
    assert cell.homes_unjudged == 0
    assert "no home" in cell.note


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


# ---------------------------------------------------------------------------
# H37 — the away signature must survive the heat being on the JUDGED meter.
#
# `away_signature` divides the active window by the base-load window. That is an
# occupancy statistic only while the denominator is a base load, and a heat pump
# does not stop at midnight. These homes are synthetic ON PURPOSE: the defect is
# a property of the arithmetic, so it is named in arithmetic that a reader can
# check by hand, rather than left resting on whichever regimes the panel happens
# to carry today.
# ---------------------------------------------------------------------------

_H37_DAYS = fgl.MIN_DAYS_FOR_TEXTURE + 5


def _h37_behaviour(*, occupied: bool):
    """One day of the household's own load. Occupied: 0.10 kWh per half hour
    overnight against 0.50 in the active window (signature 5.0). Empty: 0.10 flat
    — the fridge, and nothing else (signature 1.0)."""
    if not occupied:
        return [0.10] * 48
    return [
        0.50 if p in fgl.ACTIVE_PERIODS else 0.10 if p in fgl.BASE_LOAD_PERIODS else 0.20
        for p in range(48)
    ]


# Three regimes, each a plumbing fact about where the heating machine lands.
_H37_HEAT = {
    # gas: the heat is on the OTHER meter, so this stream is zeros and every
    # number below must be bit-for-bit what it was before H37 existed.
    "gas": [0.0] * 48,
    # heat pump: a low, continuous draw straight THROUGH the base-load window.
    "heat_pump": [2.0] * 48,
    # resistive panel heaters: on when the room is used, off overnight — the
    # opposite error, and the one that hides a real absence rather than
    # inventing a false one.
    "resistive": [0.0 if p in fgl.BASE_LOAD_PERIODS else 3.0 for p in range(48)],
}


def _h37_home(regime, *, occupied):
    """(meter, space_heat) for a home in `regime` that is either occupied every
    day or empty every day."""
    heat = [list(_H37_HEAT[regime]) for _ in range(_H37_DAYS)]
    behaviour = [_h37_behaviour(occupied=occupied) for _ in range(_H37_DAYS)]
    meter = [[b + h for b, h in zip(bd, hd)] for bd, hd in zip(behaviour, heat)]
    return meter, heat


@pytest.mark.parametrize("regime", ["heat_pump", "resistive"])
def test_H37_the_DEFECT_is_reproduced_on_the_raw_meter(regime):
    """The mutation this repair is proved against, stated as its own test: read on
    the electricity meter, an electrically-heated home's away-day count is a
    reading of its plumbing rather than of its occupancy. A heat pump makes an
    occupied home look empty; panel heaters make an empty one look occupied. Both
    are wrong, and the raw meter cannot tell either of them from the truth."""
    meter, _ = _h37_home(regime, occupied=(regime == "heat_pump"))
    on_the_meter = fgl.trough_statistics(meter).away_signature_days
    truth = 0 if regime == "heat_pump" else _H37_DAYS
    assert on_the_meter != truth, (
        f"{regime}: the meter read {on_the_meter} away days where the truth is "
        f"{truth} — if this now agrees, the defect H37 repairs has gone away and "
        "the netting below is no longer proved by anything"
    )


@pytest.mark.parametrize("regime", ["gas", "heat_pump", "resistive"])
def test_H37_an_OCCUPIED_home_is_not_called_empty_in_any_regime(regime):
    """The direction the repair is FOR. A household that never left must read zero
    away days whatever its heating machine is, and after netting it does."""
    meter, heat = _h37_home(regime, occupied=True)
    assert fgl.trough_statistics(meter, machines=heat).away_signature_days == 0


@pytest.mark.parametrize("regime", ["gas", "heat_pump", "resistive"])
def test_H37_a_genuinely_EMPTY_home_is_still_detected_in_any_regime(regime):
    """The FAIL-CLOSED direction, which the obvious netting could have broken. An
    empty house must still be detectable after the heating machine is taken out —
    and it is, because what netting leaves behind is the fridge, which is exactly
    the load the 1.30 cutoff was always about. On the resistive home the netting
    RECOVERS an absence the meter had hidden, which is the same result the live
    panel gives (E15, recall 0.75 -> 1.00)."""
    meter, heat = _h37_home(regime, occupied=False)
    stats = fgl.trough_statistics(meter, machines=heat)
    assert stats.away_signature_days == _H37_DAYS
    assert fgl.BANDS["L1.3_away_days_per_year"].judge(stats.away_days_per_year) is fgl.Verdict.PASS


def test_H37_a_generator_with_no_absences_at_all_still_FAILS_the_band():
    """The other half of R15: the repair must not have bought its precision by
    making the band unfailable. A home that is occupied every day fails L1.3 in
    every regime, netted."""
    for regime in _H37_HEAT:
        meter, heat = _h37_home(regime, occupied=True)
        stats = fgl.trough_statistics(meter, machines=heat)
        assert fgl.BANDS["L1.3_away_days_per_year"].judge(
            stats.away_days_per_year
        ) is fgl.Verdict.FAIL, regime


def test_H37_no_split_supplied_judges_the_WHOLE_meter_fail_closed():
    """`machines=None` is the strict reading, not a lenient one: it is exactly
    the pre-H37 behaviour, so a generator that supplies no split buys nothing by
    staying silent."""
    meter, _ = _h37_home("heat_pump", occupied=True)
    assert (
        fgl.trough_statistics(meter, machines=None).away_signature_days
        == fgl.trough_statistics(meter).away_signature_days
        == _H37_DAYS
    )


def test_H37_a_gas_home_is_bit_for_bit_what_it_was(generated, traces):
    """The netting must be a no-op where the heat is on the other meter — zeros
    subtract to nothing. Asserted on the LIVE generator rather than the synthetic
    homes, so a change to the netting cannot pass here while moving the panel."""
    for k, grid in enumerate(_grids(generated)):
        heat = _machines_of(generated, k)
        if any(any(day) for day in heat):
            continue
        assert (
            fgl.trough_statistics(grid, machines=heat)
            == fgl.trough_statistics(grid)
        ), generated.homes[k]


def test_H37_the_L1_3_CELL_reads_the_netted_stream_not_the_meter(generated):
    """The statistic being repairable is not the same as the ledger reading the
    repaired one. The cell must carry the netting AND say so — an exclusion nobody
    can see in the note is how a netting becomes a quiet one."""
    cell = fgl.evaluate_two_level(generated).cell("L1.3_away_days_per_year")
    assert "net of space AND water heat" in cell.note
    netted = [
        fgl.trough_statistics(
            g, machines=_machines_of(generated, k)
        ).away_days_per_year
        for k, g in enumerate(_grids(generated))
    ]
    assert cell.worst_value == pytest.approx(min(netted))


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
    """The raw statistic still MOVES under the mutation — that was never the
    problem — and the cell that JUDGES it fires."""
    grids = _grids(generated)
    before = fgl.timing_diversity(grids)
    after = fgl.timing_diversity(_collapse_evening_peak(grids))
    assert after == pytest.approx(0.0, abs=1e-12), "one national constant is an exact point mass"
    assert before > 0.0
    ratio = fgl._timing_ratio_or_zero(_collapse_evening_peak(grids))
    assert ratio == 0.0, "a degenerate re-deal null is scored a violation, never skipped"
    assert fgl.BANDS["L2.3n_timing_diversity_null_ratio"].judge(ratio) is fgl.Verdict.FAIL


# ---------------------------------------------------------------------------
# L2.3n — THE REPAIR, PROVEN AT EVERY WINDOW IT IS APPLIED AT (atom H34)
# ---------------------------------------------------------------------------
#
# The H33 sweep found the 0.5-half-hour floor sitting INSIDE its own null at 40,
# 60 and 90 days and clearing it at 120 by 3.8% of the null's spread. The
# disposition was repair-the-STATISTIC, never lower-the-floor and never
# repair-the-window (R12) — so the proof owed here is a proof AT EVERY WINDOW,
# because a control proven only at the window someone happened to run is the
# exact defect being repaired.

#: The windows the band must hold at, spanning the shortest run anyone plausibly
#: judges on up to the applied `couple_fabric` window (10 homes x 120 days).
L2_3N_WINDOWS = (40, 60, 90, 120)

#: Independent structureless populations per window. Not a power calculation — it
#: is the number at which a 5%-alpha test's pass rate is distinguishable from the
#: floor's 68% within a test-suite time budget.
L2_3N_DEALS = 20

#: A one-sided permutation test at alpha = 0.05 passes a structureless population
#: about 1 time in 20 BY CONSTRUCTION — that is its size, not a fail-open. The
#: ceiling here is 5x that nominal rate, fixed from alpha BEFORE any of the rates
#: below were measured, and generous for 20 draws. It is not a target: nothing in
#: the band may ever be tuned to sit under it (R12).
L2_3N_MAX_STRUCTURELESS_PASS_RATE = 0.25

#: The floor this cell replaced, quoted so the comparison below is against the
#: real superseded control rather than a straw one. Gone from `BANDS` on purpose.
SUPERSEDED_L2_3_FLOOR = 0.5


def _timing_less(grids, seed):
    """A population with no home-level timing: pool every day and deal them back.

    Deliberately NOT `fgl.deal_preserving_counts`, though it is the same
    operation. The statistic under test builds its null with that function, and a
    test that manufactured its structureless population with the subject's own
    helper would be checking the helper against itself. Four lines of independent
    shuffle costs nothing and removes the question.
    """
    rng = random.Random(seed)
    pool = [list(day) for home in grids for day in home]
    rng.shuffle(pool)
    out, cursor = [], 0
    for home in grids:
        out.append(pool[cursor:cursor + len(home)])
        cursor += len(home)
    return out


def _l2_3n_rates(grids, window):
    """(floor pass rate, ratio pass rate) on structureless populations at `window`
    days — the two controls judged on identical draws."""
    truncated = [home[:window] for home in grids]
    floor_passes = ratio_passes = 0
    for k in range(L2_3N_DEALS):
        dealt = _timing_less(truncated, seed=9000 + k)
        if fgl.timing_diversity(dealt) >= SUPERSEDED_L2_3_FLOOR:
            floor_passes += 1
        # The null seed varies with the draw too. Sharing one seed across draws
        # correlates the tests through their common permutation set and inflates
        # the measured pass rate — observed while deriving these numbers.
        if fgl.timing_diversity_vs_own_null(dealt, seed=400000 + k * 7919).ratio >= 1.0:
            ratio_passes += 1
    return floor_passes / L2_3N_DEALS, ratio_passes / L2_3N_DEALS


def test_L2_3n_a_REAL_population_passes_at_EVERY_window(generated):
    """Direction one of R15. The band must not simply fail everything — and it
    must not need a long run to say so.

    Measured 2026-08-10 on this panel: 1.35 / 1.47 / 1.67 / 2.07 at 40 / 60 / 90 /
    120 days. The ratio RISES with the window (the null shrinks while the real
    spread does not), which is the diagnostic that the spread is a real property
    of these homes and not the sampling term the raw statistic carried.
    """
    grids = _grids(generated)
    ratios = {}
    for window in L2_3N_WINDOWS:
        ratios[window] = fgl.timing_diversity_vs_own_null([h[:window] for h in grids]).ratio
    for window, value in ratios.items():
        assert value >= 1.0, (
            f"the real panel must beat its own re-deal null at {window} days, "
            f"got {value:.3f} — all windows: {ratios}"
        )
    assert ratios[120] > ratios[40], (
        "the ratio must GROW with the window as the null shrinks; if it does not, "
        f"the statistic still carries its null's sampling term: {ratios}"
    )


def test_L2_3n_a_TIMING_LESS_population_FAILS_at_EVERY_window(generated):
    """Direction two of R15, and the finding this atom was minted from.

    Deal one population's days out at random and no home has an evening timing of
    its own. The superseded 0.5 floor cleared that population most of the time at
    a short window and rarely at a long one — a control whose fail-open rate is a
    function of how long anyone watched. The ratio's is flat at its own alpha.
    """
    grids = _grids(generated)
    measured = {w: _l2_3n_rates(grids, w) for w in L2_3N_WINDOWS}
    for window, (floor_rate, ratio_rate) in measured.items():
        assert ratio_rate <= L2_3N_MAX_STRUCTURELESS_PASS_RATE, (
            f"a structureless population cleared L2.3n {ratio_rate:.0%} of the time "
            f"at {window} days, above the {L2_3N_MAX_STRUCTURELESS_PASS_RATE:.0%} "
            f"ceiling alpha allows — all windows: {measured}"
        )
        assert ratio_rate <= floor_rate, (
            f"at {window} days the repair is WORSE than the floor it replaced "
            f"({ratio_rate:.0%} vs {floor_rate:.0%}) — all windows: {measured}"
        )
    short, long = measured[40][0], measured[120][0]
    assert short > long, (
        "THE FINDING ITSELF must stay reproducible: the superseded floor's "
        f"fail-open rate has to be worse at 40 days ({short:.0%}) than at 120 "
        f"({long:.0%}). If it is not, this whole repair rests on a stale "
        f"measurement: {measured}"
    )
    assert short >= 0.5, (
        f"the floor cleared a timing-less population {short:.0%} of the time at 40 "
        "days when this was measured (68%) — that is what made it fail-open"
    )


def test_L2_3n_the_decision_point_is_the_CONSTRUCTION_not_a_chosen_number():
    """1.0 is where the real spread equals the 95th percentile of its own null.
    That is a property of the ratio, not a figure anyone picked, and it is the
    reason there is nothing here to goal-seek (R12)."""
    band = fgl.BANDS["L2.3n_timing_diversity_null_ratio"]
    assert band.threshold == 1.0 and band.direction == "at_least"
    assert band.anchor is fgl.AnchorStatus.STRUCTURAL, (
        "borrowing an external anchor for a self-referential ratio would be the "
        "tautology this band exists to avoid claiming"
    )
    at_the_point = fgl.DiversityAgainstNull(raw=0.7, null_median=0.4, null_p95=0.7, samples=99)
    assert at_the_point.ratio == 1.0
    assert band.judge(at_the_point.ratio) is fgl.Verdict.PASS
    just_under = fgl.DiversityAgainstNull(raw=0.7, null_median=0.4, null_p95=0.71, samples=99)
    assert band.judge(just_under.ratio) is fgl.Verdict.FAIL


def test_L2_3n_the_null_does_not_INVENT_structure(generated):
    """The R15 pattern that cost the H33 sweep two rebuilt nulls: a null that ADDS
    the movement the statistic measures manufactures defects that are not there.

    A deal is a permutation. Every day survives byte-identical, each home keeps
    its day count, and the pooled multiset is unchanged — so nothing about the
    days themselves can differ between the population and its null.
    """
    grids = [h[:60] for h in _grids(generated)]
    dealt = fgl.deal_preserving_counts(
        [tuple(day) for home in grids for day in home],
        [len(home) for home in grids],
        random.Random(4),
    )
    assert [len(h) for h in dealt] == [len(h) for h in grids]
    assert sorted(d for h in dealt for d in h) == sorted(
        tuple(day) for home in grids for day in home
    )
    with pytest.raises(fgl.InsufficientEvidence):
        fgl.deal_preserving_counts([1, 2, 3], [2, 2], random.Random(1))


def test_L2_3n_a_DEGENERATE_null_RAISES_rather_than_returning_a_verdict(generated):
    """FAIL-CLOSED. When every day peaks in the same half-hour the null is exactly
    zero, and raw/0 would read as a spectacular pass. The statistic raises; the
    CELL decides what a subject with no null scores, and scores it a violation."""
    collapsed = _collapse_evening_peak(_grids(generated))
    with pytest.raises(fgl.DegenerateNull):
        fgl.timing_diversity_vs_own_null(collapsed)
    assert fgl._timing_ratio_or_zero(collapsed) == 0.0


def test_L2_3n_and_the_SWEEPS_null_are_ONE_implementation(generated):
    """One name, one number. The sweep measures L2.3's null with the same deal the
    live cell scores against; a second copy would let the measured null and the
    judged null drift apart silently."""
    from background import band_null_sweep as bns

    population = dataclasses.replace(
        generated, grids=tuple(tuple(tuple(d) for d in h[:60]) for h in generated.grids),
        is_weekend=generated.is_weekend[:60],
        weather_driver=generated.weather_driver[:60],
        space_heat_grids=tuple(tuple(tuple(d) for d in g[:60]) for g in generated.space_heat_grids),
        water_heat_grids=tuple(tuple(tuple(d) for d in g[:60]) for g in generated.water_heat_grids),
    )
    via_sweep = bns._exchangeable_homes_null(population, random.Random(11))
    via_ledger = fgl.deal_preserving_counts(
        [day for home in population.grids for day in home],
        [len(home) for home in population.grids],
        random.Random(11),
    )
    assert [list(h) for h in via_sweep.grids] == [list(h) for h in via_ledger]


def test_the_raw_L2_3_cell_is_REPORTED_and_NOT_JUDGED(generated_result):
    """The floor came out and the record says so. This test is the thing that
    stops it drifting back in unnoticed: a number restored to L2.3 without the
    external panel that would justify one turns this red."""
    band = fgl.BANDS["L2.3_timing_diversity_periods"]
    assert band.threshold is None and band.anchor is fgl.AnchorStatus.NEED
    cell = generated_result.cell("L2.3_timing_diversity_periods")
    assert cell.verdict is fgl.Verdict.UNVALIDATED
    assert cell.value > 0.0, "the statistic is still measured and still reported"
    assert "SERL" in band.anchor_source, (
        "an unjudged cell must name what would close it, or it is a blank with no "
        "route back to a number"
    )


def test_L2_4_scale_spread_FIRES_when_every_home_is_set_to_the_mean(generated):
    annuals = list(generated.annual_kwh)
    before = fgl.scale_spread(annuals)
    mean = sum(annuals) / len(annuals)
    after = fgl.scale_spread([mean] * len(annuals))
    assert after.p90_over_p10 == pytest.approx(1.0)
    assert after.iqr_ratio == pytest.approx(1.0)
    assert before.p90_over_p10 > 1.0
    # AND THE BAND, not merely the statistic. A statistic that moves under its own
    # mutation while the band it feeds stays green is the fail-open this suite
    # exists to refuse, and it is a distinct assertion because until 2026-08-09
    # this cell HAD no band to check.
    band = fgl.BANDS["L2.4_scale_spread_p90_p10"]
    assert band.judge(after.p90_over_p10) is fgl.Verdict.FAIL


def test_the_L2_4_BAND_CAN_PASS_and_is_not_a_control_that_can_only_fail(generated):
    """R15's other direction, and the one a red-on-arrival band most needs.

    L2.4 is red on both generators and on every population this suite measures. A
    band nobody has ever seen pass is indistinguishable from a band that cannot,
    and a control that can only fail wedges whatever it gates instead of measuring
    it.

    The demonstration uses the model's OWN homes, stretched about their median by a
    stated exponent until they span what real households span. Nothing about the
    stretch is realistic — it is arithmetic — and that is the point: the band is a
    statement about dispersion and can be satisfied by dispersion, so failing it is
    a fact about this generator rather than about the threshold.
    """
    band = fgl.BANDS["L2.4_scale_spread_p90_p10"]
    annuals = list(generated.annual_kwh)
    assert band.judge(fgl.scale_spread(annuals).p90_over_p10) is fgl.Verdict.FAIL

    median = statistics.median(annuals)
    stretched = [median * (a / median) ** 3.0 for a in annuals]
    spread = fgl.scale_spread(stretched).p90_over_p10
    assert band.judge(spread) is fgl.Verdict.PASS, (
        f"the anchored spread band must be reachable; stretched population reads "
        f"{spread:.3f} against a floor of {band.threshold:.3f}"
    )
    # The anchor panel itself clears its own floor. Stated as a SANITY check and
    # not as evidence: the floor is the bootstrap P05 of this panel's own ratio, so
    # this comparison is true by construction and proves only that the derivation
    # was not wired up backwards.
    assert band.judge(
        fgl.scale_spread(anchors.panel_daily_kwh()).p90_over_p10
    ) is fgl.Verdict.PASS


def test_the_L1_4_ANCHOR_DOES_NOT_TRANSFER_to_a_120_day_window(population):
    """THE FINDING THAT TOOK AN ANCHOR BACK OUT, pinned (2026-08-09).

    The same Low Carbon London panel that anchored L2.4 also measures L1.4 — real
    households' weekday-vs-weekend total-variation distance, median 0.0724 over
    calendar 2013, bootstrap floor 0.0262. It was wired into the L1.4 band and
    removed again within the hour, because this cell's own named R15 mutation —
    "shuffle day-types" — could not make it fire.

    THE MEASUREMENT IS THE TEST. Relabelling the day-type calendar at random,
    keeping the same weekday/weekend counts, destroys every trace of real
    weekday/weekend structure. Over the samples below not one home lands under the
    floor: the statistic is biased upward at 120 days, where 35 weekend days
    against 85 weekday days leaves two arbitrary subsets of the SAME home differing
    by about as much as a real household's weekday differs from its weekend over a
    full year.

    THE GENERAL FORM, which is why this is pinned rather than written in a comment:
    an anchor is a number AND a window. Both bands came off the same panel by the
    same rule on the same day; L2.4's statistic is a ratio BETWEEN homes and does
    not care how long each was watched, L1.4's is a distance between two subsets of
    ONE home's days and cares enormously. Nothing in an anchor's provenance says
    which kind you have — only the mutation does.
    """
    floor = anchors.LCL_WEEKDAY_WEEKEND_TV_FLOOR
    grids = _grids(population)
    real = list(population.is_weekend)
    weekends = sum(real)
    rnd = random.Random(4242)

    null: list[float] = []
    for _ in range(4):
        chosen = set(rnd.sample(range(len(real)), weekends))
        labels = [i in chosen for i in range(len(real))]
        null.extend(fgl.weekday_weekend_separation(g, labels) for g in grids)

    assert min(null) > floor, (
        "if a randomised day-type calendar can breach the floor, the anchor "
        "transfers after all and this test is the thing to delete"
    )
    assert min(null) > 1.3 * floor, (
        f"the null MINIMUM is {min(null):.4f} against a floor of {floor:.4f} — the "
        "margin is what makes this fail-open rather than marginal"
    )
    assert statistics.median(null) > 2 * floor
    # AND THE BAND MUST STILL BE BLANK. The finding is only worth pinning if the
    # code agrees with it: a later tick that re-wires the anchor without
    # null-correcting the statistic fails here.
    assert fgl.BANDS["L1.4_weekday_weekend_separation"].threshold is None
    assert fgl.RATE_BANDS["L1.4_weekday_weekend_separation"].threshold is None


# ===========================================================================
# §9 L1.4n — THE REPAIR, AND IT IS PROVED ON THE MUTATION THAT DEFEATED L1.4
# ===========================================================================


def _randomised_daytypes(is_weekend, seed):
    """The R15 mutation the spec names for this cell: relabel the day-type
    calendar at random, holding the weekday/weekend COUNTS fixed. Every trace of
    real weekday/weekend structure is destroyed and nothing else is touched."""
    real = list(is_weekend)
    chosen = set(random.Random(seed).sample(range(len(real)), sum(real)))
    return [i in chosen for i in range(len(real))]


def test_L1_4n_FIRES_on_the_randomised_calendar_that_L1_4_COULD_NOT_SEE(population):
    """THE WHOLE REASON THIS CELL EXISTS, stated as the comparison that motivates it.

    The raw L1.4 distance could not fail on a day-type-randomised population — the
    measurement that took its anchor back out. The SAME mutation on the SAME
    population, judged against each home's own permutation null, fails hard. That
    is a repair to the STATISTIC, and it is the only kind of evidence that a
    repair to a statistic can have.
    """
    grids = _grids(population)
    shuffled = _randomised_daytypes(population.is_weekend, 4242)
    band = fgl.BANDS["L1.4n_weekday_weekend_null_ratio"]

    ratios = [
        fgl.weekday_weekend_separation_vs_own_null(g, shuffled).ratio for g in grids
    ]
    violating = sum(1 for r in ratios if band.judge(r) is not fgl.Verdict.PASS)
    rate = violating / len(ratios)

    assert rate > fgl.RATE_BANDS["L1.4n_weekday_weekend_null_ratio"].threshold, (
        f"a day-type-randomised population violates at {rate:.3f}, which must "
        "breach the population tolerance or this cell is fail-open exactly where "
        "L1.4 was"
    )
    assert statistics.median(ratios) < 1.0, (
        f"the median randomised home reads {statistics.median(ratios):.3f} — under "
        "its own null is where a structureless home belongs"
    )
    # AND THE CONTRAST WITH THE RAW CELL, re-measured here rather than quoted, so
    # this stops being true the moment it stops being true.
    raw_floor = anchors.LCL_WEEKDAY_WEEKEND_TV_FLOOR
    raw = [fgl.weekday_weekend_separation(g, shuffled) for g in grids]
    assert min(raw) > raw_floor, (
        "the raw statistic must still clear the LCL floor on this randomised "
        "population — if it no longer does, the finding this cell repairs has "
        "changed and both should be re-derived"
    )


def test_L1_4n_CAN_PASS_and_is_not_a_control_that_can_only_fail(population_result):
    """A band nobody has ever seen pass is indistinguishable from one that cannot.

    The real calendar on the real drawn population passes, and it is the SAME
    population, the SAME homes and the SAME statistic that fail above under a
    randomised calendar — so the pass is evidence about the generator rather than
    about the band being loose.
    """
    cell = next(
        c for c in population_result.cells
        if c.statistic == "L1.4n_weekday_weekend_null_ratio"
    )
    assert cell.verdict is fgl.Verdict.PASS, population_result.summary()
    assert cell.homes_judged == population_result.homes, (
        "every home must be judged — an unjudged home here would be a quiet "
        "exclusion, and the pass would be over a population nobody named"
    )
    assert cell.value < fgl.RATE_BANDS["L1.4n_weekday_weekend_null_ratio"].threshold, (
        f"violation rate {cell.value} must sit inside the tolerance for this to be "
        "a pass anyone can read"
    )


def test_L1_4n_the_NULL_is_window_stable_where_the_RAW_NULL_IS_NOT(population):
    """THE PROPERTY THE REPAIR IS FOR, measured rather than argued.

    L1.4's defect was that its null MOVES with the window, so a floor derived on a
    full year is meaningless at 120 days. Expressed against its own null, a
    structureless population sits below 1.0 at EVERY window — which is what makes
    the band transferable in the way the raw floor was not.

    The magnitude does NOT transfer and this test says so: the real population's
    violation rate walks from 0.183 at 60 days to 0.017 at 120, because the
    per-home test simply has less power on fewer days. That is why the population
    tolerance is set in the empty gap between the two ends rather than at zero.
    """
    grids = _grids(population)
    real = list(population.is_weekend)
    band = fgl.BANDS["L1.4n_weekday_weekend_null_ratio"]
    tolerance = fgl.RATE_BANDS["L1.4n_weekday_weekend_null_ratio"].threshold

    for days in (60, 90, len(real)):
        labels = real[:days]
        shuffled = _randomised_daytypes(labels, 909 + days)

        def _rate(lab, n=days):
            vals = [
                fgl.weekday_weekend_separation_vs_own_null(g[:n], lab).ratio for g in grids
            ]
            return sum(1 for v in vals if band.judge(v) is not fgl.Verdict.PASS) / len(vals)

        null_rate, real_rate = _rate(shuffled), _rate(labels)
        assert null_rate > tolerance, (
            f"at {days} days a structureless population violates at {null_rate:.3f}, "
            f"which must exceed the {tolerance} tolerance at EVERY window or the "
            "band is window-bound after all"
        )
        assert real_rate < tolerance, (
            f"at {days} days the real calendar violates at {real_rate:.3f}, which "
            f"must sit inside the {tolerance} tolerance at every window or a correct "
            "generator is failed for being watched for less time"
        )
        assert null_rate > 2 * real_rate, (
            f"at {days} days the two ends are {real_rate:.3f} and {null_rate:.3f} — "
            "the tolerance is only meaningful while there is a gap to sit in"
        )


def test_L1_4n_FAILS_CLOSED_rather_than_returning_a_spectacular_pass(population):
    """An unavailable check is a FAILED check (R15), and this statistic has one
    fail-open shape all of its own: a degenerate null puts a zero in the
    DENOMINATOR, and an infinite ratio would read as the most structured home ever
    measured. It raises instead."""
    grid = _grids(population)[0]
    identical = [list(grid[0]) for _ in grid]  # every day the same shape
    real = list(population.is_weekend)
    with pytest.raises(fgl.DegenerateNull, match="degenerate"):
        fgl.weekday_weekend_separation_vs_own_null(identical, real)

    # And the ordinary insufficiency guards are inherited, not re-implemented.
    with pytest.raises(fgl.InsufficientEvidence):
        fgl.weekday_weekend_separation_vs_own_null(grid[:10], real[:10])
    with pytest.raises(fgl.InsufficientEvidence, match="two samples"):
        fgl.weekday_weekend_separation_vs_own_null(grid, real, samples=1)


def test_L1_4n_scores_a_DEGENERATE_home_as_a_VIOLATION_not_as_a_pass(population):
    """THE FAIL-OPEN THAT SURVIVED THE FIRST MUTATION PASS, so it is pinned here.

    `_null_ratio_or_zero` decides what a home with no null of its own is worth,
    and the whole suite stayed GREEN when that decision was mutated from 0.0 (a
    violation) to 1.0 (a pass) — i.e. nothing was checking the one line where the
    fail-open lives. A home with identical days is not an awkward edge case in
    this suite: replaying one day's shape all year is a mutation the spec NAMES,
    and a smoothed home lands exactly here. Reading it as a pass would let the
    cell's own named defect walk straight through it.
    """
    grids = _grids(population)
    poisoned = [[list(day) for day in home] for home in grids]
    poisoned[-1] = [list(poisoned[-1][0]) for _ in poisoned[-1]]  # every day identical

    flat_home = population.homes[len(poisoned) - 1]
    assert fgl._null_ratio_or_zero(poisoned[-1], population.is_weekend) == 0.0, (
        "a home whose days are identical has no null to be judged against and must "
        "score zero — if this returns a number, the fixture is not degenerate"
    )

    cell = fgl.evaluate_two_level(fgl.PopulationTraces(
        generator=population.generator,
        homes=population.homes,
        grids=tuple(tuple(tuple(day) for day in home) for home in poisoned),
        is_weekend=population.is_weekend,
        annual_kwh=population.annual_kwh,
        weather_driver=population.weather_driver,
        pc1_is_an_input=population.pc1_is_an_input,
    )).cell("L1.4n_weekday_weekend_null_ratio")

    assert cell.homes_violating >= 1, cell.note
    assert cell.worst_value == 0.0, (
        f"the flat home must be the worst home in the cell, not merely counted: "
        f"{cell.note}"
    )
    assert flat_home in cell.note, (
        f"a violating home the cell cannot NAME is a number nobody can act on: {cell.note}"
    )


def test_L1_4n_is_DETERMINISTIC_so_a_threshold_cannot_be_moved_by_reseeding(population):
    """C-S2. The null is a random object; a band judged against a re-rolled null
    every run is a band that moves on its own."""
    grid = _grids(population)[0]
    real = list(population.is_weekend)
    a = fgl.weekday_weekend_separation_vs_own_null(grid, real)
    b = fgl.weekday_weekend_separation_vs_own_null(grid, real)
    assert a == b
    # The raw separation is a property of the data and must NOT depend on the seed;
    # only the null may. This is what stops a reseed from moving the numerator too.
    c = fgl.weekday_weekend_separation_vs_own_null(grid, real, seed=1)
    assert c.raw == a.raw
    assert c.null_p95 != a.null_p95 or c.null_median != a.null_median
    assert a.raw == pytest.approx(fgl.weekday_weekend_separation(grid, real), rel=1e-9), (
        "L1.4n's numerator must be the SAME measurement L1.4 reports, or the two "
        "cells are two statistics wearing one name"
    )


# ===========================================================================
# §9b L1.1n — THE FLOOR'S NULL IS A PROPERTY OF THE HOME, AND THIS REMOVES IT
#
# H39. `half_hourly_texture` reads part of the 0.15 floor off a home's own mean
# diurnal profile, which moves between adjacent half-hours whether or not the
# generator ever fired an appliance. That reading is not zero and is not the same
# for every home, so ONE floor asks a different question of each — and the
# band-null sweep sees it from outside as a margin (0.0550) inside the null's own
# spread across homes (0.0558).
#
# The repair is a companion statistic whose null is the SAME NUMBER for every
# home: each home's texture over its OWN flat counterfactual. The floor does not
# move (R12) — it keeps the MAGNITUDE question it has a domain anchor for, and
# L1.1n takes the question the floor's own anchor text says it is really for.
# ===========================================================================


def _rescaled_base_shape(behavioural):
    """THE MUTATION, and it is the generator L1.1's own rationale names: ONE base
    shape, rescaled per home per day, with no day-to-day behaviour in it at all.

    The base shape is a REAL DAY from a REAL home rather than a smooth
    construction, which is the whole point — the floor's rationale assumes the
    fake shape is a national AVERAGE ("the texture of a hundred thousand homes
    already summed") and therefore smooth. A generator that rescales one real
    day is a strictly more convincing fake and the floor cannot see it.
    """
    base = list(behavioural[0][0])
    total = sum(base)
    unit = [v / total for v in base]
    return [[[v * sum(day) for v in unit] for day in home] for home in behavioural]


def _behavioural_streams(population):
    """The load set BOTH L1.1 cells are read on, net of both machines (H38)."""
    return [
        fgl.meter_net_of_machines(
            [list(day) for day in home],
            fgl.machine_draw(
                [list(d) for d in population.space_heat_grids[k]]
                if population.space_heat_grids else None,
                [list(d) for d in population.water_heat_grids[k]]
                if population.water_heat_grids else None,
            ),
        )
        for k, home in enumerate(population.grids)
    ]


def test_L1_1n_FIRES_on_the_RESCALED_REAL_DAY_that_the_FLOOR_CANNOT_SEE(population):
    """THE WHOLE REASON THIS CELL EXISTS, stated as the comparison that motivates it.

    A generator that rescales ONE REAL DAY as every home's base shape has zero
    day-to-day behaviour, which is precisely what L1.1 certifies — and it clears
    the 0.15 floor at EVERY home, because a real day is textured and rescaling it
    does not smooth it. Judged against each home's own flat counterfactual the
    same population reads exactly 1.0 and fails at every home.

    SAID OUT LOUD, because overselling this would be the easy mistake: L1.2 and
    L1.5 also fail this generator, so the CELL as a whole was never blind to it.
    The claim is about L1.1's own null, which is the thing the band-null sweep
    measures band by band and the thing H39 is about.
    """
    behavioural = _behavioural_streams(population)
    faked = _rescaled_base_shape(behavioural)
    floor = fgl.BANDS[fgl.TEXTURE_STATISTIC]
    ratio_band = fgl.BANDS[fgl.TEXTURE_NULL_RATIO_STATISTIC]

    texture = [fgl.half_hourly_texture(h) for h in faked]
    ratios = [fgl._texture_ratio_or_zero(h) for h in faked]

    assert all(floor.judge(t) is fgl.Verdict.PASS for t in texture), (
        f"the floor must PASS this generator for the finding to be real — it "
        f"reads {min(texture):.4f}-{max(texture):.4f} against 0.15"
    )
    assert all(ratio_band.judge(r) is not fgl.Verdict.PASS for r in ratios), (
        f"L1.1n must fail every home of a generator with no behaviour in it; "
        f"worst ratio {max(ratios):.17g}"
    )
    assert max(ratios) == pytest.approx(1.0, abs=1e-9), (
        "a flat generator must read EXACTLY 1.0 — anything else means the "
        "counterfactual is no longer the same arithmetic as the reading"
    )
    # ...and the honest half.
    assert any(
        fgl.day_to_day_shape_correlation(h) > fgl.BANDS[
            "L1.2_day_to_day_shape_correlation"].threshold for h in faked
    ), "L1.2 is expected to catch this too; if it stopped, that is a bigger finding"


def test_L1_1n_CAN_PASS_and_is_not_a_control_that_can_only_fail(population_result):
    """A band nobody has ever seen pass is indistinguishable from one that cannot.

    The real drawn population passes at every home, and it is the SAME homes and
    the SAME statistic that fail above under a rescaled base shape — so the pass
    is evidence about the generator rather than about the band being loose.
    """
    cell = next(
        c for c in population_result.cells
        if c.statistic == fgl.TEXTURE_NULL_RATIO_STATISTIC
    )
    assert cell.homes_violating == 0, population_result.summary()
    assert cell.homes_judged == population_result.homes, (
        "every home must be judged — an unjudged home here would be a quiet "
        "exclusion, and the pass would be over a population nobody named"
    )
    assert cell.worst_value > 2.0, (
        f"the worst real home reads {cell.worst_value:.3f} times its own flat "
        "counterfactual; if that ever approached 1.0 the pass would be a squeak "
        "rather than a verdict"
    )


def test_the_NULL_is_ONE_NUMBER_for_every_home_where_the_FLOORs_is_NOT(population):
    """THE PROPERTY THE REPAIR IS FOR, measured rather than argued — and it is the
    H39 finding restated as an assertion.

    Under the flat counterfactual the RAW statistic reads a different number for
    every home, because it is reading that home's own mean profile. The RATIO
    reads 1.0 for all of them. That is what makes one floor comparable across
    homes and the other not, and it is why the sweep's margin-inside-its-own-
    spread verdict on L1.1 cannot be repaired by moving 0.15 in either direction.
    """
    behavioural = _behavioural_streams(population)
    flat = [fgl.flatten_to_mean_profile(h) for h in behavioural]

    raw_nulls = [fgl.half_hourly_texture(h) for h in flat]
    ratio_nulls = [fgl._texture_ratio_or_zero(h) for h in flat]

    assert max(raw_nulls) / min(raw_nulls) > 2.0, (
        f"the raw null must vary materially across homes for this finding to be "
        f"real — measured {min(raw_nulls):.4f} to {max(raw_nulls):.4f}"
    )
    assert max(ratio_nulls) - min(ratio_nulls) < 1e-9, (
        f"the ratio's null must be one number for every home — measured "
        f"{min(ratio_nulls):.17g} to {max(ratio_nulls):.17g}"
    )
    # The floor's own margin against the biggest of those nulls, quoted so a
    # reader can see how much of 0.15 is already spent before any behaviour.
    assert max(raw_nulls) > 0.5 * fgl.BANDS[fgl.TEXTURE_STATISTIC].threshold, (
        "if no home's flat reading gets anywhere near the floor any more, H39's "
        "premise has changed and this cell should be re-derived, not carried"
    )


def test_the_TOLERANCE_is_LOAD_BEARING_and_at_least_1_0_would_be_FAIL_OPEN(population):
    """R15 ON THE CONSTANT ITSELF. `TEXTURE_NULL_RATIO_TOLERANCE` looks like a
    rounding-error nicety and is not: the flat counterfactual is the same
    arithmetic as the reading in a different order, so a structureless home lands
    at 1.0 plus or minus a few units in the last place — and roughly a third of
    them land ABOVE. A band written `at_least 1.0` would pass them.

    The mutation is the removal of the tolerance, and the assertion is that the
    control stops firing without it.
    """
    behavioural = _behavioural_streams(population)
    flat = [fgl.flatten_to_mean_profile(h) for h in behavioural]
    ratios = [fgl._texture_ratio_or_zero(h) for h in flat]

    passes_without_tolerance = sum(1 for r in ratios if r >= 1.0)
    assert passes_without_tolerance > 0, (
        "the tolerance is not load-bearing on this population — if float error "
        "never lands above 1.0 here, say so and delete the constant rather than "
        "carrying a guard nobody can show firing"
    )
    band = fgl.BANDS[fgl.TEXTURE_NULL_RATIO_STATISTIC]
    assert all(band.judge(r) is not fgl.Verdict.PASS for r in ratios), (
        "with the tolerance in place NO structureless home may pass"
    )
    # And the tolerance is nowhere near a real home: nine orders below the
    # smallest real margin, so it can never be doing threshold work.
    real = [fgl._texture_ratio_or_zero(h) for h in behavioural]
    assert min(real) - 1.0 > 1e6 * fgl.TEXTURE_NULL_RATIO_TOLERANCE, (
        f"the smallest real margin is {min(real) - 1.0:.4f}; a tolerance that "
        "approached it would have become a threshold"
    )


def test_the_FLAT_COUNTERFACTUAL_is_IDEMPOTENT_which_is_what_makes_1_0_EXACT(population):
    """The construction claim the decision point rests on, asserted rather than
    argued: flattening an already-flat home returns the same home.

    If it did not, the null would be some other number near 1.0 that nobody had
    derived, and the band would need a threshold rather than a construction."""
    behavioural = _behavioural_streams(population)
    for home in behavioural:
        once = fgl.flatten_to_mean_profile(home)
        twice = fgl.flatten_to_mean_profile(once)
        for a, b in zip(once, twice):
            assert a == pytest.approx(b, rel=1e-12, abs=1e-15)


def test_the_FLATTENING_is_the_LEDGERS_and_the_SWEEP_keeps_no_second_copy():
    """ONE null, not a measured one and a judged one free to drift apart.

    The sweep measures L1.1's null with the same counterfactual L1.1n divides by.
    Two implementations would let the sweep report a clean margin for a statistic
    the ledger does not apply — R15's first killer pattern, one module over."""
    from background import band_null_sweep as bns

    days = [[float((i * 7 + p) % 5) + 1.0 for p in range(48)] for i in range(10)]
    assert bns._flatten_home(days) == fgl.flatten_to_mean_profile(days)

    # Behavioural equality is not enough on its own — an inlined copy satisfies it
    # today and drifts tomorrow. The source must actually CALL the ledger, and the
    # check is on the AST rather than on the text: this module's own docstring
    # names the function, and a substring match would have passed a copy that
    # merely mentioned it. Prose is not a call — the same reason
    # `band_null_sweep.unswept_band_sources` matches band declarations on the call
    # node instead of on the file's text.
    import ast
    import inspect
    import textwrap

    tree = ast.parse(textwrap.dedent(inspect.getsource(bns._flatten_home)))
    called = {
        node.func.attr if isinstance(node.func, ast.Attribute) else
        node.func.id if isinstance(node.func, ast.Name) else None
        for node in ast.walk(tree) if isinstance(node, ast.Call)
    }
    assert "flatten_to_mean_profile" in called, (
        "the sweep must CALL the ledger's flattening, not merely agree with it — "
        f"calls found: {sorted(c for c in called if c)}"
    )


def test_L1_1n_FAILS_CLOSED_rather_than_returning_a_spectacular_pass():
    """A home whose mean profile is a CONSTANT has no null: its flat
    counterfactual has no half-hourly movement, so the ratio would be a reading
    over zero. It raises. An unavailable check is a failed check (R15)."""
    flat_profile = [[1.0] * 48 for _ in range(40)]
    with pytest.raises(fgl.DegenerateNull):
        fgl.half_hourly_texture_vs_own_null(flat_profile)
    # ...and the raw statistic on the same home is a perfectly ordinary number,
    # which is exactly why the degenerate case has to be caught here.
    assert fgl.half_hourly_texture(flat_profile) == 0.0


def test_L1_1n_scores_a_DEGENERATE_home_as_a_VIOLATION_not_as_a_pass():
    """And the cell's decision about that home is a VIOLATION, never a skip.

    A constant mean profile is what a rescaled base shape looks like when the
    base shape is flat — the generator this cell is written for. Skipping it
    would be fail-open on precisely that population."""
    flat_profile = [[1.0] * 48 for _ in range(40)]
    assert fgl._texture_ratio_or_zero(flat_profile) == 0.0
    band = fgl.BANDS[fgl.TEXTURE_NULL_RATIO_STATISTIC]
    assert band.judge(0.0) is not fgl.Verdict.PASS


def test_L1_1n_NETS_THE_MACHINE_BEFORE_it_flattens(population):
    """The order matters and getting it wrong reintroduces H36's defect.

    Flattening the METER and then subtracting the real machine leaves
    `flat_meter - real_heat`, which carries the machine's whole day-to-day
    structure with a minus sign in front — the null would be INVENTING the
    behaviour the band looks for. The shipped call nets first; this pins that the
    two orders actually differ on a home with heat on the judged meter, so the
    pin is not vacuous.
    """
    k = next(
        (i for i in range(len(population.grids))
         if population.space_heat_grids
         and any(any(d) for d in population.space_heat_grids[i])),
        None,
    )
    if k is None:
        pytest.skip("no home in this population carries heat on the judged meter")
    meter = [list(d) for d in population.grids[k]]
    heat = fgl.machine_draw(
        [list(d) for d in population.space_heat_grids[k]],
        [list(d) for d in population.water_heat_grids[k]]
        if population.water_heat_grids else None,
    )
    net_then_flat = fgl.half_hourly_texture(
        fgl.flatten_to_mean_profile(fgl.meter_net_of_machines(meter, heat))
    )
    flat_then_net = fgl.half_hourly_texture(
        fgl.meter_net_of_machines(fgl.flatten_to_mean_profile(meter), heat)
    )
    assert net_then_flat != pytest.approx(flat_then_net, rel=1e-6), (
        "if the two orders agree on this home the pin is vacuous and the wrong "
        "one could be shipped unnoticed"
    )
    shipped = fgl.half_hourly_texture_vs_own_null(meter, machines=heat)
    assert shipped.null == pytest.approx(net_then_flat, rel=1e-12)


def test_the_MINTS_INFERRED_MECHANISM_was_REFUTED_by_measurement(population):
    """THE CORRECTION, recorded as a test rather than as a sentence.

    H39 was minted with an `inferred`-labelled mechanism: "the p95 is set by
    whichever home has the peakiest mean profile". It is not. Measured across the
    live panel the flat null is essentially UNCORRELATED with the mean profile's
    peak-to-mean (-0.05), and sharpening a profile's peak does not raise the
    reading at all — texture is period-to-period ROUGHNESS, and a tall smooth
    peak is still smooth between adjacent half-hours. The defect is real and the
    repair is unchanged; the stated cause was wrong, and a wrong cause left in
    place is how the next repair gets aimed at the wrong thing.
    """
    behavioural = _behavioural_streams(population)
    flat = [fgl.flatten_to_mean_profile(h) for h in behavioural]
    nulls = [fgl.half_hourly_texture(h) for h in flat]
    peakiness = [
        fgl.peak_to_mean([
            sum(day[p] for day in home) / len(home) for p in range(fgl.PERIODS_PER_DAY)
        ])
        for home in flat
    ]
    n = len(nulls)
    mn, mp = sum(nulls) / n, sum(peakiness) / n
    cov = sum((a - mn) * (b - mp) for a, b in zip(nulls, peakiness))
    denom = (
        sum((a - mn) ** 2 for a in nulls) * sum((b - mp) ** 2 for b in peakiness)
    ) ** 0.5
    r = cov / denom
    assert abs(r) < 0.4, (
        f"peak-to-mean now explains the null at r={r:+.3f}. The mint's inferred "
        "mechanism was refuted at r=-0.05 on 2026-08-10; if it has come back, "
        "re-open the diagnosis rather than trusting this docstring"
    )


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
    assert "L2.3n_timing_diversity_null_ratio" in failed, (
        "collapsing the per-home routine MUST re-open L2.3n — if it does not, the "
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
    assert two_level["is_red"] is (
        bool(two_level["failed"]) or bool(two_level["inconclusive"])
    )
    assert set(two_level["failed"]) == {
        s for s, c in two_level["cells"].items() if c["verdict"] == fgl.Verdict.FAIL.value
    }
    assert two_level["inconclusive"] == []
    assert two_level["failed_levels"] == sorted(
        {c.level for c in population_result.failed}
    )
    # A READER MUST BE ABLE TO SIZE THE RESULT, which is the whole reason the
    # population fields are on the wire: "0 of 60 homes", not "green". The rate
    # cells carry their denominator whatever the verdict — a green cell with no n
    # behind it is exactly the fail-open this suite spent a day removing.
    assert two_level["homes"] == fgl.MIN_HOMES_FOR_L1_RATE
    for statistic in ("L1.1_half_hourly_texture",
                      "L1.2_day_to_day_shape_correlation",
                      "L1.3_away_days_per_year", "L1.5_max_multiplicity_share"):
        cell = two_level["cells"][statistic]
        assert cell["homes_judged"] == fgl.MIN_HOMES_FOR_L1_RATE
        assert cell["homes_violating"] == 0
        assert cell["worst_home"]
    # L1.1 JOINED THAT LOOP ON 2026-08-10 (H38): its 1-in-60 breach closed when
    # the water heater came out of the denominator, so the live population no
    # longer has a red RATE cell for this to ride on. The direction that matters —
    # a cell that stops reporting its n the moment it FAILS is a cell whose
    # failure cannot be sized — therefore keeps its own arm below rather than
    # being quietly dropped along with the breach that used to witness it.
    red = dataclasses.replace(
        population_result,
        cells=tuple(
            dataclasses.replace(c, verdict=fgl.Verdict.FAIL, homes_violating=1)
            if c.statistic == fgl.TEXTURE_STATISTIC else c
            for c in population_result.cells
        ),
    )
    red_ledger = tmp_path / "red_fabric_gap.json"
    fgl.write_fabric_gap_entries(
        _observations(epc_bias=1.3, inferred_bias=1.1),
        unit_rate_p_per_kwh=25.0,
        measured_at="2026-08-03T00:00:00Z",
        run_git_commit="deadbeef",
        two_level=red,
        path=red_ledger,
    )
    red_texture = json.loads(red_ledger.read_text())[fgl.GENERATOR_WORLD_ATOM][
        "components"]["two_level"]["cells"]["L1.1_half_hourly_texture"]
    assert red_texture["homes_judged"] == fgl.MIN_HOMES_FOR_L1_RATE
    assert red_texture["homes_violating"] == 1
    assert red_texture["worst_home"]
    for statistic in two_level["failed"]:
        # ONLY THE PER-HOME CELLS NAME A HOME. An L2 cell is one number over the
        # whole population and has no worst home to name — this loop asserted
        # otherwise and never noticed, because until L2.4 was anchored on
        # 2026-08-09 every failure this suite had ever produced was an L1 rate
        # cell. A loop that has only ever seen one shape of input is not evidence
        # about the others.
        cell = two_level["cells"][statistic]
        if "homes_judged" in cell:
            assert cell["worst_home"], statistic
        else:
            assert cell["verdict"] == fgl.Verdict.FAIL.value, statistic
            assert math.isfinite(cell["value"]), statistic
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


def _flatten_behaviour(grid, space_heat, weight):
    """MUTATION for L1.1 AS IT IS NOW READ (H36) — blend the BEHAVIOURAL stream
    toward its own flat daily mean and put the heating machine back on top of it,
    unchanged.

    This is the defect the cell exists to catch, stated as a mutation: a generator
    that emits a household with no appliance events, in a house that still has a
    real heating machine in it. Applying the blend to the whole METER instead would
    damage the machine too, which is a different (and easier) defect — and it is
    precisely the conflation that let the old whole-meter reading pass five of six
    electrically heated homes with their behaviour destroyed.

    Every day's behavioural TOTAL is preserved at every weight, so the mutation
    attacks within-day behavioural shape and nothing else, and the meter it
    rebuilds still has the heat stream as a genuine component of it — so
    `meter_net_of_machines` recovers exactly the flattened stream.
    """
    behavioural = fgl.meter_net_of_machines(grid, space_heat)
    flat = [[sum(day) / 48.0] * 48 for day in behavioural]
    mutated = [
        [(1 - weight) * behavioural[d][p] + weight * flat[d][p] for p in range(48)]
        for d in range(len(behavioural))
    ]
    if space_heat is None:
        return mutated
    return [
        [b + h for b, h in zip(mutated_day, heat_day)]
        for mutated_day, heat_day in zip(mutated, space_heat)
    ]


def _critical_behaviour_weight(grid, space_heat, threshold):
    """How much behavioural flattening a home can absorb before it drops under the
    floor. The unit in which two homes in DIFFERENT heating regimes can be compared
    for strictness: both answer "how broken must this home be to fire?"."""
    lo, hi = 0.0, 1.0
    for _ in range(40):
        mid = (lo + hi) / 2
        value = fgl.half_hourly_texture(
            _flatten_behaviour(grid, space_heat, mid), machines=space_heat
        )
        if value < threshold:
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


def test_the_FLOOR_is_ONE_NUMBER_and_no_regime_has_its_own(matched_pair):
    """H36 — the atom's own claim, asserted as a property of the band table
    rather than as a sentence in a docstring.

    What this replaced: three regime-conditioned floors, each `0.15 x behavioural
    share` at ONE published typical home (Ofgem TDCV medium against a DESNZ/ESC
    median-SPFH4 heat pump = 47.0% behavioural, resistive = 24.2%). Those bands
    were derived correctly and were still wrong, because the panel's homes are not
    that home: measured behavioural shares run 0.30-0.74, so one fixed number was
    25% too strict for the largest electrically heated home and fail-open for the
    smallest. There is now ONE judged texture floor, and the only other entry is
    the NEED band for a home whose behavioural stream cannot be recovered at all.

    WIDENED, NOT WEAKENED, BY H39 (2026-08-10). `L1.1n` is a second judged L1.1
    band and it is deliberately NOT a second floor: it carries no absolute
    threshold at all, its decision point is 1.0 by construction, and — the
    property this test is really about — it is not routed by
    `texture_band_for`, so no heating regime can acquire one of its own. The
    assertion is therefore on the shape of each judged band rather than on there
    being exactly one of them: an absolute kWh-ratio floor may exist ONCE, and
    `texture_band_for` may return only that one.
    """
    texture_bands = {
        name: band for name, band in fgl.BANDS.items()
        if name.startswith("L1.1")
    }
    judged = {n: b for n, b in texture_bands.items() if b.threshold is not None}
    assert set(judged) == {fgl.TEXTURE_STATISTIC, fgl.TEXTURE_NULL_RATIO_STATISTIC}, (
        f"a second judged texture band is back: {sorted(judged)}"
    )
    assert judged[fgl.TEXTURE_STATISTIC].threshold == 0.15
    assert set(texture_bands) - set(judged) == {fgl.NO_BEHAVIOURAL_STREAM_BAND}

    # THE HALF THAT KEEPS THE TEETH: exactly one band is an absolute floor on the
    # raw statistic, and the ROUTER can only ever hand a home that one or the NEED
    # band. A regime-conditioned floor coming back through `L1.1n`'s door would
    # have to appear here.
    routed = {
        fgl.texture_band_for(regime, has_split=split).statistic
        for regime in ("gas_boiler_combi", "heat_pump_air", "electric_direct",
                       "electric_storage", "", None)
        for split in (True, False)
    }
    assert routed <= {fgl.TEXTURE_STATISTIC, fgl.NO_BEHAVIOURAL_STREAM_BAND}, routed
    assert fgl.TEXTURE_NULL_RATIO_STATISTIC not in routed, (
        "the null-ratio band must be one band for every home — the moment the "
        "register can route it, it is a per-regime threshold in new coordinates"
    )

    # ...and no derivation of a per-regime threshold survives anywhere, which is
    # the half that would let one grow back quietly.
    for gone in ("heating_texture_threshold", "electric_heat_texture_threshold",
                 "resistive_heat_texture_threshold", "HEATING_REGIMES"):
        assert not hasattr(fgl, gone), f"{gone} is back — so is the defect"


def test_the_floor_does_not_move_with_a_homes_HEAT_SHARE(matched_pair):
    """The property the old design could not have: two homes whose heat is a
    wildly different fraction of their own meter are judged by the SAME number.

    Asserted on the real matched pair — same household, one gas and one heat pump
    — because the claim is about what the band does to homes that differ only in
    how much of the meter their machine occupies.
    """
    heat_pump, gas = matched_pair
    hp_share = sum(sum(d.heating_fuel_kwh) for d in heat_pump.days) / sum(
        sum(d.electricity_kwh) for d in heat_pump.days
    )
    assert hp_share > 0.3, hp_share
    assert sum(sum(d.heating_fuel_kwh) for d in gas.days) == 0.0 or (
        gas.heating_commodity != "electricity"
    )
    assert (
        fgl.texture_band_for("heat_pump_air", has_split=True).threshold
        == fgl.texture_band_for("gas_boiler_combi", has_split=True).threshold
        == 0.15
    )


def test_the_SMOOTH_mutation_is_VALID_AGAIN_once_the_MACHINE_IS_OUT(matched_pair):
    """RE-AIMED BY H36, and the reversal is the point.

    `_smooth` is this file's mutation for L1.1 and it was sound on a gas home and
    INVALID on a heat-pump home: measured on this matched pair it took the gas
    home 0.2417 -> 0.1559 but RAISED the heat-pump home 0.1080 -> 0.1430, because
    averaging the same period across neighbouring days strips day-specific
    appliance noise while leaving the heat pump's repeated diurnal cycle standing.
    A mutation that raises the statistic cannot demonstrate that a band fires, so
    `_flatten_blend` had to be built for the electric bands.

    Read net of space heat the INVERSION is gone but the mutation was still not
    valid: smoothing the space-heat-netted stream RAISED it, 0.2118 -> 0.2312.
    H36 recorded that and said in this test that if it ever reversed, the reason
    was to be RE-STATED and not deleted. It has reversed, so here is the reason.

    THE SECOND MACHINE WAS DOING IT, AND THIS IS EVIDENCE FOR H38 RATHER THAN A
    CONSEQUENCE OF IT. What was left after the space heater came out was a stream
    carrying three enormous 12-minute water-heating draws a day among 48 periods.
    Against that, `_smooth` — a mean across the same period on neighbouring days —
    SMEARS each rare spike across its neighbours, which turns a few huge steps
    into many medium ones and RAISES a median step while lowering the peak. That
    is why the mutation kept inverting; it was reading the machine, not the
    behaviour. Net of BOTH machines it behaves on a heat-pump home exactly as it
    does on a gas home (0.2118 -> 0.1925), which is a statement about the load
    set and not about the mutation: the residual is now a behavioural stream, so
    a mutation that destroys behavioural texture destroys it.
    """
    heat_pump, gas = matched_pair
    hp_grid = [list(day) for day in heat_pump.half_hourly("electricity")]
    gas_grid = [list(day) for day in gas.half_hourly("electricity")]
    hp_heat = _machines_of_trace(heat_pump)

    # The whole-meter reading, pinned so the anomaly this repair removed stays on
    # the record rather than becoming folklore.
    assert fgl.half_hourly_texture(_smooth(hp_grid)) > fgl.half_hourly_texture(hp_grid)

    assert fgl.half_hourly_texture(_smooth(gas_grid)) < fgl.half_hourly_texture(gas_grid)

    # THE MIDDLE READING, pinned so the two-stage story stays checkable rather
    # than becoming a claim about a stream nobody can reconstruct: net of SPACE
    # heat alone the mutation still inverted.
    hp_space_only = fgl.meter_net_of_machines(
        hp_grid, [list(d.heating_fuel_kwh) for d in heat_pump.days]
    )
    assert (
        fgl.half_hourly_texture(_smooth(hp_space_only))
        > fgl.half_hourly_texture(hp_space_only)
    ), "the water heater is what kept _smooth inverted — if not, re-state the reason"

    # AND NET OF BOTH MACHINES IT IS A VALID MUTATION AGAIN, on the load set the
    # cell actually reads. `_flatten_blend` is kept anyway (it attacks the defect
    # this cell is really about), but the electric bands no longer NEED it.
    hp_behavioural = fgl.meter_net_of_machines(hp_grid, hp_heat)
    assert (
        fgl.half_hourly_texture(_smooth(hp_behavioural))
        < fgl.half_hourly_texture(hp_behavioural)
    ), (
        "if this reverses again, the residual has stopped behaving like a "
        "behavioural stream and H38's load set needs re-examining, not this line"
    )


def test_L1_1_FIRES_when_a_real_heat_pump_homes_BEHAVIOUR_is_FLATTENED(matched_pair):
    """R15 — the mutation, on the load set the cell now reads.

    THE MUTATION IS APPLIED TO THE BEHAVIOURAL STREAM AND THE MACHINE IS LEFT
    ALONE, which is both the realistic defect (a generator that produces a
    household with no appliance events, in a house that still has a heat pump in
    it) and the one the previous reading could not see.
    """
    heat_pump, _ = matched_pair
    grid = [list(day) for day in heat_pump.half_hourly("electricity")]
    heat = _machines_of_trace(heat_pump)
    band = fgl.BANDS[fgl.TEXTURE_STATISTIC]

    before = fgl.half_hourly_texture(grid, machines=heat)
    assert band.judge(before) is fgl.Verdict.PASS, (
        f"the unmutated heat-pump trace should clear the floor: {before}"
    )
    # Monotone in the mutation, so "it fired" is not an artefact of one weight.
    values = [
        fgl.half_hourly_texture(_flatten_behaviour(grid, heat, w), machines=heat)
        for w in (0.0, 0.25, 0.5, 0.75, 1.0)
    ]
    assert values == sorted(values, reverse=True), values
    assert band.judge(values[-1]) is fgl.Verdict.FAIL
    assert band.judge(values[2]) is fgl.Verdict.FAIL


def test_the_floor_is_NOT_LOOSER_for_an_ELECTRIC_home_against_the_same_defect(
    matched_pair,
):
    """The charge any change to a control has to answer: that it was moved so the
    thing it judges would stop failing (R12 goal-seek).

    Under the old design the two thresholds sat on different denominators and
    could only be compared through how broken each home had to be before its own
    band fired. That comparison is now direct — one floor, one load set — and the
    unit is kept anyway, because it is the one that answers the charge. Measured:
    the heat-pump home's behaviour must be flattened 0.292 of the way to a flat
    day before the floor fires, the gas home's 0.385.

    THE ELECTRIC HOME'S NUMBER MOVED 0.169 -> 0.292 WHEN H38 TOOK THE WATER
    HEATER OUT (2026-08-10), and that direction is the charge restated rather
    than dodged: this is the netting making the cell EASIER on the home it
    affects. It is defensible only because the gas home is the reference and the
    gas home is untouched — 0.385 under both readings, its water heated by gas —
    and 0.292 is still BELOW it. The electric home remains judged at least as
    harshly as the population whose meters derived the floor, which is the claim.
    It is bounded on both sides here for that reason: an electric home that
    became HARDER to fail than the gas home would be the relaxation this test
    exists to catch, and the old 0.169 was not a virtue but the 18x over-strictness
    measured across the drawn 60 in
    `test_the_WATER_HEATER_netting_is_a_LOAD_SET_repair_and_not_a_LOOSENING`.
    """
    heat_pump, gas = matched_pair
    hp_grid = [list(day) for day in heat_pump.half_hourly("electricity")]
    gas_grid = [list(day) for day in gas.half_hourly("electricity")]
    hp_heat = _machines_of_trace(heat_pump)

    hp_critical = _critical_behaviour_weight(hp_grid, hp_heat, 0.15)
    gas_critical = _critical_behaviour_weight(gas_grid, None, 0.15)

    assert hp_critical == pytest.approx(0.292, abs=0.02)
    assert gas_critical == pytest.approx(0.385, abs=0.02)
    assert hp_critical <= gas_critical, (
        f"the electrically heated home tolerates more damage than the gas home "
        f"before the shared floor fires ({hp_critical:.3f} vs {gas_critical:.3f})"
    )


def test_the_heating_fact_comes_from_the_REGISTER_not_from_the_numbers(matched_pair, weather):
    """R15 TAUTOLOGY, at the place the register still decides something.

    Since H36 the register does not choose a threshold — with a split supplied
    every home meets the same floor. What it still decides is whether a home whose
    generator supplied NO split can be judged at all, and that has to be a
    register fact (what a real supplier holds as `main_heating_fuel`), never a
    reading of the series. Inferring "this looks smooth, so it must be a heat
    pump" from the very statistic being judged would make the cell unfalsifiable
    in the worst way available: a smooth home would talk its way out of being
    judged.

    Proven by holding the NUMBERS fixed and changing only the claim.
    """
    heat_pump, _ = matched_pair
    assert fgl.texture_band_for("gas_boiler_combi").threshold == 0.15
    assert fgl.texture_band_for("heat_pump_air").threshold is None
    # ...and with the split present the claim buys nothing at all.
    assert fgl.texture_band_for("heat_pump_air", has_split=True).threshold == 0.15

    # The builder reads that fact off the trace's register field, which is itself
    # set from the household at generation time.
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
    """The lowest raw texture is not necessarily the home in most trouble. The
    worst cell must be the worst MARGIN against each home's own band, or a gas
    home sitting just under 0.15 is hidden behind a home carrying a smaller
    number for a reason that is not a breach.

    RE-AIMED BY H36 (2026-08-10) and the hazard survived the collapse to one
    floor. It used to be a second THRESHOLD that made raw numbers
    incomparable — a heat-pump home comfortably clearing 0.0705 while reading
    lower than a failing gas home. It is now the UNJUDGED home: a heat-pump home
    whose generator supplied no split has no band at all, so it must not be able
    to become the reported worst cell by carrying the smallest number in the
    population. Same fail-open, one rung along, and the same expression closes
    it."""
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
        f"lower home that is not judged at all: {cell.note}"
    )
    assert "worst home GAS" in cell.note
    assert cell.verdict is fgl.Verdict.FAIL
    assert cell.band.threshold == 0.15
    # And the RATE says how many homes are in trouble, which the worst-of-N form
    # could never do: exactly one, the gas home that was mutated under its band —
    # out of the homes that were JUDGED, the heat-pump home not being one of them.
    assert cell.homes_violating == 1
    assert cell.homes_judged == len(population.homes) - 1
    assert cell.homes_unjudged == 1


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
    were worst-of-N. Under a rate it is not: a rescaled base shape is a property
    of the GENERATOR, so it would be in every home it makes, and one home in sixty
    is a home to diagnose (R4). Both prevalences must therefore be exercised, and
    the warning must be silent at one and loud at the other.

    THE VEHICLE IS NOW SYNTHETIC ON BOTH ARMS, 2026-08-09, AND SAYING SO IS THE
    POINT. Until this tick the low-prevalence arm rode on the live population's
    real 1/60 L1.5 breach; that breach was the away-day clone and it is fixed, so
    L1.5 now passes and there is no live FAIL to borrow. Rebuilding the low arm
    with `dataclasses.replace` keeps the control genuinely under test — every
    field the warning reads is set explicitly and the warning itself is not
    stubbed — but it does mean this test no longer witnesses that the generator
    can produce a low-prevalence breach at all. That witness moved to
    `tests/simulation/test_premise_trace.py::test_the_L1_5_STRUCTURAL_CELL_fires_
    when_the_coupling_is_REMOVED`, which restores the ambient-invariant duty and
    watches the real statistic go back over the real band.
    """
    # THE TEXTURE ARM WAS SYNTHETIC FOR ONE DAY (H36, 2026-08-10) BECAUSE THE LIVE
    # CELL WAS RED, AND IS NOT ANY MORE. The warning only speaks when texture
    # PASSES; H36 opened a 1-in-60 breach that would have made this test silent for
    # the wrong reason, and H38 closed it by taking the water heater out of the
    # denominator. The live cell is asserted GREEN here rather than the assertion
    # being deleted with the breach — if L1.1 goes red again this test must be
    # rewritten and not merely observed to still pass, because a stubbed-PASS arm
    # over a red live cell proves nothing about prevalence.
    assert population_result.cell(fgl.TEXTURE_STATISTIC).verdict is fgl.Verdict.PASS

    def with_structural(value: float, verdict: fgl.Verdict) -> fgl.TwoLevelResult:
        def rewrite(c):
            if c.statistic == fgl.STRUCTURAL_STATISTIC:
                return dataclasses.replace(c, value=value, verdict=verdict)
            if c.statistic == fgl.TEXTURE_STATISTIC:
                return dataclasses.replace(c, value=0.0, verdict=fgl.Verdict.PASS)
            return c

        return dataclasses.replace(
            population_result, cells=tuple(rewrite(c) for c in population_result.cells)
        )

    rare = with_structural(1 / 60, fgl.Verdict.FAIL)
    assert rare.cell(fgl.STRUCTURAL_STATISTIC).value < 0.05
    assert rare.goal_seek_warning() is None, (
        "one home in sixty is a home to diagnose (R4), not evidence that someone "
        "moved a number"
    )

    # ...and the silence is not a broken control: raise the prevalence past the
    # floor on the SAME result object and the warning comes back.
    widespread = with_structural(0.9, fgl.Verdict.FAIL)
    assert widespread.goal_seek_warning() is not None, (
        "with the artefact in 90% of homes this IS the tuning signature and the "
        "warning must fire"
    )


# ===========================================================================
# §8 THE HEATING REGIME IS A LOAD SET, NOT A THRESHOLD (R10 class closure)
#
# `docs/staging/WORKER_FINDING_HEATING_REGIME_CONDITIONING_IS_BINARY_2026-08-09.md`
# and then H36 (`docs/design/BAND_NULL_SWEEP.md`, 2026-08-10). The 2026-08-08 fix
# conditioned the L1.1 band on `is_gas_heated`, a BOOLEAN; the 2026-08-09 fix keyed
# it on delivered efficiency, one published figure per regime. Both were still
# compensating in the THRESHOLD for a statistic read on the wrong LOAD SET, and the
# second one bought a fixed number for every home size — 25% too strict for the
# largest electrically heated home on the panel and fail-open for the smallest.
# The class closes at the load set: one floor, read net of space heat, no published
# efficiency for any machine, and a machine this file has never heard of judged
# like every other one.
# ===========================================================================


REGIME_FIXTURES = (
    ("G1", HeatingSystem.GAS_BOILER_COMBI, False),
    ("HP1", HeatingSystem.HEAT_PUMP_AIR, True),
    ("ST1", HeatingSystem.ELECTRIC_STORAGE, True),
    ("ED1", HeatingSystem.ELECTRIC_DIRECT, True),
    # The machine that used to need its own published SPF and now needs nothing.
    ("GS1", HeatingSystem.HEAT_PUMP_GROUND, True),
)


@pytest.fixture(scope="module")
def matched_regimes(weather):
    """The SAME household with five different machines in it — the panel the
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
    """THE CLASS GUARD (R10), which survives H36 with a smaller register to guard.

    The instance was a storage heater judged by a heat pump's band; the class is a
    heating system reaching L1.1 through a decision nobody made. What the register
    now holds is a PLUMBING fact — is this machine's heat on the judged meter —
    and it is needed for exactly one case: a generator that supplies no split, so
    the behavioural stream cannot be recovered and the home has to be counted
    rather than judged.

    This test fails the moment a new machine appears in the generator's enum with
    no entry here, which is the only reason the register is written out as strings
    rather than derived from the enum: a register derived from the thing it is
    supposed to constrain could not fail.
    """
    for system in HeatingSystem:
        assert system.value in fgl.HEAT_ON_THE_JUDGED_METER, (
            f"{system.value} has no entry in HEAT_ON_THE_JUDGED_METER — it would "
            "fall to the fail-closed default, which is visible, but a NEW machine "
            "deserves a decision rather than a fallback"
        )
        assert isinstance(fgl.HEAT_ON_THE_JUDGED_METER[system.value], bool)


def test_an_UNKNOWN_machine_fails_CLOSED_rather_than_onto_the_floor():
    """The fail-closed direction of that register, asserted rather than assumed.

    A machine nobody has classified might have its heat on this meter. Judging it
    at 0.15 with no split would fail a correct heat pump for owning a thermostat;
    the reading that cannot be wrong in the lenient direction is to count it. With
    a split it needs no classification at all, which is the point of the repair.
    """
    assert fgl.texture_band_for("something_nobody_registered").threshold is None
    assert fgl.texture_band_for(
        "something_nobody_registered", has_split=True
    ).threshold == 0.15


@pytest.mark.parametrize("premise_id, heating, heat_is_on_this_meter", REGIME_FIXTURES)
def test_each_REGIME_is_judged_by_the_SAME_band_on_ITS_OWN_load_set(
    matched_regimes, premise_id, heating, heat_is_on_this_meter
):
    """Every registered machine reaches the SAME floor, on a real trace, once its
    own machine is out of the denominator.

    THE ROW THAT MOVED, AND THEN CLOSED. H36 recorded ED1 — the panel heater —
    reading 0.1313 net of space heat and NOT clearing 0.15, said its whole deficit
    was the water heater still in the stream, and left the row red rather than
    moving the floor or dropping the fixture. H38 took the water heater out and
    ED1 reads 0.2050. That is the prediction H36 wrote down being paid off on a
    row it deliberately left failing, which is worth more than a row that was
    green all along: the diagnosis was made BEFORE the repair and it held.

    EVERY registered regime now clears the same floor on its own load set, so the
    expected verdict is PASS for all of them and there is no per-regime exception
    left in this test. A regime that goes red here is a finding, not a row to
    re-pin.
    """
    trace = matched_regimes[heating]
    grid = [list(d) for d in trace.half_hourly("electricity")]
    heat = _machines_of_trace(trace, on_this_meter=heat_is_on_this_meter)
    assert (trace.heating_commodity == "electricity") is heat_is_on_this_meter

    band = fgl.texture_band_for(heating.value, has_split=True)
    assert band.statistic == fgl.TEXTURE_STATISTIC
    assert band.threshold == 0.15

    texture = fgl.half_hourly_texture(grid, machines=heat)
    assert band.judge(texture) is fgl.Verdict.PASS, (
        f"{premise_id} texture {texture:.4g} against the shared floor 0.15 — if "
        "this row has moved, the H38 record is out of date and the reason has to "
        "be written down, not the assertion changed"
    )
    if heat is not None:
        # ...and the netting is what put it there: the same trace read on the
        # whole meter carries the machine and reads LOWER.
        assert fgl.half_hourly_texture(grid) < texture


@pytest.mark.parametrize("premise_id, heating, heat_is_on_this_meter", REGIME_FIXTURES)
def test_the_MUTATION_that_proves_the_floor_is_VALID_on_EVERY_regime(
    matched_regimes, premise_id, heating, heat_is_on_this_meter
):
    """R15, and the class behind
    `WORKER_FINDING_MUTATION_VALID_ON_ONE_SUBPOPULATION_ONLY_2026-08-09.md`.

    A mutation is the evidence that a band CAN fail. `_smooth` moves the statistic
    the wrong way on a heat-pump home's METER, so reusing it there would have
    produced an R15 proof that was vacuous in the only direction that matters. The
    guard against a repeat stays per-regime rather than per-band even though there
    is now only one band: for EVERY registered machine, the mutation must move that
    machine's own statistic DOWN and take it below the floor.

    THE MUTATION IS APPLIED TO THE BEHAVIOURAL STREAM ONLY. Flattening the whole
    meter would damage the heating machine too, which is a different and easier
    defect — and it is exactly the conflation H36 removed from the reading.

    A new regime added to `HEAT_ON_THE_JUDGED_METER` with no fixture here fails
    `test_EVERY_heating_system_is_registered_or_explicitly_UNANCHORED` first, so
    the class cannot be reopened quietly.
    """
    trace = matched_regimes[heating]
    grid = [list(d) for d in trace.half_hourly("electricity")]
    heat = _machines_of_trace(trace, on_this_meter=heat_is_on_this_meter)
    band = fgl.texture_band_for(heating.value, has_split=True)

    before = fgl.half_hourly_texture(grid, machines=heat)
    after = fgl.half_hourly_texture(
        _flatten_behaviour(grid, heat, 0.9), machines=heat
    )
    assert after < before, (
        f"the mutation must DESTROY texture on a {heating.value} home, not raise "
        f"it: {before:.4g} -> {after:.4g}"
    )
    assert band.judge(after) is fgl.Verdict.FAIL, (
        f"{heating.value}: the mutation left {after:.4g}, still inside a floor of "
        f"{band.threshold:.4g} — this band has no proof that it can fire"
    )


def test_a_home_with_NO_RECOVERABLE_behaviour_is_COUNTED_never_folded_in(weather):
    """The hole is VISIBLE. A home whose register says its heat is on this meter,
    whose generator supplies no split, has no behavioural stream to read the floor
    on — and both silent folds are wrong in a different direction: judging the
    whole meter at 0.15 fails a correct heat pump, and rescaling the floor by an
    assumed home is the fixed-number defect H36 removed. It is measured, counted,
    and excluded from the rate."""
    band = fgl.texture_band_for(HeatingSystem.HEAT_PUMP_GROUND.value)
    assert band.statistic == fgl.NO_BEHAVIOURAL_STREAM_BAND
    assert band.threshold is None and band.anchor is fgl.AnchorStatus.NEED

    floor = fgl.BANDS[fgl.TEXTURE_STATISTIC]
    n = 100
    values = [floor.threshold * 1.5] * n
    bands = [floor] * n
    bands[0] = band                       # one home with nothing to read
    cell = _texture_cell(values, tuple(bands), tuple(f"H{i}" for i in range(n)))
    assert cell.homes_unjudged == 1
    assert cell.homes_judged == n - 1
    assert cell.verdict is fgl.Verdict.PASS, cell.note


def test_a_population_MOSTLY_unjudgeable_is_INSUFFICIENT_not_clean():
    """The vacuity guard. A population control that reports a clean rate while
    most of its homes were never judged is the exact shape this codebase has
    already been bitten by (1557/1557 passing while the field was absent)."""
    floor = fgl.BANDS[fgl.TEXTURE_STATISTIC]
    unjudgeable = fgl.BANDS[fgl.NO_BEHAVIOURAL_STREAM_BAND]
    n = 100
    unjudged = int(n * fgl.MAX_UNJUDGED_SHARE) + 1
    bands = [unjudgeable] * unjudged + [floor] * (n - unjudged)
    cell = _texture_cell(
        [floor.threshold * 1.5] * n, tuple(bands), tuple(f"H{i}" for i in range(n))
    )
    assert cell.verdict is fgl.Verdict.INSUFFICIENT, cell.note
    assert "coverage floor" in cell.note


def test_a_population_with_NO_judgeable_band_at_all_is_INSUFFICIENT():
    """And the degenerate end of the same guard: zero judged homes is not a clean
    sheet, it is no measurement. An unavailable check is a FAILED check."""
    unjudgeable = fgl.BANDS[fgl.NO_BEHAVIOURAL_STREAM_BAND]
    n = 10
    cell = _texture_cell(
        [0.5] * n, (unjudgeable,) * n, tuple(f"H{i}" for i in range(n))
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

    # The same trace, with the register fact supplied and still no split: the home
    # is COUNTED, not judged by a floor derived for somebody else's house. That is
    # the H36 half of the distinction — before it, naming the machine bought a
    # rescaled threshold, and a threshold nobody could read off this home is what
    # the visible hole replaced.
    named = _clone_population(
        grid, fgl.MIN_HOMES_FOR_L1_RATE, weather,
        heating=HeatingSystem.HEAT_PUMP_AIR.value,
    )
    assert not named.space_heat_grids
    cell = fgl.evaluate_two_level(named).cell(fgl.TEXTURE_STATISTIC)
    assert cell.band.statistic == fgl.NO_BEHAVIOURAL_STREAM_BAND
    assert cell.homes_judged == 0 and cell.homes_unjudged == fgl.MIN_HOMES_FOR_L1_RATE
    assert cell.verdict is fgl.Verdict.INSUFFICIENT, cell.note


# ===========================================================================
# §8 THE HEADLINE'S OWN FAILURE MODES
# ===========================================================================
#
# The controls added 2026-08-11 for this atom's three open Expert-Hour findings.
# Everything in §5 asks whether the COMPANY is wrong. This section asks whether the
# two numbers §5 publishes mean what a reader takes them to mean.
#
# Each control is landed with its NAMED DEFECT as a population it must fire on, and
# with a clean population it must stay silent on (R15 both ways). The defect is a
# population shape rather than a source mutation because these are statistics: the
# thing that can break them is the data they are handed, and a control that has only
# ever been shown its own happy case has demonstrated nothing.


def _coverage_population(*, lodged: int, n=12):
    """A population where the ESTIMATOR IS FIXED and only EPC LODGEMENT COVERAGE moves.

    The first `lodged` premises are meter-armed and their posterior improves on the
    register by a constant factor; the rest were never lodged, so the company holds
    its prior and the two arms are identical. Nothing about the inference differs
    between two populations built this way — only how many premises it reached.

    THE STOCK REPEATS EVERY HALF, and that is the load-bearing detail. `prediction_gap`
    normalises to the no-skill baseline of the population it is handed, so a covered
    set that is a PREFIX of a rising HLC range is a different stock from the whole, and
    the conditioned figure would move for that reason rather than for the estimator's.
    Repeating the range means the covered halves are EXCHANGEABLE — 6-of-12 and 12-of-12
    draw the same HLC multiset — so the conditioned figure is invariant EXACTLY and the
    control can assert an identity instead of a tolerance.
    """
    rows = []
    for i in range(n):
        actual = 0.10 + 0.05 * (i % (n // 2))
        epc = actual * 1.30
        armed = i < lodged
        rows.append(
            fgl.FabricObservation(
                premise_id=f"P{i}",
                actual_hlc_kw_per_k=actual,
                epc_hlc_kw_per_k=epc,
                # The SAME estimator everywhere it runs: halve the register's error.
                inferred_hlc_kw_per_k=actual * 1.15 if armed else epc,
                floor_area_m2=60.0 + 10.0 * (i % (n // 2)),
                annual_heat_kwh=8000.0 + 1500.0 * (i % (n // 2)),
                annual_degree_days_k_day=FIXTURE_DEGREE_DAYS,
                epc_relative_sd=FIXTURE_RELATIVE_SD,
                inferred_relative_sd=FIXTURE_RELATIVE_SD,
                epc_basis=EvidenceBasis.EPC_ONLY,
                inferred_basis=(
                    EvidenceBasis.METER_AND_EPC if armed else EvidenceBasis.EPC_ONLY
                ),
            )
        )
    return rows


def test_the_published_improvement_MOVES_WITH_COVERAGE_WHILE_THE_ESTIMATOR_DOES_NOT():
    """THE NAMED DEFECT (finding 2): coverage reading as skill.

    Two populations, same estimator, different EPC lodgement coverage. The headline
    this atom publishes moves; the conditioned figure does not. If the conditioned
    figure ever starts moving too, the conditioning has stopped working and this
    test says so — that is the whole reason both numbers are carried.
    """
    sparse = fgl.arm_agreement(_coverage_population(lodged=6))
    dense = fgl.arm_agreement(_coverage_population(lodged=12))

    # The DEFECT, demonstrated rather than asserted: the published headline DOUBLES
    # on a change that touched no estimator anywhere. The truth values are identical
    # in both worlds, so the no-skill denominator is too, and the factor is exactly
    # the ratio of the tie fractions.
    assert dense.improvement_all == pytest.approx(sparse.improvement_all * 2.0)
    # The CONTROL: the conditioned figure is a property of the estimator, so it is
    # the SAME NUMBER in both worlds — an identity, not a tolerance.
    assert dense.improvement_informed == pytest.approx(
        sparse.improvement_informed, rel=1e-12
    )
    assert sparse.tie_fraction == pytest.approx(0.5)
    assert dense.tie_fraction == pytest.approx(0.0)
    # And the dilution is exactly the informed fraction, which is what makes the
    # published figure readable once both numbers are carried: on an exchangeable
    # covered set the two differ by coverage and by nothing else.
    assert sparse.improvement_all == pytest.approx(
        sparse.improvement_informed * sparse.informed_fraction
    )


def test_the_tie_fraction_is_read_off_the_BASIS_not_off_the_two_numbers():
    """Independence (R15 TAUTOLOGY). A posterior that genuinely ran and landed
    exactly on its prior must count as INFORMED — deciding by float equality would
    put the measured quantity on both sides of its own measurement."""
    rows = _coverage_population(lodged=12)
    landed_on_prior = [
        dataclasses.replace(o, inferred_hlc_kw_per_k=o.epc_hlc_kw_per_k) for o in rows
    ]
    agreement = fgl.arm_agreement(landed_on_prior)
    assert agreement.informed_premises == len(rows)
    assert agreement.tie_fraction == pytest.approx(0.0)
    # ...and it is REPORTED, because an estimator that never moves anything is also
    # what a broken estimator looks like.
    assert agreement.informed_but_identical == len(rows)


def test_a_BASIS_THAT_DOES_NOT_DESCRIBE_THE_BELIEF_is_refused():
    """The basis predicate's own falsifier. If `epc_only` can sit on a premise whose
    posterior differs from its prior, every conditioned figure below is meaningless
    and the module must say so rather than compute one."""
    rows = _coverage_population(lodged=12)
    lying = [dataclasses.replace(rows[0], inferred_basis=EvidenceBasis.EPC_ONLY)] + rows[1:]
    with pytest.raises(fgl.InsufficientEvidence, match="does not describe the belief"):
        fgl.arm_agreement(lying)


def test_an_inference_headline_over_a_population_it_barely_touched_RAISES():
    """FAIL-LOUD, not fail-open. Returning the diluted figure here would be the
    module's own named anti-pattern: pass on missing evidence."""
    with pytest.raises(fgl.InsufficientEvidence, match="not a substitute"):
        fgl.arm_agreement(_coverage_population(lodged=2))


def test_a_ONE_SIGNED_belief_error_is_reported_as_BIAS_and_a_random_one_is_not():
    """THE NAMED DEFECT (finding 3): the |gap| headline scores a belief that is
    wrong the same way everywhere identically to one that is wrong at random."""
    one_signed = _observations(n=12, epc_bias=0.85)
    bias = fgl.belief_bias(one_signed, belief="epc")
    assert bias.is_systematic and bias.direction == "under"
    assert bias.n_below == 12 and bias.n_above == 0
    assert bias.signed_mean_relative_error == pytest.approx(-0.15)

    # The SAME magnitude of error, alternating sign. The gap is materially the same
    # and the bias verdict is the opposite — which is the point of carrying it.
    alternating = [
        dataclasses.replace(
            o,
            epc_hlc_kw_per_k=o.actual_hlc_kw_per_k * (0.85 if i % 2 else 1.15),
        )
        for i, o in enumerate(_observations(n=12))
    ]
    scattered = fgl.belief_bias(alternating, belief="epc")
    assert not scattered.is_systematic
    assert fgl.epc_vs_actual_gap(alternating).gap == pytest.approx(
        fgl.epc_vs_actual_gap(one_signed).gap, rel=0.05
    ), "the fixture must hold |error| roughly fixed, else sign is not what moved"


def test_a_belief_that_is_never_wrong_has_NO_DIRECTION_rather_than_a_default_one():
    """Vacuity. An all-exact population has nothing to be one-signed about, and a
    sign test over zero decided premises must not report a direction."""
    bias = fgl.belief_bias(_observations(n=8), belief="epc")
    assert bias.n_exact == 8 and bias.n_above == 0 and bias.n_below == 0
    assert bias.sign_test_p == 1.0
    assert not bias.is_systematic and bias.direction == "none"


def test_the_sign_test_is_the_EXACT_binomial_and_not_an_approximation():
    """Checked against hand arithmetic, not against itself: 1-of-15 two-sided is
    2 * (C(15,0) + C(15,1)) / 2**15 = 32/32768."""
    assert fgl._two_sided_sign_test_p(1, 14) == pytest.approx(32 / 32768)
    assert fgl._two_sided_sign_test_p(8, 8) == pytest.approx(1.0)
    assert fgl._two_sided_sign_test_p(0, 0) == 1.0


def test_the_PANEL_MIRROR_reverses_the_registers_direction_and_keeps_its_magnitude():
    rows = _observations(n=10, epc_bias=0.80, inferred_bias=0.90)
    assert fgl.belief_bias(rows, belief="epc").direction == "under"
    mirrored = fgl.mirror_panel_composition(rows)
    assert fgl.belief_bias(mirrored, belief="epc").direction == "over"
    # The log error is preserved EXACTLY — that is what makes the mirror a change of
    # sign rather than a change of subject.
    for before, after in zip(rows, mirrored):
        assert math.log(before.epc_hlc_kw_per_k / before.actual_hlc_kw_per_k) == (
            pytest.approx(-math.log(after.epc_hlc_kw_per_k / after.actual_hlc_kw_per_k))
        )
    # The bill moves with the fabric. A house whose heat loss halves and whose
    # consumption does not is not a house, and the decision reads both.
    for before, after in zip(rows, mirrored):
        assert after.annual_heat_kwh / before.annual_heat_kwh == pytest.approx(
            after.actual_hlc_kw_per_k / before.actual_hlc_kw_per_k
        )


def test_the_REVISION_MIRROR_leaves_a_premise_the_inference_never_touched_alone():
    """By construction, not by a special case: reflecting a posterior through a prior
    it already equals returns the prior."""
    rows = _coverage_population(lodged=6)
    mirrored = fgl.mirror_revision_direction(rows)
    for before, after in zip(rows, mirrored):
        if not fgl.inference_ran(before):
            assert after.inferred_hlc_kw_per_k == pytest.approx(
                before.inferred_hlc_kw_per_k
            )
        else:
            assert (after.inferred_hlc_kw_per_k > before.epc_hlc_kw_per_k) != (
                before.inferred_hlc_kw_per_k > before.epc_hlc_kw_per_k
            )


def test_the_CONFIDENCE_MIRROR_cannot_move_accuracy_at_all():
    """The instrument's own guarantee, and the reason a money flip under it is
    attributable. If a future edit lets this mirror touch a point estimate, both
    assertions here fail and the `confidence_bought` verdict stops meaning anything."""
    rows = _observations(
        n=10, epc_bias=1.3, inferred_bias=1.1,
        epc_relative_sd=0.50, inferred_relative_sd=0.15,
    )
    mirrored = fgl.mirror_decision_confidence(rows)
    assert fgl.epc_vs_actual_gap(mirrored).gap == pytest.approx(
        fgl.epc_vs_actual_gap(rows).gap
    )
    assert fgl.inferred_vs_actual_gap(mirrored).gap == pytest.approx(
        fgl.inferred_vs_actual_gap(rows).gap
    )
    assert mirrored[0].epc_relative_sd == pytest.approx(rows[0].inferred_relative_sd)
    assert mirrored[0].epc_basis is rows[0].inferred_basis


def test_a_MONEY_VERDICT_BOUGHT_BY_THE_ERROR_BAR_is_named_as_such():
    """THE NAMED DEFECT (finding 4): the money headline can rank the two arms on how
    confidently the company may ACT rather than on how right it is.

    Both arms hold the SAME estimate here, so there is no accuracy difference to
    find at all — only one arm is allowed to act on it. A money verdict that still
    names a winner is measuring permission, and the caveat must say so.
    """
    rows = _observations(
        n=10,
        epc_bias=1.35,
        inferred_bias=1.35,
        epc_relative_sd=0.60,
        inferred_relative_sd=0.12,
        epc_basis=EvidenceBasis.STOCK_PRIOR,
        inferred_basis=EvidenceBasis.METER_AND_EPC,
    )
    verdict = fgl.composition_verdict(rows, unit_rate_p_per_kwh=FIXTURE_UNIT_RATE)
    assert verdict.improvement == pytest.approx(0.0), (
        "the fixture must hold accuracy exactly equal, else the flip is not "
        "attributable to confidence"
    )
    assert verdict.money_favours == "inferred"
    assert verdict.confidence_bought
    assert verdict.confidence_mirror_money_favours == "epc"
    caveats = fgl.headline_caveats(rows, unit_rate_p_per_kwh=FIXTURE_UNIT_RATE)
    assert any(c.startswith("CONFIDENCE-BOUGHT") for c in caveats), caveats


def test_an_equally_confident_pair_is_NOT_reported_as_confidence_bought():
    """The other way (R15). When both arms carry the same error bar and basis, the
    confidence mirror is the identity and the verdict must not fire — a control that
    fires on everything is as ignored as one that fires on nothing."""
    rows = _observations(n=10, epc_bias=1.35, inferred_bias=1.10)
    verdict = fgl.composition_verdict(rows, unit_rate_p_per_kwh=FIXTURE_UNIT_RATE)
    assert not verdict.confidence_bought
    assert verdict.declined_epc == verdict.declined_inferred


def test_the_caveat_list_is_EMPTY_on_a_population_with_nothing_to_caveat():
    """The vacuity guard. `headline_caveats` is only evidence if it CAN be silent —
    a list that is never empty carries no information about the row it annotates."""
    rows = [
        dataclasses.replace(
            o,
            # Errors of equal size and alternating sign, on both arms, with the
            # posterior genuinely closer: nothing diluted, nothing one-signed, and
            # both headlines naming the same arm.
            epc_hlc_kw_per_k=o.actual_hlc_kw_per_k * (0.75 if i % 2 else 1.25),
            inferred_hlc_kw_per_k=o.actual_hlc_kw_per_k * (0.95 if i % 2 else 1.05),
        )
        for i, o in enumerate(_observations(n=12))
    ]
    assert fgl.headline_caveats(rows, unit_rate_p_per_kwh=FIXTURE_UNIT_RATE) == []


def test_the_ledger_row_CARRIES_the_caveats_rather_than_offering_them(tmp_path):
    """R11, no orphan transition. The door renders what the row holds; a caveat
    computed and not written is a caveat nobody reads."""
    path = tmp_path / "ledger.json"
    rows = _coverage_population(lodged=6)
    fgl.write_fabric_gap_entries(
        rows,
        unit_rate_p_per_kwh=FIXTURE_UNIT_RATE,
        measured_at="2026-08-11T00:00:00+00:00",
        path=path,
    )
    ledger = json.loads(path.read_text())
    components = ledger[fgl.GENERATOR_WORLD_ATOM]["components"]
    assert components["arm_agreement"]["tie_fraction"] == pytest.approx(0.5)
    assert components["arm_agreement"]["improvement_informed"] != (
        components["inference_improvement"]
    )
    assert components["belief_bias"]["epc"]["direction"] == "over"
    assert "composition_verdict" in components
    assert any(
        c.startswith("DILUTED") for c in components["headline_caveats"]
    ), components["headline_caveats"]


def test_a_MAJORITY_AND_AN_AVERAGE_THAT_DISAGREE_are_named_rather_than_juxtaposed():
    """The defect this caveat was landed for, found on the drawn 200-premise
    population the ledger actually publishes: the register sits BELOW truth on 126
    of 200 premises while the mean signed error is +19.6%, because a minority of
    large over-statements outweighs the majority of small under-statements.

    Both numbers are right. A sentence that printed them side by side without saying
    so reads as a contradiction — one name, two numbers. The control fires when they
    point opposite ways and stays silent when they agree.
    """
    rows = _observations(n=12)
    skewed = [
        dataclasses.replace(
            o,
            # Eleven small under-statements, one large over-statement: the majority
            # says "under", the mean says "over".
            epc_hlc_kw_per_k=o.actual_hlc_kw_per_k * (6.0 if i == 0 else 0.95),
        )
        for i, o in enumerate(rows)
    ]
    bias = fgl.belief_bias(skewed, belief="epc")
    assert bias.direction == "under" and bias.n_below == 11
    assert bias.signed_mean_relative_error > 0.0
    assert not bias.mean_agrees_with_majority
    caveats = fgl.headline_caveats(skewed, unit_rate_p_per_kwh=FIXTURE_UNIT_RATE)
    assert any(c.startswith("SKEWED (epc)") for c in caveats), caveats

    # The other way: a uniformly under-stated register has a majority and an average
    # that agree, and must NOT be reported as skewed.
    plain = _observations(n=12, epc_bias=0.85)
    plain_bias = fgl.belief_bias(plain, belief="epc")
    assert plain_bias.direction == "under" and plain_bias.mean_agrees_with_majority
    assert not any(
        c.startswith("SKEWED")
        for c in fgl.headline_caveats(plain, unit_rate_p_per_kwh=FIXTURE_UNIT_RATE)
    )


def test_a_belief_with_no_systematic_direction_is_not_reported_as_skewed():
    """Vacuity again: `mean_agrees_with_majority` must be True when there is no
    majority to agree with, or every scattered population would carry a SKEWED line."""
    bias = fgl.belief_bias(_observations(n=8), belief="epc")
    assert bias.direction == "none" and bias.mean_agrees_with_majority
