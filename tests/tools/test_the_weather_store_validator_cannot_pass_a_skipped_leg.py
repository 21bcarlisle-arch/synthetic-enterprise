#!/usr/bin/env python3
"""R15 proof that the weather store's validator fails closed and can actually refuse.

THE DEFECT IT NAMES (2026-09-16). `tools/validate_weather_world.py` was cited by name in two
module docstrings for eight days before it existed. A path in a prose comment is a reachability
edge, so the store's only claimed control was a file nothing could run -- and because nothing ran
it, nobody noticed that the store's writer and its bytes had different shapes.

A validator written to close that hole has two ways to be worthless, and both are the ordinary
outcome rather than the unlucky one:

  * IT PASSES WHAT IT DID NOT CHECK. Its most expensive leg re-derives temperature from HadUK
    grids that may not be on the machine at all. A leg that reports "absent cache" as a pass turns
    the whole module into a green light for a store nobody measured.
  * IT CANNOT REFUSE ANYTHING. Every leg here asks about an artefact that is, today, correct. A
    leg asserted only against the good store would be indistinguishable from `return True`, which
    is this project's most expensive recurring shape.

So each leg below is asked TWICE -- once of a consistent store, which must pass, and once of a
store broken in the single specific way that leg exists to catch, which must fail. The pair is the
control; neither half is one on its own.
"""
from __future__ import annotations

import csv
import gzip
import json

import pytest

from tools import build_weather_world as bw
from tools import validate_weather_world as vw

ALPHA = "E100N0200"
BETA = "E300N0400"
DATES = ("2016-01-01", "2016-01-02", "2016-01-03")


@pytest.fixture
def store(tmp_path, monkeypatch):
    """A consistent two-cell store, written by the real writer.

    Built by `build_weather_world._write` rather than hand-rolled, so the fixture cannot drift
    away from the shape the validator is supposed to be checking.
    """
    paths = {"CELLS_PATH": tmp_path / "cells.json",
             "SERIES_PATH": tmp_path / "daily.csv.gz",
             "REGIMES_PATH": tmp_path / "regimes.json"}
    for module in (bw, vw):
        for attr, path in paths.items():
            monkeypatch.setattr(module, attr, path, raising=False)
    monkeypatch.setattr(bw, "STORE_DIR", tmp_path)
    # The window the validator checks against, shortened to the fixture's three days.
    for module in (bw, vw):
        monkeypatch.setattr(module, "START_DATE", DATES[0], raising=False)
        monkeypatch.setattr(module, "END_DATE", DATES[-1], raising=False)

    cells = {ALPHA: {"cell_id": ALPHA, "east_km": 100, "north_km": 200,
                     "latitude": 51.5, "longitude": -0.1},
             BETA: {"cell_id": BETA, "east_km": 300, "north_km": 400,
                    "latitude": 53.5, "longitude": -2.2}}
    rows = {c: [{"cell_id": c, "date": d,
                 "temperature_min_c": t - 2, "temperature_mean_c": t,
                 "temperature_max_c": t + 2, "wind_speed_mean_ms": 5.0,
                 "cloud_cover_pct": 80.0, "precipitation_mm": 1.0}
                for d, t in zip(DATES, (9.0, 10.0, 11.0))]
            for c in (ALPHA, BETA)}
    bw._write(cells, rows)
    return tmp_path


def _legs(store):
    cells, regimes, series = vw.load_store()
    return cells, regimes, series


def test_a_leg_that_could_not_run_is_never_counted_as_a_pass(store, monkeypatch):
    """The fail-open this module exists to prevent.

    Both halves matter: the leg must be reported as COULD NOT RUN, and it must not be swept into
    the passed count. A validator that printed the skip honestly and still counted it green would
    satisfy only the first.
    """
    monkeypatch.setattr(vw, "HADUK_DAY", store / "no-such-cache")

    legs = vw.validate(temperature=True)
    haduk = next(leg for leg in legs if "HadUK" in leg.name)

    assert haduk.passed is None, "an absent grid cache must not read as a pass"
    assert haduk.mark == "COULD NOT RUN"
    assert "absent" in haduk.detail
    assert haduk not in [leg for leg in legs if leg.passed is True]


def test_a_leg_NOT_ASKED_FOR_is_never_counted_as_a_pass_either(store):
    """THE SECOND ROUTE TO A SKIP, and the one the flag actually takes (2026-09-17).

    A skipped leg arrives two ways and only the first was asked about:

      * the HadUK cache is absent, so `check_temperature_reproduces` returns `None` -- above;
      * `--no-temperature` was passed, so `validate` builds `Leg(..., None, "not asked for")`
        itself and the checker never runs at all -- HERE.

    The second is not the exotic one. The re-derive opens 360 monthly grids and takes minutes, so
    `--no-temperature` is the mode a gate or a cron reaches for, and under it the mutation
    `Leg(..., None, "not asked for")` -> `Leg(..., True, "not asked for")` survived every one of
    this file's controls: the store reported "5 passed, 0 failed, 0 could not run" with its most
    expensive leg never executed. The module's whole name is that this cannot happen.

    Asked of the PROPERTY -- a skip is a skip however it arose -- and not of today's exit codes.
    """
    legs = vw.validate(temperature=False)
    haduk = next(leg for leg in legs if "HadUK" in leg.name)

    assert haduk.passed is None, (
        "a leg that was NOT ASKED FOR must read as a skip, not a pass; counting it green is a "
        "validator reporting a measurement it declined to make")
    assert haduk.mark == "COULD NOT RUN"
    assert haduk not in [leg for leg in legs if leg.passed is True]


def test_require_temperature_turns_a_skip_into_a_refusal(store, monkeypatch):
    """A gate wants the skip to be fatal; an exploratory run does not. Both are asserted.

    Without the first half, a `main` that returned non-zero unconditionally would pass the second.
    """
    monkeypatch.setattr(vw, "HADUK_DAY", store / "no-such-cache")
    # The one real FAIL in this fixture is absent (both cells carry the ERA5 columns), so the only
    # thing separating these two exit codes is how the skipped leg is treated.
    assert vw.main(["--no-temperature"]) == 0
    assert vw.main(["--require-temperature"]) == 2
    # ...AND ASKED OF THE OTHER ROUTE. Both flags at once is the contradiction a gate hits when it
    # wants the cheap run to be authoritative, and the honest answer is a refusal: the leg was
    # required and it was not run. Without this line the `--no-temperature` skip can be minted as
    # a pass and both assertions above still hold, because neither of them is reached through it.
    assert vw.main(["--no-temperature", "--require-temperature"]) == 2


def test_the_agreement_leg_refuses_a_store_whose_files_disagree(store):
    """The live defect: a series keyed by regime under a reader keyed by cell."""
    cells, regimes, series = _legs(store)
    assert vw.check_artefacts_agree(cells, regimes, series).passed is True

    # Exactly one fault, of exactly the live kind: a series key the regime map does not know.
    broken = json.loads(json.dumps(regimes))
    del broken["regime_of_cell"][BETA]
    broken["k"] = 1
    leg = vw.check_artefacts_agree(cells, broken, series)
    assert leg.passed is False
    assert "R01" in leg.detail, "the failure must name the key it could not place"


def test_the_decomposition_leg_refuses_a_series_that_is_not_an_anomaly(store):
    """A writer that stored the raw series under a reader that adds the level back.

    Every value would then be wrong by the cell's climatology -- about eleven degrees -- and every
    value would still look like a temperature.

    THIS TEST ALREADY EARNED ITS PLACE. The first version of the leg asked whether `level_c` was
    the mean of the reconstructed raw series, which is `mean(stored) + level_c` compared against
    `level_c`: true for every possible level. Shifting ALPHA's level by 3 C left the leg green,
    and that is how the tautology was found. The property asserted now is the non-circular one.
    """
    cells, regimes, series = _legs(store)
    assert vw.check_decomposition(cells, regimes, series).passed is True

    raw = {r: ([dict(row, temperature_mean_c=float(row["temperature_mean_c"]) + 10.0)
                for row in rows] if r == "R00" else rows)
           for r, rows in series.items()}
    leg = vw.check_decomposition(cells, regimes, raw)
    assert leg.passed is False
    assert ALPHA in leg.detail

    # AND the shifted level, which this leg honestly cannot see, is not claimed to be seen: it is
    # the HadUK leg's job, named in the docstring, and asserted here so the boundary stays true.
    shifted = json.loads(json.dumps(cells))
    shifted["cells"][ALPHA]["level_c"] += 3.0
    assert vw.check_decomposition(shifted, regimes, series).passed is True


def test_the_coverage_leg_refuses_a_temperature_only_cell(store):
    """18 of the real store's 156 cells are temperature-only, so this is the live state.

    The fabric path reads cloud cover: a cell with temperature and no cloud cannot drive it, and a
    store 88% pulled looks finished to every consumer that only asks for temperature.
    """
    cells, regimes, series = _legs(store)
    assert vw.check_era5_coverage(cells, regimes, series).passed is True

    stripped = {r: [dict(row, wind_speed_mean_ms="", cloud_cover_pct="", precipitation_mm="")
                    for row in rows] if r == "R01" else rows
                for r, rows in series.items()}
    leg = vw.check_era5_coverage(cells, regimes, stripped)
    assert leg.passed is False
    assert BETA in leg.detail


def test_the_window_leg_refuses_a_regime_with_a_missing_day(store):
    """A store that silently lost days still answers every lookup that does not ask for them."""
    cells, regimes, series = _legs(store)
    assert vw.check_window(series).passed is True

    short = {r: (rows[:-1] if r == "R00" else rows) for r, rows in series.items()}
    leg = vw.check_window(short)
    assert leg.passed is False
    assert "R00" in leg.detail


def test_an_absent_store_fails_rather_than_finding_nothing_to_check(store, monkeypatch):
    """The emptiest fail-open of all: zero artefacts, zero failures, a clean bill of health."""
    monkeypatch.setattr(vw, "CELLS_PATH", store / "gone.json")
    legs = vw.validate(temperature=False)
    assert [leg.passed for leg in legs] == [False]
    assert "build_weather_world" in legs[0].detail, "the refusal must say how to fix it"


def test_the_writers_output_passes_every_leg_it_is_asked(store):
    """The end-to-end pair: what the writer produces is what the validator accepts.

    This is the leg that would go red if the two modules ever drift apart again -- which is the
    whole failure this pair of files exists to end.
    """
    legs = vw.validate(temperature=False)
    failed = [leg for leg in legs if leg.passed is False]
    assert not failed, f"the writer produced a store its own validator refuses: {failed}"

    with gzip.open(store / "daily.csv.gz", "rt") as handle:
        assert len(list(csv.DictReader(handle))) == 2 * len(DATES)
