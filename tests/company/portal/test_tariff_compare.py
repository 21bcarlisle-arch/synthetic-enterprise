"""Tests for Portal Phase 2: tariff comparison routes (Phase 77)."""

import pytest
from starlette.testclient import TestClient
from company.portal.app import app

client = TestClient(app, raise_server_exceptions=True)
_KNOWN = "C1"


def test_tariff_compare_route_ok():
    r = client.get(f"/account/{_KNOWN}/tariff-compare")
    assert r.status_code == 200


def test_tariff_compare_shows_heading():
    r = client.get(f"/account/{_KNOWN}/tariff-compare")
    assert "Tariff Comparison" in r.text


def test_tariff_compare_shows_options():
    r = client.get(f"/account/{_KNOWN}/tariff-compare")
    assert "Fixed 1 Year" in r.text
    assert "Fixed 2 Year" in r.text
    assert "Variable SVT" in r.text


def test_tariff_compare_shows_annual_cost():
    r = client.get(f"/account/{_KNOWN}/tariff-compare")
    assert "Est. Annual Cost" in r.text


def test_tariff_compare_404_unknown():
    r = client.get("/account/UNKNOWN_ACCT/tariff-compare")
    assert r.status_code == 404


def test_switch_tariff_post_ok():
    r = client.post(
        f"/account/{_KNOWN}/switch-tariff",
        data={"tariff_name": "Fixed 1 Year", "term_months": "12"},
        follow_redirects=False,
    )
    assert r.status_code == 200


def test_switch_tariff_shows_confirmation():
    r = client.post(
        f"/account/{_KNOWN}/switch-tariff",
        data={"tariff_name": "Fixed 2 Year", "term_months": "24"},
    )
    assert "Switch Request Received" in r.text
    assert "Fixed 2 Year" in r.text


def test_switch_tariff_includes_reference():
    r = client.post(
        f"/account/{_KNOWN}/switch-tariff",
        data={"tariff_name": "Variable SVT", "term_months": "1"},
    )
    assert "SW-" in r.text


def test_tariff_compare_content_type_is_html():
    r = client.get(f"/account/{_KNOWN}/tariff-compare")
    assert "text/html" in r.headers.get("content-type", "")


def test_tariff_compare_shows_unit_rate():
    r = client.get(f"/account/{_KNOWN}/tariff-compare")
    assert "p/kWh" in r.text or "unit" in r.text.lower()


def test_switch_tariff_shows_customer_id():
    r = client.post(
        f"/account/{_KNOWN}/switch-tariff",
        data={"tariff_name": "Fixed 1 Year", "term_months": "12"},
    )
    assert _KNOWN in r.text
