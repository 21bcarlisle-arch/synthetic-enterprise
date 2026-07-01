"""Phase 91: CSS filing wired to real ServiceLog tests."""

from starlette.testclient import TestClient
from company.portal.app import app

client = TestClient(app, raise_server_exceptions=True)


def test_regulatory_contains_css_section():
    r = client.get("/regulatory")
    assert r.status_code == 200
    assert "Customer Service Standards" in r.text


def test_regulatory_css_total_contacts_rendered():
    r = client.get("/regulatory")
    assert "Total contacts" in r.text


def test_regulatory_css_shows_resolution_rate():
    r = client.get("/regulatory")
    assert "Resolution rate" in r.text
    assert "%" in r.text


def test_regulatory_css_shows_resolution_target():
    r = client.get("/regulatory")
    assert "Resolution target met" in r.text


def test_regulatory_css_shows_vulnerable_count():
    r = client.get("/regulatory")
    assert "Vulnerable customers contacted" in r.text


def test_contact_form_increments_css_contacts():
    r1 = client.get("/regulatory")
    import re
    before_match = re.search(r"Total contacts.*?<td>(\d+)</td>", r1.text, re.DOTALL)
    before = int(before_match.group(1)) if before_match else 0

    client.post(
        "/account/C1/contact",
        data={"contact_reason": "billing_query", "notes": "CSS test"},
    )

    r2 = client.get("/regulatory")
    after_match = re.search(r"Total contacts.*?<td>(\d+)</td>", r2.text, re.DOTALL)
    after = int(after_match.group(1)) if after_match else 0
    assert after == before + 1


def test_css_filing_in_regulatory_data():
    from company.portal.app import _load_regulatory_data
    data = _load_regulatory_data()
    assert "css" in data
    css = data["css"]
    assert "total_contacts" in css
    assert "complaint_resolution_rate" in css
    assert "resolution_target_met" in css


def test_css_resolution_target_met_is_bool():
    from company.portal.app import _load_regulatory_data
    data = _load_regulatory_data()
    assert isinstance(data["css"]["resolution_target_met"], bool)


def test_css_complaint_stats_after_complaint_form():
    client.post(
        "/account/C3/contact",
        data={"contact_reason": "complaint", "notes": "CSS complaint test", "complaint": "yes"},
    )
    from company.portal.app import _load_regulatory_data
    data = _load_regulatory_data()
    assert data["css"]["total_complaints"] >= 1


def test_regulatory_content_type_is_html():
    r = client.get("/regulatory")
    assert "text/html" in r.headers.get("content-type", "")


def test_css_total_contacts_is_nonneg_int():
    from company.portal.app import _load_regulatory_data
    data = _load_regulatory_data()
    count = data["css"]["total_contacts"]
    assert isinstance(count, int)
    assert count >= 0


def test_css_filing_has_vulnerable_contacts_key():
    from company.portal.app import _load_regulatory_data
    data = _load_regulatory_data()
    css = data["css"]
    assert "vulnerable_contacts" in css or "vulnerable" in str(css).lower()


def test_regulatory_returns_200():
    r = client.get("/regulatory")
    assert r.status_code == 200


def test_css_resolution_rate_in_range():
    from company.portal.app import _load_regulatory_data
    data = _load_regulatory_data()
    rate = data["css"]["complaint_resolution_rate"]
    assert 0.0 <= rate <= 100.0


def test_css_resolution_target_met_is_bool_type():
    from company.portal.app import _load_regulatory_data
    data = _load_regulatory_data()
    css = data["css"]
    assert isinstance(css["resolution_target_met"], bool)
