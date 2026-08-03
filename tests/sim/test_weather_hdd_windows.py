"""Tests for cumulative/rolling HDD windows (thermal memory).

Director instruction 2026-08-03, docs/design/PREMISE_FABRIC_PHYSICS_DISCOVER.md
section 4 item E: `get_hdd()` is memoryless (today's HDD depends only on
today's temperature); real gas demand depends on the recent HISTORY of
temperature too (building thermal mass; system-level storage/linepack
drawdown). This file proves `get_cumulative_hdd()` actually captures that,
and proves it the R15 way -- with a control that can be shown to FIRE against
a "mutant" that erases the memory (window_days=1), not just a happy-path
assertion.

Citation for the decay shape (National Grid "Gas Demand Forecasting
Methodology" 2020 v1, Appendix 1.1, Et = 0.5*Et-1 + 0.5*ATt):
docs/market_research/gas_demand_cumulative_hdd_cwv.md
"""
from __future__ import annotations

import math

import pytest

from sim.weather_hdd import (
    _WEATHER_CACHE,
    HDD_BASE_TEMP_C,
    HDD_WINDOW_DAYS,
    HDD_WINDOW_DECAY,
    REFERENCE_MONTHLY_HDD,
    _finite_hdd_window_weights,
    get_cumulative_hdd,
    get_hdd,
)


def _inject(customer_id: str, temps: dict[str, float]) -> None:
    """Directly seed the module's weather cache (same technique as
    test_weather_hdd.py::test_hdd_formula_correct) so scenarios are exact and
    independent of the real historical CSVs -- avoids any dependency on real
    weather data changing under us."""
    _WEATHER_CACHE[customer_id] = dict(temps)


# ---------------------------------------------------------------------------
# 1. Weight-generation correctness (independent hand calculation --
#    NOT derived by calling get_cumulative_hdd, to avoid a tautological check)
# ---------------------------------------------------------------------------

class TestWindowWeights:
    def test_weights_sum_to_one(self):
        for window_days in (1, 2, 3, 5, 10, 14, 30):
            weights = _finite_hdd_window_weights(window_days, 0.5)
            assert math.isclose(sum(weights), 1.0, rel_tol=1e-12)

    def test_weights_match_hand_calculation_for_window_3(self):
        # Independent calculation: decay=0.5, window=3 -> raw weights
        # [0.5, 0.25, 0.125], total 0.875 -> normalised [4/7, 2/7, 1/7]
        weights = _finite_hdd_window_weights(3, 0.5)
        expected = [0.5 / 0.875, 0.25 / 0.875, 0.125 / 0.875]
        for w, e in zip(weights, expected):
            assert math.isclose(w, e, rel_tol=1e-9)

    def test_weights_strictly_decreasing(self):
        weights = _finite_hdd_window_weights(10, 0.5)
        for a, b in zip(weights, weights[1:]):
            assert a > b, "more recent days must always weigh more than older ones"

    def test_default_window_residual_mass_under_one_tenth_percent(self):
        # Documents the truncation-depth rationale: 0.5**10 residual vs the
        # pre-normalisation total.
        raw_total = sum(0.5 ** (k + 1) for k in range(HDD_WINDOW_DAYS))
        residual = 1.0 - raw_total
        assert residual < 0.001

    @pytest.mark.parametrize("window_days", [0, -1, -5])
    def test_rejects_nonpositive_window(self, window_days):
        with pytest.raises(ValueError):
            _finite_hdd_window_weights(window_days, 0.5)

    @pytest.mark.parametrize("decay", [0.0, 1.0, -0.2, 1.5])
    def test_rejects_out_of_range_decay(self, decay):
        with pytest.raises(ValueError):
            _finite_hdd_window_weights(5, decay)


# ---------------------------------------------------------------------------
# 2. window_days=1 collapses exactly to the memoryless get_hdd (identity
#    that must hold given the weight normalisation -- independent check).
# ---------------------------------------------------------------------------

class TestSingleDayCollapseIdentity:
    def test_window_one_equals_memoryless_hdd(self):
        _inject("WIN1", {"2021-03-10": 3.0})
        direct = get_hdd("2021-03-10", "WIN1")
        windowed = get_cumulative_hdd("2021-03-10", "WIN1", window_days=1)
        assert math.isclose(direct, windowed, rel_tol=1e-12)


# ---------------------------------------------------------------------------
# 3. Precise weighted-sum formula check against an independently
#    hand-computed expected value (window=3, tractable by hand).
# ---------------------------------------------------------------------------

class TestWeightedSumFormula:
    def test_three_day_window_matches_hand_calculation(self):
        # Day D=5.0C -> HDD 10.5; D-1=10.0C -> HDD 5.5; D-2=15.5C -> HDD 0.0
        _inject("WINCALC", {
            "2021-01-10": 5.0,
            "2021-01-09": 10.0,
            "2021-01-08": 15.5,
        })
        result = get_cumulative_hdd("2021-01-10", "WINCALC", window_days=3, decay=0.5)
        # Independently hand-computed: weights [4/7, 2/7, 1/7], hdds [10.5, 5.5, 0.0]
        expected = (4 / 7) * 10.5 + (2 / 7) * 5.5 + (1 / 7) * 0.0
        assert math.isclose(result, expected, rel_tol=1e-9)


# ---------------------------------------------------------------------------
# 4. R15 mutation proof -- the actual required control.
#    Two scenarios share IDENTICAL temperature on the target day D but
#    differ in the days before D (a cold snap vs. an isolated cold day).
#    A control asserting "thermal memory" must FIRE (distinguish them) at
#    the real (window_days=10) implementation, and the SAME assertion must
#    provably FAIL if the window is mutated/collapsed to window_days=1 --
#    proving the control actually tests the memory, not something incidental.
# ---------------------------------------------------------------------------

class TestThermalMemoryMutationProof:
    COLD_SNAP_TEMPS = {
        "2021-02-01": 0.0,
        "2021-02-02": 0.0,
        "2021-02-03": 0.0,
        "2021-02-04": 0.0,
        "2021-02-05": 0.0,   # day D: identical to the isolated-cold-day scenario
    }
    ISOLATED_COLD_DAY_TEMPS = {
        "2021-02-01": 15.5,  # warm -> 0 HDD
        "2021-02-02": 15.5,
        "2021-02-03": 15.5,
        "2021-02-04": 15.5,
        "2021-02-05": 0.0,   # day D: identical own-day temperature to the cold-snap scenario
    }
    DAY_D = "2021-02-05"

    def setup_method(self):
        _inject("COLDSNAP", self.COLD_SNAP_TEMPS)
        _inject("ISOLATED", self.ISOLATED_COLD_DAY_TEMPS)

    def test_own_day_hdd_is_identical_by_construction(self):
        # Sanity: the memoryless HDD for day D is exactly the same in both
        # scenarios -- any difference the window shows is due ONLY to history.
        assert get_hdd(self.DAY_D, "COLDSNAP") == get_hdd(self.DAY_D, "ISOLATED")

    def test_real_window_shows_thermal_memory(self):
        cold_snap = get_cumulative_hdd(self.DAY_D, "COLDSNAP", window_days=5, decay=0.5)
        isolated = get_cumulative_hdd(self.DAY_D, "ISOLATED", window_days=5, decay=0.5)
        # THE CONTROL: same day-D temperature, but the cold-snap history must
        # produce a strictly higher cumulative HDD than the isolated-cold-day
        # history. This is the fidelity property item E exists to deliver.
        assert cold_snap > isolated, (
            "cumulative HDD must be higher after a multi-day cold snap than "
            "after an isolated cold day with the same day-D temperature -- "
            "this is the thermal-memory property the window exists to add"
        )

    def test_mutant_window_one_erases_the_memory_control_fires(self):
        # MUTATION: collapse the window to a single day (window_days=1) --
        # this is exactly what "reverting to memoryless" looks like in this
        # API. The SAME property asserted above must now be FALSE: the two
        # scenarios must be indistinguishable, proving the control above
        # would have caught this regression had it shipped.
        cold_snap_mutant = get_cumulative_hdd(self.DAY_D, "COLDSNAP", window_days=1)
        isolated_mutant = get_cumulative_hdd(self.DAY_D, "ISOLATED", window_days=1)
        assert math.isclose(cold_snap_mutant, isolated_mutant, rel_tol=1e-12), (
            "window_days=1 must collapse to memoryless behaviour -- the two "
            "scenarios becoming indistinguishable here is the proof that the "
            "test above is actually exercising thermal memory, not noise"
        )
        # Restore-and-pass: the un-mutated (default-window) call still shows
        # the distinction, in the same test run, proving the control isn't
        # itself broken or order-dependent.
        cold_snap_real = get_cumulative_hdd(self.DAY_D, "COLDSNAP")
        isolated_real = get_cumulative_hdd(self.DAY_D, "ISOLATED")
        assert cold_snap_real > isolated_real


# ---------------------------------------------------------------------------
# 5. FAIL-OPEN / FAIL-SILENT / TAUTOLOGY defence
# ---------------------------------------------------------------------------

class TestFailOpenFailSilentNaN:
    def test_nan_temperature_raises_not_silently_zeroes(self):
        # Pre-fix, max(0.0, HDD_BASE_TEMP_C - nan) == 0.0 in Python -- a
        # corrupt reading would have silently read as "zero heating demand".
        _inject("NANDAY", {"2021-05-05": float("nan")})
        with pytest.raises(ValueError):
            get_hdd("2021-05-05", "NANDAY")

    def test_nan_inside_a_window_propagates_as_an_error_not_a_silent_value(self):
        _inject("NANWIN", {
            "2021-05-01": 5.0,
            "2021-05-02": float("nan"),
            "2021-05-03": 4.0,
        })
        with pytest.raises(ValueError):
            get_cumulative_hdd("2021-05-03", "NANWIN", window_days=3)

    def test_inf_temperature_raises(self):
        _inject("INFDAY", {"2021-05-06": float("inf")})
        with pytest.raises(ValueError):
            get_hdd("2021-05-06", "INFDAY")
        _inject("NEGINFDAY", {"2021-05-06": float("-inf")})
        with pytest.raises(ValueError):
            get_hdd("2021-05-06", "NEGINFDAY")

    def test_missing_days_fall_back_to_climatology_not_zero(self):
        # Unknown customer -> _load_weather_means returns {} for every day ->
        # every day in the window falls back to REFERENCE_MONTHLY_HDD, never
        # to a silent zero and never to a full/duplicate-day substitution.
        result = get_cumulative_hdd("2022-01-15", "TOTALLY_UNKNOWN_CUSTOMER", window_days=5)
        jan_climatology_daily = REFERENCE_MONTHLY_HDD[1] / 30.0
        assert math.isclose(result, jan_climatology_daily, rel_tol=1e-9)
        assert result > 0.0, "missing history must not silently read as zero HDD"

    def test_window_days_zero_rejected(self):
        with pytest.raises(ValueError):
            get_cumulative_hdd("2021-01-01", "C1", window_days=0)

    def test_invalid_date_string_rejected(self):
        with pytest.raises(ValueError):
            get_cumulative_hdd("not-a-date", "C1")

    def test_decay_out_of_range_rejected(self):
        with pytest.raises(ValueError):
            get_cumulative_hdd("2021-01-01", "C1", decay=1.0)


# ---------------------------------------------------------------------------
# 6. Point-in-Time Blindfold: a window at date D must never be influenced by
#    a day AFTER D.
# ---------------------------------------------------------------------------

class TestPointInTimeBlindfold:
    def test_future_day_value_never_influences_the_window(self):
        base_temps = {
            "2021-06-01": 8.0,
            "2021-06-02": 9.0,
            "2021-06-03": 7.0,
        }
        _inject("PITB", dict(base_temps))
        before = get_cumulative_hdd("2021-06-03", "PITB", window_days=3)

        # Now add/alter a day AFTER the target date with an extreme value --
        # if the window ever peeked forward this would change the result.
        mutated = dict(base_temps)
        mutated["2021-06-04"] = -50.0
        _inject("PITB", mutated)
        after = get_cumulative_hdd("2021-06-03", "PITB", window_days=3)

        assert math.isclose(before, after, rel_tol=1e-12), (
            "a future day's temperature must never change an earlier day's "
            "cumulative HDD -- point-in-time blindfold violation"
        )


# ---------------------------------------------------------------------------
# 7. C-S1 event-arrival tolerance: stateless recomputation means call order
#    and repetition never matter.
# ---------------------------------------------------------------------------

class TestEventArrivalTolerance:
    def test_call_order_does_not_affect_result(self):
        temps = {f"2021-07-{d:02d}": 5.0 + d for d in range(1, 11)}
        _inject("ORDER_A", temps)
        _inject("ORDER_B", temps)

        # Scenario A: query days in forward chronological order.
        results_forward = [
            get_cumulative_hdd(f"2021-07-{d:02d}", "ORDER_A", window_days=5)
            for d in range(5, 11)
        ]
        # Scenario B: query the SAME days, reverse order, interleaved with
        # repeats -- simulating late/out-of-order/duplicate arrival.
        order = [10, 5, 9, 6, 8, 7, 10, 5]
        seen = {}
        for d in order:
            seen[d] = get_cumulative_hdd(f"2021-07-{d:02d}", "ORDER_B", window_days=5)
        results_backward = [seen[d] for d in range(5, 11)]

        assert results_forward == results_backward

    def test_repeated_calls_are_idempotent(self):
        _inject("IDEMPOTENT", {"2021-08-01": 2.0, "2021-08-02": 3.0})
        r1 = get_cumulative_hdd("2021-08-02", "IDEMPOTENT", window_days=2)
        r2 = get_cumulative_hdd("2021-08-02", "IDEMPOTENT", window_days=2)
        r3 = get_cumulative_hdd("2021-08-02", "IDEMPOTENT", window_days=2)
        assert r1 == r2 == r3


# ---------------------------------------------------------------------------
# 8. R14: default-window sanity + non-negativity + basis-level sanity checks.
# ---------------------------------------------------------------------------

class TestCumulativeHddSanity:
    def test_default_window_is_ten_days_decay_half(self):
        assert HDD_WINDOW_DAYS == 10
        assert HDD_WINDOW_DECAY == 0.5

    def test_cumulative_hdd_never_negative(self):
        for day in range(1, 15):
            date_str = f"2020-01-{day:02d}"
            result = get_cumulative_hdd(date_str, "C1")
            assert result >= 0.0

    def test_cumulative_hdd_close_to_memoryless_in_a_stable_regime(self):
        # In a run of identical days, the cumulative and memoryless HDD must
        # coincide (weighted average of a constant is that constant) --
        # regression guard against a weighting bug that shifts level.
        _inject("STABLE", {f"2021-09-{d:02d}": 4.0 for d in range(1, 11)})
        direct = get_hdd("2021-09-10", "STABLE")
        windowed = get_cumulative_hdd("2021-09-10", "STABLE", window_days=10)
        assert math.isclose(direct, windowed, rel_tol=1e-9)
