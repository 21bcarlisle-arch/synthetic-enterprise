Project Status

Last updated: 2026-07-01T11:37Z
Current phase: Phase MU COMPLETE (2026-07-01). 13,033 tests passing.

Current state:

Phase MU (2026-07-01): Coverage Depth Sprint CXIX
  sim/hedging_strategy: EVOLUTION_STEP, MARGIN_TOLERANCE_GBP, hold_at_exact boundaries.
  sim/risk_engine: Z_SCORE, WACC, sigma_recent_float, bootstrap_fallback, var_formula.
  sim/weather_price_sensitivity: HDD_THRESHOLD, BASELINE, MULTIPLIER, boundary tests.
  30 new tests (13,033 total).

Phase MT (2026-07-01): I&C Triad Demand Curtailment
  simulation/triad.py: build_triad_alert_set (SSP>80 + Triad season + SP 33-39).
  make_triad_aware_shape_fn: 25% load reduction for I&C HH customers in Triad windows.
  run_phase2b.py wired for I&C HH customers. triad_notification_book.get_active_alerts.
  27 new tests (13,003 total).

Phase MS (2026-07-01): Real NBP Forward Curve
  forward_curve.py seasonal multipliers now data-derived (Elexon SSP + TTF proxy 2016-2024).
  sim/data/seasonal_calibration.json added. Gas Dec 1.294 (was 1.20), Elec Dec 1.257 (was 1.12).
  Crisis years (2022) included. 16 new tests (12,976 total).

Latest simulation results (2016-2025):
  Net margin: £6,174,052 | Gross: £6,411,912 | Capital: £237,860
  Treasury: £2,466,636 -> £3,684,796 | 38 committee interventions | 1,531 bills
  Enterprise value: £5,982,075 | Net after CTS: £6,307,559

Five hollow gaps: all closed.
  1. Customer events: DEEPENED (life events + household model, Phases A/B)
  2. Ledger: CLOSED (Phase 7a/7b)
  3. SIM/company barrier: CLOSED (epistemic verifier passes)
  4. HH data path: CLOSED (Phase 6a)
  5. Reporting: CLOSED (Phase 5a/5b)

Capability gaps (new framing):
  Gap 1 Real Forward Curve: CLOSED (Phase MS, 2026-07-01)
  Gap 2 I&C Triad Curtailment: CLOSED (Phase MT, 2026-07-01)
  Gap 3 Human Simulation Layer: OPEN -- property/EPC/income dimensions not yet built

Next: Phase MV (Coverage Depth Sprint CXX) -- opt-out window expires 14:46 UTC 2026-07-01.
  After MV: Human Simulation Layer Dim 1 (property/EPC -> seasonal demand scalar).

13,033 tests passing.

Report: https://21bcarlisle-arch.github.io/synthetic-enterprise/reports/ANNUAL_REPORT.md
Status: https://raw.githubusercontent.com/21bcarlisle-arch/synthetic-enterprise/main/docs/status/LATEST.md
