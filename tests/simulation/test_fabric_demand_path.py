"""The fabric seam into the shipped demand path — `simulation.fabric_demand_path`.

R15 DISCIPLINE: every control in the module is exercised BOTH ways here — it
passes on the real seam AND a named mutation proves it fires on the specific
defect it exists to catch. A bare "control returns True" assertion never appears
alone in this file.

The defect the seam itself exists to close is named in each mutation: a fabric
trace stacked on top of the legacy overlays (double count), a trace with a hole in
it (a settlement day priced at nothing), a trace flattened between the generator
and the seam (the texture drained in the plumbing), and — the one that was live on
the shipped path — a prebound response whose `prior_year_bill_gbp` input no caller
ever supplied, so every household heated to full SAP comfort however expensive its
dwelling was to run.
"""

from __future__ import annotations

import dataclasses
import datetime as dt

import pytest

from simulation import fabric_demand_path as fdp
from simulation import premise_trace as pt
from simulation.household import BuildEra, IncomeStress, InsulationLevel, PropertyType
from tests.simulation.test_premise_trace import make_household

# Short windows keep this suite cheap (~1.2 ms per premise-day). The prebound
# tests need two calendar years, which is the response's own unit of time.
WINDOW_START = dt.date(2021, 11, 1)
WINDOW_END = dt.date(2022, 2, 28)
TWO_YEAR_START = dt.date(2021, 1, 1)
TWO_YEAR_END = dt.date(2022, 12, 31)
LATITUDE = 53.0


@pytest.fixture(scope="module")
def weather() -> list[pt.TraceWeatherDay]:
    """The REAL Open-Meteo archive — Historical Ground Truth, never a synthetic
    shape. A missing file must FAIL this suite, not skip it."""
    return pt.load_trace_weather("C1", start=WINDOW_START, end=WINDOW_END)


@pytest.fixture(scope="module")
def two_year_weather() -> list[pt.TraceWeatherDay]:
    return pt.load_trace_weather("C1", start=TWO_YEAR_START, end=TWO_YEAR_END)


def constant_household(household):
    return lambda _date_str: household


@pytest.fixture(scope="module")
def series(weather):
    household = make_household("C1")
    return fdp.build_fabric_series(
        customer_id="C1",
        household_at_date=constant_household(household),
        weather=weather,
        latitude_deg=LATITUDE,
    )


# ---------------------------------------------------------------------------
# Eligibility — decided from real fields, with the reason kept
# ---------------------------------------------------------------------------


def test_a_domestic_premise_with_weather_is_fabric_driven():
    verdict = fdp.fabric_eligibility(
        {"customer_id": "C1"},
        make_household("C1"),
        is_half_hourly_metered=False,
        weather_available=True,
    )
    assert verdict.is_eligible is True
    assert verdict.customer_id == "C1"


@pytest.mark.parametrize(
    "kwargs, household, expected_in_reason",
    [
        ({"is_half_hourly_metered": True, "weather_available": True}, make_household(), "metered"),
        ({"is_half_hourly_metered": False, "weather_available": True}, None, "no household"),
        (
            {"is_half_hourly_metered": False, "weather_available": True},
            make_household(property_type=PropertyType.COMMERCIAL_OFFICE, bedrooms=None),
            "non-domestic",
        ),
        (
            {"is_half_hourly_metered": False, "weather_available": True},
            make_household(bedrooms=None),
            "bedroom",
        ),
        ({"is_half_hourly_metered": False, "weather_available": False}, make_household(), "weather"),
    ],
)
def test_every_exclusion_carries_its_reason(kwargs, household, expected_in_reason):
    verdict = fdp.fabric_eligibility({"customer_id": "C1"}, household, **kwargs)
    assert verdict.is_eligible is False
    assert expected_in_reason in verdict.reason


def test_a_customer_without_an_id_cannot_be_classified():
    """FAIL-OPEN guard: an unidentifiable customer must raise, never quietly
    return 'not eligible' and take the legacy path unnoticed."""
    with pytest.raises(ValueError):
        fdp.fabric_eligibility(
            {}, make_household(), is_half_hourly_metered=False, weather_available=True
        )


# ---------------------------------------------------------------------------
# Segmentation — the LCT timeline
# ---------------------------------------------------------------------------


def test_a_life_event_starts_a_new_segment():
    before, after = make_household("C1"), make_household("C1", has_ev=True, ev_charger_kw=7.0)
    dates = [dt.date(2021, 3, 1) + dt.timedelta(days=i) for i in range(10)]
    segments = fdp.household_segments(
        lambda d: before if d < "2021-03-06" else after, dates
    )
    assert [s.n_days for s in segments] == [5, 5]
    assert segments[0].household.has_ev is False and segments[1].household.has_ev is True


def test_the_new_year_starts_a_new_segment():
    """The prebound response is re-evaluated annually, so 1 January is a boundary
    even when nothing about the household changed."""
    dates = [dt.date(2021, 12, 30) + dt.timedelta(days=i) for i in range(4)]
    segments = fdp.household_segments(constant_household(make_household()), dates)
    assert [s.year for s in segments] == [2021, 2022]


def test_segmenting_an_empty_window_raises():
    with pytest.raises(ValueError):
        fdp.household_segments(constant_household(make_household()), [])


def test_a_missing_household_raises_rather_than_skipping_the_day():
    with pytest.raises(ValueError):
        fdp.household_segments(lambda _d: None, [dt.date(2021, 3, 1)])


def test_the_thermal_state_chains_across_a_segment_boundary(two_year_weather):
    """The reason `PremiseTrace.final_state` exists. Generated in segments with the
    state chained, the New Year's Day demand must look like an ordinary winter day —
    not like a house whose walls were reset to setback overnight."""
    household = make_household("C1")
    series = fdp.build_fabric_series(
        customer_id="C1",
        household_at_date=constant_household(household),
        weather=two_year_weather,
        latitude_deg=LATITUDE,
    )
    boundary = sum(series.gas_kwh["2022-01-01"])
    neighbours = [
        sum(series.gas_kwh[d]) for d in ("2021-12-30", "2021-12-31", "2022-01-02", "2022-01-03")
    ]
    assert boundary <= 1.4 * max(neighbours), (
        f"segment-boundary spike: {boundary:.1f} kWh against neighbours {neighbours}"
    )


# ---------------------------------------------------------------------------
# The seam
# ---------------------------------------------------------------------------


def test_the_shape_fn_returns_a_settlement_day(series):
    shape = fdp.fabric_shape_fn(series)("2021-11-15")
    assert len(shape) == 48
    assert all(v >= 0.0 for v in shape)
    assert sum(shape) > 0.0


def test_a_date_outside_the_trace_raises_rather_than_settling_at_zero(series):
    """FAIL-OPEN guard. The legacy provider falls back to an unadjusted base shape
    on a weatherless day; doing that here would settle a physically-driven customer
    against a national average and hide it in the totals."""
    with pytest.raises(KeyError):
        fdp.fabric_shape_fn(series)("1999-01-01")


def test_an_unknown_commodity_raises(series):
    with pytest.raises(ValueError):
        fdp.fabric_shape_fn(series, "hydrogen")


def test_electricity_is_returned_net_of_on_site_generation(weather):
    solar = make_household("C1", has_solar=True, solar_kwp=3.5)
    solar_series = fdp.build_fabric_series(
        customer_id="C1",
        household_at_date=constant_household(solar),
        weather=weather,
        latitude_deg=LATITUDE,
    )
    day = "2022-02-20"
    gross = sum(solar_series.gross_electricity_kwh[day])
    net = sum(fdp.fabric_shape_fn(solar_series)(day))
    assert sum(solar_series.pv_generation_kwh[day]) > 0.0
    assert net < gross


def test_the_battery_composition_is_left_to_the_caller(series):
    """The one asset the trace generator does not model. The seam hands the caller
    gross and generation so its existing dispatch keeps working unchanged."""
    seen = {}

    def dispatch(gross, generation, date_str):
        seen["date"] = date_str
        return [0.5 * v for v in gross]

    shape = fdp.fabric_shape_fn(series, battery_dispatch=dispatch)("2021-11-15")
    assert seen["date"] == "2021-11-15"
    assert sum(shape) == pytest.approx(0.5 * sum(series.gross_electricity_kwh["2021-11-15"]))


def test_the_series_is_deterministic_in_its_seed(weather):
    household = make_household("C1")
    kwargs = dict(
        customer_id="C1",
        household_at_date=constant_household(household),
        weather=weather,
        latitude_deg=LATITUDE,
    )
    assert (
        fdp.build_fabric_series(**kwargs).gas_kwh
        == fdp.build_fabric_series(**kwargs).gas_kwh
    )


def test_an_empty_window_raises(weather):
    with pytest.raises(ValueError):
        fdp.build_fabric_series(
            customer_id="C1",
            household_at_date=constant_household(make_household()),
            weather=[],
            latitude_deg=LATITUDE,
        )


def test_a_non_positive_reference_price_raises(weather):
    with pytest.raises(ValueError):
        fdp.build_fabric_series(
            customer_id="C1",
            household_at_date=constant_household(make_household()),
            weather=weather,
            latitude_deg=LATITUDE,
            reference_unit_price_p_per_kwh=0.0,
        )


# ---------------------------------------------------------------------------
# R15 — the controls, both ways
# ---------------------------------------------------------------------------


def test_overlays_are_mutually_exclusive_passes_for_a_fabric_driven_customer():
    assert fdp.overlays_are_mutually_exclusive(True, []) is True
    assert fdp.overlays_are_mutually_exclusive(False, list(fdp.LEGACY_OVERLAYS)) is True


def test_MUTATION_overlays_control_fires_on_the_double_count():
    """The defect: the fabric trace already contains the heating fuel and the EV,
    so applying the legacy uplifts on top bills the same energy twice."""
    assert (
        fdp.overlays_are_mutually_exclusive(True, ["ashp_electricity_uplift"]) is False
    )
    assert fdp.overlays_are_mutually_exclusive(True, ["overnight_ev_overlay"]) is False


def test_the_overlay_control_raises_on_an_overlay_it_does_not_recognise():
    """FAIL-OPEN guard: a control that ignores what it cannot classify passes a
    double count it simply did not know the name of."""
    with pytest.raises(ValueError):
        fdp.overlays_are_mutually_exclusive(True, ["some_future_uplift"])


def test_series_covers_window_passes_on_the_real_series(series, weather):
    assert fdp.series_covers_window(series, [d.date for d in weather]) is True


def test_MUTATION_coverage_control_fires_on_a_hole_in_the_trace(series, weather):
    holed = dataclasses.replace(
        series,
        gross_electricity_kwh={
            k: v for k, v in series.gross_electricity_kwh.items() if k != "2021-11-15"
        },
    )
    assert fdp.series_covers_window(holed, [d.date for d in weather]) is False


def test_the_coverage_control_raises_on_an_empty_window(series):
    with pytest.raises(ValueError):
        fdp.series_covers_window(series, [])


def test_texture_control_passes_on_the_real_series(series):
    assert fdp.trace_carries_half_hourly_texture(series) is True


def test_MUTATION_texture_control_fires_when_the_seam_flattens_the_day(series):
    """The plumbing defect: a daily total spread evenly across 48 periods. The
    annual level is untouched and every total reconciles — and the whole reason
    this atom exists is gone."""
    flattened = {
        day: [sum(values) / 48] * 48 for day, values in series.gross_electricity_kwh.items()
    }
    mutant = dataclasses.replace(series, gross_electricity_kwh=flattened)
    assert fdp.trace_carries_half_hourly_texture(mutant) is False


def test_the_texture_control_raises_on_a_series_too_short_to_have_a_distribution(series):
    one_day = dataclasses.replace(
        series,
        gross_electricity_kwh=dict(list(series.gross_electricity_kwh.items())[:1]),
    )
    with pytest.raises(ValueError):
        fdp.trace_carries_half_hourly_texture(one_day)


# ---------------------------------------------------------------------------
# The prebound channel — the live mechanism with the dead input
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def expensive_dwelling_series(two_year_weather):
    """A pre-1919 solid-wall detached: the dwelling class where the empirical
    prebound gap is largest, and the one the shipped path heated to full SAP
    comfort because nothing ever told it what the heating cost."""
    household = make_household(
        "C4",
        property_type=PropertyType.DETACHED,
        build_era=BuildEra.PRE_1919,
        insulation=InsulationLevel.POOR,
        bedrooms=4,
    )
    return fdp.build_fabric_series(
        customer_id="C4",
        household_at_date=constant_household(household),
        weather=two_year_weather,
        latitude_deg=LATITUDE,
    )


def test_the_prebound_channel_is_fed_on_an_expensive_dwelling(expensive_dwelling_series):
    series = expensive_dwelling_series
    assert fdp.prebound_channel_is_fed(series) is True
    years = sorted(series.constraint_by_year)
    assert series.constraint_by_year[years[1]].rationing_intensity > (
        series.constraint_by_year[years[0]].rationing_intensity
    ), "a household with an unaffordable heating bill did not turn anything down"


def test_MUTATION_prebound_control_fires_when_the_bill_is_never_threaded(
    expensive_dwelling_series,
):
    """THE DEFECT THIS SEAM CLOSED. `comfort_constraint_for` has always accepted
    `prior_year_bill_gbp`; no caller on the shipped path supplied it, so the
    mechanism was live and its input was dead. This mutant reproduces exactly that
    — every year generated with the same unfed constraint — and the control fires."""
    unfed = pt.comfort_constraint_for(income_stress=IncomeStress.LOW)
    mutant = dataclasses.replace(
        expensive_dwelling_series,
        constraint_by_year={
            year: unfed for year in expensive_dwelling_series.constraint_by_year
        },
    )
    assert fdp.prebound_channel_is_fed(mutant) is False


def test_a_cheap_dwelling_is_legitimately_unconstrained(two_year_weather):
    """The control asks whether the CHANNEL works, not whether every household
    rations. A well-insulated flat whose bill never reaches the affordability
    reference should not be turning the heating down, and is reported satisfied."""
    flat = make_household(
        "C1", property_type=PropertyType.FLAT, insulation=InsulationLevel.FULL, bedrooms=2
    )
    series = fdp.build_fabric_series(
        customer_id="C1",
        household_at_date=constant_household(flat),
        weather=two_year_weather,
        latitude_deg=LATITUDE,
    )
    bill = series.annual_gas_kwh * pt.REFERENCE_UNIT_PRICE_P_PER_KWH / 100.0
    assert bill < fdp._AFFORDABLE_BILL_REFERENCE_GBP
    assert fdp.prebound_channel_is_fed(series) is True


def test_the_prebound_control_raises_on_a_single_year(two_year_weather):
    """A response to LAST year's bill is not observable inside one year. Passing
    such a series would be the fail-silent form of this control."""
    one_year = fdp.build_fabric_series(
        customer_id="C1",
        household_at_date=constant_household(make_household("C1")),
        weather=[d for d in two_year_weather if d.date.year == 2021],
        latitude_deg=LATITUDE,
    )
    assert len(one_year.constraint_by_year) == 1
    with pytest.raises(ValueError):
        fdp.prebound_channel_is_fed(one_year)


def test_the_affordability_reference_has_not_drifted():
    """`_AFFORDABLE_BILL_REFERENCE_GBP` is restated from `comfort_constraint_for`'s
    own default so the control can judge whether a premise SHOULD have responded.
    Two copies of a number drift; this fails when they do."""
    import inspect

    default = inspect.signature(pt.comfort_constraint_for).parameters[
        "affordable_bill_gbp"
    ].default
    assert fdp._AFFORDABLE_BILL_REFERENCE_GBP == default


def test_the_heating_commodity_of_a_gas_home_is_gas(series):
    assert series.heating_commodity == "gas"
    assert series.annual_gas_kwh > series.annual_electricity_kwh
