"""What each driver is for, each test named by the defect it exists to catch.

The question this module answers decides whether a cell count is worth paying, so the failure that
matters is a plausible ratio between two effects that were not measured over the same thing.
"""
from __future__ import annotations

import re

import pytest

from tools import weather_driver_sensitivity as wds


def test_THE_WIND_TERM_IS_DETECTED_BY_RUNNING_THE_MODEL_not_by_reading_it():
    """A CONTROL THAT WAS WRONG TWICE IN OPPOSITE DIRECTIONS, both times for reading source text.

    First it asked `"wind" in name.lower()` over `fabric_parameters` and returned True — on
    `window_area`. It would have published "the SIM models wind" on the strength of the glazing.
    Segment-matched, it returned False correctly, and then `W1_26` put the SAP factor in
    `FabricParameters.with_wind` rather than in `fabric_parameters`: the mechanism moved one method
    along and the control could not see it. **A control keyed to WHERE a thing is written goes
    stale the moment it is written somewhere else.**

    It now asks the parameter vector for its heat loss coefficient at two wind speeds. That cannot
    be fooled by a name and cannot go stale on a rename — the only thing that makes it False is the
    factor genuinely not being applied.
    """
    from simulation import fabric_physics as fp

    assert wds._sim_has_a_wind_term() is True

    params = fp.fabric_parameters(wds._probe_household())
    calm = params.with_wind(2.0).heat_loss_coefficient_kw_per_k
    windy = params.with_wind(8.0).heat_loss_coefficient_kw_per_k
    assert windy > calm, "more wind must mean more heat loss"

    # the substring trap that produced the first wrong answer, kept as a unit on the pattern itself
    # so the lesson survives even though the function no longer greps
    pattern = r"(?:^|_)wind(?:chill|speed|_speed)?(?:_|$)"
    for glazing in ("window_area", "_WINDOW_U_BY_ERA", "_WINDOW_AREA_RATIO", "windows"):
        assert not re.search(pattern, glazing.lower()), f"{glazing} matched the wind pattern"
    for genuine in ("wind_speed_ms", "WIND_FACTOR", "wind", "_windchill_dd", "site_wind"):
        assert re.search(pattern, genuine.lower()), f"{genuine} did not match the wind pattern"


def test_the_REFERENCE_WIND_reproduces_the_model_that_had_NO_WIND_TERM():
    """THE PROPERTY THAT MAKES `W1_26` AN EXTENSION AND NOT A RE-CALIBRATION.

    SAP normalises the infiltration factor at 4 m/s, so `with_wind(4.0)` must return exactly the
    parameter vector the model produced before the term existed. Without this the change would be
    a silent re-baselining of every historical demand figure in the tree, and the movement it
    actually causes could not be attributed to the wind series.
    """
    from simulation import fabric_physics as fp

    params = fp.fabric_parameters(wds._probe_household())
    at_reference = params.with_wind(fp.SAP_REFERENCE_WIND_MS)

    assert at_reference.r_ia_k_per_kw == pytest.approx(params.r_ia_k_per_kw, rel=1e-12)
    assert at_reference.heat_loss_coefficient_kw_per_k == pytest.approx(
        params.heat_loss_coefficient_kw_per_k, rel=1e-12)


def test_a_parameter_vector_WITHOUT_its_ventilation_components_REFUSES_the_wind_factor():
    """FAIL-CLOSED, and the direction is the whole point. A hand-built `FabricParameters` has no
    raw ACH or volume, so the factor cannot be computed — and the tempting implementation returns
    `self`, which is a silent no-op that looks exactly like a calm day. That is how the wind term
    would stay absent while appearing present, which is the defect this atom removed."""
    from simulation import fabric_physics as fp

    bare = fp.FabricParameters(floor_area_m2=90.0, r_ia_k_per_kw=5.0, r_im_k_per_kw=0.5,
                               c_i_kwh_per_k=0.75, c_m_kwh_per_k=7.5, solar_aperture_m2=5.0,
                               internal_gain_kw=0.36)

    with pytest.raises(ValueError, match="ventilation components"):
        bare.with_wind(6.0)


def test_the_WIND_and_TEMPERATURE_effects_span_the_SAME_PERCENTILES_of_the_SAME_population():
    """A ratio between two numbers that count different things is this project's most common way of
    publishing something misleading. "Wind is 0.8x temperature" only means anything if both are the
    5th-to-95th-percentile move of the SAME household-weighted population — which is why the four
    percentile constants sit together and are asserted against `W1_20`'s published table."""
    assert (wds.WIND_P05_MS, wds.WIND_P95_MS) == (2.98, 5.61)
    assert (wds.WINTER_TEMP_P05_C, wds.WINTER_TEMP_P95_C) == (3.95, 6.13)
    assert wds.WIND_P05_MS < wds.WIND_MEDIAN_MS < wds.WIND_P95_MS

    published = (wds.PROJECT / "docs" / "market_research" /
                 "half_the_land_is_empty_and_weighting_halves_the_variation.md")
    assert published.is_file()
    text = published.read_text(encoding="utf-8")
    for value in ("2.98", "5.61", "3.95", "6.13"):
        assert value in text, (
            f"{value} is not in the document these constants claim to come from; the two effects "
            "may no longer be spanning the same population")


def test_the_SAP_WIND_FACTOR_is_LINEAR_and_normalised_at_FOUR():
    """The published mechanism, pinned. SAP 10.2 / BREDEM: adjusted ACH = raw x shelter x (wind/4).
    A quadratic or a threshold form would change the answer by a factor and there is nothing in the
    output that would look wrong."""
    from simulation import fabric_physics as fp

    assert wds.SAP_REFERENCE_WIND_MS == 4.0
    calm = wds.wind_hlc_sensitivity(areas=(90.0,))
    assert calm["hlc_change_p05_to_p95_wind"]["median"] > 0

    # linearity: doubling the wind must double the infiltration ACH, before the Part F floor bites
    raw = 1.0
    assert raw * (8.0 / wds.SAP_REFERENCE_WIND_MS) == 2 * raw * (4.0 / wds.SAP_REFERENCE_WIND_MS)
    assert fp._MINIMUM_VENTILATION_ACH > 0, (
        "the Part F floor is what stops the calm end going to zero; without it the ratio is "
        "unbounded and the reported spread is an artefact")


def test_WIND_IS_NOT_SECOND_ORDER_and_the_comparison_is_the_claim():
    """THE ANSWER TO THE DIRECTOR'S CHALLENGE, keyed to the property rather than to today's number:
    wind's effect on heat loss is the same ORDER as temperature's, not a rounding error. The
    threshold is a tenth — if wind ever measures under 10% of the temperature effect the document's
    conclusion is wrong and this must say so."""
    result = wds.wind_hlc_sensitivity()

    assert result["combinations"] > 100, "too few stock combinations for a median to mean anything"
    assert 0.10 < result["ventilation_share_of_hlc"]["median"] < 0.50
    assert result["wind_effect_relative_to_temperature"] > 0.25, (
        f"wind measured at {result['wind_effect_relative_to_temperature']}x temperature, which "
        "WOULD make it second-order and refute the published conclusion")
    assert result["hdd_change_p05_to_p95_winter_temp"] < 0, (
        "warmer 95th percentile must mean FEWER degree days; a positive sign means the span is "
        "inverted and the ratio is meaningless")


def test_ANGSTROM_PRESCOTT_COMPRESSES_the_spread_and_the_direction_is_not_a_choice():
    """`H/H0 = a + b*(n/N)` with `a > 0` makes relative variation in irradiation STRICTLY smaller
    than in sunshine duration. That is arithmetic, not a modelling preference, and it is why a cell
    count argued from sunshine hours overstates what PV needs. Checked across the whole published
    coefficient range, because a conclusion that turned on one paper's a and b would not be one."""
    assert wds.ANGSTROM_A > 0, "a zero intercept makes yield proportional to duration and the "\
                               "compression disappears"
    for (a, b) in wds.ANGSTROM_RANGE:
        fraction = 0.35
        elasticity = b * fraction / (a + b * fraction)
        assert 0 < elasticity < 1, f"a={a} b={b} gives elasticity {elasticity}"
        assert elasticity < 0.6


def test_the_PV_CURVE_starts_at_the_NATIONAL_number_the_company_actually_uses():
    """`cells=1` is not a mathematical limit here, it is the company's live behaviour:
    `seg_export_estimator` applies one kWh/kWp figure to every household. If that ever stops being
    true this test should fail, because the 3.4% headline is a statement about a real defect."""
    from company.regulatory import seg_export_estimator as seg

    assert isinstance(seg.ANNUAL_YIELD_KWH_PER_KWP, float), (
        "the national yield figure has moved or become geographic; the '1 cell today' claim needs "
        "re-checking before it is published again")

    curve = wds.pv_yield_error(cells=(1, 5))
    rows = {r["cells"]: r for r in curve["curve"]}
    assert rows[1]["yield_rms"] > rows[5]["yield_rms"] * 2, (
        "five cells must materially beat one; if they do not, the curve is flat and the "
        "recommendation is unfounded")
    assert 0.0 < curve["elasticity_of_irradiation_to_sunshine"] < 1.0


def test_SOLAR_GAIN_REACHABILITY_IS_MEASURED_BY_RUNNING_THE_MODEL_not_by_reading_it():
    """THE DIRECTOR'S INSTRUCTION, as a control: check rather than assume, given the wind term's
    history.

    Wind was named in `fabric_physics`'s own docstring as an available archive field and consumed by
    nothing, so any check that greps for a word would have reported both drivers present. This one
    zeroes the aperture and re-runs the 2R2C integration: "reachable" means the fuel number moved.
    A version that reported reachability from the presence of `solar_aperture_m2` would pass on a
    model that computed the term and threw it away.

    THE TWO FUEL NUMBERS ARE THE EVIDENCE AND THERE IS NO BOOLEAN BESIDE THEM. One was there and it
    survived a mutation hardcoding it to True — a summary flag that could disagree with the figures
    printed next to it. Deleted rather than guarded.
    """
    result = wds.solar_gain_sensitivity()

    assert "reachable" not in result, "a boolean here can lie about the numbers below it"
    with_sun = result["half_year_fuel_kwh"]["with_solar_gain"]
    without = result["half_year_fuel_kwh"]["aperture_zeroed"]
    assert with_sun < without, "zeroing the glazing must RAISE heating fuel, not lower it"
    assert result["solar_gain_offsets_of_heating_fuel"] > 0.05, (
        "solar gain offsetting under 5% of heating fuel would make it immaterial and the published "
        "conclusion wrong")


def test_the_DATA_CONTRACT_CARRIES_WIND_AND_IT_IS_REQUIRED():
    """WAS `..._carries_no_wind_field` UNTIL W1_26 LANDED, and re-keyed rather than deleted.

    The finding was that `DailyWeather` — the record the entire demand path runs on — had nowhere
    to put a wind speed, which is why the repair was an atom and not a patch. The control now
    asserts the repair holds AND that the field is required, because a defaulted one would restore
    the original state for every caller that forgot it.

    Asserted alongside the fields that were always there, so a rename of the record cannot quietly
    turn this into a check of nothing.
    """
    import dataclasses

    from simulation.fabric_physics import DailyWeather

    names = {f.name for f in dataclasses.fields(DailyWeather)}
    assert {"temperature_mean_c", "cloud_cover_pct", "day_of_year"} <= names, (
        "DailyWeather has changed shape; this control is no longer reading what it thinks it is")
    assert wds._daily_weather_has_wind() is True

    # AND IT MUST HAVE NO DEFAULT. A default restores the old world silently for every caller that
    # forgets, which is precisely the state W1_26 removed -- the column was in the archive all
    # along and the reader skipped it.
    wind = next(f for f in dataclasses.fields(DailyWeather) if f.name == "wind_speed_mean_ms")
    assert wind.default is dataclasses.MISSING and wind.default_factory is dataclasses.MISSING, (
        "a default wind speed makes a caller that forgets it silently receive a windless world")


def test_SOLAR_AND_WIND_pull_in_OPPOSITE_directions_across_the_stock():
    """THE TARGETING CLAIM, and the reason both sweeps are published rather than two medians.

    Solar gain matters MORE the better the house is — free heat against a shrinking demand — while
    wind's effect collapses in the tightest modern homes, because the Part F minimum air change rate
    clamps the calm end. A model that used one driver as a proxy for the other would be wrong at
    both ends of the stock, and a single median for each would hide it.
    """
    solar = wds.solar_gain_sensitivity()["fuel_change_across_that_spread_by_stock"]

    assert abs(solar["POST_2000/FULL"]) > abs(solar["PRE_1919/POOR"]) * 2, (
        "solar gain must bite harder in a tight modern home than a leaky old one")
    for value in solar.values():
        assert value < 0, "more sun must mean less fuel in every stock combination"


def test_the_ANGSTROM_SPREAD_comes_from_the_PUBLISHED_household_percentiles():
    """The solar effect is quoted over the same 5th-to-95th span as the wind and temperature ones,
    or the three numbers cannot be compared — which is the whole point of publishing them together."""
    assert (wds.SUNSHINE_P05_H, wds.SUNSHINE_P95_H) == (1320.13, 1734.48)
    spread = wds.pv_irradiation_spread()

    assert 1.0 < spread < 1.3, f"an irradiation spread of {spread} is not a GB household spread"
    naive = wds.SUNSHINE_P95_H / wds.SUNSHINE_P05_H
    assert spread < naive, (
        "the Angstrom intercept must COMPRESS the spread; if irradiation varied as much as sunshine "
        "duration the whole PV argument would change")


def test_the_sensitivity_runs_THE_WAY_A_COMMAND_LINE_RUNS_IT():
    """Eighth module in this repository where the script entry point could be dead while every test
    is green — and this one imports from BOTH `simulation` and `tools`, so it needs the repo root
    on the path twice over."""
    import os
    import subprocess
    import sys as _sys

    done = subprocess.run(
        [_sys.executable, "-c",
         "import sys; sys.path[0] = 'tools';"
         "import runpy;"
         "runpy.run_path('tools/weather_driver_sensitivity.py', run_name='probe');"
         "import simulation.fabric_physics, tools.weather_cell_derivation"],
        cwd=str(wds.PROJECT), capture_output=True, text=True, timeout=300,
        env={**os.environ, "PYTHONPATH": ""},
    )

    assert "ModuleNotFoundError" not in done.stderr, done.stderr
    assert done.returncode == 0, done.stderr
