# LATEST -- Synthetic Enterprise Simulation
Last updated: 2026-07-03T14:20:47Z

## Current Status
Phase NT COMPLETE (2026-07-03) -- Year-on-Year Net Margin Bridge (P1: Observability): saas/reporting/margin_attribution.py (MarginBridge, build_margin_bridge_series, dominant_driver); _section_net_margin_bridge board section (9 transitions 2016-2025, RAG, primary driver, most-damaging/best summary). Key findings: 2019->2020 policy-levy-driven deterioration (-£162k); 2021->2022 crisis windfall despite bad debt surge (+£232k net); 2024->2025 gross collapse (-£732k) offset by policy/network relief (+£510k). 19 tests, 14,843 total. Board can now trace any year's net margin change to its causal drivers.

Phase NS COMPLETE (2026-07-03) -- Price-Elasticity Switching Model: market_switching_propensity.py; savings-elasticity churn multiplier (2022: 0.44x; 2016: 2.17x; 2024: 1.0x baseline). 19 tests, 14,824 total.

Phase NR COMPLETE (2026-07-03) -- Bad Debt -> Capital Stress Feedback: credit_risk_stress.py; capital_adequacy stress_test_passes = equity > (VaR + credit); board section. 19 tests, 14,805 total.

## Last Run
See docs/reports/run_output_latest.json.
Net position: £1,445,258 (git c388671e, 2026-07-03)

## Test Suite
- **14,843 tests passing** (fast suite ~10s)
- Epistemic verifier: PASS

## Recent Phases
- **Phase NT** (2026-07-03): margin_attribution.py; year-on-year net margin bridge; 9 transitions 2016-2025; RAG + primary driver. 19 tests, 14,843 total.
- **Phase NS** (2026-07-03): market_switching_propensity.py; savings-elasticity churn multiplier (2022: 0.44x; 2016: 2.17x; 2024: 1.0x baseline). 19 tests, 14,824 total.
- **Phase NR** (2026-07-03): credit_risk_stress.py; capital_adequacy stress_test_passes = equity > (VaR + credit); _section_credit_risk_capital board section. 19 tests, 14,805 total.
- **Phase NQ** (2026-07-03): INDUSTRY_BASE_CHURN_RATE=0.05 floor; yoy_extended 24-month reference window; Phase NP pay_metrics bug fixed. 14 tests, 14,786 total.
- **Phase NO** (2026-07-03): counterfactual_retention.py + threshold_sensitivity.py; _section_threshold_optimisation in annual report; optimal F1 threshold=0% reveals model underestimation. 15 tests, 14,772 total.
