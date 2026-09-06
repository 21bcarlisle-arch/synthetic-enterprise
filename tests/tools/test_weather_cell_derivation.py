"""The coverage curve, each test named by the defect it exists to catch.

This is the module that answers the director's question, so the failure that matters most is not a
crash: it is a curve that looks entirely reasonable and is a statement about the wrong population,
the wrong metric, or the wrong thing being held constant.
"""
from __future__ import annotations

import numpy as np
import pytest

from tools import weather_cell_derivation as wcd

SMALL = (1, 2, 5, 13)


@pytest.fixture(scope="module")
def space():
    """One synthetic driver space, so the suite never pays the 1.67 million row census join.

    Two dense clusters and one far outlier cell holding almost no households. Built so that the
    household- and area-weighted answers MUST differ: an outlier with one household is a third of
    the area-weighted variation and none of the household-weighted variation.
    """
    rng = np.random.default_rng(0)
    native = np.vstack([
        rng.normal([4.0, 4.0, 1400.0], [0.2, 0.2, 30.0], size=(400, 3)),
        rng.normal([6.0, 3.0, 1700.0], [0.2, 0.2, 30.0], size=(400, 3)),
        np.array([[-2.0, 15.0, 800.0]]),
    ])
    weights = np.concatenate([np.full(800, 1000.0), [1.0]])

    def built(household_weighted=True):
        w = weights if household_weighted else np.ones(len(native))
        mean = np.average(native, axis=0, weights=w)
        sd = np.sqrt(np.average((native - mean) ** 2, axis=0, weights=w))
        return (native - mean) / sd, native, w, mean, sd

    return built


def test_the_curve_is_HOUSEHOLD_weighted_and_the_area_curve_is_a_DIFFERENT_answer(space):
    """THE DEFECT THIS WHOLE ATOM EXISTS TO AVOID. An unweighted curve is a statement about land.
    Half of GB's land cells hold nobody, and the empty ones are the climatic extremes -- so an
    unweighted curve spends its cells resolving places with no customers in them and reports a
    larger number with no sign that anything is wrong."""
    household = wcd.coverage_curve(SMALL, space=space(True))
    area = wcd.coverage_curve(SMALL, space=space(False))

    assert [r["captured"] for r in household] != [r["captured"] for r in area], (
        "if the two curves agree, the weighting is not reaching the clustering")
    at_two = {r["cells"]: r["captured"] for r in household}[2]
    area_at_two = {r["cells"]: r["captured"] for r in area}[2]
    assert at_two > area_at_two, (
        "two cells should capture more of the households than of the land: the outlier cell holds "
        "one household and a third of the area-weighted spread")


def test_SPACE_ITSELF_honours_the_household_weighting_flag(monkeypatch):
    """A SURVIVOR THAT WAS A MISSING TEST, NOT AN EQUIVALENCE, and it named the one line that
    matters most.

    Every other test here injects its own driver space, so `_space` -- the only code path
    production ever takes -- was never exercised. Replacing `w[occupied] if household_weighted else
    ones` with a bare `ones` left the whole suite green while every published figure silently became
    a statement about land. That is precisely the defect this atom exists to prevent, surviving in
    the module that publishes the answer.
    """
    from tools import weather_cell_drivers as drivers_mod
    from tools import weather_cell_weights as weights_mod

    fake = {"winter_temp": np.array([1.0, 2.0, 9.0, -50.0]),
            "annual_wind": np.array([1.0, 2.0, 9.0, 40.0]),
            "annual_sun": np.array([100.0, 200.0, 900.0, 0.0]),
            "east": np.array([0.0, 1000.0, 2000.0, 3000.0]),
            "north": np.array([0.0, 0.0, 0.0, 0.0])}
    monkeypatch.setattr(drivers_mod, "drivers", lambda: fake)
    # the fourth cell is EMPTY LAND at an extreme -- half of GB's land cells are exactly this
    monkeypatch.setattr(weights_mod, "aligned_to_land",
                        lambda d: (np.array([1000.0, 1000.0, 1.0, 0.0]), {}))

    _, native_h, household, _, _ = wcd._space(True)
    _, native_a, area, _, _ = wcd._space(False)

    assert list(household) == [1000.0, 1000.0, 1.0], "the census weights did not reach the space"
    assert list(area) == [1.0, 1.0, 1.0]
    assert household.sum() != area.sum()
    assert len(native_h) == len(native_a) == 3, (
        "the area comparison must be over the SAME cells as the household one. Let the empty cell "
        "in and the two curves differ in population AND in weighting, and neither difference is "
        "attributable to either.")
    assert -50.0 not in native_a[:, 0], "an empty land cell reached the area-weighted space"


def test_an_UNREACHED_target_returns_NONE_and_not_the_largest_k():
    """"We cannot tell" is a result. Returning the biggest swept k -- or extrapolating to one --
    would answer the director's question with a number the measurement does not contain, and it
    would look exactly like an answer."""
    rows = [{"cells": 1, "captured": 0.1}, {"cells": 2, "captured": 0.5}]

    assert wcd.cells_for(0.99, rows) is None
    assert wcd.cells_for(0.5, rows) == 2, "the reachable branch must still work"


def test_the_drivers_are_STANDARDISED_or_SUNSHINE_decides_everything(space):
    """Sunshine is in hours with a spread near 127; wind is in m/s with a spread near 0.8. Cluster
    the raw columns and the answer is a partition on sunshine alone, with the other two drivers
    contributing about one part in 25,000 -- and the curve still rises to 99%, so nothing in the
    output says the wind and the temperature were ignored."""
    z, native, weights, mean, sd = space(True)

    assert np.allclose(np.average(z, axis=0, weights=weights), 0, atol=1e-9)
    assert np.allclose(np.sqrt(np.average(z ** 2, axis=0, weights=weights)), 1, atol=1e-9)
    assert native.std(axis=0).max() / native.std(axis=0).min() > 50, (
        "if the raw drivers had comparable spreads, standardising would be cosmetic and this "
        "control would be guarding nothing")


def test_the_curve_RISES_with_k_and_starts_at_ZERO(space):
    """One cell captures nothing by construction -- the single centroid IS the weighted mean, so
    the within-cluster sum of squares is the total. A curve that started anywhere else would mean
    the denominator and the numerator are computed about different centres, which is the most
    common way a variance-explained figure comes out flattering."""
    rows = wcd.coverage_curve(SMALL, space=space(True))

    assert rows[0]["cells"] == 1 and abs(rows[0]["captured"]) < 1e-9
    captured = [r["captured"] for r in rows]
    assert captured == sorted(captured), f"coverage fell as cells were added: {captured}"


def test_the_NATIVE_RESIDUALS_are_in_REAL_UNITS_and_SHRINK(space):
    """A dimensionless variance share cannot be argued with by a practitioner. Degrees can. These
    are the numbers that let a reader who rejects the equal-weighting Choice price the
    disagreement instead of debating it."""
    rows = wcd.coverage_curve(SMALL, space=space(True))
    first, last = rows[0]["native_residuals"], rows[-1]["native_residuals"]

    assert set(first) == set(wcd.DRIVERS)
    for driver in wcd.DRIVERS:
        assert last[driver] < first[driver], f"{driver} residual did not fall as cells were added"
    assert set(wcd.UNITS) == set(wcd.DRIVERS), "every driver must declare its unit"


def test_EQUAL_WEIGHTING_IS_THE_CONSERVATIVE_CHOICE_and_this_is_the_falsifier(space):
    """THE CLAIM THE MODULE'S DOCSTRING MAKES, checked rather than asserted.

    It says equal standardisation "can only ever ask for MORE cells than a temperature-dominant
    metric would", which makes the published counts an upper bound. That is falsifiable, and if it
    were false the reasoning behind the Choice -- not just the number -- would be wrong.
    """
    sens = wcd.choice_sensitivity(SMALL, space=space(True))

    assert set(sens) == set(wcd.METRICS)
    for k in range(len(SMALL)):
        equal = sens["equal"]["curve"][k]["captured"]
        temp_only = sens["temperature_only"]["curve"][k]["captured"]
        assert temp_only >= equal - 1e-9, (
            f"at {SMALL[k]} cells a temperature-only metric captured LESS ({temp_only}) than the "
            f"equal metric ({equal}). The Choice is not conservative and the docstring is wrong.")


def test_a_metric_that_ZEROES_a_driver_actually_ignores_it(space):
    """REACHABILITY of the sensitivity mechanism. If the scale vector were dropped on the way to
    `fit`, all three metrics would return the identical curve and the test above would pass by
    tautology -- three copies of one number agreeing with themselves."""
    sens = wcd.choice_sensitivity(SMALL, space=space(True))
    curves = {name: [r["captured"] for r in v["curve"]] for name, v in sens.items()}

    assert curves["equal"] != curves["temperature_only"], "the metric scaling never reached fit()"
    assert curves["equal"] != curves["temperature_dominant_4_1_1"]


def test_the_PER_DRIVER_curve_partitions_on_ONE_DRIVER_and_not_on_all_three():
    """THE CONTROL THE PUBLISHED CONCLUSION RESTS ON.

    `W1_25` reports that all three drivers want about the same ~21 cells asked one at a time, and
    that the joint 987 is dimensionality rather than any driver's own roughness. A `per_driver_curve`
    that quietly clustered on the full matrix would return three copies of the JOINT curve — three
    identical, plausible, monotone curves — and the finding would invert with nothing to show for it.

    The fixture makes the two answers unmistakable: eight corners of a cube, so each driver alone is
    a two-cluster problem and the three together are an eight-cluster problem.
    """
    corners = np.array([[x, y, z] for x in (-1.0, 1.0) for y in (-1.0, 1.0) for z in (-1.0, 1.0)])
    standardised = np.repeat(corners, 40, axis=0)
    # THE THREE SPREADS ARE DELIBERATELY DIFFERENT -- 1 degC, 2 m/s, 100 hours, the real drivers'
    # order of magnitude. With three equal spreads a residual scored against the WRONG driver
    # index is indistinguishable from one scored against the right one, and the control below
    # would pass on a module that always reported driver 0.
    mean = np.array([5.0, 4.0, 1500.0])
    sd = np.array([1.0, 2.0, 100.0])
    native = standardised * sd + mean
    weights = np.ones(len(native))
    space = (standardised, native, weights, mean, sd)

    per_driver = wcd.per_driver_curve((2,), space=space)
    joint = wcd.coverage_curve((2,), space=space)

    assert set(per_driver) == set(wcd.DRIVERS)
    for name, rows in per_driver.items():
        assert rows[0]["captured"] > 0.99, (
            f"{name} alone is a two-cluster problem and must be fully captured at k=2; "
            f"got {rows[0]['captured']} — the partition is not one-dimensional")
        # AND THE RESIDUAL MUST BE ~0 THERE. A centre left in standardised units — `centres + mean`
        # instead of `centres * sd + mean` — still captures 100% of the variance, because variance
        # is computed in standardised space. Only the native residual can see it.
        assert rows[0]["rms"] < 0.05, (
            f"{name} fits exactly at k=2, so its native residual must be ~0, not {rows[0]['rms']} "
            "— the cluster centre was not converted back into the driver's own units")
    assert joint[0]["captured"] < 0.5, (
        "two cells cannot capture eight corners; if they do, the fixture is not discriminating")

    # AND THE RMS COLUMN IS THE ONLY PART A PRACTITIONER CAN ARGUE WITH, so it must be a real
    # residual in the driver's own units and not a placeholder. On this fixture two cells fit each
    # driver exactly, so the RMS is ~0; widen to one cell and it must be the driver's own spread.
    one = wcd.per_driver_curve((1,), space=space)
    for name, expected in zip(wcd.DRIVERS, sd):
        got = one[name][0]["rms"]
        assert got == pytest.approx(expected, rel=0.05), (
            f"{name} at one cell must carry ITS OWN spread ({expected}) in ITS OWN units, not "
            f"{got} — a residual scored against another driver's column reads as a real number")


def test_the_curve_runs_THE_WAY_A_COMMAND_LINE_RUNS_IT():
    """Sixth module in this repository where the script entry point could be dead while every test
    is green: pytest fixes `sys.path` before a test can import anything, so `from tools import
    weather_cell_drivers` inside `_space` is never exercised by the suite. Probed with `sys.path[0]`
    forced to `tools`, because a plain `-c` leaves the working directory on the path and the
    assertion becomes a tautology."""
    import os
    import subprocess
    import sys as _sys

    done = subprocess.run(
        [_sys.executable, "-c",
         "import sys; sys.path[0] = 'tools';"
         "import runpy;"
         "runpy.run_path('tools/weather_cell_derivation.py', run_name='probe');"
         # the module's guard is what makes the next line work; without it this is the exact
         # ModuleNotFoundError `_space` raises on its first call from the command line
         "import tools.weather_cell_drivers, tools.weather_cell_weights"],
        cwd=str(wcd.PROJECT), capture_output=True, text=True, timeout=300,
        env={**os.environ, "PYTHONPATH": ""},
    )

    assert "ModuleNotFoundError" not in done.stderr, done.stderr
    assert done.returncode == 0, done.stderr
