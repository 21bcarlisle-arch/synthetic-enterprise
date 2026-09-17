"""The two claims `fabric_demand_path` makes about the cell store, which were prose until now.

THE DEFECT (2026-09-17). `fabric_demand_path` names two controls in its own docstrings as "the
failable control" for the load-bearing claims of the W1_14 landing, and **neither existed**:

* `the_runner_reads_the_cell_store` — named at `_archive_days`, as what says the settlement path
  passes `WeatherWorldSource.days` rather than the four legacy `sim/weather_data/*.csv` files.
* `weather_days_for_two_premises_in_one_cell_is_the_same_sky` — named on `WeatherWorldSource`, as
  what says the memoisation holds, i.e. that one cell means one sky.

Both are claims about the change that took the book from 4 fabric-driven premises to 130. This
project's standard is that a rule lives in prose *and* as enforced code or not at all.

**WHY THE FIRST ONE IS NOT PARANOIA.** `_archive_days` is still the DEFAULT value of
`weather_days_for`, kept because the tests and `tools/fabric_settlement_gap` drive the seam with the
four archive sites. So a call site that simply *forgets* the keyword reads four CSVs, and 130
premises fall back to the national profile — with no exception, no refusal, and no verdict anywhere
saying so, because falling back to the legacy archive is a legal thing for that parameter to do.
The failure mode is silence, which is this repository's most expensive shape.

**AND WHY THE SECOND IS NOT EITHER.** "Two households in one cell must experience identical weather
— that's what makes the difference in their demand attributable to fabric and people rather than to
two separate downloads" is the director's architecture, in his words. If the memoisation broke, two
premises in one cell would get two lists built from the same rows, and nothing would look wrong:
every number would still be right, and the attribution the whole design exists for would be gone.
"""
from __future__ import annotations

import ast
import datetime as dt
from pathlib import Path

import pytest

from simulation import fabric_demand_path as fdp

PROJECT = Path(__file__).resolve().parents[2]
RUNNER = PROJECT / "simulation" / "run_phase2b.py"

#: The seam functions that read weather. A call to either from the runner MUST name its source.
WEATHER_READING_CALLS = ("fabric_providers_for_book", "build_fabric_series_for_site")


def _calls_in(path: Path, names: tuple[str, ...]) -> list[ast.Call]:
    tree = ast.parse(path.read_text())
    found = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        ident = func.id if isinstance(func, ast.Name) else getattr(func, "attr", None)
        if ident in names:
            found.append(node)
    return found


def test_the_runner_reads_the_cell_store():
    """Every weather-reading call in `run_phase2b` names its source explicitly.

    AST rather than a string search, because what must hold is a property of the CALL -- that the
    keyword is present on it -- and a grep for "weather_days_for" is satisfied by the word
    appearing in a comment three hundred lines away.

    Keyed to "names its source", not to "names `_weather_source.days`": the runner is allowed to
    change which store it reads. What it may never do is fall through to the default, because the
    default is the four-CSV archive and the fallback is silent.
    """
    calls = _calls_in(RUNNER, WEATHER_READING_CALLS)
    assert calls, (
        "population floor: no call to any of "
        f"{WEATHER_READING_CALLS} was found in {RUNNER.name} at all. Either the seam was renamed "
        "and this control is now blind, or the runner stopped reading weather -- and this test "
        "cannot tell those apart, so it refuses rather than passing vacuously."
    )
    missing = [c.lineno for c in calls
               if not any(kw.arg == "weather_days_for" for kw in c.keywords)]
    assert not missing, (
        f"{RUNNER.name} calls the fabric seam at line(s) {missing} without passing "
        "`weather_days_for`, so it falls through to `_archive_days` -- the four legacy "
        "sim/weather_data CSVs. That is not an error at runtime: those premises settle on the "
        "national profile and no verdict records it. This is the silent half of the defect the "
        "cell store was built to end."
    )


def test_the_legacy_archive_is_still_the_default_so_this_control_is_load_bearing():
    """The premise of the test above: forgetting the keyword really does read the legacy archive.

    If `weather_days_for` ever becomes required, or its default becomes the cell store, the control
    above stops guarding anything -- and a control that cannot fail must not be left standing green.
    This leg is what notices.
    """
    import inspect
    for name in WEATHER_READING_CALLS:
        sig = inspect.signature(getattr(fdp, name))
        default = sig.parameters["weather_days_for"].default
        assert default is fdp._archive_days, (
            f"{name}'s `weather_days_for` default is no longer the legacy archive. That is "
            "probably an improvement -- but re-read `test_the_runner_reads_the_cell_store`, "
            "because it exists only to catch a fall-through to this default."
        )


# ---------------------------------------------------------------------------
# One cell is one sky
# ---------------------------------------------------------------------------

CELL = "E450N0206"
START, END = dt.date(2022, 1, 1), dt.date(2022, 1, 3)
ROWS = [
    {"date": "2022-01-01", "temperature_min_c": 2.0, "temperature_max_c": 7.0,
     "temperature_mean_c": 4.5, "cloud_cover_pct": 70.0, "wind_speed_mean_ms": 5.0},
    {"date": "2022-01-02", "temperature_min_c": 1.0, "temperature_max_c": 6.0,
     "temperature_mean_c": 3.5, "cloud_cover_pct": 55.0, "wind_speed_mean_ms": 4.0},
    {"date": "2022-01-03", "temperature_min_c": 0.0, "temperature_max_c": 5.0,
     "temperature_mean_c": 2.5, "cloud_cover_pct": 40.0, "wind_speed_mean_ms": 6.0},
]


class _FakeWorld:
    """A world of one cell. Counts its reads, so "memoised" is observed and not assumed."""

    def __init__(self, rows=None):
        self.rows = ROWS if rows is None else rows
        self.reads = 0

    def cell_id_for(self, lat, lon):
        return CELL

    def for_cell(self, site, start=None, end=None):
        self.reads += 1
        if site != CELL:
            raise fdp.WeatherWorldRefusal(f"no cell {site!r}")
        return [r for r in self.rows
                if (start is None or r["date"] >= start) and (end is None or r["date"] <= end)]


def test_weather_days_for_two_premises_in_one_cell_is_the_same_sky():
    """The director's architecture, as a control: one cell, one sky, by object identity.

    `is`, not `==`. Two lists built from the same rows would compare equal and would still be two
    downloads in a different coat -- and the whole reason for a per-cell store rather than a
    per-property pull is that the difference between two households' demand is attributable to
    fabric and people, never to which copy of the weather they happened to get.
    """
    world = _FakeWorld()
    src = fdp.WeatherWorldSource(world)
    a = src.site_for({"location": {"lat": 51.5, "lon": -0.1}})
    b = src.site_for({"location": {"lat": 51.5001, "lon": -0.1001}})
    assert a == b == CELL, "the two premises did not snap to one cell; this proves nothing"

    days_a = src.days(a, start=START, end=END)
    days_b = src.days(b, start=START, end=END)
    assert days_a is days_b, (
        "two premises in one cell got two different day lists -- one cell is no longer one sky"
    )
    assert world.reads == 1, (
        f"the store was read {world.reads} times for one cell and one window; the memoisation is "
        "not holding, and at 130 premises that is 130 reads of an 8 MB gzip"
    )


def test_a_different_window_is_a_different_read_so_the_memo_is_not_keyed_too_loosely():
    """The mirror: a memo keyed only on the cell would serve January's sky for February.

    This is the leg that stops the test above being satisfied by a cache that never invalidates,
    which would be a far worse defect than the one it guards.
    """
    world = _FakeWorld()
    src = fdp.WeatherWorldSource(world)
    first = src.days(CELL, start=START, end=END)
    second = src.days(CELL, start=START, end=dt.date(2022, 1, 2))
    assert first is not second
    assert len(first) == 3 and len(second) == 2
    assert world.reads == 2


def test_a_cell_missing_a_field_refuses_and_names_the_cell_and_the_right_remedy():
    """A refusal must be clearable by the reader, and must not name the design the director refused.

    The remedy sentence said "pull that coordinate" until 2026-09-17 -- an instruction to do the
    per-property pull that was rejected in writing, under which two households in one cell get two
    skies. A refusal naming the wrong remedy is worse than one naming none: it recruits the reader
    into rebuilding the thing the architecture exists to prevent.
    """
    holed = [dict(ROWS[0]), dict(ROWS[1])]
    holed[1]["wind_speed_mean_ms"] = float("nan")
    src = fdp.WeatherWorldSource(_FakeWorld(holed))

    with pytest.raises(fdp.WeatherWorldRefusal) as exc:
        src.days(CELL, start=START, end=END)
    message = str(exc.value)
    assert CELL in message, "the refusal must name the cell that has to be pulled"
    assert "wind_speed_mean_ms" in message and "2022-01-02" in message
    assert "CELL" in message and "build_weather_world" in message, (
        "the remedy must point at extending the per-cell store"
    )
    assert "coordinate" not in message.lower(), (
        "the remedy is naming a per-property pull again -- the design the director refused"
    )


def test_a_cell_with_no_days_in_the_window_refuses_rather_than_returning_an_empty_sky():
    """Zero days is not a quiet answer: a settlement day of no demand prices as a real free day."""
    src = fdp.WeatherWorldSource(_FakeWorld())
    with pytest.raises(fdp.WeatherWorldRefusal, match="holds no day"):
        src.days(CELL, start=dt.date(2019, 1, 1), end=dt.date(2019, 1, 2))


def test_availability_is_decided_over_every_field_not_over_the_cell_existing():
    """A membership test would call a temperature-only cell available and hand the trace a NaN.

    Eight cells in the live store are exactly this shape -- temperature, no wind, no cloud -- so
    this is a real population, not a hypothetical.
    """
    holed = [dict(r) for r in ROWS]
    holed[0]["cloud_cover_pct"] = float("nan")
    assert fdp.WeatherWorldSource(_FakeWorld()).available(CELL) is True
    assert fdp.WeatherWorldSource(_FakeWorld(holed)).available(CELL) is False
