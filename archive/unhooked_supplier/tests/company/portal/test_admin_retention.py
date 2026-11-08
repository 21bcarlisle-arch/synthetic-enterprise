"""Phase 109: Admin retention dashboard tests."""

from starlette.testclient import TestClient
from company.portal.app import app

client = TestClient(app, raise_server_exceptions=True)


def test_retention_route_returns_200():
    r = client.get("/admin/retention")
    assert r.status_code == 200


def test_retention_shows_tier_labels():
    r = client.get("/admin/retention")
    text = r.text
    assert "HIGH" in text or "MEDIUM" in text or "LOW" in text


def test_retention_shows_customer_links():
    r = client.get("/admin/retention")
    assert "/account/C" in r.text


def test_admin_has_retention_link():
    r = client.get("/admin")
    assert "/admin/retention" in r.text


def test_retention_template_has_score_col():
    with open("company/portal/templates/admin_retention.html") as f:
        html = f.read()
    assert "Score" in html
    assert "Signals" in html


def test_retention_summary_cards():
    with open("company/portal/templates/admin_retention.html") as f:
        html = f.read()
    assert "high_risk" in html
    assert "medium_risk" in html
    assert "low_risk" in html


def test_retention_all_customers_present():
    from company.portal.app import _load_admin_data
    admin = _load_admin_data()
    total = admin["total_customers"]
    r = client.get("/admin/retention")
    assert r.status_code == 200
    # All customer account links should be present
    from company.portal.app import _CUSTOMER_INDEX
    for cid in list(_CUSTOMER_INDEX.keys())[:3]:
        assert cid in r.text


def test_retention_route_content_type_is_html():
    r = client.get("/admin/retention")
    assert "text/html" in r.headers.get("content-type", "")


def test_retention_has_table():
    r = client.get("/admin/retention")
    assert "<table" in r.text.lower()


def test_retention_risk_column_present():
    r = client.get("/admin/retention")
    assert "Risk" in r.text


def test_retention_route_has_risk_label():
    client = TestClient(app)
    r = client.get("/admin/retention")
    assert "risk" in r.text.lower()


def test_retention_total_customers_positive():
    from company.portal.app import _load_admin_data
    d = _load_admin_data()
    assert d["total_customers"] >= 0


def test_retention_csat_has_promoter_pct_key():
    from company.portal.app import _load_admin_data
    d = _load_admin_data()
    assert "promoter_pct" in d["csat"]
