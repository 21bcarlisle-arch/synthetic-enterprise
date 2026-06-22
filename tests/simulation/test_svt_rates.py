"""Tests for Phase 39a SVT electricity rate lookup."""
import pytest
from simulation.svt_rates import get_svt_elec_rate_gbp_per_mwh


def test_returns_float_for_known_quarter():
    rate = get_svt_elec_rate_gbp_per_mwh("2024-04-01")
    assert isinstance(rate, float)
    assert rate > 0


def test_jan_2019_matches_ofgem_cap():
    # Ofgem cap Jan 2019: 16.52p/kWh = 165.2 £/MWh
    rate = get_svt_elec_rate_gbp_per_mwh("2019-01-15")
    assert abs(rate - 165.2) < 0.1


def test_oct_2022_reflects_crisis():
    # Energy crisis peak: 51.89p/kWh = 518.9 £/MWh
    rate = get_svt_elec_rate_gbp_per_mwh("2022-11-01")
    assert abs(rate - 518.9) < 1.0


def test_quarter_fallthrough_within_year():
    # March is in Q1 (Jan period)
    rate_jan = get_svt_elec_rate_gbp_per_mwh("2024-01-01")
    rate_mar = get_svt_elec_rate_gbp_per_mwh("2024-03-31")
    assert rate_jan == rate_mar


def test_quarter_boundary_april():
    # April period differs from January period
    rate_mar = get_svt_elec_rate_gbp_per_mwh("2024-03-31")
    rate_apr = get_svt_elec_rate_gbp_per_mwh("2024-04-01")
    # 2024 Q1: 27.4p → 274 £/MWh, Q2: 24.5p → 245 £/MWh
    assert rate_apr < rate_mar


def test_before_2016_returns_none():
    rate = get_svt_elec_rate_gbp_per_mwh("2015-12-31")
    assert rate is None


def test_2026_extrapolated_returns_float():
    rate = get_svt_elec_rate_gbp_per_mwh("2026-06-01")
    assert isinstance(rate, float)
    assert rate > 0


def test_2029_extrapolated_returns_float():
    rate = get_svt_elec_rate_gbp_per_mwh("2029-09-15")
    assert isinstance(rate, float)
    assert rate > 0


def test_gbp_per_mwh_unit_conversion():
    # Rate should be roughly 10× the p/kWh value
    # Jan 2025: 24.86p/kWh → 248.6 £/MWh
    rate = get_svt_elec_rate_gbp_per_mwh("2025-01-01")
    assert abs(rate - 248.6) < 0.5


def test_crisis_rate_much_higher_than_normal():
    rate_2020 = get_svt_elec_rate_gbp_per_mwh("2020-06-01")
    rate_2022_oct = get_svt_elec_rate_gbp_per_mwh("2022-11-01")
    assert rate_2022_oct > rate_2020 * 2.5
