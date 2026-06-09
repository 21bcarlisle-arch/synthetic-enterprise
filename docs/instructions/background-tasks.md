# Background Task Queue

Tasks in QUEUED status will be picked up by background/background_worker.py
during off-peak hours (not between 16:00-19:00 GMT).
Tasks move to RUNNING then DONE. Worker logs to docs/observability/background-worker-log.md.

---

## QUEUED

### Task: pre-fetch-elexon-full
Description: Fetch and cache full Elexon SSP/SBP settlement data for 2016-01-01 to 2025-06-07.
Store as parquet in sim/cache/elexon_ssp_full.parquet.
Use sim/system_prices.py as the base — extend to support date range batching.
Model: qwen2.5-coder:14b
Output: sim/cache/elexon_ssp_full.parquet + docs/observability/cache-status.md

### Task: pre-fetch-weather-full
Description: Fetch and cache Open-Meteo historical daily weather for all four customer locations, 2016-01-01 to 2025-06-07.
Locations: London (51.51,-0.12), Manchester (53.48,-2.24), Glasgow (55.86,-4.25), Cotswolds (51.83,-1.83).
Fields: temperature_max_c, temperature_min_c, temperature_mean_c, wind_speed_mean_ms, cloud_cover_pct, precipitation_mm.
Store as sim/weather_data/{location}.csv (update existing files if partial).
Model: qwen2.5-coder:14b
Output: sim/weather_data/*.csv updated + entry in docs/observability/cache-status.md

### Task: pre-fetch-pc3-profiles
Description: Download PC3 Standard Load Profile data from Elexon portal (portal.elexon.co.uk).
Same DTC pipe-delimited format as PC1. Parse for profile_class='03'.
Store as sim/profiles/pc3_coefficients.csv with columns: season, day_type, period_1..period_48.
Model: qwen2.5-coder:14b
Output: sim/profiles/pc3_coefficients.csv + docs/data-sources/profile-class-3.md

### Task: pre-fetch-nbp-gas-full
Description: Fetch historical NBP System Average Price (SAP) from NGT MIPI API.
Endpoint: https://mipidata.nationalgas.com/api
Fields: ApplicableFor (gas day), Value (p/kWh), DataItemName.
Date range: 2016-01-01 to 2025-06-07. Store as sim/gas_data/nbp_sap.csv.
Model: qwen2.5-coder:14b
Output: sim/gas_data/nbp_sap.csv + docs/data-sources/gas-nbp.md

### Task: code-quality-audit
Description: Review all Python files in sim/ and saas/ for open-doors violations:
- Hardcoded 'electricity' commodity assumptions
- Missing data_regime field on any record-producing function
- Implicit assumptions that a position can only be positive (not negative)
- Any hardcoded CV or calorific value constants not stored as config
Produce a findings report only — do not change any code.
Model: qwen2.5:7b
Output: docs/observability/code-quality-audit.md

### Task: simulation-sensitivity-experiments
Description: Run the Phase 1e simulation (simulation/run_phase1e.py) with three parameter variants.
Do not modify the main simulation — create simulation/run_sensitivity.py that imports and overrides params.
Variants to test:
  A: WACC=0.15 (expensive debt scenario)
  B: Starting treasury=£1,000 (thin capitalisation)
  C: sigma_stressed_pre2023=0.75 (tighter pre-reform floor)
For each variant log: did administration trigger? Final treasury? Net 9yr margin?
Model: qwen2.5-coder:14b for script, qwen2.5:7b for results summary
Output: docs/observability/sensitivity-results.md

---

## RUNNING
(none)

## DONE
(none)
