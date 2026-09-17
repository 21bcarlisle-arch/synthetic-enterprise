# Historical Weather Data Source — Open-Meteo Archive API

Decision record for where and how daily historical weather data (2016-2025) for the four customer locations defined in `saas/customers.py` is sourced, retrieved, and stored. This choice adheres to the spirit of the Historical Ground Truth law by ensuring real, citable, and reproducible data.

## What This Is For

Phase 1b requires daily historical weather data (2016-2025) for four customer locations to store now and correlate with consumption later. Phase 1b explicitly does not perform correlation yet; this is future backlog work.

## Why Open-Meteo?

### Free, No API Key Required
Open-Meteo's Historical Weather Archive API ("Archive API") provides free access without the need for an API key. This significantly reduces operational costs and simplifies integration.

### Rate Limits — and Why the Sentence That Used To Be Here Was Wrong

This section previously read *"There were no rate-limit issues encountered, ensuring smooth data
retrieval."* That was true of the probe it described — **four** locations — and it stopped being
true the moment the per-cell store made this a **221-cell** pull. It was still here on 2026-09-17,
when the limits had already cost two sessions a combined ~2h20m. Corrected rather than deleted,
because the sentence is why nobody looked.

**Published free-tier limits** (open-meteo.com [pricing](https://open-meteo.com/en/pricing) and
[terms](https://open-meteo.com/en/terms), both read 2026-09-17, figures agreeing):

| window | limit |
|---|---|
| minute | 600 calls |
| hour | 5,000 calls |
| day | 10,000 calls |
| month | 300,000 calls |

**A request is NOT one call.** Per the pricing page: *"Requests for data covering more than 10
weather variables or extending over a period of more than 2 weeks for a single location are
considered multiple API calls"* — each further 2-week period adds 1.0, each variable beyond 10 adds
0.1. Their worked example: 2 weeks × 15 variables = 1.5 calls; 4 weeks = 3.0 calls.

**What that makes one cell of this project's pull cost.** One cell is 2016-01-01..2025-12-31 =
3,653 days at 6 daily variables. Six is under ten, so there is no variable surcharge, and the cost
is the window: `3653 / 14 = 260.9 calls per cell`. The ceilings that follow:

| window | cells |
|---|---|
| minute | **2.3** |
| hour | **19.2** |
| day | **38.3** |

**Cross-checked against our own record, and it is the HOURLY limit that has been biting.** The
resume in `f94ebb1d2` completed **21 cells and then stopped** — against a predicted hourly ceiling
of 19.2, a ~9% miss, and nowhere near the daily 38.3. The stop was attributed at the time to "the
rate limiter" and then, on 2026-09-17, to the daily quota; the arithmetic says the daily quota is
what a *day* of such runs exhausts, while what ends any *single* run at ~19 cells is the hourly
bucket.

Three consequences for anyone planning a pull:

1. **A 23-cell pass fits in a day (38.3) but not in an hour (19.2).** It needs two passes roughly
   an hour apart, not two days.
2. **`tools/build_weather_world.RETRY_BACKOFF_SECONDS` cannot clear an hourly limit.** Four
   attempts at 60/120/180 s is six minutes against a bucket that refills over sixty. The cells past
   the hourly ceiling will be recorded as ordinary refusals and must be picked up by a later run —
   which is safe, because `build` is resumable by construction, but it is not the same thing as the
   run having failed.

   **CLOSED IN CODE 2026-09-17, and this paragraph is why it was found.** The sentence above
   described the hole correctly and left it open: `_is_daily_quota` matched only *"daily api
   request limit exceeded"*, so an hourly 429 was classified as a burst limit and took the retry
   path — the identical defect `WeatherQuotaExhausted` was minted to close for the daily quota,
   one axis over, on the limit that actually fires. `sim.weather_ingestor` now classifies all
   three limits by **reset horizon** (`LIMIT_RESET_SECONDS`) rather than by enumerating which ones
   count as quotas, so the hourly limit stops the run and names the top of the hour as the wait.
   A fourth limit with a minute-scale reset classifies itself. Control:
   `tests/sim/test_weather_ingestor.py::test_the_hourly_limit_is_a_stop_and_not_a_retry_like_the_minutely_one`.
3. **`PAUSE_SECONDS = 20.0` sits just under the published minutely floor** of `60 / 2.3 = 26.1 s`
   per cell. It is left at 20.0 deliberately: 21 consecutive cells went through at that pause
   without a minutely refusal, so the measurement refutes the arithmetic here and the arithmetic
   alone is not grounds to slow every future pull down by 30%. Recorded so the next reader knows
   the gap is known rather than unnoticed.

**CONSEQUENCE 1 IS REFUTED, AND SO IS THE HOURLY ATTRIBUTION ABOVE IT. Corrected beside the claim
rather than over it, 2026-09-17, by the pull it was written to plan.** The 23-cell pass ran
08:07–08:18 and completed **all 23 cells in eleven minutes with zero 429s** — one pass, not two an
hour apart. By this page's own arithmetic that is ~6,000 call-units inside eleven minutes, against
a stated hourly ceiling of 5,000; and with the 21 cells of `f94ebb1d2` at 05:26 the same day, 44
cells against a stated daily 38.3. Both ceilings were passed without a single refusal.

So the cell ceilings in the table above are **not established**, and no plan should be built on
19.2/hour or 38.3/day. The suspect term is the per-cell cost: one cell is **one HTTP request**
(`sim.weather_ingestor.get_daily_weather`, no cache), and the `3653 / 14 = 260.9` weighting is the
only part of the sum nothing here has measured. Consequence 3 already recorded the same direction
of error at the minute scale; this is that finding at the hour and the day.

What survives is what the code relies on and nothing more: the 02:38 refusal was real, it refused
every cell alike, and it cleared with time rather than with backoff. Measurement:
`docs/staging/records/WORKER_RESULT_THE_LAST_23_IN_BOOK_CELLS_PULLED_IN_ELEVEN_MINUTES_AND_THE_HOURLY_CEILING_DERIVED_FROM_THE_PUBLISHED_RULE_IS_REFUTED_2026-09-17.md`.

**THE CEILING IS REFUTED; THE PER-CELL COST IS NOT — and the block above names the wrong suspect.**
Written by a second lane the same hour, from a measurement the block above did not have, and kept
beside it rather than over it because only one of its two claims moves.

At **07:39 UTC**, fifteen minutes after that 23-cell pass finished and with no other pull against
this key in between, a bare **two-day** probe was refused: *"Hourly API request limit exceeded.
Please try again in the next hour."* If one cell cost one call, 23 calls could not empty a
5,000/hour bucket — the bucket would have been all but untouched. **The bucket was empty, so the
per-cell cost is of the order the `3653 / 14 = 260.9` weighting predicts, not 1.** "One cell is one
HTTP request" is true and is not the same claim as "one cell is one *call*": Open-Meteo's published
rule weights a request by its window, and that is the term the 07:39 refusal confirms rather than
refutes.

What is genuinely refuted is **19.2 as a cut-off**. The reconciliation is that the hourly limit is
enforced **on the bucket, not on the request that overdraws it**: a run may spend past 5,000 and
only the *next* caller is refused. So 19.2 is a rate the bucket sustains, not a count any single
run is stopped at — which is exactly why a 23-cell pass finished clean and still left nothing for
the next caller thirteen minutes later. Both observations are consistent; neither ceiling should be
quoted as a hard stop, and neither should the per-cell cost be dropped from the arithmetic.

The refusal for **any limit a backoff cannot outlive** is a distinct type —
`sim.weather_ingestor.WeatherQuotaExhausted` — and is matched on Open-Meteo's `reason` string,
never on the 429 status, because all three limits above return the same status. The three reasons
and their reset horizons are `LIMIT_RESET_SECONDS`; anything resetting slower than
`CLEARABLE_BY_BACKOFF_SECONDS` (600 s) stops the run, so the minutely limit is retried and the
hourly and daily ones are not. An unrecognised reason stays **retryable** on purpose: a wrongly
retried refusal costs six minutes, a wrongly stopped run costs the whole pull.

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