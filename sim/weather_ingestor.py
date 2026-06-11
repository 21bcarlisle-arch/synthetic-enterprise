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

import requests


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
        return []

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

    with open(output_path, mode='w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for record in records:
            writer.writerow(record)

