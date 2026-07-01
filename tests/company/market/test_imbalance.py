import pytest
"""Phase 126: Imbalance price risk model tests."""

from company.market.imbalance import compute_imbalance, imbalance_summary


def test_short_position_is_cost():
    exp = compute_imbalance("SP001", metered_mwh=1.0, contracted_mwh=0.8, spot_price_gbp_mwh=100.0)
    assert exp.status == "short"
    assert exp.charge_gbp > 0


def test_long_position_is_receipt():
    exp = compute_imbalance("SP002", metered_mwh=0.8, contracted_mwh=1.0, spot_price_gbp_mwh=100.0)
    assert exp.status == "long"
    assert exp.charge_gbp < 0


def test_balanced_is_zero():
    exp = compute_imbalance("SP003", metered_mwh=1.0, contracted_mwh=1.0, spot_price_gbp_mwh=100.0)
    assert exp.status == "balanced"
    assert exp.charge_gbp == 0.0


def test_short_charge_uses_ssp_premium():
    exp = compute_imbalance("SP001", metered_mwh=1.0, contracted_mwh=0.0, spot_price_gbp_mwh=100.0)
    # SSP = 100 * 1.18 = 118; charge = 1 MWh * 118 = 118
    assert abs(exp.charge_gbp - 118.0) < 0.5


def test_stress_mode_higher_premium():
    normal = compute_imbalance("SP001", 1.0, 0.0, 100.0, stress=False)
    stressed = compute_imbalance("SP001", 1.0, 0.0, 100.0, stress=True)
    assert stressed.charge_gbp > normal.charge_gbp


def test_long_charge_uses_sbp_discount():
    exp = compute_imbalance("SP002", metered_mwh=0.0, contracted_mwh=1.0, spot_price_gbp_mwh=100.0)
    # SBP = 100 * 0.95 = 95; receipt = -1 MWh * 95 = -95
    assert abs(exp.charge_gbp - (-95.0)) < 0.5


def test_imbalance_mwh_sign():
    exp_short = compute_imbalance("SP001", 1.2, 1.0, 100.0)
    exp_long = compute_imbalance("SP002", 0.8, 1.0, 100.0)
    assert exp_short.imbalance_mwh > 0
    assert exp_long.imbalance_mwh < 0


def test_summary_totals():
    exposures = [
        compute_imbalance("SP001", 1.0, 0.8, 100.0),
        compute_imbalance("SP002", 0.8, 1.0, 100.0),
        compute_imbalance("SP003", 1.0, 1.0, 100.0),
    ]
    s = imbalance_summary(exposures)
    assert s["total_periods"] == 3
    assert s["short_periods"] == 1
    assert s["long_periods"] == 1
    assert s["balanced_periods"] == 1


def test_summary_net_cost_or_receipt():
    short_exp = compute_imbalance("SP001", 2.0, 0.0, 100.0)  # big short = net cost
    s = imbalance_summary([short_exp])
    assert s["net_cost_or_receipt"] == "cost"

import pytest

# --- Phase KX depth tests ---

def test_period_id_stored():
    exp = compute_imbalance("SP_KX", 1.0, 0.8, 100.0)
    assert exp.period_id == "SP_KX"


def test_metered_mwh_stored():
    exp = compute_imbalance("SP001", 5.0, 4.0, 100.0)
    assert exp.metered_mwh == pytest.approx(5.0)


def test_contracted_mwh_stored():
    exp = compute_imbalance("SP001", 5.0, 4.0, 100.0)
    assert exp.contracted_mwh == pytest.approx(4.0)


def test_spot_price_stored():
    exp = compute_imbalance("SP001", 1.0, 1.0, 75.0)
    assert exp.spot_price_gbp_mwh == pytest.approx(75.0)


def test_imbalance_mwh_is_metered_minus_contracted():
    exp = compute_imbalance("SP001", 3.0, 2.5, 100.0)
    assert exp.imbalance_mwh == pytest.approx(0.5, abs=0.001)


def test_status_is_string():
    exp = compute_imbalance("SP001", 1.0, 1.0, 100.0)
    assert isinstance(exp.status, str)


def test_status_balanced_when_equal():
    exp = compute_imbalance("SP001", 1.0, 1.0, 100.0)
    assert exp.status == "balanced"


def test_charge_is_float():
    exp = compute_imbalance("SP001", 2.0, 1.5, 100.0)
    assert isinstance(exp.charge_gbp, float)


def test_summary_total_periods():
    exposures = [compute_imbalance(f"SP{i:03}", 1.0, 0.9, 100.0) for i in range(5)]
    s = imbalance_summary(exposures)
    assert s["total_periods"] == 5


def test_summary_short_count():
    exposures = [compute_imbalance("SP001", 2.0, 1.0, 100.0)]  # short
    s = imbalance_summary(exposures)
    assert s["short_periods"] == 1
