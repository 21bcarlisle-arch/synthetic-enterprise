"""Phase 120: Wholesale risk limits and position governor tests."""

from company.trading.risk_limits import RiskGovernor, RiskLimit


def _governor():
    g = RiskGovernor()
    g.set_limit(RiskLimit("max_open_position_mwh", 500.0, "MWh", 2025))
    g.set_limit(RiskLimit("max_single_contract_mwh", 100.0, "MWh", 2025))
    g.set_limit(RiskLimit("var_limit_gbp", 50_000.0, "GBP", 2025))
    g.set_limit(RiskLimit("stop_loss_gbp", 20_000.0, "GBP", 2025))
    return g


def test_check_ok():
    g = _governor()
    result = g.check("max_open_position_mwh", 100.0)
    assert result.status == "OK"


def test_check_warning():
    g = _governor()
    result = g.check("max_open_position_mwh", 420.0)  # 84% of 500
    assert result.status == "WARNING"


def test_check_breach():
    g = _governor()
    result = g.check("max_open_position_mwh", 600.0)  # 120%
    assert result.status == "BREACH"


def test_utilisation_calculated():
    g = _governor()
    result = g.check("max_open_position_mwh", 250.0)
    assert abs(result.utilisation_pct - 50.0) < 0.1


def test_no_limit_returns_ok():
    g = RiskGovernor()
    result = g.check("nonexistent_limit", 999.0)
    assert result.status == "OK"


def test_check_all():
    g = _governor()
    current = {
        "max_open_position_mwh": 100.0,
        "max_single_contract_mwh": 50.0,
        "var_limit_gbp": 30_000.0,  # 60% of 50k -> OK
        "stop_loss_gbp": 5_000.0,
    }
    results = g.check_all(current)
    assert len(results) == 4
    assert all(r.status == "OK" for r in results)


def test_governance_summary_breach():
    g = _governor()
    current = {"max_open_position_mwh": 600.0}
    s = g.governance_summary(current)
    assert s["overall_status"] == "BREACH"
    assert s["breach"] == 1


def test_governance_summary_ok():
    g = _governor()
    current = {"max_open_position_mwh": 100.0, "max_single_contract_mwh": 50.0, "var_limit_gbp": 10_000.0, "stop_loss_gbp": 5_000.0}
    s = g.governance_summary(current)
    assert s["overall_status"] == "OK"


def test_new_position_allowed_within_limit():
    g = _governor()
    assert g.new_position_allowed(100.0, 300.0) is True  # 400 < 500


def test_new_position_blocked_over_limit():
    g = _governor()
    assert g.new_position_allowed(200.0, 400.0) is False  # 600 > 500


def test_get_limit():
    g = _governor()
    l = g.get_limit("var_limit_gbp")
    assert l is not None
    assert l.value == 50_000.0
