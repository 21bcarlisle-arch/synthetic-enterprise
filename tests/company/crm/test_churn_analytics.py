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
