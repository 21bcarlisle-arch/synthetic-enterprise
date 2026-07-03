# LATEST -- Synthetic Enterprise Simulation
Last updated: 2026-07-03T13:11:06Z

## Current Status
NQ Advisor Redirect (2026-07-03) -- enriched_churn_estimate 5% floor DROPPED (uniform shift, no discrimination); PRIORITIES.md refreshed (P1: observability, P2: billing infra, P3: population anchoring, P4: shadow ops); PROJECT_STATE.txt sync fixed (deploy-pages.yml overwrite removed). 14,823 tests total.

Phase NS COMPLETE (2026-07-03) -- Price-Elasticity Switching Model: simulation/market_switching_propensity.py (MARKET_SAVINGS_BY_YEAR; _savings_to_rate piecewise; market_switching_multiplier normalised 2024=1.0); customer_events.py market_year param wired; run_phase2b passes year at each renewal. 19 tests, 14,824 total. KEY: rising prices do NOT drive switching -- savings available is primary driver (2022: bills £3,549 yet switching 3-4%).

Phase NR COMPLETE (2026-07-03) -- Bad Debt -> Capital Stress Feedback: company/risk/credit_risk_stress.py (CreditRiskStress dataclass, 2.5x Ofgem crisis multiplier); capital_adequacy.py stress_test_passes = equity > (price_VaR + credit_stress); _section_credit_risk_capital board section. 19 tests, 14,805 total. Capital model now reflects full Ofgem FRA requirement.

Phase NQ COMPLETE (2026-07-03) -- Churn Model Recalibration: INDUSTRY_BASE_CHURN_RATE=0.05 floor on enriched_churn_estimate + passive model; yoy_extended 24-month reference window. 14 tests, 14,786 total.

## Last Run
See docs/reports/run_output_latest.json.
Net position: £1,445,258 (git 59a77bb1, 2026-07-03)

## Test Suite
- **14,823 tests passing** (fast suite ~10s)
- Epistemic verifier: PASS

## Recent Phases
- **Phase NS** (2026-07-03): market_switching_propensity.py; savings-elasticity churn multiplier (2022: 0.44x; 2016: 2.17x; 2024: 1.0x baseline). 19 tests, 14,824 total.
- **Phase NR** (2026-07-03): credit_risk_stress.py; capital_adequacy stress_test_passes = equity > (VaR + credit); _section_credit_risk_capital board section. 19 tests, 14,805 total.
- **Phase NQ** (2026-07-03): INDUSTRY_BASE_CHURN_RATE=0.05 floor; yoy_extended 24-month reference window; Phase NP pay_metrics bug fixed. 14 tests, 14,786 total.
- **Phase NO** (2026-07-03): counterfactual_retention.py + threshold_sensitivity.py; _section_threshold_optimisation in annual report; optimal F1 threshold=0% reveals model underestimation. 15 tests, 14,772 total.
- **Phase NP** (2026-07-03): simulation/household_demand.py income_stress_trajectory + life_event_history; run_phase2b emits per_customer_behavioral; customer_sample.json wired. 13 tests, 14,757 total.
- **Remote Staging Bridge + Harness Hardening** (2026-07-03): Sim boundary audit (3 violations); observability tools; epistemic verifier extended to saas/; plausibility vs industry section. 15 tests.
- **Phase NL** (2026-07-02): saas/customer_reaction.py YoY comparison; saas/churn_model.py comparison_mode=yoy. 13 tests, 14,744 total.
- **Phase NK** (2026-07-02): churn_model_performance section in annual report. 14 tests, 14,731 total.

**Latest simulation results (2016–2025)** — auto-processed (624s / 10 min):
- Net margin: £1,445,257.67 | Gross: £6,467,308.57 | Capital: £51,433
- Treasury: £2,466,636 → £3,911,894 | 38 committee interventions | 1605 bills issued
- Enterprise value: £8,826,938.57 | Net after CTS: £6,360,822
- Retention: 12 offers, 12/12 retained | 6 no-offer churns | 6 total churned accounts