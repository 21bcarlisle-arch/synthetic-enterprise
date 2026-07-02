# LATEST -- Synthetic Enterprise Simulation
Last updated: 2026-07-02T04:17:24Z

## Current Status
**Phase NG complete** -- 14,668 tests

## Last Run
See docs/reports/run_output_latest.json.
Net position: £1,443,537 (git bca252a7, 2026-07-02)

## Test Suite
- **14,668 tests passing** (fast suite ~10s)
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
- **NG** (2026-07-02): Company Satisfaction Score -> Renewal Churn Estimate -- CustomerSatisfactionAccumulator wired into run_phase2b.py; enriched_churn_estimate now gets satisfaction_score from observable bill shocks (14,668 tests)
- **NF** (2026-07-02): Gap 3 Dim 4 SIM-side -- sim_satisfaction.py + satisfaction_churn.py wired into roll_lifecycle_event; all 4 dimensions CLOSED (14,652 tests)
- **NE** (2026-07-02): Gap 5 Gas Pass-Through Capital Fix -- naked_kwh=0 for pass_through in assess_term_risk; C_IC3g net -£134k -> +£95k. Gap 5 CLOSED (14,636 tests)
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

**Latest simulation results (2016–2025)** — auto-processed (461s / 8 min):
- Net margin: £1,443,537.32 | Gross: £5,422,401.40 | Capital: £40,289
- Treasury: £2,466,636 → £3,910,174 | 38 committee interventions | 1383 bills issued
- Enterprise value: £5,256,728.12 | Net after CTS: £5,334,425
- Retention: 26 offers, 25/26 retained | 6 no-offer churns | 7 total churned accounts