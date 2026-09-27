"""The household siting frame's build — W2_18. Each test named by the defect it exists to catch.

The frame decides where every drawn household in the world is. Everything here guards the ways it
could be built wrongly and still produce a file full of perfectly plausible coordinates.
"""
from __future__ import annotations

import csv
import json

import pytest

from tools import household_siting_frame as f


def _page(rows: list[tuple[str, str]], total: int | None = None) -> bytes:
    """Serve the service's own shape: a Welsh row carries a NULL region and a country code."""
    return json.dumps({"features": [
        {"attributes": {"OA21CD": oa,
                        "RGN25CD": None if rgn.startswith("W9") else rgn,
                        "CTRY25CD": rgn if rgn.startswith("W9") else "E92000001"}}
        for oa, rgn in rows]}).encode()


def _server(monkeypatch, rows: list[tuple[str, str]], total: int | None = None):
    """Serve `rows` the way the real service does — a KEYSET scan on OA21CD, two rows a page.

    The fake answers `OA21CD>'<cursor>'` rather than an offset, because that is the query the
    pager now sends; a fake that still understood offsets would keep passing after the pager was
    changed and prove nothing about it.
    """
    monkeypatch.setattr(f, "PAGE", 2)
    monkeypatch.setattr(f, "EXPECTED_OUTPUT_AREAS", len(rows) if total is None else total)

    def fake(url: str, tries: int = 5) -> bytes:
        if "returnCountOnly" in url:
            return json.dumps({"count": len(rows) if total is None else total}).encode()
        cursor = ""
        if "OA21CD%3E%27" in url:
            cursor = url.split("OA21CD%3E%27")[1].split("%27")[0]
        after = [r for r in sorted(rows) if r[0] > cursor]
        return _page(after[:2])

    monkeypatch.setattr(f, "_get", fake)


def test_an_OUTPUT_AREA_IN_TWO_REGIONS_is_refused(monkeypatch, tmp_path):
    """THE DEFECT THAT ALREADY HAPPENED, on the route this module tried first. ONSPD assigns a
    region to a POSTCODE, and output area E00174957 holds postcodes in both London and the South
    East. Read as an output-area attribute it would have taken whichever postcode came back first
    and reported nothing at all.

    The check outlived its cause deliberately: the lookup this module now reads is one row per
    output area, so it can only fail this way if ONS changes what the table is."""
    _server(monkeypatch, [("E00000001", "E12000007"), ("E00000001", "E12000008")], total=2)
    with pytest.raises(ValueError, match="two regions"):
        f.pull_oa_regions(tmp_path / "oa.csv", progress=lambda *_: None)
    assert not (tmp_path / "oa.csv").is_file(), (
        "a refused pull must leave no file: a partial lookup on disk is indistinguishable from a "
        "complete one on the next run")


def test_a_SHORT_LOOKUP_is_refused_rather_than_written(monkeypatch, tmp_path):
    """DEFECT: a paged service that stops returning rows before the total, which is exactly how
    `weather_cell_weights` was once handed 25,000 of 188,880 output areas with no error anywhere.
    A frame built from a prefix covers a real-looking subset of England and sites everyone else
    nowhere."""
    _server(monkeypatch, [("E00000001", "E12000007"), ("E00000002", "E12000007")], total=4)
    with pytest.raises(ValueError, match="prefix"):
        f.pull_oa_regions(tmp_path / "oa.csv", progress=lambda *_: None)
    assert not (tmp_path / "oa.csv").is_file()


def test_a_CHANGED_GEOGRAPHY_is_refused_because_the_census_counts_are_keyed_to_2021(
        monkeypatch, tmp_path):
    """DEFECT: joining 2021 census household counts to a later output-area geography. The join
    would still succeed for most areas and the households in the changed ones would move."""
    _server(monkeypatch, [("E00000001", "E12000007")], total=1)
    monkeypatch.setattr(f, "EXPECTED_OUTPUT_AREAS", 188_880)
    with pytest.raises(ValueError, match="geography has changed"):
        f.pull_oa_regions(tmp_path / "oa.csv", progress=lambda *_: None)


def test_an_UNNAMEABLE_REGION_CODE_is_refused_rather_than_dropped(monkeypatch, tmp_path):
    """DEFECT: a region code this module cannot name being silently skipped. Every household in it
    would fall out of the frame, and the regions that remain would still look complete."""
    _server(monkeypatch, [("E00000001", "E12000007"), ("N00000001", "N92000002")], total=2)
    with pytest.raises(ValueError, match="cannot name"):
        f.pull_oa_regions(tmp_path / "oa.csv", progress=lambda *_: None)


def test_the_PAGER_KEEPS_GOING_past_the_first_page(monkeypatch, tmp_path):
    """REACHABILITY of the loop's second iteration: a pager that asked once and stopped would pass
    every refusal above whenever the page size happened to exceed the total."""
    rows = [(f"E{i:08d}", "E12000007") for i in range(6)]
    _server(monkeypatch, rows)
    f.pull_oa_regions(tmp_path / "oa.csv", progress=lambda *_: None)
    with (tmp_path / "oa.csv").open(encoding="utf-8") as fh:
        assert len(list(csv.DictReader(fh))) == 6


def test_WALES_SURVIVES_A_NULL_REGION_COLUMN(monkeypatch, tmp_path):
    """THE DEFECT THAT ALREADY HAPPENED, on this module's first complete pull. Wales is a COUNTRY
    and this table's region column is England's, so all 10,275 Welsh output areas carry a NULL
    region — and `if not rgn: continue` dropped every one of them. That is 5.7% of the
    curriculum's households and one of its ten regions, gone, with nine regions still looking
    perfectly complete.

    Found by the count check, not by reading the code: 178,605 + 10,275 = 188,880.
    """
    rows = [("E00000001", "E12000007"), ("W00000001", "W92000004")]
    _server(monkeypatch, rows)
    f.pull_oa_regions(tmp_path / "oa.csv", progress=lambda *_: None)
    namer = f.region_namer(tmp_path / "oa.csv")
    assert namer("W00000001") == "Wales", "Wales was dropped for having no region code"
    assert namer("E00000001") == "London"


def test_the_NAMER_NEVER_FOLDS_SCOTLAND_INTO_ANOTHER_REGION(monkeypatch, tmp_path):
    """DEFECT: an output area being given the nearest available name. Scotland is 9% of GB
    households and it is the cold, windy 9% -- folded into the North East it would move that
    region's weather and leave the national total looking right.

    KEYED TO THE PROPERTY, AND IT WAS NOT BEFORE. Until 2026-09-07 this asserted `namer("S00...")
    is None`, which is satisfied by two opposite worlds: Scotland correctly held apart, and
    Scotland silently LOST. It was the second -- 46,270 Scottish output areas arrived from the
    census join with their households counted and were discarded by this namer, and this control
    was green throughout because `None` was the answer it wanted. What must be true is that a
    Scottish area never wears an English or Welsh label; whether it wears its own is a separate
    question, asserted separately below so neither leg can stand in for the other."""
    path = tmp_path / "oa.csv"
    with path.open("w", newline="", encoding="utf-8") as fh:
        out = csv.writer(fh)
        out.writerow(["oa", "region_code"])
        out.writerows([["E00000001", "E12000007"], ["W00000001", "W92000004"]])
    namer = f.region_namer(path)
    assert namer("E00000001") == "London"
    assert namer("W00000001") == "Wales"

    scottish = namer("S00000001")
    not_scotland = set(f.REGION_NAMES.values()) | {f.WALES}
    assert scottish not in not_scotland, (
        f"a Scottish output area was folded into {scottish!r} -- its households would move that "
        "region's weather and the GB total would still look right")
    assert scottish == f.SCOTLAND, (
        "a Scottish output area is no longer dropped: it carries its own region, because the "
        "census join has counted its households all along")


def test_THE_LABELLER_NAMES_EVERY_OUTPUT_AREA_THE_CENSUS_JOIN_COUNTED():
    """DEFECT — THE ONE THAT ACTUALLY HAPPENED, and it ran for the frame's whole life. The
    labeller returned None for a whole country, `census_weights` counted that in
    `output_area_outside_the_grouping` exactly as designed, the number was written into the
    committed manifest at 46,270, and nothing anywhere read it. A drop counter is not a control.

    Read off the COMMITTED artefact, so it is a claim about what ships rather than about a fixture,
    and it needs no census cache. Keyed to the property `the frame's population is the join's
    population`, so it stays honest if the sources gain a country or the namer loses one."""
    _assert_the_join_lost_nothing(json.loads(f.FRAME_MANIFEST.read_text(encoding="utf-8")))


def _assert_the_join_lost_nothing(manifest: dict) -> None:
    dropped = manifest["diagnostics"]["output_area_outside_the_grouping"]
    assert dropped == 0, (
        f"{dropped} output areas arrived from the census join with household counts and were "
        "discarded for want of a region label. That is not a scope limit -- the join already "
        "holds them -- it is a lost region, and the households vanish from the frame while every "
        "published GB coverage figure still counts their cells")


def test_the_lost_region_control_fires_on_the_manifest_that_shipped_for_weeks():
    """The reachability leg: an assertion on a committed number proves nothing unless the number
    could be something else and the assertion would then fire. The witness is not invented — it is
    the frame's OWN manifest as it stood before 2026-09-07, when the counter read 46,270.

    That the counter can MOVE is a separate property and belongs where the counter is written:
    `test_weather_cell_weights.py::...output_area_outside_the_grouping == 1`. This leg is only
    about whether the reader above can refuse."""
    with pytest.raises(AssertionError, match="lost region"):
        _assert_the_join_lost_nothing(
            {"diagnostics": {"output_area_outside_the_grouping": 46_270}})


def test_the_BUILD_REFUSES_A_FRAME_THAT_DOES_NOT_COVER_THE_CURRICULUMS_REGIONS(monkeypatch):
    """DEFECT, and it is the silent one: a frame covering nine of the ten regions the curriculum
    draws. Nine regions' households are sited, the tenth quietly goes back to `lat: None`, and
    nothing on any surface distinguishes that slice from the honest placeholder answer."""
    monkeypatch.setattr(f, "frame", lambda: ({"London": [(51.5, -0.1, 10.0)]}, {}))
    with pytest.raises(ValueError, match="Missing"):
        f.build(progress=lambda *_: None)


def test_the_EXPECTED_REGIONS_come_from_the_CURRICULUM_and_not_from_a_list_here():
    """DEFECT (R15, keyed to today's answer): a hard-coded region list in this module, which cannot
    notice the director adding a region to the marginal -- the exact change the control above exists
    to catch."""
    import inspect

    from simulation.population_draw import _load_cohort_curriculum, region_weights_from_curriculum

    assert f.expected_regions() == set(region_weights_from_curriculum(_load_cohort_curriculum()))
    src = inspect.getsource(f.expected_regions)
    assert "region_weights_from_curriculum" in src
    for name in f.REGION_NAMES.values():
        assert f'"{name}"' not in src, f"{name!r} is listed in expected_regions() rather than read"


# ---------------------------------------------------------------------------
# W2_19: the output areas of each committed cell
# ---------------------------------------------------------------------------

def _oa_build(monkeypatch, tmp_path, committed, placed):
    """Build the output-area frame over a fake committed frame and a fake placement.

    `committed` is [(region, cell)]; each cell (x, y) gets coordinate (50 + y/100, x/100)."""
    from tools import weather_cell_weights as wcw

    cells = sorted({c for _, c in committed} | {c for p in placed.values() for c in p})
    index = {c: i for i, c in enumerate(cells)}
    lat = [50 + c[1] / 100 for c in cells]
    lon = [c[0] / 100 for c in cells]
    frame = tmp_path / "frame.csv"
    with frame.open("w", newline="", encoding="utf-8") as fh:
        out = csv.writer(fh)
        out.writerow(["region", "lat", "lon", "households"])
        for region, c in committed:
            out.writerow([region, f"{lat[index[c]]:.4f}", f"{lon[index[c]]:.4f}", "10.000"])
    monkeypatch.setattr(f, "FRAME_CSV", frame)
    monkeypatch.setattr(f, "ARTEFACT_DIR", tmp_path)
    monkeypatch.setattr(f, "OUTPUT_AREA_CSV", tmp_path / "oa.csv.gz")
    monkeypatch.setattr(f, "region_namer", lambda: None)
    monkeypatch.setattr(f, "_cell_coordinates", lambda: (index, lat, lon))
    monkeypatch.setattr(wcw, "census_weights",
                        lambda group_of=None, per_output_area=False: (placed, {}))
    return f.build_output_areas(progress=lambda *_: None)


def test_a_committed_cell_takes_its_own_areas_first_and_the_nearest_ring_only_when_it_has_none(
        monkeypatch, tmp_path):
    """DEFECT: a cell with no address of its region given no area (every home sited there would draw
    nationally), or a cell WITH its own areas diluted by its neighbours'. Both branches must be
    taken, then each checked. No committed cell needs the ring today; 2,944 did while the frame
    predated the address placement, and the ring is what a frame that drifts again falls back on."""
    import gzip

    summary = _oa_build(monkeypatch, tmp_path,
                        committed=[("East", (10, 10)), ("East", (20, 20))],
                        placed={"East": {(10, 10): {"E_OWN": 5.0},
                                         (11, 10): {"E_NEIGHBOUR": 7.0},
                                         (21, 21): {"E_RING": 3.0}},
                                "London": {(20, 20): {"E_OTHER_REGION": 9.0}}})
    assert summary["cells_by_ring"] == {"0": 1, "1": 1}
    with gzip.open(tmp_path / "oa.csv.gz", "rt", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    by_cell: dict[str, set] = {}
    for r in rows:
        by_cell.setdefault(r["lat"], set()).add(r["output_area"])
    assert by_cell["50.1000"] == {"E_OWN"}, "a cell's own areas were diluted by a neighbour's"
    assert by_cell["50.2000"] == {"E_RING"}, "the ring crossed into another region"


def test_a_committed_cell_with_no_area_of_its_region_nearby_refuses_the_build(
        monkeypatch, tmp_path):
    """DEFECT: borrowing areas from ever further away once the committed frame has drifted from the
    placement. Past `MAX_OUTPUT_AREA_RING` the build refuses and names the rebuild."""
    far = f.MAX_OUTPUT_AREA_RING + 1
    with pytest.raises(ValueError, match="rebuild it"):
        _oa_build(monkeypatch, tmp_path, committed=[("East", (10, 10))],
                  placed={"East": {(10 + far, 10): {"E_FAR": 1.0}}})


def test_the_committed_frame_was_built_by_the_placement_the_weather_cells_were_cut_over():
    """DEFECT: the frame outliving its placement. It was built on the window placement and kept for
    three weeks after `census_weights` moved to ONSUD, so 111 of its cells were not occupied land
    cells of the weather partition, their households were refused a weather cell, and 2,944 cells
    borrowed their output areas from a neighbour. Built by the same placement, the frame's
    coordinates ARE the occupied land cells, and a frame or a partition rebuilt without the other
    breaks that equality."""
    from simulation import weather_cell_siting as wcs

    _, land_cells = wcs.load_land_cells()
    with f.FRAME_CSV.open(encoding="utf-8") as fh:
        frame = {f"{r['lat']},{r['lon']}" for r in csv.DictReader(fh)}
    assert frame - set(land_cells) == set(), (
        f"{len(frame - set(land_cells)):,} frame cells are not occupied land cells -- the frame "
        "and the weather partition were built by different placements; rebuild with `--build` "
        "then `--build-output-areas`")
    assert set(land_cells) - frame == set(), (
        f"{len(set(land_cells) - frame):,} occupied land cells hold no household in the frame")
