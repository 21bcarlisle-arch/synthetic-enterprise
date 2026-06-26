"""Phase 105: CSAT score tracking tests."""

from company.crm.service_log import ServiceLog, ServiceEvent


def _event(cid="C1", csat=None) -> ServiceEvent:
    return ServiceEvent(
        customer_id=cid, event_date="2026-06-26",
        channel="portal", contact_reason="general",
        outcome="pending", csat_score=csat,
    )


def test_csat_summary_empty_when_no_ratings():
    log = ServiceLog()
    s = log.csat_summary()
    assert s["count"] == 0
    assert s["mean"] is None


def test_csat_summary_with_single_score():
    log = ServiceLog()
    log.record_contact(_event(csat=5))
    s = log.csat_summary()
    assert s["count"] == 1
    assert s["mean"] == 5.0


def test_csat_summary_promoter_pct():
    log = ServiceLog()
    for score in [5, 4, 3, 2]:
        log.record_contact(_event(csat=score))
    s = log.csat_summary()
    assert s["promoter_pct"] == 50.0  # 2 of 4 are 4+ stars


def test_rate_contact_updates_score():
    log = ServiceLog()
    log.record_contact(_event())
    cid = log.latest_contact_id("C1")
    assert cid is not None
    result = log.rate_contact(cid, 4)
    assert result is True
    s = log.csat_summary()
    assert s["mean"] == 4.0


def test_rate_contact_invalid_score():
    log = ServiceLog()
    log.record_contact(_event())
    cid = log.latest_contact_id("C1")
    import pytest
    with pytest.raises(ValueError):
        log.rate_contact(cid, 6)


def test_csat_ignores_unrated_contacts():
    log = ServiceLog()
    log.record_contact(_event(csat=None))
    log.record_contact(_event(csat=5))
    s = log.csat_summary()
    assert s["count"] == 1  # only rated contact counted


def test_contact_success_page_has_csat_widget():
    with open("company/portal/templates/contact.html") as f:
        html = f.read()
    assert "csat" in html.lower() or "rating" in html.lower()
    assert "/contact/rate" in html


def test_contact_route_returns_contact_id():
    from starlette.testclient import TestClient
    from company.portal.app import app
    client = TestClient(app, raise_server_exceptions=True)
    r = client.post("/account/C1/contact", data={
        "contact_reason": "general",
        "notes": "test csat",
        "complaint": "",
    })
    assert r.status_code == 200
    assert "contact/rate" in r.text


def test_csat_rate_route_accepts_score():
    from starlette.testclient import TestClient
    from company.portal.app import app, _SERVICE_LOG
    client = TestClient(app, raise_server_exceptions=True)
    # First submit a contact
    client.post("/account/C1/contact", data={
        "contact_reason": "billing_query", "notes": "", "complaint": ""})
    cid = _SERVICE_LOG.latest_contact_id("C1")
    assert cid is not None
    r = client.post("/account/C1/contact/rate", data={"contact_id": str(cid), "score": "5"})
    assert r.status_code == 200
