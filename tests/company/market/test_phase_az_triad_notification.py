"""Phase AZ: Triad Notification Book tests."""
import pytest
from datetime import date
from company.market.triad_notification_book import (
    TriadNotificationBook, CustomerTriadProfile, TriadAlert, AlertStatus,
    TriadSavingsRecord, _TNUOS_TRIAD_RATE_GBP_PER_KW,
)


def _ic_profile(cid="C_IC1", kwh=1_200_000, peak_kw=300.0, zone="midlands", enrolled=True):
    return CustomerTriadProfile(
        account_id=cid, annual_kwh=kwh, peak_demand_kw=peak_kw, zone=zone, is_enrolled=enrolled
    )


def _alert(cid="C_IC1", d="2022-01-15", sp=35, demand_kw=280.0, status=AlertStatus.RESPONDED, confirmed=True):
    return TriadAlert(
        account_id=cid, alert_date=d, settlement_period=sp,
        estimated_demand_kw=demand_kw, status=status, confirmed_triad=confirmed
    )


# 1. Enrolment
def test_enrol_adds_profile():
    book = TriadNotificationBook()
    p = book.enrol(_ic_profile())
    assert "C_IC1" in [a.account_id for a in book.enrolled_accounts()]


# 2. Issue alert requires enrolled account
def test_issue_alert_unenrolled_raises():
    book = TriadNotificationBook()
    with pytest.raises(KeyError):
        book.issue_alert(_alert())


# 3. Issue alert unenrolled profile raises ValueError
def test_issue_alert_not_enrolled_raises():
    book = TriadNotificationBook()
    book.enrol(_ic_profile(enrolled=False))
    with pytest.raises(ValueError):
        book.issue_alert(_alert())


# 4. Alert demand reduction = 70% when responded
def test_responded_alert_reduces_demand():
    a = _alert(status=AlertStatus.RESPONDED, demand_kw=200.0)
    assert abs(a.demand_reduction_kw - 140.0) < 0.01


# 5. Alert with no_response has zero reduction
def test_no_response_zero_reduction():
    a = _alert(status=AlertStatus.NO_RESPONSE, demand_kw=200.0)
    assert a.demand_reduction_kw == 0.0


# 6. Triad season detection
def test_triad_season_months():
    assert TriadNotificationBook.is_triad_season(date(2022, 11, 15))
    assert TriadNotificationBook.is_triad_season(date(2022, 1, 10))
    assert not TriadNotificationBook.is_triad_season(date(2022, 6, 15))


# 7. Triad risk period detection (SP 33-39)
def test_triad_risk_periods():
    assert TriadNotificationBook.is_triad_risk_period(35)
    assert not TriadNotificationBook.is_triad_risk_period(25)


# 8. savings_for_account_year computes correctly
def test_savings_for_account_year():
    book = TriadNotificationBook()
    book.enrol(_ic_profile(peak_kw=300.0))
    book.issue_alert(_alert(d="2022-01-15", demand_kw=300.0, status=AlertStatus.RESPONDED))
    rec = book.savings_for_account_year("C_IC1", 2022)
    rate = _TNUOS_TRIAD_RATE_GBP_PER_KW[2022]
    expected_saving = round(300.0 * 0.70 * rate, 2)
    assert abs(rec.estimated_saving_gbp - expected_saving) < 0.01
    assert rec.alerts_issued == 1
    assert rec.alerts_responded == 1


# 9. Response rate percentage
def test_response_rate_pct():
    book = TriadNotificationBook()
    book.enrol(_ic_profile())
    book.issue_alert(_alert(d="2022-01-15", status=AlertStatus.RESPONDED))
    book.issue_alert(_alert(d="2022-02-10", status=AlertStatus.NO_RESPONSE))
    rec = book.savings_for_account_year("C_IC1", 2022)
    assert rec.response_rate_pct == 50.0


# 10. Full charge without alerts
def test_full_triad_charge_without_alerts():
    book = TriadNotificationBook()
    book.enrol(_ic_profile(peak_kw=250.0))
    rec = book.savings_for_account_year("C_IC1", 2022)
    rate = _TNUOS_TRIAD_RATE_GBP_PER_KW[2022]
    expected = round(250.0 * rate, 2)
    assert abs(rec.full_triad_charge_gbp - expected) < 0.01
    assert rec.estimated_saving_gbp == 0.0


# 11. Portfolio total saving sums correctly
def test_total_portfolio_saving_gbp():
    book = TriadNotificationBook()
    book.enrol(_ic_profile("C_IC1", peak_kw=300.0))
    book.enrol(_ic_profile("C_IC2", peak_kw=200.0))
    book.issue_alert(_alert("C_IC1", d="2022-01-15", demand_kw=300.0, status=AlertStatus.RESPONDED))
    book.issue_alert(_alert("C_IC2", d="2022-01-15", demand_kw=200.0, status=AlertStatus.RESPONDED))
    total = book.total_portfolio_saving_gbp(2022)
    rate = _TNUOS_TRIAD_RATE_GBP_PER_KW[2022]
    expected = round((300.0 * 0.70 + 200.0 * 0.70) * rate, 2)
    assert abs(total - expected) < 0.01


# 12. Confirmed Triad in summary
def test_confirmed_triad_in_summary():
    book = TriadNotificationBook()
    book.enrol(_ic_profile())
    book.issue_alert(_alert(confirmed=True))
    summary = book.triad_notification_summary()
    assert "Confirmed Triad hits" in summary
    assert "1" in summary


# 13. saving_pct derived correctly
def test_saving_pct():
    book = TriadNotificationBook()
    book.enrol(_ic_profile(peak_kw=200.0))
    book.issue_alert(_alert(demand_kw=200.0, status=AlertStatus.RESPONDED))
    rec = book.savings_for_account_year("C_IC1", 2022)
    assert abs(rec.saving_pct - 70.0) < 0.1


# 14. Unknown account in savings_for_account_year raises KeyError
def test_unknown_account_raises():
    book = TriadNotificationBook()
    with pytest.raises(KeyError):
        book.savings_for_account_year("UNKNOWN", 2022)


# 15. High-value calibration: C_IC3 at 1000 kW demand
def test_high_demand_customer_calibration():
    book = TriadNotificationBook()
    book.enrol(_ic_profile("C_IC3", peak_kw=1000.0))
    book.issue_alert(TriadAlert(
        account_id="C_IC3", alert_date="2022-01-20", settlement_period=36,
        estimated_demand_kw=1000.0, status=AlertStatus.RESPONDED, confirmed_triad=True
    ))
    rec = book.savings_for_account_year("C_IC3", 2022)
    rate = _TNUOS_TRIAD_RATE_GBP_PER_KW[2022]
    # 1000 kW × 70% × £60.40/kW = £42,280
    expected = round(1000.0 * 0.70 * rate, 2)
    assert abs(rec.estimated_saving_gbp - expected) < 1.0
    assert rec.estimated_saving_gbp > 40_000
