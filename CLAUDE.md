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

**Phase 193 COMPLETE (2026-06-26):** Demand-Side Response (DSR) programme book -- 7 new tests (2,822 passing). company/market/dsr_book.py (new): DSRStatus (ENROLLED/ACTIVE/SUSPENDED/WITHDRAWN), DispatchResult (DELIVERED>=95%/PARTIAL/NON_DELIVERY/CANCELLED), DSRParticipant (frozen: contracted_mw/payment_per_mwh_gbp), DispatchEvent (frozen: duration_hours/delivered_mwh/delivery_rate/payment_gbp), DSRBook (enroll/dispatch/events_for_customer/total_contracted_mw/total_payments_gbp/delivery_rate_year/annual_summary). I&C customers can earn £50-100/MWh dispatched.
**Phase 192 COMPLETE (2026-06-26):** Gas MPRN supply point register -- 9 new tests (2,815 passing). company/market/mprn_register.py (new): GasConsumptionBand (DOMESTIC <=73.2 MWh / SMALL_NON_DOMESTIC <=293 MWh / MEDIUM_NON_DOMESTIC <=732 MWh / LARGE), classify_gas_band(), MPRNStatus (REGISTERED/DEREGISTERED/PENDING_REGISTRATION/PENDING_SWITCH/DISCONNECTED/OBJECTED), MPRNRecord (frozen: consumption_band/is_active), MPRNRegister (register/initiate_switch/complete_switch/deregister/active_mprns/by_band/portfolio_summary with total_aq_kwh). Xoserve MPRN management (gas equivalent of MPAS).
**Phase 191 COMPLETE (2026-06-26):** Risk appetite framework -- 8 new tests (2,806 passing). company/risk/risk_appetite.py (new): RiskCategory (MARKET/CREDIT/LIQUIDITY/OPERATIONAL/REGULATORY), RiskRAG (WITHIN_APPETITE/APPROACHING_LIMIT/LIMIT_BREACH), RiskLimit (frozen: warning_value at 80% of limit), RiskMeasurement (frozen: utilisation_pct/rag/is_breach), RiskAppetiteFramework (add_limit/record_measurement/latest_measurement/active_breaches/risk_dashboard). 2022: bad_debt_pct 5% vs 3% limit -> LIMIT_BREACH; open_position 5,500 MWh vs 5,000 -> BREACH.
**Phase 190 COMPLETE (2026-06-26):** Ofgem annual supply data return -- 8 new tests (2,798 passing). company/regulatory/ofgem_supply_return.py (new): OfgemSupplyReturn (frozen: total_customers/complaints_per_100/is_submitted/whd_penetration_pct/summary()), OfgemReturnBook (file_return/get/missing_years/all_returns sorted by year). 2022 crisis: avg_debt_per_customer £180, bad_debt_written_off £900k, complaints_per_100=10 (3x Ofgem benchmark). Missing years signal compliance gap before Ofgem enforcement.
**Phase 189 COMPLETE (2026-06-26):** Contact centre performance metrics -- 9 new tests (2,790 passing). company/crm/contact_centre_metrics.py (new): AgentPerformancePeriod (frozen: calls_handled/fcr/escalations/complaints/csat; avg_handle_time_seconds/fcr_rate/escalation_rate/complaint_rate), ContactCentreMetrics (frozen: total_calls/answered_sla/abandoned/handle_time/agents; abandonment_rate/sla_answer_rate/avg_handle_time/calls_per_agent/summary()). 2022 crisis: call volumes 3x normal, abandonment_rate peaked at 25%, SLA answer rate dropped to 40%.
**Phase 188 COMPLETE (2026-06-26):** Supplier of Last Resort (SoLR) intake management -- 8 new tests (2,781 passing). company/crm/solr_intake.py (new): SoLRIntakeStatus (NOTIFIED/CONTACTED/ONBOARDED/SWITCHED_AWAY/UNRESPONSIVE), SoLRBatch (frozen: failed_supplier/appointment_date/customer_count/deemed_tariff_rate_pct_above_cap/is_priced_above_cap), SoLRCustomer (mutable: mark_contacted/onboarded/switched_away), SoLRBook (register_batch/add_customer/retention_rate/contact_rate/batch_summary). 2021: Bulb SAR -> SoLR-appointed suppliers received 1,700 stranded customers each.
**Phase 187 COMPLETE (2026-06-26):** CLV cohort analysis book -- 9 new tests (2,773 passing). company/crm/clv_cohort_book.py (new): CustomerCLVRecord (frozen: acquisition_year/channel/segment/clv/annual_margin/tenure), CohortSummary (frozen: avg/median/total CLV, avg_margin/tenure, profitable_pct, is_profitable_cohort), CLVCohortBook (add/by_acquisition_year/by_channel/by_segment/all_cohorts_by_year/best_cohort_by_year/worst_cohort_by_year/portfolio_summary). 2022 cohort: profitable_pct=0% when crisis-acquired customers churn immediately with negative CLV.
**Phase 186 COMPLETE (2026-06-26):** Supplier switching analytics -- 8 new tests (2,764 passing). company/crm/switch_analytics.py (new): SwitchDirection (GAIN/LOSS), SwitchStatus (INITIATED/COMPLETED/OBJECTED/CANCELLED/ERRONEOUS), SwitchEvent (frozen: days_to_complete/is_completed), SwitchAnalytics (record/complete/object/mark_erroneous/gains_in_year/losses_in_year/erroneous_transfers_in_year/avg_days_to_complete/net_customer_change/annual_summary). 2022 crisis: mass switching out on SVT price cap rises; high erroneous transfer rate.
**Phase 185 COMPLETE (2026-06-26):** MPAN supply point register -- 9 new tests (2,756 passing). company/market/mpan_register.py (new): MPANStatus (REGISTERED/DEREGISTERED/PENDING_REGISTRATION/PENDING_SWITCH/ENERGISED/DE_ENERGISED/OBJECTED), ProfileClass (PC1-PC8 with Ofgem descriptions), MPANRecord (frozen: is_active/profile_class_description), MPANRegister (register/initiate_switch/complete_switch changes supplier/object_to_switch/deregister/active_mpans/pending_switches/by_profile_class/portfolio_summary). Foundation for MPAS interactions.
**Phase 184 COMPLETE (2026-06-26):** Third-party intermediary (TPI/broker) book -- 9 new tests (2,747 passing). company/crm/tpi_book.py (new): TPITier (PREFERRED/STANDARD/PROBATION/SUSPENDED), TPICommissionBasis (FIXED_PER_CUSTOMER/PCT_OF_ANNUAL_REVENUE/PCT_OF_ANNUAL_CONSUMPTION), TPI (frozen), TPIDeal (frozen: commission_gbp derived from basis), TPIBook (register/suspend/record_deal raises if suspended/deals_for_tpi/total_commission_gbp/active_tpis/annual_summary). Suspension blocks new deals. 2022 context: some brokers mis-sold fixed-price contracts not honoured.
**Phase 183 COMPLETE (2026-06-26):** 13-week rolling cash flow forecast -- 9 new tests (2,738 passing). company/finance/cash_flow_forecast.py (new): WeeklyCashFlow (frozen: total_inflows/total_outflows/net_cash/is_net_positive), CashFlowForecast (frozen: closing_cash/minimum_weekly_balance/weeks_to_cash_concern/is_solvent_throughout/total_net_cash/summary()), build_cash_flow_forecast(). Other outflows support per-week spike payments (e.g. BSC credit cover drawdown). 2022 crisis: weekly wholesale £100k vs receipts £100k leaves opex/network uncovered from week 1 -> weeks_to_cash_concern=1.
**Phase 182 COMPLETE (2026-06-26):** Board KPI dashboard (RAG status) -- 9 new tests (2,729 passing). company/finance/board_kpis.py (new): KPIStatus (GREEN/AMBER/RED), KPIValue (frozen: vs_target_pct/status; lower_is_better flag; GREEN=within -5%, AMBER=-5 to -20%, RED<-20%), BoardKPIDashboard (frozen: green/amber/red_count/overall_status/get_kpi/summary()), build_board_dashboard(7 standard KPIs: customer_count/gross_margin/EBITDA/bad_debt/complaint_days/CSAT/GSOP_compliance). 2022 crisis: bad_debt_pct=5% on 1.5% target -> RED; cascades to overall_status=RED.
**Phase 181 COMPLETE (2026-06-26):** Company-level P&L income statement -- 9 new tests (2,720 passing). company/finance/company_pl.py (new): CompanyPL frozen dataclass (revenue/wholesale/policy/network/operating/marketing/bad_debt/whd_rebates/gsop_payments; gross_margin_gbp/gross_margin_pct/total_operating_cost_gbp/ebitda_gbp/ebitda_margin_pct/bad_debt_as_pct_revenue/is_profitable/summary()), build_company_pl(). WHD rebates and GSOP payments included in opex as regulatory obligations. New company/finance/ sub-package for company-layer financial models.
**Phase 180 COMPLETE (2026-06-26):** Sales and marketing budget tracker -- 8 new tests (2,711 passing). company/crm/marketing_budget.py (new): MarketingCategory enum (7: PCW_commission/digital_adv/telesales_commission/brand_adv/partner_commission/retention_outbound/referral_reward), MarketingSpend (frozen: cost_per_customer_gbp), AnnualMarketingBudget (frozen: total_spent/budget_utilisation_pct/blended_cac_gbp/total_customers_acquired/summary()), MarketingBudgetTracker (set_budget/record_spend/annual_budget/total_spend_all_years/cac_by_category). Brand advertising has zero customers_acquired (awareness); PCW has highest CPC. Complements channel_roi.py (Ph175).
**Phase 179 COMPLETE (2026-06-26):** Hedge performance tracker -- 8 new tests (2,703 passing). company/market/hedge_performance.py (new): HedgeOutcome (PROFITABLE/NEUTRAL/COSTLY; neutral=within 5% of spot), HedgeDelivery (frozen: pnl_gbp/price_differential/outcome/hedge_effectiveness_pct), HedgePerformanceBook (record_delivery/total_pnl_gbp/profitable_trades/costly_trades/avg_effectiveness_pct/annual_summary). 2022 crisis: forward hedge at £80/MWh vs £200 spot delivery = +£120k on 1,000 MWh -- exactly what saved hedged UK suppliers while unhedged ones went insolvent.
**Phase 178 COMPLETE (2026-06-26):** Customer portfolio load forecast -- 9 new tests (2,695 passing). company/market/load_forecast.py (new): SegmentLoadForecast (frozen: segment/commodity/account_count/annual_mwh/q1-q4_mwh/monthly_avg_mwh), PortfolioLoadForecast (frozen: total_elec/gas_mwh/quarterly_mwh/summary()), build_portfolio_forecast(resi/sme/ic/include_gas). Seasonal factors: elec Q1=1.18x/Q3=0.82x; gas Q1=1.55x/Q3=0.55x (3:1 winter:summer). Trading desk input for hedging decisions.
**Phase 177 COMPLETE (2026-06-26):** Customer portfolio energy position -- 9 new tests (2,686 passing). company/market/portfolio_position.py (new): CommodityType (ELECTRICITY/GAS), PositionDirection (LONG/SHORT/FLAT ±5% tolerance), EnergyPosition (frozen: hedge_ratio_pct/net_position_mwh/direction/is_within_policy), PortfolioEnergyPosition (elec+gas combined; is_fully_hedged/summary()), compute_energy_position(). Company-layer view of hedged-vs-forecast position; does not read simulation hedge internals.
**Phase 176 COMPLETE (2026-06-26):** Invoice / billing dispute resolution -- 8 new tests (2,677 passing). company/billing/billing_dispute.py (new): BillingDisputeType enum (7: wrong_tariff/incorrect_unit_rate/missing_discount/duplicate_invoice/dd_error/standing_charge/exit_fee), BillingDisputeStatus (OPEN/UNDER_REVIEW/RESOLVED_CREDIT/RESOLVED_NO_CHANGE/ESCALATED), BillingDispute (frozen: is_open/days_to_resolution), BillingDisputeBook (raise/update_status/resolve_with_credit/resolve_no_change/open_disputes/total_credits/annual_summary). Complementary to meter_dispute.py (Ph154): billing errors vs meter-read errors.
**Phase 175 COMPLETE (2026-06-26):** Acquisition channel ROI model -- 9 new tests (2,669 passing). company/crm/channel_roi.py (new): AcquisitionChannel enum (7 channels: PCW/direct_web/telesales/partner/smart_meter_install/referral/outbound_retention), _BASE_CAC_GBP (£12-£90) + _CHANNEL_CHURN_FACTOR (0.65-1.45x), ChannelROIResult (frozen: effective_churn/tenure/roi_ratio/is_profitable), compute_channel_roi() DCF-based, channel_roi_ranking() sorts all channels by roi_ratio. PCW has highest churn multiplier (1.45x); smart meter installs and referrals have lowest.
**Phase 174 COMPLETE (2026-06-26):** Arrears escalation workflow -- 9 new tests (2,660 passing). company/billing/arrears_book.py (new): ArrearsStage enum (10 stages: CURRENT->DD_FAILED->FIRST_NOTICE->SECOND_NOTICE->PLAN_OFFERED->PLAN_ACCEPTED->PLAN_DEFAULTED->REFERRED_TO_DEBT->WRITTEN_OFF / RESOLVED), ArrearsCase (outstanding_gbp/is_open/days_open; terminal stage guard), ArrearsBook (open_case/advance_stage/record_recovery/resolve/write_off/open_cases/total_arrears_outstanding/annual_summary). Vulnerable customer flag. Terminal stage guard prevents spurious transitions post-resolution.
**Phase 173 COMPLETE (2026-06-26):** Neighbourhood energy comparison (social proof) -- 10 new tests (2,651 passing). company/crm/neighbourhood_comparison.py (new): ConsumptionRating enum (MUCH_LOWER/LOWER/SIMILAR/HIGHER/MUCH_HIGHER at -20%/-5%/+10%/+30% vs median), NeighbourhoodComparison (frozen: vs_median_pct/vs_efficient_pct/consumption_rating/potential_saving_kwh/summary()), build_neighbourhood_comparison(sample -> median=n//2/efficient=n//5). Real UK suppliers (OVO, Octopus) send neighbour comparison reports to drive demand reduction behaviour.
**Phase 172 COMPLETE (2026-06-26):** Premises occupancy history register -- 9 new tests (2,641 passing). company/crm/occupancy_register.py (new): TenancyEndReason enum (MOVED_OUT/DECEASED/SWITCHED_SUPPLIER/EVICTED/VOID), OccupancyPeriod (mpan/customer_id/move_in/move_out/end_reason; is_current/duration_days), PremisesOccupancyRegister (record_move_in/record_move_out/current_occupant/occupancy_at_date/void_mpans/history_for_mpan/history_for_customer/portfolio_summary). Duplicate-occupancy guard. occupancy_at_date() resolves who was at a meter point on any historical date.
**Phase 171 COMPLETE (2026-06-26):** Customer conversation transcript model -- 9 new tests (2,632 passing). company/crm/conversation_log.py (new): ConversationOutcome enum (RESOLVED/ESCALATED/PENDING_CALLBACK/ABANDONED/TRANSFERRED), ConversationTurn (frozen: speaker/text/timestamp), CustomerConversation (add_turn/close/duration_seconds/is_open; CSAT 1-5 / NPS 0-10 validation), ConversationLog (start/get/conversations_for_customer/open_conversations/avg_csat/avg_nps/resolution_rate/annual_summary). Closes the human-conversation simulation gap raised by Rich.
**Phase 170 COMPLETE (2026-06-26):** Payment deferral/holiday scheme -- 9 new tests (2,623 passing). company/billing/payment_deferral.py (new): DeferralStatus (ACTIVE/COMPLETED/DEFAULTED/CANCELLED), DeferralReason (FINANCIAL_HARDSHIP/COVID_19/JOB_LOSS/ILLNESS/BEREAVEMENT/BENEFIT_DELAY), PaymentDeferral (deferred_amount/repayment_plan/outstanding_gbp/deferral_days/is_active), PaymentDeferralBook (create/record_repayment/mark_defaulted/cancel/active_deferrals/overdue_deferrals/total_deferred_outstanding_gbp/annual_summary). Auto-completes when repaid in full. Ofgem SLC 27A: suppliers must offer repayment plans to customers in difficulty.
**Phase 169 COMPLETE (2026-06-26):** Customer vulnerability register -- 11 new tests (2,614 passing). company/crm/vulnerability_register.py (new): VulnerabilityFlag enum (12 flags: fuel_poverty/serious_illness/elderly/disabled/mental_health/bereavement/job_loss/language_barrier/payment_difficulty/ppm_self_disconnected/child_dependent/medical_equipment), severity weights (medical_equipment=5, PPM=5, illness=4, mental=4 down to language=1), required_actions by flag (PSR/no_disconnect/debt_advice/ECO4/WHD etc), VulnerabilityRecord (frozen: severity_score, required_actions, psr_required, no_disconnect_required), VulnerabilityRegister (register/update_flags/remove/psr_customers/no_disconnect_customers/high_severity/annual_summary).
**Phase 168 COMPLETE (2026-06-26):** Decarbonisation recommendation engine -- 11 new tests (2,603 passing). company/crm/decarb_recommender.py (new): Measure enum (9 measures: cavity/solid-wall/loft insulation, heat_pump, solar_pv, smart_controls, double_glazing, LED, battery_storage), FundingScheme enum (ECO4/BUS/SEG/GHG/self_funded), MeasureRecommendation (frozen: savings/cost/funding/priority, simple_payback_years), DecarbonisationPlan (total_potential_savings_gbp, top_measure, summary()). recommend_measures(): EPC + property_type -> insulation; EPC D+ + gas boiler -> heat pump (BUS grant); no solar -> solar PV (SEG); always -> smart controls. ECO4 eligibles get zero-cost insulation.
**Phase 167 COMPLETE (2026-06-26):** Warm Home Discount (WHD) register -- 11 new tests (2,592 passing). company/billing/whd_register.py (new): WHDEligibilityReason (CORE_GROUP/BROADER_GROUP_LIHC/BROADER_GROUP_PSR/INDUSTRY_INITIATIVE), WHDStatus, WHDApplication (frozen: status property), WHDRegister (apply/mark_rebated/pending_rebates/total_rebated_gbp/applications_for_customer/annual_summary). Duplicate-year guard. WHD_REBATE_GBP=150.0 (Ofgem-mandated). Connects to fuel_poverty.py (Ph166): LIHC->broader group; PSR->broader group. Annual summary by eligibility reason feeds Ofgem WHD returns.
**Phase 166 COMPLETE (2026-06-26):** Fuel poverty income assessment -- 10 new tests (2,581 passing). company/crm/fuel_poverty.py (new): FuelPovertyBand (NOT_FUEL_POOR/BORDERLINE/FUEL_POOR/SEVERELY_FUEL_POOR at 0-8%/8-10%/10-20%/>20% income), LIHCStatus (NOT_LIHC/LIHC/LIHC_SEVERE per post-2012 Low Income High Cost definition), FuelPovertyAssessment (frozen: energy_spend_pct/fuel_poverty_band/lihc_status/is_fuel_poor/whd_eligible/eco4_priority), assess_fuel_poverty(). LIHC threshold: income <60% of median AND cost above median. UK median income GBP34,963 / cost GBP2,074.
→ Phases 1–165: `docs/claude/phase-history.md` | Earlier: `CLAUDE_HISTORY.md`

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
