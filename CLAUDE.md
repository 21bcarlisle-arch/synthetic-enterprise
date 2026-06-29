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

**Phase L COMPLETE (2026-06-29):** Tariff Segment Profitability Book -- 19 new tests (4,814 total). company/pricing/segment_profitability.py: SegmentProfitabilityRecord (account_count/total_*_gbp/is_net_negative/average_net_contribution_gbp/net_margin_pct); SegmentProfitabilityBook (aggregate_from_customers groups by segment+year, net_negative_segments, most_profitable_segment, segment_summary). Portfolio-level complement to Phase J (per-customer). Observable-only inputs.
**Fix (2026-06-29):** Phase 44a import fix + Phase G test updates -- 13 broken tests restored (4,795 total). company/crm/customer_profitability.py: estimate_prior_term_net_margin()/compute_profitability_uplift()/MIN_RECORDS_FOR_JUDGEMENT/NET_NEGATIVE_UPLIFT_GBP_PER_MWH implemented. Phase G tests updated for Phase I HDD-weighted shape.
**Phase K COMPLETE (2026-06-29):** Break-Even Tariff Assessor -- 21 new tests (4,782 passing). company/pricing/break_even_assessor.py: BreakEvenAssessment (frozen; break_even=total_cost+min_margin; is_cap_constrained; headroom/uncovered_loss_gbp/minimum_viable_tariff_gbp_pa), BreakEvenAssessorBook (cap_constrained/total_uncovered_loss_gbp/cap_constrained_rate_pct/assessor_summary). Connects PhJ profitability + Ph295 cap + Ph294 CTS. ASHP 8,600 kWh test: structurally constrained when 2022-Q4 cap < break-even. Closes "flat margin" loop.
**Phase J COMPLETE (2026-06-29):** Customer Profitability Register -- 25 new tests (4,761 passing). company/crm/customer_profitability.py: CustomerProfitabilityRecord (frozen; net_contribution_gbp=revenue-wholesale-levies-operating; is_net_negative; gross/net margin pcts), CustomerProfitabilityBook (record/latest_for/history_for/net_negative_accounts/top_n_by_contribution/total_net_contribution_gbp/net_negative_rate_pct/profitability_summary). Observable inputs only -- epistemic-compliant. Key test: ASHP customer at standard tariff becomes net-negative once volume-driven levies (CM/CfD/RO) are counted. Addresses CLAUDE.md "flat margin" concern. Connects to cost_to_serve (Ph294).
**Phase I COMPLETE (2026-06-29):** ASHP Seasonal Electricity Shape (HDD-Weighted) -- 10 new tests (4,736 passing). simulation/run_phase2b.py: _weather_adjusted_shape_fn Phase G flat ASHP adder replaced with HDD-weighted: 70% heating (get_hdd/REFERENCE_MONTHLY_HDD), 30% DHW (flat). Annual total conserved over reference year (~5,500 kWh, within 3%). Winter peak ~2x flat; July trough ~0.03x flat. Imports get_hdd, REFERENCE_MONTHLY_HDD from sim/weather_hdd.py. First weather-responsive ASHP electricity shape.
**Phase H COMPLETE (2026-06-29):** Electricity EAC Multiplier at Term Signing -- 12 new tests (4,726 passing). simulation/run_phase2b.py: _company_eac_estimate() gains base_eac_override kwarg. At electricity term signing: eac_multiplier_for_date() applied to declared base EAC (EPC * (1+ev_fraction+ashp_fraction) * (1-solar_fraction)); override used only on first term (no billing history), not on renewals (billing history already reflects actual consumption -- no double-counting). Mirrors Phase D gas wiring. EV customers: first-term EAC higher; solar: lower; ASHP: matches Phase G settlement uplift. eac_multiplier_for_date now has 1 production call site (was 0).
**Phase G COMPLETE (2026-06-29):** ASHP Electricity Settlement Wiring -- 12 new tests (4,714 passing). simulation/household.py: ASHP_BASE_ELECTRICITY_KWH=5_500.0 module-level constant (was inline). simulation/run_phase2b.py: Phase G block in _weather_adjusted_shape_fn adds ashp_annual_kwh()/365.25/48 flat load per half-hour for heat pump homes. Phase F built eac_multiplier_for_date() but never called it in settlement; Phase G wires the electricity side to match Phase D's gas wiring. From ASHP install date: demand shape +5,500 kWh/yr additive AND gas AQ -88% (Phase D). First complete dual-fuel settlement effect.
**Phase F COMPLETE (2026-06-29):** Heat Pump Electricity Uplift -- 14 new tests (4,702 passing). simulation/household.py: ashp_annual_kwh() returns 5,500 kWh/yr for ASHP (BEIS calibrated). household_demand.py: eac_multiplier_for_date() adds ASHP fraction; _cid_hash() fixes PYTHONHASHSEED non-reproducibility. From ASHP install date: electricity EAC +5,500 kWh AND gas AQ -88% (Phase D). First dual-fuel heat pump effect from single life event.
**Phase E COMPLETE (2026-06-29):** EPC Band Evolution via Insulation Upgrades -- 19 new tests (4,688 passing). simulation/household.py: epc_consumption_multiplier() caps at 1.00 for FULL insulation, 1.25 for PARTIAL (A/B unaffected). ECO-scheme upgrades from life_events.py now flow through electricity and gas P&L. First time insulation events affect actual settlement.
**Phase D COMPLETE (2026-06-27):** Gas EAC Integration with Household Demand Register -- 16 new tests (4,669 passing). simulation/household_demand.py: GAS_HEAT_PUMP_RESIDUAL_FRACTION=0.12; gas_eac_multiplier_for_date() returns epc_consumption_multiplier() for gas-boiler resi (EPC-D=1.25, EPC-E=1.55), 0.12 for heat-pump, 1.0 for I&C. run_phase2b.py: 3-line change applies multiplier to aq_kwh at gas term signing. C1g 12,000->15,000 kWh; C2g->18,750; C3g->21,700; C4g->34,100; C_IC3g unchanged. Total resi gas +42%. First time EPC band affects gas settlement. Connects to household.py (A), life_events.py (B), household_demand.py (C), gas_settlement.py.
**Phase C COMPLETE (2026-06-27):** Household-Driven EAC Integration -- 26 new tests (4,653 passing). `simulation/household_demand.py` (new): `HouseholdDemandRegister` — builds household register from all 18 customers; generates seeded life events 2016-2025; `epc_multiplier(cid, date)` → float; `eac_multiplier_for_date(cid, date)` → composite (EPC × (1+EV_fraction) × max(0,1−solar_fraction)); `dynamic_assets(cid, date)` → {ev/solar/smart_meter}. `simulation/run_phase2b.py` (2-line change): instantiates register at startup; passes dynamic_assets and epc_multiplier to settlement loop. First time Phase A household model and Phase B life events affect actual P&L. Connects to household.py (Phase A), life_events.py (Phase B).
**Phase B COMPLETE (2026-06-27): Life events engine — 32 new tests (4,626 passing). `simulation/life_events.py` (new): `LifeEvent` frozen dataclass; `generate_life_events()` — Bernoulli trials per year on calibrated UK probability tables (solar 3%→5.7%, EV 0.3%→7%, ASHP 0.1%→0.6%, boiler replacement by age, insulation upgrade by ECO); `apply_events()` reconstructs Household state; `household_at_date()` for point-in-time reconstruction. Constraints: no flat solar, no I&C EVs, battery conditional on solar, no duplicate acquisitions. All 18 real customers generate events without error.
**Phase A COMPLETE (2026-06-27):** Household physical model — 36 new tests (4,594 passing). `simulation/household.py` (new): `Household` frozen dataclass (PropertyType/BuildEra/HeatingSystem/BoilerAge/InsulationLevel enums; epc_consumption_multiplier calibrated to EHS 2022-23 AT1_6 C=1.0 baseline; seasonal_flatness_factor/ev_annual_kwh/solar_annual_generation_kwh). `make_household()` maps existing customer records to representative UK profiles. `build_household_register()` covers all 18 customers.
**Phase 332 COMPLETE (2026-06-27):** Risk Committee Deterministic Engine + File API Fix -- 21 new tests (4,559 passing). sim/risk_committee_rules.py: parse_handshake/should_escalate/apply_rules/decide. Rule engine: +0.15/0.20/0.25 step by VaR ratio; escalates to LLM only if sigma>1.5 or all customers maxed. Removes ~95% of Ollama calls per run. File API fix: auto-loads .env.file-api (fixes /ui/stage 403). Connects to risk_committee_agent.py, context-handshake.
**Phase 331 COMPLETE (2026-06-27):** Dual-Fuel Account Consolidator -- 25 new tests (4,538 passing). company/crm/dual_fuel_account.py: FuelType (ELECTRICITY/GAS), FuelLeg (frozen; MPAN/MPRN ref, estimated_annual_cost_gbp from EAC/AQ; active flag), DualFuelAccount (frozen; is_dual_fuel/is_electricity_only/is_gas_only/combined_annual_cost_gbp/active_fuels), DualFuelAccountBook (register_electricity_leg/register_gas_leg/get_account/dual_fuel_accounts/electricity_only/gas_only/total_combined_annual_cost_gbp/dual_fuel_summary). BSC/MPAN for electricity; UNC/MPRN for gas; separate settlement, one customer account. Connects to supply_point_register (Ph299), customer_registry.
**Phase 330 COMPLETE (2026-06-27):** Payment Method Register -- 22 new tests (4,513 passing). company/billing/payment_method_register.py: PaymentMethod (DIRECT_DEBIT/PREPAYMENT_METER/BACS_TRANSFER/CHEQUE/CASH), PaymentMethodSource (VOLUNTARY/DEBT_MANDATED/VULNERABILITY_PROTECTION/DEFAULT), PaymentMethodRecord (frozen; is_prepayment/is_direct_debit/is_debt_mandated), PaymentMethodRegister (set_method/current/history_for/ppm_accounts/dd_accounts/debt_mandated_ppm/method_breakdown/payment_method_summary). UK ~70% DD, ~15% PPM; SLC 27 debt-mandated PPM; 2023 forced-fitting scandal. Connects to direct_debit, prepayment, ppm_debt_loading (Ph313).
**Phase 329 COMPLETE (2026-06-27):** Fuel Poverty Indicator Book -- 21 new tests (4,491 passing). company/regulatory/fuel_poverty.py: FuelPovertyDefinition (CLASSIC/LIHC/AFFORDABLE_WARMTH), FuelPovertyAssessment (frozen; energy_as_pct_income/is_fuel_poor; LIHC: below 60% median after costs AND >10%), FuelPovertyBook (latest_for/fuel_poor_accounts/fuel_poverty_rate_pct/summary). 6.5M UK households fuel poor 2023. Connects to whd_book (Ph281), consumer_duty (Ph283).
**Phase 328 COMPLETE (2026-06-27):** Disconnection Warning Register -- 17 new tests (4,470 passing). company/billing/disconnection_warning.py: WarningStep (W1/W2/W3/NOTICE), DisconnectionWarning (frozen; earliest_next_action/can_escalate), DisconnectionWarningRegister (mark_sent/resolve/override/can_disconnect: requires all 4 steps + 28d notice/warning_summary). SLC 27: 4 contacts minimum; 2023 Ofgem investigated for threats without full sequence. Connects to debt_collection (Ph311), winter_moratorium (Ph325).
**Phase 327 COMPLETE (2026-06-27):** Third Party Authority (TPA) Register -- 19 new tests (4,453 passing). company/crm/tpa_register.py: TPAScope (VIEW_ONLY/BILLING_MANAGEMENT/FULL_AUTHORITY), TPARelationship (CARER/ENERGY_ADVISOR/DEBT_CHARITY/SOLICITOR/POWER_OF_ATTORNEY/LANDLORD), TPARecord (frozen; is_active/has_billing_access/has_full_authority), TPARegister (revoke/expire/expiring_soon/power_of_attorney_accounts/tpa_summary). Ofgem Consumer Duty: must accept designated TPAs; POA legally binding. Connects to consumer_duty (Ph283).
**Phase 326 COMPLETE (2026-06-27):** DD Indemnity Claim Register -- 23 new tests (4,434 passing). company/billing/dd_indemnity.py: DDIndemnityReason/DDIndemnityStatus, DDIndemnityClaim (frozen; is_active/creates_debt/is_investigation_overdue 10-WD), DDIndemnityRegister (uphold/reject/write_off/overdue_investigations/total_exposure/total_upheld/dd_indemnity_summary). BACS DD Guarantee: immediate refund; 10-WD investigation; upheld = debt. Connects to direct_debit, billing_dispute, debt_collection (Ph311).
**Phase 325 COMPLETE (2026-06-27):** Winter Disconnection Moratorium Register -- 25 new tests (4,411 passing). company/billing/winter_moratorium.py: MoratoriumType/DisconnectionRisk, MoratoriumRecord (frozen; is_active/protection_status), is_winter_period() Nov-Mar, WinterMoratoriumRegister (is_protected/can_disconnect/vulnerable_protections/moratorium_summary). SLC 27: domestic Nov-Mar ban; vulnerable year-round; 2022-23 PPM scandal. Connects to debt_collection (Ph311), consumer_duty (Ph283).
**Phase 324 COMPLETE (2026-06-27):** MHHS Readiness Tracker -- 22 new tests (4,386 passing). company/market/mhhs_tracker.py: MHHSMilestone (8 milestones from DCC_CONNECTIVITY to GO_LIVE_PRODUCTION), MHHSMilestoneRecord (frozen; is_overdue/days_to_target), MHHSReadinessSnapshot (frozen; migration_completion_pct/is_on_track), MHHSReadinessTracker (overdue/at_risk/readiness_rag/mhhs_summary). Ofgem SCR 2020 / BSC P272: shadow Nov-2024, production June-2025; DCC for SMETS2 HH data.
**Phase 323 COMPLETE (2026-06-27):** Energy Theft Reporting Book -- 21 new tests (4,364 passing). company/billing/energy_theft_book.py: TheftCaseStatus (SUSPECTED/UNDER_INVESTIGATION/CONFIRMED/DNO_NOTIFIED/ESTIMATED_BILL_RAISED/CLOSED), TheftType, TheftCase (frozen; is_dno_notification_overdue 2-WD/is_active), EnergyTheftBook (confirm_theft/notify_dno/overdue_dno_notifications/total_estimated_loss_kwh). GS(SS)5: 2-WD DNO notification; 3-year back-bill theft exception. Connects to theft_indicator, supply_point_register (Ph299).
**Phase 322 COMPLETE (2026-06-27):** Deemed Contract Register -- 22 new tests (4,343 passing). company/billing/deemed_contract.py: DeemedSupplyReason/DeemedContractStatus, DeemedContractRecord (frozen; is_notification_overdue 5-WD/months_on_deemed/is_extended_deemed 12m), DeemedContractRegister (notify/convert/vacate/overdue_notifications/extended_deemed/deemed_summary). SLC 2B: 5-WD notification; 12m extended obligations. Connects to cot.py, supply_point_register (Ph299).
**Phase 321 COMPLETE (2026-06-27):** SoLR Register -- 24 new tests (4,321 passing). company/crm/solr_register.py: SoLRStatus, SoLRTransferRecord (frozen; notification/contract/billing period overdue checks), SoLRDesignation, SoLRRegister (notify/offer_contract/accept/integrate/overdue_notifications/overdue_contract_offers/in_solr_billing_period/total_credit/solr_summary). 2021-22: 28 failures, 4M customers via SoLR. 5-day notice, 30-day offer, 90-day SVT rate.
**Phase 320 COMPLETE (2026-06-27):** Credit Refund Book -- 26 new tests (4,297 passing). company/billing/credit_refund.py: RefundTrigger/RefundStatus (PENDING/APPROVED/PAID/REJECTED/HELD), CreditRefundRecord (frozen; working_days_to_pay/is_overdue/breached_deadline; weekday-aware), CreditRefundBook (raise/approve/pay/reject/hold/overdue/deadline_breaches/refund_summary). SLC 14: 10 working days (tightened 2019); 2022 crisis: Ofgem enforcement for credit withholding. Connects to account_closure (Ph312).
**Phase 319 COMPLETE (2026-06-27):** Hedge Effectiveness Assessment Book -- 29 new tests (4,271 passing). company/risk/hedge_effectiveness.py: EffectivenessOutcome (HIGHLY_EFFECTIVE/INEFFECTIVE/PROSPECTIVE_ONLY), EffectivenessTest (frozen; effectiveness_ratio_pct/outcome/is_effective/ineffectiveness_gbp), HedgeEffectivenessBook (failed_tests/de_designated_hedges/total_ineffectiveness_gbp/effectiveness_summary). IFRS 9 80-125% band; de-designation on fail; 2022: volume shrinkage caused widespread de-designation. Connects to forward_book (Ph307), hedge_policy (Ph22b).
**Phase 318 COMPLETE (2026-06-27):** Financial Resilience Assessment Book -- 27 new tests (4,242 passing). company/risk/financial_resilience.py: FRAStatus (RESILIENT/ADEQUATE/BORDERLINE/INADEQUATE), FRATrigger, FRAAssessment (frozen; total_liquidity/months_of_liquidity/status/is_compliant/period_label), FinancialResilienceBook (inadequate_quarters/borderline_or_worse/trend_is_deteriorating/fra_summary). Ofgem FRA Framework post-2022 crisis: 28 supplier failures; 12m liquidity minimum; stress+VaR must pass. Connects to stress_test (Ph303), var_monitor (Ph282).
**Phase 317 COMPLETE (2026-06-27):** VAT Book -- 20 new tests (4,215 passing). company/finance/vat_book.py: VATRateCategory (5%/20%/0%/exempt), classify_vat_category, VATTransaction (frozen; vat_rate/vat_gbp/gross_amount), VATQuarterlyReturn (net_vat_due/is_repayment), VATBook (quarterly_return/total_output_vat/vat_summary). UK domestic energy 5% (Finance Act 1994); SME threshold <=33/145 kWh/day. Connects to invoice, ccl_ledger (Ph304), corporation_tax (Ph316).
**Phase 316 COMPLETE (2026-06-27):** Corporation Tax Provision Book -- 24 new tests (4,195 passing). company/finance/corporation_tax.py: _ct_rate_for_year (20% 2016, 19% 2017-22, 25% 2023+), TaxProvision (frozen; taxable_profit/current_tax/effective_rate/is_loss_year), CorporationTaxBook (provision_for_year with loss-carry-forward; total_tax/loss_years/accumulated_losses/tax_summary). 19->25% from April 2023 = biggest UK CT rise since 1974. Connects to company_pl, pnl, management_accounts.
**Phase 315 COMPLETE (2026-06-27):** Payment Plan Adequacy Checker -- 19 new tests (4,171 passing). company/billing/payment_plan_adequacy.py: ATPCompliance (AFFORDABLE/BORDERLINE/UNAFFORDABLE/UNKNOWN), PaymentPlanAdequacyCheck (frozen; disposable_income/plan_as_pct_disposable; compliance thresholds 15%/25%/GBP50-residual floor), PaymentPlanAdequacyBook (non_compliant/borderline/vulnerable_non_compliant/total_at_risk_gbp/adequacy_summary). Ofgem SLC 27A ATP: 2022-23 crisis, 40% of plans unaffordable. Connects to payment_plan, ppm_debt_loading (Ph313), debt_collection (Ph311).
**Phase 314 COMPLETE (2026-06-27):** Back-billing Compliance Book -- 16 new tests (4,152 passing). company/billing/back_billing.py: BackBillingReason, BackBillingAssessment (frozen; cap_applies: domestic+post-2018-05+old consumption; capped_amount_gbp pro-rata; written_off_gbp), BackBillingBook (capped_assessments/total_written_off_gbp/back_billing_summary). Ofgem SLC 31A 01-May-2018: 12-month cap on retrospective domestic charges; ~GBP90M sector write-off 2018-2022; non-domestic excluded. Connects to invoice, smart_meter_rollout (Ph284).
**Phase 313 COMPLETE (2026-06-27):** PPM Debt Loading Tracker -- 19 new tests (4,136 passing). company/billing/ppm_debt_loading.py: PPMDebtLoadStatus, PPMDebtLoad (frozen; is_compliant [GBP250 cap/5% rate cap/smart-meter consent]; expected_recovery_days), PPMDebtLoadingBook (record_load/suspend/complete/non_compliant_loads/smart_meter_consents_missing/total_loaded_gbp/loading_summary). Ofgem PPM Rules 2019: GBP250 domestic cap, 5% recovery rate, smart PPM consent required. 2023 forced-fitting scandal context. Connects to debt_collection (Ph311), account_closure (Ph312), prepayment, smart_meter_rollout (Ph284).
**Phase 312 COMPLETE (2026-06-27):** Account Closure Book -- 23 new tests (4,117 passing). company/billing/account_closure.py: ClosureReason/ClosureStatus (7 states), AccountClosure (frozen; net_balance_gbp/requires_debt_referral/is_final_bill_overdue 42-day SLC 21B), AccountClosureBook (initiate/receive_final_read/issue_final_bill/return_deposit/apply_deposit_to_debt/refer_to_debt_collection/close/overdue_final_bills/requiring_debt_referral/closure_summary). Closes customer lifecycle loop: switch complete -> final bill -> deposit returned or debt referred. Connects to cos_process (Ph298), supply_point_register (Ph299), debt_collection (Ph311).
**Phase 311 COMPLETE (2026-06-27):** Debt Collection Process Book -- 26 new tests (4,094 passing). company/finance/debt_collection.py: DebtStage (INITIAL_REMINDER/WARNING_LETTER/PRE_LEGAL/DEBT_AGENCY/LEGAL_ACTION/WRITE_OFF), DebtRecord (frozen; days_in_stage/is_statute_barred >6yr/recovery_probability 0.95->0.0/expected_recovery_gbp), DebtCollectionBook (record_debt/escalate/write_off/active_debts/debts_by_stage/total_outstanding_gbp/expected_recovery_gbp/vulnerable_accounts/statute_barred_check/debt_summary). Recovery rates: 95% initial -> 0% write-off; agency 65p/GBP. Connects to bad_debt_provision, debt_referral (SLC 27A), warm_home_discount (Ph281), consumer_duty (Ph283), stress_test (Ph303).
**Phase 310 COMPLETE (2026-06-27):** Smart Export Guarantee (SEG) Book -- 20 new tests (4,068 passing). company/regulatory/seg_book.py: SEGTechnology, SEGContract (frozen; is_active), SEGPayment (frozen; payment_gbp), SEGBook (seg_rate_for_year/register_contract/terminate_contract/record_payment/active_contracts/payments_for_customer/payments_for_year/total_paid_gbp/total_export_kwh/seg_summary). SEG replaced FIT export Jan 2020; mandatory for >150k domestic customers; not levy-recoverable. Connects to fit_book (Ph286), eep_book, decarbonisation_score (Ph279).
**Phase 309 COMPLETE (2026-06-27):** Gas Procurement Policy Book -- 23 new tests (4,048 passing). company/risk/gas_procurement_policy.py: GasProcurementStatus (COMPLIANT/SHORT_COVER/OVER_HEDGED/STOP_LOSS_ALERT), GasCoverTarget, GasProcurementCheck (cover_pct/is_crisis_alert/status/shortfall_mwh), GasProcurementPolicyBook (cover_target_for_year historical targets; check_cover/non_compliant_checks/crisis_alerts/mean_cover_pct/policy_summary). Post-2022 minimum 80% cover; 2022 raised to 85%. Closes gas hedging governance gap (parallel to electricity hedge_policy.py Ph22b). Connects to gas_otc_book (Ph253), gas_imbalance_ledger (Ph306), stress_test (Ph303).

→ Phases 1–308: `docs/claude/phase-history.md` | Earlier: `CLAUDE_HISTORY.md`

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
