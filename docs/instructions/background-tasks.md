# Background Task Queue

Tasks in QUEUED status will be picked up by background/background_worker.py
during off-peak hours (not between 16:00-19:00 GMT).
Tasks move to RUNNING then DONE. Worker logs to docs/observability/background-worker-log.md.

---

## QUEUED




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

### Task: pre-fetch-pc3-profiles
Completed: 2026-06-11 14:30 UTC


### Task: pre-fetch-weather-full
Completed: 2026-06-11 14:00 UTC


### Task: pre-fetch-elexon-full
Completed: 2026-06-11 13:59 UTC


