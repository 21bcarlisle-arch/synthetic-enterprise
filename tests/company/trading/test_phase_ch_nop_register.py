"""Phase CH: Net Open Position Register tests."""
import pytest
from company.trading.net_open_position_register import (
    NetOpenPositionRegister, DeliveryPeriodPosition,
    ExposureDirection, NOPSeverity
)


def _reg():
    return NetOpenPositionRegister()


def _pos(retail, forward, yr=2022, q=1, commodity="electricity"):
    r = _reg()
    p = r.record(yr, q, commodity, retail, forward)
    return r, p


# 1. NOP positive when overhedged
def test_nop_positive_overhedged():
    _, p = _pos(retail=1000, forward=1200)
    assert p.net_open_position_mwh == 200


# 2. NOP negative when underhedged
def test_nop_negative_underhedged():
    _, p = _pos(retail=1000, forward=600)
    assert p.net_open_position_mwh == -400


# 3. Hedge fraction correct
def test_hedge_fraction():
    _, p = _pos(retail=1000, forward=750)
    assert abs(p.hedge_fraction_pct - 75.0) < 0.01


# 4. Direction FLAT when within tolerance
def test_direction_flat():
    _, p = _pos(retail=1000, forward=1030)  # +3% overhedged
    assert p.direction == ExposureDirection.FLAT


# 5. Direction LONG_RETAIL when retail > forwards
def test_direction_long_retail():
    _, p = _pos(retail=1000, forward=500)  # -50%
    assert p.direction == ExposureDirection.LONG_RETAIL


# 6. Direction OVERHEDGED when forwards > retail + tolerance
def test_direction_overhedged():
    _, p = _pos(retail=1000, forward=1300)  # +30%
    assert p.direction == ExposureDirection.OVERHEDGED


# 7. RED severity when absolute NOP > 40%
def test_severity_red():
    _, p = _pos(retail=1000, forward=500)  # -50% -> RED
    assert p.severity == NOPSeverity.RED


# 8. AMBER severity when 20-40% absolute NOP
def test_severity_amber():
    _, p = _pos(retail=1000, forward=750)  # -25% -> AMBER
    assert p.severity == NOPSeverity.AMBER


# 9. GREEN severity when <20% absolute NOP
def test_severity_green():
    _, p = _pos(retail=1000, forward=900)  # -10% -> GREEN
    assert p.severity == NOPSeverity.GREEN


# 10. red_positions filters correctly
def test_red_positions():
    r = _reg()
    r.record(2022, 1, "electricity", 1000, 500)   # RED (-50%)
    r.record(2022, 2, "electricity", 1000, 950)   # GREEN (-5%)
    assert len(r.red_positions) == 1


# 11. aggregate_for_year correct
def test_aggregate_for_year():
    r = _reg()
    r.record(2022, 1, "electricity", 500, 300)
    r.record(2022, 2, "electricity", 600, 400)
    agg = r.aggregate_for_year(2022)
    assert agg["retail_mwh"] == 1100
    assert agg["forward_mwh"] == 700
    assert abs(agg["nop_mwh"] - (-400)) < 0.01


# 12. nop_summary contains key fields
def test_nop_summary():
    r = _reg()
    r.record(2022, 1, "electricity", 1000, 500)
    summary = r.nop_summary()
    assert "Net Open Position" in summary
    assert "RED" in summary


# --- Phase MF depth tests ---

def test_delivery_year_stored():
    _, p = _pos(100, 100, yr=2023)
    assert p.delivery_year == 2023


def test_delivery_quarter_stored():
    _, p = _pos(100, 100, q=3)
    assert p.delivery_quarter == 3


def test_commodity_stored():
    _, p = _pos(100, 100, commodity="gas")
    assert p.commodity == "gas"


def test_retail_commitment_mwh_stored():
    _, p = _pos(500, 400)
    assert p.retail_commitment_mwh == pytest.approx(500.0)


def test_forward_position_mwh_stored():
    _, p = _pos(500, 400)
    assert p.forward_position_mwh == pytest.approx(400.0)


def test_record_returns_delivery_period_position():
    reg = _reg()
    result = reg.record(2022, 1, "electricity", 1000, 900)
    assert isinstance(result, DeliveryPeriodPosition)


def test_positions_for_year_filter():
    reg = _reg()
    reg.record(2021, 1, "electricity", 1000, 900)
    reg.record(2022, 2, "gas", 800, 800)
    assert len(reg.positions_for_year(2021)) == 1
    assert reg.positions_for_year(2021)[0].delivery_year == 2021


def test_positions_for_commodity_filter():
    reg = _reg()
    reg.record(2022, 1, "electricity", 1000, 900)
    reg.record(2022, 2, "gas", 800, 800)
    gas = reg.positions_for_commodity("gas")
    assert len(gas) == 1
    assert gas[0].commodity == "gas"


def test_long_retail_positions():
    reg = _reg()
    reg.record(2022, 1, "electricity", 1000, 500)  # LONG_RETAIL (underhedged 50%)
    reg.record(2022, 2, "gas", 800, 850)           # OVERHEDGED
    assert len(reg.long_retail_positions) == 1
    assert reg.long_retail_positions[0].direction == ExposureDirection.LONG_RETAIL


def test_overhedged_positions():
    reg = _reg()
    reg.record(2022, 1, "electricity", 500, 700)   # OVERHEDGED 40%
    reg.record(2022, 2, "gas", 1000, 500)           # LONG_RETAIL
    assert len(reg.overhedged_positions) == 1
    assert reg.overhedged_positions[0].direction == ExposureDirection.OVERHEDGED
