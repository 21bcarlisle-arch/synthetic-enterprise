"""The driver loader, each test named by the defect it exists to catch.

`W1_19` published a range table and six correlations from a shell session that no longer exists.
These tests are what makes that table a claim anyone can open.
"""
from __future__ import annotations

import numpy as np
import pytest

from tools import weather_cell_drivers as wcd

pytestmark = pytest.mark.skipif(
    not (wcd.CACHE / "tas" / "mon-30y").is_dir(),
    reason="HadUK-Grid normals are not in this machine's cache")


@pytest.fixture(scope="module")
def d():
    return wcd.drivers()


def test_every_driver_is_FLATTENED_TO_LAND_and_carries_no_sea(d):
    """THE DEFECT. The grid is 1,305,000 cells and 81% of them are sea, carrying NaN. Drop the
    `[mask]` and every array is 5.3x longer, every correlation is nan, and the failure surfaces
    somewhere downstream as a missing number rather than here as a wrong shape.

    Note what this does NOT claim. `np.nanmean` over the full array returns the land mean exactly,
    because skipping NaN IS the mask -- so "the unmasked mean is different" would be false, and a
    control asserting it would be asserting something untrue about the data.
    """
    assert d["land_cells"] == 245_077
    for key in ("annual_temp", "winter_temp", "annual_wind", "annual_sun", "latitude", "east"):
        assert d[key].size == d["land_cells"], f"{key} is not flattened to the land mask"
        assert not np.isnan(d[key]).any(), f"{key} carries sea cells"

    grid = wcd.GRID_SHAPE[0] * wcd.GRID_SHAPE[1]
    assert d["land_cells"] / grid < 0.25, (
        "if most of the grid were land the mask would not be load-bearing and this suite would be "
        "guarding nothing")


def test_the_three_VARIABLE_masks_coincide_in_this_release_which_is_an_EQUIVALENCE_not_a_control(d):
    """`drivers()` intersects the land masks of tas, sfcWind and sun. On the 1991-2020 normals all
    three are the same 245,077 cells, so the intersection changes nothing and mutating it away
    would not fire.

    Established rather than assumed, and recorded rather than deleted: a variable added later, or a
    release with a different coastline treatment, makes it bind. What this asserts is the
    equivalence itself -- if the masks ever diverge, this reds and the intersection starts earning
    its place.
    """
    masks = {v: ~np.isnan(wcd._monthly(v)).any(axis=0) for v in ("tas", "sfcWind", "sun")}
    counts = {v: int(m.sum()) for v, m in masks.items()}

    assert set(counts.values()) == {d["land_cells"]}, (
        f"the per-variable masks have diverged: {counts}. The intersection in `drivers()` is now "
        "load-bearing and the figures published from a single-variable mask are wrong.")


def test_SUNSHINE_IS_SUMMED_over_the_year_and_not_averaged(d):
    """A monthly sunshine normal is a TOTAL in hours, so the annual figure is a sum. Averaging
    gives a median near 119 -- a plausible-looking number, wrong by a factor of twelve, and with
    nothing in the units to catch it. Pinned to the physical range instead of to today's value."""
    med = float(np.median(d["annual_sun"]))
    assert 900 < med < 2000, f"annual sunshine median {med} h is not an ANNUAL duration"
    assert float(d["annual_sun"].max()) < 4380, "no GB cell gets half the year in sunshine"


def test_the_two_NORTH_SOUTH_measures_are_NOT_interchangeable(d):
    """W1_19 published -0.806 for latitude x sunshine. The OSGB northing gives -0.807, because the
    projection converges northward. A module that silently substituted one for the other would
    reproduce the published table to two decimals and disagree at the third -- which is exactly how
    an unreproducible figure gets called reproduced."""
    lat_r = np.corrcoef(d["latitude"], d["annual_sun"])[0, 1]
    north_r = np.corrcoef(d["north"], d["annual_sun"])[0, 1]

    assert round(float(lat_r), 3) != round(float(north_r), 3), (
        "if these agree to three decimals the distinction this module draws is not real")
    assert not np.array_equal(d["latitude"], d["north"])


def test_the_published_W1_19_table_reproduces():
    """THE POINT OF THE MODULE. Keyed to the PUBLISHED figures, so it reds if the loader changes
    what it reads -- and the document beside it names the same numbers."""
    m = wcd.measurement()

    assert m["land_cells"] == 245_077
    assert m["ranges"]["winter_temp"]["min"] == -2.96
    assert m["ranges"]["annual_wind"]["max"] == 16.36
    c = m["correlations"]
    assert c["latitude_x_sunshine"] == -0.806
    assert c["annual_temp_x_sunshine"] == 0.841
    assert c["winter_temp_x_winter_wind"] == -0.43


def test_the_SPATIAL_winter_correlation_is_NEGATIVE_and_the_repos_TEMPORAL_one_is_POSITIVE():
    """THE FINDING, and the control that stops it being flattened back.

    The ruling predicted winter temperature and wind positively correlated; across land cells it is
    -0.430, while `W1_COUPLED_WEATHER_CASCADE_DISCOVER` records +0.507 in TIME. Both are right and
    they answer different questions. A later change that made this module agree with the temporal
    figure would look like a bug being fixed.
    """
    from pathlib import Path

    m = wcd.measurement()
    assert m["correlations"]["winter_temp_x_winter_wind"] < 0

    doc = Path(wcd.__file__).resolve().parent.parent / "docs" / "market_research" / \
        "the_three_weather_drivers_per_land_cell_and_the_sign_that_flips.md"
    assert doc.is_file(), "the finding is published in a document that must exist beside the code"
    text = doc.read_text(encoding="utf-8")
    assert "+0.507" in text and "0.430" in text, (
        "the published document must carry BOTH signs; one alone is the definitional failure")


def test_a_grid_that_is_not_the_1km_grid_is_REFUSED_rather_than_reshaped(monkeypatch):
    """FAIL-CLOSED on the wrong product. HadUK also publishes 5 km, 12 km and 25 km grids under the
    same variable names. A loader that accepted whatever shape arrived would place every cell
    somewhere else and report nothing."""
    import numpy as _np

    monkeypatch.setattr(wcd, "GRID_SHAPE", (290, 180))
    with pytest.raises(ValueError, match="expected"):
        wcd._monthly("tas")

    monkeypatch.undo()
    monkeypatch.setattr(wcd, "EXPECTED_LAND_CELLS", 1)
    monkeypatch.setattr(wcd, "_monthly", lambda v: _np.zeros((12, *wcd.GRID_SHAPE)))
    with pytest.raises(ValueError, match="land mask"):
        wcd.drivers()


def test_a_missing_pull_names_the_command_that_fixes_it(tmp_path, monkeypatch):
    """A refusal that says only "not found" sends the reader hunting. This one is checked because
    the pull is a 20 GB operation nobody re-derives by guesswork."""
    monkeypatch.setattr(wcd, "CACHE", tmp_path)
    with pytest.raises(FileNotFoundError, match="fetch_haduk_grid"):
        wcd._normals_path("tas")
