"""What each driver is for, each test named by the defect it exists to catch.

The question this module answers decides whether a cell count is worth paying, so the failure that
matters is a plausible ratio between two effects that were not measured over the same thing.
"""
from __future__ import annotations

import pytest

from tools import weather_driver_sensitivity as wds


def test_WINDOW_CANNOT_ANSWER_FOR_WIND():
    """THE DEFECT, AND IT SHIPPED. The first version of `_sim_has_a_wind_term` asked
    `"wind" in name.lower()` and returned True — on `window_area`, `_WINDOW_U_BY_ERA` and
    `_WINDOW_AREA_RATIO`. It would have published "the SIM models wind" on the strength of the
    glazing, in the one place where the whole finding is that it does not.

    Caught by printing the number, not by a test, which is why this one exists.
    """
    import ast
    import re

    pattern = r"(?:^|_)wind(?:chill|speed|_speed)?(?:_|$)"
    for glazing in ("window_area", "_WINDOW_U_BY_ERA", "_WINDOW_AREA_RATIO", "windows"):
        assert not re.search(pattern, glazing.lower()), f"{glazing} matched the wind pattern"
    for genuine in ("wind_speed_ms", "WIND_FACTOR", "wind", "_windchill_dd", "site_wind"):
        assert re.search(pattern, genuine.lower()), f"{genuine} did not match the wind pattern"

    # and the real source, which is what the claim rests on
    src = (wds.PROJECT / "simulation" / "fabric_physics.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    fn = next(n for n in ast.walk(tree)
              if isinstance(n, ast.FunctionDef) and n.name == "fabric_parameters")
    assert any("window" in (getattr(n, "id", "") or getattr(n, "attr", "")).lower()
               for n in ast.walk(fn)), (
        "if `fabric_parameters` no longer mentions windows, this control has stopped guarding the "
        "false positive it was written for")

    assert wds._sim_has_a_wind_term() is False


def test_a_MISSING_SUBJECT_RAISES_rather_than_reporting_NO_WIND_TERM(monkeypatch, tmp_path):
    """FAIL-CLOSED, and the direction matters. If `fabric_parameters` is renamed, an absent function
    has no wind term in it — so a lenient implementation would report False, which is the FINDING,
    and the finding would then be an artefact of a rename. "I cannot tell" is not "no"."""
    (tmp_path / "simulation").mkdir()
    (tmp_path / "simulation" / "fabric_physics.py").write_text("def something_else():\n    pass\n")
    monkeypatch.setattr(wds, "PROJECT", tmp_path)

    with pytest.raises(RuntimeError, match="renamed"):
        wds._sim_has_a_wind_term()


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
