"""Phase 52 — ToU demand response model tests."""
import pytest
from saas.demand_response import (
    PEAK_PERIODS,
    OFFPEAK_PERIODS,
    BASE_SHIFT_FRACTION,
    EV_BOOST,
    HEAT_PUMP_BOOST,
    compute_shift_fraction,
    apply_demand_shift,
    make_shifted_shape_fn,
)

_FLAT_PROFILE = [1.0] * 48  # 1 kWh per period


class TestPeriodSets:
    def test_peak_periods_count(self):
        assert len(PEAK_PERIODS) == 7  # SP 32-38

    def test_offpeak_periods_include_overnight(self):
        # SP 1-14 = 00:00-07:00
        assert all(sp in OFFPEAK_PERIODS for sp in range(1, 15))

    def test_peak_and_offpeak_disjoint(self):
        assert PEAK_PERIODS.isdisjoint(OFFPEAK_PERIODS)


class TestComputeShiftFraction:
    def test_no_assets_returns_base(self):
        assert compute_shift_fraction(None) == pytest.approx(BASE_SHIFT_FRACTION)

    def test_empty_assets_returns_base(self):
        assert compute_shift_fraction({}) == pytest.approx(BASE_SHIFT_FRACTION)

    def test_ev_adds_boost(self):
        frac = compute_shift_fraction({"ev": True})
        assert frac == pytest.approx(BASE_SHIFT_FRACTION + EV_BOOST)

    def test_heat_pump_adds_boost(self):
        frac = compute_shift_fraction({"heat_pump": True})
        assert frac == pytest.approx(BASE_SHIFT_FRACTION + HEAT_PUMP_BOOST)

    def test_ev_and_heat_pump_both_add(self):
        frac = compute_shift_fraction({"ev": True, "heat_pump": True})
        assert frac == pytest.approx(BASE_SHIFT_FRACTION + EV_BOOST + HEAT_PUMP_BOOST)

    def test_result_capped_at_one(self):
        # Artificially large values should not exceed 1.0
        frac = compute_shift_fraction({"ev": True, "heat_pump": True})
        assert frac <= 1.0

    def test_false_assets_ignored(self):
        frac = compute_shift_fraction({"ev": False, "solar": True})
        assert frac == pytest.approx(BASE_SHIFT_FRACTION)


class TestApplyDemandShift:
    def test_zero_shift_returns_unchanged_profile(self):
        shifted, kwh = apply_demand_shift(_FLAT_PROFILE, 0.0)
        assert shifted == _FLAT_PROFILE
        assert kwh == 0.0

    def test_total_consumption_conserved(self):
        shifted, kwh = apply_demand_shift(_FLAT_PROFILE, BASE_SHIFT_FRACTION)
        assert sum(shifted) == pytest.approx(sum(_FLAT_PROFILE), abs=1e-9)

    def test_shifted_kwh_matches_difference(self):
        profile = [2.0] * 48
        shifted, reported_kwh = apply_demand_shift(profile, 0.5)
        peak_before = 2.0 * len(PEAK_PERIODS)
        expected_shifted = peak_before * 0.5
        assert reported_kwh == pytest.approx(expected_shifted, rel=1e-6)

    def test_peak_periods_reduced(self):
        shifted, _ = apply_demand_shift(_FLAT_PROFILE, BASE_SHIFT_FRACTION)
        for sp in PEAK_PERIODS:
            assert shifted[sp - 1] < _FLAT_PROFILE[sp - 1]

    def test_offpeak_periods_increased(self):
        shifted, _ = apply_demand_shift(_FLAT_PROFILE, BASE_SHIFT_FRACTION)
        for sp in OFFPEAK_PERIODS:
            assert shifted[sp - 1] > _FLAT_PROFILE[sp - 1]

    def test_non_peak_non_offpeak_periods_unchanged(self):
        """Mid-day periods (not peak, not off-peak) should not change."""
        shifted, _ = apply_demand_shift(_FLAT_PROFILE, BASE_SHIFT_FRACTION)
        for i in range(48):
            sp = i + 1
            if sp not in PEAK_PERIODS and sp not in OFFPEAK_PERIODS:
                assert shifted[i] == pytest.approx(_FLAT_PROFILE[i])

    def test_shift_fraction_clamped_to_one(self):
        # shift_fraction > 1.0 should behave as 1.0 (all peak moves off-peak)
        shifted, kwh = apply_demand_shift(_FLAT_PROFILE, 1.5)
        peak_kwh = sum(shifted[sp - 1] for sp in PEAK_PERIODS)
        assert peak_kwh == pytest.approx(0.0, abs=1e-9)

    def test_wrong_length_profile_returned_unchanged(self):
        short_profile = [1.0] * 10
        shifted, kwh = apply_demand_shift(short_profile, 0.5)
        assert shifted == short_profile
        assert kwh == 0.0


class TestMakeShiftedShapeFn:
    def test_wraps_correctly(self):
        def base_fn(date_str: str):
            return _FLAT_PROFILE[:]

        wrapped = make_shifted_shape_fn(base_fn, BASE_SHIFT_FRACTION)
        result = wrapped("2022-01-15")
        assert len(result) == 48
        assert sum(result) == pytest.approx(sum(_FLAT_PROFILE), abs=1e-9)

    def test_zero_shift_returns_original(self):
        def base_fn(date_str: str):
            return [float(i) for i in range(1, 49)]

        wrapped = make_shifted_shape_fn(base_fn, 0.0)
        result = wrapped("2022-01-15")
        assert result == list(range(1, 49))
