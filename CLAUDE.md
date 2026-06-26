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

**Phase 214 COMPLETE (2026-06-26):** Ancillary product bundle tracker -- 8 new tests (2,984 passing). company/crm/ancillary_products.py (new): AncillaryProduct (7: BOILER_COVER £18/SMART_HOME £5/HOME_INSURANCE £32/BROADBAND £28/CARBON_OFFSET £3/SOLAR_MONITORING £4/EV_TARIFF £0 monthly), _MONTHLY_REVENUE_GBP defaults, ProductSubscription (mutable: is_active/annual_revenue_gbp(year) prorated), AncillaryRevenueTracker (subscribe/cancel/active_subscriptions/products_per_customer/avg_products_per_customer/total_annual_revenue/revenue_by_product/portfolio_summary). Octopus: 2.8 products/customer average in 2024.
**Phase 213 COMPLETE (2026-06-26):** Meter read validation engine -- 7 new tests (2,976 passing). company/billing/meter_read_validation.py (new): ReadSource (CUSTOMER/ESTIMATED/SMART_METER/ENGINEER_VISIT), ValidationFlag (REVERSAL/EXCESSIVE_DAILY_RATE >3x/LOW_DAILY_RATE <0.2x/TRANSPOSITION_LIKELY/METER_ADVANCE_ZERO), ValidationResult (ACCEPTED/QUERIED/REJECTED), MeterReadValidation (frozen: advance_kwh/implied_daily_kwh/days_elapsed/flags/result/summary()). REVERSAL or EXCESSIVE->REJECTED; any other flag->QUERIED. Transposition detection rotates last digit.
**Phase 212 COMPLETE (2026-06-26):** Wholesale price monitor -- 8 new tests (2,969 passing). company/market/price_monitor.py (new): PriceAlertLevel (NORMAL/ELEVATED/HIGH/EXTREME), Commodity (ELECTRICITY/GAS), PriceObservation (frozen: term_structure_slope/is_backwardation/is_contango), PriceTrigger, WholesalePriceMonitor (add_trigger/record_observation/latest_observation/active_alerts/highest_alert_level/price_history/monitor_summary). 2022: spot £500 hits EXTREME; backwardation -£50 MoM signals supply stress. 150 company/ files milestone.
**Phase 211 COMPLETE (2026-06-26):** Customer payment behaviour analytics -- 9 new tests (2,961 passing). company/billing/payment_behaviour.py (new): PaymentResult (ON_TIME/LATE/DD_FAILED/PARTIAL/MISSED), PaymentBehaviour (EXCELLENT/GOOD/FAIR/POOR/CRITICAL), PaymentRecord (frozen: days_late/shortfall_gbp), PaymentBehaviourAnalytics (record/records_for_customer/on_time_rate/dd_failure_rate/avg_days_late/behaviour_score/total_shortfall_gbp/portfolio_summary). CRITICAL: >50% missed/DD_failed. EXCELLENT: 0 failures. Feeds credit_scoring (Ph135) and arrears_book (Ph174).
**Phase 210 COMPLETE (2026-06-26):** Regulatory reporting calendar -- 8 new tests (2,952 passing). company/regulatory/reporting_calendar.py (new): ReportingFrequency (MONTHLY/QUARTERLY/ANNUAL/AD_HOC), DeadlineStatus (PENDING/SUBMITTED/OVERDUE/WAIVED), RegulatoryDeadline (frozen: status(as_of)/is_submitted/days_until_due), RegulatoryCalendar (add_deadline/mark_submitted replaces frozen/overdue/due_within_days/by_regulator/calendar_summary). Overdue detection feeds licence_health (Ph206) BREACH escalation.
**Phase 209 COMPLETE (2026-06-26):** Carbon emissions per customer (Scope 2) -- 8 new tests (2,944 passing). company/regulatory/carbon_emissions.py (new): _EMISSION_FACTORS_G_CO2_PER_KWH (8 fuel types: coal 820/gas 490/nuclear 12/wind 11/solar 41/hydro 24/biomass 230/imports 300), FuelMixRecord (frozen: total_pct/renewable_pct/low_carbon_pct/emission_intensity_g_per_kwh VWAP), CustomerCarbonFootprint (frozen: electricity_co2_kg/gas_co2_kg/total_co2_kg/total_co2_tonnes; gas fixed at 183g/kWh), build_customer_footprint(). 2016 coal-heavy grid: ~380g/kWh; 2024 green: ~140g/kWh.
**Phase 208 COMPLETE (2026-06-26):** Staff headcount and payroll model -- 8 new tests (2,936 passing). company/finance/payroll.py (new): Department (8: OPS/CUSTOMER_SERVICES/TRADING/FINANCE/TECHNOLOGY/REGULATORY/SALES/SENIOR_MGT), EmploymentType (PERMANENT/CONTRACT/PART_TIME), HeadcountRole (frozen: total_annual_salary/employer_ni_gbp 13.8% above £9,100/pension_cost_gbp 5%/total_employment_cost_gbp), HeadcountPlan (add_role/total_headcount/total_fte/total_payroll_cost/cost_by_department/cost_per_customer_gbp/summary). Mid-sized UK supplier (5k-50k customers): £2-8M payroll; CS cost/customer £40-80.
→ Phases 1–207: `docs/claude/phase-history.md` | Earlier: `CLAUDE_HISTORY.md`
`docs/claude/phase-history.md` | Earlier: `CLAUDE_HISTORY.md`
`docs/claude/phase-history.md` | Earlier: `CLAUDE_HISTORY.md`

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
