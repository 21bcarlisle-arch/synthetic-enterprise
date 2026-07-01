"""Phase 97: Annual cost forecast tests."""

from company.billing.consumption_forecast import forecast_annual_cost
from company.billing.invoice import create_invoice, create_schema


def _make_bill(cid, period_start, period_end, kwh, amount):
    return {
        "customer_id": cid,
        "account_id": cid,
        "commodity": "electricity",
        "period_start": period_start,
        "period_end": period_end,
        "total_consumption_kwh": kwh,
        "total_amount_gbp": amount,
    }


def test_forecast_returns_none_when_no_history(tmp_path):
    db = tmp_path / "inv.db"
    create_schema(db)
    result = forecast_annual_cost("C1", 24.5, 61.0, db)
    assert result is None


def test_forecast_returns_dict_with_history(tmp_path):
    db = tmp_path / "inv.db"
    create_schema(db)
    # Two invoices spanning > 1 year
    create_invoice(_make_bill("C1", "2023-01-01", "2023-06-30", 1250.0, 350.0), db)
    create_invoice(_make_bill("C1", "2023-07-01", "2023-12-31", 1250.0, 350.0), db)
    result = forecast_annual_cost("C1", 24.5, 61.0, db)
    assert result is not None
    assert result["eac_kwh"] > 0
    assert result["annual_total_gbp"] > 0


def test_forecast_structure(tmp_path):
    db = tmp_path / "inv.db"
    create_schema(db)
    create_invoice(_make_bill("C1", "2023-01-01", "2023-12-31", 2500.0, 700.0), db)
    result = forecast_annual_cost("C1", 24.5, 61.0, db)
    assert result is not None
    assert "annual_commodity_gbp" in result
    assert "annual_sc_gbp" in result
    assert "quarterly_total_gbp" in result
    assert len(result["quarterly_total_gbp"]) == 4
    assert len(result["monthly_total_gbp"]) == 12


def test_quarterly_sums_to_annual(tmp_path):
    db = tmp_path / "inv.db"
    create_schema(db)
    create_invoice(_make_bill("C1", "2023-01-01", "2023-12-31", 2500.0, 700.0), db)
    result = forecast_annual_cost("C1", 24.5, 61.0, db)
    assert result is not None
    quarterly_sum = sum(result["quarterly_total_gbp"])
    assert abs(quarterly_sum - result["annual_total_gbp"]) < 1.0


def test_sc_included_in_total(tmp_path):
    db = tmp_path / "inv.db"
    create_schema(db)
    create_invoice(_make_bill("C1", "2023-01-01", "2023-12-31", 2500.0, 700.0), db)
    result_no_sc = forecast_annual_cost("C1", 24.5, 0.0, db)
    result_with_sc = forecast_annual_cost("C1", 24.5, 61.0, db)
    assert result_with_sc["annual_total_gbp"] > result_no_sc["annual_total_gbp"]


def test_consumption_template_has_forecast():
    with open("company/portal/templates/consumption.html") as f:
        html = f.read()
    assert "cost_forecast" in html
    assert "annual_total_gbp" in html


def test_consumption_route_returns_200():
    from starlette.testclient import TestClient
    from company.portal.app import app
    client = TestClient(app, raise_server_exceptions=True)
    r = client.get("/account/C1/consumption")
    assert r.status_code == 200


def test_forecast_zero_eac_returns_zero_cost(tmp_path):
    db = tmp_path / "inv.db"
    create_schema(db)
    # 0 kWh — degenerate but should not crash
    create_invoice(_make_bill("C1", "2023-01-01", "2023-12-31", 0.0, 50.0), db)
    result = forecast_annual_cost("C1", 24.5, 61.0, db)
    # May return None (0 kWh) or a valid result with 0 commodity
    if result is not None:
        assert result["annual_commodity_gbp"] == 0.0


# --- Phase KG depth tests ---

def test_monthly_sum_equals_annual(tmp_path):
    db = tmp_path / "inv.db"
    create_schema(db)
    create_invoice(_make_bill("C1", "2023-01-01", "2023-12-31", 2500.0, 700.0), db)
    result = forecast_annual_cost("C1", 24.5, 61.0, db)
    assert result is not None
    monthly_sum = sum(result["monthly_total_gbp"])
    assert abs(monthly_sum - result["annual_total_gbp"]) < 1.0


def test_higher_unit_rate_higher_commodity(tmp_path):
    db = tmp_path / "inv.db"
    create_schema(db)
    create_invoice(_make_bill("C1", "2023-01-01", "2023-12-31", 2500.0, 700.0), db)
    low = forecast_annual_cost("C1", 20.0, 61.0, db)
    high = forecast_annual_cost("C1", 40.0, 61.0, db)
    assert high["annual_commodity_gbp"] > low["annual_commodity_gbp"]


def test_c2_returns_none_no_history(tmp_path):
    db = tmp_path / "inv.db"
    create_schema(db)
    create_invoice(_make_bill("C1", "2023-01-01", "2023-12-31", 2500.0, 700.0), db)
    # C2 has no history
    result = forecast_annual_cost("C2", 24.5, 61.0, db)
    assert result is None


def test_monthly_all_non_negative(tmp_path):
    db = tmp_path / "inv.db"
    create_schema(db)
    create_invoice(_make_bill("C1", "2023-01-01", "2023-12-31", 2500.0, 700.0), db)
    result = forecast_annual_cost("C1", 24.5, 61.0, db)
    assert result is not None
    assert all(v >= 0 for v in result["monthly_total_gbp"])


def test_sc_zero_gives_zero_sc_gbp(tmp_path):
    db = tmp_path / "inv.db"
    create_schema(db)
    create_invoice(_make_bill("C1", "2023-01-01", "2023-12-31", 2500.0, 700.0), db)
    result = forecast_annual_cost("C1", 24.5, 0.0, db)
    assert result is not None
    assert result["annual_sc_gbp"] == 0.0


def test_eac_kwh_positive_with_consumption(tmp_path):
    db = tmp_path / "inv.db"
    create_schema(db)
    create_invoice(_make_bill("C1", "2023-01-01", "2023-12-31", 3500.0, 900.0), db)
    result = forecast_annual_cost("C1", 24.5, 61.0, db)
    assert result is not None
    assert result["eac_kwh"] > 0


def test_different_customers_independent(tmp_path):
    db = tmp_path / "inv.db"
    create_schema(db)
    create_invoice(_make_bill("C1", "2023-01-01", "2023-12-31", 1000.0, 300.0), db)
    create_invoice(_make_bill("C2", "2023-01-01", "2023-12-31", 4000.0, 1100.0), db)
    r1 = forecast_annual_cost("C1", 24.5, 61.0, db)
    r2 = forecast_annual_cost("C2", 24.5, 61.0, db)
    assert r1 is not None and r2 is not None
    assert r2["eac_kwh"] > r1["eac_kwh"]


def test_quarterly_has_four_elements(tmp_path):
    db = tmp_path / "inv.db"
    create_schema(db)
    create_invoice(_make_bill("C1", "2023-01-01", "2023-12-31", 2500.0, 700.0), db)
    result = forecast_annual_cost("C1", 24.5, 61.0, db)
    assert result is not None
    assert len(result["quarterly_total_gbp"]) == 4


def test_two_invoices_same_customer(tmp_path):
    db = tmp_path / "inv.db"
    create_schema(db)
    create_invoice(_make_bill("C1", "2023-01-01", "2023-06-30", 1000.0, 300.0), db)
    create_invoice(_make_bill("C1", "2023-07-01", "2023-12-31", 1200.0, 350.0), db)
    result = forecast_annual_cost("C1", 24.5, 61.0, db)
    assert result is not None
    assert result["annual_total_gbp"] > 0


def test_annual_total_contains_commodity_and_sc(tmp_path):
    db = tmp_path / "inv.db"
    create_schema(db)
    create_invoice(_make_bill("C1", "2023-01-01", "2023-12-31", 2500.0, 700.0), db)
    result = forecast_annual_cost("C1", 24.5, 61.0, db)
    assert result is not None
    expected = result["annual_commodity_gbp"] + result["annual_sc_gbp"]
    assert abs(result["annual_total_gbp"] - expected) < 0.01
