"""Persistence and synchrony, each test named by the defect it exists to catch.

These are the figures a hedge would be priced off, so the failure that matters is not a crash: it
is a plausible number that overstates diversification, and nothing downstream could tell.
"""
from __future__ import annotations

import numpy as np
import pytest

from tools import weather_cell_persistence as wcp


def _series(monkeypatch, series, times, mass=None, rows=None, cols=None):
    n = series.shape[1]
    monkeypatch.setattr(wcp, "load_series", lambda: (
        series,
        np.array(times, dtype="datetime64[D]"),
        np.ones(n) if mass is None else np.asarray(mass, dtype=float),
        np.zeros(n, dtype=int) if rows is None else np.asarray(rows),
        np.arange(n) if cols is None else np.asarray(cols),
    ))


def _winter_days(years, months=(10, 11, 12, 1, 2, 3), per_month=10):
    out = []
    for year in years:
        for month in months:
            y = year if month >= 10 else year + 1
            out.extend(f"{y}-{month:02d}-{day + 1:02d}" for day in range(per_month))
    return out


def test_a_SPELL_CANNOT_SPAN_THE_ARCHIVES_SIX_MONTH_GAP(monkeypatch):
    """THE DEFECT. The archive holds October to March only, so 31 March and the next 1 October are
    adjacent ROWS and six months apart in TIME. Run them together and the measurement manufactures
    cold spells that never happened -- and manufactures the longest ones, because they are the
    joins. Nothing in the output would look wrong."""
    days = ["1999-03-29", "1999-03-30", "1999-03-31", "1999-10-01", "1999-10-02"]
    cold = np.array([[-9.0], [-9.0], [-9.0], [-9.0], [-9.0]])
    _series(monkeypatch, cold, days)

    winters = wcp._winter_index(np.array(days, dtype="datetime64[D]"))

    assert list(winters) == [1998, 1998, 1998, 1999, 1999], (
        "March belongs to the winter that began the previous October")
    assert len(set(winters)) == 2, "the March/October boundary must split the run"


def test_the_NULL_IS_A_PERMUTATION_so_only_CLUSTERING_differs(monkeypatch):
    """A null that resampled cold days from a Bernoulli would confound how OFTEN a cell is cold
    with whether the cold days CLUMP, and the ruling's claim is entirely about clumping. The
    permutation holds the count per cell per winter exactly fixed.

    Asserted by conservation: the observed and independent spell collections must contain the same
    number of cold DAYS, and differ only in how those days are cut into runs.
    """
    rng = np.random.default_rng(1)
    days = _winter_days(range(1991, 2001))
    # one cell whose cold days arrive in blocks
    values = rng.normal(6.0, 2.0, size=(len(days), 1))
    values[::20] = -5.0
    values[1::20] = -5.0
    _series(monkeypatch, values, days)

    result = wcp.persistence()
    observed_days = result["mean_length"]["observed"] * result["cold_spells_observed"]
    null_days = result["mean_length"]["independent"] * result["cold_spells_under_independence"]

    assert abs(observed_days - null_days) < 1.0, (
        f"the null changed the number of cold days ({observed_days} vs {null_days}); it is "
        "resampling frequency, not permuting clustering")
    assert result["cold_spells_observed"] < result["cold_spells_under_independence"], (
        "clustered cold days must form FEWER, longer spells than the same days shuffled")


def test_run_lengths_include_a_run_that_ENDS_AT_THE_LAST_DAY():
    """The classic off-by-one in run-length code: the loop appends on the falling edge, and a run
    still open when the array ends is silently discarded. A winter that ends mid-cold-snap is
    exactly the case that matters."""
    assert wcp._runs([True, True, False, True]) == [2, 1]
    assert wcp._runs([False, False]) == []
    assert wcp._runs([True] * 4) == [4], "a run open at the end of the array was dropped"


def test_the_COLD_THRESHOLD_IS_PER_CELL_and_not_one_national_number(monkeypatch):
    """THE CHOICE. A global threshold reports that Scotland has all the cold spells, which is true
    and useless: it measures where Britain is cold rather than where it is colder than it is built
    for. Two cells offset by 10 degC must produce the same spell statistics."""
    days = _winter_days(range(1991, 1996))
    rng = np.random.default_rng(2)
    base = rng.normal(0.0, 1.0, size=(len(days), 1))
    values = np.hstack([base + 5.0, base + 15.0])
    _series(monkeypatch, values, days)

    result = wcp.persistence()

    warm_only = np.hstack([base + 15.0])
    _series(monkeypatch, warm_only, days)
    single = wcp.persistence()

    assert result["mean_length"]["observed"] == pytest.approx(single["mean_length"]["observed"]), (
        "the warm cell contributed different spells: the threshold is not cell-relative")


def test_INDEPENDENT_CELLS_SCORE_A_LIFT_OF_ONE(monkeypatch):
    """CALIBRATION OF THE SYNCHRONY MEASURE, and the reason it is stated as a lift. A measure that
    could not return 1.0 for genuinely independent cells would make every real result look like
    synchrony, and 7.21 would mean nothing."""
    rng = np.random.default_rng(3)
    days = _winter_days(range(1991, 2021), per_month=25)
    values = rng.normal(5.0, 3.0, size=(len(days), 6))
    _series(monkeypatch, values, days)

    result = wcp.synchrony()

    assert 0.6 < result["mean_joint_cold_lift"] < 1.5, (
        f"independent cells scored {result['mean_joint_cold_lift']}, not ~1.0")
    assert result["worst_day_share"] < 1.0, "independent cells cannot all be cold on one day"


def test_PERFECTLY_LOCKED_CELLS_SCORE_TEN(monkeypatch):
    """The other end of the scale, so the measure is bounded at both ends rather than only shown
    to be large once."""
    rng = np.random.default_rng(4)
    days = _winter_days(range(1991, 2011), per_month=25)
    one = rng.normal(5.0, 3.0, size=(len(days), 1))
    values = np.hstack([one, one + 2.0, one - 3.0])
    _series(monkeypatch, values, days)

    result = wcp.synchrony()

    assert result["mean_joint_cold_lift"] == pytest.approx(10.0, abs=0.3)
    assert result["worst_day_share"] == pytest.approx(1.0)


def test_the_PORTFOLIO_SHARE_IS_HOUSEHOLD_WEIGHTED_and_not_cell_counted(monkeypatch):
    """The number that decides whether cells diversify is a share of the BOOK. Count cells instead
    and a cluster holding a hundred households counts the same as one holding four million -- the
    error runs in the flattering direction, because the sparse cells are the ones least likely to
    be cold at the same time as London."""
    days = _winter_days(range(1991, 2001), per_month=25)
    n = len(days)
    # Two cells that are NEVER cold together: the crowded one takes the first half of every
    # ranking, the empty one the second. Their coldest deciles are disjoint by construction.
    crowded = np.linspace(0.0, 10.0, n)
    empty = np.linspace(10.0, 0.0, n)
    values = np.column_stack([crowded, empty])

    _series(monkeypatch, values, days, mass=[4_000_000.0, 100.0])
    weighted = wcp.synchrony()

    _series(monkeypatch, values, days, mass=[1.0, 1.0])
    counted = wcp.synchrony()

    assert weighted["worst_day_share"] > 0.999, (
        "the crowded cell alone is essentially the whole book, so its own cold decile is a day on "
        "which the whole book is cold")
    assert counted["worst_day_share"] == pytest.approx(0.5), (
        "counting cells instead of households, the same day is a 'half the portfolio' event -- and "
        "the error runs in the flattering direction, because the sparse cells are the ones least "
        "likely to be cold when London is")


def test_the_GRID_ORIGIN_IS_MINUS_200KM_and_not_zero():
    """HadUK's 1 km grid starts at -199,500 m, not at 0. Use `east // 1000` and every extracted
    series comes from a point 200 km south-west of the cell it is labelled with -- still on land
    for most of Britain, still plausible, and wrong everywhere."""
    assert wcp.GRID_ORIGIN_M == -200_000
    assert (500 - wcp.GRID_ORIGIN_M) // 1000 == 200, "the first grid column must map to index 0+200"
    assert (0 - wcp.GRID_ORIGIN_M) // 1000 != 0, (
        "if the origin were zero this arithmetic would be a no-op and the constant unnecessary")


def test_the_ALTERNATIVE_DEFINITION_shows_a_FIXED_THRESHOLD_falling_unevenly(monkeypatch):
    """The Choice is priced, not argued. An absolute threshold must be shown to concentrate on some
    cells; if it fell evenly, the cell-relative definition would be an unnecessary complication and
    the docstring's reasoning would be wrong."""
    days = _winter_days(range(1991, 1996))
    rng = np.random.default_rng(6)
    base = rng.normal(0.0, 1.0, size=(len(days), 1))
    values = np.hstack([base + 2.0, base + 12.0])
    _series(monkeypatch, values, days, mass=[1.0, 9.0])

    result = wcp.absolute_threshold(5.0)

    assert result["share_of_days_below"]["max_cell"] > \
        result["share_of_days_below"]["min_cell"] * 5
    assert result["household_share_in_the_coldest_quartile_of_cells"] < 0.5, (
        "the cold cells hold a minority of the book, which is the whole objection")


def test_the_measurement_runs_THE_WAY_A_COMMAND_LINE_RUNS_IT():
    """Seventh module in this repository where a script entry point could be dead while every test
    is green, because pytest fixes `sys.path` before any test can import anything."""
    import os
    import subprocess
    import sys as _sys

    done = subprocess.run(
        [_sys.executable, "-c",
         "import sys; sys.path[0] = 'tools';"
         "import runpy;"
         "runpy.run_path('tools/weather_cell_persistence.py', run_name='probe');"
         "import tools.weather_cell_derivation, tools.weather_cell_weights"],
        cwd=str(wcp.PROJECT), capture_output=True, text=True, timeout=300,
        env={**os.environ, "PYTHONPATH": ""},
    )

    assert "ModuleNotFoundError" not in done.stderr, done.stderr
    assert done.returncode == 0, done.stderr
