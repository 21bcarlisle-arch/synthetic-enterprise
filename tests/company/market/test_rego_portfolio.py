import pytest
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

import pytest

# --- Phase LC depth tests ---

def test_purchase_id_stored():
    r = RegoPurchase("R_LC", "2024-01-01", 2024, 500.0, 3.5, "Gen", "wind_onshore")
    assert r.purchase_id == "R_LC"


def test_scheme_year_stored():
    r = RegoPurchase("R001", "2024-01-01", 2024, 500.0, 3.5, "Gen", "wind_onshore")
    assert r.scheme_year == 2024


def test_mwh_stored():
    r = RegoPurchase("R001", "2024-01-01", 2024, 750.0, 3.5, "Gen", "wind_onshore")
    assert r.mwh == pytest.approx(750.0)


def test_price_per_mwh_stored():
    r = RegoPurchase("R001", "2024-01-01", 2024, 500.0, 4.0, "Gen", "wind_onshore")
    assert r.price_per_mwh == pytest.approx(4.0)


def test_generator_stored():
    r = RegoPurchase("R001", "2024-01-01", 2024, 500.0, 3.5, "Humber Wind", "wind_offshore")
    assert r.generator == "Humber Wind"


def test_technology_stored():
    r = RegoPurchase("R001", "2024-01-01", 2024, 500.0, 3.5, "Gen", "solar")
    assert r.technology == "solar"


def test_retired_false_by_default():
    r = RegoPurchase("R001", "2024-01-01", 2024, 500.0, 3.5, "Gen", "hydro")
    assert r.retired is False


def test_rego_price_2022():
    assert get_rego_price(2022) == pytest.approx(6.5)


def test_rego_price_2021():
    assert get_rego_price(2021) == pytest.approx(2.0)


def test_portfolio_total_cost_zero_empty_year():
    p = RegoPortfolio()
    assert p.total_cost_gbp(2030) == pytest.approx(0.0)
