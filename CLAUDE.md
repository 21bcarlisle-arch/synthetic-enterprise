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
3. **Run epistemic verifier:** `python3 -m tools.epistemic_verifier` — must PASS before committing. If FAIL: fix violations first.
4. **`wc -c CLAUDE.md` — hard limit 35,000 chars / 200 lines.** If over: move to `docs/claude/phase-history.md`. Never accumulate phase details in CLAUDE.md.
5. Add one-line phase completion entry to CLAUDE.md "Current state".
6. Commit and push.
PROJECT_OVERVIEW.md is updated at phase close. Run-complete pipeline does NOT update it.
## Current state
**Phase CY COMPLETE (2026-06-30):** Supplier Fitness Register -- 13 tests (6,116). company/regulatory/supplier_fitness_register.py: FitnessRole (EXECUTIVE_DIRECTOR/NON_EXEC/SENIOR_MANAGER/MAJOR_SHAREHOLDER); FitnessConcernCategory (CRIMINAL_CONVICTION/BANKRUPTCY/PRIOR_SUPPLIER_FAILURE etc.); FitnessAssessment (frozen; review_due_date +365d/is_review_overdue/is_fit); SupplierFitnessRegister (not_fit_persons/overdue_reviews/prior_supplier_failure_risk/all_fit). Ofgem LC 30A (June 2022): fit-and-proper for directors; annual review.
**Phase CX COMPLETE (2026-06-30):** Regulatory Breach Log -- 12 tests (6,103). company/regulatory/regulatory_breach_log.py: BreachSeverity (LOW/MEDIUM/HIGH/CRITICAL); BreachStatus (POTENTIAL→CONFIRMED→REMEDIATED/REPORTED_TO_OFGEM); BreachSource; RegulatoryBreachRecord (frozen; is_open/is_reportable: H/C only); RegulatoryBreachLog (record/confirm/report_to_ofgem/remediate/open_breaches/critical_breaches/reportable_breaches/total_estimated_penalty_gbp/by_slc). Central breach register for SLC violations; Ofgem penalty up to 10% turnover.
**Phase CW COMPLETE (2026-06-30):** Licence Application Register -- 12 tests (6,091). company/regulatory/licence_application_register.py: LicenceType (4 types: elec/gas domestic/non-domestic); LicenceTier (TIER_1 <250k / TIER_2 >=250k); LicenceRecord (frozen; has_special_conditions); LicenceApplication (frozen; is_open/is_approved); LicenceApplicationRegister (submit/decide/active_licences/licences_with_special_conditions/open_applications). Post-2022 Ofgem requires explicit continuation when FRA deteriorates.
**Phase CV COMPLETE (2026-06-30):** DA/DC Contract Register -- 12 tests (6,079). company/market/dadc_contract_register.py: MeteringAgentType (DA/DC/DA_DC/MOA); AgentAppointment (frozen; is_active); DADCContractRegister (appoint/terminate/agent_for_mpan/mpans_without_dc/mpans_without_da/agents_by_name). BSC SVA: DC reads/submits; DA aggregates HH data; DA_DC combined covers NHH; missing appointment = BSC breach.
**Phase CU COMPLETE (2026-06-30):** Interruptible Gas Supply Register -- 13 tests (6,067). company/market/interruptible_supply_register.py: InterruptionReason (COLD_WEATHER/NGT_INSTRUCTION/NETWORK_CONSTRAINT/SUPPLIER_DISCRETION); InterruptibleContract (saving_vs_firm_gbp_pa at 15% INT discount); InterruptibleSupplyRegister (register/record_interruption/notice_violations: <2h/annual_curtailment_days/over_cap_accounts: >30d/total_portfolio_annual_kwh). UNC TPD X3: 2-hour min notice; 30-day cap.
**Phase CT COMPLETE (2026-06-30):** Shipper Code Register -- 13 tests (6,054). company/market/shipper_code_register.py: LDZ enum (13 GB Local Distribution Zones); LDZAuthorisation (frozen); ShipperRecord (ldz_coverage_count/is_national/can_supply_in/add_ldz/revoke_ldz); ShipperCodeRegister (register/suspend/active_shippers/suspended). Xoserve UK Link: shipper code required for gas nomination; 13 LDZs; MPRN registry.
**Phase CS COMPLETE (2026-06-30):** Gas Nomination Register -- 12 tests (6,041). company/market/gas_nomination_register.py: ImbalanceDirection (LONG/SHORT/BALANCED); GasNominationRecord (effective_nominated_kwh/imbalance_kwh/imbalance_pct/direction/is_in_tolerance: ±5%); GasNominationRegister (nominate/revise/settle/out_of_tolerance_days/short_days/long_days/mean_imbalance_pct). UNC: nominate by 08:30; cash-out outside tolerance; gas day 06:00-06:00.
**Phase CR COMPLETE (2026-06-30):** Priority Services Register -- 12 tests (6,029). company/regulatory/priority_services_register.py: PSRCategory (9 eligibility types incl. MEDICAL_EQUIPMENT/PENSIONABLE_AGE); PSRService (6 core services); PSRRecord (needs_priority_reconnection/is_review_overdue/is_compliant); PriorityServicesRegister (active/electricity_dependent/non_compliant/overdue_reviews/network_shared/psr_penetration_pct). SLC 26B: ≥1 service per PSR customer. UK ~9M households / 31% domestic.
**Phase CQ COMPLETE (2026-06-30):** Environmental Impact Register -- 12 tests (6,017). company/sustainability/environmental_impact.py: EmissionScope (SCOPE_1/2_LOCATION/2_MARKET/3_DOWNSTREAM); EmissionRecord (emissions_tco2e/mtco2e); EnvironmentalImpactRegister (record_gas_scope3/record_electricity_scope3: market=REGO×0 + grid×unmatched; total_scope3_tco2e/emissions_by_year/peak_year). DEFRA 2023: gas 0.18253 kgCO₂e/kWh; grid 0.2104; REGO=0. SECR/TCFD compliance.
**Phase CP COMPLETE (2026-06-30):** BSC Settlement Exposure Section -- 12 tests (6,005). annual_report.py: _section_bsc_settlement_exposure(): BSC credit + peak daily per year; <<flag if >0.4% of revenue; peak year identified. 2022=£10,210 credit; 2025=0.51% flagged. Elexon BSC: suppliers must post credit cover for imbalance.
**Phase CO COMPLETE (2026-06-30):** Contract Exposure Register -- 12 tests (5,993). company/crm/contract_exposure_register.py: ContractStatus (FIXED_TERM/SVT/OOC/DEEMED/PENDING_RENEWAL); ContractRecord (is_fixed_term/is_svt/days_remaining/is_in_notice_window/annual_contract_revenue_gbp); ContractExposureRegister (fixed_term/svt_contracts/in_notice_window/notice_not_issued→SLC 22 breach risk/svt_revenue_at_risk_gbp). SVT = at-risk; OOC = supplier may exit.
**Phase CN COMPLETE (2026-06-30):** Unit Economics Annual Report Section -- 12 tests (5,981). annual_report.py: _section_unit_economics(): rev/gross/net per active customer by year; <<flag for net margin <5% (Ofgem FRA); best/worst year per customer. 2021=3.3% flagged; 2024=14.3% clean. Wired before Phase CD section.
**Phase CM COMPLETE (2026-06-30):** Market Share Estimator -- 12 tests (5,969). company/market/market_share_estimator.py: MarketSegment (DOMESTIC/SME/I&C); UK benchmarks (29M domestic/1.7M SME/28k I&C, Ofgem); SegmentShareEstimate (market_share_pct/is_micro_supplier <0.01%/customers_needed_for_1pct); MarketShareSnapshot (blended_share/largest_segment); MarketShareEstimator (record_year/growth_rate_pct/share_trend). Our 4 I&C = 0.014% share; 9 resi = 0.000031% (micro).
**Phase CL COMPLETE (2026-06-30):** Fuel Mix Disclosure Book -- 12 tests (5,957). company/regulatory/fuel_mix_disclosure.py: FuelSource enum (11 sources); _CARBON_INTENSITY / _IS_RENEWABLE lookup tables; FuelMixComponent (weighted_carbon/is_renewable); FuelMixDisclosure (renewable_fraction/carbon_intensity/rego_coverage_fraction/is_fully_rego_matched/unmatched_volume_mwh); FuelMixDisclosureBook (record/carbon_trend/fully_matched_years/fmd_summary). SLC 21C: must disclose fuel mix annually; REGO=1MWh; UK residual 280 gCO₂e/kWh.
**Phase CK COMPLETE (2026-06-30):** Liquidity Stress Test Book -- 12 tests (5,945). company/risk/liquidity_stress_test.py: StressScenario (wholesale/volume/IM shocks; is_severe); LiquidityStressOutcome (SOLVENT/MARGIN_CONSTRAINED/CRITICAL/INSOLVENT); StressTestResult (vm_drain/im_call/retail_inflow/ending_cash/survival_days/headroom_pct); LiquidityStressTestBook (run_scenario/standard_scenarios: mild/moderate/severe_2022/worst_outcome). 2022: IM tripled + daily VM = insolvency within weeks. Ofgem FRA: 365d comfort / 90d minimum.
**Phase CJ COMPLETE (2026-06-30):** Initial Margin Register -- 12 tests (5,933). company/trading/initial_margin_register.py: MarginAccountType (BILATERAL_OTC/EXCHANGE_CLEARED/INTERNAL_NETTING); IMStatus (POSTED/RETURNED/CALLED/PARTIAL); InitialMarginRecord (total_held_gbp=posted+additional; margin_rate_pct; is_active); InitialMarginRegister (post_margin/issue_additional_call/return_margin/total_locked_gbp/records_by_counterparty). 2022: clearing houses tripled IM requirements; combined IM+VM drain destroyed supplier liquidity. Extends Phase CC (variation margin).
**Phase CI COMPLETE (2026-06-30):** Annual Board Pack Synthesiser -- 12 tests (5,921). company/risk/annual_board_pack.py: BoardSignalRAG/BoardSignalCategory enums; BoardSignal (frozen; is_red/is_green); AnnualBoardPack (add_financial/risk/compliance/portfolio/strategic; red_signals/overall_rag/highest_risk_signals/pack_summary). Overall RAG = RED if any RED, AMBER if any AMBER. Aggregates all company-layer risk signals for CEO-level pack.
**Phase CH COMPLETE (2026-06-30):** Net Open Position Register -- 12 tests (5,909). company/trading/net_open_position_register.py: ExposureDirection (LONG_RETAIL/OVERHEDGED/FLAT ±5%); NOPSeverity (GREEN/AMBER/RED at 20%/40%); DeliveryPeriodPosition (nop_mwh/hedge_fraction_pct/direction/severity); NetOpenPositionRegister (red_positions/long_retail/overhedged/aggregate_for_year). Core risk metric: NOP = forwards - retail commitment; long retail in 2022 = catastrophic.
**Phase CG COMPLETE (2026-06-30):** Supplier Resilience Scorecard -- 12 tests (5,897). company/risk/supplier_resilience_scorecard.py: PillarScore (score_value 1-3 RED/AMBER/GREEN); 5 pillars: Liquidity (≥12m GREEN); Hedge (≥70%); Credit Quality (bad_debt ≤1%); Concentration (max_cust ≤20%); Stress Resilience (stressed_net≥1.0x). SupplierResilienceScorecard (composite_score/overall_rag/red_pillars). Ofgem FRA post-2022 framework.
**Phase CF COMPLETE (2026-06-30):** TPI Commission Book -- 12 tests (5,885). company/market/tpi_commission_book.py: TPITier (NATIONAL/REGIONAL/INDEPENDENT/ONLINE); CommissionType (UPFRONT/TRAIL/HYBRID); TPIAgreement (is_compliant=disclosed; rate_gbp_per_mwh); TPICommissionBook (register_tpi/record_payment/non_compliant_agreements/total_for_year/avg_rate_gbp_per_mwh). Ofgem 2022 disclosure rules. Typical trail rates £2-25/MWh I&C.
**Phase CE COMPLETE (2026-06-30):** SLC Compliance Tracker -- 12 tests (5,873). slc_compliance_tracker.py: SLCStatus/SLCCategory (7); SLCObservation (severity 0-2); SLCComplianceTracker (overall_rag/breached/at_risk/highest_severity_slcs). Consolidates SLC 6/14/21B/22/27/27A/31A/45 into single RAG.
**Phase CD COMPLETE (2026-06-30):** Customer Commodity P&L section -- 12 tests (5,861). _section_customer_commodity_pnl(): per-customer lifetime elec/gas split; loss-marking (*); gas loss summary; gas % of total. C_IC3g -£132,711; C4g -£1,950; C7 -£1,378 loss-making. Confirms Phase AR gas exit rationale.
**Phase CC COMPLETE (2026-06-30):** OTC Margin Call Book -- 12 tests (5,849). otc_margin_book.py: VariationMarginCall (CALL/RETURN; T+1 CSA; cash_impact/is_settled/is_overdue); OTCMarginBook (record/settle/pending/overdue/calls_by_counterparty/net_cash_for_year). Key 2022 supplier-failure mechanism.
**Phase CB COMPLETE (2026-06-30):** Hedge Value-Add Analysis -- 12 tests (5,837). _section_hedge_value_add(): actual vs naked net margin 10-yr table; value-add always negative (backwardation 2016-21; hedging cost £4.04M total vs spot). 2022 worst (-£988k); 2016 best (-£8.9k).
**Phase CA COMPLETE (2026-06-30):** Service Quality Monitor -- 12 tests (5,825). service_quality_monitor.py: RAG (clarity/complaint/shock); is_improving; quality_summary. Annual report: 10-yr table; 2022=RED; 2025 declining.
**Phase BZ COMPLETE (2026-06-30):** Portfolio Margin Sensitivity Analyser -- 12 tests (5,813). company/finance/portfolio_margin_sensitivity.py: 5-factor/10-row sensitivity table; wholesale most sensitive (-10.4%); LOW/MEDIUM/HIGH severity. Board tool using observed P&L fractions.
**Phase BY COMPLETE (2026-06-30):** VaR & Treasury -- 12 tests (5,801). Peak 2016(3.25); £2.47M→£3.59M.
**Phase BX COMPLETE (2026-06-30):** Fuel Mix -- 12 tests (5,789). 45.5%→68.5% LC; 55% ren 2025.
**Phase BW COMPLETE (2026-06-30):** Missed Retention -- 12 tests (5,777). C6 24.7% no-offer.
**Phase BV COMPLETE (2026-06-30):** Retention ROI -- 12 tests (5,765). 6.7×; 17/18 retained.
**Phase BU COMPLETE (2026-06-30):** Gas Exit -- 12 tests (5,753). Reprice +£135k vs SQ.
**Phase BT COMPLETE (2026-06-30):** Hedge Fraction -- 12 tests (5,741). 2019 naked; 79.3% 2024.
**Phase BS COMPLETE (2026-06-30):** Committee -- 12 tests (5,729). 2016: 13; 2022: 9.
**Phase BR COMPLETE (2026-06-30):** Worst Settlement Period -- 12 tests (5,717). 2023: -£3,475 (C_IC3g).
**Phase BQ COMPLETE (2026-06-30):** BSC & Levies -- 12 tests (5,705). £30→£10,210; mute 2021.
**Phase BP COMPLETE (2026-06-30):** Cohort Revenue -- 12 tests (5,693). 2017 £837k; 2019 loss.
**Phase BO COMPLETE (2026-06-30):** CfD & Treasury -- 12 tests (5,681). 2022 CfD CREDIT; draws 2022-2024.
**Phase BN COMPLETE (2026-06-30):** Segment Attribution -- 12 tests (5,669). 5×10yr table; 2022 resi gas -£742; I&C £964k.
**Phase BM COMPLETE (2026-06-30):** Price Cap Headroom -- 12 tests (5,657). 2021: 5/9 above SVT.
**Phase BL COMPLETE (2026-06-30):** Stress Test History -- 12 tests (5,645). 5 scenarios/yr RAG.
**Phase BK COMPLETE (2026-06-30):** Financial Ratios -- 12 tests (5,633). EBIT%/rev-per-cust; 2022 worst; peak £306k/cust.
**Phase BJ COMPLETE (2026-06-30):** Churn Calibration -- 12 tests (5,621). UNDER/ACCURATE/OVER + MAE; 5/6 underestimated.
**Phase BI COMPLETE (2026-06-30):** Tariff Accuracy -- 12 tests (5,609). GOOD/MODERATE/POOR; 2024 best 9.75%; 2023 worst 19.89%.
**Phase BH COMPLETE (2026-06-30):** Dynamic Pricing -- 12 tests (5,597). adj/delta/up/down/emergency by year; 2022 peak +18.1 £/MWh.
**Phase BG COMPLETE (2026-06-30):** CLV Evolution -- 12 tests (5,585). 2018 →£1M; peak 2025 £3.46M.
**Phase BF COMPLETE (2026-06-30):** Acquisition Strategy Intelligence -- 15 tests (5,573). acquisition_strategy_book.py: is_viable=CLV≥3×CAC; rank_channels; model_growth_scenario. PCW £55/ref £20/broker £160.
**Phase BE COMPLETE (2026-06-30):** Gross Margin Bridge -- 12 tests (5,558). YoY revenue/wholesale/GM; 2022 worst GM 24.8%; 2024 recovery 42.4%.
**Phase BD COMPLETE (2026-06-30):** Renewal Pricing Engine -- 15 tests (5,546). renewal_pricing_engine.py: FULL_MARGIN/COMPETITIVE/COST_PLUS/NO_OFFER; SVT-cap; I&C 0.3× decay; portfolio_renewal_plan.
**Phase BC COMPLETE (2026-06-30):** Risk Committee Activity Section -- 12 tests (5,531). _section_risk_committee_activity(): sessions/peak-VaR/accounts table; 38 sessions 2016-2025; 2016 busiest (13); 2023 peak VaR £130k (only 4 sessions); C1 adjusted 22× most.
**Phase BB COMPLETE (2026-06-30):** Risk Committee Decision Ledger -- 15 tests (5,519). risk_committee_ledger.py: EFFECTIVE/NEUTRAL/COUNTERPRODUCTIVE/PENDING (±£1k); intervention_effectiveness_rate; busiest_year; governance_summary.
**Phase BA COMPLETE (2026-06-30):** Price Elasticity Estimator -- 15 tests (5,504). price_elasticity.py: ElasticityBand/PriceChangeImpact/PortfolioImpact; PriceElasticityBook (crisis×1.5; estimate_churn_impact; optimal_tariff_change). CMA 2016: resi=-0.18; SME=-0.12; I&C=-0.05.
**Phase AZ COMPLETE (2026-06-30):** I&C Triad Notification Book -- 15 tests (5,489). triad_notification_book.py: TriadNotificationBook (enrol/issue_alert/savings_summary). 2022 £60.40/kW; C_IC3 1000kW→£42,280 at 70% response.
**Phase AY COMPLETE (2026-06-30):** Customer Strategic Value Matrix -- 12 tests (5,474). _section_customer_strategic_value(): 2x2 CLV×churn quadrant; PROTECT/CRITICAL/MONITOR/EXIT. I&C (99% CLV) in PROTECT.
**Phase AX COMPLETE (2026-06-30):** Customer Experience & Service Quality -- 12 tests (5,462). _section_customer_experience(): clarity/complaint-prob + flags; 2025=0.777 (worst clarity); 0/5 acquisition wins.
**Phase AW COMPLETE (2026-06-30):** Bill Shock Analysis -- 12 tests (5,438). annual_report.py: _section_bill_shock_analysis(): avg_shock %/events/bills/shock-rate by year; HIGH >=30%/ELEVATED >=20% flags; crisis peak note (2022=33.8%, SLC 21 note). Normal 14-17%, crisis 34%.
**Phase AV COMPLETE (2026-06-30):** Policy Cost & Levy Breakdown -- 12 tests (5,426). _section_policy_cost_breakdown(): RO/CfD/CCL/CM/FiT per year; negative 2022 CfD noted (spot>strike); CAGR 76.7%/yr.
**Phase AU COMPLETE (2026-06-30):** Commodity Split -- 12 tests (5,414). _section_commodity_split(): elec/gas net+revenue per year; profitable flag; gas-share%. Gas loss-making since 2021 (was profitable 2016-20).
**Phase AT COMPLETE (2026-06-30):** Management Accounts P&L Section -- 12 tests (5,402). _section_management_accounts(): income statement + balance sheet per year; best/worst year annotation.
**Phase AS COMPLETE (2026-06-30):** Gas Exit Analysis Report Section -- 10 tests (5,390). _section_gas_exit_analysis(): 3-scenario table (SQ/EXIT/REPRICE) with ROC + breakeven uplift per account.
**Phase AR COMPLETE (2026-06-30):** Gas Exit Decision Book -- 14 tests (5,380). gas_exit_analysis.py: 3 scenarios (SQ/EXIT/REPRICE); I&C 40%/resi 20% churn on exit. REPRICE +£134k; EXIT +£99k vs SQ.
**Phase AQ COMPLETE (2026-06-30):** Board Risk Summary -- 12 tests (5,366). _section_board_risk_summary(): 6 RAG indicators; 4 RED (gas-ROC=-0.7x, churn-miss 67%, demand-error 3.3%/15.6%, basis-risk +32.8%), 1 AMBER, 1 GREEN.
**Phase AP COMPLETE (2026-06-30):** Segment Capital Efficiency -- 12 tests (5,354). _section_segment_capital_efficiency(): lifetime ROC per segment; CAPITAL DESTROYER flag; I&C gas=-0.7x, resi gas=-0.9x; electricity cross-subsidises.
**Phase AO COMPLETE (2026-06-30):** Demand Estimation Error Trend -- 12 tests (5,342). demand_error_by_year; 0.07%→15.56% by 2024.
**Phase AN COMPLETE (2026-06-30):** Portfolio Concentration Risk -- 12 tests (5,330). HHI=2249 MODERATE; I&C=98.7% portfolio.
**Phase AM COMPLETE (2026-06-30):** Pricing Basis Risk -- 12 tests (5,318). company_fwd vs sim_fwd; HIGH OVER-PRICE 2023/2025 (+18-33%).
**Phase AL COMPLETE (2026-06-30):** Counterfactual Retention -- 12 tests (5,306). £3,621 recoverable from 4 blind misses at £293 cost.
**Phase AK COMPLETE (2026-06-30):** Churn Root Cause Attribution -- 14 tests (5,294). 6 churns £39,706 lost; 3 blind misses.
**Phase AJ COMPLETE (2026-06-30):** CRM Risk Triage -- 14 tests (5,280). CRITICAL/HIGH/MEDIUM/LOW triage; rate-vs-SVT.
**Phase AI COMPLETE (2026-06-30):** EAC Drift Snapshot -- 10 tests (5,266). Demand drift per customer; EV/solar/efficiency.
**Phase AH COMPLETE (2026-06-30):** Board Intelligence Pack -- 12 tests (5,256). Retention/flex CAGR/churn peak/4 board recs.
**Phase AG COMPLETE (2026-06-30):** Annual Report Flex Revenue Section -- 12 tests (5,244). CM/DFS table; pre-DFS labels.
**Phase AF COMPLETE (2026-06-30):** DSR/Flexibility Revenue Integration -- 15 tests (5,232). CM £75/kW/yr; DFS £4.5/MWh×20; EV+battery £2,046/yr.
**Phase AE COMPLETE (2026-06-29):** Customer Retention Offer Book -- 21 tests (5,217). company/crm/customer_retention.py: OfferType; RetentionOffer (max_spend=50%); EV+shock→TOU/8%/5% offers.
**Phase AD COMPLETE (2026-06-29):** Portfolio Churn Risk Book -- 34 tests (5,196). portfolio_churn_risk.py: ChurnRiskBand/Driver; PortfolioChurnRiskBook (by_band/by_driver/rate_pct). Connects J, M, AC.
**Phase AC COMPLETE (2026-06-29):** Portfolio Repricing Action Book -- 24 tests (5,162). company/crm/portfolio_repricing.py: RepricingPriority (CRITICAL/HIGH/MEDIUM/MONITOR); RepricingAction (tariff_delta/recovery at 70% retention); EV 3,000→11,000 kWh = £2,000/yr delta, £1,400/yr recovery. Connects AB, M, K.
**Phase AB COMPLETE (2026-06-29):** EAC Drift Assessor -- 35 tests (5,138). company/crm/eac_drift_assessor.py: DriftDirection/RenewalAction; EACDriftBook (urgent_reprice/mean_drift_pct). EV 3,000→11,000 kWh = URGENT_REPRICE. Connects C, H, M.
**Phase AA COMPLETE (2026-06-29):** Demand Flexibility Potential Assessor -- 23 tests (5,103). company/market/flexibility_potential.py: FlexibilityPotentialBook (EV/ASHP/BATTERY types; DFS £4.5/MWh×20; CM £75/kW/yr; EV+battery £2,046/yr). Connects to dsr_book.py.
**Phase Z COMPLETE (2026-06-29):** Smart Meter Reconciliation Book -- 23 tests (5,080). smart_meter_reconciliation.py: ReconciliationType/ReconciliationAdjustment (SLC31A 12m cap); SmartMeterReconciliationBook. Domestic undercharges >12m not recoverable; I&C always recoverable.
**Phase Y COMPLETE (2026-06-29):** ToU Rate Card Optimiser -- 29 tests (5,057). tou_rate_card.py: 3 candidates (Octopus Go/aggressive/conservative); viable_rates/optimal_rate. Octopus Go not viable at 20% margin threshold. Completes T-U-V-X-Y.
**Phase X COMPLETE (2026-06-29):** ToU Product Launch Decision Engine -- 25 tests (5,028). LaunchReadinessSignal/ToUProductLaunchBook; EV penetration/margin thresholds. HOLD for EV-heavy portfolio (cross-subsidy). Completes T-U-V-X chain.
**Phase W COMPLETE (2026-06-29):** Gas Boiler Daily HDD Shape -- 13 tests (5,003). gas_settlement.py: 70% heating (HDD-weighted) + 30% DHW; I&C keeps monthly profile.
**Phase V COMPLETE (2026-06-29):** ToU Migration Impact Scenario -- 16 tests (4,990). tou_migration_scenario.py: 0% migration best for all-EV portfolio (flat cross-subsidy never recovered under ToU).
**Phase U COMPLETE (2026-06-29):** EV Cross-Subsidy Register -- 16 tests (4,974). company/pricing/ev_cross_subsidy.py: CrossSubsidyRecord + CrossSubsidyRegister. Connects Phase T.
**Phase T COMPLETE (2026-06-29):** ToU Tariff Profitability Assessor -- 16 tests (4,958). tou_tariff_assessor.py: OVERNIGHT_HEAVY/STANDARD_FLAT/PEAK_HEAVY; EV = 4x more margin flat vs ToU (£746 vs £189). Enabled by Phase P.
**Phase P COMPLETE (2026-06-29):** EV Smart Charging Shape (Overnight-Weighted) -- 12 tests (4,942). _EV_OVERNIGHT_PERIODS: 23:00-07:00 (16 HH); 90%/10% overnight/day (UK SCPR 2021). Triad low; overnight 9x daytime. Precondition for Phase T.
**Phase S COMPLETE (2026-06-29):** Dual-Fuel Billing Engine + Payment Ledger -- 44 tests (4,930). dual_fuel_bill.py/payment_ledger.py: VAT resi=5%/I&C=20%/SME usage-gated; billing_calendar.
**Phase R COMPLETE (2026-06-29):** SEG Export Estimator -- 21 tests (4,886). seg_export_estimator.py: 850 kWh/kWp/yr; BEIS 2022 50%/70% self-consumption; 2022=7.5p, 2020=4.0p.
**Phase Q COMPLETE (2026-06-29):** Battery Settlement Wiring -- 14 tests (4,865). _battery_daily_dispatch(): charge solar excess; discharge peaks (33-40); 90% roundtrip. HH gap closed.
**Phase O COMPLETE (2026-06-29):** Solar Dynamic Settlement Wiring -- 12 tests (4,851). run_phase2b.py: dynamic solar assets update; cloud_cover/latitude for all profile-class customers. Solar-via-life-events now reduces import. Phase 25a unaffected.
**Phase N COMPLETE (2026-06-29):** EV Settlement Wiring + Physical Suitability -- 26 tests (4,861). household.py: has_driveway/roof_aspect/hp_eligible; EV/solar/HP acquisition gates. EV flat demand shape in run_phase2b.py. Flats/no-driveway cannot acquire EV.
**Phase M COMPLETE (2026-06-29):** Renewal Conversion Rate Book -- 21 tests (4,835). renewal_conversion.py: RenewalRecord (SLC22 42-day/is_retained); RenewalConversionBook (conversion_rate/notice_breaches/best_segment). Completes CRM lifecycle.
**Phase C COMPLETE (2026-06-27):** Household-Driven EAC Integration -- 26 tests (4,653 passing). HouseholdDemandRegister: epc_multiplier/eac_multiplier_for_date/dynamic_assets. First time Phase A+B affect actual P&L.
**Phase B COMPLETE (2026-06-27):** Life events engine -- 32 tests (4,626). life_events.py: Bernoulli trials (solar 3→5.7%, EV 0.3→7%, ASHP); apply_events/household_at_date. No flat solar; no I&C EVs; battery on solar only.
**Phase A COMPLETE (2026-06-27):** Household physical model -- 36 tests (4,594). household.py: Household frozen dataclass (PropertyType/BuildEra/HeatingSystem/InsulationLevel enums; epc_consumption_multiplier EHS 2022-23); make_household/build_household_register for all 18 customers.
**Phase 332 COMPLETE (2026-06-27):** Risk Committee Deterministic Engine + File API Fix -- 21 tests (4,559). parse_handshake/apply_rules: +0.15/0.20/0.25 by VaR ratio; LLM only if sigma>1.5 or all maxed. Removes ~95% Ollama calls. File API: auto-loads .env.file-api.
**Phase 331 COMPLETE (2026-06-27):** Dual-Fuel Account Consolidator -- 25 tests (4,538). dual_fuel_account.py: FuelLeg (MPAN/MPRN); DualFuelAccount (is_dual_fuel/combined_cost/active_fuels); MPAN+MPRN separate settlement, one account.
**Phase 330 COMPLETE (2026-06-27):** Payment Method Register -- 22 tests (4,513). payment_method_register.py: DD/PPM/BACS/CHEQUE/CASH; debt-mandated PPM (SLC 27); 2023 forced-fitting scandal. UK ~70% DD, ~15% PPM.
**Phase 329 COMPLETE (2026-06-27):** Fuel Poverty Indicator Book -- 21 tests (4,491). fuel_poverty.py: CLASSIC/LIHC/AFFORDABLE_WARMTH definitions; LIHC: below 60% median after costs AND >10% energy spend; 6.5M UK households fuel poor 2023.
**Phase 328 COMPLETE (2026-06-27):** Disconnection Warning Register -- 17 tests (4,470). disconnection_warning.py: SLC 27 4-contact sequence (W1/W2/W3/NOTICE) + 28-day notice; 2023 Ofgem investigated for skipped steps.
**Phase 327 COMPLETE (2026-06-27):** Third Party Authority Register -- 19 tests (4,453). tpa_register.py: TPAScope (VIEW_ONLY/BILLING/FULL_AUTHORITY); 6 relationships incl. POA; Consumer Duty: must accept designated TPAs.
**Phase 326 COMPLETE (2026-06-27):** DD Indemnity Claim Register -- 23 tests (4,434). dd_indemnity.py: BACS Guarantee immediate refund; 10-WD investigation; upheld = debt; overdue_investigations.
**Phase 325 COMPLETE (2026-06-27):** Winter Disconnection Moratorium -- 25 tests (4,411). winter_moratorium.py: SLC 27 Nov-Mar domestic ban; vulnerable year-round; is_winter_period() helper.
**Phase 324 COMPLETE (2026-06-27):** MHHS Readiness Tracker -- 22 tests (4,386). mhhs_tracker.py: 8 milestones DCC→GO_LIVE; shadow Nov-2024 / production June-2025; RAG overdue tracking.
**Phase 323 COMPLETE (2026-06-27):** Energy Theft Reporting Book -- 21 tests (4,364). energy_theft_book.py: GS(SS)5 2-WD DNO notification; 3-year back-bill exception; CONFIRMED/DNO_NOTIFIED/ESTIMATED_BILL_RAISED states.
**Phase 322 COMPLETE (2026-06-27):** Deemed Contract Register -- 22 tests (4,343). deemed_contract.py: SLC 2B 5-WD notification; 12m extended deemed; COT/new occupant auto-supply.
**Phase 321 COMPLETE (2026-06-27):** SoLR Register -- 24 tests (4,321). solr_register.py: 5-day notice / 30-day offer / 90-day SVT. 2021-22: 28 failures, 4M customers transferred via SoLR.
**Phase 320 COMPLETE (2026-06-27):** Credit Refund Book -- 26 tests (4,297). credit_refund.py: SLC 14 10-working-day deadline; weekday-aware overdue detection; 2022 Ofgem enforcement for credit withholding.
**Phase 319 COMPLETE (2026-06-27):** Hedge Effectiveness Assessment Book -- 29 tests (4,271). hedge_effectiveness.py: IFRS 9 80-125% band; de-designation on fail; 2022 volume shrinkage = widespread failures. EffectivenessOutcome (HIGHLY_EFFECTIVE/INEFFECTIVE).
**Phase 318 COMPLETE (2026-06-27):** Financial Resilience Assessment Book -- 27 tests (4,242). financial_resilience.py: FRAStatus (RESILIENT/ADEQUATE/BORDERLINE/INADEQUATE); 12m liquidity min; stress+VaR must pass. Ofgem post-2022: 28 failures.
**Phase 317 COMPLETE (2026-06-27):** VAT Book -- 20 tests (4,215). vat_book.py: 5%/20% rates; SME ≤33kWh/day threshold; quarterly returns; is_repayment flag. Finance Act 1994.
**Phase 316 COMPLETE (2026-06-27):** Corporation Tax Provision Book -- 24 tests (4,195). corporation_tax.py: 20%/19%/25% rates; loss-carry-forward; 2023 25% = biggest UK CT rise since 1974.
**Phase 315 COMPLETE (2026-06-27):** Payment Plan Adequacy Checker -- 19 tests (4,171). payment_plan_adequacy.py: AFFORDABLE/BORDERLINE/UNAFFORDABLE; 15%/25% disposable income thresholds (SLC 27A ATP). 2022-23: 40% of plans unaffordable.
**Phase 314 COMPLETE (2026-06-27):** Back-billing Compliance Book -- 16 tests (4,152). back_billing.py: SLC 31A 12-month cap (post May-2018 domestic); BackBillingAssessment (cap_applies/capped_amount/written_off); ~£90M sector write-off 2018-22.
**Phase 313 COMPLETE (2026-06-27):** PPM Debt Loading Tracker -- 19 tests (4,136). ppm_debt_loading.py: £250 cap/5% rate cap/smart-meter consent (Ofgem 2019); 2023 forced-fitting scandal context.
**Phase 312 COMPLETE (2026-06-27):** Account Closure Book -- 23 tests (4,117). account_closure.py: 7 ClosureStatuses; 42-day final bill SLC 21B; deposit returned or debt referred. Closes lifecycle loop.
**Phase 311 COMPLETE (2026-06-27):** Debt Collection Process Book -- 26 tests (4,094). debt_collection.py: 6 DebtStages; statute-barred >6yr; recovery 95%→0%; agency 65p/£; SLC 27A.
**Phase 310 COMPLETE (2026-06-27):** Smart Export Guarantee (SEG) Book -- 20 new tests (4,068 passing). company/regulatory/seg_book.py: SEGTechnology, SEGContract (frozen; is_active), SEGPayment (frozen; payment_gbp), SEGBook (seg_rate_for_year/register_contract/terminate_contract/record_payment/active_contracts/payments_for_customer/payments_for_year/total_paid_gbp/total_export_kwh/seg_summary). SEG replaced FIT export Jan 2020; mandatory for >150k domestic customers; not levy-recoverable. Connects to fit_book (Ph286), eep_book, decarbonisation_score (Ph279).
→ Phases 1–309: `docs/claude/phase-history.md` | Earlier: `CLAUDE_HISTORY.md`
---
## Architectural Laws — Epistemic Honesty: The Company Cannot See Inside the SIM
The company layer operates under the same information constraints as a real energy supplier.
It cannot see simulation internals — churn parameters, forward curve construction, weather
engine outputs, VaR internals. It discovers the world through observable interfaces: market data feeds, meter reads, customer interactions, its own bills and payments, regulatory publications.
The company's models are approximations built from observed outcomes — not reads from ground
truth. That imperfection is the point.
**Before writing any company-layer code:** ask "Could a real UK energy supplier know this?"
If the answer requires reading simulation internals, it is a violation.
The SIM/company seam (`company/interfaces/sim_interface.py`) exposes observables only, never internals.
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
**Network/AI:** Tailscale WSL2 `100.69.81.59` | File API `https://skynet-1.taila062fa.ts.net:8765` | Claude Code → qwen3:14b/Ollama → risk committee (Ollama)
**Key paths:** `docs/staging/` (instructions) | `docs/status/LATEST.md` | `docs/reports/ANNUAL_REPORT.md`
**Data:** Elexon `data.elexon.co.uk` (key-free; API migrated to Insights Solution — legacy wrappers partly stale) | NESO CKAN | Open-Meteo | synthetic forward curves
