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

**Phase 232 COMPLETE (2026-06-26):** Counterparty credit rating book -- 8 new tests (3,137 passing). company/trading/credit_rating_book.py (new): CreditRating (9: AAA-D/NR), _RATING_SCORE (0-10), _PROBABILITY_OF_DEFAULT_PCT (0.01%-100%), is_investment_grade(rating) (BBB+ = score>=7), CounterpartyCreditProfile (frozen: score/pd_pct/is_investment_grade), CreditExposure (mutable), CreditRatingBook (register/record_exposure/total_exposure_gbp/is_within_limit/sub_investment_grade_counterparties/credit_summary). Feeds trade_blotter.py credit gate.
**Phase 231 COMPLETE (2026-06-26):** Gas supply interruption risk model -- 8 new tests (3,129 passing). company/market/gas_interruption.py (new): InterruptClass (FIRM/INTERRUPTIBLE/EMERGENCY_ONLY), _INTERRUPTIBLE_DISCOUNT_PCT (0/8/15%), InterruptionReason (5), GasInterruption (mutable: notice_days/expected_duration_days/actual_duration_days/restore), InterruptibilityContract (frozen: discount_pct), GasInterruptionManager (register_contract/issue_interruption/active/vulnerable_customers_affected/summary). Interruptible tariff = 8% cheaper. Feb 2022 supply emergency: NGAS storage at 3%.
**Phase 230 COMPLETE (2026-06-26):** Integrated board KPI dashboard -- 8 new tests (3,121 passing). company/finance/board_dashboard.py (new): KPIStatus (GREEN/AMBER/RED/NOT_SET), KPIMetric (frozen: vs_target_pct/status/is_on_target; lower_is_better flag; AMBER±10%/RED>10%), BoardDashboard (10 KPIs: customer count/net margin/gross margin/treasury/EV/churn/complaints/bad debt/cash runway/hedge ratio; kpis(targets)/rag_summary). RED if any KPI RED; at_risk_metrics list. The monthly MD view.
**Phase 229 COMPLETE (2026-06-26):** Customer switching gain/loss report -- 9 new tests (3,113 passing). company/crm/switching_report.py (new): SwitchDirection (GAIN/LOSS), SwitchReason (8 including price/service/green/smart_meter/deal/complaint/moving_home), SwitchRecord (frozen: annual_mwh/is_gain), SwitchingReport (record/gains/losses/net_customer_movement/net_mwh_movement/churn_rate_pct/loss_reasons/top_gaining_from/switching_summary). top_gaining_from() identifies which competitor is losing most to us. Core weekly MD report.
**Phase 228 COMPLETE (2026-06-26):** Tariff change notification log -- 8 new tests (3,104 passing). company/crm/tariff_notification.py (new): ADVANCE_NOTICE_DAYS=42 (SLC 25B), NotificationChannel (EMAIL/POST/SMS/IN_APP), TariffChangeReason (5 types), TariffNotification (mutable: notice_days/meets_advance_notice/unit_rate_change_pct/is_price_increase), TariffNotificationLog (send/mark_confirmed/compliance_breaches/price_increases/notification_summary). Breaches trigger Ofgem complaints. October 2022: 10m customers notified simultaneously.
**Phase 227 COMPLETE (2026-06-26):** UK ETS emission allowance registry -- 9 new tests (3,096 passing). company/regulatory/ets_registry.py (new): _UKETS_PRICE_GBP_PER_TONNE (2021-2025; 2022 peak £72), _FREE_ALLOCATION (gas 0.06t/MWh; coal 0), get_ukets_price(year), AllowanceSource (AUCTION/FREE_ALLOCATION/SECONDARY_MARKET/FORWARD_PURCHASE), AllowancePurchase (frozen: total_cost_gbp), ComplianceObligation (frozen: gross/net_obligation_tonnes; net never negative), ETSRegistry (purchase/record_obligation/surrender/holding_tonnes/total_spend_gbp/compliance_position). UK ETS launched 2021 post-Brexit.
**Phase 226 COMPLETE (2026-06-26):** Multisite I&C account management -- 9 new tests (3,087 passing). company/crm/multisite_account.py (new): SiteCategory (6: head_office/manufacturing/warehouse/retail_unit/data_centre/remote_office), BillingFrequency (MONTHLY/QUARTERLY/CONSOLIDATED), SupplyPoint (frozen: is_hv>=11kV/annual_mwh), MultisiteAccount (add_site/remove_site/total_annual_mwh/peak_site/sites_by_category/hv_sites/summary), MultisitePortfolio (create/get/total_portfolio_mwh/accounts_by_manager/largest_accounts). HV supply = 11kV+ direct DNO connection.
**Phase 225 COMPLETE (2026-06-26):** Working capital daily cash monitor -- 9 new tests (3,078 passing). company/finance/working_capital.py (new): CashFlowType (9: collections/wholesale_settlement/network_charges/payroll/VAT/facility_drawdown/facility_repayment/DSR/REGO), CashFlowEntry (frozen: signed_amount), DailyCashPosition (opening_balance/net_cash_flow/closing_balance/total_inflows/total_outflows), WorkingCapitalMonitor (post_day/current_balance/is_below_minimum/headroom_gbp/lowest_balance_in_period/cash_summary). Minimum £50k operating balance default.
**Phase 224 COMPLETE (2026-06-26):** Demand Side Response (DSR) portfolio -- 9 new tests (3,069 passing). company/market/dsr_portfolio.py (new): DSREventType (5: grid_stress/frequency_response/triad_avoidance/capacity_market_dispatch/voluntary), CurtailmentStatus (NOTIFIED/COMPLIED/PARTIAL/NON_COMPLIANT/EXEMPTED), DSREvent (duration_hours/target_mwh/is_short_notice<30min), CustomerCurtailment (compliance_pct; auto-status: COMPLIED>=95%/PARTIAL>0/NON_COMPLIANT), DSRPortfolio (create_event/record_curtailment/total_mwh_delivered/compliance_rate_pct/annual_revenue_gbp/dsr_summary). Triad avoidance saves £15/MWh TNUoS.
**Phase 223 COMPLETE (2026-06-26):** Period-end financial reconciliation ledger -- 9 new tests (3,060 passing). company/finance/period_reconciliation.py (new): ReconciliationStatus/VarianceType (5: settlement_difference/cost_overrun/revenue_shortfall/accrual_reversal/meter_read_error), ReconciliationVariance (frozen: is_adverse/abs_amount), PeriodReconciliation (mutable: total_revenue/cost/gross_margin/total_variance/adjusted_margin/add_variance/close), ReconciliationLedger (open_period/open_periods/annual_gross_margin_gbp/variances_by_type/summary). Feeds company_pl month-close workflow.

→ Phases 1–222: `docs/claude/phase-history.md` | Earlier: `CLAUDE_HISTORY.md`
`docs/claude/phase-history.md` | Earlier: `CLAUDE_HISTORY.md`
`docs/claude/phase-history.md` | Earlier: `CLAUDE_HISTORY.md`
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
