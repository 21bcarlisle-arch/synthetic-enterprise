"""Tests for Forward Curve Confidence Band (Phase ET)."""
import datetime as dt
import pytest
from company.trading.forward_curve_confidence import (
    TenorBand, ForwardCurvePoint, ForwardCurveConfidenceBand,
    _tenor_band, _CONFIDENCE_INTERVAL_PCT,
)

AS_OF = dt.date(2024, 1, 1)


def make_point(months_fwd=6, mid=80.0, fuel="electricity", source="market"):
    delivery = dt.date(AS_OF.year + (AS_OF.month + months_fwd - 1) // 12,
                       (AS_OF.month + months_fwd - 1) % 12 + 1, 1)
    return ForwardCurvePoint(
        delivery_date=delivery,
        as_of_date=AS_OF,
        fuel=fuel,
        mid_price_gbp_per_mwh=mid,
        source=source,
    )


class TestTenorBand:
    def test_front_month(self):
        assert _tenor_band(0) == TenorBand.FRONT_MONTH
        assert _tenor_band(1) == TenorBand.FRONT_MONTH

    def test_near_quarter(self):
        assert _tenor_band(3) == TenorBand.NEAR_QUARTER
        assert _tenor_band(6) == TenorBand.NEAR_QUARTER

    def test_far_quarter(self):
        assert _tenor_band(12) == TenorBand.FAR_QUARTER

    def test_near_seasonal(self):
        assert _tenor_band(18) == TenorBand.NEAR_SEASONAL

    def test_far_seasonal(self):
        assert _tenor_band(30) == TenorBand.FAR_SEASONAL


class TestForwardCurvePoint:
    def test_months_forward(self):
        p = make_point(months_fwd=6)
        assert p.months_forward == 6

    def test_tenor_band_near_quarter(self):
        p = make_point(months_fwd=6)
        assert p.tenor_band == TenorBand.NEAR_QUARTER

    def test_confidence_interval(self):
        p = make_point(months_fwd=6)
        assert p.confidence_interval_pct == _CONFIDENCE_INTERVAL_PCT[TenorBand.NEAR_QUARTER]

    def test_lower_band(self):
        p = make_point(months_fwd=6, mid=100.0)
        expected = 100.0 * (1 - 12.0 / 100)  # NEAR_QUARTER = 12%
        assert p.lower_band_gbp_per_mwh == pytest.approx(expected)

    def test_upper_band(self):
        p = make_point(months_fwd=6, mid=100.0)
        expected = 100.0 * (1 + 12.0 / 100)
        assert p.upper_band_gbp_per_mwh == pytest.approx(expected)

    def test_band_width(self):
        p = make_point(months_fwd=6, mid=100.0)
        assert p.band_width_gbp_per_mwh == pytest.approx(24.0)  # 12% * 2 * 100

    def test_is_extrapolated_true(self):
        p = make_point(source="extrapolated")
        assert p.is_extrapolated

    def test_is_extrapolated_false(self):
        p = make_point(source="market")
        assert not p.is_extrapolated

    def test_far_seasonal_wider_band(self):
        near = make_point(months_fwd=1, mid=100.0)
        far = make_point(months_fwd=30, mid=100.0)
        assert far.band_width_gbp_per_mwh > near.band_width_gbp_per_mwh

    def test_point_summary(self):
        p = make_point(months_fwd=6, mid=80.0)
        s = p.point_summary()
        assert "electricity" in s
        assert "near_quarter" in s


class TestForwardCurveConfidenceBand:
    def test_add_and_retrieve(self):
        band = ForwardCurveConfidenceBand()
        band.add_point(make_point(fuel="electricity"))
        assert len(band.points_for_fuel("electricity")) == 1

    def test_points_sorted_by_date(self):
        band = ForwardCurveConfidenceBand()
        band.add_point(make_point(months_fwd=12, fuel="gas"))
        band.add_point(make_point(months_fwd=3, fuel="gas"))
        pts = band.points_for_fuel("gas")
        assert pts[0].delivery_date < pts[1].delivery_date

    def test_points_in_band(self):
        band = ForwardCurveConfidenceBand()
        band.add_point(make_point(months_fwd=0))  # front month
        band.add_point(make_point(months_fwd=6))  # near quarter
        assert len(band.points_in_band(TenorBand.FRONT_MONTH)) == 1

    def test_extrapolated_points(self):
        band = ForwardCurveConfidenceBand()
        band.add_point(make_point(source="extrapolated"))
        band.add_point(make_point(source="market"))
        assert len(band.extrapolated_points()) == 1

    def test_max_confidence_interval(self):
        band = ForwardCurveConfidenceBand()
        band.add_point(make_point(months_fwd=1, fuel="electricity"))
        band.add_point(make_point(months_fwd=30, fuel="electricity"))
        max_ci = band.max_confidence_interval_pct("electricity")
        assert max_ci == _CONFIDENCE_INTERVAL_PCT[TenorBand.FAR_SEASONAL]

    def test_max_confidence_interval_empty(self):
        band = ForwardCurveConfidenceBand()
        assert band.max_confidence_interval_pct("electricity") == 0.0

    def test_band_summary(self):
        band = ForwardCurveConfidenceBand()
        band.add_point(make_point())
        s = band.band_summary(AS_OF)
        assert "Forward Curve Confidence" in s
