"""Tests for sim/weather_ingestor.py -- mocked Open-Meteo API calls."""

import os
import tempfile
from unittest.mock import MagicMock, patch

from sim.weather_ingestor import get_daily_weather, write_weather_csv


def _open_meteo_payload(dates: list[str], temp_mean=10.0):
    return {
        "daily": {
            "time": dates,
            "temperature_2m_max": [temp_mean + 5.0] * len(dates),
            "temperature_2m_min": [temp_mean - 5.0] * len(dates),
            "temperature_2m_mean": [temp_mean] * len(dates),
            "wind_speed_10m_mean": [3.5] * len(dates),
            "cloud_cover_mean": [60.0] * len(dates),
            "precipitation_sum": [1.2] * len(dates),
        }
    }


def _mock_response(payload, status=200):
    resp = MagicMock()
    resp.status_code = status
    resp.json.return_value = payload
    return resp


def test_returns_one_record_per_day():
    dates = ["2022-01-01", "2022-01-02", "2022-01-03"]
    payload = _open_meteo_payload(dates)
    with patch("requests.get", return_value=_mock_response(payload)):
        result = get_daily_weather("LON", 51.5, -0.1, "2022-01-01", "2022-01-03")
    assert len(result) == 3


def test_non_200_returns_empty():
    with patch("requests.get", return_value=_mock_response({}, status=503)):
        result = get_daily_weather("LON", 51.5, -0.1, "2022-01-01", "2022-01-01")
    assert result == []


def test_record_keys():
    dates = ["2022-06-15"]
    payload = _open_meteo_payload(dates)
    with patch("requests.get", return_value=_mock_response(payload)):
        result = get_daily_weather("LON", 51.5, -0.1, "2022-06-15", "2022-06-15")
    expected_keys = {
        "date", "location_id", "temperature_max_c", "temperature_min_c",
        "temperature_mean_c", "wind_speed_mean_ms", "cloud_cover_pct", "precipitation_mm",
    }
    assert set(result[0].keys()) == expected_keys


def test_location_id_stored_in_records():
    dates = ["2022-06-15"]
    payload = _open_meteo_payload(dates)
    with patch("requests.get", return_value=_mock_response(payload)):
        result = get_daily_weather("BIRMINGHAM", 52.5, -1.9, "2022-06-15", "2022-06-15")
    assert result[0]["location_id"] == "BIRMINGHAM"


def test_temperature_mean_mapped():
    dates = ["2022-06-15"]
    payload = _open_meteo_payload(dates, temp_mean=15.0)
    with patch("requests.get", return_value=_mock_response(payload)):
        result = get_daily_weather("LON", 51.5, -0.1, "2022-06-15", "2022-06-15")
    assert result[0]["temperature_mean_c"] == 15.0


def test_write_weather_csv_creates_file(tmp_path):
    records = [
        {
            "date": "2022-01-01", "location_id": "LON",
            "temperature_max_c": 12.0, "temperature_min_c": 6.0,
            "temperature_mean_c": 9.0, "wind_speed_mean_ms": 4.2,
            "cloud_cover_pct": 70.0, "precipitation_mm": 2.5,
        }
    ]
    out = str(tmp_path / "weather.csv")
    write_weather_csv(records, out)
    assert os.path.exists(out)


def test_write_weather_csv_header(tmp_path):
    records = [
        {
            "date": "2022-01-01", "location_id": "LON",
            "temperature_max_c": 12.0, "temperature_min_c": 6.0,
            "temperature_mean_c": 9.0, "wind_speed_mean_ms": 4.2,
            "cloud_cover_pct": 70.0, "precipitation_mm": 2.5,
        }
    ]
    out = str(tmp_path / "weather.csv")
    write_weather_csv(records, out)
    with open(out) as f:
        header = f.readline().strip()
    assert "date" in header and "temperature_mean_c" in header
