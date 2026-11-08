"""Phase 84: Regulatory compliance dashboard tests."""

from starlette.testclient import TestClient

from company.portal.app import app, _load_regulatory_data

client = TestClient(app, raise_server_exceptions=True)


def test_regulatory_route_returns_200():
    r = client.get("/regulatory")
    assert r.status_code == 200


def test_regulatory_shows_smart_meter_heading():
    r = client.get("/regulatory")
    assert "Smart Meter" in r.text or "smart" in r.text.lower()


def test_regulatory_shows_mcr_heading():
    r = client.get("/regulatory")
    assert "MCR" in r.text or "Capital" in r.text


def test_regulatory_shows_compliance_status():
    r = client.get("/regulatory")
    # Status must be one of the defined values
    assert any(s in r.text for s in ["COMPLIANT", "AT_RISK", "BREACH"])


def test_regulatory_shows_solvency_status():
    r = client.get("/regulatory")
    assert any(s in r.text for s in ["OK", "Watch", "STRESS"])


def test_regulatory_shows_turnover_fee():
    r = client.get("/regulatory")
    assert "turnover" in r.text.lower() or "Ofgem" in r.text


def test_load_regulatory_data_returns_dict():
    data = _load_regulatory_data()
    assert isinstance(data, dict)
    assert "sm_status" in data
    assert "solvency_status" in data
    assert "treasury_gbp" in data


def test_load_regulatory_data_sm_status_valid():
    data = _load_regulatory_data()
    assert data["sm_status"] in ("COMPLIANT", "AT_RISK", "BREACH")


def test_load_regulatory_data_solvency_status_valid():
    data = _load_regulatory_data()
    assert data["solvency_status"] in ("OK", "Watch", "STRESS")


def test_load_regulatory_data_penetration_in_range():
    data = _load_regulatory_data()
    assert 0.0 <= data["resi_penetration_pct"] <= 100.0


def test_load_regulatory_data_mcr_math():
    data = _load_regulatory_data()
    # headroom = treasury - mcr_req
    expected = data["treasury_gbp"] - data["mcr_req_gbp"]
    assert abs(data["mcr_headroom_gbp"] - expected) < 0.01


def test_regulatory_template_has_year():
    with open("company/portal/templates/regulatory.html") as f:
        html = f.read()
    assert "reg.year" in html
    assert "reg.sm_status" in html


def test_regulatory_template_has_solvency_ratio():
    with open("company/portal/templates/regulatory.html") as f:
        html = f.read()
    assert "solvency_ratio" in html
