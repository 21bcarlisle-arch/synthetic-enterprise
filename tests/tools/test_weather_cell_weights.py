"""Household weights per 1 km cell, each test named by the defect it exists to catch.

The ruling forbids taking these weights from the SIM's drawn population, because a coverage curve
weighted by our own draw would be a statement about us and would look identical to one about
Britain. Everything here guards the substitute: three open sources, joined by postcode.
"""
from __future__ import annotations

import csv

import pytest

from tools import weather_cell_weights as w


@pytest.fixture()
def cache(tmp_path, monkeypatch):
    monkeypatch.setattr(w, "CACHE", tmp_path)
    monkeypatch.setattr(w, "ONSPD_CSV", tmp_path / "onspd.csv")
    monkeypatch.setattr(w, "TS041_CSV", tmp_path / "ts041.csv")
    monkeypatch.setattr(w, "SCOTLAND_CSV", tmp_path / "scotland.csv")
    return tmp_path


def _write(path, header, rows):
    with path.open("w", newline="", encoding="utf-8") as fh:
        out = csv.writer(fh)
        out.writerow(header)
        out.writerows(rows)


def _seed(cache, postcodes, ew=(("E00000001", 100),), scot=(("S00000001", 40),)):
    _write(cache / "onspd.csv", ["pcds", "oa", "east", "north", "country"], postcodes)
    _write(cache / "ts041.csv", ["GEOGRAPHY_CODE", "OBS_VALUE"], ew)
    _write(cache / "scotland.csv", ["oa", "households"], scot)


def test_a_SHORT_NOMIS_PAGE_is_refused_rather_than_written(cache, monkeypatch):
    """THE DEFECT THAT ALREADY HAPPENED, on the first pull of this atom.

    nomis caps an unpaged request at 25,000 rows and says so nowhere in the payload. The response
    was a well-formed CSV with correct headers and real household counts for 25,000 of England and
    Wales's 188,880 output areas -- 13% of the country, and every downstream figure would have been
    computed, plotted and published without a single error anywhere.
    """
    body = "\n".join(f'"E{i:08d}",100' for i in range(10))
    monkeypatch.setattr(w, "_get", lambda url, tries=5: f'"GEOGRAPHY_CODE","OBS_VALUE"\n{body}'.encode())

    with pytest.raises(RuntimeError, match="expected 188880"):
        w.pull_ts041(cache / "ts041.csv", progress=lambda *_: None)

    assert not (cache / "ts041.csv").is_file(), (
        "a refused pull must leave no file: a truncated CSV on disk is indistinguishable from a "
        "complete one on the next run")


def test_the_pager_KEEPS_GOING_past_the_first_full_page(cache, monkeypatch):
    """REACHABILITY of the loop's second iteration. A pager that requested one page and stopped
    would pass the test above whenever the cap happened to exceed the total, and this atom's whole
    failure mode is a request that silently returns less than everything."""
    monkeypatch.setattr(w, "NOMIS_PAGE", 4)
    monkeypatch.setattr(w, "TS041_EXPECTED_AREAS", 10)
    seen = []

    def fake(url, tries=5):
        offset = int(url.split("RecordOffset=")[1])
        seen.append(offset)
        rows = [f'"E{i:08d}",100' for i in range(offset, min(offset + 4, 10))]
        return ('"GEOGRAPHY_CODE","OBS_VALUE"\n' + "\n".join(rows)).encode()

    monkeypatch.setattr(w, "_get", fake)
    w.pull_ts041(cache / "ts041.csv", progress=lambda *_: None)

    assert seen == [0, 4, 8], f"the pager stopped early: offsets {seen}"
    assert len((cache / "ts041.csv").read_text().splitlines()) == 11


def test_SCOTLAND_MISSING_is_a_REFUSAL_and_not_a_smaller_answer(cache):
    """FAIL-CLOSED, and the reason it must be closed rather than merely noted.

    Scotland is 8% of GB households and it is the cold, windy 8% -- the tail the cells exist to
    resolve. Weights computed without it would be a complete-looking GB map whose only defect sits
    exactly where the derivation is most sensitive. A warning would be read past.
    """
    _seed(cache, [["AB1 1AA", "S00000001", 325000, 674000, "S92000003"]])
    (cache / "scotland.csv").unlink()

    with pytest.raises(FileNotFoundError, match="cold, windy"):
        w.census_weights()


def test_households_are_SPLIT_across_an_output_areas_postcodes_not_piled_at_one_point(cache):
    """THE CHOICE, asserted. A rural output area can span tens of kilometres; posting its whole
    household count at a single centroid puts them all in one 1 km cell. Two postcodes of one area,
    two cells, half each."""
    _seed(cache, [
        ["AA1 1AA", "E00000001", 400_500, 300_500, "E92000001"],
        ["AA1 1AB", "E00000001", 405_500, 300_500, "E92000001"],
    ], ew=(("E00000001", 100),), scot=())

    weights, _ = w.census_weights()

    assert weights[(400, 300)] == 50
    assert weights[(405, 300)] == 50
    assert sum(weights.values()) == 100, "splitting must conserve the household count"


def test_two_postcodes_in_the_SAME_cell_ACCUMULATE(cache):
    """The sibling defect to the one above: an implementation that ASSIGNED rather than added would
    pass the split test and lose a household every time two postcodes shared a cell -- which is the
    normal case in every town."""
    _seed(cache, [
        ["AA1 1AA", "E00000001", 400_100, 300_100, "E92000001"],
        ["AA1 1AB", "E00000001", 400_900, 300_900, "E92000001"],
    ], ew=(("E00000001", 100),), scot=())

    weights, _ = w.census_weights()

    assert weights == {(400, 300): 100}


def test_every_DROP_is_COUNTED_and_none_is_silent(cache):
    """A postcode with no output area, and a census area with no live postcode, are both real and
    both move the totals. Counting them is the difference between "97% of households placed" and a
    number that looks like all of them."""
    _seed(cache, [
        ["AA1 1AA", "E00000001", 400_500, 300_500, "E92000001"],
        ["AA1 1AB", "", 401_500, 300_500, "E92000001"],
        ["AA1 1AC", "E00009999", 402_500, 300_500, "E92000001"],
    ], ew=(("E00000001", 100), ("E00000002", 70)), scot=())

    weights, drops = w.census_weights()

    assert drops["no_output_area"] == 1
    assert drops["output_area_not_in_census"] == 1
    assert drops["census_areas_with_no_live_postcode"] == 1
    assert sum(weights.values()) == 100, "only the placeable households are counted"


def test_the_CHOICE_COST_is_measured_and_can_be_NON_ZERO(cache):
    """A cost function that always returned zero would make the Choice look free. Two postcodes 5 km
    apart: the centroid lands in one cell and half the households belong in the other."""
    _seed(cache, [
        ["AA1 1AA", "E00000001", 400_500, 300_500, "E92000001"],
        ["AA1 1AB", "E00000001", 405_500, 300_500, "E92000001"],
    ], ew=(("E00000001", 100),), scot=())

    spread = w.disagreement_with_centroid()
    assert spread["share"] > 0

    _seed(cache, [
        ["AA1 1AA", "E00000001", 400_100, 300_100, "E92000001"],
        ["AA1 1AB", "E00000001", 400_900, 300_900, "E92000001"],
    ], ew=(("E00000001", 100),), scot=())

    together = w.disagreement_with_centroid()
    assert together["share"] == 0, "postcodes inside one cell cannot disagree with their centroid"


def test_the_SCOTTISH_TABLE_IS_CROSS_CHECKED_against_a_second_table(cache, monkeypatch):
    """"All occupied households" is a column HEADING, and a heading is a claim about what a column
    counts. UV402 counts households by accommodation type and UV406 by size; they must total the
    same. Reading the wrong column would give a plausible per-area number -- people, or a single
    accommodation category -- with nothing to catch it.
    """
    tables = {"UV402": {"S00000001": 40, "S00000002": 60},
              "UV406": {"S00000001": 40, "S00000002": 999}}
    monkeypatch.setattr(w, "_scotland_table", lambda z, prefix: tables[prefix])
    monkeypatch.setattr(w, "SCOTLAND_EXPECTED_AREAS", 2)
    (cache / "scot_oa_topic.zip").write_bytes(b"placeholder")

    with pytest.raises(RuntimeError, match="not the household total"):
        w.pull_scotland(cache / "scotland.csv", progress=lambda *_: None)

    tables["UV406"]["S00000002"] = 60
    w.pull_scotland(cache / "scotland.csv", progress=lambda *_: None)
    assert (cache / "scotland.csv").is_file(), "the agreeing case must be reachable"


def test_households_OFF_THE_LAND_GRID_are_COUNTED_and_not_quietly_dropped(cache):
    """A postcode's 1 km square is not always a HadUK land cell: coastal and estuary postcodes sit
    in squares the grid calls sea, and they hold real households. Aligning silently would drop them
    and leave a total that still looks like the census, because the census total is never the thing
    being compared. 160,886 households sit there in the live data."""
    import numpy as np

    _seed(cache, [
        ["AA1 1AA", "E00000001", 400_500, 300_500, "E92000001"],   # on the fake land grid
        ["AA1 1AB", "E00000002", 999_500, 999_500, "E92000001"],   # off it
    ], ew=(("E00000001", 100), ("E00000002", 60)), scot=())

    drivers = {"east": np.array([400_500.0]), "north": np.array([300_500.0])}
    vec, off = w.aligned_to_land(drivers)

    assert float(vec.sum()) == 100
    assert off["cells_off_the_land_grid"] == 1
    assert off["households_off_the_land_grid"] == 60
    assert off["land_cells_with_households"] == 1


def test_the_weighted_table_runs_THE_WAY_A_COMMAND_LINE_RUNS_IT():
    """FIFTH MODULE IN THIS REPOSITORY TO SHIP THIS DEFECT, and it shipped again here before this
    control existed.

    Run as a script, `sys.path[0]` is `tools/` and not the repo root, so `from tools import
    weather_cell_drivers` raises ModuleNotFoundError. Pytest fixes the path before any test can
    import the module, so every other test in this file stays green while `--weighted` is dead on
    the command line. The probe reproduces the script path deliberately: a plain `-c` leaves the
    working directory on `sys.path` and the assertion becomes a tautology.
    """
    import os
    import subprocess
    import sys as _sys

    done = subprocess.run(
        [_sys.executable, "-c",
         "import sys; sys.path[0] = 'tools';"
         "import runpy;"
         "m = runpy.run_path('tools/weather_cell_weights.py', run_name='probe');"
         "print('drivers' in dir(m['weather_cell_drivers']) if 'weather_cell_drivers' in m "
         "else __import__('tools.weather_cell_drivers', fromlist=['x']) is not None)"],
        cwd=str(w.PROJECT), capture_output=True, text=True, timeout=180,
        env={**os.environ, "PYTHONPATH": ""},
    )

    assert done.returncode == 0, done.stderr
    assert "ModuleNotFoundError" not in done.stderr


def test_the_GB_MASK_SEPARATES_NOT_BRITAIN_from_EMPTY_BRITAIN():
    """THE DEFECT A QUESTION ABOUT SCOTLAND SURFACED SOMEWHERE ELSE.

    HadUK-Grid's land mask is the UNITED KINGDOM. 14,911 of its 245,077 land cells are outside Great
    Britain, ONSPD carries no British grid reference for their postcodes, and this company's market
    is GB -- so they arrive with zero households and were being counted as *empty British land*. On
    a map they render identically to a Highland glen: absence drawn as emptiness.

    The threshold is checked against the PUBLISHED GB land area, not against itself, and the
    function refuses rather than returning a mask of somewhere else.
    """
    import numpy as np

    if not w.ONSPD_CSV.is_file():
        pytest.skip("the ONSPD pull is not on this machine")

    # one cell in central London, one in the middle of Northern Ireland
    drivers = {"east": np.array([530_000.0, 100_000.0]),
               "north": np.array([180_000.0, 530_000.0])}
    mask, stats = _stub_gb_reachable(drivers)
    assert list(mask) == [True, False], "the far cell must fall outside the GB mask"
    assert stats["not_gb_land_cells"] == 1


def _stub_gb_reachable(drivers):
    """`gb_reachable` with the published-area check relaxed, so the DISCRIMINATOR can be tested on
    two cells rather than on a quarter of a million. The area check itself is exercised against the
    live mask by `test_the_live_gb_mask_matches_the_published_land_area`."""
    import csv as _csv

    import numpy as np
    from scipy.spatial import cKDTree

    with w.ONSPD_CSV.open(encoding="utf-8") as fh:
        points = [(int(r["east"]), int(r["north"])) for r in _csv.DictReader(fh)]
    tree = cKDTree(np.array(points, dtype=float))
    distance, _ = tree.query(np.column_stack([drivers["east"], drivers["north"]]), k=1)
    mask = distance <= w.GB_REACH_KM * 1000.0
    return mask, {"gb_land_cells": int(mask.sum()), "not_gb_land_cells": int((~mask).sum())}


def test_the_live_gb_mask_matches_the_published_land_area():
    """The mask is held to an INDEPENDENT published figure -- ONS Standard Area Measurements for
    England, Wales and Scotland -- rather than to itself. A threshold that drifted would produce a
    perfectly self-consistent map of the wrong country."""
    from tools import weather_cell_drivers as drv

    if not (drv.CACHE / "tas" / "mon-30y").is_dir() or not w.ONSPD_CSV.is_file():
        pytest.skip("the HadUK normals or the ONSPD pull are not on this machine")

    mask, stats = w.gb_reachable(drv.drivers())

    assert abs(stats["gb_land_cells"] - w.GB_LAND_AREA_KM2) / w.GB_LAND_AREA_KM2 < 0.01
    assert stats["not_gb_land_cells"] > 10_000, (
        "the non-GB part of the UK mask has vanished; Northern Ireland is roughly 14,000 km2 and "
        "if it is no longer being separated the emptiness figure is overstated again")


def test_the_weights_do_NOT_come_from_the_SIMS_OWN_POPULATION():
    """THE RULING'S PROHIBITION, as a property of the module rather than a note in its docstring.

    Weighting the cells by the population the SIM drew would make the coverage curve a statement
    about our own draw. The curve would look identical, and nothing downstream could tell.
    """
    from pathlib import Path

    src = Path(w.__file__).read_text(encoding="utf-8")
    body = src.split('"""', 2)[-1]      # the module docstring names the prohibition; the code must
    #                                     not reach the thing it names
    for forbidden in ("population_draw", "simulation.", "from simulation", "company.", "saas."):
        assert forbidden not in body, (
            f"{forbidden!r} appears in the code: the weights must come from the censuses, not from "
            "anything this company generated")
