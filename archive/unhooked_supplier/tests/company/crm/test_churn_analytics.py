import pytest
"""Phase 124: Churn waterfall and reason code analysis tests."""

from company.crm.churn_analytics import ChurnEvent, ChurnAnalytics


def _analytics():
    ca = ChurnAnalytics()
    ca.record(ChurnEvent("C1", "loss", 2024, reason="price"))
    ca.record(ChurnEvent("C2", "loss", 2024, reason="price"))
    ca.record(ChurnEvent("C3", "loss", 2024, reason="service"))
    ca.record(ChurnEvent("C4", "gain", 2024))
    ca.record(ChurnEvent("C5", "gain", 2024))
    ca.record(ChurnEvent("C6", "loss", 2023, reason="moving_home"))
    return ca


def test_gains_by_year():
    ca = _analytics()
    assert len(ca.gains_by_year(2024)) == 2


def test_losses_by_year():
    ca = _analytics()
    assert len(ca.losses_by_year(2024)) == 3


def test_reason_breakdown_sorted():
    ca = _analytics()
    rb = ca.reason_breakdown(2024)
    keys = list(rb.keys())
    assert keys[0] == "price"  # 2 price losses > 1 service
    assert rb["price"] == 2
    assert rb["service"] == 1


def test_waterfall_closing_book():
    ca = _analytics()
    wf = ca.waterfall(2024, 10)
    assert wf.closing_book == 10 + 2 - 3  # 9


def test_waterfall_churn_rate():
    ca = _analytics()
    wf = ca.waterfall(2024, 10)
    assert abs(wf.churn_rate - 0.3) < 0.001  # 3 losses / 10


def test_waterfall_growth_rate_negative():
    ca = _analytics()
    wf = ca.waterfall(2024, 10)
    assert wf.growth_rate < 0  # net loss year


def test_retention_rate_zero_when_none_attempted():
    ca = _analytics()
    assert ca.retention_rate(2024) == 0.0


def test_retention_rate_with_successes():
    ca = ChurnAnalytics()
    ca.record(ChurnEvent("C1", "loss", 2024, retention_attempted=True, retention_succeeded=True))
    ca.record(ChurnEvent("C2", "loss", 2024, retention_attempted=True, retention_succeeded=False))
    ca.record(ChurnEvent("C3", "loss", 2024, retention_attempted=False))
    rate = ca.retention_rate(2024)
    assert abs(rate - 0.5) < 0.001  # 1 of 2 attempted


def test_summary_structure():
    ca = _analytics()
    s = ca.summary(2024, 10)
    for key in ("opening_book", "gains", "losses", "closing_book", "churn_rate_pct", "reason_breakdown"):
        assert key in s


def test_prior_year_losses_not_counted():
    ca = _analytics()
    assert len(ca.losses_by_year(2023)) == 1  # only the moving_home 2023 event
    assert len(ca.losses_by_year(2024)) == 3  # not contaminated by 2023


# --- Phase LA depth tests ---

def test_churn_event_customer_id():
    e = ChurnEvent('C_LA', 'loss', 2024, reason='price')
    assert e.customer_id == 'C_LA'


def test_churn_event_direction():
    e = ChurnEvent('C1', 'gain', 2024)
    assert e.direction == 'gain'


def test_churn_event_year():
    e = ChurnEvent('C1', 'loss', 2023)
    assert e.year == 2023


def test_churn_event_reason_stored():
    e = ChurnEvent('C1', 'loss', 2024, reason='service')
    assert e.reason == 'service'


def test_churn_event_retention_not_attempted_default():
    e = ChurnEvent('C1', 'loss', 2024)
    assert e.retention_attempted is False


def test_waterfall_closing_book():
    from company.crm.churn_analytics import ChurnWaterfall
    w = ChurnWaterfall(year=2024, opening_book=1000, gains=50, losses=80)
    assert w.closing_book == 970


def test_waterfall_net_change():
    from company.crm.churn_analytics import ChurnWaterfall
    w = ChurnWaterfall(year=2024, opening_book=1000, gains=50, losses=80)
    assert w.net_change == -30


def test_waterfall_churn_rate_formula():
    from company.crm.churn_analytics import ChurnWaterfall
    w = ChurnWaterfall(year=2024, opening_book=1000, gains=50, losses=100)
    assert w.churn_rate == pytest.approx(0.1)


def test_analytics_record_returns_none():
    import pytest
    ca = ChurnAnalytics()
    result = ca.record(ChurnEvent('C1', 'loss', 2024))
    assert result is None


def test_losses_by_year_unknown_year_empty():
    ca = _analytics()
    assert ca.losses_by_year(1999) == []
