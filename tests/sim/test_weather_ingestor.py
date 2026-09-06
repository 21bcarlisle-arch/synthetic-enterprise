"""Tests for sim/weather_ingestor.py -- mocked Open-Meteo API calls."""

import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from sim.weather_ingestor import WeatherArchiveRefusal, get_daily_weather, write_weather_csv


def _records(n: int) -> list[dict]:
    """`n` well-formed archive rows, for the write-side guards."""
    return [
        {"date": f"2022-01-{i:02d}", "location_id": "LON", "temperature_max_c": 12.0,
         "temperature_min_c": 6.0, "temperature_mean_c": 9.0, "wind_speed_mean_ms": 4.2,
         "cloud_cover_pct": 70.0, "precipitation_mm": 2.5}
        for i in range(1, n + 1)
    ]


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


def test_non_200_refuses_and_names_the_status():
    """DEFECT: this asserted `result == []` until 2026-09-06 — it pinned the fail-silent
    branch, so it stayed green through the exact failure it covers. A 503 became an empty
    list, `write_weather_csv` truncated the destination, and the pull exited 0."""
    with patch("requests.get", return_value=_mock_response({}, status=503)):
        with pytest.raises(WeatherArchiveRefusal) as excinfo:
            get_daily_weather("LON", 51.5, -0.1, "2022-01-01", "2022-01-01")
    assert "503" in str(excinfo.value)


def test_rate_limit_refusal_carries_open_meteos_own_reason():
    """The 429 that was live on 2026-09-06. An HTTP code alone cannot tell a wait from a
    bug, so the refusal has to carry the API's `reason` — this is the string that tells the
    next session to try tomorrow rather than to go looking for a defect."""
    body = {"error": True, "reason": "Daily API request limit exceeded. Please try again tomorrow."}
    with patch("requests.get", return_value=_mock_response(body, status=429)):
        with pytest.raises(WeatherArchiveRefusal) as excinfo:
            get_daily_weather("BIRMINGHAM", 52.4862, -1.8904, "2016-01-01", "2025-06-07")
    assert "Daily API request limit exceeded" in str(excinfo.value)
    assert "BIRMINGHAM" in str(excinfo.value)


def test_empty_records_never_reach_disk(tmp_path):
    """The leg that turns a refused pull into data loss: `mode='w'` truncates, so writing
    zero rows over a real archive destroys it."""
    out = str(tmp_path / "C1.csv")
    with pytest.raises(WeatherArchiveRefusal):
        write_weather_csv([], out)
    assert not os.path.exists(out)


def test_a_short_pull_cannot_shrink_an_existing_archive(tmp_path):
    """The failure the emptiness check MISSES: a 200 carrying a truncated range. Ten years
    on disk, three days retrieved, and the write is silent without this."""
    out = str(tmp_path / "C1.csv")
    write_weather_csv(_records(10), out)
    with pytest.raises(WeatherArchiveRefusal) as excinfo:
        write_weather_csv(_records(3), out)
    assert "10" in str(excinfo.value) and "3" in str(excinfo.value)
    with open(out) as f:
        assert len(f.readlines()) == 11  # header + the original 10, untouched


def test_a_longer_pull_still_replaces_the_archive(tmp_path):
    """The guard must not wedge the normal case. Without this leg a refusal that refused
    EVERYTHING would pass every test above."""
    out = str(tmp_path / "C1.csv")
    write_weather_csv(_records(3), out)
    write_weather_csv(_records(10), out)
    with open(out) as f:
        assert len(f.readlines()) == 11


def test_re_pulling_the_same_range_is_not_refused(tmp_path):
    """DATA rows, not lines — and this is the leg that proves the difference.

    I predicted the header-only test below would be the one that failed when
    `_existing_row_count` counts lines. It was not: the poison killed the SHRINK test on its
    message (11 vs 10) and the header-only case passed either way. This is the real
    discriminator, because it sits exactly on the boundary — 5 data rows is 6 lines, so
    line-counting refuses an identical re-pull and data-row counting allows it.
    """
    out = str(tmp_path / "C1.csv")
    write_weather_csv(_records(5), out)
    write_weather_csv(_records(5), out)  # must not raise
    with open(out) as f:
        assert len(f.readlines()) == 6


def test_a_header_only_archive_is_replaceable(tmp_path):
    """A file already truncated by the old behaviour counts 0 DATA rows, so a real pull can
    repair it — the fix must not wedge the very files the defect created."""
    out = str(tmp_path / "C1.csv")
    write_weather_csv(_records(1), out)
    with open(out, "w") as f:
        f.write("date,location_id,temperature_max_c,temperature_min_c,"
                "temperature_mean_c,wind_speed_mean_ms,cloud_cover_pct,precipitation_mm\n")
    write_weather_csv(_records(5), out)
    with open(out) as f:
        assert len(f.readlines()) == 6


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


def test_temperature_max_min_mapped():
    dates = ["2022-06-15"]
    payload = _open_meteo_payload(dates, temp_mean=10.0)
    from unittest.mock import patch
    with patch("requests.get", return_value=_mock_response(payload)):
        result = get_daily_weather("LON", 51.5, -0.1, "2022-06-15", "2022-06-15")
    assert result[0]["temperature_max_c"] == 15.0
    assert result[0]["temperature_min_c"] == 5.0


def test_cloud_cover_mapped():
    dates = ["2022-06-15"]
    payload = _open_meteo_payload(dates, temp_mean=10.0)
    from unittest.mock import patch
    with patch("requests.get", return_value=_mock_response(payload)):
        result = get_daily_weather("LON", 51.5, -0.1, "2022-06-15", "2022-06-15")
    assert result[0]["cloud_cover_pct"] == 60.0


def test_write_weather_csv_row_count(tmp_path):
    records = [
        {"date": f"2022-01-0{i}", "location_id": "LON", "temperature_max_c": 12.0,
         "temperature_min_c": 6.0, "temperature_mean_c": 9.0, "wind_speed_mean_ms": 4.2,
         "cloud_cover_pct": 70.0, "precipitation_mm": 2.5}
        for i in range(1, 4)
    ]
    out = str(tmp_path / "weather.csv")
    write_weather_csv(records, out)
    with open(out) as f:
        lines = f.readlines()
    assert len(lines) == 4  # header + 3 data rows


def test_precipitation_mapped():
    dates = ["2022-06-15"]
    payload = _open_meteo_payload(dates, temp_mean=10.0)
    with patch("requests.get", return_value=_mock_response(payload)):
        result = get_daily_weather("LON", 51.5, -0.1, "2022-06-15", "2022-06-15")
    assert result[0]["precipitation_mm"] == 1.2


def test_wind_speed_mapped():
    dates = ["2022-06-15"]
    payload = _open_meteo_payload(dates, temp_mean=10.0)
    with patch("requests.get", return_value=_mock_response(payload)):
        result = get_daily_weather("LON", 51.5, -0.1, "2022-06-15", "2022-06-15")
    assert result[0]["wind_speed_mean_ms"] == 3.5


def test_get_daily_weather_date_matches():
    dates = ["2022-06-15"]
    payload = _open_meteo_payload(dates, temp_mean=10.0)
    with patch("requests.get", return_value=_mock_response(payload)):
        result = get_daily_weather("LON", 51.5, -0.1, "2022-06-15", "2022-06-15")
    assert result[0]["date"] == "2022-06-15"
