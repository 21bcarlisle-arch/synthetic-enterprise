"""Retrieval of historical daily weather over a date range, from Open-Meteo.

Historical Ground Truth law: this hits the real Open-Meteo Historical Weather
Archive API (archive-api.open-meteo.com) — real reanalysis-model data, no
invented values. See docs/data-sources/weather.md for the full provenance and
decision record (why Open-Meteo, the endpoint shape, grid-snapping behaviour).

Maps Open-Meteo's daily variable names to this project's schema field names:
  time -> date, temperature_2m_max -> temperature_max_c,
  temperature_2m_min -> temperature_min_c, temperature_2m_mean ->
  temperature_mean_c, wind_speed_10m_mean -> wind_speed_mean_ms,
  cloud_cover_mean -> cloud_cover_pct, precipitation_sum -> precipitation_mm.
"""

import csv
import os

import requests


class WeatherArchiveRefusal(RuntimeError):
    """The archive could not be retrieved or written, with the reason named.

    A DISTINCT type (the `background/egress_allowlist.py` idiom), because the two callers
    below want opposite things from a failure: the pull script must stop, and a test must
    be able to assert the refusal fired rather than assert on an empty list that a silent
    success also produces.
    """


def _existing_row_count(output_path: str) -> int | None:
    """Data rows already at `output_path`, or None if there is nothing there to protect.

    Counts DATA rows, not lines: a header-only file is 0, which is what makes an already
    truncated archive replaceable by a real pull rather than permanently wedged.
    """
    if not os.path.exists(output_path):
        return None
    with open(output_path, newline="") as f:
        return sum(1 for _ in csv.DictReader(f))


def _response_reason(response) -> str:
    """Open-Meteo's own `reason` string, or the raw body if it is not the shape we expect.

    The reason is the load-bearing part: "Daily API request limit exceeded" is a wait,
    and a bad bounding box is a bug, and an HTTP code alone cannot tell the two apart.
    """
    try:
        return str(response.json().get("reason", response.text))
    except (ValueError, AttributeError):
        return str(getattr(response, "text", ""))


def get_daily_weather(location_id: str, latitude: float, longitude: float,
                      start_date: str, end_date: str) -> list[dict]:
    """
    Retrieves daily weather data from the Open-Meteo Historical Weather Archive API.

    Args:
        location_id (str): Identifier for the location.
        latitude (float): Latitude of the location.
        longitude (float): Longitude of the location.
        start_date (str): Start date in YYYY-MM-DD format.
        end_date (str): End date in YYYY-MM-DD format.

    Returns:
        list[dict]: List of dictionaries, each containing weather data for a single day.
    """
    base_url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "daily": "temperature_2m_max,temperature_2m_min,temperature_2m_mean,wind_speed_10m_mean,cloud_cover_mean,precipitation_sum",
        "wind_speed_unit": "ms",
        "timezone": "Europe/London"
    }

    response = requests.get(base_url, params=params)

    if response.status_code != 200:
        # FAIL CLOSED, NAMING THE REASON. This returned `[]` until 2026-09-06, and
        # `write_weather_csv` below then wrote a header-only CSV over the destination: a
        # rate-limited pull DESTROYED ten years of real weather and exited 0. Found by
        # running it — Open-Meteo answered 429 "Daily API request limit exceeded", the
        # two new sites came back with 0 records, and nothing anywhere said so.
        raise WeatherArchiveRefusal(
            f"Open-Meteo refused the archive for {location_id!r} "
            f"({latitude}, {longitude}) {start_date}..{end_date}: "
            f"HTTP {response.status_code} — {_response_reason(response)}"
        )

    data = response.json()
    daily_data = data["daily"]

    records = []
    for i in range(len(daily_data["time"])):
        record = {
            "date": daily_data["time"][i],
            "location_id": location_id,
            "temperature_max_c": daily_data["temperature_2m_max"][i],
            "temperature_min_c": daily_data["temperature_2m_min"][i],
            "temperature_mean_c": daily_data["temperature_2m_mean"][i],
            "wind_speed_mean_ms": daily_data["wind_speed_10m_mean"][i],
            "cloud_cover_pct": daily_data["cloud_cover_mean"][i],
            "precipitation_mm": daily_data["precipitation_sum"][i]
        }
        records.append(record)

    return records


def write_weather_csv(records: list[dict], output_path: str) -> None:
    """
    Writes the given weather records to a CSV file.

    Args:
        records (list[dict]): List of dictionaries containing weather data.
        output_path (str): Path to the output CSV file.
    """
    fieldnames = [
        "date", "location_id", "temperature_max_c", "temperature_min_c",
        "temperature_mean_c", "wind_speed_mean_ms", "cloud_cover_pct", "precipitation_mm"
    ]

    # TWO REFUSALS, because they catch different failures and the first alone is not enough.
    # An empty pull is never a legitimate archive: `mode='w'` truncates, so writing zero rows
    # over `sim/weather_data/C1.csv` is how a transport error becomes data loss.
    if not records:
        raise WeatherArchiveRefusal(
            f"refusing to write an EMPTY archive to {output_path!r} — an archive with no "
            f"days is never a real answer, and this path may already hold a real one"
        )
    # A SHORT pull is the one the emptiness check misses: the API can answer 200 with a
    # truncated range, and that silently shrinks ten years to three days.
    existing = _existing_row_count(output_path)
    if existing is not None and len(records) < existing:
        raise WeatherArchiveRefusal(
            f"refusing to SHRINK the archive at {output_path!r}: {existing} days on disk, "
            f"{len(records)} days retrieved. Delete the file deliberately if the shorter "
            f"pull is genuinely the one you want."
        )

    with open(output_path, mode='w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for record in records:
            writer.writerow(record)

