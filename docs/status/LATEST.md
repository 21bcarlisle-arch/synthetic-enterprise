# LATEST -- Synthetic Enterprise Simulation
Last updated: 2026-07-01T16:39:57Z

## Current Status
**Coverage sprints ongoing** -- 13,560+ tests

## Last Run
See docs/reports/run_output_latest.json.
Net position: £1,218,159 (git d80bd064, 2026-07-01)

## Test Suite
- **13,560+ tests passing** (fast suite ~10s)
- Epistemic verifier: PASS

## Recent Phases
- **MV** (2026-07-01): Economic Life Events -- IncomeStress enum, job_loss/income_recovery/new_baby/retirement_starts, econ_rng isolation
- **MU** (2026-07-01): Coverage Depth Sprint CXIX -- sim/hedging_strategy, sim/risk_engine, sim/weather_price_sensitivity (13,033 tests)
- **MT** (2026-07-01): I&C Triad Demand Curtailment -- build_triad_alert_set/make_triad_aware_shape_fn/get_active_alerts (13,003 tests)
- **MS** (2026-07-01): Real NBP Forward Curve -- seasonal multipliers data-derived (12,976 tests)

**Latest simulation results (2016-2025)** -- auto-processed (620s / 10 min):
- Net margin: 1,218,159 GBP | Gross: 6,398,145 GBP | Capital: 237,860 GBP
- Treasury: 2,466,636 GBP -> 3,566,652 GBP | 38 committee interventions | 1531 bills issued
- Enterprise value: 5,982,075 GBP | Revenue: 13,992,278 GBP
