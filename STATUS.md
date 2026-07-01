Project Status

Last updated: 2026-07-01T20:10:00Z
Current phase: Phase MV COMPLETE (2026-07-01). 13,949 tests passing.

Current state:

Phase MV (2026-07-01): Economic Life Events
  simulation/household: IncomeStress enum LOW/MODERATE/HIGH; income_stress field default=LOW.
  simulation/life_events: EventType +job_loss/income_recovery/new_baby/retirement_starts.
  household_demand: income_stress_at_date(). 20 new tests (13,949 total).

Phase MU (2026-07-01): Coverage Depth Sprint CXIX
  sim/hedging_strategy: EVOLUTION_STEP, MARGIN_TOLERANCE_GBP, hold_at_exact boundaries.
  sim/risk_engine: Z_SCORE, WACC, sigma_recent_float, bootstrap_fallback, var_formula.
  sim/weather_price_sensitivity: HDD_THRESHOLD, BASELINE, MULTIPLIER, boundary tests.
  30 new tests (13,033 total).

Phase MT (2026-07-01): I&C Triad Demand Curtailment
  simulation/triad.py: build_triad_alert_set (SSP>80 + Triad season + SP 33-39).
  make_triad_aware_shape_fn: 25% load reduction for I&C HH customers in Triad windows.
  27 new tests (13,003 total).

Latest simulation results (2016-2025):
  Net margin: £6,174,052 | Gross: £6,411,912 | Capital: £237,860
  Treasury: £2,466,636 -> £3,684,796 | Enterprise value: £5,982,075

Five hollow gaps: all closed.
  1. Customer events: DEEPENED (life events + household model, Phases A/B)
  2. Ledger: CLOSED (Phase 7a/7b)
  3. SIM/company barrier: CLOSED (epistemic verifier passes)
  4. HH data path: CLOSED (Phase 6a)
  5. Reporting: CLOSED (Phase 5a/5b)

Capability gaps (new framing):
  Gap 1 Real Forward Curve: CLOSED (Phase MS, 2026-07-01)
  Gap 2 I&C Triad Curtailment: CLOSED (Phase MT, 2026-07-01)
  Gap 3 Human Simulation Layer: IN PROGRESS
    MV: IncomeStress enum + economic life events (job_loss, income_recovery, new_baby, retirement_starts)
    MW (proposed): wire income_stress -> observable payment behaviour (opt-out expires 23:10Z)

Next: Phase MW (opt-out window expires 2026-07-01T23:10Z)
  job_loss -> income_stress HIGH -> LATE/DD_FAILED payment records -> company PaymentBehaviourAnalytics.
  25 new tests (target ~13,974).

14,460 tests passing (full suite, inc coverage depth sprints).

Report: https://21bcarlisle-arch.github.io/synthetic-enterprise/reports/ANNUAL_REPORT.md
Status: https://raw.githubusercontent.com/21bcarlisle-arch/synthetic-enterprise/main/docs/status/LATEST.md
