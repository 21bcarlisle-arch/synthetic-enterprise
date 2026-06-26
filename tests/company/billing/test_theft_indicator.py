"""Phase 116: Energy theft indicator tests."""

from company.billing.theft_indicator import classify_anomaly, screen_portfolio


def test_classify_ok():
    result = classify_anomaly(3000, 3500)
    assert result["status"] == "ok"


def test_classify_watch():
    result = classify_anomaly(2000, 3500)  # 57% -> watch
    assert result["status"] == "watch"


def test_classify_investigate():
    result = classify_anomaly(1000, 3500)  # 28% -> investigate
    assert result["status"] == "investigate"


def test_classify_no_data_when_eac_zero():
    result = classify_anomaly(1000, 0)
    assert result["status"] == "no_data"


def test_ratio_is_correct():
    result = classify_anomaly(1000, 4000)
    assert abs(result["ratio"] - 0.25) < 0.01


def test_classify_boundary_exactly_40_percent():
    result = classify_anomaly(1400, 3500)  # 40% -> watch
    assert result["status"] == "watch"


def test_classify_at_65_percent():
    result = classify_anomaly(2275, 3500)  # 65% -> ok
    assert result["status"] == "ok"


def test_screen_portfolio_counts():
    customers = [
        {"customer_id": "C1", "eac_kwh": 3500, "annualised_actual_kwh": 1000},  # investigate
        {"customer_id": "C2", "eac_kwh": 3500, "annualised_actual_kwh": 2000},  # watch
        {"customer_id": "C3", "eac_kwh": 3500, "annualised_actual_kwh": 3000},  # ok
    ]
    s = screen_portfolio(customers)
    assert s["investigate"] == 1
    assert s["watch"] == 1
    assert s["ok"] == 1
    assert s["total"] == 3


def test_screen_results_sorted_by_ratio():
    customers = [
        {"customer_id": "C1", "eac_kwh": 3500, "annualised_actual_kwh": 3000},
        {"customer_id": "C2", "eac_kwh": 3500, "annualised_actual_kwh": 1000},
    ]
    s = screen_portfolio(customers)
    assert s["results"][0]["customer_id"] == "C2"  # lowest ratio first


def test_investigate_message_mentions_ofgem():
    result = classify_anomaly(500, 3500)
    assert "Ofgem" in result["message"]
