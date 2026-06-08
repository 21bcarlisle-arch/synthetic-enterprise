# Historical Weather Data Source — Open-Meteo Archive API

Decision record for where and how daily historical weather data (2016-2025) for the four customer locations defined in `saas/customers.py` is sourced, retrieved, and stored. This choice adheres to the spirit of the Historical Ground Truth law by ensuring real, citable, and reproducible data.

## What This Is For

Phase 1b requires daily historical weather data (2016-2025) for four customer locations to store now and correlate with consumption later. Phase 1b explicitly does not perform correlation yet; this is future backlog work.

## Why Open-Meteo?

### Free, No API Key Required
Open-Meteo's Historical Weather Archive API ("Archive API") provides free access without the need for an API key. This significantly reduces operational costs and simplifies integration.

### Programmatically Reliable
The API has been tested and found to be reliable during probing. There were no rate-limit issues encountered, ensuring smooth data retrieval.

### Real Coverage of the Full Sim Window Confirmed by Direct Probe
A direct probe confirmed that Open-Meteo's archive data is available from at least 2015-11-01 through 2025-06-07. This fully covers the simulation window (2016-01-01 to 2025-06-07) with a margin either side, satisfying the Historical Ground Truth law.

### Underlying Data: Reanalysis Model
Open-Meteo's historical archive is based on reanalysis data (ERA5 / ERA5-Land blend), which is modelled and gridded historical weather. While this is not raw station observations, it is the standard, citable, open way to get multi-decade daily weather for arbitrary coordinates worldwide. This trade-off between practicality and raw data is similar to the choice made in `docs/data-sources/profile-class-1.md` for Profile Class 1 shapes.

### Citation
For more information about Open-Meteo's Historical Weather API, refer to their [source/about page](https://open-meteo.com/en/docs/historical-weather-api).

## The Exact Endpoint Shape

### Base URL
The base URL for the Archive API is:
```
https://archive-api.open-meteo.com/v1/archive
```

### Query Parameters
The query parameters used in requests are as follows:

- **latitude**: The latitude of the location (e.g., `51.49`).
- **longitude**: The longitude of the location (e.g., `-0.16`).
- **start_date**: The start date for the data retrieval in YYYY-MM-DD format (e.g., `2016-01-01`).
- **end_date**: The end date for the data retrieval in YYYY-MM-DD format (e.g., `2016-01-03`).
- **daily**: A comma-separated list of variable names to retrieve daily values (e.g., `temperature_2m_max,temperature_2m_min,temperature_2m_mean,wind_speed_10m_mean,cloud_cover_mean,precipitation_sum`).
- **wind_speed_unit=ms**: Forces wind speed output in meters per second (m/s) instead of the default kilometers per hour (km/h). This matches the schema's `_ms` field naming directly.
- **timezone=Europe/London**: Specifies the timezone for the data.

### Response Shape
The response is structured as follows:

```json
{
  "latitude": <float>,
  "longitude": <float>,
  "timezone": <string>,
  "daily_units": {
    "time": "iso8601",
    "temperature_2m_max": "°C",
    "temperature_2m_min": "°C",
    "temperature_2m_mean": "°C",
    "wind_speed_10m_mean": "m/s",
    "cloud_cover_mean": "%",
    "precipitation_sum": "mm"
  },
  "daily": {
    "time": [<string>],
    "temperature_2m_max": [<float>],
    "temperature_2m_min": [<float>],
    "temperature_2m_mean": [<float>],
    "wind_speed_10m_mean": [<float>],
    "cloud_cover_mean": [<int>],
    "precipitation_sum": [<float>]
  }
}
```

### Sample Real Response
For London (latitude=51.49, longitude=-0.16) from 2016-01-01 to 2016-01-03:
```json
{
  "latitude": 51.49,
  "longitude": -0.16,
  "timezone": "Europe/London",
  "daily_units": {
    "time": "iso8601",
    "temperature_2m_max": "°C",
    "temperature_2m_min": "°C",
    "temperature_2m_mean": "°C",
    "wind_speed_10m_mean": "m/s",
    "cloud_cover_mean": "%",
    "precipitation_sum": "mm"
  },
  "daily": {
    "time": ["2016-01-01", "2016-01-02", "2016-01-03"],
    "temperature_2m_max": [7.8, 10.1, 9.5],
    "temperature_2m_min": [-0.4, 7.6, 5.5],
    "temperature_2m_mean": [4.6, 9.2, 7.7],
    "wind_speed_10m_mean": [4.37, 6.46, 5.2],
    "cloud_cover_mean": [76, 94, 88],
    "precipitation_sum": [1.10, 5.70, 11.30]
  }
}
```

## Grid-Snapping Behaviour

Open-Meteo snaps the requested latitude and longitude to its nearest grid cell. The response echoes back the actual grid-cell coordinates used, which is normal reanalysis-model behaviour. This does not indicate a bug or location mismatch.

For example, requesting lat=51.5074/lon=-0.1278 returns lat=51.4938/lon=-0.1630 in the response.

## Mapping from Open-Meteo's Daily Variable Names to This Project's Schema Field Names

| Open-Meteo Variable Name | Project Schema Field Name |
|-------------------------|---------------------------|
| `temperature_2m_max`    | `temperature_max_c`       |
| `temperature_2m_min`    | `temperature_min_c`       |
| `temperature_2m_mean`   | `temperature_mean_c`      |
| `wind_speed_10m_mean`   | `wind_speed_mean_ms`      |
| `cloud_cover_mean`      | `cloud_cover_pct`         |
| `precipitation_sum`     | `precipitation_mm`        |

## Implementation and Data Storage

- **Implementation**: The data is retrieved using the code in `sim/weather_ingestor.py`.
- **Data Storage**: The historical weather data is stored in `sim/weather_data/`, with one CSV file per location.

By documenting these details, future developers can easily reproduce and understand the data source and its integration without needing to re-derive the choices made.