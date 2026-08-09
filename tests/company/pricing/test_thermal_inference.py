"""C14 — company-side thermal parameter inference.

R15 DISCIPLINE: every control in `company.pricing.thermal_inference` is
exercised BOTH ways here. A bare "the control returned True" assertion is never
sufficient on its own and never appears alone — each is paired with a named
mutation that proves it fires on the specific defect it exists to catch.

THE WALL IS THE POINT OF THIS ATOM. The module under test may see only meter
reads, published weather and the EPC register. This SUITE is allowed to see
both sides — it is the harness, and measuring the belief-vs-truth gap is what
the coupled triad requires — but it feeds the company nothing but observables,
and `test_the_wall_is_intact` fails if the module itself ever reaches inside.

The recovery bounds below were MEASURED against `W1_12` traces on 2026-08-03
and are stated as relationships or generous outer bounds, never as pinned
generated values: a threshold pinned to a specific RNG draw is a control that
passes for the wrong reason.
"""

from __future__ import annotations

import datetime as dt
import math
from pathlib import Path

import pytest

from company.pricing import thermal_inference as ti
from simulation import premise_trace as pt
from simulation.fabric_physics import DEFAULT_LATITUDE_DEG
from simulation.household import (
    BoilerAge,
    BuildEra,
    HeatingSystem,
    Household,
    InsulationLevel,
    PropertyType,
)

WINDOW_START = dt.date(2022, 1, 1)
WINDOW_END = dt.date(2022, 12, 31)
AS_OF = dt.date(2023, 1, 1)

# The EPC register's own vocabulary. The company never sees the SIM's enums, so
# the harness translates here — deliberately in the TEST, not in the module.
_ERA_BAND = {
    BuildEra.PRE_1919: "pre-1919",
    BuildEra.ERA_1919_1944: "1919-1944",
    BuildEra.ERA_1945_1964: "1945-1964",
    BuildEra.ERA_1965_1980: "1965-1980",
    BuildEra.ERA_1981_2000: "1981-2000",
    BuildEra.POST_2000: "post-2000",
}
_EPC_PROPERTY_TYPE = {
    PropertyType.SEMI_DETACHED: "semi-detached",
    PropertyType.DETACHED: "detached",
    PropertyType.FLAT: "flat",
    PropertyType.TERRACED: "terraced",
}


def make_household(
    customer_id: str,
    *,
    property_type: PropertyType = PropertyType.SEMI_DETACHED,
    build_era: BuildEra = BuildEra.ERA_1965_1980,
    insulation: InsulationLevel = InsulationLevel.PARTIAL,
    heating_system: HeatingSystem = HeatingSystem.GAS_BOILER_COMBI,
    bedrooms: int = 3,
) -> Household:
    return Household(
        customer_id=customer_id,
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
def weather_days():
    return pt.load_trace_weather("C1", start=WINDOW_START, end=WINDOW_END)


@pytest.fixture(scope="module")
def published_weather(weather_days):
    """What the company sees: date and mean temperature, nothing else."""
    return [
        ti.PublishedWeatherDay(day.date, day.weather.temperature_mean_c)
        for day in weather_days
    ]


def reads_from_trace(trace, commodity: str, *, every_n_days: int, start: dt.date):
    """Turn a generated trace into the CUMULATIVE REGISTER READS a supplier
    would hold, at the cadence its meter actually reports."""
    cumulative = 0.0
    reads = [ti.MeterRead(start - dt.timedelta(days=1), 0.0)]
    for index, (day, daily_kwh) in enumerate(zip(trace.days, trace.daily(commodity))):
        cumulative += daily_kwh
        if (index + 1) % every_n_days == 0:
            reads.append(ti.MeterRead(day.date, cumulative))
    return reads


def certificate_for(trace, household: Household, *, lodged: dt.date, insulation=None):
    return ti.EpcCertificate(
        lodged_date=lodged,
        total_floor_area_m2=trace.fabric.floor_area_m2,
        property_type=_EPC_PROPERTY_TYPE[household.property_type],
        build_era_band=_ERA_BAND[household.build_era],
        insulation=(insulation or household.insulation.value),
        main_heating_fuel=(
            "air source heat pump"
            if household.heating_system == HeatingSystem.HEAT_PUMP_AIR
            else "mains gas"
        ),
    )


PANEL = [
    ("gas-semi-1965", PropertyType.SEMI_DETACHED, BuildEra.ERA_1965_1980,
     InsulationLevel.PARTIAL, HeatingSystem.GAS_BOILER_COMBI, 3),
    ("gas-detached-pre1919", PropertyType.DETACHED, BuildEra.PRE_1919,
     InsulationLevel.POOR, HeatingSystem.GAS_BOILER_COMBI, 4),
    ("gas-flat-post2000", PropertyType.FLAT, BuildEra.POST_2000,
     InsulationLevel.FULL, HeatingSystem.GAS_BOILER_COMBI, 2),
    ("gas-terrace-1919", PropertyType.TERRACED, BuildEra.ERA_1919_1944,
     InsulationLevel.PARTIAL, HeatingSystem.GAS_BOILER_COMBI, 3),
    ("ashp-semi-1981", PropertyType.SEMI_DETACHED, BuildEra.ERA_1981_2000,
     InsulationLevel.FULL, HeatingSystem.HEAT_PUMP_AIR, 3),
]


@pytest.fixture(scope="module")
def panel(weather_days):
    """Generate the truth side ONCE. ~0.5 s per premise-year."""
    out = []
    for name, ptype, era, insulation, system, bedrooms in PANEL:
        household = make_household(
            name,
            property_type=ptype,
            build_era=era,
            insulation=insulation,
            heating_system=system,
            bedrooms=bedrooms,
        )
        trace = pt.generate_premise_trace(
            premise_id=name, household=household, weather=weather_days, seed=17,
            # W1_11 HARDEN made latitude_deg REQUIRED on every public entry point
            # (it is a legitimate INPUT, a defect only as a silent FALLBACK). This
            # panel is a synthetic national one with no site, so it passes the
            # population-weighted UK value explicitly.
            latitude_deg=DEFAULT_LATITUDE_DEG,
        )
        commodity = (
            "electricity" if system == HeatingSystem.HEAT_PUMP_AIR else "gas"
        )
        out.append((name, household, trace, commodity))
    return out


def believe(entry, published_weather, *, every_n_days=1, lodged=dt.date(2019, 6, 1),
            insulation=None, certificate=...):
    name, household, trace, commodity = entry
    cert = (
        certificate_for(trace, household, lodged=lodged, insulation=insulation)
        if certificate is ...
        else certificate
    )
    return ti.infer_thermal_parameters(
        premise_id=name,
        reads=reads_from_trace(
            trace, commodity, every_n_days=every_n_days, start=WINDOW_START
        ),
        weather=published_weather,
        certificate=cert,
        as_of=AS_OF,
        property_type_hint=_EPC_PROPERTY_TYPE[household.property_type],
        main_heating_fuel=(
            "air source heat pump"
            if household.heating_system == HeatingSystem.HEAT_PUMP_AIR
            else "mains gas"
        ),
    )


def actual_hlc(entry) -> float:
    return entry[2].fabric.heat_loss_coefficient_kw_per_k


# ---------------------------------------------------------------------------
# THE WALL — the gate on this atom
# ---------------------------------------------------------------------------


def test_the_wall_is_intact():
    """The module may not import the SIM. Passes on the real source."""
    module_path = Path(ti.__file__)
    assert ti.sim_imports_in(module_path.read_text()) == []
    ti.assert_wall_intact()  # does not raise


@pytest.mark.parametrize(
    "injected",
    [
        "from simulation.fabric_physics import fabric_parameters",
        "import simulation.premise_trace",
        "from sim.weather_hdd import hdd",
        "    from simulation import household",
    ],
)
def test_the_wall_control_fires_on_a_sim_import(injected, tmp_path):
    """MUTATION: the same control, run over source that DOES reach inside, must
    name the import. A wall control that cannot fail is worse than no wall."""
    mutated = "import math\n" + injected + "\n\ndef f():\n    return 1\n"
    assert ti.sim_imports_in(mutated), "the wall control missed a real SIM import"

    path = tmp_path / "leaky.py"
    path.write_text(mutated)
    with pytest.raises(ti.WallViolationError, match="imports SIM internals"):
        ti.assert_wall_intact(path)


def test_the_wall_control_does_not_fire_on_similar_names(tmp_path):
    """It must not fire on `similarity`, `simple`, or a company module whose
    name merely starts with the same letters — a control that cries wolf gets
    switched off, which is its own kind of failure."""
    innocent = (
        "import simplejson\n"
        "from company.pricing import simulation_helpers_not_really\n"
        "from simulated import x  # not the SIM package\n"
    )
    assert ti.sim_imports_in(innocent) == []


# ---------------------------------------------------------------------------
# Meter-history guards — malformed input must FAIL, never be quietly repaired
# ---------------------------------------------------------------------------


def _reads(pairs):
    return [ti.MeterRead(dt.date(2022, 1, 1) + dt.timedelta(days=d), v) for d, v in pairs]


def test_backwards_register_is_rejected():
    with pytest.raises(ti.UnusableMeterHistoryError, match="backwards"):
        ti.consumption_intervals(_reads([(0, 0.0), (30, 500.0), (60, 400.0)]))


def test_backwards_guard_is_nan_blind_without_the_finite_check():
    """MUTATION, and the reason `_require_finite` runs FIRST: `nan < x` is
    False, so a NaN register slides straight past the backwards comparison.
    The naive comparison is shown failing to fire, then the real code raising."""
    nan = float("nan")
    assert not (nan < 500.0), "the guard's own comparison is NaN-blind"
    with pytest.raises(ti.UnusableMeterHistoryError, match="not finite"):
        ti.consumption_intervals(_reads([(0, 0.0), (30, 500.0), (60, nan)]))


def test_two_reads_on_one_day_are_rejected():
    with pytest.raises(ti.UnusableMeterHistoryError, match="two reads"):
        ti.consumption_intervals(_reads([(0, 0.0), (30, 500.0), (30, 510.0)]))


def test_a_single_read_cannot_form_an_interval():
    with pytest.raises(ti.InsufficientObservationError, match="at least 2 reads"):
        ti.consumption_intervals(_reads([(0, 0.0)]))


def test_a_well_formed_history_is_not_rejected():
    """The other half of every guard above: legitimate input passes. A control
    that rejects everything is indistinguishable from a broken pipeline."""
    intervals = ti.consumption_intervals(_reads([(0, 0.0), (30, 500.0), (60, 900.0)]))
    assert [i.days for i in intervals] == [30, 30]
    assert intervals[0].kwh_per_day == pytest.approx(500.0 / 30)


def test_too_few_intervals_raises_rather_than_fitting(published_weather):
    reads = _reads([(0, 0.0), (91, 3000.0), (182, 4000.0), (273, 4500.0)])
    with pytest.raises(ti.InsufficientObservationError, match="read intervals"):
        ti.fit_heating_response(reads, published_weather)


def test_summer_only_history_cannot_see_a_heating_gradient(published_weather):
    """A supplier that has never observed the premise in the cold does not know
    its heat loss. MEASURED FAIL-OPEN (2026-08-03): the span test alone passed
    this, because the searched balance point drifts to 18 C and a UK July still
    spreads a few degree days — so the fit extrapolated winter fabric loss from
    summer hot water. `MIN_PEAK_HDD_K` is what refuses it."""
    summer = [
        ti.MeterRead(dt.date(2022, 6, 1) + dt.timedelta(days=7 * i), 100.0 * i)
        for i in range(10)
    ]
    with pytest.raises(ti.InsufficientObservationError):
        ti.fit_heating_response(summer, published_weather)


def test_the_cold_weather_requirement_is_what_refuses_the_summer_history(
    published_weather, monkeypatch
):
    """MUTATION: drop the cold-weather requirement back to zero — the state the
    measurement above found — and the same summer history is accepted."""
    monkeypatch.setattr(ti, "MIN_PEAK_HDD_K", 0.0)
    summer = [
        ti.MeterRead(dt.date(2022, 6, 1) + dt.timedelta(days=7 * i), 100.0 * i)
        for i in range(10)
    ]
    fit = ti.fit_heating_response(summer, published_weather)
    assert fit.hdd_span_k >= ti.MIN_HDD_SPAN_K, (
        "if the span test had refused this history, the peak-HDD requirement "
        "would not be the control under test here"
    )


def test_an_interval_the_weather_does_not_cover_is_dropped_not_approximated(
    published_weather,
):
    """Partial weather coverage would understate degree days and drag the
    gradient down. The interval is dropped; if too many are, the fit raises."""
    reads = [
        ti.MeterRead(dt.date(2021, 10, 1) + dt.timedelta(days=14 * i), 400.0 * i)
        for i in range(8)
    ]
    with pytest.raises(ti.InsufficientObservationError):
        ti.fit_heating_response(reads, published_weather)


# ---------------------------------------------------------------------------
# The EPC register's three error sources
# ---------------------------------------------------------------------------


def test_absent_certificate_gives_a_stock_prior_that_is_not_actionable():
    prior = ti.epc_prior(None, as_of=AS_OF, property_type_hint="semi-detached")
    assert prior.basis is ti.EvidenceBasis.STOCK_PRIOR
    assert prior.relative_sd == ti.STOCK_PRIOR_RELATIVE_SD
    assert prior.relative_sd > ti.EPC_MODELLING_RELATIVE_SD


def test_no_certificate_and_no_property_type_is_an_error_not_a_default():
    """FAIL-OPEN GUARD: with nothing at all known about the premise, the honest
    answer is a refusal. Returning a national average would look like a belief."""
    with pytest.raises(ti.InsufficientObservationError, match="no fabric prior"):
        ti.epc_prior(None, as_of=AS_OF, property_type_hint=None)


def test_staleness_widens_the_prior_monotonically_and_is_capped():
    def sd_at(years):
        cert = ti.EpcCertificate(
            lodged_date=AS_OF - dt.timedelta(days=int(365.25 * years)),
            total_floor_area_m2=90.0,
            property_type="semi-detached",
            build_era_band="1965-1980",
            insulation="partial",
        )
        return ti.epc_prior(cert, as_of=AS_OF).relative_sd

    sds = [sd_at(y) for y in (0, 2, 5, 10)]
    assert sds == sorted(sds), f"staleness must widen the prior, got {sds}"
    assert sds[0] == pytest.approx(ti.EPC_MODELLING_RELATIVE_SD)
    assert sd_at(60) == pytest.approx(ti.EPC_MAX_RELATIVE_SD)
    # And the modelling-error floor is never removed, however new the paper is.
    assert sd_at(0) > 0.0


def test_a_fresh_certificate_is_still_uncertain():
    """MUTATION of the premise, not the code: if the modelling-error floor were
    dropped, a day-old certificate would read as exact. It must not."""
    cert = ti.EpcCertificate(
        lodged_date=AS_OF - dt.timedelta(days=1),
        total_floor_area_m2=90.0,
        property_type="semi-detached",
        build_era_band="1965-1980",
        insulation="partial",
    )
    assert ti.epc_prior(cert, as_of=AS_OF).relative_sd >= ti.EPC_MODELLING_RELATIVE_SD


@pytest.mark.parametrize(
    "field,value",
    [("property_type", "houseboat"), ("build_era_band", "1066-1070")],
)
def test_an_unreadable_certificate_field_raises(field, value):
    kwargs = dict(
        lodged_date=dt.date(2019, 1, 1),
        total_floor_area_m2=90.0,
        property_type="semi-detached",
        build_era_band="1965-1980",
    )
    kwargs[field] = value
    with pytest.raises(ti.InsufficientObservationError, match="unrecognised"):
        ti.epc_prior(ti.EpcCertificate(**kwargs), as_of=AS_OF)


def test_epc_property_type_synonyms_are_read():
    """The register does not use one spelling. `mid-terrace` and `maisonette`
    are real EPC values and must not fall through to the raise above."""
    for spelling, expected in [
        ("Mid-Terrace", "terraced"),
        ("Maisonette", "flat"),
        ("Semi-Detached", "semi-detached"),
    ]:
        cert = ti.EpcCertificate(
            lodged_date=dt.date(2019, 1, 1),
            total_floor_area_m2=90.0,
            property_type=spelling,
            build_era_band="1965-1980",
        )
        prior = ti.epc_prior(cert, as_of=AS_OF)
        assert prior.hlc_kw_per_k > 0.0, spelling
        assert expected  # the mapping is exercised by not raising


# ---------------------------------------------------------------------------
# The shrinkage estimator's own invariants
# ---------------------------------------------------------------------------


def _belief(posterior, prior_hlc, prior_sd, meter_hlc, meter_sd):
    prior = ti.HlcPrior(prior_hlc, prior_sd, ti.EvidenceBasis.EPC_ONLY, 90.0, 3.0)
    return ti.ThermalBelief(
        premise_id="X",
        hlc_kw_per_k=posterior,
        relative_sd=min(prior_sd, meter_sd) * 0.9,
        basis=ti.EvidenceBasis.METER_AND_EPC,
        prior=prior,
        meter_hlc_kw_per_k=meter_hlc,
        meter_relative_sd=meter_sd,
        fit=None,
        response_time_constant_hours=None,
    )


def test_bracketing_control_fires_on_a_posterior_outside_its_sources():
    """BOTH WAYS. A shrinkage estimator that lands outside both its inputs has
    a sign or weighting error, and this is the control that says so."""
    assert ti.belief_is_bracketed_by_its_sources(_belief(0.22, 0.20, 0.3, 0.26, 0.2))
    assert not ti.belief_is_bracketed_by_its_sources(
        _belief(0.31, 0.20, 0.3, 0.26, 0.2)
    ), "the bracketing control missed a posterior above both sources"
    assert not ti.belief_is_bracketed_by_its_sources(
        _belief(0.15, 0.20, 0.3, 0.26, 0.2)
    ), "the bracketing control missed a posterior below both sources"


def test_narrowing_control_fires_when_evidence_widens_uncertainty():
    good = _belief(0.22, 0.20, 0.3, 0.26, 0.2)
    assert ti.evidence_narrows_uncertainty(good)
    widened = ti.ThermalBelief(
        premise_id="X",
        hlc_kw_per_k=0.22,
        relative_sd=0.40,  # MUTATION: wider than the prior it started from
        basis=ti.EvidenceBasis.METER_AND_EPC,
        prior=good.prior,
        meter_hlc_kw_per_k=0.26,
        meter_relative_sd=0.2,
        fit=None,
        response_time_constant_hours=None,
    )
    assert not ti.evidence_narrows_uncertainty(widened)


def test_the_blend_is_in_log_space_so_the_lower_bound_stays_positive():
    """A symmetric band on a small HLC with a wide prior would cross zero — a
    house that loses negative heat. The log-space interval cannot."""
    belief = _belief(0.03, 0.028, 0.6, 0.033, 0.5)
    low, high = belief.interval_95
    assert low > 0.0
    assert low < belief.hlc_kw_per_k < high


def test_a_non_positive_gradient_cannot_become_an_hlc():
    with pytest.raises(ValueError, match="non-positive"):
        ti.hlc_from_gradient(0.0, 0.85)
    with pytest.raises(ValueError, match="non-positive"):
        ti.hlc_from_gradient(-3.0, 0.85)


def test_the_gap_metric_rejects_a_degenerate_truth():
    """`relative_gap` is the harness's number; it must refuse to divide by a
    zero or non-finite actual rather than returning inf as a 'score'."""
    assert ti.relative_gap(0.22, 0.20) == pytest.approx(0.10)
    for bad in (0.0, -1.0, float("nan"), float("inf")):
        with pytest.raises(ValueError):
            ti.relative_gap(0.22, bad)
    with pytest.raises(ValueError):
        ti.relative_gap(float("nan"), 0.20)


def test_structural_uncertainty_grows_with_the_read_interval():
    def fit_with(mean_days, intervals=12):
        return ti.HeatingResponseFit(
            balance_point_c=15.5,
            gradient_kwh_per_day_k=7.0,
            baseload_kwh_per_day=3.0,
            gradient_relative_se=0.02,
            r2=0.9,
            n_intervals=intervals,
            days_covered=int(mean_days * intervals),
            hdd_span_k=8.0,
        )

    sds = [
        ti.method_structural_sd(fit_with(days), main_heating_fuel="mains gas")
        for days in (1, 7, 30, 91)
    ]
    assert sds == sorted(sds), f"coarser reads must not read as equally certain: {sds}"
    assert sds[0] == pytest.approx(ti.METHOD_RELATIVE_SD_FLOOR)
    # A heat pump is strictly less certain than the same premise on gas: the
    # company is assuming a flat SCOP away.
    assert ti.method_structural_sd(
        fit_with(1), main_heating_fuel="air source heat pump"
    ) > sds[0]


def test_a_stock_prior_is_never_actionable():
    prior = ti.HlcPrior(0.24, 0.05, ti.EvidenceBasis.STOCK_PRIOR, 92.0, None)
    belief = ti.ThermalBelief(
        premise_id="X",
        hlc_kw_per_k=0.24,
        relative_sd=0.05,  # MUTATION: an absurdly tight sd on a class average
        basis=ti.EvidenceBasis.STOCK_PRIOR,
        prior=prior,
        meter_hlc_kw_per_k=None,
        meter_relative_sd=None,
        fit=None,
        response_time_constant_hours=None,
    )
    assert not belief.is_actionable, (
        "a stock-class average contains no information about THIS premise, so "
        "no width of confidence interval may make it actionable"
    )


# ---------------------------------------------------------------------------
# THE COUPLED MEASUREMENT — belief against W1_12 ground truth
# ---------------------------------------------------------------------------


def test_daily_reads_recover_the_true_hlc_across_the_gas_panel(panel, published_weather):
    """The core claim of the atom: from cumulative gas reads, published mean
    temperatures and an EPC, the company recovers each premise's actual heat
    loss coefficient. Bound is an OUTER bound (measured 0.2–4% on 2026-08-03),
    not a pinned value."""
    gaps = {}
    for entry in panel:
        if entry[3] != "gas":
            continue
        belief = believe(entry, published_weather)
        assert belief.basis is ti.EvidenceBasis.METER_AND_EPC
        gaps[entry[0]] = ti.relative_gap(belief.hlc_kw_per_k, actual_hlc(entry))
    assert gaps, "the gas panel is empty — this test would pass vacuously"
    assert max(gaps.values()) < 0.15, gaps


_MATERIALLY_WRONG_PRIOR = 0.05
"""A certificate within 5% of the truth is already a good answer. Demanding that
meter evidence improve on it is not a claim about meter evidence — it is a coin
flip on the fourth decimal place."""


def test_meter_evidence_beats_the_certificate_WHERE_THE_CERTIFICATE_IS_WRONG(
    panel, published_weather
):
    """Why a supplier bothers reading meters, stated as the claim it actually is.

    SPLIT FROM a single `improved >= len(panel) - 1` counter on 2026-08-08. That
    counter conflated two different things and, because it allowed exactly one
    failure, spent its whole allowance hiding a real defect — see the pinned
    degradation below. It was also passing on a knife edge: `gas-semi-1965`
    counted as "improved" by 0.0007 of relative gap on a prior already accurate
    to 2.3%, so any change anywhere in the world could flip it, and a W1_12
    fidelity fix duly did.

    The claim worth making is this one: where the certificate is MATERIALLY
    wrong, reading the meter must fix it.
    """
    checked = 0
    for entry in panel:
        belief = believe(entry, published_weather)
        truth = actual_hlc(entry)
        prior_gap = ti.relative_gap(belief.prior.hlc_kw_per_k, truth)
        if prior_gap < _MATERIALLY_WRONG_PRIOR:
            continue
        checked += 1
        assert ti.relative_gap(belief.hlc_kw_per_k, truth) < prior_gap, (
            f"{entry[0]}: the certificate is {prior_gap:.1%} wrong and meter "
            "evidence failed to improve on it"
        )
    assert checked >= 3, (
        f"only {checked} panel premises have a materially wrong certificate — "
        "this test would be near-vacuous; widen the panel rather than trust it"
    )


@pytest.mark.xfail(
    strict=True,
    reason=(
        "PRE-EXISTING DEFECT, isolated and measured 2026-08-08. `ashp-semi-1981` "
        "is the one HEAT-PUMP premise on the panel, so its space heating is in "
        "the ELECTRICITY read: the inference must separate heating from a "
        "non-heating baseline it cannot see, and it does not. Its EPC prior is "
        "0.4% from truth and meter evidence takes the belief to 25.5% — the "
        "evidence makes a good answer sixty times worse. "
        "OLDER THAN THE W1_12 WORK THAT SURFACED IT: reverting BOTH 2026-08-08 "
        "generator changes (routine offset clamped to zero, switched banks "
        "restored to their continuous expectation) leaves it at 25.7%, so the "
        "world change is not the cause — it merely stopped the "
        "`improved >= len(panel) - 1` slack from absorbing it. "
        "STRICT so the fix cannot land unnoticed. Queued as company-side work on "
        "C14: the gas panel is unaffected and stays green."
    ),
)
def test_meter_evidence_never_MATERIALLY_DEGRADES_a_good_certificate(
    panel, published_weather
):
    """The other half of the split: evidence may fail to help, but it must not
    take a premise whose certificate was right and make it badly wrong."""
    for entry in panel:
        belief = believe(entry, published_weather)
        truth = actual_hlc(entry)
        prior_gap = ti.relative_gap(belief.prior.hlc_kw_per_k, truth)
        if prior_gap >= _MATERIALLY_WRONG_PRIOR:
            continue
        assert ti.relative_gap(belief.hlc_kw_per_k, truth) < _MATERIALLY_WRONG_PRIOR, (
            f"{entry[0]}: certificate was {prior_gap:.1%} from truth; meter "
            f"evidence moved the belief to "
            f"{ti.relative_gap(belief.hlc_kw_per_k, truth):.1%}"
        )


def test_the_confidence_band_actually_covers_the_truth(panel, published_weather):
    """CALIBRATION, and the control that makes the uncertainty model failable.
    A 95% band that never contains the answer is decoration."""
    misses = []
    for entry in panel:
        belief = believe(entry, published_weather)
        low, high = belief.interval_95
        if not low <= actual_hlc(entry) <= high:
            misses.append((entry[0], low, actual_hlc(entry), high))
    assert not misses, f"the 95% band missed the truth: {misses}"


def test_the_heat_pump_premise_is_both_wronger_and_less_certain(panel, published_weather):
    """The flat-SCOP assumption biting, stated as a relationship. The company
    over-reads fabric loss on a heat pump because cold-day electricity rises
    faster than linearly in degree days — and it must SAY it is less sure."""
    ashp = next(e for e in panel if e[3] == "electricity")
    gas = next(e for e in panel if e[3] == "gas")
    ashp_belief = believe(ashp, published_weather)
    gas_belief = believe(gas, published_weather)

    assert ashp_belief.meter_hlc_kw_per_k > actual_hlc(ashp), (
        "a flat SCOP should make the meter over-read a heat pump's fabric loss"
    )
    assert ashp_belief.relative_sd > gas_belief.relative_sd
    assert ti.relative_gap(
        ashp_belief.meter_hlc_kw_per_k, actual_hlc(ashp)
    ) > ti.relative_gap(gas_belief.meter_hlc_kw_per_k, actual_hlc(gas))


def test_coarser_reads_are_reported_as_less_certain(panel, published_weather):
    """THE DEFECT THIS CONTROL EXISTS FOR (measured 2026-08-03): before the
    cadence term, monthly reads were 18% out while reporting the same
    confidence as daily reads that were 0.2% out."""
    entry = next(e for e in panel if e[3] == "gas")
    sds = []
    for cadence in (1, 7, 30):
        belief = believe(entry, published_weather, every_n_days=cadence)
        assert belief.meter_hlc_kw_per_k is not None, cadence
        sds.append(belief.relative_sd)
    assert sds == sorted(sds) and sds[0] < sds[-1], sds


def test_the_cadence_control_fires_when_the_cadence_term_is_removed(
    panel, published_weather, monkeypatch
):
    """MUTATION: set the cadence term to zero — the defect as it stood before
    the fix — and the monotonicity above must collapse."""
    monkeypatch.setattr(ti, "CADENCE_SD_PER_INTERVAL_DOUBLING", 0.0)
    entry = next(e for e in panel if e[3] == "gas")
    sds = [
        believe(entry, published_weather, every_n_days=c).relative_sd
        for c in (1, 30)
    ]
    assert sds[1] - sds[0] < 0.02, (
        "with the cadence term removed the sds should be near-identical — if "
        "they still separate, this control is not testing what it claims to"
    )


def test_a_stale_certificate_is_rescued_by_the_meter(panel, published_weather):
    """EPC staleness, end to end: a premise insulated since its certificate was
    lodged. The paper is wrong; the meter is not."""
    entry = next(e for e in panel if e[0] == "gas-semi-1965")
    truth = actual_hlc(entry)
    stale = believe(
        entry,
        published_weather,
        lodged=dt.date(2013, 6, 1),
        insulation="poor",  # the pre-retrofit fabric the certificate describes
    )
    assert stale.prior.certificate_age_years > 9.0
    assert ti.relative_gap(stale.hlc_kw_per_k, truth) < ti.relative_gap(
        stale.prior.hlc_kw_per_k, truth
    )
    assert stale.prior.relative_sd > ti.EPC_MODELLING_RELATIVE_SD


def test_no_certificate_plus_coarse_reads_fails_closed(panel, published_weather):
    """EPC absence AND an unfittable read history: the company must end up with
    a labelled stock prior it refuses to act on, not a number."""
    entry = next(e for e in panel if e[3] == "gas")
    belief = believe(
        entry, published_weather, every_n_days=91, certificate=None
    )
    assert belief.basis is ti.EvidenceBasis.STOCK_PRIOR
    assert not belief.is_actionable
    assert any("no usable meter evidence" in note for note in belief.notes)


def test_no_certificate_but_good_reads_still_yields_a_belief(panel, published_weather):
    """The other half: absence alone must not disqualify a premise the company
    has genuinely measured. 40% of the stock has no EPC."""
    entry = next(e for e in panel if e[3] == "gas")
    belief = believe(entry, published_weather, certificate=None)
    assert belief.basis is ti.EvidenceBasis.METER_ONLY
    assert belief.is_actionable
    assert ti.relative_gap(belief.hlc_kw_per_k, actual_hlc(entry)) < 0.20


GENERIC_CERT = ti.EpcCertificate(
    lodged_date=dt.date(2019, 1, 1),
    total_floor_area_m2=90.0,
    property_type="semi-detached",
    build_era_band="1965-1980",
    insulation="partial",
)


def noisy_weak_response_reads(published_weather):
    """A read history that IS weakly weather-responsive but is dominated by
    something else — an erratic occupancy, a second heat source, a landlord's
    void period. Deliberately constructed so the gradient stays POSITIVE and
    only the r2 floor can reject it: a fixture whose gradient was zero would be
    rejected by the sign test instead, and the mutation below would prove
    nothing about the floor."""
    reads = [ti.MeterRead(published_weather[0].date - dt.timedelta(days=1), 0.0)]
    cumulative = 0.0
    for index in range(26):
        window = published_weather[index * 14 : (index + 1) * 14]
        if len(window) < 14:
            break
        hdd = sum(max(0.0, 15.5 - day.mean_temp_c) for day in window)
        # Weak real signal, large deterministic swing that no weather series
        # explains — r2 collapses while the slope stays positive. The swing is
        # ADDITIVE-ONLY: a register that went backwards would be rejected by
        # the meter-history guard instead, which is a different control.
        cumulative += 60.0 + 0.4 * hdd + (70.0 if index % 2 else 0.0)
        reads.append(ti.MeterRead(window[-1].date, cumulative))
    return reads


def test_demand_that_barely_responds_to_weather_is_refused(published_weather):
    """A premise whose meter is dominated by something other than the weather.
    The company must fall back to the certificate and SAY it did."""
    reads = noisy_weak_response_reads(published_weather)
    fit = ti.fit_heating_response(reads, published_weather)
    assert fit.gradient_kwh_per_day_k > 0.0, (
        "fixture check: the gradient must be positive so that the r2 floor, "
        "not the sign test, is the control being exercised"
    )
    assert fit.r2 < ti.MIN_FIT_R2

    belief = ti.infer_thermal_parameters(
        premise_id="weak-response",
        reads=reads,
        weather=published_weather,
        certificate=GENERIC_CERT,
        as_of=AS_OF,
    )
    assert belief.basis is ti.EvidenceBasis.EPC_ONLY
    assert belief.meter_hlc_kw_per_k is None
    assert any("not degree-day responsive" in note for note in belief.notes)


def test_the_r2_floor_control_fires_when_it_is_removed(published_weather, monkeypatch):
    """MUTATION: drop the r2 floor to zero and the same history now produces a
    meter-derived belief — exactly the fail-open the floor exists to stop."""
    monkeypatch.setattr(ti, "MIN_FIT_R2", 0.0)
    belief = ti.infer_thermal_parameters(
        premise_id="weak-response",
        reads=noisy_weak_response_reads(published_weather),
        weather=published_weather,
        certificate=GENERIC_CERT,
        as_of=AS_OF,
    )
    assert belief.basis is ti.EvidenceBasis.METER_AND_EPC, (
        "with the floor removed the unresponsive history should have been "
        "accepted — if it still is not, the floor is not what rejected it"
    )


def test_a_flat_history_is_rejected_by_the_sign_test_and_says_so(published_weather):
    """The neighbouring case, and the diagnostic that used to lie about it: a
    genuinely flat meter is refused for a NON-POSITIVE GRADIENT, not for r2."""
    flat = [
        ti.MeterRead(WINDOW_START + dt.timedelta(days=14 * i), 42.0 * i)
        for i in range(20)
    ]
    belief = ti.infer_thermal_parameters(
        premise_id="flat-demand",
        reads=flat,
        weather=published_weather,
        certificate=GENERIC_CERT,
        as_of=AS_OF,
    )
    assert belief.basis is ti.EvidenceBasis.EPC_ONLY
    assert any("is not positive" in note for note in belief.notes), belief.notes


def test_the_response_time_constant_is_only_claimed_when_it_can_be_seen(
    panel, published_weather
):
    """Honest absence. Daily reads can see thermal memory; monthly reads
    cannot, and the company must return None rather than a number."""
    entry = next(e for e in panel if e[3] == "gas")
    daily = believe(entry, published_weather, every_n_days=1)
    monthly = believe(entry, published_weather, every_n_days=30)

    assert daily.response_time_constant_hours is not None
    assert 2.0 < daily.response_time_constant_hours < 120.0
    assert monthly.response_time_constant_hours is None
    assert any("too coarse" in note for note in monthly.notes)


def test_the_response_constant_discriminates_between_homes(panel, published_weather):
    """What the lag estimate DOES deliver: a per-home number that varies. If it
    collapsed to one value it would be a national constant wearing a per-premise
    label — the exact defect W1_11 was minted to remove."""
    taus = [
        believe(entry, published_weather).response_time_constant_hours
        for entry in panel
        if entry[3] == "gas"
    ]
    taus = [t for t in taus if t is not None]
    assert len(taus) >= 3
    assert all(2.0 < t < 120.0 for t in taus), taus
    assert max(taus) / min(taus) > 1.2, f"response constants barely differ: {taus}"


@pytest.mark.xfail(
    strict=True,
    reason=(
        "MEASURED NEGATIVE RESULT, 2026-08-03 — recorded, deliberately NOT "
        "tuned away. The daily-lag memory fraction does NOT recover fabric "
        "mass ordering: the pre-1919 solid-wall detached house came out at "
        "13.3 h against the post-2000 flat's 21.8 h, i.e. backwards. The "
        "estimate is a DEMAND-response constant, and demand memory is "
        "dominated by the occupant's setback schedule and by the heat source's "
        "recovery power, not by the structure. Fixing this needs an estimator "
        "that separates the controller from the fabric (the UKF the FRAME left "
        "open), which is a level-3 escalation this atom has not earned. "
        "STRICT so that an estimator improvement FAILS here and forces the "
        "claim in the module docstring to be corrected rather than silently "
        "outgrown."
    ),
)
def test_heavier_fabric_is_inferred_to_remember_for_longer(panel, published_weather):
    """The claim this atom does NOT support, kept executable so it cannot be
    quietly assumed by anything downstream."""
    heavy = next(e for e in panel if e[0] == "gas-detached-pre1919")
    light = next(e for e in panel if e[0] == "gas-flat-post2000")
    heavy_tau = believe(heavy, published_weather).response_time_constant_hours
    light_tau = believe(light, published_weather).response_time_constant_hours
    assert heavy_tau is not None and light_tau is not None
    assert heavy_tau > light_tau, (
        f"heavy fabric {heavy_tau:.1f}h should out-remember light {light_tau:.1f}h"
    )


def test_every_belief_is_internally_consistent(panel, published_weather):
    """The two standing controls applied across the whole panel — bracketing
    and narrowing — so a regression in the blend shows up on real beliefs and
    not only on the hand-built ones above."""
    for entry in panel:
        belief = believe(entry, published_weather)
        assert ti.belief_is_bracketed_by_its_sources(belief), entry[0]
        assert ti.evidence_narrows_uncertainty(belief), entry[0]
        assert belief.hlc_per_m2_w_per_k > 0.0
        low, high = belief.interval_95
        assert 0.0 < low < belief.hlc_kw_per_k < high
