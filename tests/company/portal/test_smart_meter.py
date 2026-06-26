"""Phase 103: Smart meter upgrade request flow tests."""

from starlette.testclient import TestClient
from company.portal.app import app

client = TestClient(app, raise_server_exceptions=True)


def test_smart_meter_get_non_hh_customer():
    # C1 is resi, profile-class (no smart meter)
    r = client.get("/account/C1/smart-meter")
    assert r.status_code == 200
    assert "Smart Meter Upgrade" in r.text
    assert "Request smart meter upgrade" in r.text


def test_smart_meter_get_hh_customer():
    # C_IC1 is HH metered I&C
    r = client.get("/account/C_IC1/smart-meter")
    assert r.status_code == 200
    assert "already have a smart meter" in r.text
    assert "Request smart meter upgrade" not in r.text


def test_smart_meter_post_creates_service_event():
    from company.portal.app import _SERVICE_LOG
    initial_count = len(_SERVICE_LOG.contacts_for_customer("C1"))
    r = client.post("/account/C1/smart-meter", data={
        "contact_pref": "morning",
        "notes": "prefer Tuesdays",
    })
    assert r.status_code == 200
    assert "Upgrade request received" in r.text
    events = _SERVICE_LOG.contacts_for_customer("C1")
    new_events = [e for e in events[initial_count:] if e.contact_reason == "smart_meter"]
    assert len(new_events) == 1
    assert new_events[0].outcome == "upgrade_requested"


def test_smart_meter_post_shows_reference():
    r = client.post("/account/C1/smart-meter", data={
        "contact_pref": "weekend",
        "notes": "",
    })
    assert "SM-C1-" in r.text


def test_smart_meter_post_event_is_self_service():
    from company.portal.app import _SERVICE_LOG
    initial_count = len(_SERVICE_LOG.contacts_for_customer("C2"))
    client.post("/account/C2/smart-meter", data={"contact_pref": "afternoon", "notes": ""})
    events = _SERVICE_LOG.contacts_for_customer("C2")
    new_events = [e for e in events[initial_count:] if e.contact_reason == "smart_meter"]
    assert new_events[0].agent_type == "self_service"


def test_dashboard_has_smart_meter_link_for_non_hh():
    r = client.get("/account/C1")
    assert r.status_code == 200
    assert "smart-meter" in r.text


def test_smart_meter_404_for_unknown():
    r = client.get("/account/NOACCOUNT/smart-meter")
    assert r.status_code == 404


def test_template_has_timeline():
    with open("company/portal/templates/smart_meter.html") as f:
        html = f.read()
    assert "Installation typically takes" in html
    assert "Half-hourly data" in html
