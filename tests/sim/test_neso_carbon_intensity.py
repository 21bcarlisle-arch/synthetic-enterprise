"""The NESO published-intensity adapter, and the controls that must be able to fail.

Every control here is written against a NAMED DEFECT and checked to FIRE on it (R15). The three
killer patterns are addressed explicitly:

  TAUTOLOGY   -- `test_the_comparison_does_not_derive_the_published_series_from_our_own`
  FAIL-OPEN   -- the null-actual family: a missing gram is never zero grams
  FAIL-SILENT -- the `NesoIntensityUnavailable` family: an absent series raises, never returns
                 an empty or flat one that would read as perfect agreement

The settlement-period tests carry the mutation inline: each asserts BOTH that the real function
is right AND that the obvious wrong implementation (local-clock arithmetic) gets a different,
wrong answer -- so the test cannot pass by accident on a day where the two agree.
"""
from __future__ import annotations

import datetime as dt
import json
from zoneinfo import ZoneInfo

import pytest

from sim.neso_carbon_intensity import (
    FIRST_PUBLISHED_DATE,
    PUBLISHED_BASIS,
    NesoIntensityUnavailable,
    actual_by_period,
    compare_shapes,
    fetch_national,
    load_cached,
    published_shape,
    settlement_key,
    to_settlement_periods,
)

LONDON = ZoneInfo("Europe/London")


def _utc(text: str) -> dt.datetime:
    return dt.datetime.strptime(text, "%Y-%m-%dT%H:%MZ").replace(tzinfo=dt.timezone.utc)


def _periods_of_local_day(day: str) -> list[int]:
    """Every settlement period the real function assigns to `day`, walked in UTC."""
    d = dt.date.fromisoformat(day)
    start = dt.datetime.combine(d, dt.time(0, 0), tzinfo=LONDON).astimezone(dt.timezone.utc)
    end = dt.datetime.combine(d + dt.timedelta(days=1), dt.time(0, 0), tzinfo=LONDON).astimezone(dt.timezone.utc)
    out = []
    cursor = start
    while cursor < end:
        date_str, period = settlement_key(cursor)
        if date_str == day:
            out.append(period)
        cursor += dt.timedelta(minutes=30)
    return out


# --------------------------------------------------------------------------------------
# Settlement-period mapping
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "instant,expected",
    [
        ("2024-01-15T00:00Z", ("2024-01-15", 1)),   # GMT: UTC midnight IS local midnight
        ("2022-12-31T23:30Z", ("2022-12-31", 48)),  # GMT: last half hour of the year
        ("2024-06-30T23:00Z", ("2024-07-01", 1)),   # BST: the day starts an hour early in UTC
        ("2024-07-01T00:00Z", ("2024-07-01", 3)),   # BST: UTC midnight is period 3, not period 1
    ],
)
def test_settlement_key_on_known_half_hours(instant, expected):
    assert settlement_key(_utc(instant)) == expected


def test_bst_is_where_clock_arithmetic_first_goes_wrong():
    """NAMED DEFECT: reading the period off the UTC clock instead of the London clock.

    Silent for five winter months a year, then wrong by two periods all summer.
    """
    instant = _utc("2024-07-01T00:00Z")
    naive_utc_period = instant.hour * 2 + instant.minute // 30 + 1
    assert naive_utc_period == 1
    assert settlement_key(instant)[1] == 3


def test_the_spring_forward_day_has_46_periods():
    """NAMED DEFECT: local-clock arithmetic numbers this day 1..48. GB says it has 46."""
    periods = _periods_of_local_day("2024-03-31")
    assert len(periods) == 46
    assert periods == sorted(periods) == list(range(1, 47))


def test_the_autumn_back_day_has_50_periods_and_loses_none():
    """NAMED DEFECT: local-clock arithmetic yields TWO half hours numbered 3 on this day and
    silently overwrites one, so an hour of the dirtiest-or-cleanest grid of the year vanishes."""
    periods = _periods_of_local_day("2024-10-27")
    assert len(periods) == 50
    assert len(set(periods)) == 50, "a repeated period number means a half hour was overwritten"
    assert periods == list(range(1, 51))


def test_an_ordinary_day_has_48_periods():
    assert _periods_of_local_day("2024-06-12") == list(range(1, 49))


def test_a_naive_datetime_is_refused_rather_than_assumed_utc():
    """FAIL-OPEN: assuming a naive instant is UTC would silently misdate every BST half hour."""
    with pytest.raises(ValueError):
        settlement_key(dt.datetime(2024, 7, 1, 0, 0))


# --------------------------------------------------------------------------------------
# Parsing — FAIL-OPEN controls
# --------------------------------------------------------------------------------------


def test_a_null_actual_is_dropped_and_never_zeroed():
    """NAMED DEFECT: `float(intensity.get('actual') or 0)`.

    Zero grams is not a neutral placeholder -- it is a perfectly clean grid, the single most
    flattering value for the mission's own thesis, and it would inflate the measured worth of
    time-shifting without bound.
    """
    records = [
        {"from": "2024-01-15T00:00Z", "intensity": {"forecast": 100, "actual": 99}},
        {"from": "2024-01-15T00:30Z", "intensity": {"forecast": 98, "actual": None}},
    ]
    series = to_settlement_periods(records)
    assert set(series) == {("2024-01-15", 1)}
    assert ("2024-01-15", 2) not in series
    assert all(entry["actual"] > 0 for entry in series.values())


def test_a_published_zero_is_treated_as_absence_not_as_a_clean_grid():
    """NAMED DEFECT, found against the real feed: guarding `is None` but not `<= 0`.

    The API really does publish `actual: 0` for five half hours over 2019-2024. GB's grid cannot
    reach zero gCO2/kWh, and a zero is what the SPREAD statistic divides by.
    """
    records = [
        {"from": "2024-01-15T00:00Z", "intensity": {"actual": 99}},
        {"from": "2024-01-15T00:30Z", "intensity": {"actual": 0}},
        {"from": "2024-01-15T01:00Z", "intensity": {"actual": -3}},
    ]
    series = to_settlement_periods(records)
    assert set(series) == {("2024-01-15", 1)}


def test_a_zero_valued_half_hour_makes_the_spread_raise_by_name():
    """FAIL-SILENT: a bare ZeroDivisionError names the arithmetic, not the cause. Anything that
    reaches `compare_shapes` with a zero should be told what is actually wrong."""
    demand = {("2024-01-15", p): 20000.0 for p in range(1, 4)}
    good = {("2024-01-15", p): 1.0 for p in range(1, 4)}
    with_zero = {("2024-01-15", 1): 0.0, ("2024-01-15", 2): 1.0, ("2024-01-15", 3): 2.0}
    with pytest.raises(NesoIntensityUnavailable, match="absent reading"):
        compare_shapes(good, with_zero, demand, "2024")


def test_the_real_cached_feed_has_no_zero_or_negative_half_hour_after_parsing():
    """The control run against the actual artefact, not a fixture -- the parse is what stands
    between five real outage half hours and a published claim about the cleanest grid in GB."""
    pytest.importorskip("json")
    import pathlib

    if not pathlib.Path("sim/cache/neso_carbon_intensity_national.json").exists():
        pytest.skip("NESO cache not built on this machine")
    series = actual_by_period(to_settlement_periods(load_cached()))
    assert series, "the cache parsed to nothing"
    assert min(series.values()) > 0.0
    assert min(series.values()) >= 10.0, "a single-digit grams reading deserves a second look"


def test_a_forecast_is_never_substituted_for_a_missing_actual():
    """NAMED DEFECT: falling back to forecast to 'fill the gap'. Forecast and outturn answer
    different questions, and silently mixing them is a foresight leak dressed as completeness."""
    records = [{"from": "2024-01-15T00:00Z", "intensity": {"forecast": 250, "actual": None}}]
    with pytest.raises(NesoIntensityUnavailable):
        to_settlement_periods(records)


def test_an_all_null_window_raises_rather_than_returning_empty():
    """FAIL-SILENT: an empty dict downstream reads as 'nothing to compare', i.e. agreement."""
    records = [{"from": "2024-01-15T00:00Z", "intensity": {"actual": None}} for _ in range(48)]
    with pytest.raises(NesoIntensityUnavailable):
        to_settlement_periods(records)


def test_malformed_records_are_skipped_without_taking_the_window_down():
    records = [
        {"from": "not-a-timestamp", "intensity": {"actual": 100}},
        {"intensity": {"actual": 100}},
        {"from": "2024-01-15T00:00Z", "intensity": {"actual": 99}},
    ]
    assert set(to_settlement_periods(records)) == {("2024-01-15", 1)}


def test_forecast_is_carried_when_present():
    records = [{"from": "2024-01-15T00:00Z", "intensity": {"forecast": 117, "actual": 99}}]
    series = to_settlement_periods(records)
    assert series[("2024-01-15", 1)] == {"actual": 99.0, "forecast": 117.0}


# --------------------------------------------------------------------------------------
# Shape normalisation
# --------------------------------------------------------------------------------------


def test_the_published_shape_is_demand_weighted_to_exactly_one():
    intensity = {("2024-01-15", p): 100.0 + p for p in range(1, 49)}
    demand = {("2024-01-15", p): 20000.0 + 100 * p for p in range(1, 49)}
    shape = published_shape(intensity, demand)
    weighted = sum(shape[k] * demand[k] for k in shape) / sum(demand[k] for k in shape)
    assert weighted == pytest.approx(1.0, abs=1e-12)


def test_the_weighting_is_demand_weighted_not_arithmetic():
    """NAMED DEFECT: a plain mean. It would re-level every consumer's annual total -- a change
    to a published figure disguised as a units convention.

    Built so the two means genuinely differ: the dirty half hours carry most of the demand.
    """
    intensity = {("2024-01-15", 1): 100.0, ("2024-01-15", 2): 300.0}
    demand = {("2024-01-15", 1): 1000.0, ("2024-01-15", 2): 9000.0}
    shape = published_shape(intensity, demand)
    demand_weighted_mean = (100.0 * 1000 + 300.0 * 9000) / 10000  # 280
    arithmetic_mean = 200.0
    assert shape[("2024-01-15", 1)] == pytest.approx(100.0 / demand_weighted_mean)
    assert shape[("2024-01-15", 1)] != pytest.approx(100.0 / arithmetic_mean)


def test_a_half_hour_with_no_demand_weight_is_skipped_not_weighted_at_zero():
    intensity = {("2024-01-15", 1): 100.0, ("2024-01-15", 2): 300.0}
    demand = {("2024-01-15", 1): 1000.0}
    shape = published_shape(intensity, demand)
    assert set(shape) == {("2024-01-15", 1)}


def test_no_overlap_between_intensity_and_demand_raises():
    """FAIL-SILENT: returning {} here makes every downstream comparison vacuously pass."""
    with pytest.raises(NesoIntensityUnavailable):
        published_shape({("2024-01-15", 1): 100.0}, {("2023-01-15", 1): 1000.0})


# --------------------------------------------------------------------------------------
# The comparison itself
# --------------------------------------------------------------------------------------


def test_two_identical_series_show_no_gap():
    intensity = {("2024-01-15", p): 100.0 + 5 * p for p in range(1, 49)}
    demand = {("2024-01-15", p): 20000.0 for p in range(1, 49)}
    shape = published_shape(intensity, demand)
    stats = compare_shapes(shape, shape, demand, "2024")
    assert stats["mean_abs_error"] == pytest.approx(0.0, abs=1e-12)
    assert stats["correlation"] == pytest.approx(1.0, abs=1e-9)
    assert stats["half_hours"] == 48


def test_the_comparison_renormalises_over_the_intersection():
    """NAMED DEFECT: comparing two series each normalised over its OWN coverage.

    One series here is missing the dirty half of the day, so its own mean is lower and every one
    of its shape values is correspondingly inflated. Without re-normalisation the comparison
    reports that inflation as a physics disagreement. Re-normalised over the common keys, the
    two agree exactly -- which is the truth: on the half hours both cover, they are the same.
    """
    demand = {("2024-01-15", p): 20000.0 for p in range(1, 49)}
    grams = {("2024-01-15", p): 100.0 + 5 * p for p in range(1, 49)}

    full = published_shape(grams, demand)
    partial_keys = {k: v for k, v in grams.items() if k[1] <= 24}
    partial = published_shape(partial_keys, demand)

    # The two disagree BEFORE re-normalisation -- that is the defect the control must survive.
    shared = [k for k in partial if k in full]
    raw_gap = max(abs(full[k] - partial[k]) for k in shared)
    assert raw_gap > 0.1, "the fixture must actually exhibit the coverage-inflation defect"

    stats = compare_shapes(full, partial, demand, "2024")
    assert stats["half_hours"] == 24
    assert stats["mean_abs_error"] == pytest.approx(0.0, abs=1e-12)


def test_a_series_that_is_genuinely_flatter_is_reported_as_flatter():
    """The measurement that matters: the reconstruction is expected to swing MORE than NESO's
    series does, and the statistic that says so must move in the right direction."""
    demand = {("2024-01-15", p): 20000.0 for p in range(1, 49)}
    swingy = published_shape({("2024-01-15", p): 50.0 + 10 * p for p in range(1, 49)}, demand)
    flat = published_shape({("2024-01-15", p): 200.0 + 1 * p for p in range(1, 49)}, demand)
    stats = compare_shapes(swingy, flat, demand, "2024")
    assert stats["reconstructed_spread"] > stats["published_spread"]
    assert stats["reconstructed_min"] < stats["published_min"]


def test_no_shared_half_hour_in_the_year_raises():
    demand = {("2024-01-15", 1): 20000.0}
    with pytest.raises(NesoIntensityUnavailable):
        compare_shapes({("2024-01-15", 1): 1.0}, {("2023-01-15", 1): 1.0}, demand, "2024")


def test_the_comparison_does_not_derive_the_published_series_from_our_own():
    """TAUTOLOGY control, enforced structurally rather than asserted.

    `sim/neso_carbon_intensity.py` must not import the reconstruction. If it ever did, the
    'independent' truth series would be a restatement of the thing it is checking and every gap
    statistic would be a measurement of nothing.
    """
    import ast
    import pathlib

    tree = ast.parse(pathlib.Path("sim/neso_carbon_intensity.py").read_text())
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported += [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.append(node.module)

    assert imported, "the AST walk found no imports at all -- the control would pass on anything"
    offenders = [name for name in imported if "grid_carbon_intensity" in name]
    assert not offenders, (
        f"the adapter imports {offenders}: the 'independent' truth series would be a "
        "restatement of the thing it checks, and every gap statistic a measurement of nothing"
    )


# --------------------------------------------------------------------------------------
# Availability — FAIL-SILENT controls
# --------------------------------------------------------------------------------------


def test_a_request_before_the_series_begins_is_refused():
    """FAIL-OPEN: the API returns an EMPTY window for pre-2018 dates rather than an error, so a
    caller asking for 2016 would silently get a shorter comparison and never know."""
    with pytest.raises(NesoIntensityUnavailable):
        fetch_national("2016-01-01", "2016-02-01")
    assert FIRST_PUBLISHED_DATE == "2018-05-11"


def test_an_absent_cache_raises_rather_than_returning_empty(tmp_path, monkeypatch):
    import sim.neso_carbon_intensity as mod

    monkeypatch.setattr(mod, "CACHE_PATH", tmp_path / "nope.json")
    with pytest.raises(NesoIntensityUnavailable):
        load_cached()


def test_an_empty_cache_file_raises(tmp_path, monkeypatch):
    import sim.neso_carbon_intensity as mod

    path = tmp_path / "empty.json"
    path.write_text("[]")
    monkeypatch.setattr(mod, "CACHE_PATH", path)
    with pytest.raises(NesoIntensityUnavailable):
        load_cached()


def test_the_published_basis_names_what_makes_the_two_series_differ():
    """R14 on a basis. The level difference between the two series is legitimate and explained
    by exactly these three inclusions; a basis string that dropped them would make the gap look
    like an error in one of them."""
    for term in ("loss-corrected", "interconnector", "coal"):
        assert term in PUBLISHED_BASIS.lower()


def test_actual_by_period_is_a_plain_view():
    series = {("2024-01-15", 1): {"actual": 99.0, "forecast": 117.0}}
    assert actual_by_period(series) == {("2024-01-15", 1): 99.0}
