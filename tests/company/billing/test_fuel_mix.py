"""Phase 111: Fuel mix disclosure tests."""

from company.billing.fuel_mix import get_fuel_mix, fuel_mix_summary


def test_fuel_mix_2016_renewable():
    mix = get_fuel_mix(2016)
    assert mix["renewable"] == 24.6


def test_fuel_mix_2025_renewable_majority():
    mix = get_fuel_mix(2025)
    assert mix["renewable"] > 50.0


def test_fuel_mix_sums_to_100():
    mix = get_fuel_mix(2023)
    total = sum(mix.values())
    assert abs(total - 100.0) < 0.5


def test_fuel_mix_summary_structure():
    s = fuel_mix_summary(2024)
    assert "renewable_pct" in s
    assert "low_carbon_pct" in s
    assert "fossil_pct" in s
    assert "trend_direction" in s


def test_low_carbon_includes_nuclear():
    s = fuel_mix_summary(2022)
    assert s["low_carbon_pct"] == round(s["mix"]["renewable"] + s["mix"]["nuclear"], 1)


def test_renewable_trend_direction():
    s = fuel_mix_summary(2024)
    # Renewables grew 2023-2024
    assert s["trend_direction"] == "up"


def test_regulatory_route_has_fuel_mix():
    from starlette.testclient import TestClient
    from company.portal.app import app
    client = TestClient(app, raise_server_exceptions=True)
    r = client.get("/regulatory")
    assert r.status_code == 200
    assert "Fuel Mix" in r.text


def test_regulatory_template_has_fuel_section():
    with open("company/portal/templates/regulatory.html") as f:
        html = f.read()
    assert "fuel_mix" in html
    assert "Renewable" in html


def test_prior_year_fallback():
    # Year before data range returns 2016 values
    mix = get_fuel_mix(2010)
    assert mix["renewable"] == 24.6
