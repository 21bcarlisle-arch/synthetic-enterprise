#!/usr/bin/env python3
"""R15 proof that a daily-quota 429 stops the ERA5 pull rather than being backed off per cell.

THE DEFECT THEY NAME, measured 2026-09-17 by running the resume and watching it do nothing.
Open-Meteo enforces at least two limits behind ONE status code, and only its own `reason` string
separates them:

  * a BURST limit, which `PAUSE_SECONDS = 20.0` was measured against and which waiting clears;
  * a DAILY QUOTA -- "Daily API request limit exceeded. Please try again tomorrow." -- which
    nothing clears before the reset.

`_fetch_with_backoff` asked `"429" not in str(exc)`, so it treated them identically: four attempts
at 60/120/180 s, six minutes of sleeping PER CELL, against a limit six minutes cannot reach. The
observed run sat in `hrtimer_nanosleep` for eleven minutes having used 11 s of CPU, wrote nothing,
and its own log said nothing because `print` block-buffers to a file. Left alone, the 23-cell
resume would have spent about two and a quarter hours and reported 23 separate refusals whose
single shared cause appeared nowhere in the summary.

WHY THE STOP AND NOT JUST THE NON-RETRY. Skipping the backoff alone would still walk all 23 cells,
turning one legible "come back tomorrow" into a list only an exhaustive reader could diagnose. The
quota is a property of the DAY, so the first cell to hit it has already answered for every cell
behind it.

THE FIXTURES CARRY BOTH SIDES. Every leg that asserts the quota path is paired with the burst path
through the same code, because a version that stopped on EVERY 429 -- the fail-closed mirror of the
defect -- passes any quota-only test and would wedge the pull on a transient limit.
"""
from __future__ import annotations

import json

import pytest

from sim.weather_ingestor import WeatherArchiveRefusal, WeatherQuotaExhausted
from tools import build_weather_world as bw

QUOTA = "Open-Meteo refused the archive for 'X' (1, 2) a..b: HTTP 429 — Daily API request limit exceeded. Please try again tomorrow."  # noqa: E501
BURST = "Open-Meteo refused the archive for 'X' (1, 2) a..b: HTTP 429 — Minutely API request limit exceeded."  # noqa: E501

#: Three cells, so "stopped at the second" is distinguishable from "stopped at the last" -- with
#: two, a loop that ran to the end and one that broke early leave the same store behind.
CELL_IDS = ("E100N0200", "E300N0400", "E500N0600")
DATES = ("2016-01-01", "2016-01-02")


def _cells() -> dict[str, dict]:
    return {
        cid: {"cell_id": cid, "east_km": 100 * (i + 1), "north_km": 200 * (i + 1),
              "latitude": 51.5 + i, "longitude": -0.1 - i}
        for i, cid in enumerate(CELL_IDS)
    }


def _records(cell: str) -> list[dict]:
    """What a successful archive pull hands back. Only the ERA5 columns are read by `build`."""
    return [{"date": d, "location_id": cell, "temperature_max_c": 12.0,
             "temperature_min_c": 6.0, "temperature_mean_c": 9.0,
             "wind_speed_mean_ms": 4.2, "cloud_cover_pct": 70.0,
             "precipitation_mm": 2.5} for d in DATES]


@pytest.fixture
def store(tmp_path, monkeypatch):
    """An empty store, and no clock. The real store is never read or written here.

    `time.sleep` is neutered so the BURST legs below assert the retry COUNT without paying the
    360 s the real backoff costs -- the count is the property, the wall-clock is not.
    """
    for attr, name in (("STORE_DIR", None), ("CELLS_PATH", "cells.json"),
                       ("SERIES_PATH", "daily.csv.gz"), ("REGIMES_PATH", "regimes.json")):
        monkeypatch.setattr(bw, attr, tmp_path if name is None else tmp_path / name)
    monkeypatch.setattr(bw.time, "sleep", lambda _s: None)
    return tmp_path


def test_a_quota_is_tried_once_and_a_burst_limit_is_tried_four_times(store):
    """The retry decision itself, at the smallest surface that holds it.

    BOTH LEGS IN ONE TEST. `_fetch_with_backoff` retrying nothing passes a quota-only assertion,
    and retrying everything passes a burst-only one. The pair is what makes the branch provable.
    """
    attempts = []

    def quota_fetch(*args):
        attempts.append(args[0])
        raise WeatherQuotaExhausted(QUOTA)

    with pytest.raises(WeatherQuotaExhausted):
        bw._fetch_with_backoff(quota_fetch, "C", 1.0, 2.0, "a", "b", lambda *_: None)
    assert len(attempts) == 1, (
        "the daily quota must cost exactly ONE request: the reset is tomorrow and "
        f"{bw.RETRY_ATTEMPTS} backoffs totalling "
        f"{sum(bw.RETRY_BACKOFF_SECONDS * a for a in range(1, bw.RETRY_ATTEMPTS)):.0f}s "
        "cannot reach it")

    burst = []

    def burst_fetch(*args):
        burst.append(args[0])
        raise WeatherArchiveRefusal(BURST)

    with pytest.raises(WeatherArchiveRefusal):
        bw._fetch_with_backoff(burst_fetch, "C", 1.0, 2.0, "a", "b", lambda *_: None)
    assert len(burst) == bw.RETRY_ATTEMPTS, (
        "a burst 429 must still be retried -- a fix that stops on every 429 wedges the pull "
        "on a limit that twenty seconds clears")


def test_the_quota_stops_the_run_and_keeps_the_cells_already_fetched(store, monkeypatch):
    """The loop-level half: one legible stop, not N refusals, and no lost work.

    The first cell succeeds and the second hits the quota, so this separates three behaviours a
    quota-only assertion cannot: continuing to cell three, discarding cell one, and filing the
    quota as an ordinary per-cell refusal.
    """
    monkeypatch.setattr(bw, "book_cells", _cells)
    monkeypatch.setattr(bw, "extract_temperature", lambda cells, progress=print: {})

    seen = []

    def fetch(key, lat, lon, start, end):
        seen.append(key)
        if len(seen) == 1:
            return _records(key)
        raise WeatherQuotaExhausted(QUOTA)

    monkeypatch.setattr("sim.weather_ingestor.get_daily_weather", fetch)
    result = bw.build(pause=0.0, progress=lambda *_: None, temperature=False)

    assert seen == [CELL_IDS[0], CELL_IDS[1]], (
        "the run must stop AT the quota, not walk the rest of the book asking a question whose "
        f"answer it already has -- attempted {seen}")
    assert result["quota_exhausted"] and "tomorrow" in result["quota_exhausted"].lower()
    assert result["refused"] == [], (
        "the quota is not a per-cell refusal: filing it as one is what buries the single shared "
        "cause in a list")

    # The cell that DID come back is on disk. `_write` fires after every success, and a stop that
    # discarded it would make the whole pull worthless rather than partial.
    read_back, have = bw._existing_rows()
    assert CELL_IDS[0] in have and bw._has_era5(read_back[CELL_IDS[0]])
    assert not bw._has_era5(read_back.get(CELL_IDS[1], [])), (
        "the cell that hit the quota must hold no ERA5 columns, so the next run retries it")


def test_a_burst_limit_does_not_stop_the_run(store, monkeypatch):
    """The mirror, and the reason the fix is not simply "break on 429".

    Without this leg, a `build` that stopped on any refusal at all passes every assertion above
    while quietly turning one transient limit into a two-thirds-empty store.
    """
    monkeypatch.setattr(bw, "book_cells", _cells)
    monkeypatch.setattr(bw, "extract_temperature", lambda cells, progress=print: {})

    seen = []

    def fetch(key, lat, lon, start, end):
        seen.append(key)
        if key == CELL_IDS[1]:
            raise WeatherArchiveRefusal(BURST)
        return _records(key)

    monkeypatch.setattr("sim.weather_ingestor.get_daily_weather", fetch)
    result = bw.build(pause=0.0, progress=lambda *_: None, temperature=False)

    # Cell two is attempted RETRY_ATTEMPTS times and the run carries on to cell three.
    assert seen.count(CELL_IDS[2]) == 1, "a burst limit on one cell must not abandon the rest"
    assert result["quota_exhausted"] is None
    assert [r["cell_id"] for r in result["refused"]] == [CELL_IDS[1]]

    _, have = bw._existing_rows()
    assert have == {CELL_IDS[0], CELL_IDS[2]}


def test_incomplete_cells_outside_the_book_are_named_rather_than_scored_as_a_failed_pull(
        store, monkeypatch):
    """The counting defect the drawn item itself carried, 2026-09-17.

    The item said "the 31 of 221 cells that still hold temperature only", and reads as though a
    clean `--build` reaches 221/221. It cannot: `todo` is drawn from `book_cells()`, and 8 of
    those 31 are cells the book no longer occupies, which `_write` keeps on purpose and this loop
    never fetches. A run that succeeds at everything it attempts still leaves them incomplete, so
    the ceiling has to be on the surface or a perfect run reads as 8 short.
    """
    monkeypatch.setattr(bw, "book_cells", lambda: {CELL_IDS[0]: _cells()[CELL_IDS[0]]})
    monkeypatch.setattr(bw, "extract_temperature", lambda cells, progress=print: {})
    monkeypatch.setattr("sim.weather_ingestor.get_daily_weather",
                        lambda key, lat, lon, start, end: _records(key))

    # A departed cell, temperature-only: in the store, not in the book.
    departed = CELL_IDS[2]
    bw._write(_cells(), {departed: [{"cell_id": departed, "date": d, "temperature_min_c": 1.0,
                                     "temperature_mean_c": 2.0, "temperature_max_c": 3.0,
                                     "wind_speed_mean_ms": "", "cloud_cover_pct": "",
                                     "precipitation_mm": ""} for d in DATES]})

    lines = []
    result = bw.build(pause=0.0, progress=lines.append, temperature=False)

    assert result["unreachable"] == [departed], (
        "an incomplete cell outside the book is unreachable by this pass and must be reported "
        "as such, not left to look like a cell the pull failed on")
    assert any(departed in line and "not in the book" in line.lower() for line in lines), (
        "and it must be NAMED on the progress surface, not merely counted -- a bare count is "
        "what makes the next reader re-derive which cells they are")

    # The store still holds it. Reporting it must not become a reason to drop it: its centre is
    # recorded nowhere else.
    assert departed in json.loads((store / "cells.json").read_text())["cells"]
