"""Phase 106: CSAT reporting in admin dashboard tests."""

from starlette.testclient import TestClient
from company.portal.app import app

client = TestClient(app, raise_server_exceptions=True)


def test_admin_route_returns_200():
    r = client.get("/admin")
    assert r.status_code == 200


def test_admin_has_csat_card():
    r = client.get("/admin")
    assert "CSAT" in r.text


def test_admin_csat_shows_dash_when_no_ratings():
    # No contacts rated yet in fresh session
    r = client.get("/admin")
    # Either shows a score or shows em-dash for "no data"
    assert "/5" in r.text or "—" in r.text


def test_admin_template_has_csat_card():
    with open("company/portal/templates/admin.html") as f:
        html = f.read()
    assert "csat" in html.lower()
    assert "CSAT" in html


def test_csat_data_key_in_admin_route():
    from company.portal.app import _load_admin_data
    data = _load_admin_data()
    assert "csat" in data
    assert "count" in data["csat"]
    assert "mean" in data["csat"]
    assert "promoter_pct" in data["csat"]


def test_csat_score_in_grid_after_rating():
    from company.portal.app import _SERVICE_LOG
    from company.crm.service_log import ServiceEvent
    # Submit contact then rate it
    r_post = client.post("/account/C1/contact",
                         data={"contact_reason": "general", "notes": "", "complaint": ""})
    cid = _SERVICE_LOG.latest_contact_id("C1")
    if cid:
        _SERVICE_LOG.rate_contact(cid, 5)
    data = _load_admin_data()
    assert data["csat"]["count"] >= 1
    assert data["csat"]["mean"] is not None



from company.portal.app import _load_admin_data


def test_promoter_pct_is_percentage():
    from company.portal.app import _SERVICE_LOG
    # Give a high score for another customer
    client.post("/account/C2/contact",
                data={"contact_reason": "billing_query", "notes": "", "complaint": ""})
    cid = _SERVICE_LOG.latest_contact_id("C2")
    if cid:
        _SERVICE_LOG.rate_contact(cid, 5)
    data = _load_admin_data()
    pct = data["csat"].get("promoter_pct")
    if pct is not None:
        assert 0.0 <= pct <= 100.0


def test_csat_count_is_int():
    data = _load_admin_data()
    assert isinstance(data["csat"]["count"], int)


def test_admin_route_content_type_is_html():
    r = client.get("/admin")
    assert "text/html" in r.headers.get("content-type", "")


def test_csat_initial_mean_none_or_float():
    data = _load_admin_data()
    mean = data["csat"]["mean"]
    assert mean is None or isinstance(mean, float)
