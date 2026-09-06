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


def test_the_NAMER_DROPS_SCOTLAND_rather_than_folding_it_into_a_region(monkeypatch, tmp_path):
    """DEFECT: an output area outside the curriculum's ten regions being given the nearest name.
    Scotland is 8% of GB households and it is the cold, windy 8% -- folded into the North East it
    would move that region's weather and leave the national total looking right."""
    path = tmp_path / "oa.csv"
    with path.open("w", newline="", encoding="utf-8") as fh:
        out = csv.writer(fh)
        out.writerow(["oa", "region_code"])
        out.writerows([["E00000001", "E12000007"], ["W00000001", "W92000004"]])
    namer = f.region_namer(path)
    assert namer("E00000001") == "London"
    assert namer("W00000001") == "Wales"
    assert namer("S00000001") is None, "a Scottish output area was given an English region"


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
