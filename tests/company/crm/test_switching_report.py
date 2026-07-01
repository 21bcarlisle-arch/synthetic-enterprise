import datetime as dt
import pytest
from company.crm.switching_report import (
    SwitchDirection, SwitchReason, SwitchRecord, SwitchingReport
)


def _make_report() -> SwitchingReport:
    r = SwitchingReport('BrightEnergy')
    r.record('S001', 'C001', dt.date(2022, 3, 1), SwitchDirection.GAIN,
              'OldCo', 3000.0, SwitchReason.PRICE)
    r.record('S002', 'C002', dt.date(2022, 4, 15), SwitchDirection.GAIN,
              'BigSupplier', 5000.0, SwitchReason.GREEN_TARIFF)
    r.record('S003', 'C003', dt.date(2022, 5, 1), SwitchDirection.LOSS,
              'Octopus', 2500.0, SwitchReason.PRICE)
    return r


def test_gains_count():
    r = _make_report()
    assert len(r.gains(2022)) == 2


def test_losses_count():
    r = _make_report()
    assert len(r.losses(2022)) == 1


def test_net_customer_movement():
    r = _make_report()
    assert r.net_customer_movement(2022) == 1


def test_net_mwh_movement():
    r = _make_report()
    net = r.net_mwh_movement(2022)
    assert net == pytest.approx((3000.0 + 5000.0 - 2500.0) / 1000, rel=0.01)


def test_churn_rate():
    r = _make_report()
    rate = r.churn_rate_pct(2022, 100)
    assert rate == pytest.approx(1.0)


def test_is_gain():
    r = _make_report()
    gain = r.gains(2022)[0]
    assert gain.is_gain


def test_loss_reasons():
    r = _make_report()
    reasons = r.loss_reasons(2022)
    assert reasons.get('price', 0) == 1


def test_top_gaining_from():
    r = SwitchingReport('TestSupplier')
    r.record('G001', 'C01', dt.date(2022, 1, 1), SwitchDirection.GAIN, 'BigCo', 3000.0)
    r.record('G002', 'C02', dt.date(2022, 1, 2), SwitchDirection.GAIN, 'BigCo', 2000.0)
    r.record('G003', 'C03', dt.date(2022, 1, 3), SwitchDirection.GAIN, 'SmallCo', 1000.0)
    assert r.top_gaining_from(2022) == 'BigCo'


def test_switching_summary():
    r = _make_report()
    s = r.switching_summary(2022, 50)
    assert s['gains'] == 2
    assert s['losses'] == 1
    assert s['net_movement'] == 1
    assert 'loss_reasons' in s


# --- Phase KS depth tests ---

def test_switch_id_stored():
    r = _make_report()
    gain = r.gains(2022)[0]
    assert gain.switch_id == 'S001'


def test_customer_id_stored():
    r = _make_report()
    gain = r.gains(2022)[0]
    assert gain.customer_id == 'C001'


def test_direction_stored():
    r = _make_report()
    loss = r.losses(2022)[0]
    assert loss.direction == SwitchDirection.LOSS


def test_switch_date_stored():
    r = _make_report()
    gain = r.gains(2022)[0]
    assert gain.switch_date == dt.date(2022, 3, 1)


def test_annual_kwh_stored():
    r = _make_report()
    gain = r.gains(2022)[0]
    assert gain.annual_kwh == pytest.approx(3000.0)


def test_reason_stored():
    r = _make_report()
    gain = r.gains(2022)[0]
    assert gain.reason == SwitchReason.PRICE


def test_gains_empty_wrong_year():
    r = _make_report()
    assert r.gains(2021) == []


def test_losses_empty_wrong_year():
    r = _make_report()
    assert r.losses(2021) == []


def test_net_zero_equal_gains_losses():
    r = SwitchingReport('TestCo')
    r.record('G1', 'C1', dt.date(2022,1,1), SwitchDirection.GAIN, 'A', 3000.0, SwitchReason.PRICE)
    r.record('L1', 'C2', dt.date(2022,2,1), SwitchDirection.LOSS, 'B', 3000.0, SwitchReason.PRICE)
    assert r.net_customer_movement(2022) == 0


def test_churn_rate_zero_no_losses():
    r = SwitchingReport('TestCo')
    r.record('G1', 'C1', dt.date(2022,1,1), SwitchDirection.GAIN, 'A', 3000.0)
    assert r.churn_rate_pct(2022, 100) == pytest.approx(0.0)
