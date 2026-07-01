import pytest
"""Phase 99: Market rate comparison tests."""

import json
from pathlib import Path
from company.market.rate_comparison import (
    market_rate_comparison, _effective_rate_p_per_kwh
)
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


def _make_feed(tmp_path, price_gbp_per_mwh=80.0):
    feed = {
        "published_at": "2026-06-26T10:00:00Z",
        "prices": [
            {"fuel": "electricity", "period": "2026-06-26T10:00:00Z",
             "price_gbp_per_mwh": price_gbp_per_mwh},
        ]
    }
    p = tmp_path / "price_feed.json"
    p.write_text(json.dumps(feed))
    return p


def test_effective_rate_no_invoices(tmp_path):
    db = tmp_path / "inv.db"
    create_schema(db)
    assert _effective_rate_p_per_kwh("C1", db) is None


def test_effective_rate_from_invoice(tmp_path):
    db = tmp_path / "inv.db"
    create_schema(db)
    # 1000 kWh for £150 (before VAT) — invoice total will be with VAT
    create_invoice(_make_bill("C1", "2025-01-01", "2025-12-31", 1000.0, 150.0), db)
    rate = _effective_rate_p_per_kwh("C1", db)
    # total = 150 * 1.05 = 157.5; rate = 157.5 / 1000 * 100 = 15.75 p/kWh
    assert rate is not None
    assert 14.0 < rate < 17.0


def test_rate_comparison_no_feed(tmp_path):
    db = tmp_path / "inv.db"
    feed = tmp_path / "nofeed.json"
    result = market_rate_comparison("C1", db, feed)
    assert result is None


def test_rate_comparison_returns_market_p(tmp_path):
    db = tmp_path / "inv.db"
    create_schema(db)
    feed = _make_feed(tmp_path, 80.0)
    result = market_rate_comparison("C1", db, feed)
    assert result is not None
    assert result["market_p"] == 8.4  # 80 £/MWh + 5% premium = 84 £/MWh = 8.4 p/kWh


def test_rate_comparison_no_invoice_data(tmp_path):
    db = tmp_path / "inv.db"
    create_schema(db)
    feed = _make_feed(tmp_path)
    result = market_rate_comparison("C1", db, feed)
    assert result is not None
    assert result["contracted_p"] is None
    assert "No invoice" in result["message"]


def test_protected_when_below_market(tmp_path):
    db = tmp_path / "inv.db"
    create_schema(db)
    # Low contracted rate (15 p/kWh) vs high market (80 £/MWh = 8 p/kWh)... 
    # Actually: 15 p/kWh contracted vs 8 p/kWh market => market < contracted => not protected
    # Let market be high: 200 £/MWh = 20 p/kWh vs contracted 15 p/kWh => protected
    create_invoice(_make_bill("C1", "2025-01-01", "2025-12-31", 1000.0, 142.86), db)
    feed = _make_feed(tmp_path, 200.0)  # 200 £/MWh = 20 p/kWh
    result = market_rate_comparison("C1", db, feed)
    assert result is not None
    if result["contracted_p"] is not None:
        # market (20) > contracted (15) => protected = True
        assert result["protected"] is True


def test_consumption_template_has_rate_widget():
    with open("company/portal/templates/consumption.html") as f:
        html = f.read()
    assert "rate_cmp" in html
    assert "market_p" in html


def test_consumption_route_returns_200():
    from starlette.testclient import TestClient
    from company.portal.app import app
    client = TestClient(app, raise_server_exceptions=True)
    r = client.get("/account/C1/consumption")
    assert r.status_code == 200


# --- Phase KN depth tests ---

def test_result_has_five_keys(tmp_path):
    db = tmp_path / "inv.db"
    create_schema(db)
    feed = _make_feed(tmp_path, 80.0)
    result = market_rate_comparison("C1", db, feed)
    assert set(result.keys()) == {"market_p", "contracted_p", "delta_p", "protected", "message"}


def test_market_p_formula(tmp_path):
    db = tmp_path / "inv.db"
    create_schema(db)
    feed = _make_feed(tmp_path, 100.0)  # 100 GBP/MWh
    result = market_rate_comparison("C1", db, feed)
    # 100 GBP/MWh * 1.05 / 10 = 10.5 p/kWh
    assert result["market_p"] == pytest.approx(10.5)


def test_protected_false_when_contracted_above_market(tmp_path):
    db = tmp_path / "inv.db"
    create_schema(db)
    # contracted ~15.75 p/kWh, market 8.4 p/kWh => contracted > market => not protected
    create_invoice(_make_bill("C1", "2025-01-01", "2025-12-31", 1000.0, 150.0), db)
    feed = _make_feed(tmp_path, 80.0)
    result = market_rate_comparison("C1", db, feed)
    assert result["protected"] is False


def test_delta_p_is_market_minus_contracted(tmp_path):
    db = tmp_path / "inv.db"
    create_schema(db)
    create_invoice(_make_bill("C1", "2025-01-01", "2025-12-31", 1000.0, 100.0), db)
    feed = _make_feed(tmp_path, 80.0)
    result = market_rate_comparison("C1", db, feed)
    if result["contracted_p"] is not None:
        assert result["delta_p"] == pytest.approx(result["market_p"] - result["contracted_p"])


def test_message_is_string(tmp_path):
    db = tmp_path / "inv.db"
    create_schema(db)
    feed = _make_feed(tmp_path, 80.0)
    result = market_rate_comparison("C1", db, feed)
    assert isinstance(result["message"], str)


def test_effective_rate_returns_float(tmp_path):
    db = tmp_path / "inv.db"
    create_schema(db)
    create_invoice(_make_bill("C1", "2025-01-01", "2025-12-31", 1000.0, 100.0), db)
    rate = _effective_rate_p_per_kwh("C1", db)
    assert isinstance(rate, float)


def test_effective_rate_proportional_to_amount(tmp_path):
    db = tmp_path / "inv.db"
    create_schema(db)
    create_invoice(_make_bill("C1", "2025-01-01", "2025-12-31", 1000.0, 200.0), db)
    rate_high = _effective_rate_p_per_kwh("C1", db)
    db2 = tmp_path / "inv2.db"
    create_schema(db2)
    create_invoice(_make_bill("C2", "2025-01-01", "2025-12-31", 1000.0, 100.0), db2)
    rate_low = _effective_rate_p_per_kwh("C2", db2)
    assert rate_high > rate_low


def test_contracted_p_none_when_no_invoice(tmp_path):
    db = tmp_path / "inv.db"
    create_schema(db)
    feed = _make_feed(tmp_path, 80.0)
    result = market_rate_comparison("C1", db, feed)
    assert result["contracted_p"] is None


def test_market_p_positive(tmp_path):
    db = tmp_path / "inv.db"
    create_schema(db)
    feed = _make_feed(tmp_path, 50.0)
    result = market_rate_comparison("C1", db, feed)
    assert result["market_p"] > 0.0


def test_result_none_when_no_feed(tmp_path):
    db = tmp_path / "inv.db"
    create_schema(db)
    missing_feed = tmp_path / "missing.json"
    result = market_rate_comparison("C1", db, missing_feed)
    assert result is None
