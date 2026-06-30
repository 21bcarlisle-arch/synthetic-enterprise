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
- `run_complete_*.md` — publish results (regenerate report, LATEST.md, dashboard.json), commit, push, archive. **Do NOT send NTFY for routine sim run completions.** Only NTFY for notable exceptions (admin event, all-time high/low margin). Batch silently if multiple queued.
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
**Phase DO COMPLETE (2026-06-30):** Embedded Network Supply Register -- 23 tests (5,813 total). company/market/embedded_network_register.py: EmbeddedNetworkType (RESIDENTIAL_BLOCK/COMMERCIAL_PARK/MIXED_USE/STUDENT_ACCOMMODATION/MARINA/CARAVAN_PARK); ENOStatus (ACTIVE/TERMINATED/DISPUTED/EXEMPT); EmbeddedNetworkRecord (frozen; rate_premium_pct; is_rate_compliant: ≤20% above DNO; rate_excess_pct); EmbeddedNetworkRegister (register/terminate/active_networks/non_compliant_rates/total_units/by_type/terminated_networks/embedded_network_summary). Ofgem 2024 EN protections; 28-day switching notice; 20% rate cap above DNO.
**Phase DN COMPLETE (2026-06-30):** SLC Compliance Tracker tests -- 21 tests (5,790 total). company/regulatory/slc_compliance_tracker.py (existing, tested): SLCStatus (COMPLIANT/BREACH_RISK/BREACHED/N_A/UNKNOWN); SLCCategory (BILLING/CREDIT/DEBT/METERING/RENEWAL/VULNERABILITY/SMART); SLCObservation (frozen; is_compliant/is_breached/severity_score 0/1/2); SLCComplianceTracker (record/get/all_observations sorted/breached/at_risk/compliant/total_breach_count/total_at_risk_count/overall_rag RED/AMBER/GREEN/by_category/highest_severity_slcs(n)/compliance_summary). 8 SLCs tracked (6/14/21B/22/27/27A/31A/45).
**Phase DM COMPLETE (2026-06-30):** Priority Services Register (PSR) -- 25 tests (5,769 total). company/regulatory/priority_services_register.py: PSRCategory (9 categories: pensionable_age/disability/medical_equipment/child_under_5/chronic_illness/mental_health/visual_impairment/hearing_impairment/language_support); PSRService (6 core services); PSRRecord (frozen; is_electricity_dependent on MEDICAL_EQUIPMENT; needs_priority_reconnection MEDICAL+PENSIONABLE; is_review_overdue(as_of) method; has_at_least_one_service; is_compliant); PriorityServicesRegister (register/deregister(sets_inactive)/active_records/electricity_dependent/priority_reconnection_customers/non_compliant_records/network_shared_count/overdue_reviews(as_of)/psr_penetration_pct/psr_summary). SLC 26B; UK ~31% penetration; 4h priority reconnection. Fixed date.today() antipattern → as_of params.
**Phase DL COMPLETE (2026-06-30):** Price Transparency Publication Register -- 22 tests (5,744 total). company/pricing/price_transparency_register.py: PublicationChannel (WEBSITE/OFGEM_FEED/COMPARISON/MIDATA); TariffType (FIXED/VARIABLE_SVT/ECONOMY_7/TOU/PREPAYMENT); UpdateStatus (PUBLISHED/PENDING/STALE/WITHDRAWN); TariffPublication (frozen; rate_change_pct/is_rate_increase; is_stale: PENDING >48h SLC 31; annual_cost_estimate_gbp at 3,100 kWh typical domestic); PriceTransparencyRegister (publish/active_tariffs/stale_publications/by_channel/rate_increases/withdrawn/cheapest_active/price_transparency_summary). SLC 31 / TCT feed. 30-day notice on rate change (SLC 22).
**Phase DK COMPLETE (2026-06-30):** Switching Cost Model -- 20 tests (5,722 total). company/crm/switching_cost_model.py: MeterType (LEGACY_MANUAL/SMART_SMETS1/SMART_SMETS2); CustomerSegment; SwitchingCostBreakdown (frozen; meter_read_cost_gbp ×2 dual-fuel; final_bill ×1.5 dual-fuel; mpas=£17.50; da_dc=£15; staff £35/65/150 by segment; bad_debt_risk_gbp: 5%/3% domestic/commercial; total/direct_cost_gbp); SwitchingCostModel (estimate/max_retention_offer_gbp: switch_cost + margin headroom above floor; portfolio_summary). Calibrated to UK Ofgem 2022-24 switching data. Informs retention offer pricing.
**Phase DJ COMPLETE (2026-06-30):** Statutory Annual Accounts Register -- 30 tests (5,702 total). company/regulatory/statutory_accounts_register.py: AccountsType (MICRO/SMALL/MEDIUM/LARGE by revenue); FilingStatus (DRAFT→SIGNED_OFF→SUBMITTED→ACCEPTED/REJECTED/LATE); DisclosureFlag (SECR/TCFD/GENDER_PAY_GAP/AUDIT_REQUIRED); StatutoryAccountsRecord (frozen; filing_deadline=FYE+9m; is_overdue/days_overdue; late_penalty_gbp: £150/375/750/1500 by bracket; requires_audit for MEDIUM+LARGE); StatutoryAccountsRegister (classify static/record_year/overdue/total_penalty_exposure_gbp/filed/requiring_audit/statutory_accounts_summary). CA2006 s442; SECR 2019+; TCFD 2023+.
**Phase DI COMPLETE (2026-06-30):** Social Obligation Spend Register -- 24 tests (5,672 total). company/regulatory/social_obligation_register.py: SocialObligationType (WHD/PSR/ENERGY_EFFICIENCY/FUEL_POVERTY/CARBON_OFFSET); ObligationStatus (PROJECTED→COMMITTED→PAID/UNDERPERFORMING/COMPLIANT); SocialObligationRecord (frozen; variance_gbp/is_underspend/spend_rate/cost_per_beneficiary_gbp/is_compliant); SocialObligationSpendRegister (estimate_whd_levy: 18×customers; record_obligation/for_year/by_type/non_compliant/underspend_records/total_spend_gbp/total_target_gbp/total_beneficiaries/annual_summary). WHD Scheme Regs 2011: £150/customer benefit; ECO4 2022-2026; Ofgem annual reporting.
**Phase DH COMPLETE (2026-06-30):** BSC Settlement Run Tracking Register -- 25 tests (5,648 total). company/market/bsc_settlement_run_register.py: SettlementRunType (SF/R1/R2/R3/RF); AdjustmentDirection; SettlementRunRecord (frozen; adjustment_gbp=0 for SF; direction; variance_pct=|adj|/prior; is_material ≥5%; is_final; expected_run_date); BSCSettlementRunRegister (record_run/runs_for_date/by_run_type/material_variances/credits/debits/total_adjustment_gbp/total_credit_gbp/total_debit_gbp/finalised_dates/run_type_breakdown). BSC P272/SVA: SF→R1→R2→R3→RF; R2/R3 most material as smart meter actuals replace estimated reads. Smart meter rollout shrinks variance gap.
**Phase DG COMPLETE (2026-06-30):** Consumer Vulnerability Duty Action Register -- 23 tests (5,623 total). company/regulatory/consumer_vulnerability_register.py: VulnerabilityCategory (8: MEDICAL_DEPENDENCY/MENTAL_HEALTH/BEREAVED/FINANCIAL_HARDSHIP/ELDERLY_FRAIL/DISABILITY/LANGUAGE_BARRIER/TEMPORARY); VulnerabilityAction (10: PSR_ENROLMENT/PPM_WAIVER/DEBT_WRITEOFF/DISCONNECTION_HOLD/etc.); ActionOutcome; VulnerabilityActionRecord (follow_up_overdue(as_of)/is_medical/is_effective); ConsumerVulnerabilityRegister (record_action/actions_for/by_category/by_action_type/medical_dependency_accounts/overdue_follow_ups/effectiveness_rate/disconnection_holds). Ofgem CSV2/SLC 26B. Companion to Phase DF (SAR) and Phase 329 (PSR).
**Phase DF COMPLETE (2026-06-30):** Data Subject Access Request Register (UK GDPR Art.15) -- 32 tests (5,600 total). company/regulatory/sar_register.py: SARStatus (6); SARTrigger (7 incl. PRE_LITIGATION/OMBUDSMAN_REFERRAL); SARRefusalReason (4); SARRecord (deadline=+30d/+90d extended; is_overdue(as_of)/days_to_deadline/days_to_respond/responded_within_deadline/is_active); SARRegister (receive/acknowledge/extend/respond/refuse/mark_ico_complaint/overdue/active/late_responses/by_trigger/compliance_rate). UK GDPR Art.15; 30-day standard/90-day extended; max fine GBP17.5M. Companion to ICO breach register (Phase DB).
**Phase DE COMPLETE (2026-06-30):** Energy Bills Support Scheme (EBSS) Register -- 28 tests (5,568). company/regulatory/ebss_register.py: EBSSDeliveryMethod (AUTOMATIC_CREDIT/VOUCHER/SMART_PPM_CREDIT); EBSSRedemptionStatus (6 states); _EBSS_INSTALMENT_SCHEDULE Oct=GBP66/Nov=GBP67/Dec-Mar=GBP66 (GBP400 total); EBSSRegister (apply_instalment raises outside Oct22-Mar23; redeem_voucher/expire_voucher/mark_recovered; unredeemed_vouchers/expired_vouchers). Domestic counterpart to EBRS. PPM voucher failure = 2022-23 scandal.
**Phase DD COMPLETE (2026-06-30):** Energy Bill Relief Scheme (EBRS) Register -- 28 tests (5,540). company/regulatory/ebrs_register.py: EBRSFuel/EBRSEligibilityStatus/RecoveryStatus; is_eligible_period (Oct22-Mar23); EBRSRecord (discount_applied=contract_rate - baseline; outstanding_recovery_gbp); EBRSRegister (record_billing_month/claim_recovery/mark_paid; by_fuel/pending_claims). Baselines: electricity 21.1p/kWh, gas 7.5p/kWh (BEIS). Domestic=always ineligible. GBP5.5B total cost.
**Phase DC COMPLETE (2026-06-30):** EMIR Trade Repository Reporting Register -- 29 tests (5,512). company/trading/emir_reporting_register.py: CounterpartyType (FC/NFC/NFC+); ReportingStatus (PENDING/REPORTED/LATE_REPORTED/AMENDED/CANCELLED/FAILED); _add_working_days (weekend skip); EMIRTradeRecord (uti=GB+LEI+date+id; T+1 working day deadline; is_overdue/is_late); EMIRReportingRegister (record_trade/report/amend/cancel/mark_failed; overdue/late_reports; compliance_rate; total_notional_gbp excludes cancelled). UK EMIR SI 2019/335; FCA max fine GBP7.2M.
**Phase DB COMPLETE (2026-06-30):** ICO Data Breach Notification Register (UK GDPR) -- 33 tests (5,483). company/regulatory/ico_breach_register.py: BreachType/DataCategory (BANK_DETAILS/SMART_METER/VULNERABILITY_FLAGS = sensitive); BreachSeverity; ICONotificationStatus/IndividualNotificationStatus; DataBreachRecord (is_within_72h; notification_overdue; contains_sensitive_data; maximum_fine_exposure: Art83(5)=GBP17.5M/Art83(4)=GBP8.75M); ICOBreachRegister (record_breach/_assess_severity; notify_ico/complete_individual_notification/close; active_breaches/overdue; total_fine_exposure). 72h ICO window; smart meter data = sensitive.
**Phase DA COMPLETE (2026-06-30):** Customer Comm Preferences -- 12 tests (6,140). company/crm/customer_comm_preferences.py: CommChannel (EMAIL/POST/PHONE/SMS/PORTAL/PAPER_BILL); CommPurpose (BILLING/SERVICE_NOTICE essential; MARKETING requires opt-in); CustomerCommPreferences (can_contact/marketing_opt_in/suppressed); CustomerCommPreferenceRegister (set_preference/set_marketing_opt_in/suppress_account/paperless_accounts). GDPR/PECR/SLC 25C.
**Phase CZ COMPLETE (2026-06-30):** Revenue Protection Register -- 12 tests (6,128). revenue_protection_register.py: 5 RPCaseType incl. METER_TAMPERING/SUPPLY_DIVERSION; open_case/confirm/recover/write_off; 3yr theft backbill exception (vs SLC 31A 12m cap).
**Phase CY COMPLETE (2026-06-30):** Supplier Fitness Register -- 13 tests (6,116). supplier_fitness_register.py: Ofgem LC 30A fit-and-proper for directors; annual review; PRIOR_SUPPLIER_FAILURE flagged; not_fit_persons/overdue_reviews.
**Phase CX COMPLETE (2026-06-30):** Regulatory Breach Log -- 12 tests (6,103). regulatory_breach_log.py: POTENTIAL→CONFIRMED→REMEDIATED/REPORTED_TO_OFGEM; is_reportable (H/C); total_estimated_penalty_gbp; by_slc. Ofgem up to 10% turnover.
**Phase CW COMPLETE (2026-06-30):** Licence Application Register -- 12 tests (6,091). licence_application_register.py: 4 LicenceTypes; TIER_1/2; submit/decide/licences_with_special_conditions. Post-2022 Ofgem continuation required when FRA deteriorates.
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
→ Phases 1–AP: `docs/claude/phase-history.md` | Earlier: `CLAUDE_HISTORY.md`
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
