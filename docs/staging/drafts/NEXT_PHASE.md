Phase 303 -- Stress Test Framework

Status: PROPOSED (2026-06-27T00:30Z)
4h opt-out window: expires 2026-06-27T04:30Z

Context:
company/risk/ has only 3 modules (hedge_policy, risk_appetite, var_monitor = 305 lines total).
Ofgem Financial Resilience Assessment Framework (introduced 2022) requires quarterly stress
tests from every licensed supplier. The 28 supplier failures 2021-2022 partly resulted from
failure to stress-test credit facilities against margin call cascades. Closes largest gap in
company/risk/.

Connects to: var_monitor (Ph282), margin_call_book (Ph289), credit_limit_book (Ph290),
bsuos_ledger (Ph293), imbalance_ledger (Ph297).

Design:
- company/risk/stress_test.py (new)
- StressScenario enum (5): MARKET_SPIKE / CREDIT_DEFAULT / DEMAND_SHOCK / LIQUIDITY_CRISIS / COMBINED_CRISIS
- StressAssumption (frozen): scenario / price_multiplier_elec / price_multiplier_gas /
  demand_uplift_pct / margin_call_gbp / counterparty_default_gbp / duration_weeks
- StressResult (frozen): scenario / starting_treasury_gbp / stressed_treasury_gbp /
  treasury_drawdown_gbp / peak_var_gbp / margin_calls_triggered_gbp /
  weeks_to_cash_concern (Optional[int]) / survives / survival_headroom_gbp
  Properties: drawdown_pct / is_severe / severity_rag (GREEN/AMBER/RED)
- StressTestBook: run_stress / results_for_scenario / worst_case / probability_weighted_loss_gbp /
  scenarios_survived / scenarios_failed / all_red / stress_summary

Estimated: ~14 tests, ~160 lines

Fidelity delta: COMBINED_CRISIS calibrated to 2022 (elec 5x, gas 4x, margin calls
500k GBP, counterparty default 1M GBP) -- conditions that caused real UK suppliers to fail.
