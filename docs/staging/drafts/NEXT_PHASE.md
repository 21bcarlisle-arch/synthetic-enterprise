Phase 271 -- /sim/ Section: Weather Engine & Heating Degree Days

Status: PROPOSED (2026-06-26T18:30Z)
4h opt-out window: expires 2026-06-26T22:30Z

Context:
Phase 270 (Qwen NL query) was an urgent Rich request that superseded the
original Phase 270 proposal. The Weather Engine remains the highest-priority
unbuilt /sim/ item. The /sim/ section (Phase 268) shows wholesale prices
but has no weather data -- yet weather is the primary demand driver for gas
and the key explanation for why 2021-22 prices spiked.

Goal:
Add a Weather tab to site/sim/index.html showing 10 years of UK temperature and
Heating Degree Days (HDD) data, wired to process_run_complete so it auto-refreshes.

Design:
- tools/fetch_weather_data.py (new):
  Fetches daily mean temps from Open-Meteo historical archive API for 2016-2025 (London).
  Computes monthly HDD = sum(max(0, 15.5 - daily_mean_temp)) per month.
  (15.5C is the UK National Grid base temperature for demand forecasting.)
  Computes monthly mean temp and CDD. Stores to site/data/weather.json.
  process_run_complete.py: call on every run (guard with try/except for network errors).

- site/sim/index.html -- Weather tab:
  Monthly mean temperature line chart (10-year, 2016-2025), colour-coded by year.
  Monthly HDD bar chart with 10-year average overlay.
  6 KPI cards: coldest month, warmest month, highest annual HDD, 2022 vs avg HDD %,
  2022 peak HDD month, avg UK base temperature.
  Annual HDD table with COLD WINTER badge for years above 10-yr-average.
  Narrative card explaining 2021/22 crisis: cold winter + storage depletion.

Tests: tests/tools/test_fetch_weather_data.py (~8 tests)
  - weather.json written with monthly/annual keys
  - HDD non-negative, monthly mean temp in plausible range (-5 to 30C)
  - All months present 2016-2025
  - 2022 annual HDD reasonable (1500-2500 for London)
  - Network error falls back gracefully (mock requests)
  - HDD highest in Dec/Jan/Feb, lowest in Jun/Jul/Aug
  - process_run_complete integration

Estimated: ~8 tests, ~150 lines Python, ~100 lines JS

Why this over other items:
The weather engine closes a genuine fidelity gap -- the /sim/ section explains WHAT
prices did but not WHY (weather-driven demand). The monthly assessment is housekeeping;
the weather engine is simulation depth.
