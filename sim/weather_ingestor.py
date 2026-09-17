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


class WeatherQuotaExhausted(WeatherArchiveRefusal):
    """A limit whose reset NO backoff inside this run can outlive, so the run must stop.

    A SUBCLASS on purpose: every existing `except WeatherArchiveRefusal` keeps catching it
    unchanged, and only a caller that wants the distinction has to know the name.

    WHY THE DISTINCTION IS WORTH A TYPE, measured 2026-09-17. Open-Meteo enforces THREE limits
    behind the SAME 429, and only its `reason` string separates them: a minutely burst limit,
    which `tools/build_weather_world.PAUSE_SECONDS` was measured against and which a pause does
    clear, and the hourly and daily ones, which nothing inside a per-cell backoff reaches.
    `_fetch_with_backoff` asked `"429" not in str(exc)` and so retried all of them identically --
    four backoffs totalling six minutes PER CELL against limits six minutes cannot reach. A
    23-cell resume run under an exhausted daily quota spends about two and a quarter hours
    sleeping, writes nothing, and reports 23 refusals whose shared cause appears nowhere in the
    summary.

    THE HOURLY LIMIT WAS ON THE WRONG SIDE OF THAT SPLIT UNTIL 2026-09-17, and it was found by
    hitting it. This class and `_is_daily_quota` were written naming exactly two limits -- "a
    burst limit" and "the daily quota" -- so the live reason "Hourly API request limit exceeded.
    Please try again in the next hour." matched neither and fell through to the retry path. That
    is the SAME defect one axis over: six minutes of backoff against a reset up to fifty-nine
    minutes away. Named here because the two-limit sentence above is what made the third
    invisible, and a reader who trusts it will reintroduce the hole.
    """

    def __init__(self, message: str, reset_seconds: float | None = None):
        super().__init__(message)
        #: How long until the limit that refused resets, so the caller can say WHICH wait it is
        #: rather than printing "come back tomorrow" for an hourly bucket. `None` when the reason
        #: is one we do not recognise and the horizon is genuinely unknown.
        self.reset_seconds = reset_seconds


#: Open-Meteo's own words for each limit it enforces, mapped to HOW LONG that limit takes to
#: reset. Lowercased for comparison, and each key is a PREFIX of the live string (the daily one
#: continues "... Please try again tomorrow.") so a change to the trailing advice does not
#: silently reclassify the limit.
#:
#: MATCHED ON THE REASON, NOT THE STATUS: the status is 429 for all three, which is exactly the
#: confusion this exists to end. ORIGIN: Open-Meteo's published free-tier limits, recorded in
#: docs/data-sources/weather.md -- 600/minute, 5,000/hour, 10,000/day. The horizons are the
#: bucket periods themselves and are upper bounds: a limit hit at 07:39 resets at 08:00, not
#: 08:39, so the true wait is never longer than the figure here.
LIMIT_RESET_SECONDS = {
    "minutely api request limit exceeded": 60.0,
    "hourly api request limit exceeded": 3600.0,
    "daily api request limit exceeded": 86400.0,
}

#: The longest reset a per-cell backoff is permitted to try to sleep through. KEYED TO THE
#: PROPERTY rather than to the list above: the question a caller actually has is "can I wait this
#: out", and answering it by enumerating which limits are 'quotas' is what put the hourly one on
#: the retry path. `tools/build_weather_world` spends 60+120+180 = 360s across its four attempts,
#: so 600s is that budget with room to spare -- any limit resetting slower than this is a stop.
#: A fourth Open-Meteo limit appearing with a minute-scale reset therefore classifies itself.
CLEARABLE_BY_BACKOFF_SECONDS = 600.0


def _reset_seconds(reason: str) -> float | None:
    """How long the limit named in `reason` takes to reset, or None if it names no known limit."""
    lowered = reason.lower()
    return next((secs for phrase, secs in LIMIT_RESET_SECONDS.items() if phrase in lowered), None)


def _is_daily_quota(reason: str) -> bool:
    """Whether the limit named outlasts any backoff, so the caller must stop rather than retry.

    THE NAME IS KEPT AND IT IS NOW WRONG ON ITS FACE -- "daily" is one of two limits this answers
    True for. Left as-is deliberately: renaming it is a wider edit than this repair earns, and a
    reader who takes the name literally is exactly the reader the docstring above needs to catch.
    An unrecognised reason is retryable, which is the fail-SAFE direction here: a wrongly retried
    refusal costs six minutes, a wrongly stopped run costs the whole pull.
    """
    reset = _reset_seconds(reason)
    return reset is not None and reset > CLEARABLE_BY_BACKOFF_SECONDS


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
        reason = _response_reason(response)
        # THE TYPE IS CHOSEN HERE, where the reason is read, and nowhere else. A caller that
        # re-sniffs the message string would be a second place to keep in step with Open-Meteo's
        # wording, and the first one already drifted once -- then drifted again, which is how the
        # hourly limit spent a day on the retry path. See `WeatherQuotaExhausted`.
        message = (
            f"Open-Meteo refused the archive for {location_id!r} "
            f"({latitude}, {longitude}) {start_date}..{end_date}: "
            f"HTTP {response.status_code} — {reason}"
        )
        if _is_daily_quota(reason):
            raise WeatherQuotaExhausted(message, reset_seconds=_reset_seconds(reason))
        raise WeatherArchiveRefusal(message)

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

