"""Tests for Phase HL: Net Open Position Register."""
import pytest
from company.trading.net_open_position_register import (
    DeliveryPeriodPosition,
    ExposureDirection,
    NOPSeverity,
    NetOpenPositionRegister,
    _AMBER_THRESHOLD_PCT,
    _FLAT_TOLERANCE_PCT,
    _RED_THRESHOLD_PCT,
)


def _pos(retail, forward, year=2024, quarter=1, commodity="electricity") -> DeliveryPeriodPosition:
    reg = NetOpenPositionRegister()
    return reg.record(year, quarter, commodity, retail, forward)


class TestDeliveryPeriodPosition:
    def test_nop_underhedged(self):
        p = _pos(1000, 800)
        assert p.net_open_position_mwh == pytest.approx(-200)

    def test_nop_overhedged(self):
        p = _pos(1000, 1100)
        assert p.net_open_position_mwh == pytest.approx(100)

    def test_nop_flat(self):
        p = _pos(1000, 1000)
        assert p.net_open_position_mwh == pytest.approx(0)

    def test_nop_pct_underhedged(self):
        p = _pos(1000, 800)
        assert p.nop_pct_of_retail == pytest.approx(-20.0)

    def test_nop_pct_zero_retail(self):
        p = _pos(0, 100)
        assert p.nop_pct_of_retail == 0.0

    def test_hedge_fraction_pct(self):
        p = _pos(1000, 800)
        assert p.hedge_fraction_pct == pytest.approx(80.0)

    def test_direction_long_retail(self):
        p = _pos(1000, 700)
        assert p.direction == ExposureDirection.LONG_RETAIL

    def test_direction_overhedged(self):
        p = _pos(1000, 1300)
        assert p.direction == ExposureDirection.OVERHEDGED

    def test_direction_flat_within_tolerance(self):
        p = _pos(1000, 1030)
        assert p.direction == ExposureDirection.FLAT

    def test_direction_flat_at_tolerance_boundary(self):
        p = _pos(1000, 1050)
        assert p.direction == ExposureDirection.FLAT

    def test_direction_long_retail_just_past_tolerance(self):
        p = _pos(1000, 940)
        assert p.direction == ExposureDirection.LONG_RETAIL

    def test_severity_green(self):
        p = _pos(1000, 900)
        assert p.severity == NOPSeverity.GREEN

    def test_severity_amber(self):
        p = _pos(1000, 700)
        assert p.severity == NOPSeverity.AMBER

    def test_severity_red(self):
        p = _pos(1000, 500)
        assert p.severity == NOPSeverity.RED

    def test_severity_red_overhedged(self):
        p = _pos(1000, 1500)
        assert p.severity == NOPSeverity.RED



class TestNetOpenPositionRegister:
    def _build(self):
        reg = NetOpenPositionRegister()
        reg.record(2024, 1, "electricity", 1000, 700)
        reg.record(2024, 2, "electricity", 1000, 1200)
        reg.record(2024, 1, "gas", 500, 250)
        reg.record(2023, 4, "electricity", 800, 600)
        return reg

    def test_record_returns_position(self):
        reg = NetOpenPositionRegister()
        p = reg.record(2024, 1, "electricity", 1000, 800)
        assert isinstance(p, DeliveryPeriodPosition)
        assert p.retail_commitment_mwh == 1000
        assert p.forward_position_mwh == 800

    def test_all_positions_sorted(self):
        reg = self._build()
        ps = reg.all_positions
        assert len(ps) == 4
        assert ps[0].delivery_year == 2023

    def test_positions_for_year(self):
        reg = self._build()
        ps = reg.positions_for_year(2024)
        assert len(ps) == 3

    def test_positions_for_year_empty(self):
        reg = self._build()
        assert reg.positions_for_year(2099) == []

    def test_positions_for_commodity(self):
        reg = self._build()
        gas = reg.positions_for_commodity("gas")
        assert len(gas) == 1
        assert gas[0].commodity == "gas"

    def test_red_positions(self):
        reg = self._build()
        reds = reg.red_positions
        assert any(p.commodity == "gas" and p.delivery_year == 2024 for p in reds)

    def test_long_retail_positions(self):
        reg = self._build()
        lr = reg.long_retail_positions
        assert all(p.direction == ExposureDirection.LONG_RETAIL for p in lr)

    def test_overhedged_positions(self):
        reg = self._build()
        oh = reg.overhedged_positions
        assert all(p.direction == ExposureDirection.OVERHEDGED for p in oh)

    def test_aggregate_for_year(self):
        reg = self._build()
        agg = reg.aggregate_for_year(2024)
        assert agg["n_periods"] == 3
        assert agg["retail_mwh"] == pytest.approx(2500)
        assert agg["forward_mwh"] == pytest.approx(2150)

    def test_aggregate_nop_mwh(self):
        reg = self._build()
        agg = reg.aggregate_for_year(2024)
        assert agg["nop_mwh"] == pytest.approx(-350)

    def test_aggregate_empty_year(self):
        reg = self._build()
        agg = reg.aggregate_for_year(2099)
        assert agg["n_periods"] == 0
        assert agg["retail_mwh"] == 0.0

    def test_nop_summary_contains_key_info(self):
        reg = self._build()
        s = reg.nop_summary()
        assert "Periods" in s
        assert "RED" in s

    def test_empty_register(self):
        reg = NetOpenPositionRegister()
        assert reg.all_positions == []
        assert reg.red_positions == []
        assert reg.long_retail_positions == []

    def test_constant_thresholds_sensible(self):
        assert 0 < _FLAT_TOLERANCE_PCT < _AMBER_THRESHOLD_PCT < _RED_THRESHOLD_PCT

