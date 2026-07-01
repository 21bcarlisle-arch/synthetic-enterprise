# Proposed Phase MV — Coverage Depth Sprint CXX

**Drafted:** 2026-07-01T10:46:07Z
**4-hour opt-out window expires:** ~2026-07-01T14:46:07Z

## Summary
Deepen test coverage across three sim/ modules that currently have 4-8 tests
and contain additional testable logic: `sim/forward_curve.py`,
`sim/gas_scenario_generator.py`, and `sim/bimodal_generator.py`.

## Why these modules
- `sim/forward_curve.py` — 8 tests. New seasonal_calibration.json (Phase MS)
  adds testable paths: load_seasonal_calibration(), calibrated multiplier
  lookup, fallback for unknown tenor, crisis year (2022) returns elevated
  value, calibrated vs uncalibrated seasonal diff.
- `sim/gas_scenario_generator.py` — 4 tests (very shallow given its
  complexity). Testable: scenario_count constant, generate_gas_scenarios
  returns N scenarios, each scenario has required keys (scenario_name,
  price_shock, volume_shock), base scenario has zero shocks, severe scenario
  has larger shocks than mild.
- `sim/bimodal_generator.py` — 16 tests (modest). Can add: peak/off-peak
  boundary SPs, weekday vs weekend split, annual total sums to consumption,
  HH output length is always 48.

## Target
30 new tests, total 13,063.

## Files to create
- `tests/sim/test_phase_mv_coverage_cxx.py` — 30 tests

## Epistemic note
All three modules are pure physics/calibration — no company-layer reads,
no PIT issues.
