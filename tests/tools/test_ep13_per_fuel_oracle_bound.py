"""R15 for `tools/ep13_per_fuel_oracle_bound.py`.

WHAT THIS INSTRUMENT'S HEADLINE IS, and therefore what its controls have to be able to do. It
reports a POSITIVE — per-fuel truth clears the shipped reconstruction by +0.19 in 2024 — so the
R15 danger is inverted from the four EP13 bounds that reported negatives. An instrument that says
"big headroom" whatever it is handed reports a CONSTANT and its headline is worthless. The
load-bearing test is therefore `test_the_instrument_reports_a_LOW_oracle_when_THE_FUELS_DO_NOT_
CARRY_THE_TIMING`, and beside it `test_the_ablation_ladder_NAMES_THE_FUEL_THAT_CARRIES_THE_TIMING`,
which requires the ladder to finger a fuel the fixture chose in advance.

THE SECOND LOAD-BEARING TEST IS A FAIL-CLOSED ONE, and it exists because the first draft of this
measurement had the defect. The four FUELHH caches do not cover identical half hours. A half hour
with no CCGT row is not a half hour with no gas; summing it as zero deletes the largest carbon
term on the system and publishes a clean grid.
`test_a_half_hour_MISSING_A_FUEL_is_REFUSED_and_not_summed_as_zero` pins that shut.

The fixture is SYNTHETIC and does not read `sim/cache`, because a control that needs 500 MB of
cache present is fail-silent the day the cache is absent. One test reads the COMMITTED artefact to
pin the published headline to the measurement, and it skips (loudly, with the reason) when that
file is missing rather than passing on its absence.
"""

from __future__ import annotations

import json
import math
import random
from pathlib import Path

import pytest

from sim import neso_carbon_intensity as neso
from tools import ep13_per_fuel_oracle_bound as per_fuel

YEAR = "2024"
DAYS = 60
PERIODS = 48

FACTORS = {
    "COAL": 937.0,
    "CCGT": 394.0,
    "OCGT": 651.0,
    "BIOMASS": 120.0,
    "NUCLEAR": 0.0,
    "NPSHYD": 0.0,
    "WIND": 0.0,
}


def _key_date(day: int) -> str:
    return f"{YEAR}-03-{day:02d}" if day <= 31 else f"{YEAR}-04-{day - 31:02d}"


def _world(
    *,
    fuels_carry_timing: bool = True,
    every_fuel_flat_within_day: bool = False,
    seed: int = 11,
):
    """(shipped, actual, demand, mix, wind) for one synthetic year.

    CCGT IS THE FUEL THE FIXTURE PUTS THE WITHIN-DAY TIMING IN, chosen in advance so the ablation
    ladder has a right answer to be scored against rather than an output to be admired.

    NESO's `actual` is the oracle's arithmetic PLUS a midday-shaped term the fuels cannot see —
    the fixture's stand-in for embedded solar, and what stops this being a replay of itself.

    The SHIPPED baseline is a COMPETENT model: right about the day's level, partly wrong about the
    ordering inside it, which is the real shape of what this atom ships. A fixture whose baseline
    is absurd makes its own bar meaningless.
    """
    rng = random.Random(seed)
    demand: dict[tuple[str, int], float] = {}
    mix: dict[tuple[str, int], dict[str, float]] = {}
    wind: dict[tuple[str, int], float] = {}
    shipped_g: dict[tuple[str, int], float] = {}
    actual: dict[tuple[str, int], float] = {}

    for day in range(1, DAYS + 1):
        date = _key_date(day)
        windiness = 6000.0 + 5000.0 * math.sin(2 * math.pi * day / 17.0)
        for period in range(1, PERIODS + 1):
            phase = 2 * math.pi * period / PERIODS
            key = (date, period)
            demand[key] = 30000.0 + 8000.0 * math.sin(phase - 0.6)

            within = 0.0 if every_fuel_flat_within_day else 1.0
            wind[key] = windiness + within * 1500.0 * math.sin(phase + 1.1)
            # CCGT is the marginal plant: it swings hard inside the day and follows demand.
            ccgt = 9000.0 + within * (6000.0 * math.sin(phase - 0.6) + 1200.0 * math.sin(2 * phase))
            fuels = {
                "COAL": 900.0 + 300.0 * math.sin(2 * math.pi * day / 23.0),
                "CCGT": ccgt if fuels_carry_timing else 9000.0,
                "OCGT": 40.0,
                "BIOMASS": 2200.0,
                "NUCLEAR": 6000.0,
                "NPSHYD": 500.0,
            }
            mix[key] = fuels

            clean = per_fuel.oracle_intensity(fuels, wind[key], FACTORS)
            # The term the fuels cannot see: midday-shaped, like embedded solar. Sized so the
            # fixture's oracle sits the same distance from its target as the real one does from
            # NESO's (a mean absolute error in the tens of grams, not in ones).
            embedded = -55.0 * max(0.0, math.sin(phase - 0.4))
            if fuels_carry_timing:
                actual[key] = clean + embedded + rng.gauss(0.0, 3.0)
            else:
                # The timing lives somewhere the fuel mix has no access to at all.
                actual[key] = (
                    clean + 90.0 * math.sin(phase + 2.4) + embedded + rng.gauss(0.0, 3.0)
                )
            level = 200.0 + 30.0 * math.sin(2 * math.pi * day / 29.0)
            shipped_g[key] = level + 0.60 * (actual[key] - level) + 30.0 * math.sin(phase + 2.2)

    shipped = neso.published_shape(shipped_g, demand)
    return shipped, actual, demand, mix, wind


def _row(**kwargs):
    shipped, actual, demand, mix, wind = _world(**kwargs)
    oracle, _refused = per_fuel.build_oracle(mix, wind, FACTORS)
    row = per_fuel.measure_year(
        YEAR,
        shipped=shipped,
        actual=actual,
        oracle=oracle,
        demand=demand,
        mix=mix,
        wind=wind,
        factors=FACTORS,
    )
    row["controls"] = per_fuel.verdicts(row)
    return row


@pytest.fixture(scope="module")
def row():
    return _row()


def test_the_fixture_is_a_population_and_the_baseline_is_competent(row):
    """POPULATION FIRST. A correlation over a handful of half hours is noise wearing a statistic's
    clothes, and a bar cleared by an absurd baseline measures nothing."""
    assert row["control_scored_half_hours"] >= per_fuel.MIN_SCORED_HALF_HOURS
    assert row["control_scored_half_hours"] >= 1000
    assert 0.55 < row["baseline"]["correlation"] < 0.95


def test_the_instrument_reports_a_LOW_oracle_when_THE_FUELS_DO_NOT_CARRY_THE_TIMING():
    """THE LOAD-BEARING TEST. This instrument's finding is a POSITIVE, so one that reports a high
    oracle on any input reports a CONSTANT.

    The bad world is not noise: the fuel mix is still true and still drives the level, and only the
    within-day ordering of NESO's series has moved somewhere the fuels cannot see. Asserted by
    ATTAINMENT -- the oracle must fall BELOW the shipped baseline and its within-day control must
    go False -- not merely by "it went down".
    """
    bad = _row(fuels_carry_timing=False)
    assert bad["oracle"]["correlation"] < bad["baseline"]["correlation"]
    assert bad["controls"]["oracle_exceeds_baseline"] is False
    assert bad["controls"]["oracle_beats_its_own_day_mean"] is False


def test_the_ablation_ladder_NAMES_THE_FUEL_THAT_CARRIES_THE_TIMING(row):
    """The ladder's whole job. The fixture put the within-day swing in CCGT and nowhere else, so an
    instrument that cannot finger CCGT cannot be trusted when it fingers CCGT on the real cache.

    Asserted as an ORDERING and a MARGIN, not as "CCGT appears": a ladder that ranks CCGT first by
    1e-6 over biomass has not discriminated.
    """
    assert row["dominant_within_day_fuel"] == "CCGT"
    costs = row["ablation_cost"]
    assert costs["CCGT"] > per_fuel.MIN_ABLATION_SIGNAL
    assert costs["CCGT"] > 5 * max(costs["COAL"], costs["BIOMASS"], costs["OCGT"])


def test_the_ladder_control_FIRES_when_no_fuel_carries_any_timing():
    """MUTATION: every fuel flat within the day. Ablating a flat series changes nothing, so every
    rung costs ~0 and the ladder has named nothing — which must read as FAILURE, not as five
    agreeable numbers."""
    degenerate = _row(every_fuel_flat_within_day=True)
    assert degenerate["controls"]["ablation_ladder_discriminates"] is False
    assert max(degenerate["ablation_cost"].values()) < per_fuel.MIN_ABLATION_SIGNAL


def test_a_REPLAY_of_NESOs_own_arithmetic_is_caught_by_the_tautology_control(row):
    """MUTATION: actual := the oracle itself. R15's first killer — a series compared with itself.

    Without this control the instrument would report a perfect oracle and the atom would conclude
    per-fuel truth reproduces the target exactly, when what it had reproduced was its own sum.
    """
    assert row["controls"]["oracle_is_not_nesos_arithmetic"] is True

    shipped, _actual, demand, mix, wind = _world()
    oracle, _refused = per_fuel.build_oracle(mix, wind, FACTORS)
    replayed = per_fuel.measure_year(
        YEAR,
        shipped=shipped,
        actual=dict(oracle),
        oracle=oracle,
        demand=demand,
        mix=mix,
        wind=wind,
        factors=FACTORS,
    )
    verdicts = per_fuel.verdicts(replayed)
    assert replayed["control_oracle_identical_share"] == 1.0
    assert replayed["control_oracle_mean_abs_error_g"] == 0.0
    assert verdicts["oracle_is_not_nesos_arithmetic"] is False
    assert replayed["oracle"]["correlation"] == pytest.approx(1.0, abs=1e-9)


def test_the_tautology_bar_is_far_below_the_measured_distance(row):
    """A bar the data sits just above is a bar carrying the result. The measured distance on the
    real cache is 11.7-33.1 g against a 2.0 g bar; the fixture must clear it by a wide margin
    too, or this test is pinning a number rather than a property."""
    assert per_fuel.MIN_TAUTOLOGY_DISTANCE_G == 2.0
    assert row["control_oracle_mean_abs_error_g"] > 5 * per_fuel.MIN_TAUTOLOGY_DISTANCE_G


def test_the_within_day_control_fires_when_the_oracle_is_its_own_day_mean():
    """MUTATION: oracle := its own day mean. It keeps every between-day fact and loses only the
    axis under measurement, so a control that still passes is measuring the wrong axis."""
    shipped, actual, demand, mix, wind = _world()
    oracle, _refused = per_fuel.build_oracle(mix, wind, FACTORS)
    flat = per_fuel.day_mean(oracle)
    flattened = per_fuel.measure_year(
        YEAR,
        shipped=shipped,
        actual=actual,
        oracle=flat,
        demand=demand,
        mix=mix,
        wind=wind,
        factors=FACTORS,
    )
    assert per_fuel.verdicts(flattened)["oracle_beats_its_own_day_mean"] is False


def test_the_within_day_margin_is_far_below_the_measured_signal(row):
    """MIN_WITHIN_DAY_ADVANTAGE exists because a strict inequality passes on 1e-16 of floating
    point when a mutation makes both sides equal — the mutation that survived `ep13_peer_bound`'s
    first battery. It must stay an order of magnitude below the real gap or it carries the result.
    """
    assert per_fuel.MIN_WITHIN_DAY_ADVANTAGE == 0.01
    gap = row["oracle"]["correlation"] - row["oracle_day_mean"]["correlation"]
    assert gap > 10 * per_fuel.MIN_WITHIN_DAY_ADVANTAGE


def test_day_mean_actually_flattens_the_within_day_axis():
    """The placebo has to do what its name says, or every control built on it is vacuous."""
    series = {("2024-03-01", p): float(p) for p in range(1, 49)}
    flat = per_fuel.day_mean(series)
    assert len(set(flat.values())) == 1
    assert flat[("2024-03-01", 1)] == pytest.approx(24.5)


def test_the_NULL_rung_collapses_and_the_control_fires_when_it_does_not(row):
    """A null that does not collapse means the axis is not what the instrument thinks it is."""
    assert row["controls"]["null_collapses"] is True
    assert abs(row["oracle_shuffled"]["correlation"]) < 0.1

    intact = dict(row)
    intact["oracle_shuffled"] = {"correlation": 0.8}
    assert per_fuel.verdicts(intact)["null_collapses"] is False


def test_shuffled_preserves_the_VALUES_and_destroys_only_the_TIMING():
    """If the null changed the value distribution it would test the scale of the numbers instead of
    the axis under measurement."""
    series = {("2024-03-01", p): float(p) for p in range(1, 49)}
    dealt = per_fuel.shuffled(series, list(series))
    assert sorted(dealt.values()) == sorted(series.values())
    assert dealt != series


def test_a_half_hour_MISSING_A_FUEL_is_REFUSED_and_not_summed_as_zero():
    """THE DEFECT THIS INSTRUMENT'S FIRST DRAFT HAD, pinned shut.

    The four FUELHH caches do not cover the same half hours. Treating an absent CCGT row as zero
    gas is not a small error: it is the largest carbon term on the system, and it publishes a clean
    grid. The test asserts BOTH halves — the half hour is refused AND counted — and then shows what
    the fail-open reading would have been, so a later reader can see the size of what is refused.
    """
    _shipped, _actual, _demand, mix, wind = _world()
    victim = ("2024-03-02", 20)
    complete = per_fuel.oracle_intensity(mix[victim], wind[victim], FACTORS)

    holed = {k: (dict(v) if k != victim else {f: mw for f, mw in v.items() if f != "CCGT"})
             for k, v in mix.items()}
    oracle, refused = per_fuel.build_oracle(holed, wind, FACTORS)

    assert victim not in oracle
    assert refused[YEAR] == 1
    assert per_fuel.oracle_intensity(holed[victim], wind[victim], FACTORS) is None

    # What summing the absent fuel as zero would have published, had it not been refused.
    as_zero = per_fuel.oracle_intensity(
        {**holed[victim], "CCGT": 0.0}, wind[victim], FACTORS
    )
    assert as_zero < complete
    assert complete - as_zero > 50.0


def test_a_LOST_FLEET_is_caught_by_the_coverage_control(row):
    """MUTATION: the denominator loses a fleet. Generation over demand is the only thing standing
    between this instrument and a silently rescaled intensity, and a one-sided bound would pass by
    being wide — so BOTH ends are checked."""
    assert row["controls"]["fuel_coverage_is_plausible"] is True

    for broken, name in ((0.5, "half the fleet"), (1.9, "double-counted")):
        mutated = dict(row)
        mutated["control_generation_over_demand"] = broken
        assert per_fuel.verdicts(mutated)["fuel_coverage_is_plausible"] is False, name


def test_the_coverage_bound_admits_a_NET_EXPORT_year(row):
    """KEYED TO THE PROPERTY, NOT TO TODAY'S ANSWER. GB generation legitimately exceeded GB demand
    in 2022 (ratio 1.063), and a bound capped at 1.0 would have gone red because the world got more
    honest. That is exactly backwards and it is why the ceiling is 1.20."""
    assert per_fuel.MAX_GENERATION_OVER_DEMAND > 1.063
    exporting = dict(row)
    exporting["control_generation_over_demand"] = 1.063
    assert per_fuel.verdicts(exporting)["fuel_coverage_is_plausible"] is True


def test_a_year_too_thin_to_measure_is_REFUSED_not_reported():
    """A fortnight of cache must not report a correlation as if it were a year."""
    shipped, actual, demand, mix, wind = _world()
    oracle, _refused = per_fuel.build_oracle(mix, wind, FACTORS)
    thin = sorted(oracle)[:200]
    with pytest.raises(neso.NesoIntensityUnavailable):
        per_fuel.measure_year(
            YEAR,
            shipped={k: shipped[k] for k in thin},
            actual=actual,
            oracle=oracle,
            demand=demand,
            mix=mix,
            wind=wind,
            factors=FACTORS,
        )


def test_the_oracle_cannot_reach_the_published_feed():
    """NESO's factor table on metered truth is NESO's arithmetic. Publishing it as this world's
    carbon series would make the reconstruction pointless — refused structurally, by an AST walk,
    not by a sentence in a docstring."""
    assert per_fuel.oracle_is_unreachable_from(per_fuel._published_feed_source()) is True
    assert per_fuel.oracle_is_unreachable_from(
        "from tools.ep13_per_fuel_oracle_bound import measure"
    ) is False
    assert per_fuel.oracle_is_unreachable_from("import tools.ep13_per_fuel_oracle_bound") is False
    # A mention in a COMMENT is not a call, and a substring search would have said it was.
    assert per_fuel.oracle_is_unreachable_from("# see ep13_per_fuel_oracle_bound\nx = 1") is True


def test_the_committed_artefact_carries_the_numbers_the_frame_doc_quotes():
    """Pins the published headline to the measurement. SKIPS LOUDLY when the artefact is absent
    rather than passing on its absence."""
    path = per_fuel.OUT_PATH
    if not path.exists():
        pytest.skip(f"{path} not generated -- run `python3 -m tools.ep13_per_fuel_oracle_bound`")
    data = json.loads(Path(path).read_text(encoding="utf-8"))

    assert data["oracle_reaches_the_published_feed"] is False
    year = data["years"]["2024"]
    assert year["baseline"]["correlation"] == pytest.approx(0.7425, abs=5e-3)
    assert year["oracle"]["correlation"] == pytest.approx(0.9352, abs=5e-3)
    assert year["oracle_over_baseline"] > 0.15
    assert year["dominant_within_day_fuel"] == "CCGT"
    assert all(year["controls"][name] for name in (
        "oracle_is_not_nesos_arithmetic",
        "oracle_beats_its_own_day_mean",
        "null_collapses",
        "fuel_coverage_is_plausible",
        "ablation_ladder_discriminates",
    ))
