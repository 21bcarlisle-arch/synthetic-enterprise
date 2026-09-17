#!/usr/bin/env python3
"""R15 proof that the weather store's writer and its resume-reader are exact inverses.

THE DEFECT THEY NAME (2026-09-16). `sim/weather_world/` held 156 cells x 3,653 days and no
committed code could rebuild it, in three separate ways that all presented as "the tool works":

  1. `build()` NEVER CALLED `extract_temperature`. The HadUK 1 km extractor was defined, correct,
     and dead -- `build` took every column from the ERA5 archive, while `cells.json` on disk named
     HadUK as the temperature source. Nothing could see the disagreement because nothing compared
     them.
  2. `_write()` EMITTED NO `level_c`, NO `decomposition` AND NO `regimes.json`, though all three
     were on disk. The store is per-cell LEVEL + per-regime ANOMALY and the writer knew nothing
     about the decomposition, so a rebuild would have written raw series under a reader that adds
     a level back -- every temperature in the store wrong by its cell's climatology, about eleven
     degrees, and every value still perfectly plausible.
  3. THE ONE NEITHER NOTE SAW: `daily.csv.gz` is keyed by REGIME (`R00`...) and `_existing_rows`
     read that key as a CELL id. So all 156 held cells read as missing, a resume re-pulled every
     one of them over the network, and the rewritten file would have carried regime ids and cell
     ids in the same column.

Each defect is silent under the obvious test -- "does the tool run without error" is green for all
three. What catches them is asking whether the writer and the reader agree, so that is what these
assert.

BOTH SIDES IN EVERY FIXTURE. The synthetic store below is built so the regime id and the cell id
are never the same string, and so one cell carries the ERA5 columns while another carries
temperature only. A fixture whose keys coincided would pass with defect 3 fully in place, and a
fixture where every cell looked alike could not tell a coverage question from a row-count one.
"""
from __future__ import annotations

import csv
import gzip
import json

import pytest

from tools import build_weather_world as bw

#: Two cells, and the ids are deliberately far apart in the sorted order so the regime each gets
#: (`R00`, `R01`) is never mistakable for the cell id that earned it.
ALPHA = "E100N0200"
BETA = "E300N0400"

#: ALPHA's series is warm and BETA's is cold, so a level swapped between them is visible rather
#: than absorbed. The means are 10.0 and 2.0 exactly, which makes `level_c` checkable by hand.
ALPHA_MEANS = (9.0, 10.0, 11.0)
BETA_MEANS = (1.0, 2.0, 3.0)
DATES = ("2016-01-01", "2016-01-02", "2016-01-03")


def _cells() -> dict[str, dict]:
    return {
        ALPHA: {"cell_id": ALPHA, "east_km": 100, "north_km": 200,
                "latitude": 51.5, "longitude": -0.1},
        BETA: {"cell_id": BETA, "east_km": 300, "north_km": 400,
               "latitude": 53.5, "longitude": -2.2},
    }


def _raw_rows() -> dict[str, list[dict]]:
    """RAW rows, the terms `_write` consumes and `_existing_rows` must hand back.

    ALPHA carries the ERA5 columns; BETA carries temperature only. That asymmetry is the live
    one -- 18 of the store's 156 cells are temperature-only -- and it is what stops a coverage
    control from passing vacuously.
    """
    rows: dict[str, list[dict]] = {ALPHA: [], BETA: []}
    for date, alpha, beta in zip(DATES, ALPHA_MEANS, BETA_MEANS):
        rows[ALPHA].append({
            "cell_id": ALPHA, "date": date,
            "temperature_min_c": alpha - 2, "temperature_mean_c": alpha,
            "temperature_max_c": alpha + 2,
            "wind_speed_mean_ms": 5.0, "cloud_cover_pct": 80.0, "precipitation_mm": 1.0})
        rows[BETA].append({
            "cell_id": BETA, "date": date,
            "temperature_min_c": beta - 2, "temperature_mean_c": beta,
            "temperature_max_c": beta + 2,
            "wind_speed_mean_ms": "", "cloud_cover_pct": "", "precipitation_mm": ""})
    return rows


@pytest.fixture
def store(tmp_path, monkeypatch):
    """Point both modules at an empty directory. The real store is never read or written here."""
    for attr, name in (("STORE_DIR", None), ("CELLS_PATH", "cells.json"),
                       ("SERIES_PATH", "daily.csv.gz"), ("REGIMES_PATH", "regimes.json")):
        monkeypatch.setattr(bw, attr, tmp_path if name is None else tmp_path / name)
    return tmp_path


def test_the_writer_emits_the_three_artefacts_the_reader_expects(store):
    """Defect 2: a writer that emits no level, no decomposition and no regime map."""
    bw._write(_cells(), _raw_rows())

    cells = json.loads((store / "cells.json").read_text())
    assert "HadUK" in cells["source"] and "ERA5" in cells["source"], (
        "cells.json must name BOTH sources: temperature is HadUK and the other three are ERA5, "
        "and a single-source line is how the two docstrings came to disagree with the artefact")
    assert "decomposition" in cells
    # The level is the cell's OWN mean, and the two cells' means differ by 8 C -- so a level
    # computed over the wrong cell, or over the pooled series, cannot pass this.
    assert cells["cells"][ALPHA]["level_c"] == pytest.approx(10.0)
    assert cells["cells"][BETA]["level_c"] == pytest.approx(2.0)

    regimes = json.loads((store / "regimes.json").read_text())
    assert regimes["k"] == 2
    assert regimes["regime_of_cell"] == {ALPHA: "R00", BETA: "R01"}


def test_the_series_is_keyed_by_regime_and_holds_the_anomaly(store):
    """Defect 3's other half: prove the on-disk key is NOT the cell id.

    Asserted before the round-trip below, because if the two keyings coincided the round-trip
    would pass with the defect in place.
    """
    bw._write(_cells(), _raw_rows())
    with gzip.open(store / "daily.csv.gz", "rt") as handle:
        rows = list(csv.DictReader(handle))

    keys = {r["cell_id"] for r in rows}
    assert keys == {"R00", "R01"}, "the series must be keyed by regime, not by cell"
    assert not keys & {ALPHA, BETA}, "no cell id may appear in the series' key column"

    # ALPHA's mean is its level, so its stored anomaly is zero on the middle day -- and 10.0 would
    # be the value a writer that skipped the decomposition wrote.
    middle = next(r for r in rows if r["cell_id"] == "R00" and r["date"] == DATES[1])
    assert float(middle["temperature_mean_c"]) == pytest.approx(0.0)
    assert float(middle["wind_speed_mean_ms"]) == pytest.approx(5.0), (
        "wind is stored RAW -- it has no level to remove and a 'wind anomaly' is a quantity "
        "nobody asked for")


def test_the_reader_hands_back_exactly_what_the_writer_was_given(store):
    """Defect 3: every held cell read as missing, so a resume re-pulled all of them."""
    written = _raw_rows()
    bw._write(_cells(), written)

    read_back, have = bw._existing_rows()
    assert have == {ALPHA, BETA}, (
        "the resume-reader must return CELL ids; returning the regime ids it finds in the file "
        "is what made 156 held cells look missing")

    for cell in (ALPHA, BETA):
        got = {r["date"]: r for r in read_back[cell]}
        for original in written[cell]:
            row = got[original["date"]]
            for field in bw.FIELDS:
                if original[field] == "":
                    assert row[field] == "", f"{cell} {field} must stay empty, not become 0"
                else:
                    assert float(row[field]) == pytest.approx(float(original[field])), (
                        f"{cell} {original['date']} {field} did not survive the round trip")


def test_the_reader_refuses_a_store_whose_files_disagree(store):
    """A refusal that names its reason -- and a control that proves the door opens first.

    The first half asserts the good store passes. Without it a reader that refused EVERY store
    would satisfy the second half perfectly.
    """
    bw._write(_cells(), _raw_rows())
    bw._existing_rows()          # the door is open: a consistent store does not refuse

    regimes = json.loads((store / "regimes.json").read_text())
    del regimes["regime_of_cell"][BETA]
    regimes["k"] = 1
    (store / "regimes.json").write_text(json.dumps(regimes))

    with pytest.raises(bw.WeatherWorldRefusal) as refusal:
        bw._existing_rows()
    assert "R01" in str(refusal.value), "the refusal must name the key it could not place"


def test_a_cell_that_has_left_the_book_keeps_its_rows_and_its_centre(store):
    """The book moved by 72 cells between 09-09 and 09-16, so this is not hypothetical.

    `_write` is handed the cells the book occupies TODAY. If it wrote only those, every cell the
    book had dropped would lose a real network pull and -- worse -- its centre, which is recorded
    nowhere else once `book_cells` stops returning it.
    """
    bw._write(_cells(), _raw_rows())

    todays_book = {ALPHA: _cells()[ALPHA]}          # BETA has left
    rows, _ = bw._existing_rows()
    result = bw._write(todays_book, rows)

    assert result["cells"] == 2, "a departed cell must be kept, not dropped"
    cells = json.loads((store / "cells.json").read_text())["cells"]
    assert BETA in cells and cells[BETA]["latitude"] == pytest.approx(53.5), (
        "the departed cell's centre survives only in the store; losing it makes the cell "
        "unrebuildable")


def test_a_temperature_only_cell_is_not_mistaken_for_a_finished_one(store):
    """Defect 1's trap: the temperature pass runs FIRST, so 'has any rows' means 'has temperature'.

    Under the old question -- is this cell in the store at all -- every cell would read as done
    the moment the HadUK pass created its rows, and the archive pull would never run again.
    """
    rows = _raw_rows()
    assert bw._has_era5(rows[ALPHA]) is True
    assert bw._has_era5(rows[BETA]) is False, (
        "a cell with temperature and no wind/cloud/precip still needs the archive pull")


def test_build_takes_temperature_from_haduk_and_never_from_the_archive(store, monkeypatch):
    """Defect 1: `extract_temperature` was dead code and `build` filled temperature from ERA5.

    THE TWO FAKES DISAGREE ON PURPOSE. Each returns a temperature the other never returns, so the
    finished store says which source it came from. Fakes that agreed would make this test green
    whichever branch ran -- which is exactly how the live defect survived.
    """
    import sim.weather_ingestor as ingestor

    HADUK_T, ERA5_T = 7.5, -99.0

    monkeypatch.setattr(bw, "book_cells", _cells)
    monkeypatch.setattr(bw, "extract_temperature", lambda cells, progress=print: {
        cell: {d: {f: HADUK_T for f in bw.LEVELLED} for d in DATES} for cell in cells})
    monkeypatch.setattr(ingestor, "get_daily_weather", lambda key, lat, lon, start, end: [
        {"date": d, "temperature_min_c": ERA5_T, "temperature_mean_c": ERA5_T,
         "temperature_max_c": ERA5_T, "wind_speed_mean_ms": 4.0, "cloud_cover_pct": 50.0,
         "precipitation_mm": 0.2} for d in DATES])

    result = bw.build(pause=0.0, progress=lambda *a: None)
    assert result["refused"] == []

    with gzip.open(store / "daily.csv.gz", "rt") as handle:
        rows = list(csv.DictReader(handle))
    levels = json.loads((store / "cells.json").read_text())["cells"]

    # Every temperature is HadUK's, recovered by adding the level back exactly as the reader does.
    for row in rows:
        cell = next(c for c, r in
                    json.loads((store / "regimes.json").read_text())["regime_of_cell"].items()
                    if r == row["cell_id"])
        raw = float(row["temperature_mean_c"]) + levels[cell]["level_c"]
        assert raw == pytest.approx(HADUK_T), (
            "temperature must come from the HadUK grids; this value came from the ERA5 archive")
        # ...and the archive's OWN three columns did land, so the fake was genuinely reached.
        assert float(row["wind_speed_mean_ms"]) == pytest.approx(4.0)
