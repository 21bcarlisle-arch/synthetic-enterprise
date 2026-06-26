"""Phase 92: Peak/off-peak band overlay on HH consumption view."""

from company.portal.app import _tou_band
from starlette.testclient import TestClient
from company.portal.app import app

client = TestClient(app, raise_server_exceptions=True)


def test_tou_band_peak_weekday_morning():
    assert _tou_band("2026-06-24", 9.0) == "Peak"  # Wednesday 09:00


def test_tou_band_off_peak_weekday_night():
    assert _tou_band("2026-06-24", 2.0) == "Off-Peak"  # Wednesday 02:00


def test_tou_band_off_peak_saturday():
    assert _tou_band("2026-06-20", 10.0) == "Off-Peak"  # Saturday is always off-peak


def test_tou_band_off_peak_sunday():
    assert _tou_band("2026-06-21", 14.0) == "Off-Peak"  # Sunday is always off-peak


def test_tou_band_peak_boundary_7am():
    assert _tou_band("2026-06-24", 7.0) == "Peak"  # boundary: 7am included in peak


def test_tou_band_off_peak_boundary_19():
    assert _tou_band("2026-06-24", 19.0) == "Off-Peak"  # 19:00 is off-peak


def test_consumption_route_returns_200():
    r = client.get("/account/C1/consumption")
    assert r.status_code == 200


def test_consumption_template_has_peak_legend():
    with open("company/portal/templates/consumption.html") as f:
        html = f.read()
    assert "Peak" in html
    assert "Off-Peak" in html


def test_consumption_template_has_band_column():
    with open("company/portal/templates/consumption.html") as f:
        html = f.read()
    assert "is_tou" in html
    assert "band" in html


def test_tou_band_evening_transition():
    # 18:30 still peak (hour=18.5 < 19)
    assert _tou_band("2026-06-24", 18.5) == "Peak"
    # 19:01 off-peak (hour >= 19)
    assert _tou_band("2026-06-24", 19.1) == "Off-Peak"
