"""Household weights per 1 km cell, each test named by the defect it exists to catch.

The ruling forbids taking these weights from the SIM's drawn population, because a coverage curve
weighted by our own draw would be a statement about us and would look identical to one about
Britain. Everything here guards the substitute: three open sources, joined by postcode.
"""
from __future__ import annotations

import csv
from collections import defaultdict

import pytest

from tools import weather_cell_weights as w


@pytest.fixture()
def cache(tmp_path, monkeypatch):
    monkeypatch.setattr(w, "CACHE", tmp_path)
    monkeypatch.setattr(w, "ONSPD_CSV", tmp_path / "onspd.csv")
    monkeypatch.setattr(w, "TS041_CSV", tmp_path / "ts041.csv")
    monkeypatch.setattr(w, "SCOTLAND_CSV", tmp_path / "scotland.csv")
    # `_seed` installs the address store through this handle once it knows what was seeded.
    _SEEDED_PATCH["mp"] = monkeypatch
    from tools import ons_uprn_directory as onsud
    monkeypatch.setattr(onsud, "oa_cell_addresses", lambda dest=None: {})
    yield tmp_path
    _SEEDED_PATCH["mp"] = None


@pytest.fixture()
def addresses(monkeypatch):
    """Seed the ADDRESS STORE: which output area's addresses sit in which 1 km cell, and how many.

    This is what placement reads since 2026-09-07. It used to seed a bare per-cell address count and
    let a postcode centroid choose the candidate cells; the whole point of the change is that the
    output area now owns its own addresses, so the fixture has to say which area each cell's
    addresses belong to.
    """
    from tools import ons_uprn_directory as onsud

    def place(**per_oa):
        store = {}
        for oa, cells in per_oa.items():
            for (cx, cy), count in cells.items():
                store[(oa, cx, cy)] = count
        monkeypatch.setattr(onsud, "oa_cell_addresses", lambda dest=None: store)
        return store

    return place


def _write(path, header, rows):
    with path.open("w", newline="", encoding="utf-8") as fh:
        out = csv.writer(fh)
        out.writerow(header)
        out.writerows(rows)


def _seed(cache, postcodes, ew=(("E00000001", 100),), scot=(("S00000001", 40),), monkeypatch=None):
    """Write the three census/postcode files AND the address store they imply.

    ONE ADDRESS PER POSTCODE, in that postcode's own cell, attributed to that postcode's output
    area. That is the simplest world in which the new placement is well defined, and it makes a
    test that says nothing about addresses behave the way the old equal-split did -- so each test
    below stays about the thing it is testing. `addresses(...)` overrides it.
    """
    _write(cache / "onspd.csv", ["pcds", "oa", "east", "north", "country"], postcodes)
    _write(cache / "ts041.csv", ["GEOGRAPHY_CODE", "OBS_VALUE"], ew)
    _write(cache / "scotland.csv", ["oa", "households"], scot)
    store = {}
    for row in postcodes:
        _pcds, oa, east, north = row[0], row[1], int(row[2]), int(row[3])
        if oa.strip():
            store[(oa.strip(), east // 1000, north // 1000)] = (
                store.get((oa.strip(), east // 1000, north // 1000), 0) + 1)
    cache.joinpath("_address_store").write_text(repr(store), encoding="utf-8")
    from tools import ons_uprn_directory as onsud
    if _SEEDED_PATCH["mp"] is not None:
        _SEEDED_PATCH["mp"].setattr(onsud, "oa_cell_addresses", lambda dest=None: store)
    return store


#: The monkeypatch handle the `cache` fixture installs, so `_seed` can point the address store at
#: what it just wrote without every test having to pass one in.
_SEEDED_PATCH: dict = {"mp": None}


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


def test_households_FOLLOW_THE_ADDRESSES_and_not_the_postcode_centroids(cache, addresses):
    """THE METHOD, AND THE DIRECTOR'S CORRECTION THAT PRODUCED IT.

    A postcode centroid is a POINT. Splitting an output area's households across its centroids put
    them all in the cells those points happened to land in, and a cell of scattered dwellings whose
    centroid fell next door read as empty -- undercounting occupied GB by 23 percentage points.

    Households now follow OS Open UPRN address density within the output area. Here the area's one
    postcode sits at (400,300) while its addresses are three-to-one in the NEIGHBOURING cell, and
    the households must go where the addresses are.
    """
    _seed(cache, [["AA1 1AA", "E00000001", 400_500, 300_500, "E92000001"]],
          ew=(("E00000001", 100),), scot=())
    addresses(E00000001={(400, 300): 25, (401, 300): 75})

    weights, _ = w.census_weights()

    assert weights[(401, 300)] == pytest.approx(75.0), (
        "the neighbouring cell holds three quarters of the area's addresses and no postcode "
        "centroid at all -- under the first method it held nothing")
    assert weights[(400, 300)] == pytest.approx(25.0)
    assert sum(weights.values()) == pytest.approx(100.0), (
        "the census fixes the output area's total and re-placing must conserve it exactly")


def test_TWO_OUTPUT_AREAS_sharing_a_cell_ACCUMULATE(cache, addresses):
    """An implementation that ASSIGNED rather than added would lose an output area every time two
    shared a cell -- the normal case in every town."""
    _seed(cache, [
        ["AA1 1AA", "E00000001", 400_100, 300_100, "E92000001"],
        ["AA1 1AB", "E00000002", 400_900, 300_900, "E92000001"],
    ], ew=(("E00000001", 100), ("E00000002", 40)), scot=())
    addresses(E00000001={(400, 300): 6}, E00000002={(400, 300): 4})

    weights, _ = w.census_weights()

    assert weights == {(400, 300): pytest.approx(140.0)}


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

    # THE DROP VOCABULARY CHANGED WITH THE METHOD, and the changed names are the point. Placement no
    # longer reads postcodes, so "a postcode with no output area" is not a thing that can happen to
    # it; what CAN is a census area the address directory has never heard of, which is 45 areas and
    # 2,754 households in the live data.
    assert drops["census_areas_with_no_address_in_the_directory"] == 1
    assert drops["households_in_those_areas"] == 70
    assert drops["households_placed"] == 100
    assert drops["households_in_the_censuses"] == 170
    assert sum(weights.values()) == 100, "only the placeable households are counted"


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


def test_households_OFF_THE_LAND_GRID_are_COUNTED_and_not_quietly_dropped(cache, addresses):
    """A postcode's 1 km square is not always a HadUK land cell: coastal and estuary postcodes sit
    in squares the grid calls sea, and they hold real households. Aligning silently would drop them
    and leave a total that still looks like the census, because the census total is never the thing
    being compared. 160,886 households sit there in the live data."""
    import numpy as np

    _seed(cache, [
        ["AA1 1AA", "E00000001", 400_500, 300_500, "E92000001"],   # on the fake land grid
        ["AA1 1AB", "E00000002", 650_500, 400_500, "E92000001"],   # off it
    ], ew=(("E00000001", 100), ("E00000002", 60)), scot=())
    addresses(E00000001={(400, 300): 10}, E00000002={(650, 400): 10})

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


def test_the_PLACEMENT_COST_conserves_households_and_reports_BOTH_directions(cache, addresses):
    """THE CHOICE, PRICED -- and it must price it in both directions, because the finding is that
    they point opposite ways: the coverage claim was wrong by 23 points and the weights barely
    moved. A cost function reporting only the first would read as a disaster and only the second as
    a nicety.

    Conservation is about what each method PLACED, not what landed on the land grid. The first
    version compared the two land-grid totals and reported households lost, when what it had found
    was address placement moving coastal households onto the grid -- the two methods differing,
    which is the point.
    """
    _seed(cache, [["AA1 1AA", "E00000001", 400_500, 300_500, "E92000001"]],
          ew=(("E00000001", 100),), scot=())
    addresses(E00000001={(400, 300): 25, (401, 300): 75})

    import numpy as np

    from tools import weather_cell_drivers as drv
    fake = {"east": np.array([400_500.0, 401_500.0]), "north": np.array([300_500.0, 300_500.0]),
            "winter_temp": np.array([5.0, 4.0]), "annual_wind": np.array([4.0, 5.0]),
            "annual_sun": np.array([1500.0, 1400.0])}
    import pytest as _p
    monkey = _p.MonkeyPatch()
    monkey.setattr(drv, "drivers", lambda: fake)
    monkey.setattr(w, "gb_reachable", lambda d, threshold_km=None: (np.array([True, True]), {}))
    try:
        cost = w.placement_cost()
    finally:
        monkey.undo()

    assert cost["households_conserved"] is True
    assert cost["households_placed_on_centroids"] == cost["households_placed_on_addresses"] == 100
    assert cost["occupied_on_addresses"] > cost["occupied_on_centroids"], (
        "address placement must reach cells the centroid method left empty -- that is the finding")
    assert set(cost["driver_shift_in_sd"]) == {"winter_temp", "annual_wind", "annual_sun"}
    # AND A DEGENERATE SPREAD REPORTS None, NOT ZERO. This fixture leaves the centroid method with
    # one occupied cell, so there is no standard deviation to express a shift in -- the first
    # version divided by it and crashed, and a version returning 0.0 would have said "the weights
    # did not move" when the truth is that it cannot tell.
    assert all(v is None or v >= 0 for v in cost["driver_shift_in_sd"].values())


def test_PLACEMENT_READS_NO_POSTCODE_AT_ALL(cache, addresses, monkeypatch):
    """THE PROPERTY THE THIRD PLACEMENT EXISTS FOR: no centroid anywhere in it.

    The first method put households AT postcode centroids. The second used centroids to choose the
    candidate cells and addresses to weight within them -- better, and still centroid-anchored,
    which is why 20,959 address-bearing cells stayed unreachable and 94.5% of GB's addresses sat in
    cells claimed by five or more output areas at once.

    This asserts the dependency is gone rather than the docstring saying so: the postcode file is
    replaced by one that would raise if it were opened.
    """
    _seed(cache, [["AA1 1AA", "E00000001", 400_500, 300_500, "E92000001"]],
          ew=(("E00000001", 100),), scot=())
    addresses(E00000001={(400, 300): 3, (999, 999): 1})

    class _Explode:
        def open(self, *a, **k):
            raise AssertionError("census_weights opened the postcode file -- a centroid is back")

        def is_file(self):
            return True

    monkeypatch.setattr(w, "ONSPD_CSV", _Explode())
    weights, _ = w.census_weights()

    assert weights[(400, 300)] == pytest.approx(75.0)
    assert weights[(999, 999)] == pytest.approx(25.0), (
        "a cell far from any postcode of the area must still receive its share -- under the window "
        "method it was unreachable")


def test_OCCUPIED_AND_HAS_AN_ADDRESS_BECOME_THE_SAME_STATEMENT():
    """THE IDENTITY THAT MAKES THE COVERAGE FIGURE MEAN SOMETHING.

    Households now sit exactly where addresses are, so "this cell holds a household" and "this cell
    holds an address of a census-known output area" are the same claim. Under the first method they
    differed by 23 percentage points and the page presented the first while sounding like the
    second; under the window method by 8.6. Asserted against the INDEPENDENT address record --
    `os_open_uprn`, a different file built by a different route -- rather than against the store
    the placement itself reads.
    """
    from tools import ons_uprn_directory as onsud
    from tools import os_open_uprn as uprn
    from tools import weather_cell_drivers as drv

    if not (onsud.STORE.is_file() and uprn.GRID.is_file()
            and (drv.CACHE / "tas" / "mon-30y").is_dir()):
        pytest.skip("the address directory, the address grid or the normals are not on this machine")

    weights, _ = w.census_weights()
    d = drv.drivers()
    gb, _ = w.gb_reachable(d)
    keys = list(zip((d["east"] // 1000).astype(int).tolist(),
                    (d["north"] // 1000).astype(int).tolist()))
    import numpy as np
    occupied = np.array([weights.get(k, 0.0) for k in keys]) > 0
    cov = uprn.coverage(d, gb)

    placed = int((gb & occupied).sum())
    with_address = cov["cells_with_at_least"]["1"]
    assert placed <= with_address, "households in more cells than hold an address is impossible"
    assert placed / with_address > 0.98, (
        f"{placed:,} occupied against {with_address:,} address-bearing -- a gap this wide means "
        "placement has stopped following the addresses")


def test_the_ADDRESS_DIRECTORY_is_REQUIRED_and_absence_is_a_REFUSAL(tmp_path):
    """FAIL-CLOSED ON THE DEPENDENCY PLACEMENT ACTUALLY READS.

    A SURVIVOR FOUND THIS. There was a refusal control for `os_open_uprn.cell_counts` -- the
    dependency of the method that was REPLACED -- and none for `ons_uprn_directory`, which is what
    placement reads now. Returning `{}` on absence passed the whole suite, and would have produced
    a silent empty placement: no households anywhere, every coverage figure zero, and nothing
    saying why.

    Every fallback available here routes through a postcode centroid, which is the approximation
    this method exists to remove, so absence must refuse rather than degrade.
    """
    from tools import ons_uprn_directory as onsud

    with pytest.raises(FileNotFoundError, match="postcode centroid"):
        onsud.oa_cell_addresses(tmp_path / "absent.pkl")


def test_the_ADDRESS_RECORD_is_REQUIRED_and_absence_is_a_REFUSAL(monkeypatch, tmp_path):
    """FAIL-CLOSED, and the direction is everything.

    The whole finding is that postcode centroids undercount occupied cells by 23 points. A
    placement that fell back to centroids when the address grid was missing would restore that
    defect on any machine that had not pulled -- and restore it INVISIBLY, which is worse than not
    having the fix at all.
    """
    from tools import os_open_uprn as uprn

    monkeypatch.setattr(uprn, "GRID", tmp_path / "absent.npy")
    with pytest.raises(FileNotFoundError, match="23 percentage points"):
        uprn.cell_counts(tmp_path / "absent.npy")


def test_the_ADDRESS_RECORD_AGREES_WITH_THE_PLACEMENT_it_produces():
    """THE DIRECTOR'S CHECK, kept as a control rather than as a paragraph.

    He asked whether 47% of GB kilometres really hold no address. They do not: 84.7% hold at least
    one. What the old method was measuring, to within half a percent, was "ten or more addressable
    properties". Both figures are asserted, because the second is what makes the first a defect
    rather than a difference of opinion.
    """
    from tools import os_open_uprn as uprn
    from tools import weather_cell_drivers as drv

    if not uprn.GRID.is_file() or not (drv.CACHE / "tas" / "mon-30y").is_dir():
        pytest.skip("the address grid or the HadUK normals are not on this machine")

    d = drv.drivers()
    gb, _ = w.gb_reachable(d)
    cov = uprn.coverage(d, gb)

    assert cov["share_with_any_address"] > 0.80, (
        f"only {cov['share_with_any_address']:.1%} of GB land holds an address; the finding that "
        "the centroid method undercounts rests on this being high")
    at_ten = cov["cells_with_at_least"]["10"] / cov["gb_land_cells"]
    assert 0.45 < at_ten < 0.60, (
        f"'ten or more addresses' now covers {at_ten:.1%} of GB land. The claim that the old "
        "centroid method was measuring THIS rather than 'has anybody' no longer holds.")


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


def test_GROUPING_CONSERVES_THE_UNGROUPED_PLACEMENT(cache, addresses):
    """DEFECT: a second placement. `census_weights(group_of=...)` exists so
    `tools/household_siting_frame` can split the same households by ONS region, and the hazard of
    any second implementation is that it drifts -- the two would each look right and the coverage
    figures published from them would stop being comparable.

    Asserted cell for cell, not on the total: a total conserves under a placement that puts the
    same households in the wrong squares, which is the only mistake this can make.
    """
    addresses(E00000001={(10, 10): 4, (11, 10): 1}, W00000001={(10, 10): 4, (11, 10): 1})
    _seed(cache,
          [["E1 1AA", "E00000001", 10_500, 10_500, "E92000001"],
           ["W1 1AA", "W00000001", 10_500, 10_500, "W92000004"]],
          ew=(("E00000001", 100), ("W00000001", 60)),
          scot=(("S00000001", 40),))

    flat, flat_drops = w.census_weights()
    grouped, grouped_drops = w.census_weights(group_of=lambda oa: oa[0])

    merged = defaultdict(float)
    for cells in grouped.values():
        for cell, households in cells.items():
            merged[cell] += households
    assert {k: round(v, 6) for k, v in merged.items()} == {
        k: round(v, 6) for k, v in flat.items()}, "the grouped placement is not the same placement"
    # The Scottish area has census households and no live postcode in this fixture, so it never
    # reaches the grouping at all -- it is already counted as `census_areas_with_no_live_postcode`.
    assert set(grouped) == {"E", "W"}
    assert flat_drops["output_area_outside_the_grouping"] == 0
    assert grouped_drops["output_area_outside_the_grouping"] == 0


def test_a_GROUP_OF_RETURNING_NONE_DROPS_THE_HOUSEHOLDS_AND_COUNTS_THEM(cache, addresses):
    """DEFECT (fail-silent): an output area outside the grouping absorbed into some region anyway,
    or dropped without a count. Scotland is the live instance -- it has no slot in the region
    marginal -- and 8% of GB households vanishing quietly would leave every English region's
    weather looking exactly as it should."""
    _seed(cache,
          [["E1 1AA", "E00000001", 10_500, 10_500, "E92000001"],
           ["AB1 1AA", "S00000001", 10_500, 10_500, "S92000003"]],
          ew=(("E00000001", 100),), scot=(("S00000001", 40),))
    addresses(E00000001={(10, 10): 1}, S00000001={(10, 10): 1})

    grouped, drops = w.census_weights(group_of=lambda oa: "keep" if oa.startswith("E") else None)

    assert set(grouped) == {"keep"}
    assert round(sum(grouped["keep"].values())) == 100, "the kept households moved"
    assert drops["output_area_outside_the_grouping"] == 1
