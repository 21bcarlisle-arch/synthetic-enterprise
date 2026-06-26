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

**Phase 171 COMPLETE (2026-06-26):** Customer conversation transcript model -- 9 new tests (2,632 passing). company/crm/conversation_log.py (new): ConversationOutcome enum (RESOLVED/ESCALATED/PENDING_CALLBACK/ABANDONED/TRANSFERRED), ConversationTurn (frozen: speaker/text/timestamp), CustomerConversation (add_turn/close/duration_seconds/is_open; CSAT 1-5 / NPS 0-10 validation), ConversationLog (start/get/conversations_for_customer/open_conversations/avg_csat/avg_nps/resolution_rate/annual_summary). Closes the human-conversation simulation gap raised by Rich.
**Phase 170 COMPLETE (2026-06-26):** Payment deferral/holiday scheme -- 9 new tests (2,623 passing). company/billing/payment_deferral.py (new): DeferralStatus (ACTIVE/COMPLETED/DEFAULTED/CANCELLED), DeferralReason (FINANCIAL_HARDSHIP/COVID_19/JOB_LOSS/ILLNESS/BEREAVEMENT/BENEFIT_DELAY), PaymentDeferral (deferred_amount/repayment_plan/outstanding_gbp/deferral_days/is_active), PaymentDeferralBook (create/record_repayment/mark_defaulted/cancel/active_deferrals/overdue_deferrals/total_deferred_outstanding_gbp/annual_summary). Auto-completes when repaid in full. Ofgem SLC 27A: suppliers must offer repayment plans to customers in difficulty.
**Phase 169 COMPLETE (2026-06-26):** Customer vulnerability register -- 11 new tests (2,614 passing). company/crm/vulnerability_register.py (new): VulnerabilityFlag enum (12 flags: fuel_poverty/serious_illness/elderly/disabled/mental_health/bereavement/job_loss/language_barrier/payment_difficulty/ppm_self_disconnected/child_dependent/medical_equipment), severity weights (medical_equipment=5, PPM=5, illness=4, mental=4 down to language=1), required_actions by flag (PSR/no_disconnect/debt_advice/ECO4/WHD etc), VulnerabilityRecord (frozen: severity_score, required_actions, psr_required, no_disconnect_required), VulnerabilityRegister (register/update_flags/remove/psr_customers/no_disconnect_customers/high_severity/annual_summary).
**Phase 168 COMPLETE (2026-06-26):** Decarbonisation recommendation engine -- 11 new tests (2,603 passing). company/crm/decarb_recommender.py (new): Measure enum (9 measures: cavity/solid-wall/loft insulation, heat_pump, solar_pv, smart_controls, double_glazing, LED, battery_storage), FundingScheme enum (ECO4/BUS/SEG/GHG/self_funded), MeasureRecommendation (frozen: savings/cost/funding/priority, simple_payback_years), DecarbonisationPlan (total_potential_savings_gbp, top_measure, summary()). recommend_measures(): EPC + property_type -> insulation; EPC D+ + gas boiler -> heat pump (BUS grant); no solar -> solar PV (SEG); always -> smart controls. ECO4 eligibles get zero-cost insulation.
**Phase 167 COMPLETE (2026-06-26):** Warm Home Discount (WHD) register -- 11 new tests (2,592 passing). company/billing/whd_register.py (new): WHDEligibilityReason (CORE_GROUP/BROADER_GROUP_LIHC/BROADER_GROUP_PSR/INDUSTRY_INITIATIVE), WHDStatus, WHDApplication (frozen: status property), WHDRegister (apply/mark_rebated/pending_rebates/total_rebated_gbp/applications_for_customer/annual_summary). Duplicate-year guard. WHD_REBATE_GBP=150.0 (Ofgem-mandated). Connects to fuel_poverty.py (Ph166): LIHC->broader group; PSR->broader group. Annual summary by eligibility reason feeds Ofgem WHD returns.
**Phase 166 COMPLETE (2026-06-26):** Fuel poverty income assessment -- 10 new tests (2,581 passing). company/crm/fuel_poverty.py (new): FuelPovertyBand (NOT_FUEL_POOR/BORDERLINE/FUEL_POOR/SEVERELY_FUEL_POOR at 0-8%/8-10%/10-20%/>20% income), LIHCStatus (NOT_LIHC/LIHC/LIHC_SEVERE per post-2012 Low Income High Cost definition), FuelPovertyAssessment (frozen: energy_spend_pct/fuel_poverty_band/lihc_status/is_fuel_poor/whd_eligible/eco4_priority), assess_fuel_poverty(). LIHC threshold: income <60% of median AND cost above median. UK median income GBP34,963 / cost GBP2,074.
**Phase 165 COMPLETE (2026-06-26):** Customer energy profile (360 view) -- 10 new tests (2,571 passing). company/crm/energy_profile.py (new): CustomerEnergyProfile frozen dataclass composing Property (Ph161) + HouseholdBehaviourProfile (Ph163). Properties: estimated_annual_elec/gas_kwh, is_fuel_poor, eco4_eligible, tou_candidate (medium/high sensitivity), heat_pump_candidate (gas boiler + EPC A-D), decarbonisation_priority_score (0-1 weighted by EPC/heat_pump/solar). summary() dict for CRM dashboard. Closes premises/behaviour theme: property + household + life events + contact + 360 profile all connected.
**Phase 164 COMPLETE (2026-06-26):** Inbound contact and call centre interaction model -- 9 new tests (2,561 passing). company/crm/contact_log.py (new): ContactChannel (PHONE/WEBCHAT/EMAIL/LETTER/PORTAL), ContactReason (12 reasons: BILLING_QUERY/METER_READ/PAYMENT_DIFFICULTY/COMPLAINT/DEBT_ADVICE/BEREAVEMENT etc.), ContactInteraction, ContactLog (record/contacts_for_customer/avg_handle_minutes_for_reason/annual_summary). avg_handle_minutes by reason (bereavement 25 min, complaint 18 min, meter read 5 min). escalation_rate by reason (complaint 40%, debt_advice 30%). Feeds cost-to-serve at interaction level.
**Phase 163 COMPLETE (2026-06-26):** Household behaviour profile -- 11 new tests (2,552 passing). company/crm/household_profile.py (new): HouseholdType (SINGLE/COUPLE/FAMILY/RETIRED_COUPLE/RETIRED_SINGLE/STUDENT/WFH), HeatingSystem (GAS_BOILER/HEAT_PUMP/STORAGE_HEATER/DISTRICT/OIL/SOLID_FUEL/NONE), HouseholdBehaviourProfile frozen dataclass. peak_load_factor (family 1.35x, retired couple 1.20x, student 0.75x). daytime_consumption_pct (retired 72%, student 40%). tou_price_sensitivity (high/medium/low). smart_meter_benefit_score (high-sensitivity evening-heavy households benefit most). heat_pump_eligible. Advances household simulation theme.
**Phase 162 COMPLETE (2026-06-26):** Customer life events -- 11 new tests (2,541 passing). company/crm/life_events.py (new): LifeEventType (BIRTH/DEATH/MARRIAGE/DIVORCE/JOB_LOSS/JOB_GAIN/RETIREMENT/SERIOUS_ILLNESS/MOVE_IN/MOVE_OUT/BENEFIT_CHANGE), LifeEvent (triggers_vulnerability_review/triggers_occupancy_change/triggers_cot/triggers_psr_review), LifeEventLog (record/events_for_customer/pending_vulnerability_reviews/pending_cot_triggers/pending_psr_reviews/annual_summary). Links life events to downstream workflows: COT (move events), PSR review (illness/retirement/death), vulnerability review (job loss/illness/benefit change). Advances premises simulation theme.
**Phase 161 COMPLETE (2026-06-26):** Property model -- premises attributes for consumption estimation and compliance -- 12 new tests (2,530 passing). company/crm/property_model.py (new): PropertyType (DETACHED/SEMI/TERRACED/FLAT/BUNGALOW/MOBILE_HOME/COMMERCIAL), TenureType (OWNER/PRIVATE_RENTED/SOCIAL_RENTED/SHARED_OWNERSHIP), EPCRating (A-G), Property frozen dataclass. consumption_multiplier (A=0.60x to G=1.75x D-baseline). estimated_annual_elec_kwh/gas_kwh adjusted for floor_area/occupants/EV/solar. is_fuel_poor (EPC F/G + private/social rented). eco4_eligible (EPC D-G). psr_priority_property (EPC F/G). Opens premises simulation theme per Rich direction.
**Phase 160 COMPLETE (2026-06-26):** Smart Export Guarantee (SEG) tariff management -- 12 new tests (2,518 passing). company/billing/smart_export.py (new): seg_rate_ppm() 2020-2025 (2022 peak 15p/kWh), seg_valid_rate() (must be >=1p Ofgem minimum), SEGAccount (record_export/payment_for_period/total_export_kwh/annual_summary), SEGBook (register/get_account/record_export/portfolio_summary). Zero-rate registration rejected (Ofgem SEG requirement). 2022 crisis: exported electricity valued at 15p/kWh vs 5.5p in 2020 -- prosumer customers receive substantially higher returns during the price crisis.
**Phase 159 COMPLETE (2026-06-26):** Economy 7 / off-peak tariff billing -- 11 new tests (2,506 passing). company/billing/economy7.py (new): TariffRegister (DAY/NIGHT), e7_unit_rate_ppm() 2016-2025 day/night rates, E7MeterRead (total_kwh/night_pct), E7Bill (day_charge_gbp/night_charge_gbp/total_gbp/blended_rate_ppm), generate_e7_bill(). 2022 crisis: day rate spikes to 34p (vs 12p 2016); night rate to 19p (vs 6.5p). Night rate always below day rate across all years. Blended rate falls between day and night per proportion of use.
**Phase 158 COMPLETE (2026-06-26):** Customer acquisition journey funnel -- 12 new tests (2,495 passing). company/crm/acquisition_journey.py (new): AcquisitionStage enum (QUOTE_REQUESTED/APPLICATION_SUBMITTED/CREDIT_CHECK/CREDIT_APPROVED/CREDIT_DECLINED/SIGNED_UP/FIRST_BILL_SENT/ONBOARDED), AcquisitionJourney (advance/current_stage/is_complete/converted/days_to_stage), AcquisitionFunnel (start_journey/advance/conversion_rate/drop_off_at/channel_summary). CREDIT_DECLINED and ONBOARDED are terminal stages. Connects credit_scoring.py (Ph135) with customer_registry and acquisition_cost at the funnel level.
**Phase 157 COMPLETE (2026-06-26):** Microbusiness customer classification -- 12 new tests (2,483 passing). company/crm/microbusiness.py (new): MicrobusinessStatus (MICRO/NON_MICRO/UNCLASSIFIED), MicrobusinessProfile (frozen dataclass: annual_elec_kwh/annual_gas_kwh/staff_count/annual_turnover_gbp), classify_customer(). Thresholds: elec <100 MWh, gas <293 MWh, staff <=10, turnover <=£2M. eligible_protections() returns 5 Ofgem SME protections (42-day renewal notice, no rollover without consent, Ombudsman access). Any single criterion exceeding threshold makes customer non-micro.
**Phase 156 COMPLETE (2026-06-26):** Tariff variation notice management -- 13 new tests (2,471 passing). company/billing/tariff_variation.py (new): VariationReason (PRICE_CAP_CHANGE/POLICY_COST_CHANGE/NETWORK_COST_CHANGE/TARIFF_RESTRUCTURE/COMMERCIAL_DECISION), VariationOutcome (PENDING/ACCEPTED/REJECTED_SWITCHED_AWAY/REJECTED_STAYED), TariffVariation (notice_period_days/is_adequate_notice/has_no_exit_fee_window/rate_change_pct), TariffVariationBook (issue_notice/record_response/pending_variations/inadequate_notice_violations/annual_summary). NOTICE_DAYS=30 per Ofgem SLC 23.1. No-exit-fee window: notice_sent_date to effective_date. Violations flagged for inadequate notice.
**Phase 155 COMPLETE (2026-06-26):** Customer complaint management and Ombudsman escalation -- 12 new tests (2,458 passing). company/crm/complaints.py (new): ComplaintCategory (BILLING/METERING/SUPPLY_INTERRUPTION/SWITCHING/CUSTOMER_SERVICE/DEBT_HANDLING/PPM/OTHER), ComplaintStatus (OPEN/UNDER_INVESTIGATION/RESOLVED/DEADLOCKED/ESCALATED_TO_OMBUDSMAN/OMBUDSMAN_CLOSED), Complaint (days_open/is_open/eligible_for_ombudsman), ComplaintBook (raise_complaint/update_status/resolve/escalate_to_ombudsman/overdue_for_ombudsman/annual_summary). OMBUDSMAN_ESCALATION_DAYS=56 (Ofgem SLC 2.7: 8 weeks). Annual summary includes by_category breakdown and total redress paid.
**Phase 154 COMPLETE (2026-06-26):** Meter read dispute management -- 12 new tests (2,446 passing). company/billing/meter_dispute.py (new): DisputeType (ESTIMATED_READ/ACTUAL_TOO_HIGH/METER_FAULT/PRIOR_READING_ERROR), DisputeStatus (OPEN/UNDER_REVIEW/RESOLVED_ACCEPTED/RESOLVED_REJECTED), MeterDispute (disputed_kwh/is_open), MeterDisputeBook (open_dispute/update_status/resolve/outstanding_disputes/disputes_for_customer/annual_summary). Accepts rebill credit; rejected disputes uphold original bill. Annual summary tracks total/accepted/rejected/outstanding/total_credit_gbp. Closes billing dispute resolution gap.
**Phase 153 COMPLETE (2026-06-26):** Fixed-term contract exit fee -- 10 new tests (2,434 passing). company/billing/exit_fee.py (new): ExitFeeWaiveReason enum (WITHIN_NOTICE_PERIOD/CONTRACT_EXPIRED/SUPPLIER_BREACH/CUSTOMER_DEATH/PROPERTY_EMERGENCY), ExitFeeResult frozen dataclass (days_remaining/fee_gbp/waived/waive_reason), calculate_exit_fee(). Auto-waived within 42-day notice period (Ofgem licence) or after contract expiry. Fee = days_remaining/365 × annual_kwh × rate_ppm (1.5p elec, 1.0p gas).
**Phase 152 COMPLETE (2026-06-26):** Payment plan management -- 12 new tests (2,424 passing). company/billing/payment_plan.py (new): PaymentPlanStatus enum (ACTIVE/COMPLETED/DEFAULTED/CANCELLED), PaymentPlan (plan_id/customer_id/original_debt_gbp/installment_gbp/start_date/status/payments_made/total_paid_gbp/missed_payments; expected_months/remaining_debt_gbp/is_complete properties), PaymentPlanBook (create_plan/record_payment/record_missed/cancel_plan/active_plans/defaulted_plans/plans_for_customer/portfolio_summary). 2 missed payments → DEFAULTED (triggers PPM recommendation). Bridges debt referral (Phase 151) → structured repayment → PPM (Phase 145).
**Phase 151 COMPLETE (2026-06-26):** Debt advice referral tracking -- 11 new tests (2,412 passing). company/billing/debt_referral.py (new): DebtAdviceOrg enum (StepChange/Citizens Advice/National Debtline/Money Advice Service), ReferralStatus enum (REFERRED/ACCEPTED/DECLINED/COMPLETED/NO_RESPONSE), DebtReferral (referral_id/customer_id/total_debt_gbp/referral_date/org/status/response_date/is_resolved), DebtReferralBook (refer/update_status/outstanding_referrals/eligible_for_referral/referrals_for_customer/annual_summary). Ofgem SLC 27A: mandatory referral threshold GBP200.
**Phase 150 COMPLETE (2026-06-26):** Priority Services Register (PSR) -- 12 new tests (2,401 passing). company/crm/priority_services.py (new): PSRNeed enum (10 types: LARGE_PRINT_BILLS/BRAILLE/AUDIO/ADVANCE_NOTICE/NOMINEE_BILLING/MEDICALLY_DEPENDENT/HEARING_IMPAIRED/VISUALLY_IMPAIRED/CHRONIC_ILLNESS/OTHER), PSREntry (needs/added_date/review_due_date/nominee), PSRBook (register/update_needs/is_registered/get/due_for_review/medically_dependent_customers/nominee_contacts/portfolio_summary). Annual review (365-day cycle). Distinct from vulnerability register: PSR is service ACCESS needs, not financial vulnerability.
**Phase 149 COMPLETE (2026-06-26):** Annual Energy Statement (AES) -- 12 new tests (2,389 passing). company/billing/annual_statement.py (new): AnnualStatement (frozen dataclass: consumption_kwh/total_cost_gbp/effective_unit_rate_ppm/sc_ppd/tariff_name/tariff_type/prev_year_consumption_kwh/consumption_change_pct/market_avg_cost_gbp/estimated_saving_gbp), AnnualStatementBook (generate/get/statements_for_customer/issued_for_year/overdue/summary). Ofgem SLC 31B: every domestic customer must receive annual energy statement showing usage, cost, market comparison, and estimated switching saving.
**Phase 148 COMPLETE (2026-06-26):** Annual Direct Debit Review (ADDR) -- 12 new tests (2,377 passing). company/billing/dd_review.py (new): DDAction (INCREASE/DECREASE/MAINTAIN), DDReviewResult (frozen dataclass: customer_id/review_date/current_dd/actual_spend/recommended_monthly/variance_pct/action), review() (±5% threshold: underpaying=INCREASE, overpaying=DECREASE), DDReviewBook (run_review/latest_review/overdue_for_review/summary). Ofgem SLC 27B: suppliers must review DD amounts annually and adjust if variance >5%.
**Phase 147 COMPLETE (2026-06-26):** Guaranteed Standards of Performance (GSOPs) -- 12 new tests (2,365 passing). company/regulatory/gsop.py (new): GSOPType enum (5 types), GSOPPayment dataclass (trigger/due/paid dates, amount_gbp), GSOPBook (record_trigger/pay/overdue/total_liability_gbp/annual_report). _add_working_days() skips weekends for due date calculation. 30-second amounts per Ofgem GSOP regs. annual_report(year) returns triggers/paid/auto_pay_rate_pct/overdue/by_type. Auto-pay rate <100% = Ofgem breach risk.
**Phase 146 COMPLETE (2026-06-26):** Change of Tenancy (COT) management -- 13 new tests (2,353 passing). company/billing/cot.py (new): COTEvent (move_out/move_in/new_occupant_id), COTBook (record_move_out/record_move_in/void_properties/void_days/overdue_for_nomination/portfolio_summary/events_for). deemed_rate_gbp_per_kwh(): SVT+20% uplift capped at Ofgem domestic price cap (2022: 33.6p vs 28p SVT). 28-day void -> regulatory trigger to place on named SVT. Closes meter-point lifecycle gap: ~3% of UK meter points change occupancy each year.
**Phase 145 COMPLETE (2026-06-26):** Prepayment meter (PPM) management -- 19 new tests (2,340 passing). company/billing/prepayment.py (new): PPMAccount (balance/debt/emergency_credit_limit/debt_recovery_rate/is_vulnerable), PPMBook (register/top_up/consume_daily/is_friendly_hours/is_self_disconnected/portfolio_summary). Debt recovery: 50% of top-up withheld (25% vulnerable). Emergency credit GBP5 standard (GBP10 vulnerable). Ofgem friendly hours 10pm-6am/weekends block disconnect. 2022 crisis: 3x rates exhaust emergency credit in 2 days vs weeks. Closes gap between credit_scoring PPM recommendation and operational model.
**Phase 144 COMPLETE (2026-06-26):** Gas daily balancing and nomination model -- 13 new tests (2,321 passing). company/market/gas_nominations.py (new): DailyNomination (date/gas_account_id/nominated_kwh/actual_kwh/nbp_spot_gbp_per_therm), GasNominationBook (nominate/imbalance_kwh/cash_out_cost_gbp/nomination_accuracy_pct/monthly_cashout_gbp/annual_cashout_gbp/worst_imbalance_periods/balancing_summary). Short position buys shortfall at NBP spot/therm; long gets 0.85x credit. 2022 crisis: same 1k kWh short is 10x more expensive than 2016. Closes last major daily operational gap in company layer.
**Phase 143 COMPLETE (2026-06-26):** Green tariff REGO compliance audit -- 13 new tests (2,320 passing). company/compliance/green_claims_audit.py (new): GreenClaimsAuditResult (year/obligation_mwh/rego_held_mwh/coverage_pct/status/shortfall_mwh/green_products_active/penalty_estimate_gbp), GreenClaimsAuditor (bridges TariffCatalogue Ph142 + RegoPortfolio Ph139). COMPLIANT >=100% / AT_RISK 90-99% / NON_COMPLIANT <90%. Penalty £50/MWh shortfall. Withdrawn products excluded after withdrawal date. Retired REGOs count toward coverage.
→ Phases 1–145: `docs/claude/phase-history.md` | Earlier: `CLAUDE_HISTORY.md`

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
