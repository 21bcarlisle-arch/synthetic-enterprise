# LATEST -- Synthetic Enterprise Simulation
Last updated: 2026-07-02T01:57:56Z

## Current Status
**Phase ND complete** -- 14,620 tests

## Last Run
See docs/reports/run_output_latest.json.
Net position: £1,274,350 (git a304c3da, 2026-07-02)

## Test Suite
- **14,620 tests passing** (fast suite ~10s)
- Epistemic verifier: PASS

## Recent Phases
- **CLIV** (2026-07-01): Coverage Depth Sprint -- bsc_performance_assurance, dso_flexibility_tender, gas_safety_incident (14,460 tests)
- **CLIII** (2026-07-01): Coverage Depth Sprint -- green_gas_levy, annual_compliance_attestation, liquidity_stress_test (14,310 tests)
- **CLII** (2026-07-01): Coverage Depth Sprint -- theft_risk_scoring, dno_network_charge_dispute, grid_connection_queue (14,280 tests)
- **CLI** (2026-07-01): Coverage Depth Sprint -- account_adjustment, transfer_objection, map_contract (14,250 tests)
- **CL** (2026-07-01): Coverage Depth Sprint -- agreed_capacity, fair_value_assessment, ncc_forecast (14,220 tests)
- **CXLIX** (2026-07-01): Coverage Depth Sprint -- breathing_space, ppm_emergency_credit, uig_allocation (14,190 tests)
- **CXLVIII** (2026-07-01): Coverage Depth Sprint -- query_interface, year_filter_tabs (14,160 tests)
- **CXLVII** (2026-07-01): Coverage Depth Sprint -- 9 files: sim_runner, portal_dd, portal_css, portfolio_pnl, run_phase4c, run_scenario, scenario_comparison, billing_filter, generate_sim (14,154 tests)
- **CXLVI** (2026-07-01): Coverage Depth Sprint -- phase_h eac_multiplier, phase_o solar_dynamic, phase_p ev_overnight (13,063 tests)
- **CXLV** (2026-07-01): Coverage Depth Sprint -- phase40c deemed_rate, phase41a flex, phase61 flex_passthrough, phase62 standing_charges, phase_g ashp_settlement (13,048 tests)
- **ND** (2026-07-02): Gap 4 SIM-side -- bill_shock_tracker wired into run_phase2b.py enriched_churn_estimate; Gap 4 full chain closed (14,620 tests)
- **NC** (2026-07-02): Enriched Company Churn Estimate -- enriched_churn_estimate = max(rate_model, payment_model); sim_interface.get_churn_estimate extended with behaviour+satisfaction signals (14,604 tests)
- **NB** (2026-07-02): Satisfaction Score -> Combined Churn Model -- three-signal churn probability; bill_shock+BehaviourScore+satisfaction; backward-compatible (14,588 tests)
- **NA** (2026-07-02): Dim 4 Emotional -- CustomerSatisfactionAccumulator; bill_shock/css/complaint signals, mean-reversion decay (14,572 tests)
- **MZ** (2026-07-02): Dim 3 Behavioural -- SIM switching propensity; vulnerability trap HIGH stress 35% less likely to switch (14,552 tests)
- **MY** (2026-07-02): Payment Behaviour Score -> Company Churn Model -- combined_churn_probability, CHURN_UPLIFT_BY_SCORE (14,531 tests)
- **MX** (2026-07-02): Company Payment Behaviour Analytics -- PaymentBehaviourAnalytics, BehaviourScore enum, score_payment_history (14,511 tests)
- **MW** (2026-07-02): Income Stress -> Observed Payment Behaviour -- payment_timing.py, bad debt multiplier wired to income_stress (14,485 tests)
- **MV** (2026-07-01): Economic Life Events -- IncomeStress enum, job_loss/income_recovery/new_baby/retirement life events (13,949 tests)
- **MU** (2026-07-01): Coverage Depth Sprint CXIX -- sim/hedging_strategy, sim/risk_engine, sim/weather_price_sensitivity (13,033 tests)
- **MT** (2026-07-01): I&C Triad Demand Curtailment -- build_triad_alert_set/make_triad_aware_shape_fn/get_active_alerts (13,003 tests)

**Latest simulation results (2016–2025)** — auto-processed (438s / 7 min):
- Net margin: £1,274,350.48 | Gross: £6,462,540.99 | Capital: £238,039
- Treasury: £2,466,636 → £3,740,987 | 38 committee interventions | 1443 bills issued
- Enterprise value: £5,637,813.51 | Net after CTS: £6,359,137
- Retention: 18 offers, 17/18 retained | 5 no-offer churns | 6 total churned accounts