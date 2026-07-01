"""Phase 27c: Volume tolerance for I&C contracts."""
import pytest
from simulation.volume_tolerance import (
    VOLUME_TOLERANCE_FRACTION,
    compute_term_volume_tolerance,
)


def test_tolerance_fraction_is_ten_percent():
    assert VOLUME_TOLERANCE_FRACTION == pytest.approx(0.10)


def test_within_band_no_excess_no_deficit():
    result = compute_term_volume_tolerance(
        actual_kwh=2_000_000,
        contracted_kwh=2_000_000,
        avg_spot_gbp_per_mwh=80.0,
        hedge_price_gbp_per_mwh=75.0,
        hedge_fraction=0.90,
    )
    assert result["within_band"] is True
    assert result["excess_kwh"] == pytest.approx(0.0)
    assert result["deficit_kwh"] == pytest.approx(0.0)


def test_slight_over_within_band():
    """5% over contracted volume — still within ±10% band."""
    result = compute_term_volume_tolerance(
        actual_kwh=2_100_000,
        contracted_kwh=2_000_000,
        avg_spot_gbp_per_mwh=80.0,
        hedge_price_gbp_per_mwh=75.0,
        hedge_fraction=0.90,
    )
    assert result["within_band"] is True
    assert result["excess_kwh"] == pytest.approx(0.0)
    assert result["variance_pct"] == pytest.approx(5.0)


def test_excess_above_band_high():
    """15% over contracted volume → 5% excess settles at spot."""
    result = compute_term_volume_tolerance(
        actual_kwh=2_300_000,
        contracted_kwh=2_000_000,
        avg_spot_gbp_per_mwh=100.0,
        hedge_price_gbp_per_mwh=75.0,
        hedge_fraction=0.90,
    )
    assert result["within_band"] is False
    # band_high = 2_200_000; excess = 100_000 kWh
    assert result["excess_kwh"] == pytest.approx(100_000.0)
    # spot cost = 100_000 kWh × £100/MWh / 1000 = £10,000
    assert result["excess_spot_cost_gbp"] == pytest.approx(10_000.0)
    assert result["deficit_kwh"] == pytest.approx(0.0)


def test_deficit_below_band_low():
    """15% under contracted volume → 5% deficit; supplier unwinds over-hedge."""
    result = compute_term_volume_tolerance(
        actual_kwh=1_700_000,
        contracted_kwh=2_000_000,
        avg_spot_gbp_per_mwh=80.0,
        hedge_price_gbp_per_mwh=75.0,
        hedge_fraction=0.90,
    )
    assert result["within_band"] is False
    # band_low = 1_800_000; deficit = 100_000 kWh
    assert result["deficit_kwh"] == pytest.approx(100_000.0)
    assert result["excess_kwh"] == pytest.approx(0.0)
    # hedged_deficit = 100_000 × 0.90 = 90_000 kWh
    # unwind gain = 90_000 × (80 - 75) / 1000 = £450
    assert result["deficit_unwind_gbp"] == pytest.approx(450.0)


def test_deficit_unwind_loss_when_spot_below_hedge():
    """Spot below hedge price → supplier loses on unwind of over-hedged volume."""
    result = compute_term_volume_tolerance(
        actual_kwh=1_700_000,
        contracted_kwh=2_000_000,
        avg_spot_gbp_per_mwh=60.0,
        hedge_price_gbp_per_mwh=75.0,
        hedge_fraction=0.90,
    )
    # deficit = 100_000 kWh; hedged_deficit = 90_000 kWh
    # unwind = 90_000 × (60 - 75) / 1000 = -£1,350
    assert result["deficit_unwind_gbp"] == pytest.approx(-1_350.0)


def test_variance_pct_computed_correctly():
    result = compute_term_volume_tolerance(
        actual_kwh=2_200_000,
        contracted_kwh=2_000_000,
        avg_spot_gbp_per_mwh=80.0,
        hedge_price_gbp_per_mwh=75.0,
        hedge_fraction=0.90,
    )
    assert result["variance_pct"] == pytest.approx(10.0)


def test_band_boundaries_correct():
    result = compute_term_volume_tolerance(
        actual_kwh=2_000_000,
        contracted_kwh=2_000_000,
        avg_spot_gbp_per_mwh=80.0,
        hedge_price_gbp_per_mwh=75.0,
        hedge_fraction=0.90,
    )
    assert result["band_high_kwh"] == pytest.approx(2_200_000.0)
    assert result["band_low_kwh"] == pytest.approx(1_800_000.0)


def test_all_result_keys_present():
    from simulation.volume_tolerance import compute_term_volume_tolerance
    r = compute_term_volume_tolerance(100.0, 100.0, 50.0, 60.0, 0.85)
    expected_keys = {
        "actual_kwh", "contracted_kwh", "band_high_kwh", "band_low_kwh",
        "excess_kwh", "deficit_kwh", "excess_spot_cost_gbp", "deficit_unwind_gbp",
        "variance_pct", "within_band",
    }
    assert expected_keys == set(r.keys())


def test_contracted_kwh_stored_in_result():
    from simulation.volume_tolerance import compute_term_volume_tolerance
    r = compute_term_volume_tolerance(100.0, 200.0, 50.0, 60.0, 0.85)
    assert r["contracted_kwh"] == 200.0
    assert r["actual_kwh"] == 100.0


def test_excess_spot_cost_proportional_to_excess():
    from simulation.volume_tolerance import compute_term_volume_tolerance
    spot = 50.0
    r = compute_term_volume_tolerance(130.0, 100.0, spot, 60.0, 0.85)
    expected_excess_cost = r["excess_kwh"] * spot / 1000.0
    assert abs(r["excess_spot_cost_gbp"] - expected_excess_cost) < 1e-6


def test_zero_excess_zero_deficit_when_exactly_at_band_high():
    from simulation.volume_tolerance import compute_term_volume_tolerance
    r = compute_term_volume_tolerance(110.0, 100.0, 50.0, 60.0, 0.85)
    assert r["excess_kwh"] == pytest.approx(0.0, abs=0.01)
    assert r["within_band"] is True
