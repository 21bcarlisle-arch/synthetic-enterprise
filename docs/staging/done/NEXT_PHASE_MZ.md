# Proposed Phase MZ -- Dim 3 Behavioural: Income Stress -> SIM Switching Propensity

Drafted: 2026-07-02T01:50:00Z
Depends on: Phase MY complete
Closes: Gap 3 Dim 3 (behavioural -- SIM-side only)

Summary

Add SIM-side income_stress -> actual switching propensity to the simulation.
HIGH stress customers are LESS likely to switch (vulnerability trap -- real UK evidence).
LOW stress customers are SLIGHTLY more likely to shop around when unhappy.
Company churn prediction is unchanged (already uses observables MX+MY).
Gap closes at the SIM level: actual customer behaviour becomes more realistic.

Why

Currently the SIM churn probability is derived purely from bill shocks (base 5% + 3%/shock).
Real UK energy suppliers observe that:
- Financially stressed customers tend NOT to switch even when unhappy (friction costs, deposit 
  requirements, fear of new DD, mental load)
- Financially comfortable customers are more likely to shop around, use PCWs, respond to 
  competitive offers

Files to create

simulation/switching_propensity.py:
  STRESS_SWITCHING_MULTIPLIER: dict[IncomeStress, float]
    LOW=1.10 (more likely to shop), MODERATE=0.85, HIGH=0.65 (vulnerability trap)
  stress_switching_multiplier(income_stress: IncomeStress) -> float
  adjust_churn_probability(base_prob: float, income_stress: IncomeStress) -> float
    returns min(base_prob * stress_switching_multiplier(income_stress), 0.95)

Files to modify

simulation/customer_events.py:
  roll_lifecycle_event -- add income_stress: IncomeStress | None = None parameter
  apply stress_switching_multiplier to p_churn_base before rolling

simulation/run_phase2b.py:
  look up income_stress_at_date for billing_account at term_start
  pass it to roll_lifecycle_event

Tests to create

tests/simulation/test_phase_mz_switching_propensity.py -- 20 tests:
  high_stress_multiplier_is_below_one
  low_stress_multiplier_is_above_one
  moderate_stress_multiplier_between_high_low
  adjust_churn_lowers_for_high_stress
  adjust_churn_raises_for_low_stress
  adjust_churn_no_change_for_moderate (well, 0.85x, so slightly lower)
  adjust_churn_capped_at_095
  adjust_churn_never_below_zero
  none_income_stress_uses_low_as_default
  multiplier_values_complete_for_all_enum
  high_multiplier_lt_moderate_lt_low
  adjust_zero_base_stays_zero
  adjust_exact_boundary_high_stress
  roll_lifecycle_event_accepts_income_stress_param
  roll_lifecycle_event_no_income_stress_backward_compat
  high_stress_lower_probability_than_none
  low_stress_higher_probability_than_none
  adjust_churn_at_base_rate_high_stress
  stress_factor_compounds_with_bill_shocks
  integration_high_stress_lower_sim_churn_probability

Target: 20 tests, total ~14,551.

Fidelity delta

The simulation now models a key real-world asymmetry: financially stressed customers are
NOT the ones who switch. They accumulate. The company's churn blind miss rate (Gap 4) is
partly explained by HIGH stress customers who SHOULD switch (unhappy + high bill) but DON'T
(can't bear the friction). This makes the simulation more realistic and harder for the company
to predict -- a more truthful model of UK energy supply.
