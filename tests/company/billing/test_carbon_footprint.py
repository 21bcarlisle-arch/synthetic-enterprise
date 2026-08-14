"""Phase 110: Carbon footprint tracking tests."""

from company.billing.carbon_footprint import electricity_intensity, estimate_carbon, carbon_trend


# 2026-08-14: these pinned 266 and 115 -- the local `_ELECTRICITY_INTENSITY_G_CO2E_PER_KWH`
# table, the LOWEST of three disagreeing series and the only one nothing rendered. The table is
# deleted and this module now delegates to the single owner, whose values are the ones the annual
# report has been publishing all along. The numbers below are that published series, not a new
# choice -- see tests/company/regulatory/test_carbon_emissions_single_series.py.
def test_electricity_intensity_2016():
    assert electricity_intensity(2016) == 315.4


def test_electricity_intensity_2025():
    assert electricity_intensity(2025) == 175.2


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
    # Gas 0.183 kgCO2e/kWh * 10000 kWh = 1830.0 kg. Was 0.18316 here and 0.183 in the published
    # report; 2026-08-14 collapsed both to the PUBLISHED figure rather than revalue the report on
    # an unfetched source. The ~0.09% difference is recorded in the owner module, not resolved.
    assert abs(result["kg_co2e"] - 1830.0) < 1.0


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


from company.billing.carbon_footprint import electricity_intensity, estimate_carbon, _GAS_KG_CO2E_PER_KWH


def test_electricity_intensity_pre_2016_clamps_to_2016():
    assert electricity_intensity(2010) == electricity_intensity(2016)


def test_electricity_intensity_future_clamps_to_2025():
    assert electricity_intensity(2030) == electricity_intensity(2025)


def test_estimate_gas_carbon_formula():
    result = estimate_carbon(1000.0, "gas", 2022)
    expected_kg = round(1000.0 * _GAS_KG_CO2E_PER_KWH, 1)
    assert result["kg_co2e"] == expected_kg


def test_estimate_carbon_returns_all_keys():
    result = estimate_carbon(3500.0, "electricity", 2022)
    for key in ("kg_co2e", "tonnes_co2e", "intensity", "unit", "year"):
        assert key in result


def test_estimate_carbon_year_stored():
    result = estimate_carbon(3500.0, "electricity", 2022)
    assert result["year"] == 2022


def test_estimate_carbon_gas_unit_string():
    result = estimate_carbon(5000.0, "gas", 2020)
    assert "gas" in result["unit"]
