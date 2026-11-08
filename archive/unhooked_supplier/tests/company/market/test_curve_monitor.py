import pytest
"""Phase 138: Forward curve anomaly detection tests."""

from company.market.curve_monitor import PricePoint, ForwardCurveMonitor


def _stable_series(n=20, base=50.0):
    return [PricePoint(f"2024-{i:03}", base + (i % 3 - 1) * 0.5) for i in range(n)]


def test_insufficient_history_returns_none():
    m = ForwardCurveMonitor(window=30)
    result = m.add(PricePoint("2024-001", 50.0))
    assert result is None


def test_stable_series_no_anomaly():
    m = ForwardCurveMonitor(window=20)
    points = _stable_series(20)
    results = m.screen_series(points)
    # After 10+ points, should produce results — all should be normal
    severities = [r.severity for r in results]
    assert all(s == "normal" for s in severities)


def test_spike_detected_as_alert():
    m = ForwardCurveMonitor(window=20)
    stable = _stable_series(20)
    results = m.screen_series(stable)
    # Add a massive spike
    r = m.add(PricePoint("spike", 500.0))  # 10x normal price
    assert r is not None
    assert r.severity in ("alert", "critical")


def test_critical_spike():
    m = ForwardCurveMonitor(window=20)
    m.screen_series(_stable_series(20))
    r = m.add(PricePoint("crisis", 9999.0))
    assert r is not None
    assert r.severity == "critical"


def test_negative_spike_also_detected():
    m = ForwardCurveMonitor(window=20)
    m.screen_series(_stable_series(20))
    r = m.add(PricePoint("crash", -100.0))
    assert r is not None
    assert r.severity in ("alert", "critical", "watch")


def test_z_score_returned():
    m = ForwardCurveMonitor(window=20)
    results = m.screen_series(_stable_series(20))
    for r in results:
        assert isinstance(r.z_score, float)


def test_mean_std_populated():
    m = ForwardCurveMonitor(window=20)
    results = m.screen_series(_stable_series(20))
    for r in results:
        assert r.mean_gbp_mwh > 0
        assert r.std_gbp_mwh >= 0


def test_summary_structure():
    m = ForwardCurveMonitor(window=20)
    results = m.screen_series(_stable_series(20))
    s = m.summary(results)
    for k in ("total", "critical", "alert", "watch", "normal"):
        assert k in s


def test_empty_summary():
    m = ForwardCurveMonitor()
    s = m.summary([])
    assert s["total"] == 0


# --- Phase KW depth tests ---

def _result_after_stable(n=20, base=50.0, spike=None):
    m = ForwardCurveMonitor(window=n)
    for i in range(n - 1):
        m.add(PricePoint(f"2024-{i:03}", base))
    final_price = spike if spike is not None else base
    return m.add(PricePoint(f"2024-{n:03}", final_price))


def test_period_stored_in_result():
    r = _result_after_stable()
    assert r is not None
    assert '2024' in r.period


def test_price_stored_in_result():
    r = _result_after_stable(base=50.0)
    assert r.price_gbp_mwh == pytest.approx(50.0)


def test_z_score_is_float():
    r = _result_after_stable()
    assert isinstance(r.z_score, float)


def test_mean_non_negative():
    r = _result_after_stable(base=60.0)
    assert r.mean_gbp_mwh >= 0.0


def test_std_positive():
    r = _result_after_stable(base=50.0, spike=200.0)
    assert r.std_gbp_mwh > 0.0


def test_severity_is_string():
    r = _result_after_stable()
    assert isinstance(r.severity, str)


def test_message_is_string():
    r = _result_after_stable()
    assert isinstance(r.message, str)


def test_z_warn_constant():
    from company.market.curve_monitor import _Z_WARN
    assert _Z_WARN == pytest.approx(2.5)


def test_z_critical_constant():
    from company.market.curve_monitor import _Z_CRITICAL
    assert _Z_CRITICAL == pytest.approx(5.0)


def test_summary_total_matches_added():
    m = ForwardCurveMonitor(window=10)
    series = _stable_series(20)
    results = [m.add(p) for p in series]
    valid = [r for r in results if r is not None]
    s = m.summary(valid)
    assert s["total"] == len(valid)
