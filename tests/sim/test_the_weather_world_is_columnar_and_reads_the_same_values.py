"""Controls for the COLUMNAR weather world (`sim.weather_world.DailyColumns`, `load_columns`).

THE CHANGE (director, 2026-10-09: "the weather world is now the biggest memory holder"). The store
was `{regime: {date: {field: float}}}` -- 1.25 million row dicts, ~540 bytes a row, ~674 MB
resident. It is now one `array('d')` per regime per field over ONE shared date index, ~60 MB, and
every accessor returns what it returned before.

THE DEFECTS THESE NAME. A representation change is safe only if no value read through it moves, so
the old reader (`load_daily`, kept) is the oracle and the new one is compared to it value by value,
by `float.hex`, NaN by NaN, key order included -- over a hostile fixture (out-of-order dates, a
repeated date, empty and absent columns, two regimes on different days) AND over a sample of the
real store. The memory claim is controlled too, keyed to the property (bytes per stored value), so
a quiet return to row dicts reds here rather than in the next run's RSS.
"""
from __future__ import annotations

import csv
import gzip
import math
import sys

import pytest

from sim import weather_world as ww

_HEADER = ["cell_id", "date", "temperature_min_c", "temperature_max_c", "temperature_mean_c",
           "wind_speed_mean_ms", "cloud_cover_pct", "precipitation_mm"]

#: Hostile on purpose: R1's rows are OUT OF ORDER and 2016-01-02 appears TWICE (the later row must
#: win, as `load_daily`'s dict assignment made it); R1 has an empty wind and cloud; R2 is on
#: different days from R1, so the two regimes cannot share an index.
_ROWS = [
    ["R1", "2016-01-03", "1.5", "7.25", "4.125", "", "", "0.0"],
    ["R1", "2016-01-01", "-2.0", "3.0", "0.5", "5.5", "80.0", "1.2"],
    ["R1", "2016-01-02", "0.1", "0.2", "0.3", "0.4", "0.5", "0.6"],
    ["R1", "2016-01-02", "-0.1", "6.0", "2.95", "4.0", "100.0", "3.3"],
    ["R2", "2016-01-02", "3.0", "9.0", "6.0", "2.0", "40.0", "0.0"],
    ["R2", "2016-01-04", "2.5", "8.5", "5.5", "1.5", "0.0", "0.2"],
]


def _write(path, rows, header=_HEADER):
    with gzip.open(path, "wt", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)
    return path


def _cells():
    return {
        "C1": ww.Cell("C1", 100, 200, 51.5, -0.1, level_c=9.875),
        "C2": ww.Cell("C2", 300, 400, 53.5, -2.2, level_c=-0.55),
    }


def _same_row(a: dict, b: dict) -> bool:
    if list(a) != list(b):
        return False
    for key in a:
        x, y = a[key], b[key]
        if type(x) is not type(y):
            return False
        if isinstance(x, float):
            if math.isnan(x) and math.isnan(y):
                continue
            if x.hex() != y.hex():
                return False
        elif x != y:
            return False
    return True


def _same_rows(a: list[dict], b: list[dict]) -> bool:
    return len(a) == len(b) and all(_same_row(x, y) for x, y in zip(a, b))


def _old_world(cells, daily_path, regimes):
    """The pre-columnar world, exactly: `load_daily`'s dicts, never converted."""
    world = ww.WeatherWorld(cells, {}, regimes)
    world.daily = ww.load_daily(daily_path)
    return world


_WINDOWS = ({}, {"start": "2016-01-02"}, {"end": "2016-01-02"},
            {"start": "2016-01-02", "end": "2016-01-03"}, {"start": "2016-01-05"})


def test_every_value_read_through_the_columnar_store_is_the_value_the_row_store_gave(tmp_path):
    """Defect: the columnar reader moves a value -- a repeated date resolved first-wins, an
    out-of-order file left unsorted, an empty column read as 0.0 instead of NaN, a window end
    taken exclusive, a cell's level not added back. Each changes a settled number silently.
    """
    path = _write(tmp_path / "daily.csv.gz", _ROWS)
    regimes = {"C1": "R1", "C2": "R2"}
    old = _old_world(_cells(), path, regimes)
    new = ww.WeatherWorld(_cells(), ww.load_columns(path), regimes)
    assert all(isinstance(s, ww.DailyColumns) for s in new.daily.values())
    for cell in ("C1", "C2"):
        for window in _WINDOWS:
            assert _same_rows(old.for_cell(cell, **window), new.for_cell(cell, **window)), \
                (cell, window)
    # The mapping view too: tests and tools index `world.daily[regime][date][field]` directly.
    for regime, series in old.daily.items():
        assert list(new.daily[regime]) == sorted(series)
        for date, row in series.items():
            assert _same_row(row, new.daily[regime][date])
    assert new.record_end() == old.record_end()
    # The hostile rows really are hostile: the repeated date resolved LAST-wins and the empty
    # column is NaN, read straight off the columnar view.
    assert new.daily["R1"]["2016-01-02"]["temperature_mean_c"] == 2.95
    assert math.isnan(new.daily["R1"]["2016-01-03"]["wind_speed_mean_ms"])


def test_an_absent_column_and_a_short_row_read_as_nan_as_the_row_store_read_them(tmp_path):
    """Defect: a store without a column (or a short line) loads as an error or as zeros, where
    `load_daily` gave NaN -- which `available()` reads as an incomplete cell."""
    header = [h for h in _HEADER if h != "precipitation_mm"]
    rows = [["R1", "2016-01-01", "1.0", "2.0", "1.5", "3.0", "50.0"],
            ["R1", "2016-01-02", "1.0", "2.0", "1.5"]]
    path = _write(tmp_path / "daily.csv.gz", rows, header)
    old = _old_world({}, path, {})
    new = ww.WeatherWorld({}, ww.load_columns(path), {})
    for window in _WINDOWS:
        assert _same_rows(old.for_cell("R1", **window), new.for_cell("R1", **window))


def test_a_series_that_is_not_exactly_columnar_is_kept_as_handed_and_both_shapes_read_alike():
    """Defect: a hand-built series with an int value or a ragged row is coerced (3 -> 3.0) or has a
    NaN invented for a field it never had. BOTH BRANCHES are asserted reachable in one world, so a
    converter that columnarised everything -- or nothing -- fails here."""
    exact = {"2016-01-01": {"temperature_mean_c": 1.25}, "2016-01-02": {"temperature_mean_c": 2.5}}
    ragged = {"2016-01-01": {"temperature_mean_c": 3}, "2016-01-02": {"cloud_cover_pct": 50.0}}
    world = ww.WeatherWorld({}, {"A": exact, "B": ragged}, {})
    assert isinstance(world.daily["A"], ww.DailyColumns)
    assert world.daily["B"] is ragged
    assert world.for_cell("A") == [{"date": "2016-01-01", "temperature_mean_c": 1.25},
                                   {"date": "2016-01-02", "temperature_mean_c": 2.5}]
    rows = world.for_cell("B")
    assert rows == [{"date": "2016-01-01", "temperature_mean_c": 3.0},
                    {"date": "2016-01-02", "cloud_cover_pct": 50.0}]
    assert "temperature_mean_c" not in rows[1]
    # Uniform keys, one int: the shape check passes, so only the TYPE check keeps it a dict, and
    # a non-temperature int must come back an int (the level rounding makes temperatures floats).
    whole = {"2016-01-01": {"cloud_cover_pct": 50}, "2016-01-02": {"cloud_cover_pct": 25.5}}
    world = ww.WeatherWorld({}, {"C": whole}, {})
    assert world.daily["C"] is whole
    assert type(world.for_cell("C")[0]["cloud_cover_pct"]) is int


def test_analogue_extension_of_a_columnar_world_equals_the_row_by_row_extension():
    """Defect: the columnar fast path gathers the wrong record day (or drops 29 February) for a
    forward day. The row-by-row path is the original algorithm; forcing it with one ragged regime
    must give the columnar regime identical forward weather, and the fast path must be TAKEN when
    every regime is columnar (else this compares the slow path with itself)."""
    days = [f"{y}-{m:02d}-{d:02d}" for y in (2016, 2017) for m in (1, 2, 12)
            for d in range(1, 32) if not (m == 2 and d > (29 if y == 2016 else 28))]
    series = {d: {"temperature_mean_c": float(i) / 8, "cloud_cover_pct": float(i % 7)}
              for i, d in enumerate(days)}
    other = {d: dict(r) for d, r in series.items()}
    fast = ww.WeatherWorld({}, {"R": series, "S": other}, {})
    slow = ww.WeatherWorld({}, {"R": series, "X": {"2016-01-01": {"t": 1}}}, {})
    assert isinstance(fast.daily["S"], ww.DailyColumns)
    f = fast.extended_by_analogue_years("2020-12-31", seed="w:7")
    s = slow.extended_by_analogue_years("2020-12-31", seed="w:7")
    assert f.analogue_years == s.analogue_years
    assert isinstance(f.daily["R"], ww.DailyColumns) and f.daily["R"].dates is f.daily["S"].dates
    assert _same_rows(f.for_cell("R"), s.for_cell("R"))
    assert any(r["date"] == "2020-02-29" for r in f.for_cell("R"))


@pytest.fixture(scope="module")
def real_world():
    if not ww.SERIES_PATH.is_file():
        pytest.skip("the committed weather store is absent")
    return ww.WeatherWorld.load()


def test_the_real_store_reads_the_same_values_as_the_file_says(real_world):
    """Defect: the real store, through `WeatherWorld.load`, gives a value the file does not hold.
    The reference is the file itself, streamed for a sample of cells by `load_daily`'s rules (empty
    -> NaN, then the cell's level added back and rounded) without loading the whole row store."""
    sample = sorted(real_world.cells)[::40]
    wanted = {real_world.regime_for(c): c for c in sample}
    reference: dict[str, dict[str, dict[str, float]]] = {}
    with gzip.open(ww.SERIES_PATH, "rt", newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["cell_id"] in wanted:
                reference.setdefault(row["cell_id"], {})[row["date"]] = {
                    f: float(row[f]) if row.get(f) not in ("", None) else float("nan")
                    for f in ww.FIELDS}
    assert set(reference) == set(wanted)
    for regime, cell in wanted.items():
        old = ww.WeatherWorld({cell: real_world.cells[cell]}, {}, {cell: regime})
        old.daily = {regime: reference[regime]}
        for window in ({}, {"start": "2019-02-27", "end": "2020-03-01"}):
            assert _same_rows(old.for_cell(cell, **window), real_world.for_cell(cell, **window))


def test_the_loaded_store_holds_a_value_in_about_its_eight_bytes(real_world):
    """Defect: the store goes back to (or never left) row dicts -- ~540 bytes a value-row, the
    ~674 MB the director named. Keyed to the PROPERTY: resident bytes per stored float, counted
    over the arrays, the index and the views, must stay near 8, whatever the store's size."""
    seen: set[int] = set()
    total = values = 0
    for series in real_world.daily.values():
        assert isinstance(series, ww.DailyColumns)
        for obj in (series, series.dates, series.index, series.cols, *series.cols.values(),
                    *series.dates):
            if id(obj) not in seen:
                seen.add(id(obj))
                total += sys.getsizeof(obj)
        values += sum(len(col) for col in series.cols.values())
    assert len({id(s.dates) for s in real_world.daily.values()}) == 1, \
        "every regime should share ONE date index"
    assert total / values < 10, f"{total / values:.1f} bytes per stored value"
