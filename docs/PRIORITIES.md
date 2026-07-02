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
Phase NB COMPLETE (2026-07-02): satisfaction_score wired into combined_churn_probability as third signal (14,588 tests).
Phase NC COMPLETE (2026-07-02): enriched_churn_estimate = max(rate_model, payment_model); sim_interface.get_churn_estimate extended (14,604 tests).
Phase ND COMPLETE (2026-07-02): Gap 4 SIM-side wiring -- bill_shock_tracker -> enriched_churn_estimate in run_phase2b. Gap 4 CLOSED (14,620 tests).
Phase NE COMPLETE (2026-07-02): Gas pass-through capital correction; Gap 5 CLOSED (14,636 tests).
Phase NF COMPLETE (2026-07-02): Gap 3 Dim 4 SIM-side satisfaction wiring; Gap 3 CLOSED (14,652 tests).
Next: All gaps closed -- consider simulation validation run or new gap identification.

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
Dim 4 (emotional/satisfaction): CLOSED -- company side: satisfaction_accumulator.py (NA/NB/NC). SIM side:
  sim_satisfaction.py + satisfaction_churn.py + roll_lifecycle_event (NF). Full four-dimension model complete.

### Gap 4 -- Churn Blind Miss Rate [OPEN -- in progress]
Board risk shows 4/6 departures (67%) not forecast. Company churn model (saas/churn_model.py)
uses only bill shocks. Phase MX gives company payment behaviour scores (proxy signal).
Phase MY wired BehaviourScore (payment_churn_model.py). Phase NB added satisfaction_score.
Phase NC enriched_churn_estimate = max(rate, payment) wired into sim_interface.get_churn_estimate.
CLOSED. run_phase2b uses enriched_churn_estimate with bill_shock_count from all_records (Phase ND).

### Gap 5 -- Gas Segment ROC [CLOSED -- Phase NE]
Root cause was a bug: assess_term_risk called with naked_kwh=aq_kwh for pass_through gas
(hf=0 forced), generating spurious full-VaR capital on a zero-risk position. C_IC3g bills at
spot+service_fee; company holds no commodity price risk. Fix: naked_kwh=0.0 for pass_through
in run_phase2b.py. C_IC3g: net -GBP 134k -> +GBP 95k (service_fee x volume over 9.5 years).

## Backlog (lower priority)
- Dashboard: Flexibility revenue tab -- Phase AG built the data, needs wiring to site/
- ToU tariff depth: time-of-use pricing for HH smart meter customers
- Bad debt stress test: does bad_debt_provision feed back into capital model?

## Recently completed real capability
- **I&C churn calibration fix** (2026-07-02): IC_BILL_STRESS_SENSITIVITY 0.10->0.0. I&C was estimating 95% churn vs SIM 5% (1800% error) at stable rates. 58% of retention offers were wasted. Rate-sensitivity (IC_RATE_SENSITIVITY=1.5x) now drives I&C churn exclusively. Crisis spikes still correctly reach 95%.
- Phase MW (2026-07-02): Income Stress -> Observed Payment Behaviour (14,485 tests)
- Phase MV (2026-07-01): Economic Life Events -- income_stress enum, job_loss/income_recovery/new_baby/retirement
- Phase MT (2026-07-01): I&C Triad Demand Curtailment -- wired to settlement
- Phase MS (2026-07-01): Real NBP Forward Curve -- seasonal multipliers data-derived
- Net margin GBP 1.22M | EV GBP 5.99M | Treasury GBP 3.69M on live 2016-2025 data
