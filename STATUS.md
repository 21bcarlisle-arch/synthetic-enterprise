Project Status

Last updated: 2026-06-29T21:15:24Z
Current phase: Phase W COMPLETE (2026-06-29). 5,003 tests passing.

Current state:

Phase W (2026-06-29): Gas Boiler Daily HDD Shape
  simulation/gas_settlement.py: resi/SME gas uses per-day HDD-weighted shape.
  70% space heating (scales with daily HDD / annual ref HDD), 30% DHW flat.
  Mirrors Phase I for ASHP electricity. I&C keeps monthly profile.
  run_phase2b.py: weather_factor_for_term removed (now internal to settlement).
  13 new tests (5,003 total).

Phase V (2026-06-29): ToU Migration Impact Scenario
  company/pricing/tou_migration_scenario.py: MigrationScenario/ToUMigrationScenarioBook.
  Best supplier scenario for EV portfolio = 0% migration (flat-rate cross-subsidy
  never recovered under ToU). 16 new tests (4,990 total).

Phase U (2026-06-29): EV Cross-Subsidy Register
  company/pricing/ev_cross_subsidy.py: CrossSubsidyRecord/CrossSubsidyRegister.
  16 new tests (4,974 total).

Phase T (2026-06-29): ToU Tariff Profitability Assessor
  company/pricing/tou_tariff_assessor.py: ToUTariffAssessorBook.
  EV at 3,000 kWh earns supplier GBP 746 flat vs GBP 189 ToU.
  16 new tests (4,958 total).

Latest simulation results (2016-2025):
  Net margin: £1,243,172 | Gross: £6,462,858
  Enterprise value: £6,142,209

Five hollow gaps: all closed.
  1. Customer events: DEEPENED (life events + household model, Phases A/B)
  2. Ledger: CLOSED (Phase 7a/7b)
  3. SIM/company barrier: CLOSED (epistemic verifier passes)
  4. HH data path: CLOSED (Phase 6a)
  5. Reporting: CLOSED (Phase 5a/5b)

Next: Phase X -- ToU Product Launch Decision Engine
  Company decides whether to launch ToU given EV penetration, cross-subsidy exposure,
  and migration risk. Completes T-V analytics to decision loop.

5,003 tests passing.

Report: https://21bcarlisle-arch.github.io/synthetic-enterprise/reports/ANNUAL_REPORT.md
Status: https://raw.githubusercontent.com/21bcarlisle-arch/synthetic-enterprise/main/docs/status/LATEST.md
