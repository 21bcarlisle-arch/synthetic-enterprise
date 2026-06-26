import datetime as dt
import pytest
from company.crm.tariff_notification import (
    NotificationChannel, NotificationStatus, TariffChangeReason,
    TariffNotification, TariffNotificationLog, ADVANCE_NOTICE_DAYS
)


def _make_log() -> TariffNotificationLog:
    log = TariffNotificationLog()
    log.send(
        'N001', 'C001', NotificationChannel.EMAIL,
        dt.date(2022, 9, 1), dt.date(2022, 11, 1),
        TariffChangeReason.MARKET_PRICE_CHANGE,
        28.0, 38.0, 45.0, 55.0
    )
    return log


def test_notice_days():
    log = _make_log()
    n = log.get('N001')
    assert n.notice_days == 61


def test_meets_advance_notice():
    log = _make_log()
    n = log.get('N001')
    assert n.meets_advance_notice


def test_breach_advance_notice():
    log = TariffNotificationLog()
    log.send(
        'N002', 'C002', NotificationChannel.POST,
        dt.date(2022, 10, 1), dt.date(2022, 11, 1),
        TariffChangeReason.PRICE_CAP_CHANGE,
        30.0, 35.0, 45.0, 50.0
    )
    breaches = log.compliance_breaches()
    assert len(breaches) == 1


def test_unit_rate_change_pct():
    log = _make_log()
    n = log.get('N001')
    change = n.unit_rate_change_pct
    assert change == pytest.approx((38.0 - 28.0) / 28.0 * 100, rel=0.01)


def test_is_price_increase():
    log = _make_log()
    n = log.get('N001')
    assert n.is_price_increase


def test_mark_confirmed():
    log = _make_log()
    log.mark_confirmed('N001')
    n = log.get('N001')
    assert n.status == NotificationStatus.CONFIRMED_READ


def test_price_increases():
    log = _make_log()
    increases = log.price_increases(2022)
    assert len(increases) == 1


def test_notification_summary():
    log = _make_log()
    s = log.notification_summary(2022)
    assert s['total_sent'] == 1
    assert s['compliance_breaches'] == 0
    assert s['price_increases'] == 1
    assert 'email' in s['channels']
