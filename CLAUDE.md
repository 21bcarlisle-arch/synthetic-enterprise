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
**Phase DR COMPLETE (2026-06-30):** Board Meeting Minutes Register -- 21 tests (5,876 total). company/compliance/board_meeting_register.py: MeetingType (BOARD/AUDIT_COMMITTEE/RISK_COMMITTEE/REMUNERATION/EMERGENCY); ResolutionType (FINANCIAL/REGULATORY/OPERATIONAL/GOVERNANCE/RISK); BoardResolution (frozen; passed/dissenting_directors); BoardMeetingRecord (frozen; quorum_met ≥50%; was_held; passed_resolutions); BoardMeetingRegister (schedule→BM-NNNN/record_held→HELD_or_QUORUM_FAILED/sign_off_minutes/held_meetings/unsigned_minutes/by_type/resolutions_of_type/overdue_frequency: >60 days=True/board_register_summary). CA 2006 s248: 10yr retention; Ofgem may request for compliance evidence.
**Phase DQ COMPLETE (2026-06-30):** Renewal Notice Register (SLC 22) -- 19 tests (5,855 total). company/crm/renewal_notice_register.py: NoticeOutcome (PENDING/SENT_ON_TIME/SENT_LATE/SENT_EARLY/NOT_REQUIRED/FAILED); RenewalNoticeRecord (frozen; days_before_expiry; is_compliant: ON_TIME/EARLY/NOT_REQUIRED; is_breach: LATE/FAILED; notice_due_window: 42-49 days before expiry); RenewalNoticeRegister (register_contract/record_notice_sent→auto-classify/mark_not_required/mark_failed/pending/breaches/due_for_notice(as_of)/overdue_notice(as_of)/compliance_rate/notice_register_summary). SLC 22: 42-49 day window mandatory; 2022-23 Ofgem enforcement for late notices.
**Phase DP COMPLETE (2026-06-30):** Interconnector Monitor Register -- 23 tests (5,836 total). company/market/interconnector_monitor_register.py: InterconnectorID (8: IFA/IFA2/NEMO/BRITNED/NSL/MOYLE/EWIC/VIKING); _CAPACITY_MW (8,800 MW total GB import capacity); FlowDirection (IMPORT/EXPORT/ZERO ±5 MW); InterconnectorObservation (frozen; utilisation_pct; price_differential_gbp; is_arbitrage_aligned: import OK if GB>continental); InterconnectorMonitorRegister (record/observations_for/imports/exports/non_arbitrage_aligned/avg_gb_price/high_utilisation/interconnector_summary). Commissioned years 1985–2023. Epistemic: company reads NESO/Elexon published data only.
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
**Phase CJ COMPLETE (2026-06-30):** Initial Margin Register -- 12 tests (5,933). company/trading/initial_margin_register.py: MarginAccountType (BILATERAL_OTC/EXCHANGE_CLEARED/INTERNAL_NETTING); IMStatus (POSTED/RETURNED/CALLED/PARTIAL); InitialMarginRecord (total_held_gbp=posted+additional; margin_rate_pct; is_active); InitialMarginRegister (post_margin/issue_additional_call/return_margin/total_locked_gbp/records_by_counterparty). 2022: clearing houses tripled IM requirements; combined IM+VM drain destroyed supplier liquidity. Extends Phase CC (variation margin).
→ Phases 1–DA: `docs/claude/phase-history.md` | Earlier: `CLAUDE_HISTORY.md`
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
