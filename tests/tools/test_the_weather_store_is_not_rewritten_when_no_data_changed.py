#!/usr/bin/env python3
"""R15 proof that a weather build which changed no data leaves the series FILE alone.

THE DEFECT THEY NAME, measured 2026-09-17 against a live exhausted Open-Meteo quota. `build`
calls `_write` unconditionally after the fetch loop, so a run that pulled ZERO cells still
rewrote all 11 MB of `sim/weather_world/daily.csv.gz`. gzip stamps the wall clock into its
header, so the rewrite produced:

  * decompressed md5 `6f5e8dd49e1b1a7ea2002143885990ed` -- identical, no data changed;
  * a different file, and `git status` reporting ` M sim/weather_world/daily.csv.gz`.

That is the worst available shape rather than a cosmetic one. The next step in this lane is a
pathspec commit of exactly this path, so a quota refusal handed the committer an 11 MB diff
carrying no data, and NOTHING in the diff distinguishes it from a real pull. The run's own
summary said `refused 0` and `cells held 221/221`, which reads as success.

WHY THE CONTROL IS KEYED TO THE CONTENT AND NOT TO "DID WE FETCH". A `completed == 0` guard
passes this file's first leg and still rewrites in the two other cases that reach the same
no-op: a book already complete (`todo` empty), and a re-pull returning what the store held.

BOTH LEGS, OVER THE PARTITION. A `_write` that never wrote anything at all passes every
unchanged-leg assertion here while silently discarding real pulls -- the fail-closed mirror of
the defect, and the more expensive of the two. So the rewrite branch is asserted to be REACHABLE
in the same test as the skip branch, not in a separate one a future narrowing could leave green.
"""
from __future__ import annotations

import gzip
import os

import pytest

from tools import build_weather_world as bw

CELL_IDS = ("E100N0200", "E300N0400")
DATES = ("2016-01-01", "2016-01-02")

#: An mtime no write can coincidentally reproduce. The gzip header carries whole SECONDS and the
#: filesystem's own mtime is what is asserted on, so "the file was not touched" has to be proved
#: by a stamp the test chose rather than by comparing two wall clocks a fast test may share.
UNTOUCHED_NS = 0


def _rows(cell: str, wind: float | str) -> list[dict]:
    return [{"cell_id": cell, "date": d, "temperature_min_c": 1.0, "temperature_mean_c": 2.0,
             "temperature_max_c": 3.0, "wind_speed_mean_ms": wind,
             "cloud_cover_pct": 70.0 if wind != "" else "",
             "precipitation_mm": 2.5 if wind != "" else ""} for d in DATES]


def _cells() -> dict[str, dict]:
    return {
        cid: {"cell_id": cid, "east_km": 100 * (i + 1), "north_km": 200 * (i + 1),
              "latitude": 51.5 + i, "longitude": -0.1 - i}
        for i, cid in enumerate(CELL_IDS)
    }


@pytest.fixture
def store(tmp_path, monkeypatch):
    """A store of its own. The real `sim/weather_world/` is never read or written here."""
    for attr, name in (("STORE_DIR", None), ("CELLS_PATH", "cells.json"),
                       ("SERIES_PATH", "daily.csv.gz"), ("REGIMES_PATH", "regimes.json")):
        monkeypatch.setattr(bw, attr, tmp_path if name is None else tmp_path / name)
    monkeypatch.setattr(bw.time, "sleep", lambda _s: None)
    return tmp_path


def test_an_identical_write_leaves_the_file_untouched_and_a_changed_one_rewrites_it(store):
    """The skip and the rewrite, in one test, because either alone is passed by a broken writer."""
    cells = _cells()
    rows = {CELL_IDS[0]: _rows(CELL_IDS[0], 4.2)}
    first = bw._write(cells, rows)
    assert first["series_rewritten"], "the first write creates the file and must report doing so"

    before = bw.SERIES_PATH.read_bytes()
    os.utime(bw.SERIES_PATH, ns=(UNTOUCHED_NS, UNTOUCHED_NS))

    # THE SKIP LEG. Same cells, same rows -- the no-op the quota refusal performs 11 MB at a time.
    again = bw._write(cells, rows)
    assert again["series_rewritten"] is False, (
        "a write of identical data must report that it did not rewrite: this boolean is what "
        "the build's summary line reads to tell a committer a quota refusal from a real pull")
    assert os.stat(bw.SERIES_PATH).st_mtime_ns == UNTOUCHED_NS, (
        "the file was WRITTEN. Its data is unchanged and gzip's header carries the wall clock, "
        "so this rewrite is invisible to a decompressed comparison and shows up as an 11 MB "
        "modification in `git status` -- indistinguishable from a real pull in the diff")
    assert bw.SERIES_PATH.read_bytes() == before

    # THE REWRITE LEG, against the same file in the same state. Without it, a `_write` whose body
    # is `return` passes everything above -- and that failure loses real archive pulls, which cost
    # a day of quota each, rather than merely dirtying the tree.
    changed = bw._write(cells, {CELL_IDS[0]: _rows(CELL_IDS[0], 9.9)})
    assert changed["series_rewritten"], "new data must still reach the file"
    assert os.stat(bw.SERIES_PATH).st_mtime_ns != UNTOUCHED_NS
    with gzip.open(bw.SERIES_PATH, "rt", newline="") as handle:
        assert "9.9" in handle.read(), (
            "the changed value is not in the file: the skip branch swallowed a real pull")


def test_a_build_that_fetched_nothing_does_not_dirty_the_series_file(store, monkeypatch):
    """The defect at the level it was actually observed: `build`, not `_write`.

    `_write` alone could be correct while `build` reached it by a path that always differs -- so
    this drives the whole function the way the live run did, with every cell already complete, and
    asserts on the file rather than on the return value.
    """
    monkeypatch.setattr(bw, "book_cells", _cells)
    monkeypatch.setattr(bw, "extract_temperature", lambda cells, progress=print: {})

    complete = {cid: _rows(cid, 4.2) for cid in CELL_IDS}
    bw._write(_cells(), complete)
    os.utime(bw.SERIES_PATH, ns=(UNTOUCHED_NS, UNTOUCHED_NS))

    fetched = []

    def fetch(key, lat, lon, start, end):
        fetched.append(key)
        raise AssertionError("no cell needs the archive; this must not be reached")

    monkeypatch.setattr("sim.weather_ingestor.get_daily_weather", fetch)
    result = bw.build(pause=0.0, progress=lambda *_: None, temperature=False)

    assert fetched == [], "the store is already complete, so there is nothing to pull"
    assert result["series_rewritten"] is False
    assert os.stat(bw.SERIES_PATH).st_mtime_ns == UNTOUCHED_NS, (
        "a build with an empty `todo` rewrote the series file anyway -- the same no-op that a "
        "quota-exhausted run performs, and the reason `git status` cannot be trusted to say "
        "whether a weather build actually brought anything back")
