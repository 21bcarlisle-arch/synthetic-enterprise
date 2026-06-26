"""Phase 139: REGO portfolio tests."""

from company.market.rego_portfolio import RegoPurchase, RegoPortfolio, get_rego_price


def _portfolio():
    p = RegoPortfolio()
    p.buy(RegoPurchase("R001", "2024-02-01", 2024, 500.0, 3.50, "Humber Wind", "wind_offshore"))
    p.buy(RegoPurchase("R002", "2024-03-01", 2024, 300.0, 3.20, "Scots Hydro", "hydro"))
    p.buy(RegoPurchase("R003", "2023-11-01", 2023, 400.0, 4.00, "Lincs Solar", "solar"))
    return p


def test_buy_records_purchase():
    p = _portfolio()
    assert len(p.by_scheme_year(2024)) == 2


def test_cost_gbp():
    r = RegoPurchase("X", "2024-01-01", 2024, 100.0, 3.50, "Gen", "wind_onshore")
    assert r.cost_gbp == 350.0


def test_retire_marks_retired():
    p = _portfolio()
    result = p.retire("R001", "2024-03-31")
    assert result is True
    r = next(x for x in p.by_scheme_year(2024) if x.purchase_id == "R001")
    assert r.retired is True


def test_retire_unknown_returns_false():
    p = _portfolio()
    assert p.retire("ZZZZ", "2024-03-31") is False


def test_available_mwh_excludes_retired():
    p = _portfolio()
    p.retire("R001", "2024-03-31")
    assert p.available_mwh(2024) == 300.0


def test_coverage_check_fully_covered():
    p = _portfolio()
    c = p.coverage_check(2024, 700.0)
    assert c["covered"] is True
    assert c["shortfall_mwh"] == 0.0


def test_coverage_check_shortfall():
    p = _portfolio()
    c = p.coverage_check(2024, 900.0)  # only 800 MWh held
    assert c["covered"] is False
    assert c["shortfall_mwh"] == 100.0


def test_by_technology():
    p = _portfolio()
    tech = p.by_technology(2024)
    assert "wind_offshore" in tech
    assert "hydro" in tech


def test_rego_price_crisis_year():
    assert get_rego_price(2022) == 6.50


def test_summary_structure():
    p = _portfolio()
    s = p.summary(2024)
    for k in ("purchases", "total_mwh", "retired_mwh", "available_mwh", "total_cost_gbp"):
        assert k in s
