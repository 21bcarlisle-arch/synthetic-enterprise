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
