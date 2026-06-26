"""Phase 134: Tariff change notification tests."""

from company.billing.tariff_change_log import TariffChangeNotice, TariffChangeLog


def _notice(change_type="svt_price_change", notif="2024-01-01", effective="2024-02-15",
            old=28.0, new=32.0, ack=False):
    return TariffChangeNotice(
        notice_id="TCN-001",
        customer_id="C1",
        change_type=change_type,
        notification_date=notif,
        effective_date=effective,
        old_unit_rate_p_kwh=old,
        new_unit_rate_p_kwh=new,
        acknowledged=ack,
    )


def test_notice_days_calculation():
    n = _notice(notif="2024-01-01", effective="2024-02-10")
    assert n.notice_days == 40


def test_svt_compliant():
    n = _notice(notif="2024-01-01", effective="2024-02-01")  # 31 days ≥ 30
    assert n.is_compliant is True


def test_svt_non_compliant():
    n = _notice(notif="2024-01-01", effective="2024-01-20")  # 19 days < 30
    assert n.is_compliant is False


def test_fixed_term_requires_42_days():
    n = _notice(change_type="fixed_term_expiry", notif="2024-01-01", effective="2024-02-10")
    assert n.required_notice_days == 42
    assert n.is_compliant is False   # only 40 days


def test_rate_change_pct():
    n = _notice(old=28.0, new=32.0)
    assert abs(n.rate_change_pct - 14.3) < 0.1


def test_record_and_retrieve():
    log = TariffChangeLog()
    log.record(_notice())
    assert len(log.for_customer("C1")) == 1


def test_non_compliant_filter():
    log = TariffChangeLog()
    log.record(_notice(notif="2024-01-01", effective="2024-01-20"))  # non-compliant
    log.record(_notice(notif="2024-01-01", effective="2024-02-15"))  # compliant
    assert len(log.non_compliant()) == 1


def test_pending_effective():
    log = TariffChangeLog()
    log.record(_notice(effective="2024-06-01"))
    assert len(log.pending_effective("2024-01-01")) == 1
    assert len(log.pending_effective("2024-07-01")) == 0


def test_summary_compliance_rate():
    log = TariffChangeLog()
    log.record(_notice(notif="2024-01-01", effective="2024-02-15"))  # compliant
    log.record(_notice(notif="2024-01-01", effective="2024-01-20"))  # non-compliant
    s = log.summary()
    assert s["total"] == 2
    assert s["non_compliant"] == 1
    assert s["compliance_rate_pct"] == 50.0
