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
