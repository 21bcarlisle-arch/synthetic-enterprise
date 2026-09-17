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


def test_two_uncovered_premises_do_not_receive_the_same_archive_refusal():
    """THE DEFECT: until 2026-09-16 every premise with no archive got one identical sentence --
    "no weather archive for this customer's location" -- so 213 refusals in the settling book
    named 213 nothings and could not tell anyone WHICH archives to pull.

    Asked of `reason` ALONE and not of the verdict, because `customer_id` already differs between
    any two premises: a distinguishability control asked over the union of the fields passes with
    the defect fully in place (R15).
    """
    def refusal(cid, lat, lon, site):
        verdict = fdp.fabric_eligibility(
            {"customer_id": cid, "location": {"lat": lat, "lon": lon}},
            make_household(cid),
            is_half_hourly_metered=False,
            weather_available=False,
            weather_site=site,
        )
        assert verdict.is_eligible is False
        return verdict.reason

    birmingham = refusal("C_B", 52.4862, -1.8904, "C_B")
    teesside = refusal("C_T", 54.5973, -1.1049, "C_T")

    assert birmingham != teesside
    # Not merely different -- each names the coordinate a pull would be aimed at.
    assert "52.4862" in birmingham and "-1.8904" in birmingham
    assert "54.5973" in teesside and "-1.1049" in teesside
    # And both are still grouped by the shared prefix the book's coverage count reads.
    assert birmingham.startswith(fdp.NO_ARCHIVE_REFUSAL)
    assert teesside.startswith(fdp.NO_ARCHIVE_REFUSAL)


def test_a_premise_with_no_coordinate_is_not_told_to_pull_an_archive():
    """The refusal splits, because the two populations need OPPOSITE things. A premise with a
    real coordinate is cleared by a pull; a premise carrying `lat: None` is cleared only by a
    coordinate at the draw, and printing a pull instruction for it would send someone to fetch a
    location nobody has. Kept as its own control so the split cannot be collapsed back into one
    sentence without a red."""
    verdict = fdp.fabric_eligibility(
        {"customer_id": "C_NONE", "location": {"lat": None, "lon": None}},
        make_household("C_NONE"),
        is_half_hourly_metered=False,
        weather_available=False,
        weather_site="C_NONE",
    )
    assert verdict.is_eligible is False
    assert verdict.reason.startswith(fdp.NO_ARCHIVE_REFUSAL)
    assert "no coordinate" in verdict.reason
    assert "NO PULL CAN CLEAR THIS ONE" in verdict.reason
    assert "does not exist -- pull that coordinate" not in verdict.reason


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


# ---------------------------------------------------------------------------
# The book-level provider set, and THE SWITCH
#
# `fabric_eligibility` deciding a premise is fabric-driven has never made the
# runner USE the trace: the branch that chooses the provider is separate code.
# A switch that is declared but not thrown reads identically to one that is
# thrown from everywhere except the settled numbers, which is why the control
# below judges the SETTLED book rather than the intention.
# ---------------------------------------------------------------------------


def _book(**overrides):
    """A miniature book: one domestic premise, one half-hourly-metered premise,
    one commercial premise. Enough for every branch of the switch."""
    households = {
        "C1": make_household("C1"),
        "HH1": make_household("HH1"),
        "OFF1": make_household("OFF1", property_type=PropertyType.COMMERCIAL_OFFICE,
                               bedrooms=None),
    }
    kwargs = dict(
        customers=[{"customer_id": cid} for cid in households],
        household_at_date=lambda cid, _date_str: households[cid],
        is_half_hourly_metered=lambda c: c["customer_id"] == "HH1",
        weather_site_for=lambda _c: "C1",
        weather_available=lambda _site: True,
        latitude_for=lambda _c: LATITUDE,
        start=WINDOW_START,
        end=WINDOW_END,
    )
    kwargs.update(overrides)
    return kwargs


def test_the_provider_pass_judges_every_customer_not_only_the_eligible_ones():
    """A caller must be able to say WHY a premise is not fabric-driven, rather
    than infer it from an absence — an unexplained population drop between two
    runs is exactly what a bare `{cid: series}` dict hides."""
    series_by_customer, verdicts = fdp.fabric_providers_for_book(**_book())
    assert sorted(series_by_customer) == ["C1"]
    assert sorted(v.customer_id for v in verdicts) == ["C1", "HH1", "OFF1"]
    reasons = {v.customer_id: v.reason for v in verdicts if not v.is_eligible}
    assert "metered" in reasons["HH1"]
    assert "non-domestic" in reasons["OFF1"]


def test_an_empty_settlement_window_has_no_providers():
    """FAIL-OPEN guard: an inverted window must raise, never return an empty
    provider set that reads as 'nobody is eligible'."""
    with pytest.raises(ValueError):
        fdp.fabric_providers_for_book(**_book(start=WINDOW_END, end=WINDOW_START))


def test_a_premise_whose_archive_stops_short_is_refused_UP_FRONT_not_mid_run():
    """COVERAGE IS PART OF ELIGIBILITY. The C1 archive ends 2025-06-07, so a
    window running past it cannot be settled on fabric. The premise must be
    recorded ineligible with that reason BEFORE any settlement happens — the
    alternative is a `shape_fn` that raises on the first uncovered day, halfway
    through a run that has already billed nine years."""
    series_by_customer, verdicts = fdp.fabric_providers_for_book(
        **_book(start=dt.date(2025, 5, 1), end=dt.date(2025, 8, 31))
    )
    assert series_by_customer == {}
    c1 = next(v for v in verdicts if v.customer_id == "C1")
    assert c1.is_eligible is False
    assert "does not cover" in c1.reason


def test_the_switch_control_passes_on_a_correctly_switched_book():
    _, verdicts = fdp.fabric_providers_for_book(**_book())
    providers = {
        "C1": fdp.FABRIC_PROVIDER,
        "HH1": fdp.METERED_PROVIDER,
        "OFF1": fdp.LEGACY_PROVIDER,
    }
    assert fdp.settlement_providers_match_eligibility(providers, verdicts) is True


def test_MUTATION_switch_control_fires_when_the_switch_is_DECLARED_BUT_NOT_THROWN():
    """The defect this control exists for, and the one the seam sat in for a
    build: the eligibility pass runs, the trace is generated, and the branch
    keeps handing the legacy rescaled-PC1 shape to settlement anyway."""
    _, verdicts = fdp.fabric_providers_for_book(**_book())
    providers = {
        "C1": fdp.LEGACY_PROVIDER,   # <-- eligible, but settled on the old provider
        "HH1": fdp.METERED_PROVIDER,
        "OFF1": fdp.LEGACY_PROVIDER,
    }
    assert fdp.settlement_providers_match_eligibility(providers, verdicts) is False


def test_MUTATION_switch_control_fires_when_a_trace_less_premise_is_given_fabric():
    """The opposite defect: a branch keyed on something other than the trace
    dict hands a fabric provider to a premise with no trace — which in the
    runner would raise on the first settlement day, and here is caught first."""
    _, verdicts = fdp.fabric_providers_for_book(**_book())
    providers = {
        "C1": fdp.FABRIC_PROVIDER,
        "HH1": fdp.FABRIC_PROVIDER,   # <-- half-hourly metered, no trace exists
        "OFF1": fdp.LEGACY_PROVIDER,
    }
    assert fdp.settlement_providers_match_eligibility(providers, verdicts) is False


def test_the_switch_control_raises_on_a_provider_it_cannot_classify():
    _, verdicts = fdp.fabric_providers_for_book(**_book())
    with pytest.raises(ValueError, match="unrecognised demand provider"):
        fdp.settlement_providers_match_eligibility(
            {"C1": "some_new_generator", "HH1": fdp.METERED_PROVIDER,
             "OFF1": fdp.LEGACY_PROVIDER},
            verdicts,
        )


def test_the_switch_control_raises_on_a_customer_that_settled_unjudged():
    """FAIL-OPEN guard: a customer that settled without an eligibility verdict is
    a customer the switch was never checked against. Judging only the intersection
    would report a clean switch on a book it did not cover."""
    _, verdicts = fdp.fabric_providers_for_book(**_book())
    with pytest.raises(ValueError, match="without an eligibility verdict"):
        fdp.settlement_providers_match_eligibility(
            {"C1": fdp.FABRIC_PROVIDER, "HH1": fdp.METERED_PROVIDER,
             "OFF1": fdp.LEGACY_PROVIDER, "C99": fdp.LEGACY_PROVIDER},
            verdicts,
        )


def test_a_classified_customer_that_never_settled_is_not_an_error():
    """A successor customer gated behind a churn event that did not fire is
    judged but never settles. That must not be confused with the switch failing
    to reach a customer that DID settle."""
    _, verdicts = fdp.fabric_providers_for_book(**_book())
    assert fdp.settlement_providers_match_eligibility(
        {"C1": fdp.FABRIC_PROVIDER, "HH1": fdp.METERED_PROVIDER}, verdicts
    ) is True


def test_the_switch_control_raises_on_a_book_with_no_settled_customers():
    """FAIL-SILENT guard: `all(...)` over an empty book is vacuously True, which
    would report a switched book on a run that settled nobody."""
    _, verdicts = fdp.fabric_providers_for_book(**_book())
    with pytest.raises(ValueError, match="no settled customers"):
        fdp.settlement_providers_match_eligibility({}, verdicts)


# ---------------------------------------------------------------------------
# THE SWITCH EMPTIED RATHER THAN MISSED
#
# `settlement_providers_match_eligibility` compares the settled providers against
# the DECLARED eligible set. It is therefore blind to the declaration itself being
# emptied: if the weather archive stops short of the settlement window, every
# structurally-eligible premise is refused, nobody is declared, nobody can fail to
# be switched, and the whole book quietly settles on the rescaled national shape
# the switch exists to replace — with the match-control green throughout.
# ---------------------------------------------------------------------------


def test_a_book_with_no_coverage_refusals_reports_none():
    _, verdicts = fdp.fabric_providers_for_book(**_book())
    assert fdp.coverage_refusals(verdicts) == []


def test_MUTATION_coverage_refusal_is_reported_when_the_archive_stops_short():
    """The named defect: the C1 archive ends 2025-06-07, so a window running past
    it makes an otherwise-eligible domestic premise revert to legacy. The premise
    must be NAMED, not absorbed into the same silence as a commercial office."""
    _, verdicts = fdp.fabric_providers_for_book(
        **_book(start=dt.date(2025, 5, 1), end=dt.date(2025, 8, 31))
    )
    assert fdp.coverage_refusals(verdicts) == ["C1"]


def test_the_match_control_is_GREEN_on_the_very_book_the_coverage_control_rejects():
    """Why the second control is not redundant, asserted rather than argued: on an
    emptied book the match-control reports a perfectly switched settlement, because
    an undeclared customer cannot be an unswitched one. Green here and red there is
    the whole point — if this ever starts failing, the two controls have merged and
    one of them has stopped being an independent check."""
    _, verdicts = fdp.fabric_providers_for_book(
        **_book(start=dt.date(2025, 5, 1), end=dt.date(2025, 8, 31))
    )
    all_legacy = {
        "C1": fdp.LEGACY_PROVIDER,
        "HH1": fdp.METERED_PROVIDER,
        "OFF1": fdp.LEGACY_PROVIDER,
    }
    assert fdp.settlement_providers_match_eligibility(all_legacy, verdicts) is True
    assert fdp.coverage_refusals(verdicts) == ["C1"]


def test_a_structural_refusal_is_NOT_a_coverage_refusal():
    """INDEPENDENCE: the control must key on the archive, not on 'ineligible'.
    A half-hourly-metered premise and a commercial office are refused forever and
    are not evidence of a silently-emptied switch — a control that counted them
    would fire on every healthy book and be turned off."""
    _, verdicts = fdp.fabric_providers_for_book(**_book())
    refused = {v.customer_id for v in verdicts if not v.is_eligible}
    assert refused == {"HH1", "OFF1"}
    assert fdp.coverage_refusals(verdicts) == []


def test_coverage_control_raises_rather_than_reporting_clean_on_an_unjudged_book():
    """FAIL-SILENT guard: `[]` from an empty verdict list reads identically to
    'the archive covers everyone', on a book that was never judged at all."""
    with pytest.raises(ValueError, match="never judged"):
        fdp.coverage_refusals([])


# ---------------------------------------------------------------------------
# The THIRD control: the shape that actually reaches settlement.
#
# The two controls above judge the provider LABEL and the DECLARATION. Neither
# reads a single kWh, so both stay green on a book where every fabric premise is
# handed the rescaled national shape -- the defect the switch exists to remove.
# These tests pin that hole shut and prove the new control fires in it.
# ---------------------------------------------------------------------------


def _settled_shape_for_c1():
    """The shape_fn `run_phase2b` hands to term pricing, built exactly as the
    settlement branch builds it -- not a value recomputed beside it."""
    series_by_customer, _ = fdp.fabric_providers_for_book(**_book())
    series = series_by_customer["C1"]
    return series, fdp.fabric_shape_fn(series, "electricity")


def test_the_settled_shape_is_physically_textured_on_the_real_seam():
    series, shape_fn = _settled_shape_for_c1()
    dates = sorted(series.gross_electricity_kwh)
    assert fdp.settled_shape_is_physically_textured(shape_fn, dates) is True


def test_the_control_FIRES_when_settlement_receives_a_rescaled_national_shape():
    """THE MUTATION, and it is the exact defect: a `shape_fn` that carries the
    fabric provider's name while returning one stored base shape rescaled per day.
    Nothing about the provider label, the eligibility verdict or the coverage
    refusal list changes -- which is why this control had to exist."""
    series, real_shape_fn = _settled_shape_for_c1()
    dates = sorted(series.gross_electricity_kwh)
    base = real_shape_fn(dates[0])

    def rescaled_national_shape_fn(date_str: str) -> list[float]:
        scale = 1.0 + 0.01 * (dates.index(date_str) % 7)
        return [v * scale for v in base]

    assert fdp.settled_shape_is_physically_textured(
        rescaled_national_shape_fn, dates
    ) is False


def test_the_two_shipped_controls_stay_GREEN_on_that_very_mutation():
    """INDEPENDENCE, asserted rather than argued. On the rescaled-shape book the
    label control and the coverage control both report a perfectly switched
    settlement, because a label assigned by the branch that builds the callable
    cannot disagree with itself. If this ever goes red the three controls have
    merged and one has stopped being an independent check."""
    _, verdicts = fdp.fabric_providers_for_book(**_book())
    providers = {
        "C1": fdp.FABRIC_PROVIDER,
        "HH1": fdp.METERED_PROVIDER,
        "OFF1": fdp.LEGACY_PROVIDER,
    }
    assert fdp.settlement_providers_match_eligibility(providers, verdicts) is True
    assert fdp.coverage_refusals(verdicts) == []


def test_the_control_REJECTS_a_non_finite_settled_period_before_testing_texture():
    """NaN-blind guard: `abs(nan) <= tol` is False by luck, not by design, and a
    NaN compares False against every threshold -- so a non-finite value must be
    rejected FIRST rather than silently deciding the texture verdict."""
    series, real_shape_fn = _settled_shape_for_c1()
    dates = sorted(series.gross_electricity_kwh)

    def nan_shape_fn(date_str: str) -> list[float]:
        day = list(real_shape_fn(date_str))
        day[0] = float("nan")
        return day

    with pytest.raises(ValueError, match="non-finite"):
        fdp.settled_shape_is_physically_textured(nan_shape_fn, dates)


def test_the_control_REJECTS_an_all_zero_book_rather_than_passing_it():
    """FAIL-OPEN guard, and it is reachable rather than theoretical: the zero
    floor in `fabric_shape_fn` (`max(0.0, ...)`) means a premise whose generation
    swamps its load settles at zero every period. Zero everywhere has no repeating
    fraction, so the texture test would PASS it -- a premise settling at nothing is
    not a textured premise."""
    series, _ = _settled_shape_for_c1()
    dates = sorted(series.gross_electricity_kwh)
    with pytest.raises(ValueError, match="zero"):
        fdp.settled_shape_is_physically_textured(lambda _d: [0.0] * 48, dates)


def test_the_control_REFUSES_a_window_too_short_to_detect_reuse():
    """A single day cannot show a shape being reused, and returning True for one
    would report a clean switch on evidence that cannot contain the defect."""
    series, shape_fn = _settled_shape_for_c1()
    with pytest.raises(ValueError, match="two days"):
        fdp.settled_shape_is_physically_textured(
            shape_fn, sorted(series.gross_electricity_kwh)[:1]
        )


def test_the_control_REJECTS_a_shape_that_is_not_48_periods():
    """A settlement shape is 48 half-hours. Judging a 24-vector for texture would
    report a verdict on something that is not a settlement shape at all."""
    series, _ = _settled_shape_for_c1()
    dates = sorted(series.gross_electricity_kwh)
    with pytest.raises(ValueError, match="not 48"):
        fdp.settled_shape_is_physically_textured(lambda _d: [1.0] * 24, dates)


def test_the_settled_shape_control_is_NOT_AN_ORPHAN():
    """R11, and this atom's own repeat offence. `write_fabric_gap_entries`,
    `generate_evidence_data.generate` and `tools/fabric_settlement_gap` each landed
    green-tested and uninvoked; `reconstruction_reconciles` shipped with no caller
    outside its unit test. A control the run never calls is decoration, and nothing
    about a green test says anyone runs it -- so the wiring is asserted here rather
    than trusted. Reads the real source of the settlement path, not a docstring."""
    import inspect

    from simulation import run_phase2b

    source = inspect.getsource(run_phase2b)
    assert "settled_shape_is_physically_textured(" in source, (
        "run_phase2b no longer calls the settled-shape control: the switch can be "
        "labelled without being thrown again"
    )
    assert run_phase2b.settled_shape_is_physically_textured is (
        fdp.settled_shape_is_physically_textured
    ), "run_phase2b imported a different symbol than the one tested here"


# ---------------------------------------------------------------------------
# THE INERT-SWITCH CONTROL — `the_switch_moves_the_settled_volume`
#
# The hole its three siblings shared: all of them stay green on a book whose
# fabric premises settle exactly the volume the legacy provider would have given
# them. On 2026-08-03 a tick concluded from two published run artefacts that this
# switch moved no volume and held the level on it; both artefacts turned out to be
# on the SAME side of the switch, and no control in the set could have said so.
# ---------------------------------------------------------------------------


def _legacy_shape_fn_for_c1(series):
    """The rescaled-national-shape provider the switch REPLACES, standing in for
    `run_phase2b`'s else-branch: one stored base shape scaled per day."""
    dates = sorted(series.gross_electricity_kwh)
    base = [0.12] * 48

    def legacy_shape_fn(date_str: str) -> list[float]:
        scale = 1.0 + 0.02 * (dates.index(date_str) % 5)
        return [v * scale for v in base]

    return legacy_shape_fn


def test_the_switch_moves_the_settled_volume_on_the_real_seam():
    series, shape_fn = _settled_shape_for_c1()
    dates = sorted(series.gross_electricity_kwh)
    assert fdp.the_switch_moves_the_settled_volume(
        shape_fn, _legacy_shape_fn_for_c1(series), dates
    ) is True


def test_MUTATION_the_control_FIRES_when_the_switch_is_INERT():
    """THE MUTATION, and it is the exact defect the published artefacts appeared to
    show: a fabric provider whose settled volume is indistinguishable from the
    legacy provider's. The label is right, the texture is right, and the book has
    not moved a kWh."""
    series, shape_fn = _settled_shape_for_c1()
    dates = sorted(series.gross_electricity_kwh)
    assert fdp.the_switch_moves_the_settled_volume(
        shape_fn, shape_fn, dates
    ) is False


def test_the_three_sibling_controls_stay_GREEN_on_that_very_mutation():
    """INDEPENDENCE, asserted not argued: on an INERT switch the label, coverage
    and texture controls all report a perfectly switched settlement. If this ever
    goes red the controls have merged and one has stopped being independent."""
    series, shape_fn = _settled_shape_for_c1()
    dates = sorted(series.gross_electricity_kwh)
    _, verdicts = fdp.fabric_providers_for_book(**_book())
    providers = {
        "C1": fdp.FABRIC_PROVIDER,
        "HH1": fdp.METERED_PROVIDER,
        "OFF1": fdp.LEGACY_PROVIDER,
    }
    assert fdp.settlement_providers_match_eligibility(providers, verdicts) is True
    assert fdp.coverage_refusals(verdicts) == []
    assert fdp.settled_shape_is_physically_textured(shape_fn, dates) is True


def test_the_control_REJECTS_a_non_finite_volume_before_comparing():
    """NaN-blind guard: `abs(nan) >= tol` is False, so a non-finite total would
    report an INERT switch — the fail-open reads as the defect it exists to find."""
    series, shape_fn = _settled_shape_for_c1()
    dates = sorted(series.gross_electricity_kwh)

    def nan_shape_fn(date_str: str) -> list[float]:
        day = list(shape_fn(date_str))
        day[0] = float("nan")
        return day

    with pytest.raises(ValueError, match="non-finite"):
        fdp.the_switch_moves_the_settled_volume(
            nan_shape_fn, _legacy_shape_fn_for_c1(series), dates
        )


def test_the_control_REJECTS_a_legacy_baseline_of_zero():
    """No denominator, no relative change. A bare `!=` would pass every book here."""
    series, shape_fn = _settled_shape_for_c1()
    dates = sorted(series.gross_electricity_kwh)
    with pytest.raises(ValueError, match="no baseline"):
        fdp.the_switch_moves_the_settled_volume(
            shape_fn, lambda _d: [0.0] * 48, dates
        )


def test_the_control_REFUSES_an_empty_window():
    series, shape_fn = _settled_shape_for_c1()
    with pytest.raises(ValueError, match="empty window"):
        fdp.the_switch_moves_the_settled_volume(
            shape_fn, _legacy_shape_fn_for_c1(series), []
        )


def test_the_control_REFUSES_an_unfailable_threshold():
    """A zero threshold makes it pass on any float difference — unfailable by
    construction is the R15 defect, not a lenient setting."""
    series, shape_fn = _settled_shape_for_c1()
    dates = sorted(series.gross_electricity_kwh)
    with pytest.raises(ValueError, match="unfailable"):
        fdp.the_switch_moves_the_settled_volume(
            shape_fn, _legacy_shape_fn_for_c1(series), dates,
            min_relative_change=0.0,
        )


def test_the_inert_switch_control_is_NOT_AN_ORPHAN():
    """R11 again, and this atom's fifth encounter with the class. The control is
    only worth anything if the run calls it."""
    import inspect

    from simulation import run_phase2b

    source = inspect.getsource(run_phase2b)
    assert "the_switch_moves_the_settled_volume(" in source, (
        "run_phase2b no longer calls the inert-switch control: the switch can be "
        "labelled, textured and economically invisible again"
    )
    assert run_phase2b.the_switch_moves_the_settled_volume is (
        fdp.the_switch_moves_the_settled_volume
    ), "run_phase2b imported a different symbol than the one tested here"


# ---------------------------------------------------------------------------
# The weather source — ONE SKY PER CELL (2026-09-17)
# ---------------------------------------------------------------------------
#
# Until this date the seam's weather came from `sim/weather_data/{customer_id}.csv` — four files,
# so four of the book's 146 electricity premises settled on fabric physics and 137 were refused.
# The replacement is not a wider pull but a different architecture, and these controls are keyed
# to the PROPERTY that makes it different rather than to today's cell count.


def _fake_world(cells, daily, regimes=None):
    """A tiny `WeatherWorld` built from the REAL classes.

    The real store is an 8 MB gzip; loading it per test would cost more than it proves, and the
    behaviour under test — snapping, the level offset, the NaN columns — is all in the class.
    """
    from sim.weather_world import Cell, WeatherWorld

    return WeatherWorld({k: Cell(**v) for k, v in cells.items()}, daily, regimes or {})


def _flat_days(start, end, **overrides):
    """A regime's daily record: the stored ANOMALY, so temperatures sit near zero here and
    `for_cell` adds each cell's own `level_c` back."""
    row = dict(temperature_min_c=-2.0, temperature_mean_c=0.0, temperature_max_c=2.0,
               wind_speed_mean_ms=4.0, cloud_cover_pct=60.0, precipitation_mm=0.5)
    row.update(overrides)
    days, day = {}, start
    while day <= end:
        days[day.isoformat()] = dict(row)
        day += dt.timedelta(days=1)
    return days


#: Two cells one kilometre apart, and a premise sitting in each.
_CELL_A = dict(cell_id="E400N0300", east_km=400, north_km=300,
               latitude=53.0000, longitude=-1.5000, level_c=9.5)
_CELL_B = dict(cell_id="E401N0300", east_km=401, north_km=300,
               latitude=53.0000, longitude=-1.4850, level_c=11.0)


def _source_over(cells, daily, regimes=None):
    return fdp.WeatherWorldSource(_fake_world(cells, daily, regimes))


def _premise(cid, lat, lon):
    return {"customer_id": cid, "location": {"lat": lat, "lon": lon}}


def test_two_premises_in_one_cell_read_the_IDENTICAL_sky():
    """THE DEFECT THE STORE EXISTS TO END, and the director's own words for it: "Two households
    in the same cell must experience identical weather -- that's what makes the difference in
    their demand attributable to fabric and people rather than to two separate downloads."

    Asked of the WEATHER DAYS and not of the resulting demand: two premises in one cell settle
    to different kWh whatever the source, because their fabric differs, so a control asked of
    the demand would pass with two separate downloads fully in place.
    """
    source = _source_over({"E400N0300": _CELL_A},
                          {"E400N0300": _flat_days(WINDOW_START, WINDOW_END)})
    one = source.site_for(_premise("C_ONE", 53.0002, -1.5001))
    two = source.site_for(_premise("C_TWO", 52.9998, -1.4999))
    assert one == two == "E400N0300", "two premises 40 m apart did not resolve to one cell"

    days_one = source.days(one, start=WINDOW_START, end=WINDOW_END)
    days_two = source.days(two, start=WINDOW_START, end=WINDOW_END)
    assert days_one == days_two
    # Not merely equal by value: the SAME list, so no later step can round one and not the other.
    assert days_one is days_two

    # THE MUTATION: a per-property source — the design this replaced — keyed on the customer id.
    # Every assertion above fails on it, which is what makes them a control rather than a
    # restatement of `==`.
    per_property = {
        cid: source.days("E400N0300", start=WINDOW_START, end=WINDOW_END)[:]
        for cid in ("C_ONE", "C_TWO")
    }
    per_property["C_TWO"][0] = dataclasses.replace(
        per_property["C_TWO"][0],
        weather=dataclasses.replace(per_property["C_TWO"][0].weather,
                                    temperature_mean_c=9.51),
    )
    assert per_property["C_ONE"] != per_property["C_TWO"], (
        "the mutation did not separate the two skies, so the control above proves nothing"
    )


def test_a_cell_carries_its_own_climatology_into_the_trace():
    """The two cells share one regime and must still differ, by their `level_c` and only by it.
    Without this the decomposition is a store of anomalies read as temperatures — correct-looking
    and about eleven degrees wrong."""
    daily = {"R00": _flat_days(WINDOW_START, WINDOW_END)}
    source = _source_over({"E400N0300": _CELL_A, "E401N0300": _CELL_B}, daily,
                          {"E400N0300": "R00", "E401N0300": "R00"})
    a = source.days("E400N0300", start=WINDOW_START, end=WINDOW_START)[0].weather
    b = source.days("E401N0300", start=WINDOW_START, end=WINDOW_START)[0].weather
    assert a.temperature_mean_c == pytest.approx(9.5)
    assert b.temperature_mean_c == pytest.approx(11.0)
    # The regime is shared, so everything that is NOT the cell's climatology must be identical.
    assert a.wind_speed_mean_ms == b.wind_speed_mean_ms
    assert a.cloud_cover_pct == b.cloud_cover_pct


def test_a_temperature_ONLY_cell_is_refused_and_not_answered_with_a_NaN():
    """THE NAMED FAIL the store shipped with: 18 of 156 cells held temperature and no wind,
    cloud or precipitation, and `for_cell` answers for every one of them with NaN in three
    columns. `fabric_physics` does arithmetic on all five fields, so a membership test here
    would hand `simulate_premise` a NaN that is neither an error nor a number — it settles,
    and it prices.
    """
    partial = _flat_days(WINDOW_START, WINDOW_END,
                         wind_speed_mean_ms=float("nan"), cloud_cover_pct=float("nan"))
    source = _source_over({"E400N0300": _CELL_A}, {"E400N0300": partial})

    assert source.available("E400N0300") is False
    with pytest.raises(fdp.WeatherWorldRefusal, match="wind_speed_mean_ms"):
        source.days("E400N0300", start=WINDOW_START, end=WINDOW_END)

    # THE MUTATION: availability asked as membership, which is the check a reader reaches for.
    held_by_membership = "E400N0300" in source.world.cells
    assert held_by_membership is True, (
        "the mutation is not distinguishable from the real check: the cell must BE in the store "
        "and still be unavailable, or this control passes for the wrong reason"
    )


def test_a_complete_cell_IS_available_so_the_refusal_is_not_universal():
    """The partition, over one control rather than a leg per branch: a source that refuses
    EVERYTHING passes every refusal test above. This is the assertion that the accepting branch
    can be reached at all."""
    source = _source_over({"E400N0300": _CELL_A},
                          {"E400N0300": _flat_days(WINDOW_START, WINDOW_END)})
    assert source.available("E400N0300") is True
    assert source.available("E999N9999") is False


def test_a_premise_beyond_the_snap_radius_is_refused_and_the_refusal_says_how_far():
    """A silent snap would give a Cornish premise Birmingham's weather and read as a hit. The
    distance belongs in the reason because the person clearing it has to decide whether the cell
    is missing or the coordinate is wrong."""
    source = _source_over({"E400N0300": _CELL_A},
                          {"E400N0300": _flat_days(WINDOW_START, WINDOW_END)})
    site = source.site_for(_premise("C_FAR", 50.2660, -5.0527))    # Falmouth
    assert not site.startswith("E"), f"a far premise snapped to a cell: {site}"
    assert "km from the nearest cell" in site
    assert source.available(site) is False


def test_a_premise_with_no_coordinate_gets_a_marker_that_is_not_a_cell_id():
    source = _source_over({"E400N0300": _CELL_A},
                          {"E400N0300": _flat_days(WINDOW_START, WINDOW_END)})
    assert source.site_for({"customer_id": "C_NONE", "location": {}}) == fdp.NO_CELL_SITE
    assert source.site_for({"customer_id": "C_NONE"}) == fdp.NO_CELL_SITE


def test_the_refusal_does_not_send_the_reader_to_build_the_REFUSED_design():
    """Keyed to the property, not to today's wording. The remedy sentence said "pull that
    coordinate" until 2026-09-17 — an instruction to download one archive per property, which is
    the design the director refused in writing and the reason the per-cell store exists. A
    refusal that names the wrong remedy recruits the reader into rebuilding it.
    """
    reason = fdp.fabric_eligibility(
        _premise("C_B", 52.4862, -1.8904),
        make_household("C_B"),
        is_half_hourly_metered=False,
        weather_available=False,
        weather_site="E406N0287",
    ).reason
    assert reason.startswith(fdp.NO_ARCHIVE_REFUSAL)
    assert "52.4862" in reason and "-1.8904" in reason
    assert "CELL" in reason and "never a per-property pull" in reason
    assert "pull that coordinate" not in reason
    assert "sim/weather_data" not in reason


def test_the_book_provider_ACTUALLY_USES_the_weather_days_callable_it_is_given():
    """A function gaining a parameter is ungraded until something proves the parameter reaches
    the work. Every other test in this file drives `fabric_providers_for_book` through `_book()`,
    which leaves `weather_days_for` at its default — so without this control the store could be
    wired into `run_phase2b` and silently never read.

    Proven by the SERIES DIFFERING, not by a call count: a spy that records the call would pass
    on a provider that called the callable and then threw its answer away.
    """
    daily = _flat_days(WINDOW_START, WINDOW_END)
    source = _source_over({"E400N0300": _CELL_A}, {"E400N0300": daily})
    from_store, verdicts = fdp.fabric_providers_for_book(
        **_book(weather_site_for=lambda _c: "E400N0300",
                weather_available=source.available,
                weather_days_for=source.days)
    )
    assert sorted(from_store) == ["C1"], [v.reason for v in verdicts if not v.is_eligible]

    from_archive, _ = fdp.fabric_providers_for_book(**_book())
    dates = sorted(from_store["C1"].gross_electricity_kwh)
    assert dates == sorted(from_archive["C1"].gross_electricity_kwh)
    assert (from_store["C1"].gross_electricity_kwh
            != from_archive["C1"].gross_electricity_kwh), (
        "the store-fed book returned the archive-fed book's demand: `weather_days_for` is not "
        "reaching the trace, and wiring the store into the runner would change nothing"
    )


def test_the_settlement_path_and_the_gas_leg_READ_ONE_WEATHER_SOURCE():
    """R11/R15: the electricity leg and the gas leg must not be able to disagree about which
    premises have physics. Two independently-constructed resolvers is exactly how that promise
    rots — the electricity leg moving to the cell store while the gas leg kept reading
    `sim/weather_data/*.csv` would have split the book in silence, with no red anywhere.
    """
    import inspect

    from simulation import run_phase2b

    source = inspect.getsource(run_phase2b)
    assert source.count("WeatherWorldSource.load()") == 1, (
        "run_phase2b builds the weather source more than once (or not at all): the two fabric "
        "legs can now resolve a premise differently"
    )
    assert "weather_days_for=_weather_source.days" in source, (
        "run_phase2b decides eligibility from the cell store but builds the trace from something "
        "else -- the exact fail-open shape `available` exists to prevent"
    )
    assert "WEATHER_DATA_DIR_PATH" not in source, (
        "the per-customer archive is still deciding a fabric verdict somewhere in the runner"
    )
    assert run_phase2b.WeatherWorldSource is fdp.WeatherWorldSource


# ---------------------------------------------------------------------------
# The switch reaches the BOOK — the per-premise floor generalised (2026-09-17)
# ---------------------------------------------------------------------------


def test_the_book_control_REFUSES_an_inert_switch():
    """The defect it inherits: a switch labelled, declared and textured, settling exactly the
    legacy volume everywhere. Every premise says no, so the book does."""
    assert fdp.the_switch_reaches_the_book([False] * 91) is False
    assert fdp.the_switch_reaches_the_book([True] + [False] * 90) is False


def test_the_book_control_ACCEPTS_a_book_that_moved_and_is_not_unfailable():
    """The partition over one control. A predicate that refuses EVERYTHING passes the refusal
    test above, so the accepting branch has to be asserted reachable in the same breath — and
    with the FOUR unmoved premises the real book has, not with a clean sweep."""
    real = [True] * 87 + [False] * 4              # the 2026-09-17 measurement
    assert fdp.the_switch_reaches_the_book(real) is True
    assert fdp.the_switch_reaches_the_book([True, False]) is True      # exactly the floor
    assert fdp.the_switch_reaches_the_book([True, False, False]) is False


def test_the_book_control_REFUSES_an_empty_book():
    """R15: a control that passes on an empty set is the fail-open this whole set exists to
    refuse. "Nobody was eligible, so nobody failed to be switched" is how the switch un-throws
    itself in silence — it must be a refusal, never a vacuous True."""
    with pytest.raises(ValueError, match="no premise settles"):
        fdp.the_switch_reaches_the_book([])


def test_the_book_control_REFUSES_an_unfailable_share():
    """A share of 0 passes any book including the wholly inert one; a share above 1 can never be
    met. Both are unfailable by construction, which is a defect and not a setting."""
    for bad in (0.0, -0.1, 1.5):
        with pytest.raises(ValueError, match="unfailable or unsatisfiable"):
            fdp.the_switch_reaches_the_book([True, True], min_share=bad)


def test_the_book_control_IS_NOT_AN_ORPHAN_and_the_per_premise_raise_is_gone():
    """R11, and the half that matters: the per-premise `raise` must be GONE, not merely joined.
    Left in place it still refuses the four premises the measurement says are entitled to settle
    nearly the legacy electricity volume, and the book-level control never gets a subject."""
    import inspect

    from simulation import run_phase2b

    source = inspect.getsource(run_phase2b)
    assert "the_switch_reaches_the_book(" in source
    assert run_phase2b.the_switch_reaches_the_book is fdp.the_switch_reaches_the_book
    assert "the_switch_moves_the_settled_volume(" in source, (
        "the per-premise predicate is no longer called, so the book-level count is over nothing"
    )
    assert "settles on the fabric provider but its settled volume" not in source, (
        "the per-premise raise is still live: one premise below the 2% floor still wedges the "
        "whole run, and the book-level control it was replaced by can never be reached"
    )
