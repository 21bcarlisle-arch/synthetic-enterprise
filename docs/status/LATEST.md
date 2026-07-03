# LATEST -- Synthetic Enterprise Simulation
Last updated: 2026-07-03T09:37:23Z

## Current Status
Remote Staging Bridge + Harness Hardening COMPLETE (2026-07-03) -- staging_watcher git fetch every 3min, [ADVISOR-STAGED] commits surface to local staging; sim boundary audit closed (3 violations); observability live; 14,771 tests

## Last Run
See docs/reports/run_output_latest.json.
Net position: £1,436,949 (git 8f6bbcf7, 2026-07-03)

## Test Suite
- **14,771 tests passing** (fast suite ~10s)
- Epistemic verifier: PASS

## Recent Phases
- **Harness Hardening** (2026-07-03): Sim boundary audit (3 violations fixed); observability tools (customer_sample.json + shadow HTML); epistemic verifier extended to saas/; plausibility vs industry section in annual report; CLAUDE.md 3 rules encoded. 15 tests, 14,759 total.
- **Phase NL** (2026-07-02): saas/customer_reaction.py comparison_mode=rolling|yoy; YoY compares same calendar month prior year, eliminates seasonal false-positives. saas/churn_model.py build_churn_risk comparison_mode=yoy. 13 tests, 14,744 total.
- **Phase NK** (2026-07-02): saas/reporting/annual_report.py churn_model_performance section; TP/FP/FN/TN/recall/precision/F1/per-year/RAG. 14 tests, 14,731 total.
- **Phase NJ** (2026-07-02): company/analytics/churn_accuracy_report.py -- compute_churn_model_performance computes TP/FP/FN/TN, recall, precision, F1. Board gains churn model calibration KPI. 16 tests, 14,717 total.
- **Phase NH** (2026-07-02): PaymentBehaviourAnalytics wired into run_phase2b.py -- three-signal churn model (bill_shock+behaviour+satisfaction) fully operational. 17 tests, 14,701 total.
- **Fix** (2026-07-02): TOU bill shock counter -- resi HH TOU customers no longer get 500-1500 spurious shocks. 14 tests, 14,684 total.

**Latest simulation results (2016–2025)** — auto-processed (831s / 14 min):
- Net margin: £1,436,949.07 | Gross: £6,453,707.51 | Capital: £51,306
- Treasury: £2,466,636 → £3,903,585 | 38 committee interventions | 1574 bills issued
- Enterprise value: £8,087,302.19 | Net after CTS: £6,347,906
- Retention: 12 offers, 12/12 retained | 6 no-offer churns | 6 total churned accounts