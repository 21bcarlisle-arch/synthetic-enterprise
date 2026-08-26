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
    MIN_DAYS_FOR_A_DISTRIBUTION,
    PUBLISHED_BASIS,
    SENSITIVITY_WINDOWS,
    NesoIntensityUnavailable,
    actual_by_period,
    compare_shapes,
    fetch_national,
    forecast_skill,
    load_cached,
    published_shape,
    settlement_key,
    to_settlement_periods,
    window_sensitivity,
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


def _two_day_pair(within_scale_ours: float = 1.0, between_spread_ours: float = 0.0):
    """Two days, 48 half hours each, with the WITHIN-day swing and the BETWEEN-day spread made
    independently controllable. The published side is fixed; only ours moves.

    BOTH KNOBS PRESERVE THE SERIES MEAN, and that is a property of the fixture rather than a
    detail: `published_shape` divides each series by its OWN demand-weighted mean, so a fixture
    that moves ours' mean while claiming to scale its swing measures the two together and the
    expected factor stops being the number you dialled in. The between-day knob therefore pushes
    the two days APART symmetrically instead of lifting one.
    """
    days = ("2024-01-15", "2024-01-16")
    demand = {(d, p): 20000.0 for d in days for p in range(1, 49)}
    theirs_g = {(d, p): 300.0 + (60.0 if d == days[1] else 0.0) + 4.0 * p
                for d in days for p in range(1, 49)}
    day_mean = {d: sum(theirs_g[(d, p)] for p in range(1, 49)) / 48.0 for d in days}
    push = {days[0]: -between_spread_ours, days[1]: +between_spread_ours}
    ours_g = {
        (d, p): (day_mean[d] + push[d]
                 + within_scale_ours * (theirs_g[(d, p)] - day_mean[d]))
        for d in days for p in range(1, 49)
    }
    return published_shape(ours_g, demand), published_shape(theirs_g, demand), demand


def test_the_swing_decomposition_separates_two_axes_that_move_independently():
    """The whole claim of the statistic: doubling the WITHIN-day swing must move the within-day
    factor and leave the between-day one alone, and vice versa.

    NAMED DEFECT IT FIRES ON (mutation-proven 2026-08-25): subtracting the SERIES mean instead of
    each DAY's own mean. That leaves every day's level inside the 'within-day' term, so a change
    made purely between days leaks into the intra-day figure -- which is precisely the confusion
    the split exists to end. Under that mutation the second assertion below goes to 1.14.
    """
    doubled = compare_shapes(*_two_day_pair(within_scale_ours=2.0), "2024")
    assert doubled["days"] == 2
    assert doubled["within_day_swing_overstated_by"] == pytest.approx(2.0, rel=1e-6)
    assert doubled["between_day_swing_overstated_by"] == pytest.approx(1.0, rel=1e-6)

    # The two days pushed 60 g/kWh further apart, their internal shape untouched: theirs' day
    # means sit 30 either side of the grand mean, ours 90, so the factor is exactly 3.
    apart = compare_shapes(*_two_day_pair(between_spread_ours=60.0), "2024")
    assert apart["within_day_swing_overstated_by"] == pytest.approx(1.0, rel=1e-6)
    assert apart["between_day_swing_overstated_by"] == pytest.approx(3.0, rel=1e-6)


def test_the_two_swing_terms_recombine_to_the_total_dispersion():
    """A variance decomposition that does not recombine is not one — it is two unrelated numbers
    with suggestive names. within^2 + between^2 == total^2 holds only when the day means are
    removed exactly once, so this is the arithmetic check the naming implies.

    NOT SUFFICIENT ON ITS OWN, and it is left here saying so. Every day in this fixture carries
    all 48 half hours, and on a BALANCED panel the count-weighted and equally-weighted
    between-day terms are the same number — so this control cannot see which one the module
    uses. The next test is the one that can; this one holds the identity itself.
    """
    ours, theirs, demand = _two_day_pair(within_scale_ours=1.7, between_spread_ours=25.0)
    stats = compare_shapes(ours, theirs, demand, "2024")
    for side, series in (("reconstructed", ours), ("published", theirs)):
        keys = [k for k in series if k in demand]
        # Balanced panel (48 half hours every day), which is what makes the plain identity apply.
        mean = sum(series[k] for k in keys) / len(keys)
        total_var = sum((series[k] - mean) ** 2 for k in keys) / len(keys)
        within = stats[f"{side}_within_day_sd"]
        between = stats[f"{side}_between_day_sd"]
        assert within ** 2 + between ** 2 == pytest.approx(total_var, rel=1e-9), (
            f"the {side} decomposition does not recombine, so the two terms are not a split "
            "of the dispersion they are named after"
        )


def test_the_decomposition_recombines_on_an_UNBALANCED_panel():
    """THE CONTROL THAT EXISTS BECAUSE ITS MUTATION SURVIVED THE ONE ABOVE (R15, 2026-08-25).

    The real comparison is not balanced — 2019 shares 16,923 half hours over 359 days, where a
    full day each would be 17,232 — so how a short day is weighted in the between-day term is a
    live choice, not a formality. Weighted by the half hours it carries, the split recombines to
    the total dispersion exactly. Weighted equally with every other day, it does not, and the
    error is silent: two plausible-looking numbers that no longer add up to the thing they claim
    to be a split of.

    Mutation-proven both ways, and the figures are the mutation run's own: equal-weighting the
    day means breaks the identity here by 4.2% while passing every balanced-panel control in
    this file, and subtracting the series mean in place of each day's breaks it by 68.3%.
    """
    days = {"2024-01-15": 48, "2024-01-16": 6, "2024-01-17": 30}
    demand = {(d, p): 20000.0 for d, n in days.items() for p in range(1, n + 1)}
    grams = {(d, p): 250.0 + 90.0 * i + 4.0 * p
             for i, (d, n) in enumerate(days.items()) for p in range(1, n + 1)}
    shape = published_shape(grams, demand)
    stats = compare_shapes(shape, shape, demand, "2024")

    assert stats["days"] == 3
    assert stats["half_hours"] == 84, "the fixture must actually be unbalanced"

    keys = list(shape)
    mean = sum(shape[k] for k in keys) / len(keys)
    total_var = sum((shape[k] - mean) ** 2 for k in keys) / len(keys)
    got = stats["published_within_day_sd"] ** 2 + stats["published_between_day_sd"] ** 2
    assert got == pytest.approx(total_var, rel=1e-9), (
        "the split does not recombine once the days differ in length, so a short day's "
        "dispersion is being counted into neither term"
    )


def test_a_pure_rescaling_moves_the_swing_factors_and_never_the_correlation():
    """The two published quantities answer different questions and must not be read as one.

    Correlation is scale-invariant: a model that swings 3x too hard but at exactly the right
    times scores a perfect 1.0. So a page that quotes correlation as evidence the range is right,
    or a swing factor as evidence the TIMING is right, is quoting the wrong number. This pins
    that they move independently, which is the only reason publishing both is not redundancy.
    """
    # A PURE RESCALE OF THE WHOLE SERIES, which needs BOTH knobs turned together: theirs' day
    # means sit 30 either side of the grand mean, so tripling the swing about that mean means
    # tripling the within-day term AND pushing the days to +/-90. Turn only one knob and the
    # result is a reshaping, not a rescaling, and correlation legitimately falls below 1.
    ours, theirs, demand = _two_day_pair(within_scale_ours=3.0, between_spread_ours=60.0)
    stats = compare_shapes(ours, theirs, demand, "2024")
    assert stats["correlation"] == pytest.approx(1.0, abs=1e-9)
    assert stats["within_day_swing_overstated_by"] == pytest.approx(3.0, rel=1e-6)
    assert stats["between_day_swing_overstated_by"] == pytest.approx(3.0, rel=1e-6)


def test_a_single_day_reports_no_between_day_factor_rather_than_a_nan():
    """FAIL-OPEN control. One day has no between-day term at all. NaN would survive round() and
    every downstream comparison as a quietly false answer; None forces a caller to say so."""
    demand = {("2024-01-15", p): 20000.0 for p in range(1, 49)}
    shape = published_shape({("2024-01-15", p): 100.0 + 5 * p for p in range(1, 49)}, demand)
    stats = compare_shapes(shape, shape, demand, "2024")
    assert stats["days"] == 1
    assert stats["published_between_day_sd"] == pytest.approx(0.0, abs=1e-12)
    assert stats["between_day_swing_overstated_by"] is None
    assert stats["within_day_swing_overstated_by"] == pytest.approx(1.0, rel=1e-9)


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


# --------------------------------------------------------------------------------------
# forecast_skill -- NESO's own forecast graded against NESO's own outturn
#
# Every control below was MUTATION-RUN on 2026-08-26: the named defect was written into
# `sim/neso_carbon_intensity.py`, the test confirmed RED, and the module restored GREEN. A
# control that has not been seen to fail is not evidence (R15).
# --------------------------------------------------------------------------------------

def _fabricated_days(n_days: int, per_period, *, periods: int = 48) -> dict:
    """{(date, period): {"forecast": g, "actual": g}} from a rule, for `n_days` whole days.

    Fabricated on purpose and never sampled from the cache: these controls have to exercise
    shapes the real series does not contain (a perfectly flat day, an inverted forecast, an
    impossible reading), and a fixture drawn from the data could only ever test the data.
    """
    out = {}
    for day in range(n_days):
        date_str = f"2024-{1 + day // 28:02d}-{1 + day % 28:02d}"
        for period in range(1, periods + 1):
            forecast, actual = per_period(day, period)
            out[(date_str, period)] = {"forecast": float(forecast), "actual": float(actual)}
    return out


def _sawtooth(day: int, period: int) -> float:
    """A day with a real within-day swing, so there is an achievable saving to capture."""
    return 100.0 + 60.0 * ((period * 7) % 48) / 48.0


def test_a_perfect_forecast_captures_exactly_all_of_the_achievable_saving():
    """The anchor. If this is not 1.0 the statistic is not measuring what it says."""
    series = _fabricated_days(40, lambda d, p: (_sawtooth(d, p), _sawtooth(d, p)))
    measured = forecast_skill(series, "2024")
    assert measured["capture_mean"] == pytest.approx(1.0)
    assert measured["capture_min"] == pytest.approx(1.0)
    assert measured["capture_days_worse_than_average"] == 0


def test_the_window_is_picked_by_forecast_and_scored_on_outturn():
    """MUTATION: pick the window by `actual` instead of `forecast`.

    That mutation makes the statistic 1.0 on EVERY input by construction -- it would be
    hindsight grading hindsight -- so it survives the perfect-forecast test above and only this
    one, whose forecast deliberately ranks the day backwards, can see it."""
    inverted = _fabricated_days(40, lambda d, p: (200.0 - _sawtooth(d, p), _sawtooth(d, p)))
    measured = forecast_skill(inverted, "2024")
    assert measured["capture_mean"] < 0.0, (
        "a forecast that ranks the day backwards must score below zero, not 1.0"
    )


def test_a_forecast_that_picks_worse_than_average_is_reported_negative():
    """MUTATION: `fraction = max(0.0, fraction)`.

    Clamping is the most natural-looking edit in this function and it deletes exactly the days
    the ceiling exists to warn about -- the ones where following the published forecast was
    worse than not shifting at all. On the real 2019 series the worst day scores -1.20."""
    inverted = _fabricated_days(40, lambda d, p: (200.0 - _sawtooth(d, p), _sawtooth(d, p)))
    measured = forecast_skill(inverted, "2024")
    assert measured["capture_min"] < 0.0
    assert measured["capture_days_worse_than_average"] == measured["capture_days"]


def test_a_flat_day_is_degenerate_not_a_perfect_forecast():
    """MUTATION: record a day with no achievable saving as capture 1.0 (R15 FAIL-OPEN).

    A flat day is 0/0. Scoring it 1.0 is the fail-open substitution that would let a series of
    perfectly flat days -- the exact failure a broken feed produces -- report the most
    flattering possible answer."""
    half_flat = _fabricated_days(
        40, lambda d, p: ((100.0, 100.0) if d % 2 == 0 else (_sawtooth(d, p), _sawtooth(d, p))))
    measured = forecast_skill(half_flat, "2024")
    assert measured["capture_degenerate_days"] == 20
    assert measured["capture_days"] == 20
    assert measured["days"] == 40, "the flat days are excluded from the capture, not from the panel"

    all_flat = _fabricated_days(40, lambda d, p: (100.0, 100.0))
    with pytest.raises(NesoIntensityUnavailable):
        forecast_skill(all_flat, "2024")


def test_an_impossible_published_forecast_is_refused_by_physics_and_counted():
    """MUTATION: drop the ceiling test.

    NESO's published forecast field really does carry 13,579 gCO2/kWh (2019-07-24). Averaged in
    it moves that year's timing dispersion from 15.1 to 154.7 -- a tenfold artefact in the one
    statistic this module exists to state."""
    series = _fabricated_days(40, lambda d, p: (_sawtooth(d, p), _sawtooth(d, p)))
    series[("2024-01-01", 1)] = {"forecast": 13579.0, "actual": 112.0}
    measured = forecast_skill(series, "2024")
    assert measured["refused_half_hours"] == 1
    assert measured["half_hours"] == 40 * 48 - 1
    assert measured["mean_abs_error_g"] < 1.0, "the impossible reading reached the error statistics"


def test_the_refusal_is_symmetric_across_forecast_and_outturn():
    """MUTATION: refuse on `forecast > ceiling` only.

    A filter applied to one side of a comparison measures the filter: it would remove the half
    hours where the forecast was absurd and keep the outturn that made it look wrong."""
    series = _fabricated_days(40, lambda d, p: (_sawtooth(d, p), _sawtooth(d, p)))
    series[("2024-01-01", 1)] = {"forecast": 112.0, "actual": 13579.0}
    assert forecast_skill(series, "2024")["refused_half_hours"] == 1


def test_the_ceiling_is_derived_from_nesos_own_factor_table(monkeypatch):
    """MUTATION: write the ceiling as the literal 937.0.

    The number is only defensible because it is the maximum of NESO's OWN published per-fuel
    factors -- the dirtiest grid GB could physically be. A literal would go on saying 937 after
    that table was corrected, at which point it is a fitted threshold nobody chose."""
    import sim.elexon_fuel_outturn as fuel

    monkeypatch.setitem(fuel.NESO_PUBLISHED_FACTOR_G_CO2_PER_KWH, "COAL", 5000.0)
    series = _fabricated_days(40, lambda d, p: (_sawtooth(d, p), _sawtooth(d, p)))
    series[("2024-01-01", 1)] = {"forecast": 4000.0, "actual": 112.0}
    measured = forecast_skill(series, "2024")
    assert measured["refusal_ceiling_g"] == 5000.0
    assert measured["refused_half_hours"] == 0, "the ceiling did not follow its own source table"


def test_the_level_and_timing_split_removes_the_day_mean_not_the_series_mean():
    """MUTATION: subtract the grand mean instead of each day's own mean.

    The split is the whole content of the statistic -- a forecast 20 g high all day misleads
    nobody about WHEN to run the washing. These days have a per-day OFFSET and no within-day
    error at all, so the timing term must be exactly zero; subtracting the series mean instead
    would report the between-day spread as a timing error."""
    series = _fabricated_days(40, lambda d, p: (_sawtooth(d, p) + d, _sawtooth(d, p)))
    measured = forecast_skill(series, "2024")
    assert measured["timing_error_sd_g"] == pytest.approx(0.0, abs=1e-9)
    assert measured["level_error_sd_g"] > 10.0


def test_forecast_skill_hands_back_no_half_hour_pairing():
    """MUTATION: return the (forecast, actual) pairs alongside the aggregates.

    This is the control the module docstring's refusal rests on. Grading NESO's forecast
    against NESO's outturn is a fact about published data; handing a caller a per-half-hour
    pairing is a foresight surface, and the difference has to be checkable rather than
    promised. Every value that comes back is a scalar, and none of them is a settlement key."""
    series = _fabricated_days(40, lambda d, p: (_sawtooth(d, p), _sawtooth(d, p)))
    measured = forecast_skill(series, "2024")
    for key, value in measured.items():
        assert isinstance(key, str), f"{key!r} is not an aggregate's name"
        assert isinstance(value, (int, float)), f"{key} carries {type(value).__name__}, not a scalar"
    assert len(measured) < 40, "an aggregate set this large is a series in disguise"


def test_a_handful_of_days_is_refused_rather_than_percentiled():
    """MUTATION: `MIN_DAYS_FOR_A_DISTRIBUTION = 1`.

    A p5 over four days is the minimum of four days. The refusal is what stops a coverage hole
    being published as a distribution (R15 FAIL-SILENT: an unavailable measure must say so)."""
    series = _fabricated_days(4, lambda d, p: (_sawtooth(d, p), _sawtooth(d, p)))
    with pytest.raises(NesoIntensityUnavailable) as excinfo:
        forecast_skill(series, "2024")
    assert str(MIN_DAYS_FOR_A_DISTRIBUTION) in str(excinfo.value)


def test_a_short_day_is_dropped_from_the_capture_and_counted():
    """A truncated day's 'day mean' never saw the missing half hours, so its achievable saving
    is measured against the wrong baseline. Dropped, and said -- a coverage hole that quietly
    shortens the panel is a confound this project has already been caught by once."""
    series = _fabricated_days(40, lambda d, p: (_sawtooth(d, p), _sawtooth(d, p)))
    for period in range(20, 49):
        del series[("2024-01-01", period)]
    measured = forecast_skill(series, "2024")
    assert measured["short_days_dropped"] == 1
    assert measured["days"] == 39


def test_the_window_length_is_reported_and_moves_the_answer_it_is_given_to():
    """The dial is visible. `shift_window_half_hours` comes back in the row, and the sensitivity
    sweep exists so a headline cannot be improved by quietly widening the window."""
    inverted = _fabricated_days(40, lambda d, p: (200.0 - _sawtooth(d, p), _sawtooth(d, p)))
    assert forecast_skill(inverted, "2024", window_half_hours=2)["shift_window_half_hours"] == 2
    sweep = window_sensitivity(inverted, "2024")
    assert set(sweep) == {str(w) for w in SENSITIVITY_WINDOWS}
    with pytest.raises(NesoIntensityUnavailable):
        forecast_skill(inverted, "2024", window_half_hours=0)


def test_the_real_published_forecast_is_measurably_imperfect_and_measurably_useful():
    """The measurement on the REAL cached series, pinned loosely on both sides.

    Loosely because this is a fact about NESO's forecasting, not about this repository, and a
    tight pin would red the day the cache is extended. Both sides are asserted because the two
    failure modes point opposite ways: a capture of 1.0 means the grading collapsed into
    hindsight, and a capture near 0 means the pick is not being made on the forecast at all."""
    import pathlib

    if not pathlib.Path("sim/cache/neso_carbon_intensity_national.json").exists():
        pytest.skip("published series not cached")
    series = to_settlement_periods(load_cached())
    measured = forecast_skill(series, "2024")
    assert 0.6 < measured["capture_mean"] < 0.98
    assert measured["capture_p5"] < measured["capture_mean"], "no distribution, only a mean"
    assert measured["timing_error_sd_g"] > measured["level_error_sd_g"], (
        "the forecast's error would be pure level, which would cost a shifting claim nothing"
    )
