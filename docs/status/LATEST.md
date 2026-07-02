# LATEST -- Synthetic Enterprise Simulation
Last updated: 2026-07-02T08:50:55Z

## Current Status
Phase NJ: Churn Model Calibration Report live -- board-level recall/precision/F1 for churn model (14,717 tests)

## Last Run
See docs/reports/run_output_latest.json.
Net position: £1,461,253 (git unknown, 2026-07-02)

## Test Suite
- **14,717 tests passing** (fast suite ~10s)
- Epistemic verifier: PASS

## Recent Phases
- **Phase NJ** (2026-07-02): company/analytics/churn_accuracy_report.py wired -- compute_churn_model_performance computes TP/FP/FN/TN, recall, precision, F1 from customer_events vs threshold. Board gains churn model calibration KPI. 16 tests, 14,717 total.
- **Phase NH** (2026-07-02): PaymentBehaviourAnalytics wired into run_phase2b.py -- behaviour_score now populated from monthly payment records; three-signal churn model (bill_shock+behaviour+satisfaction) fully operational. 17 tests, 14,701 total.
- **TOU bill shock counter fix** (2026-07-02): _elec_rate_shock_counts replaces count_rate_shocks; resi HH TOU customers no longer get 500-1500 spurious shocks. 14 tests, 14,684 total.
- **I&C churn calibration fix** (2026-07-02): IC_BILL_STRESS_SENSITIVITY 0.10->0.0; I&C no longer gets 95% churn estimate at stable rates. 14,670 tests.
- **Phase NG** (2026-07-02): CustomerSatisfactionAccumulator wired; satisfaction_score now live in enriched_churn_estimate. 16 tests, 14,668 total.

**Latest simulation results (2016–2025)** — auto-processed (930s / 16 min):
- Net margin: £1,461,253.49 | Gross: £6,462,528.09 | Capital: £51,123
- Treasury: £2,466,636 → £3,927,890 | 38 committee interventions | 1443 bills issued
- Enterprise value: £5,637,800.63 | Net after CTS: £6,359,124
- Retention: 11 offers, 10/11 retained | 5 no-offer churns | 6 total churned accounts