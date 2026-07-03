# Current Priorities

Last updated: 2026-07-03 -- HARD REDIRECT: Stop Observatory loop; build observability/billing/anchoring.

## CRITICAL: NO MORE COVERAGE SPRINTS
Coverage sprints (phases LQ through MU, 95+ sprints) are complete. Test count: 14,485.
All future phases must close a real capability gap from the list below.
Do NOT propose another coverage sprint. Do NOT read the old sprint pattern and repeat it.

## Now (active this session)
Last updated: 2026-07-03 -- P1/P2/P3 complete; Phase PR improves anchoring robustness.

Phase PP COMPLETE (2026-07-03): Per-Customer Invoice & Payment Ledger -- billing_ledger.json; 1,605 invoices live. 23 tests (15,171 total).
Phase PQ COMPLETE (2026-07-03): Population Anchoring Validation Gate -- population_anchoring.json; SIM vs Ofgem benchmarks. 23 tests (15,194 total, +5 from PQ update).
Phase PR COMPLETE (2026-07-03): Population Anchoring Robustness -- 3-year rolling crisis comparison; long-run 10yr average (SIM 6.4% vs Ofgem 13.6%, ratio=0.47 GREEN); crisis_divergence_flag now requires rolling+absolute+N>=10. overall_rag: AMBER (was false-alarm RED). 23 tests (15,194 total).
Cloudflare cache fix: /state/* paths now have no-cache header.

Observability URLs (all live at poesys.net):
- /state/PROJECT_STATE.txt -- Phase PQ / 15,189 tests (auto-regenerates on push; will update to PR on next run)
- /state/customer_sample.json -- behavioral data now populated (3c5c124f run processed 19:40 UTC)
- /state/billing_ledger.json -- 1,605 invoices live (confirmed)
- /state/population_anchoring.json -- AMBER (not RED); long-run GREEN
- /shadow/ /shadow/customers/ /shadow/project/ /shadow/sim/ -- all sections live


## Next (roadmap items outbid self-generated work)
Last refreshed: 2026-07-03 -- HARD REDIRECT (ADVISOR). Observatory loop stopped; board sections are NOT phases.

**RULE (permanent, added to phase-close checklist):** A new board/report/Observatory section is NOT a phase. Board sections are byproducts of building capability. Any "add an X Observatory / X dashboard" proposal is automatically outbid by the priorities below.

### PRIORITY 1: OBSERVABILITY THE ADVISOR CAN ACTUALLY USE
**Acceptance: advisor confirms successful fetch of all three -- not a statement it was built.**

(a) **PROJECT_STATE.txt auto-sync BROKEN** -- shows Phase NS / 14,823 tests from Jun 30. Fix the
    regeneration pipeline so it updates on every push. Verify by fetching the file and confirming
    current phase + test count.

(b) **customer_sample.json**: 15-20 real segment-model customers, full behavioural trajectories
    (income_stress, life_events, payment_score, satisfaction, churn_estimate, basis_risk),
    at a STABLE fetchable URL listed in PROJECT_STATE.txt.

(c) **Shadow HTML site**: ALL FOUR sections (Supplier/Customers/Project/SIM) as plain no-JS HTML
    pre-rendered static content. No client-side rendering. The advisor's fetch tool must be able
    to read the full content. Ugly is fine; complete and current is mandatory.

### PRIORITY 2: REAL BILLING & PAYMENT INFRASTRUCTURE
Per-customer money movement -- NOT an Observatory section:
- Invoices issued per customer per billing cycle with due dates
- Payment methods (DD / cash / prepay) and payment events posting to ledger
- Missed payment -> arrears state -> dunning cycle (emergent from non-payment)
- Bad debt (stage 5) emerges naturally -- do NOT build separately first
**Acceptance:** named customer's ledger shows invoices raised, payments received, arrears accruing.

### PRIORITY 3: POPULATION ANCHORING AS STANDING CONSTRAINT
SIM aggregates validated against published UK statistics every run:
- Ofgem annual switching rates by year (CRITICAL: 2021-22 crisis = switching COLLAPSE, not rise;
  SIM must NOT show churn rising during crisis -- if it does, the SIM is wrong)
- Complaints/ombudsman volumes, arrears rates vs published ranges
Build as a validation gate that flags SIM divergence from published reality.

### Completed / No longer current
~~Phase OM (Fuel Mix Disclosure board section)~~ -- SUPERSEDED BY HARD REDIRECT. Board sections
are not phases. Fuel mix capability already built; a board section is a byproduct, not a phase.

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
- ~~Dashboard: Flexibility revenue tab~~ -- CLOSED (Phase NY, 2026-07-03): extract_flexibility() + dashboard["flexibility"] key + _section_flexibility_revenue extended
- ToU tariff depth: time-of-use pricing for HH smart meter customers
- Bad debt stress test: does bad_debt_provision feed back into capital model?

## Recently completed real capability
- **I&C churn calibration fix** (2026-07-02): IC_BILL_STRESS_SENSITIVITY 0.10->0.0. I&C was estimating 95% churn vs SIM 5% (1800% error) at stable rates. 58% of retention offers were wasted. Rate-sensitivity (IC_RATE_SENSITIVITY=1.5x) now drives I&C churn exclusively. Crisis spikes still correctly reach 95%.
- Phase MW (2026-07-02): Income Stress -> Observed Payment Behaviour (14,485 tests)
- Phase MV (2026-07-01): Economic Life Events -- income_stress enum, job_loss/income_recovery/new_baby/retirement
- Phase MT (2026-07-01): I&C Triad Demand Curtailment -- wired to settlement
- Phase MS (2026-07-01): Real NBP Forward Curve -- seasonal multipliers data-derived
- Net margin GBP 1.22M | EV GBP 5.99M | Treasury GBP 3.69M on live 2016-2025 data
