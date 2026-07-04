## Phase PZ COMPLETE -- Scenario Stress Testing via Synthetic Market
Last updated: 2026-07-04T08:14:16Z

**Status:** COMPLETE. 15,300 tests (fast suite). Epistemic: PASS.

**Phase PZ -- Scenario Stress Testing via Synthetic Market:**
- tools/run_live_decisions.py: run_scenario_analysis() with 4 persistent scenarios (base/bull/bear/crisis)
- Scenario prices = CorrelatedGeneratorAdapter start prices (sustained levels, not OU projection)
- portfolio_exposure_delta: additional unhedged annual cost vs base scenario
- tools/market_adapters/synthetic_generator.py: gas_start/elec_start params added
- saas/reporting/annual_report.py: _section_scenario_sensitivity board section
- process_run_complete.py: run_scenario_analysis() wired + JSON committed

**KEY FINDINGS:**
- Crisis scenario: elec 217 GBP/MWh, gas 110 GBP/MWh → +£1,562,206 unhedged exposure vs base
- Bull scenario: elec 56 GBP/MWh → -£398,252 (cheap energy, hedge reduces cost)
- All scenarios: INCREASE hedge recommendation (portfolio underpins at 30% avg hedge fraction)
- CLOSES CLAUDE.md known failure: regime-change blindness — board can now ask "what if 2021-22 again?"

**PRIORITIES.md P1 (Correlated Simulation Endgame):** COMPLETE.


**Latest simulation results (2016–2025)** — auto-processed (519s / 9 min):
- Net margin: £1,445,257.67 | Gross: £6,467,308.57 | Capital: £51,433
- Treasury: £2,466,636 → £3,911,894 | 38 committee interventions | 1605 bills issued
- Enterprise value: £8,826,938.57 | Net after CTS: £6,360,822
- Retention: 12 offers, 12/12 retained | 6 no-offer churns | 6 total churned accounts