# CLAUDE.md — Synthetic Enterprise

## What this project is

A high-fidelity simulation of a fully autonomous UK energy supply business, operating against
real Elexon/NESO half-hourly settlement data. The business layer cannot see future data
(Point-in-Time Blindfold, strictly enforced). Goal: detailed enough to say "that is how a
real UK energy supplier works."

→ Architecture, module inventory, build history: `docs/PROJECT_OVERVIEW.md`

---

## Who does what

- **Rich** — MD/board. Stages instructions in `docs/staging/`. Staging = approval. Does not write code.
- **Claude Code** — lead orchestrator. Designs, delegates, reviews, manages build.
- **qwen3:14b (Ollama)** — all code generation and mechanical execution. Frontier tokens for reasoning only.
- **Risk committee** — local Ollama only. No frontier API spend in simulation runs.

---

## How to operate autonomously

**NTFY is the primary communication channel.** Rich uses it for steering and quick direction changes.
- `background/ntfy_responder.py` writes inbound messages (>25 chars) to `docs/staging/from_rich_TIMESTAMP.md`
- After acting on a `from_rich_*.md` message, reply via `background.ntfy_utils.send_ntfy`.
- Move actioned files to `docs/staging/done/` after processing.

**At startup and after every completed task:** poll `docs/staging/` and action unread files immediately.
- `run_complete_*.md` — publish results (regenerate report, LATEST.md, dashboard.json), commit, push,
  archive. **Do NOT send NTFY for routine sim run completions.** Only NTFY for notable exceptions
  (admin event, all-time high/low margin). Batch silently if multiple queued.
- `run_pending_*.md` — check if finished and act accordingly.
- `from_rich_*.md` — action it, reply via NTFY, archive.

**At every REVIEW_GATE:**
1. Complete phase and commit all outputs.
2. NTFY Rich with what was done and what's next.
3. Proceed immediately to the next phase — do not hold for confirmation.
4. Rich redirects via NTFY if he wants a different direction.

**Always update and commit LATEST.md before sending NTFY.** If stale, fix the root cause.

**When budget is available between tasks:** check backlog, fix known issues, improve coverage. Don't sit idle.

---

## Phase-close checklist (in order)

1. Update test count + latest run figures in PROJECT_OVERVIEW.md Section 10.
2. Add build history entry in PROJECT_OVERVIEW.md Section 4.
3. **Run epistemic verifier:** `python3 -m tools.epistemic_verifier` — must PASS before committing.
   If FAIL: fix violations before committing any phase-close output.
4. **`wc -c CLAUDE.md` — hard limit 35,000 chars / 200 lines.** If over: move phase details to
   `docs/claude/phase-history.md`. Never accumulate phase details in CLAUDE.md.
5. Add one-line phase completion entry to CLAUDE.md "Current state".
6. Commit and push.

PROJECT_OVERVIEW.md is updated at phase close. Run-complete pipeline does NOT update it.

---

## Current state

**Phase 304 COMPLETE (2026-06-27):** Climate Change Levy (CCL) Ledger -- 16 new tests (3,886 passing). company/regulatory/ccl_ledger.py: CCLFuel (ELECTRICITY/GAS), CCLExemptReason (RESIDENTIAL/LEC_COVERED), CCLCharge (frozen; is_exempt/charge_gbp=0 if exempt), CCLQuarterlyReturn (frozen; total_due_gbp/is_nil_return), CCLLedger (rate_for_year/record_charge/charges_for_account/charges_for_year/total_due_gbp/quarterly_return/ccl_summary). Real HMRC rates 2016-2025: elec 0.554->0.775 p/kWh; gas 0.195->0.465 p/kWh. 2019 Budget 2018 spike: elec +45% (0.583->0.847), gas +67% (0.203->0.339) -- NIC->CCL policy shift. Residential fully exempt; LEC holders (renewable electricity) exempt. Connects to cost_to_serve (Ph294), desnz_returns, invoice (billing).
**Phase 303 COMPLETE (2026-06-27):** Stress Test Framework -- 20 new tests (3,870 passing). company/risk/stress_test.py: StressScenario (5: MARKET_SPIKE/CREDIT_DEFAULT/DEMAND_SHOCK/LIQUIDITY_CRISIS/COMBINED_CRISIS), StressAssumption (frozen; default_for() calibrated to 2022 crisis: elec 5x/gas 4x/margin_calls GBP500k/counterparty_default GBP1M), StressResult (frozen; drawdown_pct/is_severe <GBP250k/severity_rag GREEN<10pct/AMBER 10-40pct/RED), StressTestBook (run_stress/results_for_scenario/worst_case/probability_weighted_loss_gbp/scenarios_survived/scenarios_failed/all_red/stress_summary). Ofgem Financial Resilience Assessment Framework (introduced post-2022): quarterly stress tests mandatory; 28 supplier failures 2021-22 partly from failing to stress-test credit facility adequacy. Connects to var_monitor (Ph282), margin_call_book (Ph289), credit_limit_book (Ph290), bsuos_ledger (Ph293), imbalance_ledger (Ph297).
**Phase 302 COMPLETE (2026-06-27):** GSoP Payments Tracker -- 16 new tests (3,887 passing). company/regulatory/gsop_tracker.py: GSoPStandard (10 breach types), GSoPBreachStatus (OPEN/COMPENSATED/WAIVED/DISPUTED), frozen GSoPBreach (compensation_gbp=GBP30 statutory/working_days_open Mon-Fri/is_open/is_compensated), GSoPTracker (record_breach/compensate_breach/waive_breach/open_breaches/total_compensation_paid_gbp/total_compensation_outstanding_gbp/breach_rate_per_100_customers/is_systemic >5 breaches/gsop_summary). Electricity/Gas Standards of Performance Regulations 2015: GBP30 auto-comp; >3/100 customers triggers Ofgem action; GBP21.3M paid sector-wide 2022-23. Connects to ET register (Ph301), consumer_duty (Ph283), regulatory_dashboard (Ph300).
**Phase 301 COMPLETE (2026-06-26):** Erroneous Transfer Register -- 19 new tests (3,871 passing). company/market/erroneous_transfer.py: ETStatus (OPEN/INVESTIGATING/RESOLVED_CORRECTED/RESOLVED_ACCEPTED/COMPENSATION_DUE/CLOSED), ETResolutionType (3: RETURNED_TO_ORIGINAL/CUSTOMER_ACCEPTED_GAIN/WITHDRAWN), frozen ETClaim (working_days_open Mon-Fri count/is_overdue >20 days/compensation_gbp GBP30 if overdue+unresolved), ErroneousTransferRegister (raise_claim/update_status/resolve_claim/open_claims/overdue_claims/et_rate_pct/compensation_outstanding_gbp/claims_by_status/et_summary/above_threshold). Ofgem SLC P14 / REC Schedule 19: 20-working-day resolution deadline; GBP30 auto-comp if overdue; ET rate >0.1% triggers compliance review. Connects to cos_process (Ph298), supply_point_register (Ph299).
**Phase 300 COMPLETE (2026-06-26):** Regulatory Compliance Dashboard -- 12 new tests (3,852 passing). company/regulatory/regulatory_dashboard.py: MILESTONE - Phase 300. FilingStatus (FILED/DUE/OVERDUE/NOT_APPLICABLE), ComplianceArea (8: SFR/REMIT/PRICE_CAP/ENVIRONMENTAL/SOCIAL/CONSUMER_DUTY/TRADE_REPORTING/FUEL_MIX), frozen ComplianceObligation (is_breach/needs_attention), RegulatoryDashboard (add_obligation/obligations_by_area/breaches/attention_items/overall_rag/filed_on_time_rate/area_rag/dashboard_summary). Aggregates all regulatory modules into single board-level compliance view.
**Phase 299 COMPLETE (2026-06-26):** Supply Point Register -- 11 new tests (3,840 passing). company/crm/supply_point_register.py: ProfileClass (PC1-PC8; UK settlement profile classes), FuelType (ELECTRICITY/GAS), frozen SupplyPointRecord (identifier/account_id/fuel/profile_class/supplier_start/end; is_active/is_hh PC5-8/is_domestic PC1-2), SupplyPointRegister (register/deregister via dataclasses.replace/get/active_points by fuel/hh_points/profile_class_breakdown/total_aq_kwh/register_summary). MPAN/MPRN central point-of-supply database — foundation of supplier registration obligations.
**Phase 298 COMPLETE (2026-06-26):** Change of Supplier Process -- 9 new tests (3,829 passing). company/crm/cos_process.py: CoSStage (7: REQUESTED/OBJECTION_WINDOW/CLEARED/FINAL_READ_REQUESTED/RECEIVED/COMPLETE/OBJECTED/CANCELLED), ObjectionReason (DEBT/CONTRACT/COOLING_OFF/CUSTOMER_CANCELLED), frozen CoSEvent (with final_read_kwh/objection_reason), CoSProcess (stateful 5-working-day timeline; clear_objection_window/object_to_switch/request_final_read/receive_final_read/complete/cancel), CoSRegister (open_switch/active_for_account/completed/objected/cos_summary). Closes customer churn loop from retention through to supply transfer.
**Phase 297 COMPLETE (2026-06-26):** Imbalance Charge Ledger -- 12 new tests (3,820 passing). company/market/imbalance_ledger.py: ImbalanceDirection (LONG/SHORT/FLAT), frozen ImbalanceRecord (metered vs contracted; imbalance_mwh/direction/imbalance_charge_gbp: long=sold at SSP positive, short=bought at SBP negative; is_crisis_price >500/MWh; cashout_spread), ImbalanceLedger (records_for_date/net_imbalance_cost/crisis_periods/short_periods/mean_cashout_spread/summary). 2022: SSP/SBP spread widened dramatically as balancing costs trebled.
**Phase 296 COMPLETE (2026-06-26):** REMIT Reporting Book -- 10 new tests (3,808 passing). company/regulatory/remit_book.py: REMITProductType (6: ELEC/GAS forwards/DA/intraday/CM), REMITStatus (PENDING/SUBMITTED/ACKNOWLEDGED/REJECTED), frozen REMITReport (notional_value_gbp/is_large_trade >=100MWh/is_submitted), REMITReportingBook (submit_report/acknowledge_report/pending_reports/compliance_rate/reports_for_product/large_trades/remit_summary). Connects to DayAheadBook (Ph256), IntradayBook (Ph249), GasOTCBook (Ph253). REMIT requires T+1 reporting.
**Phase 295 COMPLETE (2026-06-26):** Ofgem Price Cap Book -- 10 new tests (3,798 passing). company/regulatory/price_cap.py: 26 quarters of real quarterly cap data (Q1 2019 to Q1 2025); CapStatus (BELOW_CAP/AT_CAP/EXCEEDS_CAP/PRE_CAP), frozen CapComplianceCheck (headroom_p_kwh/status/is_compliant), PriceCapBook (elec_cap_p_kwh/gas_cap_p_kwh/typical_annual_bill; record_check/breach_quarters/cap_summary). Peak: Q3 2022 £3,549 typical bill (£1,137 Q1 2019 baseline = 3.1x). Connects to TariffSmoothingBook (Ph277) and CostToServeCalculator (Ph294).
**Phase 294 COMPLETE (2026-06-26):** Cost-to-Serve Calculator -- 10 new tests (3,788 passing). company/pricing/cost_to_serve.py: CustomerSegment (RESIDENTIAL_CREDIT/PPM/SME/I_AND_C), frozen CostToServeBreakdown (wholesale_cost + 7 levy components + bad_debt/smart_meter; levy_p_per_kwh/total_commodity_and_levy_p_per_kwh/operating_cost_gbp/operating_cost_p_per_kwh/total_cost_p_per_kwh/levy_pct_of_total), CostToServeCalculator (acquisition_cost_gbp static; mean_total_cost/high_cost_accounts/cts_summary). I&C acquisition £1,200 vs residential £60; PPM support £28/yr vs credit £18/yr.
**Phase 293 COMPLETE (2026-06-26):** BSUoS Charge Ledger -- 11 new tests (3,778 passing). company/market/bsuos_ledger.py: frozen BSUoSCharge (consumption_mwh/rate_gbp_per_mwh; charge_gbp/is_crisis_period 2021-2022), BSUoSLedger (rate_for_year 2016-2025; crisis_uplift_multiple/annual_rate_trend/bsuos_summary; peak year 2022 = £6.85/MWh vs £2.10 2016 baseline = 3.26x). 2022 BSUoS crisis: National Grid ESO balancing costs trebled due to price volatility + fossil plant operating out of merit. Completes the 7 major non-commodity cost ledgers (CM/CfD/RO/FIT/DUoS/TNUoS/BSUoS).
**Phase 292 COMPLETE (2026-06-26):** TNUoS Charge Ledger -- 10 new tests (3,767 passing). company/market/tnuos_ledger.py: TriadStatus (TRIAD/NEAR_MISS/NORMAL), frozen TNUoSCharge (residual_charge_gbp/triad_charge_gbp/total_charge_gbp), frozen TriadHalfHour (settlement_period/demand_kw/status), TNUoSLedger (residual_rate_for_year/zone_factor; record_charge/record_triad_hh/confirmed_triads/total_charged_gbp/tnuos_summary). Triad demand (3 peak HH Nov-Feb) drives most of the capacity cost; north zones pay 40% more than south (locational signal). 2016-2025 residual rates: 0.68-1.32 p/kWh.
**Phase 291 COMPLETE (2026-06-26):** DUoS Charge Ledger -- 11 new tests (3,757 passing). company/market/duos_ledger.py: DNOArea (14 UK distribution network areas), VoltageLevel (HV/LV), frozen DUoSCharge (unit_charge_gbp/total_charge_gbp/is_hv), DUoSLedger (unit_rate_for_year static; charges_for_account/total_charged_gbp by year/annual_unit_cost_p_per_kwh/hv_customer_count/duos_summary). HV customers pay 40% less (direct network connection). DUoS 2016-2025: 1.85 to 2.75 p/kWh -- one of the 7 major non-commodity electricity costs.
**Phase 290 COMPLETE (2026-06-26):** Counterparty Credit Limit Book -- 12 new tests (3,746 passing). company/finance/credit_limit_book.py: CounterpartyType (BANK/BROKER/GENERATOR/INTERCONNECTOR/CLEARING_HOUSE), frozen CreditLimit (is_material >=£1M), frozen ExposureRecord (current_mtm_gbp/potential_future_exposure_gbp; total_exposure_gbp/is_stress_exposure when PFE >2x MTM), CreditLimitBook (set_limit/record_exposure/latest_exposure/utilisation_pct/is_breach/breaches/limit_summary). Portfolio utilisation, breach detection. Connects to MarginCallBook (Ph289).
**Phase 289 COMPLETE (2026-06-26):** Margin Call Book -- 11 new tests (3,734 passing). company/finance/margin_call_book.py: MarginCallStatus (RECEIVED/SETTLED/DISPUTED/DEFAULTED), frozen MarginCallEvent (initial_margin_gbp/variation_margin_gbp/settlement_deadline; total_margin_required_gbp/is_settled/is_stress_event >500k), MarginCallBook (credit_facility_gbp; record_call/settle_call/outstanding_calls/total_outstanding/headroom/is_liquidity_stressed/stress_events/summary). 2022 crisis: margin calls wiped out supplier credit facilities causing administration events.
**Phase 288 COMPLETE (2026-06-26):** ECO Obligation Tracker -- 10 new tests (3,723 passing). company/regulatory/eco_obligation.py: ECOPhase (ECO2/ECO3/ECO4), MeasureCategory (INSULATION/HEATING/SMART_CONTROLS/RENEWABLES), frozen ECODelivery (co2_saved_tonnes/cost_gbp/is_fuel_poor; cost_per_tonne_co2), ECOObligationBook (record_delivery/deliveries_for_phase/total_co2/total_cost/estimated_annual_obligation_gbp/fuel_poor_delivery_pct/eco_summary). ECO2 £3.20/MWh, ECO3 £4.50/MWh, ECO4 £6.80/MWh. Connects to PropertyImprovementBook (Ph251). ECO4 ends 2026.
**Phase 287 COMPLETE (2026-06-26):** Fuel Mix Disclosure (FMD) Report -- 12 new tests (3,713 passing). company/regulatory/fuel_mix_disclosure.py: FuelSource enum, frozen FuelMixDisclosure (6 source percentages + rego_covered_mwh/total_retail_mwh; total_pct/rego_coverage_pct/is_100pct_renewable/vs_uk_average()), FuelMixDisclosureBook (file_disclosure/disclosure_for_year/renewable_trend/fmd_summary). Real UK average fuel mix data 2016-2023. Suppliers publishing 100% renewable must have REGO coverage to match.
**Phase 286 COMPLETE (2026-06-26):** Feed-in Tariff (FIT) Book -- 11 new tests (3,701 passing). company/regulatory/fit_book.py: FITTechnology (SOLAR_PV/WIND/MICRO_CHP/HYDRO/ANAEROBIC_DIGESTION), FITInstallation (frozen: is_active property), FITPayment (frozen: generation_payment_gbp/export_payment_gbp/total_payment_gbp), FITBook (register_installation/record_payment/payments_for_installation/total_paid_gbp/levelisation_charge_gbp/fit_summary). Real generation rates 2012-2019; scheme ended 2019-03-31. Levelisation charge (FIT levy) 2016-2019: £8.36-£9.45/MWh.
**Phase 285 COMPLETE (2026-06-26):** Renewable Obligation (RO) Tracker -- 10 new tests (3,690 passing). company/regulatory/renewable_obligation.py: ROSettlementMethod (SURRENDER_ROC/BUYOUT/MIXED), frozen ROAnnualReturn (obligation_year/electricity_supplied_mwh/rocs_surrendered/purchased; obligation_rocs/shortfall_rocs/buyout_cost_gbp/total_ro_cost_gbp/is_compliant), RenewableObligationBook (file_return/return_for_year/compliance_record/non_compliant_years/ro_summary). Real buyout prices 2016-2025 (£44.33 to £59.06). Distinct from REGOs (disclosure) -- RO is the financial supplier obligation to Ofgem.
**Phase 284 COMPLETE (2026-06-26):** Smart Meter Rollout Book -- 12 new tests (3,667 passing). company/market/smart_meter_rollout.py: MeterGeneration (SMETS1/SMETS2/TRADITIONAL), RolloutStatus (ON_TRACK/BEHIND/SIGNIFICANTLY_BEHIND), MeterPortfolioSnapshot (frozen: smart_penetration_pct/remote_reads_pct/annual_manual_read_cost_gbp computed), SmartMeterRolloutBook (record_snapshot/rollout_status/annual_progress/rollout_summary). Ofgem annual targets 2016-2025 (10% to 85%); SMETS1 75% remote read rate; SMETS2 95%; manual reads £15/visit. Connects to metering_contracts (Ph242).
**Phase 283 COMPLETE (2026-06-26):** Consumer Duty Compliance Register -- 12 new tests (3,655 passing). company/compliance/consumer_duty.py: DutyOutcome (PRODUCTS_AND_SERVICES/PRICE_AND_VALUE/CONSUMER_UNDERSTANDING/CONSUMER_SUPPORT), OutcomeRAG (GREEN/AMBER/RED), frozen OutcomeAssessment (outcome/rag/metric_name/metric_value/narrative; is_compliant), ConsumerDutyRegister (record_assessment/assessments_for_outcome/latest_for_outcome/red_outcomes/overall_rag/outcomes_summary). Also: warm_home_discount.py fixed to export whd_summary() and whd_eligible_customers() module-level functions (needed by portal/app.py); fixed 23 collection errors unblocking 226 previously-hidden tests (now 3,619 collected).
**Phase 282 COMPLETE (2026-06-26):** VaR Monitor Book -- 13 new tests (3,630 passing). company/risk/var_monitor.py: VaRBreachLevel (WITHIN_LIMIT/AMBER/RED), frozen VaRObservation (observation_date/current_var_gbp/stressed_var_gbp/treasury_gbp; var_as_pct_treasury/stress_uplift_pct), VaRMonitorBook (amber/red limits; record_observation/breach_level/observations_for_year/breach_count/peak_var/mean_var_gbp/var_trend/var_summary). Reads company VaR observable from risk committee wake-ups. Closes key gap in company/risk/ module (was only 2 test files).
**Phase 281 COMPLETE (2026-06-26):** Warm Home Discount (WHD) Tracker -- 11 new tests (3,617 passing). company/regulatory/warm_home_discount.py: WHDEligibilityBasis (CORE_GROUP/BROADER_GROUP), frozen WHDRecord (scheme_year/eligibility_basis/discount_gbp/applied_month/levy_recovered; is_core_group), WHDBook (record_discount/records_for_year/has_received_whd/total_discounted_gbp/levy_recoverable_gbp/mark_levy_recovered/core_broader_counts/whd_summary). Rates: 2015-2021 = £140, 2022-2024 = £150. Annual obligation; levy cost recovered from Ofgem after payment. Connects to VulnerabilityIndex.
**Phase 280 COMPLETE (2026-06-26):** Energy Bill Support Scheme (EBSS) Tracker -- 11 new tests (3,606 passing). company/regulatory/energy_bill_support.py: EBSSCreditType (STANDARD/ALT_FUEL), frozen EBSSCredit (account_id/credit_month/credit_type/amount_gbp/claimed_from_govt; is_standard), EBSSBook (record_credit/credits_for_account/credits_for_month/total_credited_gbp/govt_receivable_gbp/mark_claimed/is_scheme_month/monthly_summary/ebss_summary). 6 scheme months Oct 2022-Mar 2023; £66.67/month standard (£400 total), £100 alt fuel. mark_claimed() converts outstanding receivable to settled. Real 2022-23 UK government intervention.
**Phase 279 COMPLETE (2026-06-26):** Decarbonisation Score (D-Score) -- 13 new tests (3,595 passing). company/sustainability/decarbonisation_score.py (new module directory): DScoreBand (A/B/C/D), DScoreBreakdown (frozen: rego_coverage_pts + epc_improvement_pts + heat_pump_pts + carbon_reduction_pts; total/band properties), DecarbScorer (score_rego_coverage/epc_improvement/heat_pump_adoption/carbon_reduction; compute()), DScoreBook (record/latest/score_for_year/trend/improving/summary). 20% heat pump adoption = full 25pts; 100% REGO = full 25pts. Band A requires 80+ total.
**Phase 278 COMPLETE (2026-06-26):** Dashboard Monthly Ops tab -- 11 new tests (3,582 passing). tools/generate_dashboard_data.py: extract_monthly_ops() aggregates bill_shock_events/committee_wake_ups/retention_log by calendar month; fields: shock_count/avg_shock_pct/max_shock_pct/committee_interventions/retention_offers/retained/is_crisis. site/index.html: Monthly tab with 4 KPI cards (total shocks/crisis shocks/worst month/committee meetings), Chart.js bar+line chart (shocks in red/blue by crisis, committee as overlay line), full 103-month operational timeline table. dashboard.json: monthly_ops key injected. Closes Dashboard Phase E.

→ Phases 1–277: `docs/claude/phase-history.md` | Earlier: `CLAUDE_HISTORY.md`

---

## Architectural Laws

### Epistemic Honesty — The Company Cannot See Inside the SIM

The company layer operates under the same information constraints as a real energy supplier.
It cannot see simulation internals — churn parameters, forward curve construction, weather
engine outputs, VaR internals. It discovers the world through observable interfaces: market
data feeds, meter reads, customer interactions, its own bills and payments, regulatory
publications.

The company's models are approximations built from observed outcomes — not reads from ground
truth. That imperfection is the point.

**Before writing any company-layer code:** ask "Could a real UK energy supplier know this?"
If the answer requires reading simulation internals, it is a violation.

The SIM/company seam (`company/interfaces/sim_interface.py`) enforces this boundary —
exposes observables and outcomes only, never parameters or internals.

---

## Sequencing principles

**Two-way-door filter:** don't build something that depends on an unresolved upstream question.

**Build efficiency:** tests passing + capabilities added per frontier session (hard metric).
Fidelity delta — one sentence per phase on what the sim can now do (soft metric, Rich assesses).
CLV is not a stable measuring stick — it evolves with business rules.

**Reversibility** governs data architecture and agent governance. Prefer designs that can be unwound.

**Regime-change blindness** is a known failure mode. The sim converged to near-naked hedging during
calm 2016–2020 data, directly before the crisis — mirroring what killed real suppliers. All
hedging/risk models must account for this.

**Activity-based pricing:** flat margin makes some customers net-negative. Any pricing model must
account for cost-to-serve at the customer level.

---

## Key learnings — do not repeat these mistakes

- **Local models confabulate endpoints.** Pre-load ground-truth API context before any local model touches external sources.
- **LATEST.md must be committed before NTFY**, not after. If stale, fix root cause.
- **REVIEW_GATE must only match on actual pane idleness** — not on prose mentioning the string "REVIEW_GATE".
- **Staging-watcher notifies Rich, not the agent.** Poll `docs/staging/` yourself.
- **The simulation is not the company.** Company makes decisions based on what it's allowed to see.
- **Non-blocking concurrency.** If blocked on a long run, move to the next staging item and return.
- **Session usage window is ~5 hours**, not 4. Don't under-estimate available budget.
- **CLAUDE.md hard limit: 35k chars / 200 lines.** Stop and trim before anything else if exceeded.
- **Committee cooldown must be date-based**, not record-count. With 18+ customers, 1440 records ≠ 30 days.
- **sim_runner TimeoutExpired must be caught.** Uncaught exception kills the `while True` loop.

---

## Technical environment

**Hardware (Skynet):** Intel i5-13400F, 32GB DDR4, RTX 3060 12GB VRAM. Windows 11 Pro + WSL2/Ubuntu.
**Networking:** Tailscale WSL2 `100.69.81.59` | File API `https://skynet-1.taila062fa.ts.net:8765`
**AI stack:** Claude Code (orchestrator) → qwen3:14b/Ollama (code gen) → risk committee (local Ollama)
**Key paths:** `docs/staging/` (instructions) | `docs/status/LATEST.md` | `docs/reports/ANNUAL_REPORT.md`
**Data:** Elexon `data.elexon.co.uk` (key-free) | NESO CKAN | Open-Meteo | synthetic forward curves
**Elexon note:** API migrated to Insights Solution. Legacy wrappers partly stale — verify before use.
