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

**Phase 215 COMPLETE (2026-06-26):** Supply contract lifecycle manager -- 9 new tests (2,993 passing). company/billing/contract_manager.py (new): ContractStatus (ACTIVE/IN_NOTICE/EXPIRED/CANCELLED/RENEWED), ContractType (FIXED_TERM/VARIABLE/DEEMED/EVERGREEN), _NOTICE_PERIOD_DAYS (42/28/14/90d), SupplyContract (mutable: notice_period_days/term_months/notice_deadline/is_in_notice_window/days_to_expiry/annual_cost_estimate_gbp), ContractManager (register/serve_notice/expire/contracts_for_customer/active/expiring_within/contracts_in_notice_window/portfolio_summary). 42-day notice = Ofgem SLC for fixed-price contracts.
**Phase 214 COMPLETE (2026-06-26):** Ancillary product bundle tracker -- 8 new tests (2,984 passing). company/crm/ancillary_products.py (new): AncillaryProduct (7: BOILER_COVER £18/SMART_HOME £5/HOME_INSURANCE £32/BROADBAND £28/CARBON_OFFSET £3/SOLAR_MONITORING £4/EV_TARIFF £0 monthly), _MONTHLY_REVENUE_GBP defaults, ProductSubscription (mutable: is_active/annual_revenue_gbp(year) prorated), AncillaryRevenueTracker (subscribe/cancel/active_subscriptions/products_per_customer/avg_products_per_customer/total_annual_revenue/revenue_by_product/portfolio_summary). Octopus: 2.8 products/customer average in 2024.
**Phase 213 COMPLETE (2026-06-26):** Meter read validation engine -- 7 new tests (2,976 passing). company/billing/meter_read_validation.py (new): ReadSource (CUSTOMER/ESTIMATED/SMART_METER/ENGINEER_VISIT), ValidationFlag (REVERSAL/EXCESSIVE_DAILY_RATE >3x/LOW_DAILY_RATE <0.2x/TRANSPOSITION_LIKELY/METER_ADVANCE_ZERO), ValidationResult (ACCEPTED/QUERIED/REJECTED), MeterReadValidation (frozen: advance_kwh/implied_daily_kwh/days_elapsed/flags/result/summary()). REVERSAL or EXCESSIVE->REJECTED; any other flag->QUERIED. Transposition detection rotates last digit.
**Phase 212 COMPLETE (2026-06-26):** Wholesale price monitor -- 8 new tests (2,969 passing). company/market/price_monitor.py (new): PriceAlertLevel (NORMAL/ELEVATED/HIGH/EXTREME), Commodity (ELECTRICITY/GAS), PriceObservation (frozen: term_structure_slope/is_backwardation/is_contango), PriceTrigger, WholesalePriceMonitor (add_trigger/record_observation/latest_observation/active_alerts/highest_alert_level/price_history/monitor_summary). 2022: spot £500 hits EXTREME; backwardation -£50 MoM signals supply stress. 150 company/ files milestone.
→ Phases 1–211: `docs/claude/phase-history.md` | Earlier: `CLAUDE_HISTORY.md`
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
