Project Status

Last updated: 2026-06-27T08:30:00Z
Current phase: Phase B COMPLETE (2026-06-27). 4,626 tests passing.

Current state:

Phase B (2026-06-27): Life events engine
  simulation/life_events.py: LifeEvent frozen dataclass; generate_life_events();
  apply_events(); household_at_date(). Calibrated to UK probability tables
  (solar 3% to 5.7%, EV 0.3% to 7%, ASHP 0.1% to 0.6%, boiler by age).
  32 new tests (4,626 total).

Phase A (2026-06-27): Household physical model
  simulation/household.py: Household frozen dataclass (PropertyType/BuildEra/
  HeatingSystem/BoilerAge/InsulationLevel enums; epc_consumption_multiplier
  calibrated to EHS 2022-23; seasonal_flatness_factor; ev_annual_kwh;
  solar_annual_generation_kwh). make_household() + build_household_register()
  covers all 18 customers. 36 new tests (4,594 total).

Phase 332 (2026-06-27): Risk Committee Deterministic Engine
  sim/risk_committee_rules.py: parse_handshake/should_escalate/apply_rules/decide.
  Rule engine: +0.15/0.20/0.25 step by VaR ratio; escalates to LLM only if sigma>1.5
  or all customers maxed. Removes ~95% of Ollama calls per run.
  21 new tests (4,559 total).

Latest simulation results (2016-2025):
  Net margin: 6,322,835 GBP | Gross: 6,559,771 GBP | Capital: 236,935 GBP
  Treasury: 2,466,636 to 3,796,762 GBP | 38 committee interventions
  Enterprise value: 6,124,101 GBP | 1,531 bills issued

Five hollow gaps: all closed or deepened.
  1. Customer events: DEEPENED (life events + household model, Phases A/B)
  2. Ledger: CLOSED (Phase 7a/7b)
  3. SIM/company barrier: CLOSED (epistemic verifier passes)
  4. HH data path: CLOSED (Phase 6a)
  5. Reporting: CLOSED (Phase 5a/5b)

Next: Phase C -- Household-Driven EAC Integration (proposed 2026-06-27)
  Wire Phase A/B household model into settlement loop.
  EPC rating, EV ownership, solar installs will affect consumption.

4,626 tests passing.

Report: https://21bcarlisle-arch.github.io/synthetic-enterprise/reports/ANNUAL_REPORT.md
Status: https://raw.githubusercontent.com/21bcarlisle-arch/synthetic-enterprise/main/docs/status/LATEST.md
