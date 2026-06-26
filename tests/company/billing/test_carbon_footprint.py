"""Phase 110: Carbon footprint tracking tests."""

from company.billing.carbon_footprint import electricity_intensity, estimate_carbon, carbon_trend


def test_electricity_intensity_2016():
    assert electricity_intensity(2016) == 266


def test_electricity_intensity_2025():
    assert electricity_intensity(2025) == 115


def test_electricity_intensity_falls_over_time():
    assert electricity_intensity(2025) < electricity_intensity(2016)


def test_estimate_electricity_carbon():
    result = estimate_carbon(3500, "electricity", 2025)
    assert result["kg_co2e"] > 0
    assert result["tonnes_co2e"] < result["kg_co2e"]
    assert "gCO2e/kWh" in result["unit"]


def test_estimate_gas_carbon():
    result = estimate_carbon(10000, "gas", 2025)
    assert result["kg_co2e"] > 0
    # Gas 0.18316 kgCO2e/kWh * 10000 kWh = 1831.6 kg
    assert abs(result["kg_co2e"] - 1831.6) < 1.0


def test_electricity_carbon_decreasing():
    # Same EAC but decreasing intensity year on year
    c2016 = estimate_carbon(3000, "electricity", 2016)["kg_co2e"]
    c2025 = estimate_carbon(3000, "electricity", 2025)["kg_co2e"]
    assert c2025 < c2016


def test_carbon_trend_returns_list():
    trend = carbon_trend(3000, "electricity", [2020, 2021, 2022, 2023])
    assert len(trend) == 4
    assert all("year" in t and "kg_co2e" in t for t in trend)


def test_consumption_template_has_carbon():
    with open("company/portal/templates/consumption.html") as f:
        html = f.read()
    assert "carbon" in html
    assert "CO" in html


def test_consumption_route_returns_200():
    from starlette.testclient import TestClient
    from company.portal.app import app
    client = TestClient(app, raise_server_exceptions=True)
    r = client.get("/account/C1/consumption")
    assert r.status_code == 200


def test_carbon_estimate_structure():
    result = estimate_carbon(5000, "electricity", 2022)
    assert "kg_co2e" in result
    assert "tonnes_co2e" in result
    assert "intensity" in result
    assert "unit" in result
    assert "year" in result
