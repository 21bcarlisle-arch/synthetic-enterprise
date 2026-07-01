"""Phase MT: I&C Triad Demand Curtailment tests.

Verifies that build_triad_alert_set identifies correct Triad risk windows
and that make_triad_aware_shape_fn applies 25% demand reduction during
those windows. Also covers get_active_alerts on TriadNotificationBook.
"""
import pytest
from simulation.triad import (
    _IC_TRIAD_RESPONSE_REDUCTION,
    _TRIAD_ALERT_SSP_THRESHOLD,
    _TRIAD_RISK_PERIODS,
    _TRIAD_WINDOW_MONTHS,
    build_triad_alert_set,
    make_triad_aware_shape_fn,
)
from company.market.triad_notification_book import (
    AlertStatus,
    CustomerTriadProfile,
    TriadAlert,
    TriadNotificationBook,
)


# ---------- helpers ----------

def _rec(date_str: str, sp: int, ssp: float) -> dict:
    return {"settlementDate": date_str, "settlementPeriod": sp, "systemSellPrice": ssp}


def _flat_shape_fn(value: float):
    """Returns a shape function where every period returns `value`."""
    def fn(date_str: str) -> list[float]:
        return [value] * 48
    return fn


# ---------- build_triad_alert_set ----------

def test_alert_ssp_threshold_is_80():
    assert _TRIAD_ALERT_SSP_THRESHOLD == 80.0


def test_ic_response_reduction_in_range():
    assert 0.20 <= _IC_TRIAD_RESPONSE_REDUCTION <= 0.30


def test_triad_risk_periods_are_33_to_39():
    assert _TRIAD_RISK_PERIODS == frozenset(range(33, 40))


def test_build_alert_set_includes_high_ssp_risk_period():
    records = [_rec("2022-01-15", 35, 120.0)]  # Triad season, risk period, high SSP
    result = build_triad_alert_set(records)
    assert ("2022-01-15", 35) in result


def test_build_alert_set_excludes_non_triad_month():
    records = [_rec("2022-07-15", 35, 150.0)]  # July = not Triad season
    result = build_triad_alert_set(records)
    assert ("2022-07-15", 35) not in result


def test_build_alert_set_excludes_non_risk_period():
    records = [_rec("2022-01-15", 1, 150.0)]  # SP1 = 00:00-00:30, not risk period
    result = build_triad_alert_set(records)
    assert ("2022-01-15", 1) not in result


def test_build_alert_set_excludes_low_ssp():
    records = [_rec("2022-01-15", 35, 50.0)]  # SSP below threshold
    result = build_triad_alert_set(records)
    assert ("2022-01-15", 35) not in result


def test_build_alert_set_threshold_boundary_included():
    records = [_rec("2022-01-15", 35, 80.0)]  # exactly at threshold
    result = build_triad_alert_set(records)
    assert ("2022-01-15", 35) in result


def test_build_alert_set_threshold_boundary_excluded():
    records = [_rec("2022-01-15", 35, 79.99)]  # just below
    result = build_triad_alert_set(records)
    assert ("2022-01-15", 35) not in result


def test_build_alert_set_november_included():
    records = [_rec("2021-11-10", 36, 90.0)]
    result = build_triad_alert_set(records)
    assert ("2021-11-10", 36) in result


def test_build_alert_set_february_included():
    records = [_rec("2022-02-20", 38, 100.0)]
    result = build_triad_alert_set(records)
    assert ("2022-02-20", 38) in result


def test_build_alert_set_returns_frozenset():
    result = build_triad_alert_set([])
    assert isinstance(result, frozenset)


def test_build_alert_set_empty_records():
    assert build_triad_alert_set([]) == frozenset()


def test_build_alert_set_multiple_records():
    records = [
        _rec("2022-01-15", 35, 120.0),  # included
        _rec("2022-01-15", 36, 95.0),   # included
        _rec("2022-01-15", 32, 95.0),   # excluded: SP 32 not risk period
        _rec("2022-07-15", 35, 120.0),  # excluded: not Triad season
    ]
    result = build_triad_alert_set(records)
    assert ("2022-01-15", 35) in result
    assert ("2022-01-15", 36) in result
    assert ("2022-01-15", 32) not in result
    assert ("2022-07-15", 35) not in result


# ---------- make_triad_aware_shape_fn ----------

def test_curtailment_applies_to_alert_period():
    alert_set = frozenset({("2022-01-15", 35)})
    fn = make_triad_aware_shape_fn(_flat_shape_fn(100.0), alert_set)
    shape = fn("2022-01-15")
    # Period 35 (index 34) should be reduced by 25%
    assert shape[34] == pytest.approx(75.0)


def test_non_alert_period_unchanged():
    alert_set = frozenset({("2022-01-15", 35)})
    fn = make_triad_aware_shape_fn(_flat_shape_fn(100.0), alert_set)
    shape = fn("2022-01-15")
    # Period 1 (index 0) not in alert set — unchanged
    assert shape[0] == pytest.approx(100.0)


def test_non_alert_date_unchanged():
    alert_set = frozenset({("2022-01-15", 35)})
    fn = make_triad_aware_shape_fn(_flat_shape_fn(100.0), alert_set)
    shape = fn("2022-01-16")  # different date
    assert all(v == pytest.approx(100.0) for v in shape)


def test_curtailment_returns_48_periods():
    alert_set = frozenset({("2022-01-15", 35)})
    fn = make_triad_aware_shape_fn(_flat_shape_fn(100.0), alert_set)
    assert len(fn("2022-01-15")) == 48


def test_curtailment_fraction_is_25pct():
    """Demand reduction is exactly 25% (within 20-30% range)."""
    alert_set = frozenset({("2022-01-15", 33)})
    fn = make_triad_aware_shape_fn(_flat_shape_fn(200.0), alert_set)
    shape = fn("2022-01-15")
    assert shape[32] == pytest.approx(150.0)  # 200 * 0.75 = 150


def test_empty_alert_set_no_reduction():
    fn = make_triad_aware_shape_fn(_flat_shape_fn(100.0), frozenset())
    shape = fn("2022-01-15")
    assert all(v == pytest.approx(100.0) for v in shape)


def test_custom_reduction_fraction():
    alert_set = frozenset({("2022-01-15", 35)})
    fn = make_triad_aware_shape_fn(_flat_shape_fn(100.0), alert_set, reduction=0.30)
    shape = fn("2022-01-15")
    assert shape[34] == pytest.approx(70.0)  # 100 * 0.70


# ---------- get_active_alerts on TriadNotificationBook ----------

def _make_book_with_alert(alert_date: str, sp: int, status: AlertStatus) -> TriadNotificationBook:
    book = TriadNotificationBook()
    profile = CustomerTriadProfile(
        account_id="C_IC1", annual_kwh=1_000_000, peak_demand_kw=500.0
    )
    book.enrol(profile)
    alert = TriadAlert(
        account_id="C_IC1",
        alert_date=alert_date,
        settlement_period=sp,
        estimated_demand_kw=500.0,
        status=status,
    )
    book.issue_alert(alert)
    return book


def test_get_active_alerts_returns_matching():
    book = _make_book_with_alert("2022-01-15", 35, AlertStatus.ISSUED)
    alerts = book.get_active_alerts("2022-01-15", 35)
    assert len(alerts) == 1
    assert alerts[0].account_id == "C_IC1"


def test_get_active_alerts_empty_no_match():
    book = _make_book_with_alert("2022-01-15", 35, AlertStatus.ISSUED)
    alerts = book.get_active_alerts("2022-01-16", 35)
    assert alerts == []


def test_get_active_alerts_wrong_period():
    book = _make_book_with_alert("2022-01-15", 35, AlertStatus.ISSUED)
    alerts = book.get_active_alerts("2022-01-15", 36)
    assert alerts == []


def test_get_active_alerts_responded_status():
    book = _make_book_with_alert("2022-01-15", 35, AlertStatus.RESPONDED)
    alerts = book.get_active_alerts("2022-01-15", 35)
    assert len(alerts) == 1
    assert alerts[0].status == AlertStatus.RESPONDED


def test_get_active_alerts_no_response_status():
    book = _make_book_with_alert("2022-01-15", 35, AlertStatus.NO_RESPONSE)
    alerts = book.get_active_alerts("2022-01-15", 35)
    assert len(alerts) == 1


def test_get_active_alerts_empty_book():
    book = TriadNotificationBook()
    assert book.get_active_alerts("2022-01-15", 35) == []
