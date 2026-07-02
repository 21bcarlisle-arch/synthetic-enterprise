# Current Priorities

Last updated: 2026-07-02 -- Direction: Human Simulation Layer (Gap 3) + Churn (Gap 4).

## CRITICAL: NO MORE COVERAGE SPRINTS
Coverage sprints (phases LQ through MU, 95+ sprints) are complete. Test count: 14,485.
All future phases must close a real capability gap from the list below.
Do NOT propose another coverage sprint. Do NOT read the old sprint pattern and repeat it.

## Now (active this session)
Phase MW COMPLETE (2026-07-02): income_stress -> observable payment behaviour.
Phase MX COMPLETE (2026-07-02): Company-side PaymentBehaviourAnalytics -- BehaviourScore enum, score_payment_history, PaymentBehaviourAnalytics (14,511 tests).
Phase MY COMPLETE (2026-07-02): BehaviourScore wired into combined_churn_probability via payment_churn_model.py (14,531 tests).
Phase MZ COMPLETE (2026-07-02): Dim 3 behavioural SIM-side -- vulnerability trap wired (14,552 tests).
Phase NA COMPLETE (2026-07-02): Dim 4 emotional company-side -- CustomerSatisfactionAccumulator (14,572 tests).
Next: Gap 5 gas ROC or wire satisfaction score into combined churn model.
After MY: Dim 3 behavioural (income_stress -> SIM-side switching propensity) or Gap 5 gas ROC.

## Real capability gaps

### Gap 1 -- Real Forward Curve [CLOSED -- Phase MS]
NBP/EPEX term structure using real published seasonal forward strips (2016-2025).
seasonal_calibration.json now data-derived from Elexon SSP + TTF proxy. Gas Dec 1.294 (was 1.20).

### Gap 2 -- I&C Triad Demand Curtailment [CLOSED -- Phase MT]
Triad notification book wired to 25% load reduction in settlement for I&C HH customers.
build_triad_alert_set (SSP>80 + Triad season + SP 33-39) + make_triad_aware_shape_fn live.

### Gap 3 -- Human Simulation Layer [OPEN -- LARGE / MULTI-PHASE]
4-dimension customer modelling: physical (property/EPC/appliances), economic (income/credit),
behavioural (payment/switching propensity), emotional (satisfaction/trust).
Dim 1 (physical): CLOSED -- simulation/household.py + household_demand.py fully wired (EPC
  multipliers, seasonal_flatness_factor, life events for solar/EV/boiler/insulation).
Dim 2 (economic): CLOSED SIM-side (MV/MW); company-side closes with Phase MX.
Dim 3 (behavioural): CLOSED -- simulation/switching_propensity.py (Phase MZ) wires income_stress
  into roll_lifecycle_event. HIGH 0.65x / MODERATE 0.85x / LOW 1.10x multiplier on churn probability.
Dim 4 (emotional/satisfaction): PARTIAL -- company/crm/satisfaction_accumulator.py (Phase NA)
  tracks rolling satisfaction from bill_shock/css/complaint observables with mean-reversion.
  SIM-side (satisfaction -> actual churn) still OPEN.

### Gap 4 -- Churn Blind Miss Rate [OPEN -- in progress]
Board risk shows 4/6 departures (67%) not forecast. Company churn model (saas/churn_model.py)
uses only bill shocks. Phase MX gives company payment behaviour scores (proxy signal).
Phase MY will wire BehaviourScore into company/crm/churn_model.py: POOR/CRITICAL scores
add churn uplift, EXCELLENT suppresses it. Gap closes when company predicts >= 60% of churns.

### Gap 5 -- Gas Segment ROC [OPEN]
Gas legs show -0.7x ROC (net GBP -134,790 on GBP 187,116 capital for C_IC3g).
Root cause: gas crisis 2021-2023 drove NBP to GBP 100-300/MWh; large naked gas positions
generated VaR-based capital costs that wiped out gross margin. Correct simulation physics.
Business response options: exit gas (company/finance/gas_exit_decision.py),
gas-specific tariff uplift, or improved gas hedging model. Address after Gap 4 closes.

## Backlog (lower priority)
- Dashboard: Flexibility revenue tab -- Phase AG built the data, needs wiring to site/
- ToU tariff depth: time-of-use pricing for HH smart meter customers
- Bad debt stress test: does bad_debt_provision feed back into capital model?

## Recently completed real capability
- Phase MW (2026-07-02): Income Stress -> Observed Payment Behaviour (14,485 tests)
- Phase MV (2026-07-01): Economic Life Events -- income_stress enum, job_loss/income_recovery/new_baby/retirement
- Phase MT (2026-07-01): I&C Triad Demand Curtailment -- wired to settlement
- Phase MS (2026-07-01): Real NBP Forward Curve -- seasonal multipliers data-derived
- Net margin GBP 1.22M | EV GBP 5.99M | Treasury GBP 3.69M on live 2016-2025 data
