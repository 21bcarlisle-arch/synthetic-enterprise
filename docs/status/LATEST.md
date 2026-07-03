# LATEST -- Synthetic Enterprise Simulation
Last updated: 2026-07-03T11:42:04Z

## Current Status
Phase NR COMPLETE (2026-07-03) -- Bad Debt -> Capital Stress Feedback: company/risk/credit_risk_stress.py (CreditRiskStress dataclass, 2.5x Ofgem crisis multiplier); capital_adequacy.py stress_test_passes = equity > (price_VaR + credit_stress); _section_credit_risk_capital board section. 19 tests, 14,805 total. Capital model now reflects full Ofgem FRA requirement.

Phase NQ COMPLETE (2026-07-03) -- Churn Model Recalibration: INDUSTRY_BASE_CHURN_RATE=0.05 floor on enriched_churn_estimate + passive model; yoy_extended 24-month reference window. 14 tests, 14,786 total.

## Last Run
See docs/reports/run_output_latest.json.
Net position: £1,436,949 (git 15ec4fb5, 2026-07-03)

## Test Suite
- **14,805 tests passing** (fast suite ~10s)
- Epistemic verifier: PASS

## Recent Phases
- **Phase NR** (2026-07-03): credit_risk_stress.py; capital_adequacy stress_test_passes = equity > (VaR + credit); _section_credit_risk_capital board section. 19 tests, 14,805 total.
- **Phase NQ** (2026-07-03): INDUSTRY_BASE_CHURN_RATE=0.05 floor; yoy_extended 24-month reference window; Phase NP pay_metrics bug fixed. 14 tests, 14,786 total.
- **Phase NO** (2026-07-03): counterfactual_retention.py + threshold_sensitivity.py; _section_threshold_optimisation in annual report; optimal F1 threshold=0% reveals model underestimation. 15 tests, 14,772 total.
- **Phase NP** (2026-07-03): simulation/household_demand.py income_stress_trajectory + life_event_history; run_phase2b emits per_customer_behavioral; customer_sample.json wired. 13 tests, 14,757 total.
- **Remote Staging Bridge + Harness Hardening** (2026-07-03): Sim boundary audit (3 violations); observability tools; epistemic verifier extended to saas/; plausibility vs industry section. 15 tests.
- **Phase NL** (2026-07-02): saas/customer_reaction.py YoY comparison; saas/churn_model.py comparison_mode=yoy. 13 tests, 14,744 total.
- **Phase NK** (2026-07-02): churn_model_performance section in annual report. 14 tests, 14,731 total.

**Latest simulation results (2016–2025)** — auto-processed (508s / 8 min):
- Net margin: £1,436,949.07 | Gross: £6,453,707.51 | Capital: £51,306
- Treasury: £2,466,636 → £3,903,585 | 38 committee interventions | 1574 bills issued
- Enterprise value: £8,087,302.19 | Net after CTS: £6,347,906
- Retention: 12 offers, 12/12 retained | 6 no-offer churns | 6 total churned accounts
