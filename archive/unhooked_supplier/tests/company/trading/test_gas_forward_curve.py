"""Tests for Wholesale Gas Forward Curve (Phase FR)."""
import datetime as dt
import pytest
from company.trading.gas_forward_curve import (
    GasTenorBand, GasForwardPoint, GasForwardCurve, _THERMS_PER_MWH,
    _GAS_CONFIDENCE_INTERVAL_PCT,
)

DATE = dt.date(2024, 1, 15)


def make_point(tenor=GasTenorBand.FRONT_MONTH, price=70.0, date=DATE):
    return GasForwardPoint(curve_date=date, tenor_band=tenor,
                           mid_price_pence_per_therm=price)


class TestGasForwardPoint:
    def test_gbp_per_mwh(self):
        p = make_point(price=100.0)
        expected = 100.0 * _THERMS_PER_MWH * 100
        assert p.mid_price_gbp_per_mwh == pytest.approx(expected)

    def test_confidence_interval(self):
        p = make_point(tenor=GasTenorBand.FRONT_MONTH)
        assert p.confidence_interval_pct == _GAS_CONFIDENCE_INTERVAL_PCT[GasTenorBand.FRONT_MONTH]

    def test_lower_band(self):
        p = make_point(tenor=GasTenorBand.FRONT_MONTH, price=100.0)
        ci = _GAS_CONFIDENCE_INTERVAL_PCT[GasTenorBand.FRONT_MONTH]
        assert p.lower_band_pence == pytest.approx(100.0 * (1 - ci / 100))

    def test_is_crisis(self):
        p = make_point(price=300.0)
        assert p.is_crisis_price

    def test_not_crisis(self):
        p = make_point(price=70.0)
        assert not p.is_crisis_price

    def test_point_summary(self):
        s = make_point().point_summary()
        assert "GasForward" in s and "p/therm" in s


class TestGasForwardCurve:
    def test_add_and_retrieve(self):
        curve = GasForwardCurve()
        curve.add_point(make_point())
        assert len(curve.points_for_date(DATE)) == 1

    def test_latest_da_price(self):
        curve = GasForwardCurve()
        curve.add_point(make_point(tenor=GasTenorBand.DAY_AHEAD, price=68.0,
                                    date=dt.date(2024, 1, 1)))
        curve.add_point(make_point(tenor=GasTenorBand.DAY_AHEAD, price=72.0))
        assert curve.latest_da_price_pence() == pytest.approx(72.0)

    def test_winter_summer_spread(self):
        curve = GasForwardCurve()
        curve.add_point(make_point(tenor=GasTenorBand.WINTER, price=90.0))
        curve.add_point(make_point(tenor=GasTenorBand.SUMMER, price=70.0))
        assert curve.winter_summer_spread(DATE) == pytest.approx(20.0)

    def test_winter_summer_spread_none_if_missing(self):
        curve = GasForwardCurve()
        curve.add_point(make_point(tenor=GasTenorBand.WINTER, price=90.0))
        assert curve.winter_summer_spread(DATE) is None

    def test_crisis_points(self):
        curve = GasForwardCurve()
        curve.add_point(make_point(price=300.0))
        curve.add_point(make_point(price=70.0, tenor=GasTenorBand.DAY_AHEAD))
        assert len(curve.crisis_points()) == 1

    def test_gas_curve_summary(self):
        curve = GasForwardCurve()
        curve.add_point(make_point())
        s = curve.gas_curve_summary(DATE)
        assert "Gas Forward Curve" in s


# --- Phase ME depth tests ---

def test_curve_date_stored():
    p = make_point()
    assert p.curve_date == DATE


def test_tenor_band_stored():
    p = make_point(tenor=GasTenorBand.WINTER)
    assert p.tenor_band == GasTenorBand.WINTER


def test_mid_price_stored():
    p = make_point(price=85.0)
    assert p.mid_price_pence_per_therm == pytest.approx(85.0)


def test_upper_band_above_mid():
    p = make_point(price=70.0)
    assert p.upper_band_pence > p.mid_price_pence_per_therm


def test_lower_band_below_mid():
    p = make_point(price=70.0)
    assert p.lower_band_pence < p.mid_price_pence_per_therm


def test_is_crisis_false_below_200():
    p = make_point(price=199.0)
    assert p.is_crisis_price is False


def test_is_crisis_true_above_200():
    p = make_point(price=201.0)
    assert p.is_crisis_price is True


def test_gas_tenor_band_has_7_members():
    assert len(list(GasTenorBand)) == 7


def test_gas_forward_curve_add_and_count():
    curve = GasForwardCurve()
    curve.add_point(make_point(tenor=GasTenorBand.DAY_AHEAD, price=55.0))
    curve.add_point(make_point(tenor=GasTenorBand.WINTER, price=80.0))
    assert len(curve.points_for_date(DATE)) == 2


def test_gbp_per_mwh_uses_therms_per_mwh():
    p = make_point(price=100.0)
    expected = 100.0 * _THERMS_PER_MWH * 100
    assert p.mid_price_gbp_per_mwh == pytest.approx(expected)
