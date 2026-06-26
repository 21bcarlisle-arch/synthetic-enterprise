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
